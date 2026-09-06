# n8n HTTP Request — API 키·URL·Parameter 설정 가이드

> **교육 과정:** 생성형 AI 활용 교육 (Upstage · 충청ICT)  
> **대상:** n8n **HTTP Request** 노드로 외부 API를 호출하는 실습  
> **관련 실습:** `n8n_기초_실습`, `n8n_2단계_실습`, `n8n_문서_Agent_실습`, `n8n_AI_Agent_활용_실습`

---

## 목차

1. [전체 흐름 요약](#1-전체-흐름-요약)
2. [API 문서에서 정보 찾기](#2-api-문서에서-정보-찾기)
3. [API 키 발급 및 n8n 등록](#3-api-키-발급-및-n8n-등록)
4. [n8n HTTP Request 노드 설정](#4-n8n-http-request-노드-설정)
5. [curl로 파라미터 설정하기](#5-curl로-파라미터-설정하기)
6. [curl → n8n 변환표](#6-curl--n8n-변환표)
7. [실습 예제 3종](#7-실습-예제-3종)
8. [자주 하는 실수와 해결](#8-자주-하는-실수와-해결)

---

## 1. 전체 흐름 요약

외부 API를 n8n에서 호출하려면 아래 **4가지 정보**를 먼저 확보합니다.

| 항목 | 설명 | 예시 |
|------|------|------|
| **URL** | API 엔드포인트 주소 | `https://api.upstage.ai/v1/document-digitization` |
| **Method** | HTTP 메서드 | `GET`, `POST`, `PUT`, `DELETE` |
| **인증 (API Key)** | 요청 권한 확인 | Header `Authorization: Bearer {키}` |
| **Parameter** | 요청에 전달할 값 | Query, Header, Body |

### 권장 작업 순서

```
① API 공식 문서 확인
    ↓
② curl로 먼저 테스트 (터미널)
    ↓
③ 성공한 curl을 n8n HTTP Request에 옮기기
    ↓
④ n8n에서 Execute step으로 재확인
```

> **팁:** API가 처음이면 n8n보다 **curl을 먼저** 쓰는 것이 빠릅니다. curl에서 200 OK가 나오면, 같은 값을 n8n에 그대로 옮기면 됩니다.

---

## 2. API 문서에서 정보 찾기

대부분의 API 문서는 아래 항목을 제공합니다. 문서에서 해당 섹션을 찾으세요.

| 문서 항목 | 찾을 내용 | n8n에서 쓰는 곳 |
|-----------|-----------|----------------|
| **Base URL / Endpoint** | 호출 주소 | HTTP Request → **URL** |
| **Authentication** | API Key 위치·형식 | **Authentication** 또는 **Header** |
| **Query Parameters** | URL 뒤 `?key=value` | **Send Query Parameters** |
| **Request Headers** | `Content-Type` 등 | **Send Headers** |
| **Request Body** | JSON, Form Data | **Send Body** |
| **Example Request / cURL** | 복사 가능한 예제 | curl 테스트 → n8n 이식 |

### 문서 예시 읽는 법

API 문서에 아래와 같이 나와 있다면:

```http
GET https://api.openweathermap.org/data/2.5/weather?q=Seoul&appid=YOUR_API_KEY&units=metric&lang=kr
```

| 구분 | 값 |
|------|-----|
| Method | `GET` |
| URL | `https://api.openweathermap.org/data/2.5/weather` |
| Query Parameter | `q=Seoul`, `appid=YOUR_API_KEY`, `units=metric`, `lang=kr` |
| API Key 위치 | Query Parameter (`appid`) |

---

## 3. API 키 발급 및 n8n 등록

### 3-1. API 키 발급 (서비스별)

| 서비스 | 발급 위치 | 키 이름 |
|--------|-----------|---------|
| **Upstage** | [console.upstage.ai](https://console.upstage.ai) → API Keys | API Key |
| **OpenWeatherMap** | [openweathermap.org](https://openweathermap.org/api) → API keys | API Key (`appid`) |
| **KAMIS** | [kamis.or.kr](https://www.kamis.or.kr) → Open API 신청 | `p_cert_key`, `p_cert_id` |
| **카카오** | [developers.kakao.com](https://developers.kakao.com) | REST API Key, OAuth2 Token |
| **Google Gemini** | [aistudio.google.com](https://aistudio.google.com) | API Key |

### 3-2. API 키가 들어가는 위치 (3가지 패턴)

| 패턴 | curl 예시 | n8n 설정 |
|------|-----------|----------|
| **Header Bearer** | `-H "Authorization: Bearer YOUR_API_KEY"` | Authentication → **Header Auth** |
| **Header 커스텀** | `-H "X-API-Key: YOUR_API_KEY"` | Send Headers에 직접 추가 |
| **Query Parameter** | `?appid=YOUR_API_KEY` | Query Parameters에 `appid` 추가 |

### 3-3. n8n Credential 등록 방법

#### 방법 A — Header Auth (권장, Upstage 등)

1. n8n 좌측 **Credentials** → **Add Credential**
2. **Header Auth** 선택
3. 아래처럼 입력

| 필드 | 값 |
|------|-----|
| **Name** | `Authorization` |
| **Value** | `Bearer 발급받은_API_키` |

4. HTTP Request 노드 → **Authentication** → **Generic Credential Type** → **Header Auth** 선택

#### 방법 B — Query Parameter에 직접 입력 (OpenWeatherMap 등)

- Credential 없이 HTTP Request → **Query Parameters**에 `appid` = `발급받은_키` 입력
- 실습용으로는 가능하지만, **Credential 사용을 권장**합니다.

#### 방법 C — OAuth2 (카카오톡 등)

- 카카오, Google 등 로그인 기반 API는 **OAuth2 API** Credential 사용
- 상세: `카카오톡 API(나에게 보내기) 설정 방법.txt` 참고

---

## 4. n8n HTTP Request 노드 설정

### 4-1. 노드 추가

1. 워크플로우 캔버스에서 **+** 클릭
2. 검색창에 `HTTP Request` 입력 후 선택

### 4-2. 기본 설정

| 항목 | 설명 |
|------|------|
| **Method** | `GET`, `POST`, `PUT`, `PATCH`, `DELETE` |
| **URL** | API 엔드포인트 전체 주소 |
| **Authentication** | API Key 방식에 맞게 선택 (없으면 `None`) |

### 4-3. Parameter 종류별 설정

#### (1) Query Parameters — URL 뒤 `?이름=값`

**Send Query Parameters** 토글 ON

| Name | Value |
|------|-------|
| `q` | `Seoul` |
| `units` | `metric` |
| `lang` | `kr` |
| `appid` | `발급받은_API_키` |

> Expression 사용: Value 옆 **fx** 클릭 → `={{ $json.cityName }}`

#### (2) Header Parameters — 요청 헤더

**Send Headers** 토글 ON

| Name | Value |
|------|-------|
| `Content-Type` | `application/json` |
| `Authorization` | `Bearer 발급받은_API_키` (Credential 미사용 시) |

#### (3) Body Parameters — POST/PUT 요청 본문

**Send Body** 토글 ON → **Body Content Type** 선택

| Body Type | 용도 | n8n 설정 |
|-----------|------|----------|
| **JSON** | REST API 일반 | Body Parameters 또는 **JSON** 직접 입력 |
| **Form-Data (multipart)** | 파일 업로드 | Parameter Type: **Form Data** / **n8n Binary File** |
| **Form Urlencoded** | 카카오톡 등 | Body Content Type: `application/x-www-form-urlencoded` |

### 4-4. Expression으로 동적 값 넣기

이전 노드 데이터를 Parameter에 넣을 때:

| 용도 | Expression 예시 |
|------|-----------------|
| 현재 아이템 필드 | `={{ $json.userId }}` |
| 특정 노드 참조 | `={{ $('HTTP Request').item.json.userId }}` |
| URL에 직접 삽입 | `https://api.example.com/users/{{ $json.id }}` |

### 4-5. 실행 및 결과 확인

1. 노드 선택 → **Execute step** (또는 **Test workflow**)
2. **OUTPUT** 탭에서 응답 JSON 확인
3. 오류 시 **Status Code**, **error message** 확인

---

## 5. curl로 파라미터 설정하기

### 5-1. curl 기본 구조

```bash
curl [옵션] "URL"
```

| 옵션 | 의미 | n8n 대응 |
|------|------|----------|
| `-X POST` | HTTP Method | Method: `POST` |
| `-H "키: 값"` | Header | Send Headers |
| `-d 'JSON문자열'` | JSON Body | Send Body → JSON |
| `-F "키=값"` | Form Data (파일 포함) | Send Body → multipart-form-data |
| `-G --data-urlencode` | GET Query | Send Query Parameters |
| `-u user:pass` | Basic Auth | Authentication → Basic Auth |

### 5-2. GET + Query Parameter

```bash
# OpenWeatherMap — 서울 현재 날씨
curl -G "https://api.openweathermap.org/data/2.5/weather" \
  --data-urlencode "q=Seoul" \
  --data-urlencode "appid=YOUR_API_KEY" \
  --data-urlencode "units=metric" \
  --data-urlencode "lang=kr"
```

**한 줄로 쓰기:**

```bash
curl "https://api.openweathermap.org/data/2.5/weather?q=Seoul&appid=YOUR_API_KEY&units=metric&lang=kr"
```

### 5-3. GET + Header 인증 (Bearer Token)

```bash
curl -X GET "https://api.example.com/v1/data" \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json"
```

### 5-4. POST + JSON Body

```bash
curl -X POST "https://api.example.com/v1/chat" \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "solar-mini",
    "messages": [
      {"role": "user", "content": "안녕하세요"}
    ]
  }'
```

### 5-5. POST + Form Data (파일 업로드)

```bash
# Upstage Document Parse
curl -X POST "https://api.upstage.ai/v1/document-digitization" \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -F "model=document-parse" \
  -F 'output_formats=["markdown"]' \
  -F "document=@./sample.pdf"
```

| curl 옵션 | 설명 |
|-----------|------|
| `-F "model=document-parse"` | 일반 Form 필드 |
| `-F "document=@./sample.pdf"` | `@` = 파일 경로 지정 |
| `-F 'output_formats=["markdown"]'` | JSON 배열 문자열 그대로 전달 |

### 5-6. POST + Form Urlencoded

```bash
curl -X POST "https://kapi.kakao.com/v2/api/talk/memo/default/send" \
  -H "Authorization: Bearer ACCESS_TOKEN" \
  -H "Content-Type: application/x-www-form-urlencoded;charset=utf-8" \
  -d "template_object={\"object_type\":\"text\",\"text\":\"테스트 메시지\"}"
```

### 5-7. curl 응답 확인 옵션

```bash
# HTTP 상태 코드만 보기
curl -o /dev/null -s -w "%{http_code}" "https://api.example.com/health"

# 응답 헤더 + 본문 함께 보기
curl -i "https://api.example.com/data"

# JSON 예쁘게 보기 (jq 설치 시)
curl -s "https://api.example.com/data" | jq .
```

### 5-8. Windows PowerShell에서 curl

Windows 10/11에는 `curl.exe`가 기본 포함되어 있습니다. PowerShell에서 아래처럼 실행하세요.

```powershell
# JSON Body — 작은따옴표 대신 큰따옴표, 내부 따옴표는 `\"` 이스케이프
curl.exe -X POST "https://api.example.com/v1/chat" `
  -H "Authorization: Bearer YOUR_API_KEY" `
  -H "Content-Type: application/json" `
  -d "{\"model\":\"solar-mini\",\"messages\":[{\"role\":\"user\",\"content\":\"안녕\"}]}"

# 파일 업로드
curl.exe -X POST "https://api.upstage.ai/v1/document-digitization" `
  -H "Authorization: Bearer YOUR_API_KEY" `
  -F "model=document-parse" `
  -F "output_formats=[`"markdown`"]" `
  -F "document=@.\sample.pdf"
```

> PowerShell에서 `curl`만 입력하면 `Invoke-WebRequest` 별칭이 실행될 수 있습니다. **`curl.exe`** 를 명시하세요.

---

## 6. curl → n8n 변환표

| curl | n8n HTTP Request |
|------|------------------|
| `-X GET` | Method: `GET` |
| `-X POST` | Method: `POST` |
| `"https://api.../path"` | URL |
| `-H "Authorization: Bearer KEY"` | Credential: Header Auth (`Authorization` / `Bearer KEY`) |
| `-H "Content-Type: application/json"` | Send Headers → `Content-Type` |
| `?q=Seoul&appid=KEY` | Send Query Parameters |
| `-d '{"key":"value"}'` | Send Body → JSON |
| `-F "field=value"` | Send Body → multipart → Form Data |
| `-F "file=@./a.pdf"` | Send Body → multipart → Type: **n8n Binary File** |
| `-d "a=1&b=2"` (urlencoded) | Send Body → Form Urlencoded |

### 변환 실습 예시

**curl:**

```bash
curl -G "https://www.kamis.or.kr/service/price/xml.do" \
  --data-urlencode "action=dailyPriceByCategoryList" \
  --data-urlencode "p_productcls_code=01" \
  --data-urlencode "p_item_category_code=200" \
  --data-urlencode "p_regday=2026-07-08" \
  --data-urlencode "p_cert_key=YOUR_CERT_KEY" \
  --data-urlencode "p_cert_id=YOUR_CERT_ID" \
  --data-urlencode "p_returntype=json"
```

**n8n HTTP Request:**

| 설정 | 값 |
|------|-----|
| Method | `GET` |
| URL | `https://www.kamis.or.kr/service/price/xml.do` |
| Send Query Parameters | 아래 표 참고 |

| Name | Value |
|------|-------|
| `action` | `dailyPriceByCategoryList` |
| `p_productcls_code` | `01` |
| `p_item_category_code` | `200` |
| `p_regday` | `2026-07-08` |
| `p_cert_key` | `YOUR_CERT_KEY` |
| `p_cert_id` | `YOUR_CERT_ID` |
| `p_returntype` | `json` |

---

## 7. 실습 예제 3종

### 예제 1 — 공개 API (API Key 불필요)

**목표:** JSONPlaceholder에서 게시글 1건 조회

```bash
curl "https://jsonplaceholder.typicode.com/posts/1"
```

| n8n 설정 | 값 |
|----------|-----|
| Method | `GET` |
| URL | `https://jsonplaceholder.typicode.com/posts/1` |
| Authentication | `None` |

---

### 예제 2 — Upstage Document Parse (Header Auth + 파일)

**curl 테스트:**

```bash
curl -X POST "https://api.upstage.ai/v1/document-digitization" \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -F "model=document-parse" \
  -F 'output_formats=["markdown"]' \
  -F "document=@./sample.pdf"
```

| n8n 설정 | 값 |
|----------|-----|
| Method | `POST` |
| URL | `https://api.upstage.ai/v1/document-digitization` |
| Authentication | Header Auth (`Authorization` / `Bearer YOUR_API_KEY`) |
| Send Body | ON, Content Type: `multipart-form-data` |

| Body Parameter | Type | Value |
|----------------|------|-------|
| `model` | Form Data | `document-parse` |
| `output_formats` | Form Data | `["markdown"]` |
| `document` | n8n Binary File | Input Field: `file` |

---

### 예제 3 — OpenWeatherMap (Query Parameter에 API Key)

**curl 테스트:**

```bash
curl "https://api.openweathermap.org/data/2.5/weather?q=Seoul&appid=YOUR_API_KEY&units=metric&lang=kr"
```

| n8n 설정 | 값 |
|----------|-----|
| Method | `GET` |
| URL | `https://api.openweathermap.org/data/2.5/weather` |
| Send Query Parameters | ON |

| Name | Value |
|------|-------|
| `q` | `Seoul` |
| `appid` | `YOUR_API_KEY` |
| `units` | `metric` |
| `lang` | `kr` |

---

## 8. 자주 하는 실수와 해결

| 증상 | 원인 | 해결 |
|------|------|------|
| `401 Unauthorized` | API Key 오류·만료 | 키 재발급, `Bearer ` 접두어 확인 |
| `403 Forbidden` | 권한·요금제 부족 | API 콘솔에서 사용량·권한 확인 |
| `404 Not Found` | URL 오타 | Base URL + Path 다시 확인 |
| `400 Bad Request` | Body/Parameter 형식 오류 | curl과 n8n Parameter 이름·타입 일치 확인 |
| `415 Unsupported Media Type` | Content-Type 불일치 | `application/json` vs `multipart/form-data` 확인 |
| curl은 되는데 n8n만 실패 | 인증 방식 다름 | curl의 `-H`, `-d`, `-F`를 n8n 항목에 1:1 대응 |
| 파일 업로드 실패 | Binary 필드명 불일치 | API 문서의 필드명(`document`, `file` 등) 확인 |
| PowerShell curl 오류 | `Invoke-WebRequest` 실행됨 | `curl.exe` 사용 |

### 디버깅 체크리스트

- [ ] API 문서의 **Example cURL**과 내 curl이 동일한가?
- [ ] curl에서 **200 OK** 응답이 오는가?
- [ ] n8n Method, URL, Auth가 curl과 같은가?
- [ ] Query / Header / Body 중 **어디에** 파라미터를 넣는지 맞는가?
- [ ] API Key에 공백·줄바꿈이 들어가지 않았는가?

---

## 참고 링크

| 자료 | URL |
|------|-----|
| n8n HTTP Request 공식 문서 | https://docs.n8n.io/integrations/builtin/core-nodes/n8n-nodes-base.httprequest/ |
| Upstage API 문서 | https://console.upstage.ai/docs |
| OpenWeatherMap API | https://openweathermap.org/api |
| JSONPlaceholder (연습용) | https://jsonplaceholder.typicode.com |

---

## 빠른 요약

1. **API 문서**에서 URL, Method, 인증 방식, Parameter 위치를 확인한다.
2. **curl로 먼저** 호출해 200 응답을 받는다.
3. n8n **HTTP Request**에 curl 내용을 그대로 옮긴다.
4. API Key는 가능하면 **Credential**(Header Auth 등)에 저장한다.
5. Parameter는 **Query / Header / Body** 중 문서가 지정한 위치에 넣는다.
