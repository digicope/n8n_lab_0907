# n8n AI 기초 Workflow 실습 (OpenAI · Gemini)

> **교육 과정:** 생성형 AI 활용 교육  
> **선수 과목:** `n8n_기초_실습` 완료 권장  
> **사용 API:** [OpenAI API](https://platform.openai.com) · [Google Gemini API](https://aistudio.google.com)  
> **답안 위치:** `답안/` 폴더의 개별 JSON 파일 → n8n **Import from File**로 바로 가져오기

---

## 사전 준비

| 항목 | 내용 |
|------|------|
| n8n | Cloud 무료 체험 또는 로컬 설치 ([n8n.io](https://n8n.io)) |
| OpenAI API Key | [OpenAI Platform](https://platform.openai.com/api-keys)에서 발급 |
| Gemini API Key | [Google AI Studio](https://aistudio.google.com/apikey)에서 발급 |
| 인터넷 | AI 노드 실행 시 필요 |

### Credential 등록 방법

#### OpenAI

1. n8n → **Credentials** → **Add Credential**
2. **OpenAI** 검색 후 선택
3. API Key 입력 → **Save**

#### Google Gemini (PaLM)

1. n8n → **Credentials** → **Add Credential**
2. **Google Gemini(PaLM) API** 검색 후 선택
3. API Key 입력 → **Save**

> Import한 답안 워크플로우를 열면 AI 노드에 Credential 연결 안내가 표시됩니다. 위에서 만든 Credential을 선택하세요.

### 이번 실습에서 배우는 것

- **OpenAI 노드** — Text 리소스로 모델에 메시지 보내기
- **시스템 프롬프트** — AI 역할·톤 지정
- **Expression** — 이전 노드 데이터를 프롬프트에 연결
- **Basic LLM Chain** — LangChain 기반 단순 AI 호출
- **Google Gemini 노드** — Gemini 모델 기본 사용
- **Chat Model 서브노드** — OpenAI / Gemini 모델 연결

---

## 실습 1. OpenAI — 첫 AI 메시지

### 목표

OpenAI 노드를 추가하고, 모델에 간단한 메시지를 보내 응답을 확인합니다.

### 요구사항

```
Manual Trigger → OpenAI
```

| 노드 | 설정 |
|------|------|
| **OpenAI** | Resource: `Text` |
| | Operation: `Message a Model` (또는 `Generate a Chat Completion`) |
| | Model: `gpt-4o-mini` (또는 사용 가능한 경량 모델) |
| | Messages — Role: `User`, Content: `n8n AI 실습을 시작합니다. 한 문장으로 인사해 주세요.` |

### 확인 사항

- [ ] OpenAI Credential이 연결되었는가?
- [ ] 실행 후 AI 응답 텍스트가 출력되는가?
- [ ] 한국어로 인사 문장이 생성되었는가?

### 힌트

- 노드 검색창에 `OpenAI` 입력 (LangChain 카테고리)
- 응답은 보통 `message.content` 또는 `text` 필드에 담깁니다
- 모델 목록이 비어 있으면 Credential을 먼저 확인하세요

---

## 실습 2. OpenAI — 시스템 프롬프트 + 동적 입력

### 목표

시스템 메시지로 AI 역할을 지정하고, Edit Fields의 값을 Expression으로 프롬프트에 전달합니다.

### 요구사항

```
Manual Trigger → Edit Fields → OpenAI
```

| 노드 | 설정 |
|------|------|
| **Edit Fields** | `product` = `n8n` (문자열) |
| **OpenAI** | Model: `gpt-4o-mini` |
| | Message 1 — Role: `System`, Content: `당신은 IT 제품 소개 전문 카피라이터입니다. 항상 한국어로, 50자 이내로 답합니다.` |
| | Message 2 — Role: `User`, Content: `={{ $json.product + '을(를) 한 줄로 소개해 주세요.' }}` |

### 확인 사항

- [ ] User 메시지에 Expression(`fx`)을 사용했는가?
- [ ] 응답이 50자 내외의 한국어 한 줄 소개인가?
- [ ] `product` 값을 바꾸면 소개 내용도 달라지는가?

### 힌트

- 시스템 메시지는 AI의 **역할·규칙**을 정의합니다
- User 메시지에 `={{ }}` Expression을 사용하면 이전 노드 데이터를 참조할 수 있습니다

---

## 실습 3. Basic LLM Chain + OpenAI Chat Model

### 목표

Basic LLM Chain 노드에 OpenAI Chat Model 서브노드를 연결해 감정 분류를 수행합니다.

### 요구사항

```
Manual Trigger → Edit Fields → Basic LLM Chain
                                    ↑
                          OpenAI Chat Model (서브노드)
```

| 노드 | 설정 |
|------|------|
| **Edit Fields** | `review` = `배송이 빨라서 만족합니다!` |
| **Basic LLM Chain** | Prompt: `Define below` |
| | Prompt (User Message): 아래 텍스트 입력 |
| **OpenAI Chat Model** | Model: `gpt-4o-mini`, Temperature: `0.3` |

**Prompt (User Message) 내용**

```
다음 고객 리뷰의 감정을 분석하세요.
반드시 positive, negative, neutral 중 하나만 답하세요. 다른 말은 하지 마세요.

리뷰: {{ $json.review }}
```

### 확인 사항

- [ ] Basic LLM Chain에 OpenAI Chat Model 서브노드가 연결되었는가?
- [ ] 응답에 `positive`가 포함되는가?
- [ ] 리뷰를 부정 문장으로 바꾸면 `negative`로 바뀌는가?

### 힌트

- Basic LLM Chain은 Chat Model 서브노드 **없이는 실행되지 않습니다**
- 서브노드 연결: Chain 노드 하단 **Model** 슬롯 클릭 → OpenAI Chat Model 추가
- Temperature를 낮추면(0~0.3) 더 일관된 답변이 나옵니다

---

## 실습 4. Google Gemini — 첫 AI 메시지

### 목표

Google Gemini 노드를 사용해 Gemini 모델에 메시지를 보냅니다.

### 요구사항

```
Manual Trigger → Google Gemini
```

| 노드 | 설정 |
|------|------|
| **Google Gemini** | Resource: `Text` |
| | Operation: `Message a Model` |
| | Model: `gemini-2.5-flash` (또는 사용 가능한 Flash 모델) |
| | Messages — Role: `User`, Content: `n8n과 Gemini를 연결했습니다. 한 문장으로 인사해 주세요.` |

### 확인 사항

- [ ] Google Gemini(PaLM) API Credential이 연결되었는가?
- [ ] 실행 후 AI 응답이 출력되는가?
- [ ] OpenAI 실습 1과 동일한 방식으로 메시지를 보냈는가?

### 힌트

- 노드 검색창에 `Google Gemini` 입력
- Credential 이름이 **Google Gemini(PaLM) API** 입니다
- API Key는 [Google AI Studio](https://aistudio.google.com/apikey)에서 무료 발급 가능

---

## 실습 5. Google Gemini — 시스템 프롬프트 + 동적 입력

### 목표

Gemini에도 시스템 메시지와 Expression을 적용해 제품 소개 문구를 생성합니다.

### 요구사항

```
Manual Trigger → Edit Fields → Google Gemini
```

| 노드 | 설정 |
|------|------|
| **Edit Fields** | `product` = `Gemini` (문자열) |
| **Google Gemini** | Model: `gemini-2.5-flash` |
| | Message 1 — Role: `Model`, Prompt: `당신은 친절한 기술 블로거입니다. 항상 한국어로, 60자 이내로 답합니다.` |
| | Message 2 — Role: `User`, Prompt: `={{ $json.product + '이 무엇인지 한 줄로 설명해 주세요.' }}` |

### 확인 사항

- [ ] Model(System) / User 메시지 2개를 설정했는가?
- [ ] Expression으로 `product` 값을 참조했는가?
- [ ] 응답이 한국어 한 줄 설명인가?

### 힌트

- OpenAI 실습 2와 구조가 같습니다. 노드만 Gemini로 바꿉니다
- 모델 이름은 `models/gemini-2.5-flash` 형식일 수 있습니다

---

## 실습 6. Basic LLM Chain + Google Gemini Chat Model

### 목표

Basic LLM Chain에 Google Gemini Chat Model을 연결해 텍스트를 요약합니다.

### 요구사항

```
Manual Trigger → Edit Fields → Basic LLM Chain
                                    ↑
                       Google Gemini Chat Model (서브노드)
```

| 노드 | 설정 |
|------|------|
| **Edit Fields** | `article` = 아래 샘플 기사 (문자열) |
| **Basic LLM Chain** | Prompt: `Define below` |
| | Prompt (User Message): 아래 텍스트 입력 |
| **Google Gemini Chat Model** | Model: `gemini-2.5-flash`, Temperature: `0.4` |

**Edit Fields — `article` 샘플 값**

```
n8n은 노코드 자동화 도구로, 다양한 앱과 API를 시각적으로 연결할 수 있습니다.
최근에는 OpenAI, Google Gemini 등 AI 모델을 워크플로우에 직접 연결하는 기능이 강화되었습니다.
```

**Prompt (User Message) 내용**

```
아래 기사를 한국어로 3개의 불릿 포인트로 요약하세요.
각 항목은 20자 이내로 작성하세요.

기사:
{{ $json.article }}
```

### 확인 사항

- [ ] Google Gemini Chat Model 서브노드가 연결되었는가?
- [ ] 출력에 3개의 요약 항목이 있는가?
- [ ] OpenAI Chain(실습 3)과 Gemini Chain의 연결 방식이 같은가?

### 힌트

- 실습 3과 동일하게 Chain + Chat Model 조합입니다
- 서브노드만 **Google Gemini Chat Model**로 교체합니다
- 두 AI 제공업체 모두 Basic LLM Chain 패턴을 공유합니다

---

## Import 방법

1. n8n → **Workflows** → **⋯** → **Import from File**
2. `답안/` 폴더에서 해당 실습 JSON 선택
3. AI 노드 클릭 → **Credential** 연결
4. **Test workflow** 로 실행·출력 확인

| 실습 | 답안 파일 |
|------|-----------|
| 1 | `답안/실습1_OpenAI_첫_메시지.json` |
| 2 | `답안/실습2_OpenAI_시스템_프롬프트.json` |
| 3 | `답안/실습3_Basic_LLM_Chain_OpenAI.json` |
| 4 | `답안/실습4_Gemini_첫_메시지.json` |
| 5 | `답안/실습5_Gemini_시스템_프롬프트.json` |
| 6 | `답안/실습6_Basic_LLM_Chain_Gemini.json` |

---

## 자주 묻는 질문

**Q. API Key 비용이 발생하나요?**  
A. OpenAI와 Gemini 모두 무료 체험·소량 무료 할당이 있습니다. 실습용 경량 모델(`gpt-4o-mini`, `gemini-2.5-flash`)을 사용하세요.

**Q. "Message a Model"이 안 보여요.**  
A. n8n 버전에 따라 `Generate a Chat Completion`으로 표시될 수 있습니다. 둘 다 Text 리소스의 채팅 완성 기능입니다.

**Q. Basic LLM Chain이 "No prompt specified" 오류를 냅니다.**  
A. Prompt를 `Define below`로 설정하고 Prompt (User Message) 필드에 텍스트를 입력했는지 확인하세요.

**Q. 답안을 그대로 Import해도 되나요?**  
A. 학습 초기에는 Import 후 노드 설정을 하나씩 열어보며 비교하는 것을 권장합니다.
