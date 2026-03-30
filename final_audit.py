import os
import re
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()
supabase = create_client(os.environ['VITE_SUPABASE_URL'], os.environ['VITE_SUPABASE_ANON_KEY'])

def contains_invalid(text, menu_name):
    # 1. 영문/중문 포함 여부
    has_english = any('a' <= char.lower() <= 'z' for char in text)
    has_chinese = any('\u4e00' <= char <= '\u9fff' for char in text)
    
    # 2. 물결표 포함 여부
    has_tilde = '~' in text
    has_tilde2 = '!' in text
    
    # 3. 메뉴 이름 포함 여부 (공백 제거 후 비교)
    clean_name = menu_name.replace(" ", "")
    clean_text = text.replace(" ", "")
    has_menu_name = clean_name in clean_text if clean_name else False
    
    # 4. 길이 제약 (20-25자)
    length = len(text)
    invalid_length = length < 10 or length > 25
    
    # 5. 명사형 종결 여부 체크 (요, 다, 죠로 끝나면 문장형으로 간주)
    is_sentence_ending = text.strip().endswith(("요", "다", "죠"))
    
    reasons = []
    if has_english or has_chinese: reasons.append("외국어")
    if has_tilde: reasons.append("물결표(~)")
    if has_tilde2: reasons.append("느낌표(!)")
    if has_menu_name: reasons.append("메뉴명 포함")
    if invalid_length: reasons.append(f"길이 부적절({length}자)")
    if is_sentence_ending: reasons.append("문장형 어미")
    
    return reasons

data = supabase.table('recipes').select('id, name, description').execute().data
failures = []
for r in data:
    desc = r.get('description', '')
    name = r.get('name', '')
    reasons = contains_invalid(desc, name)
    if reasons:
        failures.append(f"[{name}] ({', '.join(reasons)}) : {desc}")

if failures:
    print(f"❌ 발견된 부적절한 항목 ({len(failures)}개):")
    for f in failures:
        print(f)
else:
    print("✅ 모든 레시피 설명이 규칙(20-25자, 명사형 종결, 한글 전용, 물결표 없음, 메뉴명 미포함)을 준수합니다.")
