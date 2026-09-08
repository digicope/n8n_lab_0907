# n8n RAG Agent 기초 Workflow 실습 (Google Drive · Gemini · Qdrant)

> **교육 과정:** 생성형 AI 활용 교육  
> **선수 과목:** `n8n_AI_Agent_실습` 완료 권장  
> **사용 API:** [Google Gemini API](https://aistudio.google.com) · [Qdrant Cloud](https://cloud.qdrant.io) · Google Drive  
> **모델:** `gemini-3.5-flash` (Chat) · **Embeddings Google Gemini** (벡터 임베딩)  
> **실습 문서:** 이 폴더의 `sample.pdf` (`2026년 1분기 실적 보고서`)  
> **답안 참고:** `실습1_ RAG Agent 기초 (답안 배포본).json` → n8n **Import from File**로 가져오기

---

## 실습 목표

이 폴더에 있는 **`sample.pdf`**를 Google Drive에 업로드한 뒤, n8n으로 PDF를 추출·임베딩하여 **Qdrant Vector Store**에 저장합니다.  
이후 Chat에서 **"2026년 1분기 실적 보고서 알려줘"**를 입력하면, Agent가 Vector Store 검색 결과를 근거로 보고서 내용을 답변하도록 구성합니다.

---

## 실습 문서 안내 (`sample.pdf`)

| 항목 | 내용 |
|------|------|
| 파일명 | `sample.pdf` |
| 문서 제목 | **2026년 1분기 실적 보고서** |
| 용도 | RAG 실습용 가상 보고서 (한글 1페이지) |
| 포함 내용 | 요약, 주요 성과, 매출·비용, 이슈·대응, 2분기 계획 |

**문서에 포함된 핵심 정보 (채팅 답변 확인용)**

- 총 **48명** 수료, 만족도 **4.6/5.0**
- n8n Cloud 실습 참여율 **95%**, Document Parse·Solar LLM 완료율 **92%**
- 1분기 교육 매출 **2억 1,500만 원**, 운영 비용 **1억 3,200만 원**, 영업이익률 **38.6%**
- 2분기 계획: AI Agent 심화(RAG), Solar Pro3 실습, 문서 자동화 PoC 등

---

## 이번 실습에서 배우는 것

- **Google Drive** — `sample.pdf` 다운로드
- **Extract from File** — PDF 텍스트 추출
- **Default Data Loader** — LangChain 문서 로더 연결
- **Embeddings Google Gemini** — Gemini 기반 벡터 임베딩
- **Qdrant Vector Store** — 보고서 벡터 저장·검색
- **AI Agent + Vector Store Tool** — "2026년 1분기 실적 보고서" 질의응답

---

## 사전 준비

| 항목 | 내용 |
|------|------|
| n8n | Cloud 무료 체험 또는 로컬 설치 ([n8n.io](https://n8n.io)) |
| Gemini API Key | [Google AI Studio](https://aistudio.google.com/apikey)에서 발급 |
| Qdrant Cloud 계정 | [Qdrant Cloud](https://cloud.qdrant.io) 무료 클러스터 생성 |
| Google Drive | 본인 계정에 `sample.pdf` 업로드 |
| 실습 파일 | `n8n_RAG Agent 실습/sample.pdf` |
| LangChain 노드 | **AI Agent**, **Chat Trigger**, **Vector Store Qdrant**, **Embeddings Google Gemini** |

---

## 0단계. `sample.pdf` Google Drive 업로드

실습을 시작하기 전에 아래 순서로 문서를 준비합니다.

1. 이 폴더의 **`sample.pdf`** 파일을 확인합니다.
2. [Google Drive](https://drive.google.com) 접속
3. 실습용 폴더 생성 (예: `n8n-RAG-실습`)
4. `sample.pdf`를 해당 폴더에 **업로드**
5. 업로드된 `sample.pdf` 우클릭 → **링크 복사** 또는 파일 선택 후 URL에서 **파일 ID** 확인

**파일 ID 확인 예시**

```
https://drive.google.com/file/d/1ecz7ywGGq2OZ9T15225yEl3okNvJmaIj/view
                              ↑ 이 부분이 파일 ID
```

6. n8n 워크플로우의 **Google Drive** 노드에서 업로드한 `sample.pdf`를 선택합니다.

---

## Qdrant Cloud 무료 가입 · API Key 발급

이 실습의 Vector Store는 **Qdrant Cloud 무료 클러스터**를 사용합니다.

### 1) 계정 가입

1. [Qdrant Cloud](https://cloud.qdrant.io/signup) 접속
2. **이메일**, **Google**, **GitHub** 중 하나로 가입
3. 로그인 후 대시보드로 이동

### 2) Free Cluster 생성

1. 대시보드에서 **Create a Free Cluster** 선택
2. **Cluster Name** 입력 (예: `n8n-rag-practice`)
3. **Cloud Provider / Region** 선택 (가까운 리전 권장)
4. **Create Free Cluster** 클릭
5. 클러스터 생성 완료까지 대기
6. Open Cluster UI를 누르고 Collection 메뉴에서 rag_google_drive_docs  이름으로 cluster 생성<br>
   dimension : 3072, Cosine으로 설정
> Free Tier는 학습용으로 충분합니다. 신용카드 없이 사용할 수 있습니다.

### 3) API Key 발급

1. 생성된 클러스터 상세 페이지 이동
2. **API Keys** 섹션 선택
3. **Create** 클릭
4. Key 이름 입력 (예: `n8n-rag-key`)
5. 권한은 기본값(**manage/write**) 유지
6. **Create** 후 표시되는 **API Key를 즉시 복사해 보관**

> API Key는 생성 직후 한 번만 전체 내용을 볼 수 있습니다.

### 4) n8n 연결에 필요한 값

| 항목 | 예시 | 용도 |
|------|------|------|
| **Cluster URL** | `https://xxxx.eu-central.aws.cloud.qdrant.io` | n8n Qdrant Credential URL |
| **API Key** | `eyJhbGciOi...` | n8n Qdrant Credential API Key |

### 5) n8n에 Qdrant Credential 등록

1. n8n → **Credentials** → **Add Credential**
2. **Qdrant API** 검색 후 선택
3. **URL**에 Cluster URL 입력
4. **API Key** 입력
5. **Vector Store**, **Vector Store Retrieve** 노드에 연결

---

## Credential 등록 (전체)

| Credential | 등록 방법 |
|------------|-----------|
| **Google Gemini(PaLM) API** | API Key 입력 |
| **Qdrant API** | Cluster URL + API Key |
| **Google Drive OAuth2** | Google 계정 OAuth 연동 |

연결 대상 노드:

- **Embeddings Google Gemini** (2개)
- **Google Gemini Chat Model** (2개)
- **Vector Store**, **Vector Store Retrieve**
- **Google Drive**

---

## 실습 1. RAG Agent 기초 — `sample.pdf` 실적 보고서 검색

### 목표

`sample.pdf`를 Google Drive에서 가져와 Vector Store에 저장하고,  
Chat에서 **"2026년 1분기 실적 보고서 알려줘"** 질문에 문서 기반으로 답변합니다.

### 전체 구조

#### A. 문서 적재(Ingestion) — `sample.pdf` 저장

```
When clicking Execute workflow
  ↓
Google Drive (sample.pdf download)
  ↓
Extract from File (PDF)
  ↓
Vector Store (Insert)
  ├─ Default Data Loader
  └─ Embeddings Google Gemini
  ↓
Ingestion Result
```

#### B. 질의응답(RAG Chat) — 실적 보고서 질문

```
Chat Trigger
  ↓  "2026년 1분기 실적 보고서 알려줘"
AI Agent (Gemini Chatbot)
  ├─ Google Gemini Chat Model
  └─ Vector Store Tool
       ├─ Vector Store Retrieve
       │    └─ Embeddings Google Gemini
       └─ Google Gemini Chat Model (Tool용)
```

---

### 요구사항

#### 1) 문서 적재 파이프라인

| 노드 | 필수 설정 |
|------|-----------|
| **When clicking Execute workflow** | Manual Trigger |
| **Google Drive** | Operation: `Download`, 파일: **`sample.pdf`** |
| **Extract from File** | Operation: `Extract from PDF` |
| **Vector Store** | Mode: `Insert`, Collection: `rag_google_drive_docs` |
| **Default Data Loader** | Vector Store **Document** 슬롯 연결 |
| **Embeddings Google Gemini** | Vector Store **Embedding** 슬롯 연결 |
| **Ingestion Result** | `status`, `message`, `collection` 출력 |

#### 2) RAG 챗봇 파이프라인

| 노드 | 필수 설정 |
|------|-----------|
| **Chat Trigger** | 채팅 입력 → Agent 전달 |
| **AI Agent (Gemini Chatbot)** | System Message에 RAG 규칙 포함 |
| **Google Gemini Chat Model** | Model: `gemini-3.5-flash`, Temperature: `0.2` |
| **Vector Store Tool** | Name: `rag_search_tool`, Top K: `5` |
| **Vector Store Retrieve** | Collection: `rag_google_drive_docs` |
| **Embeddings Google Gemini** | Retrieve **Embedding** 슬롯 연결 |
| **Google Gemini Chat Model (Tool용)** | Vector Store Tool **Chat Model** 슬롯 연결 |

**AI Agent System Message (권장)**

```
너는 Google Drive에 저장된 sample.pdf(2026년 1분기 실적 보고서) 기반 RAG 어시스턴트다.
Vector Store Tool에서 검색한 문맥을 우선 활용해 답하고,
문서에 없는 내용은 추측하지 말고 모른다고 답한다.
답변 시 보고서의 핵심 수치와 성과를 포함하라.
```

---

### 실습 진행 순서

1. `실습1_ RAG Agent 기초 (답안 배포본).json` Import (또는 직접 구성)
2. Qdrant / Gemini / Google Drive Credential 연결
3. Google Drive에 **`sample.pdf`** 업로드
4. **Google Drive** 노드에서 `sample.pdf` 지정
5. **Vector Store Insert/Retrieve** Collection을 `rag_google_drive_docs`로 통일
6. **When clicking Execute workflow** 실행 → Vector Store 저장 확인
7. **Chat Trigger** → **Open Chat**
8. 아래 테스트 문장 입력

```
2026년 1분기 실적 보고서 알려줘
```

9. Agent가 Vector Store 검색 결과를 바탕으로 보고서 내용을 답변하는지 확인

---

## 테스트 시나리오

### 1단계: `sample.pdf` 적재 확인

1. 워크플로우 저장
2. **When clicking Execute workflow** 실행
3. **Ingestion Result**에서 아래와 유사한 결과 확인

```json
{
  "status": "ingested",
  "message": "Google Drive 문서 임베딩/벡터 저장 완료",
  "collection": "rag_google_drive_docs"
}
```

4. **Extract from File** 출력에 `2026년 1분기 실적 보고서` 관련 텍스트가 포함되는지 확인

### 2단계: 핵심 질의 테스트 (필수)

**Chat Trigger**에서 아래 문장을 입력합니다.

```
2026년 1분기 실적 보고서 알려줘
```

### 기대 답변 (포함되면 정상)

Agent 응답에 아래 내용이 **Vector Store 검색 근거**로 포함되면 성공입니다.

| 항목 | 기대 내용 |
|------|-----------|
| 문서 제목 | 2026년 1분기 실적 보고서 |
| 수료·만족도 | 48명 수료, 만족도 4.6/5.0 |
| 주요 성과 | n8n 실습 참여율 95%, Document Parse·Solar LLM 92% 등 |
| 매출·비용 | 매출 2억 1,500만 원, 비용 1억 3,200만 원, 영업이익률 38.6% |
| 향후 계획 | AI Agent 심화(RAG), 문서 자동화 PoC 등 |

> 정확한 문장은 Agent 표현에 따라 달라질 수 있습니다. **문서에 있는 수치·항목을 근거로 답하면** 정상입니다.

### 3단계: 추가 확인 (선택)

문서에 없는 내용을 질문해 RAG 거절을 확인합니다.

```
2030년 매출 예측 수치를 알려줘.
```

**기대 결과:** "문서에 없음" 또는 "근거 부족" 응답

---

## 제출 조건

- [ ] `sample.pdf`를 Google Drive에 업로드 완료
- [ ] Google Drive → Extract from File → Vector Store Insert 성공
- [ ] Collection 이름 Insert/Retrieve 동일 (`rag_google_drive_docs`)
- [ ] Chat 입력: **"2026년 1분기 실적 보고서 알려줘"** 정상 응답
- [ ] 응답에 보고서 핵심 내용(수료 인원, 매출, 주요 성과 등) 포함
- [ ] 문서에 없는 질문에 추측 답변 없이 거절

---

## 연결 체크리스트

문서 적재:

- [ ] Manual Trigger → Google Drive(`sample.pdf`) → Extract from File → Vector Store → Ingestion Result
- [ ] Default Data Loader → Vector Store (`ai_document`)
- [ ] Embeddings Google Gemini → Vector Store (`ai_embedding`)

RAG 챗봇:

- [ ] Chat Trigger → AI Agent (`main`)
- [ ] Google Gemini Chat Model → AI Agent (`ai_languageModel`)
- [ ] Vector Store Tool → AI Agent (`ai_tool`)
- [ ] Vector Store Retrieve → Vector Store Tool (`ai_vectorStore`)
- [ ] Embeddings Google Gemini → Vector Store Retrieve (`ai_embedding`)
- [ ] Google Gemini Chat Model → Vector Store Tool (`ai_languageModel`)

---

## 힌트 · 자주 나는 오류

| 증상 | 원인 | 해결 |
|------|------|------|
| "2026년 1분기..." 질문에 일반 답변만 나옴 | Vector Store Tool 미연결 또는 Insert 미실행 | Insert 흐름 먼저 실행, Tool 연결 확인 |
| 검색 결과 없음 | Collection 이름 불일치 | Insert/Retrieve 모두 `rag_google_drive_docs` |
| PDF 텍스트 비어 있음 | 잘못된 파일 또는 Extract 미연결 | Google Drive에서 `sample.pdf` 재선택 |
| Qdrant 오류 | URL/API Key 오류 | Qdrant Credential 재확인 |
| 한글 깨짐 | PDF 추출 문제 | `sample.pdf` 원본 파일 재업로드 |

> **중요:** Chat 테스트 전에 반드시 Manual Trigger로 `sample.pdf` 적재를 1회 이상 실행하세요.

---

## 참고 파일

| 파일 | 설명 |
|------|------|
| `sample.pdf` | 실습용 **2026년 1분기 실적 보고서** (Google Drive 업로드 대상) |
| `실습1_ RAG Agent 기초 (답안 배포본).json` | 강사 배포용  답안 |

---

## 외부 문서

- [Qdrant Cloud Quickstart](https://qdrant.tech/documentation/cloud-quickstart/)
- [Qdrant Authentication (API Key)](https://qdrant.tech/documentation/cloud/authentication/)
- [Google AI Studio API Key](https://aistudio.google.com/apikey)
