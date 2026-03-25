"""
ocr_recipe_extractor.py

유튜브 쇼츠 자막을 OpenCV + EasyOCR로 추출하고
LLM으로 레시피를 구조화하는 파이프라인.

Pipeline:
  1. yt-dlp      → 영상 다운로드 (MP4)
  2. OpenCV      → 프레임 추출 (N초 간격)
  3. EasyOCR     → 각 프레임에서 텍스트 OCR
  4. 중복 제거   → 유사 문자열 필터링 (difflib)
  5. LLM         → 레시피 JSON 구조화 (Ollama)
  6. Supabase    → DB 저장 (선택)

Requirements:
  pip install yt-dlp opencv-python easyocr openai python-dotenv supabase
"""

import os
import sys
import re
import json
import time
import tempfile
import argparse
from difflib import SequenceMatcher

import cv2
import easyocr
import yt_dlp
from dotenv import load_dotenv
from openai import OpenAI


# ─────────────────────────────────────────────
# 0. 환경 설정
# ─────────────────────────────────────────────
load_dotenv()

# Supabase (선택 — 저장이 필요 없으면 upload=False 로 실행)
SUPABASE_URL = os.environ.get("VITE_SUPABASE_URL")
SUPABASE_KEY = os.environ.get("VITE_SUPABASE_ANON_KEY")

# Ollama (Local LLM)
LOCAL_LLM_URL   = "http://localhost:11434/v1"
LOCAL_LLM_MODEL = "qwen2.5:7b"   # 설치된 모델명으로 변경하세요

llm_client = OpenAI(base_url=LOCAL_LLM_URL, api_key="ollama")


# ─────────────────────────────────────────────
# 1. yt-dlp: 영상 다운로드
# ─────────────────────────────────────────────
def download_video(youtube_url: str, output_path: str = "temp_video.mp4") -> str:
    """유튜브 URL → MP4 파일로 다운로드."""
    print(f"📥 영상 다운로드 중... ({youtube_url})")
    ydl_opts = {
        "format": "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best",
        "outtmpl": output_path,
        "quiet": True,
        "no_warnings": True,
        # 쇼츠 리다이렉트를 일반 URL로 처리
        "noplaylist": True,
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([youtube_url])
    print(f"✅ 다운로드 완료 → {output_path}")
    return output_path


# ─────────────────────────────────────────────
# 2. OpenCV: 프레임 추출
# ─────────────────────────────────────────────
def extract_frames(
    video_path: str,
    frame_dir: str,
    interval_sec: float = 1.0,
    crop_bottom_ratio: float = 0.35,
) -> list[str]:
    """
    영상에서 interval_sec 간격으로 프레임을 추출합니다.
    자막은 대부분 하단에 위치하므로 crop_bottom_ratio 비율만큼 하단을 잘라냅니다.
    (crop_bottom_ratio=0.35 → 하단 35% 영역만 사용)
    """
    os.makedirs(frame_dir, exist_ok=True)
    cap = cv2.VideoCapture(video_path)
    fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    step = max(1, int(fps * interval_sec))

    saved_paths = []
    frame_idx = 0
    saved_count = 0

    print(f"🎞️  프레임 추출 중... (총 {total_frames}프레임, {interval_sec}초 간격)")

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        if frame_idx % step == 0:
            h = frame.shape[0]
            # 하단 자막 영역 크롭
            crop_y = int(h * (1.0 - crop_bottom_ratio))
            cropped = frame[crop_y:, :]

            # 대비 향상 → OCR 정확도 개선
            gray = cv2.cvtColor(cropped, cv2.COLOR_BGR2GRAY)
            enhanced = cv2.equalizeHist(gray)

            out_path = os.path.join(frame_dir, f"frame_{saved_count:05d}.png")
            cv2.imwrite(out_path, enhanced)
            saved_paths.append(out_path)
            saved_count += 1

        frame_idx += 1

    cap.release()
    print(f"✅ {saved_count}개 프레임 추출 완료 → {frame_dir}")
    return saved_paths


# ─────────────────────────────────────────────
# 3. EasyOCR: 텍스트 추출
# ─────────────────────────────────────────────
def ocr_frames(frame_paths: list[str], languages: list[str] = ["ko", "en"]) -> list[str]:
    """
    EasyOCR로 각 프레임에서 텍스트를 추출합니다.
    confidence 임계값(threshold) 이상의 결과만 사용합니다.
    """
    print("🔍 EasyOCR 초기화 중... (최초 실행 시 모델 다운로드 발생)")
    reader = easyocr.Reader(languages, gpu=False)  # GPU 있으면 gpu=True
    
    all_texts = []
    total = len(frame_paths)

    for i, path in enumerate(frame_paths):
        print(f"  OCR 진행: {i+1}/{total}", end="\r")
        try:
            results = reader.readtext(path, detail=1)
            for (_, text, confidence) in results:
                text = text.strip()
                if confidence >= 0.4 and len(text) >= 2:
                    all_texts.append(text)
        except Exception as e:
            print(f"\n⚠️  {path} OCR 오류: {e}")

    print(f"\n✅ OCR 완료 — 원시 텍스트 {len(all_texts)}개 추출")
    return all_texts


# ─────────────────────────────────────────────
# 4. 중복 제거
# ─────────────────────────────────────────────
def _similarity(a: str, b: str) -> float:
    """두 문자열의 유사도 (0~1)."""
    return SequenceMatcher(None, a, b).ratio()


def deduplicate(texts: list[str], sim_threshold: float = 0.85) -> list[str]:
    """
    순서를 유지하면서 중복(또는 유사한) 텍스트를 제거합니다.
    sim_threshold: 이 값 이상이면 동일한 자막으로 간주
    """
    unique = []
    for text in texts:
        if not any(_similarity(text, u) >= sim_threshold for u in unique):
            unique.append(text)
    print(f"🧹 중복 제거 완료: {len(texts)} → {len(unique)}개")
    return unique


def clean_texts(texts: list[str]) -> list[str]:
    """특수문자·잡음 제거 및 최소 길이 필터."""
    cleaned = []
    for t in texts:
        # 한글·영어·숫자·기본 구두점만 남기기
        t = re.sub(r"[^\uAC00-\uD7A3a-zA-Z0-9\s,.!?()%\-/]", "", t).strip()
        if len(t) >= 2:
            cleaned.append(t)
    return cleaned


# ─────────────────────────────────────────────
# 5. LLM: 레시피 구조화
# ─────────────────────────────────────────────
def _fix_json_fence(raw: str) -> str:
    """LLM 응답에서 ```json ... ``` 펜스 제거."""
    raw = raw.strip()
    if raw.startswith("```json"):
        raw = raw[7:]
    elif raw.startswith("```"):
        raw = raw[3:]
    if raw.endswith("```"):
        raw = raw[:-3]
    return raw.strip()


def _extract_json(text: str) -> dict:
    """정규식으로 중괄호 JSON 블록 파싱."""
    match = re.search(r"\{.*\}", text, re.DOTALL)
    if match:
        try:
            return json.loads(match.group(0))
        except json.JSONDecodeError:
            pass
    return json.loads(text)


def structure_with_llm(subtitle_lines: list[str]) -> dict | None:
    """자막 라인 목록 → LLM → 레시피 JSON."""
    subtitle_block = "\n".join(subtitle_lines)
    print(f"🧠 LLM({LOCAL_LLM_MODEL})으로 레시피 구조화 중...")

    prompt = f"""너는 JSON만 출력하는 API야. 마크다운 코드블록(```)이나 설명 없이 순수 JSON만 반환해.

아래는 유아식 레시피 유튜브 쇼츠에서 OCR로 추출한 자막 텍스트 목록이야.
이 텍스트를 분석해서 아래 JSON 형식에 맞게 레시피를 정리해줘.

[자막 텍스트]
{subtitle_block}

[JSON 포맷]
{{
  "name": "메뉴 이름 (예: 소고기 미역국)",
  "emoji": "메뉴와 어울리는 이모지 1개 (예: 🥣)",
  "age": "권장 개월수 (본문에 없으면 '12개월+')",
  "time": "소요 시간 (예: 20분, 본문에 없으면 '15분')",
  "difficulty": "난이도 (쉬움, 보통, 어려움 중 택 1)",
  "ingredients": ["재료1", "재료2"](순수 재료 이름만 넣을 것 예: 다진 소고기 -> 소고기),
  "description": "메뉴에 대한 한 줄 설명",
  "steps": ["조리 방법 1", "조리 방법 2", "조리 방법 3"] (자막 텍스트를 모두 조리 방법으로 나누며 , 재료 손질법, 조리 시간, 온도, 조리 기구 등 모든 정보를 포함할것),
  "tip": "조리 팁 생성 (없으면 {subtitle_block} 전체를 넣을것)")
}}
"""

    try:
        response = llm_client.chat.completions.create(
            model=LOCAL_LLM_MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2,
        )
        raw = response.choices[0].message.content.strip()
        cleaned = _fix_json_fence(raw)
        return _extract_json(cleaned)
    except Exception as e:
        print(f"❌ LLM 오류: {e}")
        return None


# ─────────────────────────────────────────────
# 6. Supabase 저장 (선택)
# ─────────────────────────────────────────────
def upload_to_supabase(recipe_data: dict) -> None:
    try:
        from supabase import create_client
    except ImportError:
        print("⚠️  supabase 패키지가 없어서 저장을 건너뜁니다.")
        return

    if not SUPABASE_URL or not SUPABASE_KEY:
        print("⚠️  .env에 Supabase 설정이 없어서 저장을 건너뜁니다.")
        return

    recipe_data["id"] = int(time.time() * 1000)
    sb = create_client(SUPABASE_URL, SUPABASE_KEY)
    try:
        sb.table("recipes").insert(recipe_data).execute()
        print(f"🎉 Supabase 저장 완료! 메뉴: {recipe_data.get('name')}")
    except Exception as e:
        print(f"❌ Supabase 저장 실패: {e}")


# ─────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser(
        description="유튜브 쇼츠 자막 → OCR → 레시피 구조화"
    )
    parser.add_argument("url", nargs="?", help="유튜브 쇼츠 URL (없으면 입력 프롬프트)")
    parser.add_argument("--interval", type=float, default=1.0, help="프레임 추출 간격(초), 기본 1.0")
    parser.add_argument("--crop", type=float, default=0.35, help="하단 자막 영역 비율, 기본 0.35")
    parser.add_argument("--no-upload", action="store_true", help="Supabase 저장 건너뛰기")
    parser.add_argument("--save-json", type=str, default="", help="결과 JSON 저장 경로 (선택)")
    args = parser.parse_args()

    youtube_url = args.url or input("유튜브 쇼츠 URL 입력: ").strip()

    with tempfile.TemporaryDirectory() as tmpdir:
        video_path = os.path.join(tmpdir, "video.mp4")
        frame_dir  = os.path.join(tmpdir, "frames")

        try:
            # ── 1. 다운로드 ──────────────────────────────
            download_video(youtube_url, video_path)

            # ── 2. 프레임 추출 ───────────────────────────
            frame_paths = extract_frames(
                video_path, frame_dir,
                interval_sec=args.interval,
                crop_bottom_ratio=args.crop,
            )
            if not frame_paths:
                print("❌ 프레임 추출 실패")
                sys.exit(1)

            # ── 3. OCR ───────────────────────────────────
            raw_texts = ocr_frames(frame_paths)

            # ── 4. 정제 + 중복 제거 ──────────────────────
            cleaned = clean_texts(raw_texts)
            unique_lines = deduplicate(cleaned)

            if not unique_lines:
                print("❌ 추출된 자막 텍스트가 없습니다. --interval이나 --crop 값을 조정해 보세요.")
                sys.exit(1)

            print("\n[📋 최종 자막 라인]")
            for line in unique_lines:
                print(f"  • {line}")

            # ── 5. LLM 구조화 ────────────────────────────
            recipe = structure_with_llm(unique_lines)
            if not recipe:
                print("❌ 레시피 구조화 실패")
                sys.exit(1)

            print("\n[🍽️  구조화된 레시피 JSON]")
            print(json.dumps(recipe, ensure_ascii=False, indent=2))

            # ── JSON 파일 저장 ───────────────────────────
            if args.save_json:
                with open(args.save_json, "w", encoding="utf-8") as f:
                    json.dump(recipe, f, ensure_ascii=False, indent=2)
                print(f"💾 JSON 저장 완료 → {args.save_json}")

            # ── 6. Supabase 저장 ─────────────────────────
            if not args.no_upload:
                upload_to_supabase(recipe)

        except KeyboardInterrupt:
            print("\n⛔ 사용자가 중단했습니다.")
            sys.exit(0)


if __name__ == "__main__":
    main()
