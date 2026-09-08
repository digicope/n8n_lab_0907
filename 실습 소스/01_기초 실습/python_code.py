# 결과를 담을 새로운 리스트 생성
output_items = []

for item in _items:
    # 안전하게 json 데이터를 가져옵니다.
    json_data = item.get("json", {})
    
    # body 필드 데이터 가져오기 (없으면 빈 문자열)
    body_content = json_data.get("body", "")
    
    # 단어 수 계산 (공백 기준 split)
    # 문자열이 아닐 경우를 대비해 str()로 변환 후 계산합니다.
    word_count = len(str(body_content).split())
    
    # 기존 필드를 모두 제외하고, 원하는 필드만 새로 구성
    new_json = {
        "body": body_content,
        "wordCount": word_count
    }
    
    # n8n 형식({"json": ...})에 맞게 새 아이템 추가
    output_items.append({"json": new_json})

# 최종 결과 반환
return output_items