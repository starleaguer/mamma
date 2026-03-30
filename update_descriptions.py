import os
import sys
import time
import re
from dotenv import load_dotenv
from supabase import create_client, Client
from openai import OpenAI

# 1. Configuration
load_dotenv()
SUPABASE_URL = os.environ.get("VITE_SUPABASE_URL")
SUPABASE_KEY = os.environ.get("VITE_SUPABASE_ANON_KEY")
OLLAMA_URL = "http://localhost:11434/v1"
OLLAMA_MODEL = "qwen2.5:7b"

if not all([SUPABASE_URL, SUPABASE_KEY]):
    print("❌ 에러: .env 파일에서 필요한 설정(Supabase URL/KEY)을 찾을 수 없습니다.")
    sys.exit(1)

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
ai_client = OpenAI(base_url=OLLAMA_URL, api_key="ollama")

def has_init_content(text, menu_name):
    has_init = '새로운 유아식 메뉴입니다.' in text
    return has_init

def has_invalid_content(text, menu_name):
    """최종 규칙 적용: 20-25자, 명사형 종결, 메뉴명 허용(단독 사용은 금지)"""
    has_english = any('a' <= char.lower() <= 'z' for char in text)
    has_chinese = any('\u4e00' <= char <= '\u9fff' for char in text)
    has_hangul = any('\uac00' <= char <= '\ud7a3' for char in text)
    has_tilde = '~' in text
    has_tilde2 = '!' in text
    # 메뉴 이름이 설명의 전체라면 금지 (단순 나열 방지)
    is_only_menu_name = text.strip() == menu_name.strip()
    
    # 길이 체크 (20~25자 사이)
    length = len(text)
    invalid_length = length > 25 or length < 10
    
    # 문장형 종결 어미 체크
    is_not_noun_ending = text.strip().endswith(("요", "다", "죠", ".", "드", ")", "("))
    
    return (not has_hangul) or has_english or has_chinese or has_tilde or has_tilde2 or is_only_menu_name or invalid_length or is_not_noun_ending

def generate_description(name, steps):
    """광고 스타일 명사형 카피 생성 (메뉴명 포함 가능)"""
    steps_text = "\n".join(steps) if isinstance(steps, list) else str(steps)
    
    prompt = f"""
[임무] 아래 요리에 대한 '유아 음식에 대한 한줄 설명'을 작성하라.

[정보]
- 요리명: {name}
- 조리법: {steps_text}

[조건]
1. 느낌: 한국 정서적 감성으로 편안하고 감각적인 스타일. (엄마와 아기를 위한)
2. 금지: "~해요", "~입니다" 등 문장형 절대 금지. 마침표(.)도 금지.
3. 길이: 공백 포함 **10자 이상 20자 이하**. (매우 엄격히 준수)
4. 언어: 오직 한국어(한글)만 사용.
"""
    
    for attempt in range(8):
        try:
            response = ai_client.chat.completions.create(
                model=OLLAMA_MODEL,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.8
            )
            res = response.choices[0].message.content.strip()
            
            # 후처리: 불필요한 기호 제거
            res = re.sub(r'[.~,"\']', '', res).strip()
            
            if not has_invalid_content(res, name):
                return res
            else:
                # 디버깅용 로그
                reason = "기타"
                if len(res) < 10: reason = f"짧음({len(res)})"
                elif len(res) > 30: reason = f"긺({len(res)})"
                elif '~' in res: reason = "물결표"
                elif '!' in res: reason = "느낌표"
                # elif res.strip() == name.strip(): reason = "이름단독"
                elif res.endswith(("요", "다", "죠")): reason = "문장형"
                print(f"      ({attempt+1}/8) {reason}: {res}")
        except Exception as e:
            print(f"⚠️ 에러: {e}")
            time.sleep(1)
            
    return None

def main():
    print("📋 최종 광고 카피 스타일로 DB 필터링 중...")
    response = supabase.table("recipes").select("*").execute()
    recipes = [r for r in response.data if has_init_content(r.get("description", ""), r.get("name", ""))]

    if not recipes:
        print("✅ 모든 레시피가 최상의 광고 카피(20-25자)로 완성되었습니다.")
        return

    print(f"🚀 {len(recipes)}개의 레시피를 세련된 광고 스타일로 변환 시작...")

    for i, recipe in enumerate(recipes):
        name = recipe["name"]
        print(f"[{i+1}/{len(recipes)}] '{name}' 카피 라이팅 중...")
        
        new_desc = generate_description(name, recipe.get("steps", []))
        if new_desc:
            supabase.table("recipes").update({"description": new_desc}).eq("id", recipe["id"]).execute()
            print(f"   ✅ 반영: {new_desc} ({len(new_desc)}자)")
        else:
            print(f"   ❌ 실패: {name}")

    print("\n🎉 모든 설명이 직관적인 임팩트 스타일로 최종 업그레이드되었습니다.")

if __name__ == "__main__":
    main()
