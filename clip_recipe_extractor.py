"""
clip_recipe_extractor.py

유튜브 쇼츠 → CLIP + EasyOCR + Whisper + LLM → 레시피 JSON 파이프라인

Pipeline:
  1. yt-dlp      → MP4 영상 + MP3 오디오 다운로드
  2. OpenCV      → 프레임 추출 (N초 간격)
  3. CLIP        → 요리/음식 관련 프레임 AI 필터링
  4. EasyOCR     → 필터된 프레임에서 화면 자막 추출
  5. Whisper     → 음성 텍스트(STT) 추출
  6. 병합·중복제거 → OCR + Whisper 텍스트 통합
  7. LLM         → 레시피 JSON 구조화 (Ollama)
  8. Supabase    → DB 저장 (선택)

Requirements:
  pip install yt-dlp opencv-python easyocr openai-whisper open-clip-torch torch torchvision python-dotenv supabase
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
import torch
import numpy as np
from PIL import Image
import open_clip
import easyocr
import whisper
import yt_dlp
from dotenv import load_dotenv
from openai import OpenAI


# ─────────────────────────────────────────────
# 0. 환경 설정
# ─────────────────────────────────────────────
load_dotenv()

SUPABASE_URL = os.environ.get("VITE_SUPABASE_URL")
SUPABASE_KEY = os.environ.get("VITE_SUPABASE_ANON_KEY")

LOCAL_LLM_URL   = "http://localhost:11434/v1"
LOCAL_LLM_MODEL = "qwen2.5:7b"  # 설치된 모델명으로 변경

llm_client = OpenAI(base_url=LOCAL_LLM_URL, api_key="ollama")

# CLIP 디바이스 설정
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"


# ─────────────────────────────────────────────
# 1. yt-dlp: 영상 + 오디오 다운로드
# ─────────────────────────────────────────────
def download_video_and_audio(
    youtube_url: str,
    video_path: str = "temp_video.mp4",
    audio_path: str = "temp_audio.mp3",
) -> tuple[str, str]:
    """유튜브 URL → MP4 영상 + MP3 오디오 동시 다운로드."""
    print(f"📥 영상/오디오 다운로드 중... ({youtube_url})")

    # 영상 다운로드
    ydl_video_opts = {
        "format": "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best",
        "outtmpl": video_path,
        "quiet": True,
        "no_warnings": True,
        "noplaylist": True,
    }
    with yt_dlp.YoutubeDL(ydl_video_opts) as ydl:
        ydl.download([youtube_url])

    # 오디오 다운로드
    audio_base = audio_path.replace(".mp3", "")
    ydl_audio_opts = {
        "format": "bestaudio/best",
        "postprocessors": [{"key": "FFmpegExtractAudio", "preferredcodec": "mp3", "preferredquality": "192"}],
        "outtmpl": audio_base,
        "quiet": True,
        "no_warnings": True,
        "noplaylist": True,
    }
    with yt_dlp.YoutubeDL(ydl_audio_opts) as ydl:
        ydl.download([youtube_url])

    print(f"✅ 다운로드 완료 → 영상: {video_path} / 오디오: {audio_path}")
    return video_path, audio_path


# ─────────────────────────────────────────────
# 2. OpenCV: 프레임 추출 (전체 + 하단 크롭)
# ─────────────────────────────────────────────
def extract_frames(
    video_path: str,
    frame_dir: str,
    interval_sec: float = 1.0,
    crop_bottom_ratio: float = 0.35,
) -> tuple[list[str], list[str]]:
    """
    영상에서 interval_sec 간격으로 프레임을 추출합니다.
    Returns:
        full_paths  - CLIP 분석용 전체 프레임 경로 목록
        crop_paths  - OCR용 하단 크롭 프레임 경로 목록
    """
    os.makedirs(os.path.join(frame_dir, "full"), exist_ok=True)
    os.makedirs(os.path.join(frame_dir, "crop"), exist_ok=True)

    cap = cv2.VideoCapture(video_path)
    fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    step = max(1, int(fps * interval_sec))

    full_paths, crop_paths = [], []  # [(path, timestamp)]
    frame_idx = saved_count = 0

    print(f"🎞️  프레임 추출 중... (총 {total_frames}프레임, {interval_sec}초 간격)")

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        if frame_idx % step == 0:
            # 전체 프레임 (CLIP 용)
            full_path = os.path.join(frame_dir, "full", f"frame_{saved_count:05d}.png")
            cv2.imwrite(full_path, frame)
            timestamp = frame_idx / fps
            full_paths.append((full_path, timestamp))

            # 하단 크롭 (OCR 용)
            h = frame.shape[0]
            crop_y = int(h * (1.0 - crop_bottom_ratio))
            cropped = frame[crop_y:, :]
            gray = cv2.cvtColor(cropped, cv2.COLOR_BGR2GRAY)
            enhanced = cv2.equalizeHist(gray)
            crop_path = os.path.join(frame_dir, "crop", f"frame_{saved_count:05d}.png")
            cv2.imwrite(crop_path, enhanced)
            crop_paths.append((crop_path, timestamp))

            saved_count += 1

        frame_idx += 1

    cap.release()
    print(f"✅ {saved_count}개 프레임 추출 완료")
    return full_paths, crop_paths


# ─────────────────────────────────────────────
# 3. CLIP: 요리 관련 프레임 필터링
# ─────────────────────────────────────────────
# 요리/음식 관련 판단을 위한 프롬프트
FOOD_PROMPTS = [
    "cooking food in a kitchen",
    "baby food recipe",
    "chopping vegetables",
    "boiling soup or broth",
    "frying or sauteing food",
    "food ingredients laid out",
    "mixing or stirring food",
    "plating or serving food",
    "steaming food",
    "a completed dish of food",
]
NON_FOOD_PROMPTS = [
    "a blank screen",
    "title card or text only",
    "person talking to camera",
    "unrelated background scene",
]


def load_clip_model() -> tuple:
    """CLIP 모델을 로드합니다."""
    print("🤖 CLIP 모델 로딩 중... (최초 실행 시 다운로드 발생)")
    model, _, preprocess = open_clip.create_model_and_transforms(
        "ViT-B-32", pretrained="openai", device=DEVICE
    )
    tokenizer = open_clip.get_tokenizer("ViT-B-32")
    model.eval()
    print("✅ CLIP 모델 로드 완료")
    return model, preprocess, tokenizer


def filter_frames_with_clip(
    full_frame_paths: list[str],
    crop_frame_paths: list[str],
    clip_model,
    clip_preprocess,
    clip_tokenizer,
    threshold: float = 0.20,
) -> list[str]:
    """
    CLIP으로 각 프레임의 요리 관련 점수를 계산하고,
    threshold 이상인 프레임의 crop 경로만 반환합니다.

    score = softmax(food_prompts의 평균 유사도 - non_food_prompts의 평균 유사도)
    """
    print(f"🔎 CLIP 프레임 필터링 중... (총 {len(full_frame_paths)}개, 임계값: {threshold})")

    # 텍스트 임베딩 사전 계산
    all_prompts = FOOD_PROMPTS + NON_FOOD_PROMPTS
    text_tokens = clip_tokenizer(all_prompts).to(DEVICE)
    with torch.no_grad():
        text_features = clip_model.encode_text(text_tokens)
        text_features = text_features / text_features.norm(dim=-1, keepdim=True)

    food_idx = list(range(len(FOOD_PROMPTS)))
    non_food_idx = list(range(len(FOOD_PROMPTS), len(all_prompts)))

    filtered_crop_paths = []
    scores = []

    for i, ((full_path, t), (crop_path, _)) in enumerate(zip(full_frame_paths, crop_frame_paths)):
        print(f"  CLIP 처리: {i+1}/{len(full_frame_paths)}", end="\r")
        try:
            image = Image.open(full_path).convert("RGB")
            image_tensor = clip_preprocess(image).unsqueeze(0).to(DEVICE)

            with torch.no_grad():
                image_features = clip_model.encode_image(image_tensor)
                image_features = image_features / image_features.norm(dim=-1, keepdim=True)

            # 코사인 유사도
            similarity = (image_features @ text_features.T).squeeze(0).cpu().numpy()

            food_score = float(np.mean(similarity[food_idx]))
            non_food_score = float(np.mean(similarity[non_food_idx]))
            net_score = food_score - non_food_score
            scores.append(net_score)

            if net_score >= threshold:
                filtered_crop_paths.append((crop_path, t))

        except Exception as e:
            print(f"\n⚠️ CLIP 오류 ({full_path}): {e}")
            # 오류 시 포함
            filtered_crop_paths.append((crop_path, t))

    total = len(full_frame_paths)
    kept = len(filtered_crop_paths)
    print(f"\n✅ CLIP 필터링 완료: {total}개 → {kept}개 (제거: {total - kept}개)")
    if scores:
        print(f"   점수 범위: {min(scores):.3f} ~ {max(scores):.3f}, 평균: {sum(scores)/len(scores):.3f}")

    return filtered_crop_paths


# ─────────────────────────────────────────────
# 4. EasyOCR: 화면 자막 추출
# ─────────────────────────────────────────────
def ocr_frames(frame_paths: list[tuple[str, float]], languages: list[str] = ["ko", "en"]) -> list[dict]:
    """EasyOCR로 프레임에서 텍스트를 추출합니다. (타임스탬프 포함)"""
    if not frame_paths:
        print("⚠️  OCR 처리할 프레임 없음")
        return []

    print("🔍 EasyOCR 초기화 중...")
    reader = easyocr.Reader(languages, gpu=(DEVICE == "cuda"))

    all_texts = []
    total = len(frame_paths)

    for i, (path, t) in enumerate(frame_paths):
        print(f"  OCR 진행: {i+1}/{total}", end="\r")
        try:
            results = reader.readtext(path, detail=1)
            for (_, text, confidence) in results:
                text = text.strip()
                if confidence >= 0.4 and len(text) >= 2:
                    all_texts.append({
                        "time": t,
                        "text": text
                    })
        except Exception as e:
            print(f"\n⚠️ OCR 오류 ({path}): {e}")

    print(f"\n✅ OCR 완료: {len(all_texts)}개 원시 텍스트 추출")
    return all_texts


# ─────────────────────────────────────────────
# 5. Whisper: 음성 STT
# ─────────────────────────────────────────────
def transcribe_audio(audio_path: str, model_size: str = "small") -> list[dict]:
    """Whisper로 오디오를 텍스트로 변환합니다. (세그먼트 반환)"""
    print(f"🎙️  Whisper({model_size}) 음성 인식 중...")
    model = whisper.load_model(model_size)
    result = model.transcribe(audio_path, language="ko")
    segments = result.get("segments", [])
    print(f"✅ Whisper 완료: {len(segments)}개 세그먼트")
    return segments


# ─────────────────────────────────────────────
# 6. 텍스트 병합 + 중복 제거
# ─────────────────────────────────────────────
def _similarity(a: str, b: str) -> float:
    return SequenceMatcher(None, a, b).ratio()


def _clean(texts: list[str]) -> list[str]:
    """한글/영어/숫자/기본 구두점만 남기고 최소 길이 필터."""
    result = []
    for t in texts:
        t = re.sub(r"[^\uAC00-\uD7A3a-zA-Z0-9\s,.!?()%\-/]", "", t).strip()
        if len(t) >= 2:
            result.append(t)
    return result


# 장면별 OCR/음성 매칭
def match_scene_data(ocr_items: list[dict], whisper_segments: list[dict]) -> list[dict]:
    scene_data = []

    for item in ocr_items:
        t = item["time"]
        ocr_text = item["text"]

        matched_speech = []
        for seg in whisper_segments:
            if seg["start"] <= t <= seg["end"]:
                matched_speech.append(seg["text"])

        scene_data.append({
            "time": t,
            "ocr": ocr_text,
            "speech": " ".join(matched_speech).strip()
        })

    print(f"🎬 장면 매칭 완료: {len(scene_data)}개")
    return scene_data


# ─────────────────────────────────────────────
# 7. LLM: 레시피 구조화
# ─────────────────────────────────────────────
def _fix_json_fence(raw: str) -> str:
    raw = raw.strip()
    if raw.startswith("```json"):
        raw = raw[7:]
    elif raw.startswith("```"):
        raw = raw[3:]
    if raw.endswith("```"):
        raw = raw[:-3]
    return raw.strip()


def _extract_json(text: str) -> dict:
    match = re.search(r"\{.*\}", text, re.DOTALL)
    if match:
        try:
            return json.loads(match.group(0))
        except json.JSONDecodeError:
            pass
    return json.loads(text)


def structure_with_llm(scene_data: list[dict]) -> dict | None:
    """장면 데이터 목록 → LLM → 레시피 JSON."""
    lines = []
    for s in scene_data:
        lines.append(f"[{round(s['time'],1)}s] OCR:{s['ocr']} | 음성:{s['speech']}")
    block = "\n".join(lines)
    print(f"🧠 LLM({LOCAL_LLM_MODEL})으로 레시피 구조화 중...")

    prompt = f"""너는 JSON만 출력하는 API야. 마크다운 코드블록(```)이나 설명 없이 순수 JSON만 반환해.

아래는 유아식 레시피 유튜브 쇼츠에서 AI(OCR + 음성인식)로 추출한 텍스트야.
이 텍스트를 분석해서 아래 JSON 형식에 맞게 레시피를 정리해줘.

[텍스트]
{block}

[JSON 포맷]
{{
  "name": "메뉴 이름 (예: 소고기 미역국)",
  "emoji": "메뉴와 어울리는 이모지 1개 (예: 🥣)",
  "age": "권장 개월수 (본문에 없으면 '12개월+')",
  "time": "소요 시간 (예: 20분, 본문에 없으면 '15분')",
  "difficulty": "난이도 (쉬움, 보통, 어려움 중 택 1)",
  "ingredients": ["재료1", "재료2"](순수 재료 이름만 넣을 것, 예: 다진 소고기 -> 소고기),
  "description": "메뉴에 대한 한 줄 설명",
  "steps": ["조리 방법 1", "조리 방법 2"] (텍스트에서 조리 내용을 모두 조리 방법으로 나누며, 재료 손질법, 조리 시간, 온도, 조리 기구 등 모든 정보를 포함할 것),
  "tip": "팁 한 줄 생성"
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
# 8. Supabase 저장 (선택)
# ─────────────────────────────────────────────
def upload_to_supabase(recipe_data: dict) -> None:
    try:
        from supabase import create_client
    except ImportError:
        print("⚠️  supabase 패키지 없음 — 저장 건너뜀")
        return

    if not SUPABASE_URL or not SUPABASE_KEY:
        print("⚠️  .env에 Supabase 설정 없음 — 저장 건너뜀")
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
        description="유튜브 쇼츠 → CLIP + OCR + Whisper → 레시피 JSON"
    )
    parser.add_argument("url", nargs="?", help="유튜브 쇼츠 URL (없으면 입력 프롬프트)")
    parser.add_argument("--interval", type=float, default=1.0, help="프레임 추출 간격(초), 기본 1.0")
    parser.add_argument("--crop", type=float, default=0.35, help="하단 자막 영역 비율, 기본 0.35")
    parser.add_argument("--clip-threshold", type=float, default=0.20, help="CLIP 필터 임계값, 기본 0.20")
    parser.add_argument("--whisper-model", type=str, default="small", help="Whisper 모델 크기 (tiny/base/small/medium), 기본 small")
    parser.add_argument("--no-upload", action="store_true", help="Supabase 저장 건너뜀")
    parser.add_argument("--save-json", type=str, default="", help="결과 JSON 저장 경로 (선택)")
    args = parser.parse_args()

    youtube_url = args.url or input("유튜브 쇼츠 URL 입력: ").strip()

    print("\n" + "="*55)
    print("  🍼 CLIP + OCR + Whisper 레시피 추출기")
    print("="*55 + "\n")

    with tempfile.TemporaryDirectory() as tmpdir:
        video_path = os.path.join(tmpdir, "video.mp4")
        audio_path = os.path.join(tmpdir, "temp_audio.mp3")
        frame_dir  = os.path.join(tmpdir, "frames")

        try:
            # ── 1. 다운로드 ─────────────────────────────────
            download_video_and_audio(youtube_url, video_path, audio_path)

            # ── 2. 프레임 추출 ──────────────────────────────
            full_paths, crop_paths = extract_frames(
                video_path, frame_dir,
                interval_sec=args.interval,
                crop_bottom_ratio=args.crop,
            )
            if not full_paths:
                print("❌ 프레임 추출 실패")
                sys.exit(1)

            # ── 3. CLIP 모델 로드 + 프레임 필터 ────────────
            clip_model, clip_preprocess, clip_tokenizer = load_clip_model()
            filtered_crop_paths = filter_frames_with_clip(
                full_paths, crop_paths,
                clip_model, clip_preprocess, clip_tokenizer,
                threshold=args.clip_threshold,
            )

            # ── 4. OCR ─────────────────────────────────────
            ocr_items = ocr_frames(filtered_crop_paths)

            # ── 5. Whisper STT ──────────────────────────────
            whisper_segments = []
            if os.path.exists(audio_path):
                whisper_segments = transcribe_audio(audio_path, args.whisper_model)
            else:
                print("⚠️  오디오 파일 없음 — Whisper 건너뜀")

            # ── 6. 장면 매칭 ────────────────────────────────
            scene_data = match_scene_data(ocr_items, whisper_segments)

            if not scene_data:
                print("❌ 장면 데이터 생성 실패")
                sys.exit(1)

            print("\n[🎬 장면 기반 데이터]")
            for s in scene_data[:20]:
                print(f"{round(s['time'],1)}s | OCR: {s['ocr']} | 음성: {s['speech']}")

            # ── 7. LLM 구조화 ───────────────────────────────
            recipe = structure_with_llm(scene_data)
            if not recipe:
                print("❌ 레시피 구조화 실패")
                sys.exit(1)

            print("\n[🍽️  구조화된 레시피 JSON]")
            print(json.dumps(recipe, ensure_ascii=False, indent=2))

            # ── JSON 파일 저장 ──────────────────────────────
            if args.save_json:
                with open(args.save_json, "w", encoding="utf-8") as f:
                    json.dump(recipe, f, ensure_ascii=False, indent=2)
                print(f"\n💾 JSON 저장 완료 → {args.save_json}")

            # ── 8. Supabase 저장 ────────────────────────────
            if not args.no_upload:
                upload_to_supabase(recipe)

        except KeyboardInterrupt:
            print("\n⛔ 사용자가 중단했습니다.")
            sys.exit(0)


if __name__ == "__main__":
    main()
