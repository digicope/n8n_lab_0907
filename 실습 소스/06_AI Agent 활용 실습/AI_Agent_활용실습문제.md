# n8n AI Agent 심화 Workflow 실습 (Gemini 3.5-flash)

> **교육 과정:** 생성형 AI 활용 교육  
> **선수 과목:** `n8n_AI_Agent_실습` 완료 필수 (`n8n_AI_활용_실습` 병행 권장)  
> **사용 API:** [Google Gemini API](https://aistudio.google.com) · [OpenWeatherMap](https://openweathermap.org) · [KAMIS](https://www.kamis.or.kr) · [카카오톡 API](https://developers.kakao.com)  
> **모델:** 모든 실습에서 **`gemini-3.5-flash`** 사용  
> **답안 위치:** `답안/` 폴더의 개별 JSON 파일 → n8n **Import from File**로 바로 가져오기

---

## 사전 준비

| 항목 | 내용 |
|------|------|
| n8n | Cloud 또는 로컬 설치 ([n8n.io](https://n8n.io)) — **1.90 이상** 권장 (HTTP Request Tool 신규 방식) |
| Gemini API Key | [Google AI Studio](https://aistudio.google.com/apikey)에서 발급 |
| OpenWeatherMap API Key | [openweathermap.org](https://openweathermap.org/api)에서 발급 (기존 실습 Credential 재사용) |
| KAMIS Open API | [KAMIS Open-API](https://www.kamis.or.kr/customer/reference/openapi_list.do)에서 `p_cert_key`, `p_cert_id` 발급 |
| 카카오톡 OAuth2 | `카카오톡 API(나에게 보내기) 설정 방법.txt` 참고 (기존 Credential 재사용) |
| 인터넷 | Wikipedia Tool, HTTP Request Tool 실행 시 필요 |

### Credential 등록

1. n8n → **Credentials** → **Add Credential**
2. **Google Gemini(PaLM) API** 검색 후 선택 → API Key 입력 후 저장
3. **OpenWeatherMap Tool** 노드 → **OpenWeatherMap API** Credential 연결 (기존 실습 Credential 재사용)
4. Import한 답안의 **HTTP Request Tool** 노드에서 아래 값을 본인 키로 교체:
   - **KAMIS 농산물 가격** → Query Parameter `p_cert_key`, `p_cert_id`
5. **카카오톡 나에게 보내기** Tool → **OAuth2 API** Credential 연결 (Scope: `talk_message`)

Import한 답안 워크플로우의 **Google Gemini Chat Model** 서브노드에 Credential을 연결하세요.

### 기초 vs 활용 실습 비교

| 구분 | AI Agent 기초 실습 | AI Agent 활용 실습 (이번) |
|------|-------------------|--------------------------|
| Tool | Calculator, Date & Time | **HTTP Request, Code, Wikipedia** |
| 출력 | 자유 텍스트 | **Structured JSON** 포함 |
| 트리거 | Chat Trigger만 | **Webhook + Chat** |
| Agent 설정 | System Message | **Max Iterations, Output Parser** |
| 외부 연동 | 없음 | **REST API, Wikipedia** |
| 종합 | Memory + 2개 Tool | **5개 이상 Tool + 구조화 출력** |

### 이번 실습에서 배우는 것

- **HTTP Request Tool** — Agent가 REST API를 직접 호출
- **앱 노드 as Tool** — OpenWeatherMap Tool 등 n8n 내장 Tool 노드를 Agent에 연결
- **Code Tool** — JavaScript로 커스텀 비즈니스 로직 구현
- **Structured Output Parser** — Agent 응답을 JSON 스키마로 강제
- **Wikipedia Tool** — 실시간 지식 검색
- **다중 Tool 오케스트레이션** — Agent가 상황에 맞는 Tool 자동 선택
- **Max Iterations** — 복합 추론·다단계 Tool 호출
- **Webhook + Agent** — 외부 앱·서비스에서 Agent 호출
- **종합 고객지원 Agent** — 실무형 멀티 Tool 설계

---

## 공통 설정 (실습 1~8)

| 공통 항목 | 설정 |
|-----------|------|
| **Google Gemini Chat Model** | Model: `gemini-3.5-flash`, Temperature: 실습별 상이 |
| **AI Agent — Prompt Source** | Chat 실습: **Connected Chat Trigger node** |
| **Simple Memory** (해당 실습) | Session Key: `={{ $json.sessionId }}` |
| **OpenWeatherMap Tool** (실습 1·5·6·7·8) | 노드 타입: `n8n-nodes-base.openWeatherMapTool` — 일반 OpenWeatherMap 노드가 아님 |

> **모델명 주의:** n8n에서 `models/gemini-3.5-flash`로 표시됩니다. Google AI Studio에서 해당 모델이 보이지 않으면 최신 n8n으로 업데이트하거나, 사용 가능한 최신 Flash 모델로 교체하세요.

---

## 실습 1. 앱 노드 + HTTP Request Tool — 실생활 API 연동 Agent

### 목표

n8n **OpenWeatherMap Tool** 노드와 **HTTP Request Tool** 2개를 Agent에 연결해, **날씨**, **KAMIS 농산물 가격**, **카카오톡 나에게 보내기**를 처리합니다.

### 요구사항
(KAMIS는 안될 경우 생략!!)

```
When chat message received → AI Agent
                           ↑    ↑    ↑
              Google Gemini   OpenWeatherMap Tool
                              KAMIS (HTTP Request Tool)
                              카카오톡 (HTTP Request Tool)
```

| 노드 | 설정 |
|------|------|
| **OpenWeatherMap Tool** | Operation: **Current Weather** (기본) |
| | City Name: `={{ $fromAI('cityName', '도시명 (예: Seoul, 청주시)', 'string') }}` |
| | Language: `kr` |
| | **OpenWeatherMap API** Credential 연결 |
| | Agent **Tool** 슬롯에 연결 (`ai_tool`) |
| **HTTP Request Tool (농산물)** | Method: `GET` |
| | URL: `https://www.kamis.or.kr/service/price/xml.do` |
| | Query: `action` = `dailyPriceByCategoryList` |
| | Query: `p_productcls_code` = `01` (소매) |
| | Query: `p_item_category_code` = `={{ $fromAI('item_code', '부류코드 (딸기:200, 고구마:100, 배추:212)', 'string') }}` |
| | Query: `p_regday` = `={{ $fromAI('regday', '조회일 YYYY-MM-DD', 'string') }}` |
| | Query: `p_cert_key`, `p_cert_id` = **본인 KAMIS 인증 정보** |
| | Query: `p_returntype` = `json` |
| | Tool Description: `KAMIS에서 농산물 소매 가격을 조회합니다. item_code는 부류코드(딸기:200, 고구마:100, 배추:212), regday는 조회일 YYYY-MM-DD입니다.` |
| **HTTP Request Tool (카카오톡)** | Method: `POST` |
| | URL: `https://kapi.kakao.com/v2/api/talk/memo/default/send` |
| | Authentication: **OAuth2 API** (카카오 Credential) |
| | Body: `template_object` = JSON (`text`에 `$fromAI('message', ...)` 사용) |
| | Tool Description: `카카오톡 나에게 보내기로 텍스트 메시지를 전송합니다.` |
| **AI Agent** | System Message: 아래 내용 |
| **Google Gemini Chat Model** | Model: `gemini-3.5-flash`, Temperature: `0.2` |

**날짜가 틀릴경우 모델을 gemin-flash-latest로 변경**

**KAMIS 부류코드 참고** (`Google Sheets에서 찾은 부류코드.txt`)

| 품목 | 부류코드 | 품목 | 부류코드 |
|------|----------|------|----------|
| 고구마 | 100 | 딸기 | 200 |
| 배추 | 200 | 사과 | 400 |

**System Message**

```
당신은 한국어 생활 정보 Agent입니다.

[도구 선택]
- 날씨·기온 질문 → OpenWeatherMap Tool (cityName 필요)
- 농산물·채소·과일 가격 → KAMIS 농산물 가격 (item_code, regday 필요)
  ※ "어제", "최근"이면 regday를 YYYY-MM-DD로 계산해 전달
- 카카오톡 전송 요청 → 카카오톡 나에게 보내기 (message 필요)

[규칙]
- API 도구 없이 추측하지 마세요.
- 응답은 한국어 존댓말, 3~5문장
```

### 테스트 시나리오

**1번 — 날씨**

```
서울시 지금 날씨와 기온 알려줘.
```

**2번 — 농산물 가격**

```
당근 소매 가격을 오늘 기준으로 알려줘. (부류코드 200)
카카오톡으로 나에게 보내줘.
```

**3번 — 카카오톡 알림**

```
"서울 날씨 확인 완료"라는 문구를 카카오톡으로 나에게 보내줘.
```

### 확인 사항

- [ ] **OpenWeatherMap Tool** 노드가 Agent **Tool** 슬롯에 연결되었는가?
- [ ] HTTP Request Tool **2개**(KAMIS, 카카오톡)가 Agent에 연결되었는가?
- [ ] OpenWeatherMap **Credential**, KAMIS `p_cert_key`/`p_cert_id`를 설정했는가?
- [ ] 카카오톡 Tool에 OAuth2 Credential이 연결되었는가?
- [ ] 1번: OpenWeatherMap 호출 + 기온·날씨 상태 응답
- [ ] 2번: KAMIS Tool 호출 + 가격 데이터 응답
- [ ] 3번: 카카오톡 Tool 호출 + 휴대폰에 메시지 수신

### 힌트

- OpenWeatherMap은 일반 노드가 아닌 **OpenWeatherMap Tool** 노드를 Agent Tool 슬롯에 연결합니다
- Agent에 Tool 추가 시 노드 검색: `OpenWeatherMap` → **OpenWeatherMap Tool** 선택 후 AI Agent의 **Tool** 영역에 드래그
- City Name에 `$fromAI('cityName', ...)` 를 넣으면 Agent가 질문에서 도시명을 자동 추출합니다
- OpenWeatherMap·카카오톡 Credential 설정은 `OpenWeatherMap-카카오톡API 호출.json` 워크플로우를 참고하세요
- KAMIS `p_regday`는 **하루 전 날짜**를 쓰면 데이터가 잘 조회됩니다 (`Google Sheets에서 찾은 부류코드.txt` 참고)
- KAMIS·카카오톡은 **`n8n-nodes-base.httpRequestTool`** 사용

---

## 실습 2. Code Tool — 부가세 계산 Agent

### 목표

**Code Tool**에 JavaScript 로직을 작성해, Agent가 **부가세(10%) 계산**을 커스텀 도구로 수행하게 합니다.

### 요구사항

```
When chat message received → AI Agent
                           ↑    ↑
              Google Gemini   Code Tool (VAT_Calculator)
```

| 노드 | 설정 |
|------|------|
| **Code Tool** | Name: `VAT_Calculator` |
| | Description: `공급가액(숫자)을 입력받아 부가세 10%와 합계금액을 계산합니다.` |
| | Language: `JavaScript` |
| | Code: 아래 내용 |
| **AI Agent** | System Message: 아래 내용 |
| **Google Gemini Chat Model** | Model: `gemini-3.5-flash`, Temperature: `0.2` |

**Code Tool JavaScript**

```javascript
const amount = parseFloat(query);
if (isNaN(amount) || amount < 0) {
  return '유효한 양수 금액을 입력하세요.';
}
const vat = Math.round(amount * 0.1);
const total = amount + vat;
return `공급가액: ${amount.toLocaleString()}원 | 부가세(10%): ${vat.toLocaleString()}원 | 합계: ${total.toLocaleString()}원`;
```

**System Message**

```
당신은 한국 세무 계산 도우미 Agent입니다.
- 금액·부가세·합계 계산 → 반드시 VAT_Calculator 도구 사용
- 도구 결과를 그대로 사용자에게 전달하세요.
- 한국어 존댓말, 3문장 이내
```

### 테스트 메시지

```
공급가액 1,250,000원의 부가세와 합계를 계산해줘.
```

### 확인 사항

- [ ] Code Tool이 Agent에 연결되었는가?
- [ ] Agent가 VAT_Calculator를 호출했는가?
- [ ] 부가세 **125,000원**, 합계 **1,375,000원**이 응답에 포함되는가?

### 힌트

- Code Tool의 입력은 `query` 변수로 접근합니다
- Tool Name은 영문·숫자·언더스코어만 사용 (`VAT_Calculator`)

---

## 실습 3. Structured Output Parser — 문의 분류 Agent

### 목표

**Structured Output Parser**를 Agent에 연결해, 고객 문의를 **JSON 형식**으로 분류·응답합니다.

### 요구사항

```
When chat message received → AI Agent (+ hasOutputParser)
                           ↑    ↑              ↑
              Google Gemini   Simple Memory   Structured Output Parser
```

| 노드 | 설정 |
|------|------|
| **AI Agent** | **Require Specific Output Format** 활성화 (`hasOutputParser: true`) |
| | System Message: 아래 내용 |
| **Structured Output Parser** | Schema Type: **Generate from JSON Example** |
| | JSON Example: 아래 내용 |
| **Simple Memory** | Session Key: `={{ $json.sessionId }}`, Context: `8` |
| **Google Gemini Chat Model** | Model: `gemini-3.5-flash`, Temperature: `0.1` |

**JSON Example**

```json
{
  "category": "billing",
  "priority": "high",
  "summary": "결제 오류 문의",
  "suggested_action": "결제팀 에스컬레이션"
}
```

**System Message**

```
당신은 고객 문의 분류 Agent입니다.
사용자 메시지를 분석하여 JSON으로만 응답하세요.

category: billing | technical | shipping | general 중 하나
priority: high | medium | low
summary: 한 줄 요약 (한국어)
suggested_action: 권장 조치 (한국어)
```

### 테스트 메시지

```
어제 결제했는데 카드에서 두 번 빠졌어요. 환불해 주세요!
```

### 확인 사항

- [ ] Structured Output Parser가 Agent **Output Parser** 슬롯에 연결되었는가?
- [ ] 응답이 JSON 구조(`category`, `priority`, `summary`, `suggested_action`)를 따르는가?
- [ ] `category`가 `billing`, `priority`가 `high`인가?

### 힌트

- AI Agent → **Add Option** → **Require Specific Output Format** 체크
- Temperature `0.1`로 낮추면 JSON 형식 준수율이 올라갑니다

---

## 실습 4. Wikipedia Tool — 지식 검색 Agent

### 목표

**Wikipedia Tool**을 연결해, Agent가 **실시간 위키피디아 검색**으로 사실 확인 후 답변합니다.

### 요구사항

```
When chat message received → AI Agent
                           ↑    ↑    ↑
              Google Gemini   Simple Memory   Wikipedia
```

| 노드 | 설정 |
|------|------|
| **Wikipedia** | 기본 설정 (Tool 서브노드) |
| **AI Agent** | System Message: 아래 내용 |
| **Simple Memory** | Session Key: `={{ $json.sessionId }}`, Context: `10` |
| **Google Gemini Chat Model** | Model: `gemini-3.5-flash`, Temperature: `0.3` |

**System Message**

```
당신은 사실 확인 기반 한국어 리서치 Agent입니다.
- 역사, 인물, 과학, 지리 등 사실 질문 → 반드시 Wikipedia 도구로 검색 후 답변
- 검색 결과에 없는 내용은 추측하지 말고 "확인할 수 없습니다"라고 답하세요.
- 답변 형식: 핵심 2~3문장 + 출처(Wikipedia) 명시
```

### 테스트 메시지

```
앨런 튜링은 어떤 업적을 남겼어? Wikipedia로 확인해줘.
```

### 확인 사항

- [ ] Wikipedia Tool이 Agent에 연결되었는가?
- [ ] 실행 로그에 Wikipedia 검색이 보이는가?
- [ ] 앨런 튜링 관련 사실(암호 해독, 튜링 테스트 등)이 응답에 포함되는가?

### 힌트

- Wikipedia Tool은 API Key 없이 사용 가능합니다
- 인터넷 연결이 필요합니다

---

## 실습 5. 다중 Tool — 리서치 비서 Agent

### 목표

**OpenWeatherMap Tool + KAMIS + 카카오톡 + Wikipedia + Calculator + Date & Time + Memory** 7개 Tool을 결합한 **리서치 비서 Agent**를 만듭니다.

### 요구사항
(KAMIS는 안될 경우 생략!!)

```
When chat message received → AI Agent
                           ↑    ↑    ↑    ↑    ↑    ↑    ↑
              Google Gemini   Memory   OpenWeatherMap Tool   KAMIS
                                    카카오톡   Wikipedia   Calculator   Date & Time
```

| 노드 | 설정 |
|------|------|
| **AI Agent** | Max Iterations: `10` |
| | System Message: 아래 내용 |
| **OpenWeatherMap Tool** | City Name: `={{ $fromAI('cityName', '도시명', 'string') }}`, Language: `kr`, Credential 연결 |
| **KAMIS 농산물 가격** | 실습 1과 동일 (HTTP Request Tool) |
| **카카오톡 나에게 보내기** | 실습 1과 동일 (HTTP Request Tool) |
| **Simple Memory** | Context: `15` |
| **Google Gemini Chat Model** | Model: `gemini-3.5-flash`, Temperature: `0.3` |

**System Message**

```
당신은 만능 리서치 비서 Agent입니다.

[도구 선택 규칙]
1. 사실·인물·역사 질문 → Wikipedia
2. 날씨·기온 질문 → OpenWeatherMap Tool (cityName 필요)
3. 농산물·채소·과일 가격 → KAMIS (item_code, regday 필요)
4. 카카오톡 전송 요청 → 카카오톡 나에게 보내기 (message 필요)
5. 숫자 계산 → Calculator
6. 현재 날짜·시간 → Date & Time

[응답 규칙]
- 사용한 도구명을 첫 줄에 명시
- 한국어 존댓말, 5문장 이내
```

### 종합 테스트 시나리오 (같은 채팅창)

**1번**

```
지금 몇 시야?
```

**2번**

```
서울시 지금 날씨와 기온 알려줘.
```

**3번**

```
아까 몇 시라고 했지?
```

### 확인 사항

- [ ] 7개 Tool + Memory가 모두 연결되었는가?
- [ ] OpenWeatherMap Tool Credential, KAMIS·카카오톡 키/Credential 설정 완료
- [ ] 1번: Date & Time 사용
- [ ] 2번: OpenWeatherMap Tool 사용 + 기온·날씨 응답
- [ ] 3번: Memory로 이전 시각 기억

---

## 실습 6. 복합 추론 — 여행 경비 플래너 Agent

### 목표

**Max Iterations**와 **다중 Tool**을 활용해, 한 번의 질문에 **여러 도구를 연쇄 호출**하는 복합 추론 Agent를 만듭니다. 실습 1과 동일한 **OpenWeatherMap Tool · KAMIS · 카카오톡** API를 포함합니다.

### 요구사항
(KAMIS는 안될 경우 생략!!)

```
When chat message received → AI Agent (Max Iterations: 12)
                           ↑    ↑    ↑    ↑    ↑    ↑    ↑
              Google Gemini   Memory   OpenWeatherMap Tool   KAMIS   카카오톡
                                    Calculator   Date & Time   Wikipedia
```

| 노드 | 설정 |
|------|------|
| **AI Agent** | Max Iterations: `12` |
| | System Message: 아래 내용 |
| **OpenWeatherMap Tool** | 실습 1과 동일 (`$fromAI` cityName, Credential 연결) |
| **KAMIS 농산물 가격** | 실습 1과 동일 (HTTP Request Tool) |
| **카카오톡 나에게 보내기** | 실습 1과 동일 (HTTP Request Tool) |
| **Google Gemini Chat Model** | Model: `gemini-3.5-flash`, Temperature: `0.25` |

**System Message**

```
당신은 해외여행 경비 플래너 Agent입니다.

[작업 순서]
1. 목적지 정보 → Wikipedia
2. 목적지 날씨 → OpenWeatherMap Tool (cityName 필요)
3. 현재 날짜 → Date & Time
4. 경비 계산 → Calculator (사용자 제공 금액 기준)
5. 식재료 가격 참고 필요 시 → KAMIS (item_code, regday)
6. 요약 전송 요청 시 → 카카오톡 나에게 보내기 (message)

[응답 형식]
📍 목적지: (한 줄)
🌤️ 날씨: (OpenWeatherMap Tool 결과)
📅 기준일: (Date & Time 결과)
💰 예상 경비: (Calculator 결과, 원화)
📝 참고: (Wikipedia 팁 1문장)
```

### 테스트 메시지

```
도쿄 3박 4일 여행인데, 1일 숙박비 12만 원, 1일 식비 5만 원, 교통비 1일 2만 원이야.
오늘 날짜 기준으로 총 경비를 계산하고, 도쿄 날씨와 Wikipedia 정보를 알려줘.
```

### 확인 사항

- [ ] OpenWeatherMap Tool Credential, KAMIS·카카오톡 키/Credential 설정 완료
- [ ] Calculator로 총 경비 **64만 원** (3박 숙박 36만 + 4일 식비 20만 + 4일 교통 8만) 근처 계산
- [ ] Date & Time으로 오늘 날짜 표시
- [ ] OpenWeatherMap Tool으로 도쿄 날씨 포함
- [ ] Wikipedia로 도쿄 관련 정보 포함
- [ ] 실행 로그에 **4개 이상 Tool 호출** 확인

### 힌트

- 복잡한 질문일수록 Max Iterations를 `10~15`로 설정하세요
- System Message에 **작업 순서**를 명시하면 Tool 호출 성공률이 올라갑니다

---

## 실습 7. Webhook + AI Agent — 외부 앱 연동

### 목표

**Webhook** 트리거로 외부에서 메시지를 받아 Agent가 처리하고, **JSON 응답**을 반환합니다. 실습 1과 동일한 **OpenWeatherMap Tool · KAMIS · 카카오톡** API를 Webhook으로 호출합니다.

### 요구사항
(KAMIS는 안될 경우 생략!!)

```
Webhook (POST) → AI Agent → Respond to Webhook
                      ↑
         Google Gemini + OpenWeatherMap Tool + KAMIS + 카카오톡
                         + Calculator + Date & Time
```

| 노드 | 설정 |
|------|------|
| **Webhook** | Method: `POST`, Path: `agent-assistant` |
| | Response Mode: **Using 'Respond to Webhook' Node** |
| **AI Agent** | Prompt Source: **Define below** |
| | Prompt (User Message): `={{ $json.body.message }}` |
| | System Message: 아래 내용 |
| **OpenWeatherMap Tool** | 실습 1과 동일 (`$fromAI` cityName, Credential 연결) |
| **KAMIS 농산물 가격** | 실습 1과 동일 (HTTP Request Tool) |
| **카카오톡 나에게 보내기** | 실습 1과 동일 (HTTP Request Tool) |
| **Respond to Webhook** | Respond With: `JSON` |
| | Response Body: `={{ { "reply": $json.output, "timestamp": $now.toISO() } }}` |
| **Google Gemini Chat Model** | Model: `gemini-3.5-flash`, Temperature: `0.3` |

**System Message**

```
당신은 Webhook API용 업무 비서입니다.

[도구 선택]
- 날씨·기온 → OpenWeatherMap Tool (cityName)
- 농산물 가격 → KAMIS (item_code, regday)
- 카카오톡 전송 → 카카오톡 나에게 보내기 (message)
- 계산 → Calculator
- 시간 → Date & Time

3문장 이내 한국어 존댓말로 답변하세요.
```

### 테스트 방법

1. 워크플로우 **Activate** (또는 Test URL 사용)
2. 아래 curl 명령 실행 (Test URL로 교체)

**계산 테스트**

```bash
curl -X POST "https://YOUR-N8N-URL/webhook-test/agent-assistant" -H "Content-Type: application/json" -d "{\"message\": \"연봉 6,000만 원을 12로 나누면 월급이 얼마야?\"}"
```

**날씨 테스트**

```bash
curl -X POST "https://YOUR-N8N-URL/webhook-test/agent-assistant" -H "Content-Type: application/json" -d "{\"message\": \"서울시 지금 날씨와 기온 알려줘.\"}"
```

### 확인 사항

- [ ] Webhook → Agent → Respond to Webhook 연결이 되어 있는가?
- [ ] OpenWeatherMap Tool Credential, KAMIS·카카오톡 키/Credential 설정 완료
- [ ] JSON 응답에 `reply`와 `timestamp` 필드가 있는가?
- [ ] 계산 테스트: `reply`에 월급 **500만 원** 근처 답변
- [ ] 날씨 테스트: `reply`에 기온·날씨 상태 포함

### 힌트

- Webhook 실습은 Chat Trigger와 달리 Prompt를 **Expression**으로 직접 지정합니다
- Production URL은 워크플로우 Activate 후 Webhook 노드에서 확인

---

## 실습 8. 종합 — 지능형 고객지원 Agent

### 목표

이번 심화 과정의 모든 기능을 통합한 **실무형 고객지원 Agent**를 완성합니다.

### 요구사항

```
When chat message received → AI Agent (+ Output Parser)
                           ↑    ↑    ↑    ↑    ↑    ↑    ↑    ↑    ↑
              Google Gemini   Memory   OpenWeatherMap Tool   KAMIS   카카오톡
                                    OrderStatus   Wikipedia   Calculator   Date & Time
                                              Structured Output Parser
```

| 노드 | 설정 |
|------|------|
| **AI Agent** | Max Iterations: `15` |
| | Require Specific Output Format: **활성화** |
| | System Message: 아래 내용 |
| **OpenWeatherMap Tool** | 실습 1과 동일 (`$fromAI` cityName, Credential 연결) |
| **KAMIS 농산물 가격** | 실습 1과 동일 (HTTP Request Tool) |
| **카카오톡 나에게 보내기** | 실습 1과 동일 (HTTP Request Tool) |
| **Code Tool** | Name: `OrderStatus` — 주문번호(문자열) 입력 시 상태 반환 (시뮬레이션) |
| **Structured Output Parser** | JSON Example: 아래 내용 |
| **Simple Memory** | Context: `20` |
| **Google Gemini Chat Model** | Model: `gemini-3.5-flash`, Temperature: `0.2` |

**Code Tool — OrderStatus**

```javascript
const orderId = String(query).trim().toUpperCase();
const statuses = {
  'ORD-1001': '배송중 (송장: 1234567890)',
  'ORD-1002': '배송완료',
  'ORD-1003': '결제대기'
};
return statuses[orderId] || `주문번호 ${orderId}를 찾을 수 없습니다. ORD-1001~1003을 확인하세요.`;
```

**JSON Example (Output Parser)**

```json
{
  "intent": "order_inquiry",
  "answer": "고객에게 전달할 한국어 답변",
  "tools_used": ["OrderStatus"],
  "confidence": 0.95
}
```

**System Message**

```
당신은 전자상거래 고객지원 Agent입니다.

[도구 매핑]
- 주문 조회 (ORD-xxxx) → OrderStatus
- 상품/회사 정보 → Wikipedia
- 날씨·기온 → OpenWeatherMap Tool (cityName)
- 농산물·식재료 가격 → KAMIS (item_code, regday)
- 카카오톡 알림 전송 → 카카오톡 나에게 보내기 (message)
- 금액 계산 → Calculator
- 현재 시각 → Date & Time

[응답]
- 반드시 지정 JSON 형식으로 응답
- answer 필드는 고객에게 보낼 한국어 메시지
- tools_used에 실제 사용한 도구명 배열 기록
```

### 종합 테스트 시나리오

**1번**

```
주문번호 ORD-1001 배송 상태 알려줘.
```

**2번**

```
딸기(부류코드 200) 소매 가격을 어제 기준으로 알려줘.
```

**3번**

```
아까 조회한 주문번호가 뭐였지?
```

### 확인 사항

- [ ] 9개 Tool + Memory + Parser가 모두 연결되었는가?
- [ ] OpenWeatherMap Tool Credential, KAMIS·카카오톡 키/Credential 설정 완료
- [ ] 1번: OrderStatus → "배송중" + JSON `intent: order_inquiry`
- [ ] 2번: KAMIS Tool → 딸기 가격 데이터 응답
- [ ] 3번: Memory → ORD-1001 기억
- [ ] 모든 응답이 JSON 구조를 따르는가?

---

## 체크 포인트

| 실습 | 배점 | 핵심 평가 |
|------|------|-----------|
| 실습 1 | 10점 | OpenWeatherMap Tool + KAMIS·카카오톡 HTTP Tool |
| 실습 2 | 10점 | Code Tool JavaScript 작성 |
| 실습 3 | 15점 | Structured Output Parser + Agent |
| 실습 4 | 10점 | Wikipedia Tool 사실 검색 |
| 실습 5 | 15점 | 7개 Tool(OpenWeatherMap Tool·KAMIS·카카오톡 포함) 오케스트레이션 |
| 실습 6 | 15점 | 복합 추론 + OpenWeatherMap Tool·KAMIS·카카오톡 연쇄 호출 |
| 실습 7 | 10점 | Webhook + OpenWeatherMap Tool·KAMIS·카카오톡 API 연동 |
| 실습 8 | 15점 | 종합 멀티 Tool(실습1 API 통일) + 구조화 출력 |
| **합계** | **100점** | |

---

## Import 방법

1. n8n → **Workflows** → **⋯** → **Import from File**
2. `답안/` 폴더에서 해당 실습 JSON 선택
3. **Google Gemini Chat Model** → **Credential** 연결
4. Chat 실습: **Open Chat** / Webhook 실습: **Activate** 후 curl 테스트

| 실습 | 답안 파일 |
|------|-----------|
| 1 | `답안/실습1_HTTP_Tool_API조회.json` |
| 2 | `답안/실습2_Code_Tool_부가세계산.json` |
| 3 | `답안/실습3_Structured_Output_문의분류.json` |
| 4 | `답안/실습4_Wikipedia_지식검색.json` |
| 5 | `답안/실습5_다중Tool_리서치비서.json` |
| 6 | `답안/실습6_복합추론_여행플래너.json` |
| 7 | `답안/실습7_Webhook_외부연동.json` |
| 8 | `답안/실습8_종합_고객지원_Agent.json` |

---

## 자주 묻는 질문

**Q. HTTP Request Tool에서 `$fromAI`가 동작하지 않아요.**  
A. n8n **1.90 이상**인지 확인하세요. 구형 `toolHttpRequest` 노드가 있다면 삭제 후 `HTTP Request Tool`(httpRequestTool)을 새로 추가하세요.

**Q. Code Tool에서 `query is not defined` 오류가 납니다.**  
A. Code Tool은 Agent가 전달한 입력을 `query` 변수로 받습니다. `return`으로 문자열을 반환해야 합니다.

**Q. Structured Output Parser 응답이 깨져요.**  
A. Temperature를 `0.1~0.2`로 낮추고, System Message에 JSON 필드 설명을 명확히 적으세요.

**Q. Wikipedia Tool이 느리거나 실패해요.**  
A. 인터넷 연결과 n8n 서버의 외부 접근 권한을 확인하세요. 방화벽이 위키피디아를 차단할 수 있습니다.

**Q. Webhook 테스트 시 404가 납니다.**  
A. 워크플로우가 **Active** 상태인지, Test URL vs Production URL을 올바르게 사용하는지 확인하세요.

**Q. KAMIS API에서 데이터가 비어 있거나 오류가 납니다.**  
A. `p_regday`를 **어제 또는 최근 영업일**로 설정했는지, `p_item_category_code`가 올바른지 확인하세요. `p_cert_key`와 `p_cert_id`가 KAMIS에 등록된 값과 일치해야 합니다.

**Q. 카카오톡 Tool이 401 오류를 반환합니다.**  
A. OAuth2 Credential을 **재연결(Connect)** 하세요. Scope에 `talk_message`가 포함되어 있는지, 카카오 개발자 콘솔에서 '카카오톡 메시지 전송' 동의 항목이 활성화되었는지 확인하세요.

**Q. OpenWeatherMap에서 도시를 찾지 못해요.**  
A. **OpenWeatherMap Tool** 노드의 **City Name**에 `$fromAI`가 설정되었는지 확인하세요. `청주시` 대신 `Cheongju` 또는 `Seoul`처럼 영문 도시명을 시도해 보세요. **OpenWeatherMap API** Credential이 연결되어 있는지도 확인하세요.

**Q. gemini-3.5-flash 모델을 찾을 수 없어요.**  
A. Google AI Studio에서 사용 가능한 최신 Flash 모델명을 확인 후 Chat Model 노드에서 교체하세요.
