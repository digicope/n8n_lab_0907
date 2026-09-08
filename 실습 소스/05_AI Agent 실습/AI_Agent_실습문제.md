# n8n AI Agent Workflow 실습 (Gemini · Chat Trigger)

> **교육 과정:** 생성형 AI 활용 교육  
> **선수 과목:** `n8n_AI_기초_실습` 완료 권장 (`n8n_AI_활용_실습` 병행 학습 권장)  
> **사용 API:** [Google Gemini API](https://aistudio.google.com)  
> **트리거:** **When chat message received** (On Chat Message)  
> **답안 위치:** `답안/` 폴더의 개별 JSON 파일 → n8n **Import from File**로 바로 가져오기

---

## 사전 준비

| 항목 | 내용 |
|------|------|
| n8n | Cloud 무료 체험 또는 로컬 설치 ([n8n.io](https://n8n.io)) |
| Gemini API Key | [Google AI Studio](https://aistudio.google.com/apikey)에서 발급 |
| LangChain 노드 | n8n에 **AI Agent**, **Chat Trigger** 노드가 보여야 합니다 |

### Credential 등록

1. n8n → **Credentials** → **Add Credential**
2. **Google Gemini(PaLM) API** 검색 후 선택
3. API Key 입력 후 저장

Import한 답안 워크플로우의 **Google Gemini Chat Model** 서브노드에 Credential을 연결하세요.

### Chain vs Agent 비교

| 구분 | Basic LLM Chain (기초·활용) | AI Agent (이번 실습) |
|------|---------------------------|---------------------|
| 트리거 | Manual Trigger | **When chat message received** |
| 입력 | Edit Fields 고정값 / Expression | **채팅창 사용자 메시지** |
| 대화 | 1회 호출 | **다회 대화** (Memory) |
| 도구 | 없음 | **Calculator, Date & Time** 등 |
| 역할 | 프롬프트 1개 | **System Message** + Agent 추론 |

### 이번 실습에서 배우는 것

- **Chat Trigger** — n8n 내장 채팅 UI로 Agent 실행
- **AI Agent + Gemini** — LangChain Agent 패턴
- **System Message** — Agent 역할·규칙 정의
- **Simple Memory** — 세션별 대화 기억
- **Tools** — Calculator, Date & Time 등 내장 도구 연결
- **종합 Agent** — Memory + Tools + 역할 프롬프트

---

## 공통 설정 (실습 1~6)

모든 실습은 아래 공통 구조를 따릅니다.

```
When chat message received → AI Agent
                                 ↑
                    Google Gemini Chat Model (서브노드)
```

| 공통 항목 | 설정 |
|-----------|------|
| **When chat message received** | 기본 설정 유지 (Chat Trigger) |
| **Google Gemini Chat Model** | Model: `gemini-3.5-flash`, Temperature: `0.4` |
| **AI Agent — Prompt Source** | **Connected Chat Trigger node** (또는 Auto-detect input) |

> **중요:** Prompt Source를 `Define below` + `{{ $json.chatInput }}`만 쓰면, 에디터 테스트 채팅에서 **두 번째 메시지부터** 입력이 비는 경우가 있습니다. 실습에서는 **Connected Chat Trigger node**를 사용하세요.

### 채팅 테스트 방법

1. 워크플로우 저장
2. **When chat message received** 노드 선택 → **Open Chat** (또는 Test step)
3. 채팅창에 메시지 입력 후 Enter
4. Agent 응답 확인

---

## 실습 1. 첫 AI Agent — Gemini 챗봇

### 목표

**When chat message received** 트리거와 **AI Agent**를 연결해, Gemini 기반 대화형 챗봇을 만듭니다.

### 요구사항

```
When chat message received → AI Agent
                                    ↑
                       Google Gemini Chat Model
```

| 노드 | 설정 |
|------|------|
| **When chat message received** | 기본값 |
| **AI Agent** | Prompt Source: **Connected Chat Trigger node** |
| **Google Gemini Chat Model** | Model: `gemini-3.5-flash`, Temperature: `0.4` |

### 테스트 메시지

```
안녕! n8n AI Agent 실습을 시작합니다. 한 문장으로 인사해 주세요.
```

### 확인 사항

- [ ] Chat Trigger → AI Agent **main** 연결이 되어 있는가?
- [ ] Google Gemini Chat Model이 AI Agent **Chat Model** 슬롯에 연결되었는가?
- [ ] 채팅창에서 한국어 인사 응답이 돌아오는가?

### 힌트

- 노드 검색: `When chat message received`, `AI Agent`, `Google Gemini Chat Model`
- AI Agent는 **서브노드**(Chat Model, Memory, Tool)를 아래쪽 슬롯에 연결합니다
- Basic LLM Chain과 달리 Agent는 **도구 선택·추론**을 스스로 수행할 수 있습니다

---

## 실습 2. System Message — n8n 학습 도우미

### 목표

AI Agent에 **System Message**를 추가해, 일반 챗봇이 아닌 **n8n 학습 도우미** 역할을 부여합니다.

### 요구사항

```
When chat message received → AI Agent (+ System Message)
                                    ↑
                       Google Gemini Chat Model
```

| 노드 | 설정 |
|------|------|
| **AI Agent** | Prompt Source: **Connected Chat Trigger node** |
| | **Add Option → System Message** 아래 내용 입력 |

**System Message**

```
당신은 n8n과 AI 자동화를 가르치는 친절한 학습 도우미입니다.
- 답변은 반드시 한국어로 작성하세요.
- 초보자도 이해할 수 있게 3~5문장 이내로 설명하세요.
- n8n 노드 이름은 Bold 없이 그대로 적으세요.
- 모르는 내용은 추측하지 말고 모른다고 말하세요.
```

| **Google Gemini Chat Model** | Model: `gemini-3.5-flash`, Temperature: `0.3` |

### 테스트 메시지

```
n8n에서 AI Agent 노드는 Basic LLM Chain과 무엇이 다른가요?
```

### 확인 사항

- [ ] System Message가 AI Agent **Options**에 저장되었는가?
- [ ] 응답이 한국어 3~5문장 내외인가?
- [ ] Agent vs Chain 차이를 설명하는가?

### 힌트

- AI Agent 노드 하단 **Add Option** → **System Message**
- Temperature를 `0.3`으로 낮추면 역할·형식 준수율이 올라갑니다

---

## 실습 3. Simple Memory — 대화 맥락 기억

### 목표

**Simple Memory**를 연결해, 같은 채팅 세션에서 **이전 대화를 기억**하는 Agent를 만듭니다.

### 요구사항

```
When chat message received → AI Agent
                           ↑        ↑
              Google Gemini Chat Model
                           Simple Memory (서브노드)
```

| 노드 | 설정 |
|------|------|
| **AI Agent** | Prompt Source: **Connected Chat Trigger node** |
| | System Message: `당신은 친절한 한국어 대화 도우미입니다. 이전 대화를 기억하며 짧게 답하세요.` |
| **Simple Memory** | Session ID: **Define below** |
| | Key: `={{ $json.sessionId }}` |
| | Context Window Length: `10` |
| **Google Gemini Chat Model** | Model: `gemini-3.5-flash`, Temperature: `0.4` |

### 테스트 시나리오 (같은 채팅창에서 순서대로)

**1번 메시지**

```
내 이름은 민수야. 기억해 줘.
```

**2번 메시지**

```
내 이름이 뭐였지?
```

### 확인 사항

- [ ] Simple Memory가 AI Agent **Memory** 슬롯에 연결되었는가?
- [ ] Session Key가 `={{ $json.sessionId }}` 인가?
- [ ] 2번 메시지에 **민수**라고 답하는가?

### 힌트

- Chat Trigger가 `sessionId`를 자동 생성합니다
- Memory 없이는 매 메시지가 **독립 1회 질문**처럼 동작합니다
- Context Window Length `10` = 최근 10턴까지 기억

---

## 실습 4. Calculator Tool — 계산 Agent

### 목표

**Calculator** 도구를 Agent에 연결해, **수식 계산**을 도구로 처리하는 Agent를 만듭니다.

### 요구사항

```
When chat message received → AI Agent
                           ↑    ↑    ↑
              Google Gemini   Simple Memory
                           Calculator (Tool)
```

| 노드 | 설정 |
|------|------|
| **AI Agent** | System Message: 아래 내용 |
| **Simple Memory** | Session Key: `={{ $json.sessionId }}`, Context: `10` |
| **Calculator** | 기본 설정 (Tool 서브노드) |
| **Google Gemini Chat Model** | Model: `gemini-3.5-flash`, Temperature: `0.2` |

**System Message**

```
당신은 계산을 정확히 수행하는 한국어 수학 도우미입니다.
- 숫자 계산이 필요하면 반드시 Calculator 도구를 사용하세요.
- 최종 답만 간단히 한국어로 알려주세요.
- 계산 과정은 1~2줄로만 설명하세요.
```

### 테스트 메시지

```
연봉 4,800만 원을 12개월로 나누면 월급이 얼마야? (Calculator 사용)
```

### 확인 사항

- [ ] Calculator가 AI Agent **Tool** 슬롯에 연결되었는가?
- [ ] Agent 실행 로그에 **Calculator** 도구 호출이 보이는가?
- [ ] 월급 **400만 원**(또는 4,000,000원) 근처 답이 나오는가?

### 힌트

- Tool 슬롯에는 여러 도구를 동시에 연결할 수 있습니다
- Temperature `0.2`로 낮추면 잘못된 mental math를 줄일 수 있습니다
- 실행 후 **Executions** 탭에서 Agent의 tool call 단계를 확인하세요

---

## 실습 5. Date & Time Tool — 현재 시각 Agent

### 목표

**Date & Time** 도구를 추가해, **현재 날짜·시간**을 물어볼 때 도구를 사용하는 Agent를 만듭니다.

### 요구사항

```
When chat message received → AI Agent
                           ↑    ↑    ↑
              Google Gemini   Simple Memory
                           Calculator
                           Date & Time (Tool)
```

| 노드 | 설정 |
|------|------|
| **AI Agent** | System Message: 아래 내용 |
| **Simple Memory** | Session Key: `={{ $json.sessionId }}`, Context: `10` |
| **Calculator** | 기본 설정 |
| **Date & Time** | Operation: **Get Current Date and Time** (기본) , Include Current Time 체크 |
| **Google Gemini Chat Model** | Model: `gemini-3.5-flash`, Temperature: `0.3` |

**System Message**

```
당신은 한국어 업무 비서 Agent입니다.
- 현재 날짜·시간 질문 → Date & Time 도구 사용
- 숫자 계산 질문 → Calculator 도구 사용
- 답변은 2~4문장, 한국어, 존댓말
```

### 테스트 메시지

```
지금 몇 시야? 오늘 날짜도 알려줘.
```

### 확인 사항

- [ ] Date & Time이 AI Agent **Tool** 슬롯에 연결되었는가?
- [ ] Calculator와 Date & Time **두 도구**가 모두 연결되었는가?
- [ ] 응답에 **오늘 날짜**와 **현재 시각**이 포함되는가?

### 힌트

- Date & Time은 Credential 없이 사용 가능한 **내장 Tool**입니다
- Agent는 질문 유형에 따라 적절한 Tool을 **스스로 선택**합니다

---

## 실습 6. 종합 — 업무 비서 Agent

### 목표

Memory + Calculator + Date & Time + System Message를 모두 적용한 **종합 업무 비서 Agent**를 완성합니다.

### 요구사항

```
When chat message received → AI Agent
                           ↑    ↑    ↑
              Google Gemini   Simple Memory
                           Calculator
                           Date & Time
```

| 노드 | 설정 |
|------|------|
| **AI Agent** | Prompt Source: **Connected Chat Trigger node** |
| | Max Iterations: `8` |
| | System Message: 아래 내용 |
| **Simple Memory** | Session Key: `={{ $json.sessionId }}`, Context: `15` |
| **Calculator** | Tool 연결 |
| **Date & Time** | Tool 연결 |
| **Google Gemini Chat Model** | Model: `gemini-3.5-flash`, Temperature: `0.3` |

**System Message**

```
당신은 n8n 실습용 한국어 업무 비서 Agent입니다.

[역할]
- 회의 일정, 시간, 간단한 업무 계산을 도와줍니다.

[규칙]
1. 날짜·시간 → Date & Time 도구 필수
2. 숫자 계산 → Calculator 도구 필수
3. 답변 형식:
   - 첫 줄: 한 줄 요약
   - 다음 줄: 근거 1~2문장
4. 한국어 존댓말, 5문장 이내
```

### 종합 테스트 시나리오 (같은 채팅창)

**1번**

```
오늘 날짜 알려줘.
```

**2번**

```
팀원 5명에게 커피 4,500원씩 나눠 내면 1인당 얼마야?
```

**3번**

```
아까 팀원이 몇 명이었지?
```

### 확인 사항

- [ ] 3개 Tool/Memory/Model 서브노드가 모두 Agent에 연결되었는가?
- [ ] 1번: Date & Time 도구 사용 + 오늘 날짜 응답
- [ ] 2번: Calculator 도구 사용 + 4,500원(1인당) 응답
- [ ] 3번: Memory로 **5명** 기억
- [ ] 응답 형식(한 줄 요약 + 근거)을 따르는가?

### 힌트

- 실습 3~5의 설정을 **하나의 워크플로우**로 합칩니다
- Max Iterations는 Agent가 Tool을 여러 번 호출할 수 있는 **최대 반복 횟수**입니다
- 실습 완료 후 **Activate**하면 Production 채팅 URL로도 사용할 수 있습니다

---

## 체크 포인트

| 실습 | 배점 | 핵심 평가 |
|------|------|-----------|
| 실습 1 | 15점 | Chat Trigger + Agent + Gemini 연결 |
| 실습 2 | 15점 | System Message 역할 정의 |
| 실습 3 | 15점 | Simple Memory + sessionId |
| 실습 4 | 15점 | Calculator Tool 호출 |
| 실습 5 | 15점 | Date & Time Tool 호출 |
| 실습 6 | 25점 | Memory + 다중 Tool + 종합 대화 |
| **합계** | **100점** | |

---

## Import 방법

1. n8n → **Workflows** → **⋯** → **Import from File**
2. `답안/` 폴더에서 해당 실습 JSON 선택
3. **Google Gemini Chat Model** → **Credential** 연결
4. **When chat message received** → **Open Chat** 으로 테스트

| 실습 | 답안 파일 |
|------|-----------|
| 1 | `답안/실습1_첫_AI_Agent_Gemini.json` |
| 2 | `답안/실습2_System_Message_학습도우미.json` |
| 3 | `답안/실습3_Simple_Memory_대화기억.json` |
| 4 | `답안/실습4_Calculator_Tool_계산.json` |
| 5 | `답안/실습5_DateTime_Tool_시각.json` |
| 6 | `답안/실습6_종합_업무비서_Agent.json` |

---

## 자주 묻는 질문

**Q. "No prompt specified" 오류가 납니다.**  
A. AI Agent의 Prompt Source를 **Connected Chat Trigger node**로 바꾸세요. Chat Trigger가 main으로 Agent에 연결되어 있는지도 확인하세요.

**Q. 두 번째 채팅 메시지부터 응답이 이상해요.**  
A. `Define below` + `{{ $json.chatInput }}` 조합은 테스트 채팅에서 session이 끊길 수 있습니다. **Connected Chat Trigger node**를 사용하세요.

**Q. Gemini에서 `[400] contents.parts must not be empty` 오류가 납니다.**  
A. 빈 메시지가 Agent에 전달된 경우입니다. Prompt Source 설정을 확인하고, n8n을 최신 버전으로 업데이트하세요.

**Q. Memory가 동작하지 않아요.**  
A. Simple Memory의 Session Key가 `={{ $json.sessionId }}` 인지, Memory 슬롯이 Agent에 연결되었는지 확인하세요. **같은 채팅창**에서 연속으로 테스트해야 합니다.

**Q. Tool을 호출하지 않고 그냥 답합니다.**  
A. System Message에 "반드시 ○○ 도구를 사용하세요"를 명시하고, Temperature를 `0.2~0.3`으로 낮춰 보세요.

**Q. Basic LLM Chain 실습과 무엇부터 하면 되나요?**  
A. `n8n_AI_기초_실습` 4~6번(Gemini)을 먼저 완료한 뒤 이 실습으로 넘어오는 것을 권장합니다.
