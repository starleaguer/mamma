import os
import sys
import json
import time
import argparse
import yt_dlp
import whisper
from dotenv import load_dotenv
from supabase import create_client, Client
from openai import OpenAI

# 1. Load .env Configuration
load_dotenv()
SUPABASE_URL = os.environ.get("VITE_SUPABASE_URL")
SUPABASE_KEY = os.environ.get("VITE_SUPABASE_ANON_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    print("❌ 에러: .env 파일에서 Supabase URL이나 KEY를 찾을 수 없습니다.")
    sys.exit(1)

# Initialize Supabase Client
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# 2. Local LLM (Ollama) Configuration
# 기본적으로 Ollama는 localhost:11434 포트를 사용합니다.
LOCAL_LLM_URL = "http://localhost:11434/v1"
# Ollama에 설치되어 있는 모델명으로 변경 가능 (예: llama3, qwen2.5, phi3 등)
LOCAL_LLM_MODEL = "qwen2.5:7b" 

client = OpenAI(
    base_url=LOCAL_LLM_URL,
    api_key="ollama", # Ollama 환경이므로 무시되는 값입니다.
)

def download_audio(youtube_url, output_path="temp_audio.mp3"):
    print(f"📥 유튜브 영상 다운로드 중... ({youtube_url})")
    ydl_opts = {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'outtmpl': output_path.replace('.mp3', ''),
        'quiet': True,
        'no_warnings': True
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([youtube_url])
    print("✅ 오디오 다운로드 완료")
    return output_path

def exact_text_from_audio(audio_path):
    print("🎙️ Whisper로 음성(STT) 분석 중... (첫 실행시 모델 다운로드로 시간이 약간 소요됩니다)")
    # 'small' 모델이 한국어 인식과 속도 사이의 밸런스가 좋습니다.
    model = whisper.load_model("small")
    result = model.transcribe(audio_path, language="ko")
    print("✅ 자막 텍스트 추출 완료")
    return result["text"]

import re

def fix_json(raw_output):
    cleaned = raw_output.strip()
    if cleaned.startswith("```json"):
        cleaned = cleaned[7:]
    elif cleaned.startswith("```"):
        cleaned = cleaned[3:]
    
    if cleaned.endswith("```"):
        cleaned = cleaned[:-3]
        
    return cleaned.strip()

def extract_json(cleaned):
    # JSON 괄호 내부만 추출 시도 (앞뒤에 다른 텍스트가 붙어있을 경우 방지)
    match = re.search(r'\{.*\}', cleaned, re.DOTALL)
    if match:
        try:
            return json.loads(match.group(0))
        except json.JSONDecodeError:
            pass
            
    # 정규식 실패시 기본 파싱 시도
    return json.loads(cleaned)

def parse_with_llm(transcribed_text):
    print(f"🧠 Local LLM ({LOCAL_LLM_MODEL})으로 텍스트 구조화 중...")
    prompt = f"""
너는 JSON만 출력하는 API다. 오직 JSON 형태의 데이터만 반환하세요. 앞뒤에 다른 설명이나 마크다운 코드블록(```)을 붙이지 마세요.

다음은 유아식 레시피 유튜브 쇼츠에서 추출한 자막 오디오 텍스트입니다. 이 텍스트를 분석해서 아래의 JSON 형식에 맞게 정보를 채워주세요.

[텍스트]
{transcribed_text}

[JSON 포맷]
{{
  "name": "메뉴 이름 (예: 소고기 미역국)",
  "emoji": "메뉴와 어울리는 이모지 1개 (예: 🥣)",
  "age": "권장 개월수 (본문에 없으면 '12개월+')",
  "time": "소요 시간 (예: 20분, 본문에 없으면 '15분')",
  "difficulty": "난이도 (쉬움, 보통, 어려움 중 택 1)",
  "ingredients": ["재료1", "재료2"](순수 재료 이름만 넣을 것 예: 다진 소고기 -> 소고기),
  "description": "메뉴에 대한 한 줄 설명",
  "steps": ["조리 방법 1", "조리 방법 2", "조리 방법 3"] (자막 텍스트에서 조리내용은 모두 조리 방법으로 나누며, 재료 손질법, 조리 시간, 온도, 조리 기구 등 모든 정보를 포함할것),
  "tip": "팁 한줄 생성하기")
}}
"""
    try:
        response = client.chat.completions.create(
            model=LOCAL_LLM_MODEL,
            messages=[
                {"role": "user", "content": prompt}
            ],
            temperature=0.2
        )
        raw_output = response.choices[0].message.content.strip()
        
        # 불안정한 LLM 응답을 파싱 기법으로 보정
        cleaned = fix_json(raw_output)
        data = extract_json(cleaned)
        
        return data
    except Exception as e:
        print(f"❌ LLM 데이터 파싱 오류: {e}")
        return None

def upload_to_supabase(recipe_data):
    # ID 생성 (타임스탬프)
    recipe_data["id"] = int(time.time() * 1000)
    
    print("☁️ Supabase에 저장 중...")
    try:
        supabase.table("recipes").insert(recipe_data).execute()
        print(f"🎉 성공적으로 DB에 저장되었습니다! 등록된 메뉴명: {recipe_data.get('name')}")
    except Exception as e:
        print(f"❌ Supabase 저장 실패: {e}")

def main():
    # parser = argparse.ArgumentParser(description="유튜브 쇼츠 -> 유아식 레시피 추출기")
    # parser.add_argument("url", help="분석할 유튜브 (또는 쇼츠) 영상 링크")
    # args = parser.parse_args()
    audio_url = input("URL주소: ")
    audio_file = "temp_audio.mp3"
    try:
        # 1. 다운로드
        download_audio(audio_url, audio_file)
        
        # 2. 음성 텍스트화
        transcribed_text = exact_text_from_audio(audio_file)
        print(f"\n[추출된 자막 원본]\n{transcribed_text}\n")
        
        # 3. LLM 정보 구조화
        recipe_data = parse_with_llm(transcribed_text)
        
        if recipe_data:
            print(f"\n[구조화된 JSON 데이터]\n{json.dumps(recipe_data, ensure_ascii=False, indent=2)}\n")
            # 4. Supabase 연동
            upload_to_supabase(recipe_data)
        else:
            print("데이터 변환에 실패하여 기록을 취소합니다.")
            
    finally:
        # 다운받은 음악 파일 정리
        if os.path.exists(audio_file):
            os.remove(audio_file)

if __name__ == "__main__":
    main()
