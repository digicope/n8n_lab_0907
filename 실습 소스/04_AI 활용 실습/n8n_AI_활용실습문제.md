# n8n AI 활용 Workflow 실습 (중급)

> **교육 과정:** 생성형 AI 활용 교육  
> **선수 과목:** `n8n_AI_기초_실습` 완료 권장 (`n8n_2단계_실습` 병행 학습 권장)  
> **사용 API:** [OpenAI API](https://platform.openai.com) · [Google Gemini API](https://aistudio.google.com) · [JSONPlaceholder](https://jsonplaceholder.typicode.com) (무료)  
> **답안 위치:** `답안/` 폴더의 개별 JSON 파일 → n8n **Import from File**로 바로 가져오기

---

## 사전 준비

| 항목 | 내용 |
|------|------|
| n8n | Cloud 무료 체험 또는 로컬 설치 ([n8n.io](https://n8n.io)) |
| OpenAI API Key | [OpenAI Platform](https://platform.openai.com/api-keys)에서 발급 |
| Gemini API Key | [Google AI Studio](https://aistudio.google.com/apikey)에서 발급 |
| JSONPlaceholder | API Key **불필요** (실습 2~3, 6에서 사용) |

### Credential 등록

기초 실습과 동일하게 **OpenAI**, **Google Gemini(PaLM) API** Credential을 등록합니다.  
Import한 답안 워크플로우의 AI 노드에 Credential을 연결하세요.

### 기초 vs 활용 실습 비교

| 구분 | AI 기초 실습 | AI 활용 실습 (이번) |
|------|-------------|---------------------|
| 노드 수 | 2~3개 | 4~7개 |
| AI 출력 | 자유 텍스트 | **Structured JSON** 포함 |
| 데이터 소스 | Edit Fields 고정값 | **HTTP API** + 동적 Expression |
| 분기 | 없음 | **Switch** + AI 결과 연동 |
| 외부 연동 | 없음 | **Webhook** API 엔드포인트 |
| 종합 | 단일 AI 호출 | API 수집 → AI 분석 → 리포트 |

### 이번 실습에서 배우는 것

- **Structured Output Parser** — AI 응답을 JSON 스키마로 강제
- **HTTP Request + AI** — 외부 데이터를 가져와 AI로 분석
- **다건 처리 + Aggregate** — 여러 아이템을 AI로 처리 후 합치기
- **Webhook + AI** — 외부에서 텍스트를 내면 AI가 분석해 응답
- **Switch + AI** — AI 분류 결과에 따라 다른 처리 경로
- **종합 파이프라인** — API 연쇄 호출 + AI 구조화 출력 + 리포트

---

## 실습 1. Structured Output Parser — 리뷰 감정 JSON 분석

### 목표

Basic LLM Chain에 **Structured Output Parser**를 연결해, AI 응답을 정해진 JSON 형식으로 받습니다.

### 요구사항

```
Manual Trigger → Edit Fields → Basic LLM Chain
                                    ↑              ↑
                          OpenAI Chat Model   Structured Output Parser
```

| 노드 | 설정 |
|------|------|
| **Edit Fields** | `review` = `배송이 빨라서 만족합니다! 포장도 깔끔했어요.` |
| **Basic LLM Chain** | Prompt: `Define below`, **Require Specific Output Format: ON** |
| | Prompt (User Message): 아래 텍스트 입력 |
| **OpenAI Chat Model** | Model: `gpt-4o-mini`, Temperature: `0.2` |
| **Structured Output Parser** | Schema Type: `Generate from JSON Example` |

**Prompt (User Message) 내용**

```
다음 고객 리뷰를 분석하세요. 반드시 지정된 JSON 형식으로만 답하세요.

리뷰: {{ $json.review }}
```

**JSON Example (Parser)**

```json
{
  "sentiment": "positive",
  "reason": "배송이 빠르고 포장이 좋음",
  "score": 85
}
```

| 필드 | 설명 |
|------|------|
| `sentiment` | `positive`, `negative`, `neutral` 중 하나 |
| `reason` | 판단 이유 (한국어, 30자 이내) |
| `score` | 만족도 점수 (0~100 정수) |

### 확인 사항

- [ ] Structured Output Parser가 Basic LLM Chain의 **Output Parser** 슬롯에 연결되었는가?
- [ ] 출력에 `output.sentiment`, `output.reason`, `output.score` 필드가 있는가?
- [ ] `sentiment`가 `positive`인가?

### 힌트

- Chain 노드에서 **Require Specific Output Format**을 켜야 Parser 슬롯이 나타납니다
- 파싱된 결과는 `$json.output` 에 담깁니다
- Temperature를 낮추면 JSON 형식 준수율이 높아집니다

---

## 실습 2. HTTP + AI — 게시글 한국어 요약

### 목표

JSONPlaceholder에서 게시글을 가져온 뒤, AI로 **한국어 2문장 요약**을 생성합니다.

### 요구사항

```
Manual Trigger → HTTP Request → Basic LLM Chain → Edit Fields
                                      ↑
                            OpenAI Chat Model
```

| 노드 | 설정 |
|------|------|
| **HTTP Request** | GET `https://jsonplaceholder.typicode.com/posts/1` |
| **Basic LLM Chain** | Prompt (User Message): 아래 텍스트 입력 |
| **OpenAI Chat Model** | Model: `gpt-4o-mini`, Temperature: `0.5` |
| **Edit Fields** | `postId` = `={{ $('HTTP Request').item.json.id }}` |
| | `summary` = `={{ $json.text }}` |

**Prompt (User Message) 내용**

```
아래 게시글을 한국어로 정확히 2문장으로 요약하세요.

제목: {{ $json.title }}
본문: {{ $json.body }}
```

### 확인 사항

- [ ] HTTP Request로 게시글 데이터를 가져왔는가?
- [ ] 프롬프트에 `{{ $json.title }}`, `{{ $json.body }}` Expression을 사용했는가?
- [ ] 최종 출력에 `postId`와 한국어 `summary`가 있는가?

### 힌트

- HTTP Request 결과가 바로 Chain의 입력이 됩니다 (`$json.title` 등)
- Edit Fields에서 `$('HTTP Request')`로 원본 게시글 ID를 참조할 수 있습니다
- Chain 출력 텍스트는 보통 `$json.text` 필드에 있습니다

---

## 실습 3. 댓글 일괄 AI 분석 + 리포트

### 목표

게시글 댓글 3건을 각각 AI로 감정 분석한 뒤, **하나의 텍스트 리포트**로 합칩니다.

### 요구사항

```
Manual Trigger → HTTP Request → Limit → Basic LLM Chain → Aggregate → Code
                                              ↑
                                    Google Gemini Chat Model
```

| 노드 | 설정 |
|------|------|
| **HTTP Request** | GET `https://jsonplaceholder.typicode.com/comments?postId=1` |
| **Limit** | Max Items: `3` |
| **Basic LLM Chain** | Prompt (User Message): 아래 텍스트 입력 |
| **Google Gemini Chat Model** | Model: `gemini-2.5-flash`, Temperature: `0.3` |
| **Aggregate** | Aggregate: `aggregateAllItemData` |
| **Code** | 아래 로직으로 `report` 필드 생성 |

**Prompt (User Message) 내용**

```
다음 댓글의 감정을 한 단어로만 답하세요 (positive, negative, neutral 중 하나).

댓글 작성자: {{ $json.name }}
댓글 내용: {{ $json.body }}
```

**Code 노드 로직**

```javascript
const items = $input.first().json.data;
const lines = items.map((item, i) => {
  const sentiment = (item.text || '').trim().toLowerCase();
  const name = $('Limit').all()[i].json.name;
  return `${i + 1}. ${name}: ${sentiment}`;
});

return [{
  json: {
    report: `📝 댓글 감정 분석 리포트 (postId=1)\n\n${lines.join('\n')}`
  }
}];
```

### 확인 사항

- [ ] Limit로 3건만 처리했는가?
- [ ] Basic LLM Chain이 **아이템마다** 실행되어 3건의 결과가 나오는가?
- [ ] Aggregate 이후 Code에서 `report` 문자열이 생성되는가?

### 힌트

- Chain 노드는 입력 아이템 수만큼 반복 실행됩니다
- Aggregate 후 데이터는 `$json.data` 배열에 모입니다
- `$('Limit').all()`로 원본 댓글 작성자 이름을 참조할 수 있습니다

---

## 실습 4. Webhook + AI — 텍스트 분석 API

### 목표

외부에서 텍스트를 POST하면 AI가 **키워드와 요약**을 JSON으로 응답하는 API를 만듭니다.

### 요구사항

```
Webhook → Basic LLM Chain → Respond to Webhook
              ↑         ↑
    OpenAI Chat Model   Structured Output Parser
```

| 노드 | 설정 |
|------|------|
| **Webhook** | Method: `POST`, Path: `analyze-text`, Response Mode: **Using 'Respond to Webhook' Node** |
| **Basic LLM Chain** | Require Specific Output Format: **ON**, Prompt: 아래 텍스트 |
| **OpenAI Chat Model** | Model: `gpt-4o-mini`, Temperature: `0.3` |
| **Structured Output Parser** | JSON Example: 아래 참고 |
| **Respond to Webhook** | Respond With: `JSON`, Body: `={{ $json.output }}` |

**Prompt (User Message) 내용**

```
아래 텍스트를 분석하여 키워드 3개와 한 줄 요약을 한국어로 작성하세요.

텍스트: {{ $json.body.text }}
```

**JSON Example (Parser)**

```json
{
  "keywords": ["자동화", "워크플로우", "AI"],
  "summary": "n8n으로 업무 자동화를 구현하는 방법"
}
```

### 테스트 방법

1. Webhook 노드에서 **Test URL** 복사
2. 워크플로우 **Activate** (또는 Listen for test event)
3. 아래 요청 전송:

```bash
curl -X POST {Webhook_URL} -H "Content-Type: application/json" -d "{\"text\": \"n8n은 다양한 앱과 AI를 연결해 업무를 자동화하는 노코드 도구입니다.\"}"
```

### 확인 사항

- [ ] 응답 JSON에 `keywords` 배열과 `summary` 문자열이 있는가?
- [ ] Webhook body의 `text` 필드를 프롬프트에서 참조했는가?
- [ ] Respond to Webhook이 `$json.output`을 반환하는가?

### 힌트

- POST body는 `$json.body.text`로 접근합니다
- Structured Output Parser 없이는 응답 형식이 매번 달라질 수 있습니다
- 실습 1과 동일한 Parser 연결 방식입니다

---

## 실습 5. AI 감정 분류 + Switch 분기

### 목표

AI가 리뷰 감정을 JSON으로 분류하면, **Switch**로 positive / negative / neutral 경로를 나눕니다.

### 요구사항

```
Manual Trigger → Edit Fields → Basic LLM Chain → Switch
                                      ↑              ↓
                          OpenAI Chat Model    Edit Fields (각 분기)
                          Structured Output Parser
```

| 노드 | 설정 |
|------|------|
| **Edit Fields** | `review` = `제품 품질은 좋은데 배송이 너무 늦었습니다.` |
| **Basic LLM Chain** | Require Specific Output Format: **ON** |
| **Structured Output Parser** | JSON Example: `{"sentiment": "negative"}` |
| **Switch** | Rules -> Routing Rules (3개 각각 설정): `{{ $json.output.sentiment }}` is equal to `positive` / `negative` / `neutral` |
| **Edit Fields** (positive) | `message` = `{{ '😊 긍정 리뷰입니다: ' + $('Edit Fields').item.json.review }}` |
| **Edit Fields1** (negative) | `message` = `{{ '😞 부정 리뷰입니다: ' + $('Edit Fields').item.json.review }}` |
| **Edit Fields2** (neutral) | `message` = `{{ '😐 중립 리뷰입니다: ' + $('Edit Fields').item.json.review }}` |

**Prompt (User Message) 내용**

```
다음 리뷰의 감정을 분석하세요. sentiment는 positive, negative, neutral 중 하나만 사용하세요.
리뷰 내용에 긍정 내용이 있어도 부정적인 내용이 조금이라도 있으면 negative로 결정해줘.

리뷰: {{ $json.review }}
```

### 확인 사항

- [ ] Switch가 AI 출력 `$json.output.sentiment` 값을 기준으로 분기하는가?
- [ ] 샘플 리뷰가 **negative** 분기로 가는가?
- [ ] 해당 분기의 `message`에 원본 리뷰가 포함되는가?

### 힌트

- Switch 조건의 Left Value에 `={{ $json.output.sentiment }}`를 사용합니다
- AI 분류 결과를 분기 조건으로 쓰는 것이 이번 실습의 핵심입니다
- 리뷰를 긍정 문장으로 바꾸면 positive 분기로 이동하는지 테스트해 보세요

---

## 실습 6. 종합 — 게시글·댓글 AI 리포트

### 목표

게시글과 댓글을 **순차 API 호출**로 수집한 뒤, AI가 **구조화된 종합 리포트**를 JSON으로 생성합니다. (활용 과정 종합 과제)

### 요구사항

```
Manual Trigger
  → HTTP Request (posts/1)
  → HTTP Request1 (comments?postId=1)
  → Limit (3건)
  → Code (프롬프트 준비)
  → Basic LLM Chain
  → Edit Fields
              ↑         ↑
    Gemini Chat Model   Structured Output Parser
```

| 노드 | URL / 설정 |
|------|------------|
| **HTTP Request** | GET `https://jsonplaceholder.typicode.com/posts/1` |
| **HTTP Request1** | GET `https://jsonplaceholder.typicode.com/comments?postId={{ $('HTTP Request').item.json.id }}` |
| **Limit** | Max Items: `3` |
| **Code** | 게시글 + 댓글을 `promptText` 필드로 합치기 (아래 로직) |
| **Basic LLM Chain** | Require Specific Output Format: **ON** |
| **Edit Fields** | `reportTitle`, `reportSummary`, `topKeywords` 추출 |

**Code 노드 로직**

```javascript
const post = $('HTTP Request').first().json;
const comments = $input.all().map(i => i.json);

const commentBlock = comments
  .map((c, i) => `${i + 1}. ${c.name}: ${c.body.substring(0, 50)}...`)
  .join('\n');

return [{
  json: {
    promptText: `게시글 제목: ${post.title}\n게시글 본문: ${post.body}\n\n댓글 (상위 ${comments.length}건):\n${commentBlock}`
  }
}];
```

**Prompt (User Message) 내용**

```
아래 게시글과 댓글을 분석하여 한국어로 리포트를 작성하세요.

{{ $json.promptText }}
```

**JSON Example (Parser)**

```json
{
  "title": "게시글 핵심 주제",
  "summary": "게시글과 댓글을 종합한 2문장 요약",
  "keywords": ["키워드1", "키워드2", "키워드3"],
  "commentTone": "positive"
}
```

| 필드 | 설명 |
|------|------|
| `title` | 게시글 핵심 주제 (한국어, 20자 이내) |
| `summary` | 종합 요약 (한국어, 2문장) |
| `keywords` | 핵심 키워드 3개 (문자열 배열) |
| `commentTone` | 댓글 전체 분위기 (`positive` / `negative` / `neutral`) |

**Edit Fields Expression**

| 필드 | Expression |
|------|------------|
| `reportTitle` | `={{ $json.output.title }}` |
| `reportSummary` | `={{ $json.output.summary }}` |
| `topKeywords` | `={{ $json.output.keywords.join(', ') }}` |

### 확인 사항

- [ ] 2개의 HTTP Request가 **순차 연결**되어 있는가?
- [ ] Code에서 `$('HTTP Request')` 참조로 게시글 정보를 사용했는가?
- [ ] AI 출력이 JSON 구조(`title`, `summary`, `keywords`, `commentTone`)로 파싱되는가?
- [ ] Edit Fields에서 `topKeywords`가 쉼표로 구분된 문자열인가?

### 힌트

- 2단계 실습 6(종합 리포트)에 AI 분석을 더한 버전입니다
- Code 노드로 긴 프롬프트를 조립하면 Chain 설정이 깔끔해집니다
- Gemini를 사용하지만 OpenAI로 교체해도 동일하게 동작합니다

---

## 체크 포인트

| 실습 | 배점 | 핵심 평가 |
|------|------|-----------|
| 실습 1 | 15점 | Structured Output Parser 연결 |
| 실습 2 | 15점 | HTTP + AI Expression |
| 실습 3 | 15점 | 다건 AI 처리 + Aggregate |
| 실습 4 | 20점 | Webhook + AI + JSON 응답 |
| 실습 5 | 15점 | AI 분류 + Switch 분기 |
| 실습 6 | 20점 | 순차 API + AI 구조화 리포트 |
| **합계** | **100점** | |

---

## Import 방법

1. n8n → **Workflows** → **⋯** → **Import from File**
2. `답안/` 폴더에서 해당 실습 JSON 선택
3. AI 노드 클릭 → **Credential** 연결
4. **Test workflow** 로 실행·출력 확인 (실습 4는 Activate 후 Webhook 테스트)

| 실습 | 답안 파일 |
|------|-----------|
| 1 | `답안/실습1_Structured_Output_감정분석.json` |
| 2 | `답안/실습2_HTTP_AI_게시글요약.json` |
| 3 | `답안/실습3_댓글_일괄분석_리포트.json` |
| 4 | `답안/실습4_Webhook_AI_텍스트분석.json` |
| 5 | `답안/실습5_AI_Switch_분기.json` |
| 6 | `답안/실습6_종합_AI_리포트.json` |

---

## 자주 묻는 질문

**Q. `output` 필드가 안 보여요.**  
A. Structured Output Parser가 Chain의 Output Parser 슬롯에 연결되었는지, Chain에서 **Require Specific Output Format**이 켜져 있는지 확인하세요.

**Q. Parser 오류 "Failed to parse"가 납니다.**  
A. Temperature를 0.2~0.3으로 낮추고, 프롬프트에 "지정된 JSON 형식으로만 답하세요"를 명시하세요. Parser의 **Auto-Fix Format**을 켜면 자동 재시도됩니다.

**Q. 실습 3에서 Aggregate 후 데이터가 비어 있어요.**  
A. Basic LLM Chain이 3건 모두 실행되었는지 확인하세요. Chain 출력 필드명은 `text`입니다.

**Q. 기초 실습 답안을 먼저 Import해도 되나요?**  
A. 네. 기초 실습 1~3을 완료한 뒤 이번 활용 실습으로 넘어오는 것을 권장합니다.
