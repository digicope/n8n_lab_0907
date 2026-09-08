# n8n Cloud 문서 Agent 실습 — PDF → Upstage → Google 리포트 자동화

> **교육 과정:** 생성형 AI 활용 교육 (Upstage · 충청ICT)  
> **환경:** [n8n Cloud](https://n8n.io/cloud) (브라우저만으로 실습)  
> **선수 과목:** `n8n_2단계_실습`, `n8n_AI_기초_실습` 완료 권장  
> **사용 API:** [Upstage API](https://console.upstage.ai) · Google Docs / Drive / Gmail  
> **답안 위치:** `답안/` 폴더 JSON → n8n Cloud **Import from File**  
> **로컬 Docker 버전:** `n8n_문서_Agent_실습` 폴더 참고

---

## 학습 목표

n8n Cloud에서 PDF를 Webhook으로 업로드하면, **HTTP Request로 Upstage Document Parse API**를 호출해 문서를 구조화하고 **Solar LLM**으로 요약한 뒤, **Google Docs**에 리포트를 만들어 **Google Drive**에 저장하고 **Gmail**로 전송하는 **문서 처리 Agent 파이프라인**을 구축합니다.

```
Webhook (PDF 업로드)
    ↓
Edit Fields (메타데이터 정리)
    ↓
HTTP Request — Upstage Document Parse API
    ↓
Edit Fields - Extract Markdown
    ↓
Basic LLM Chain + Solar LLM
    ↓
Google Docs 생성 → 내용 삽입
    ↓
Google Drive 폴더 이동
    ↓
Gmail 전송
    ↓
Respond to Webhook (완료 응답)
```

> **Cloud 참고:** n8n Cloud에서는 Upstage **Document Parse Community Node를 사용할 수 없습니다.** Document Parse는 **HTTP Request** 노드로 API를 직접 호출합니다.

---

## Cloud vs 로컬 Docker 비교

| 구분 | n8n Cloud (이번) | 로컬 Docker (`n8n_문서_Agent_실습`) |
|------|------------------|-------------------------------------|
| 설치 | 브라우저 가입만 | Docker·환경 변수 설정 |
| Webhook URL | `https://{인스턴스}.app.n8n.cloud/webhook/...` | `http://localhost:5678/webhook/...` |
| Google 인증 | **원클릭 연결** (GCP 불필요) | GCP OAuth 또는 GAS 우회 |
| Document Parse | **HTTP Request** (Community Node 미지원) | Upstage Document Parse 노드 |
| Community Node | Solar LLM용 `n8n-nodes-upstage`만 설치 | Document Parse + Solar 모두 설치 |
| 24시간 Webhook | **Activate** 후 항상 대기 | PC·Docker 항시 실행 필요 |

---

## 사전 준비

### 1. n8n Cloud 계정 생성

1. [n8n.io/cloud](https://n8n.io/cloud) 접속 → **Get started free** (또는 교육용 계정)
2. 이메일 가입 후 워크스페이스 생성
3. 대시보드 URL 확인  
   예: `https://mycompany.app.n8n.cloud`

> **무료 플랜 참고:** 월 실행 횟수·워크플로우 수에 제한이 있습니다. 교육 실습에는 충분하나, 종합 테스트는 실행 횟수를 확인하세요.

### 2. Upstage Community Node 설치 (Solar LLM용)

n8n Cloud에서는 **Document Parse Community Node를 사용할 수 없습니다.**  
Document Parse는 아래 **HTTP Request** 방식으로 대체하고, **Solar LLM**만 Community Node를 설치합니다.

1. n8n Cloud → **Settings** → **Community nodes**
2. **Install** → `n8n-nodes-upstage` 입력 → 설치 승인
3. 워크플로우에서 `Upstage Solar Chat for Agent` 노드 확인

| 구분 | Cloud 방식 |
|------|------------|
| **Document Parse** | **HTTP Request** → `https://api.upstage.ai/v1/document-digitization` |
| **Solar LLM** | **Upstage Solar Chat for Agent** Community Node |

> Solar 노드가 보이지 않으면 페이지를 새로고침하세요. Document Parse는 Community Node 설치와 **무관하게** HTTP Request로 동작합니다.

### 3. Credential 등록

#### Upstage API — Document Parse (HTTP Request용)

Document Parse API 호출에 **Header Auth** Credential을 사용합니다.

1. [Upstage Console](https://console.upstage.ai) → **API Keys** → 키 복사
2. n8n → **Credentials** → **Add Credential** → **Header Auth**
3. 아래 값 입력:

| 항목 | 값 |
|------|-----|
| **Name** | `Authorization` |
| **Value** | `Bearer YOUR_UPSTAGE_API_KEY` |

4. **HTTP Request — Document Parse** 노드에 이 Credential 연결

> `YOUR_UPSTAGE_API_KEY`를 본인 키로 바꾸세요. `Bearer ` 접두사(공백 포함)를 빠뜨리지 마세요.

#### Upstage API — Solar LLM (Community Node용)

| Credential | 설정 |
|------------|------|
| **Upstage API** | [Upstage Console](https://console.upstage.ai) → API Keys → n8n **Credentials** → **Upstage API**에 키 입력 → **Upstage Solar Chat for Agent** 노드에 연결 |

> Document Parse용 Header Auth와 Solar용 Upstage API Credential **모두 같은 API Key**를 사용해도 됩니다.

#### Google Docs / Drive / Gmail — Cloud 원클릭 연결 (권장 · GCP 불필요)

n8n Cloud는 Google OAuth가 **미리 구성**되어 있어, GCP Console 없이 **Google 계정 로그인만**으로 연결됩니다.

| Credential | 연결 방법 |
|------------|-----------|
| **Google Docs OAuth2 API** | Credentials → **Google Docs OAuth2 API** → **Connect my account** → Google 로그인 → 권한 허용 |
| **Google Drive OAuth2 API** | 동일 — **Connect my account** |
| **Gmail OAuth2 API** | 동일 — **Connect my account** (메일 발송 권한 포함) |

**연결 순서**

1. 답안 워크플로우 Import
2. **Google Docs** 노드 클릭 → Credential → **Create New Credential**
3. **Connect my account** 클릭 → 본인 Google 계정 선택 → **허용**
4. **Google Drive**, **Gmail** 노드에도 같은 Credential 재사용 또는 각각 연결

> Client ID / Secret을 직접 입력할 필요가 **없습니다**. 이것이 Cloud의 가장 큰 장점입니다.

---

#### Google 연동 대안 (Cloud에서도 사용 가능)

GCP 없이 다른 방식을 쓰고 싶다면 로컬 버전과 동일한 우회법을 사용할 수 있습니다.

| 방법 | 설명 | Cloud 적합도 |
|------|------|--------------|
| **원클릭 OAuth** (위 권장) | Connect my account | ⭐⭐⭐ 최적 |
| **B-1 SMTP + 앱 비밀번호** | Gmail 노드 → Send Email 노드 교체 | ⭐⭐ 메일만 |
| **B-2 Google Apps Script** | HTTP Request로 GAS 웹앱 호출 | ⭐⭐⭐ GCP·OAuth 모두 생략 |

##### B-1. Gmail — SMTP + 앱 비밀번호

1. [Google 계정](https://myaccount.google.com) → **보안** → **2단계 인증** → **앱 비밀번호** 생성
2. n8n **Credentials** → **SMTP** 등록

| 항목 | 값 |
|------|-----|
| Host | `smtp.gmail.com` |
| Port | `587` |
| SSL/TLS | `STARTTLS` |
| User | 본인 Gmail |
| Password | 앱 비밀번호 (16자리) |

3. 실습 6·7의 **Gmail** 노드를 **Send Email** 노드로 교체 (Credential: SMTP)

##### B-2. Google Apps Script(GAS) 프록시

Docs·Drive·Gmail을 GAS 웹앱 하나에서 처리합니다. Cloud의 **HTTP Request** 노드가 외부 URL(GAS)을 호출하므로 로컬과 동일하게 동작합니다.

1. [script.google.com](https://script.google.com) → 새 프로젝트 → 아래 코드 붙여넣기
2. **배포** → **웹 앱** → 실행 계정: **나**, 액세스: **모든 사용자**
3. 웹앱 URL을 n8n **HTTP Request** 노드에 연결

```javascript
const REPORT_FOLDER_ID = 'YOUR_FOLDER_ID_HERE';

function doPost(e) {
  try {
    const data = JSON.parse(e.postData.contents);
    const title = data.title || 'PDF 분석 리포트';
    const content = data.content || '';
    const recipientEmail = data.email || '';

    const doc = DocumentApp.create(title);
    doc.getBody().setText(content);
    doc.saveAndClose();
    const docId = doc.getId();
    const docFile = DriveApp.getFileById(docId);

    if (REPORT_FOLDER_ID && REPORT_FOLDER_ID !== 'YOUR_FOLDER_ID_HERE') {
      DriveApp.getFolderById(REPORT_FOLDER_ID).addFile(docFile);
      DriveApp.getRootFolder().removeFile(docFile);
    }

    const docUrl = 'https://docs.google.com/document/d/' + docId + '/edit';
    if (recipientEmail) {
      GmailApp.sendEmail(recipientEmail, '[n8n Agent] ' + title + ' 분석 완료',
        '문서: ' + docUrl + '\n\n' + content);
    }

    return ContentService.createTextOutput(JSON.stringify({
      status: 'completed', documentId: docId, documentUrl: docUrl, email: recipientEmail
    })).setMimeType(ContentService.MimeType.JSON);
  } catch (err) {
    return ContentService.createTextOutput(JSON.stringify({ status: 'error', message: err.message }))
      .setMimeType(ContentService.MimeType.JSON);
  }
}
```

**워크플로우 변경:** Google Docs → Docs1 → Drive → Gmail 4개 노드를 아래로 교체

```
Basic LLM Chain → HTTP Request (POST, GAS URL, JSON Body) → Respond to Webhook
```

```json
={
  "title": "{{ $('Edit Fields').item.json.docTitle }}",
  "email": "{{ $('Edit Fields').item.json.recipientEmail }}",
  "content": "{{ $('Basic LLM Chain').item.json.text }}"
}
```

---

### 4. Google Drive 폴더 준비

1. Google Drive에 `n8n-문서리포트` 폴더 생성
2. URL에서 **폴더 ID** 복사  
   예: `https://drive.google.com/drive/folders/1AbCdEfGhIjKlMnOp` → `1AbCdEfGhIjKlMnOp`
3. 실습 5·6·7 **Google Drive** 노드 `folderId`에 입력

### 5. 테스트용 PDF

- 1~3페이지 한국어 PDF, **50MB 이하**

---

## 공통 설정

| 항목 | 값 |
|------|-----|
| Webhook Method | `POST` |
| Webhook Path | `pdf-agent` |
| PDF Form 필드명 | `file` |
| 메타데이터 필드 | `email`, `title` (선택) |
| Document Parse | **HTTP Request** (multipart/form-data) |
| Document Parse — URL | `https://api.upstage.ai/v1/document-digitization` |
| Document Parse — model | `document-parse` |
| Document Parse — output_formats | `["markdown"]` |
| Document Parse — binary 필드 | form: `document` ← Webhook `file` |
| Edit Fields - Extract Markdown | `markdown` = `={{ $json.content.markdown }}` |
| Solar Model | `solar-mini` 또는 `solar-pro2` |
| Solar Temperature | `0.3` |

---

## Webhook URL 사용법 (Cloud 전용)

n8n Cloud Webhook에는 **두 가지 URL**이 있습니다.

| URL 종류 | 용도 | 예시 |
|----------|------|------|
| **Test URL** | 편집 중 1회 테스트 (`Listen for test event`) | `https://{인스턴스}.app.n8n.cloud/webhook-test/pdf-agent` |
| **Production URL** | 워크플로우 **Activate** 후 상시 수신 | `https://{인스턴스}.app.n8n.cloud/webhook/pdf-agent` |

> `{인스턴스}`는 본인 Cloud 주소입니다. Webhook 노드를 클릭하면 **Production URL** / **Test URL**이 표시됩니다.

---

## 실습 1. Webhook + PDF 업로드 수신

### 목표

Cloud Webhook으로 **PDF + 메타데이터**를 수신합니다.

### 요구사항

```
Webhook → Edit Fields → Respond to Webhook
```

| 노드 | 설정 |
|------|------|
| **Webhook** | Method: `POST`, Path: `pdf-agent`, Response Mode: **Using 'Respond to Webhook' Node** |
| **Edit Fields** | `recipientEmail` = `={{ $json.body.email }}` |
| | `docTitle` = `={{ $json.body.title \|\| 'PDF 분석 리포트' }}` |
| | `fileName` = `={{ $binary.file.fileName }}` |
| **Respond to Webhook** | Body: `={{ { status: 'received', email: $json.recipientEmail, title: $json.docTitle, file: $json.fileName } }}` |

### 테스트 방법

**방법 1 — curl (터미널)**

```bash
curl.exe -X POST "https://digicope.app.n8n.cloud/webhook-test/pdf-agent" -F "file=@sample.pdf" -F "email=your-email@example.com" -F "title=2026년 1분기 실적 보고서"
```

**방법 2 — Postman / Insomnia**

- Method: `POST`
- URL: Webhook **Test URL** (또는 Activate 후 **Production URL**)
- Body: `form-data`
  - `file` → File → PDF 선택
  - `email` → Text
  - `title` → Text

**방법 3 — n8n 에디터**

1. Webhook 노드 → **Listen for test event**
2. 위 curl 또는 Postman으로 Test URL에 요청
3. 에디터에서 실행 결과 확인

### 확인 사항

- [ ] 응답 JSON에 `status`, `email`, `title`, `file`이 있는가?
- [ ] Binary 탭에 `file` PDF가 있는가?

---

## 실습 2. Upstage Document Parse 연동 (HTTP Request)

### 목표

PDF를 **Upstage Document Parse API**로 Markdown 변환합니다. (Cloud에서는 Community Node 대신 **HTTP Request** 사용)

### 요구사항

```
Webhook → Edit Fields → HTTP Request — Document Parse → Edit Fields - Extract Markdown → Respond to Webhook
```

| 노드 | 설정 |
|------|------|
| **HTTP Request — Document Parse** | Method: `POST`, URL: `https://api.upstage.ai/v1/document-digitization` |
| | Authentication: **Bearer Auth** (Name: `Authorization`, Value: `Bearer {API_KEY}`) |
| | Body Content Type: **form-data** |
| | Body Parameter `model` | `document-parse` |
| | Body Parameter `output_formats` | `["markdown"]` |
| | Body Parameter `document` | Type: **n8n Binary File**, Input Field: `file` |
| **Edit Fields - Extract Markdown** | `markdown` = `={{ $json.content.markdown }}` |
| **Respond to Webhook** | `={{ { status: 'parsed', title: $('Edit Fields').item.json.docTitle, preview: ($json.markdown || '').substring(0, 200) + '...' } }}` |
<br>

#### Respond to Webhook Body :
```
{{ { status: 'parsed', title: $('Edit Fields').item.json.docTitle, preview: ($json.markdown || '').substring(0, 200) + '...' } }}
```

**HTTP Request Body Parameters 요약**

| Parameter | Type | Value |
|-----------|------|-------|
| `model` | Form Data | `document-parse` |
| `output_formats` | Form Data | `["markdown"]` |
| `document` | Form Binary Data | Input: `file` (Webhook PDF) |

### 확인 사항

- [ ] HTTP Request 응답에 `content.markdown` 필드가 있는가?
- [ ] **Edit-Field - Extract Markdown** 노드 출력에 `markdown`이 있는가?
- [ ] **Bearer Auth** Credential이 연결되었는가?

### 힌트

- Edit Fields 노드는 Deactivate 시켜놓고 ,**binary 데이터(`file`)를 유지**합니다.
- API 오류 시 HTTP Request 출력의 `error` 메시지와 Status Code를 확인하세요.
- curl로 API를 직접 테스트하려면:

```bash 
curl -X POST "https://api.upstage.ai/v1/document-digitization" \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -F "model=document-parse" \
  -F 'output_formats=["markdown"]' \
  -F "document=@./sample.pdf"
```

---

## 실습 3. Solar LLM 요약 리포트 생성

### 목표

Markdown을 **Solar LLM**으로 요약합니다.

### 요구사항

```
Webhook → Edit Fields → HTTP Request — Document Parse → Edit Fields - Extract Markdown → Basic LLM Chain → Respond to Webhook
                                                                                               ↑
                                                                                 Upstage Solar Chat for Agent
```

| 노드 | 설정 |
|------|------|
| **Upstage Solar Chat for Agent** | Model: `solar-mini`, Temperature: `0.3`, maxTokens: `4096` |

#### Respond to Webhook:
```
{{ { status: 'summarized', summary: $json.text } }}
```

**Prompt (User Message)**

```
당신은 기업 문서 분석 전문가입니다.
아래 Markdown 문서를 한국어로 분석하여 요약 리포트를 작성하세요.

[문서 제목]
{{ $('Edit Fields').item.json.docTitle }}

[원문]
{{ $('Edit Fields - Extract Markdown').item.json.markdown }}

아래 형식으로 작성하세요:

## 한 줄 요약
(1문장)

## 핵심 내용
- (불릿 3~5개)

## 주요 키워드
(쉼표로 구분)

## 후속 조치 제안
- (불릿 1~2개)
```

### 확인 사항

- [ ] Solar Model이 Chain **Model** 슬롯에 연결
- [ ] 프롬프트에서 `$('Edit Fields - Extract Markdown').item.json.markdown` 참조
- [ ] `$json.text`에 한국어 요약 출력

---

## 실습 4. Google Docs 생성 및 내용 삽입

### 목표

요약을 **Google Docs**에 저장합니다.

### 요구사항

```
... → Basic LLM Chain → Google Docs (Create) → Google Docs1 (Update) → Respond to Webhook
```

| 노드 | 설정 |
|------|------|
| **Google Docs** | Title: `={{ $('Edit Fields').item.json.docTitle }}`, Drive: My Drive |
| **Google Docs1** | Doc ID: `={{ $json.id }}`, Text Insert: `={{ $('Basic LLM Chain').item.json.text }}` |
| Credential | **Connect my account** (GCP 불필요) |

#### Respond to Webhook --> Response Body :
```
{{ { status: 'doc_created', documentId: $('Google Docs').item.json.id, url: 'https://docs.google.com/document/d/' + $('Google Docs').item.json.id + '/edit' } }}
```
### 확인 사항

- [ ] Google Docs에 요약 텍스트 삽입
- [ ] 문서 URL 접근 가능

---

## 실습 5. Google Drive 폴더 저장

### 목표

Docs 파일을 지정 **Drive 폴더**로 이동합니다.

### 요구사항

```
... → Google Docs1 (Update) → Google Drive (Move) → Respond to Webhook
```

| 노드 | 설정 |
|------|------|
| **Google Drive** | File Move, File ID: `={{ $('Google Docs').item.json.id }}`, Folder: **본인 폴더 ID** , Parent Drive  : My Drive , Parent Folder  : /(Root folder) |

#### Respond to Webhook :
```
{{ { status: 'saved', folder: 'n8n-문서리포트', documentId: $('Google Docs').item.json.id } }}
```
### 확인 사항

- [ ] `n8n-문서리포트` 폴더에 문서 저장

---

## 실습 6. Gmail 전송

### 목표

리포트 링크·요약을 **Gmail**로 발송합니다.

### 요구사항

```
... → Google Drive → Gmail → Respond to Webhook
```

| 노드 | 설정 |
|------|------|
| **Gmail** | To: `={{ $('Edit Fields').item.json.recipientEmail }}` |
| | Subject: `=[n8n Agent] {{ $('Edit Fields').item.json.docTitle }} 분석 완료` |
| Credential | **Gmail OAuth2 — Connect my account** |
| **Email Type** | Text |

#### Gmail Message :
```
안녕하세요,

요청하신 PDF 문서 분석이 완료되었습니다.

📄 문서 제목: {{ $('Edit Fields').item.json.body.title }}

🔗 Google Docs: https://docs.google.com/document/d/{{ $('Google Docs').item.json.id }}/edit

--- AI 요약 ---
{{ $('Basic LLM Chain').item.json.text }}

---
본 메일은 n8n 문서 Agent 워크플로우에서 자동 발송되었습니다.```

#### Respond to Webhook :
```
{{ { status: 'completed', email: $('Edit Fields').item.json.recipientEmail, documentUrl: 'https://docs.google.com/document/d/' + $('Google Docs').item.json.id + '/edit' } }}
```

### 확인 사항

- [ ] 수신자 이메일로 메일 도착
- [ ] Docs 링크·요약 포함

---

## 실습 7. 종합 — 문서 Agent 파이프라인 (100점 과제)
(이미 6번에서 모두 완성하므로  sticky note 만 추가 한다)

### 목표

실습 1~6을 **하나의 워크플로우**로 통합하고 **Activate**합니다.

### 전체 흐름

```
Webhook → Edit Fields → HTTP Request — Document Parse → Edit Fields - Extract Markdown
  → Basic LLM Chain (+ Upstage Solar Chat for Agent)
  → Google Docs (Create) → Google Docs1 (Update)
  → Google Drive (Move) → Gmail → Respond to Webhook
```

### 추가 요구사항

| 항목 | 조건 |
|------|------|
| Webhook Path | `pdf-agent` |
| Document Parse | HTTP Request + Header Auth + Edit Fields - Extract Markdown |
| 워크플로우 상태 | **Active** (Production URL 사용) |
| Solar Model | `solar-mini` 이상 |
| Google | Connect my account 연결 |
| Drive | `n8n-문서리포트` 폴더 이동 |
| 최종 응답 | `status`, `documentId`, `documentUrl`, `email` |

#### Respond to Webhook :
```
{{ { status: 'completed', email: $('Edit Fields').item.json.recipientEmail, documentId: $('Google Docs').item.json.id, documentUrl: 'https://docs.google.com/document/d/' + $('Google Docs').item.json.id + '/edit' } }}
```
### 최종 테스트

```bash
curl -X POST "https://YOUR-INSTANCE.app.n8n.cloud/webhook/pdf-agent" \
  -F "file=@./sample.pdf" \
  -F "email=your-email@example.com" \
  -F "title=종합실습 테스트 문서"
```

> `YOUR-INSTANCE`를 본인 Cloud 인스턴스명으로 바꾸세요. Webhook 노드의 **Production URL**을 복사해 사용하는 것이 가장 정확합니다.

### 확인 사항 (체크리스트)

- [ ] HTTP Request Document Parse + Edit Fields - Extract Markdown이 동작하는가?
- [ ] 워크플로우가 **Active** 상태인가?
- [ ] Production Webhook URL로 전체 파이프라인이 실행되는가?
- [ ] Google Docs · Drive · Gmail이 모두 동작하는가?
- [ ] Webhook 응답이 `completed`인가?

---

## 체크 포인트 (배점)

| 실습 | 배점 | 핵심 평가 |
|------|------|-----------|
| 실습 1 | 10점 | Cloud Webhook PDF 수신 |
| 실습 2 | 15점 | HTTP Request Document Parse + Edit Fields - Extract Markdown |
| 실습 3 | 20점 | Solar LLM 요약 |
| 실습 4 | 15점 | Google Docs (Connect my account) |
| 실습 5 | 10점 | Google Drive 폴더 이동 |
| 실습 6 | 15점 | Gmail 자동 발송 |
| 실습 7 | 15점 | Active 종합 파이프라인 |
| **합계** | **100점** | |

---

## Import 방법 (n8n Cloud)

1. n8n Cloud 로그인 → **Workflows**
2. 우측 상단 **⋯** → **Import from File**
3. `답안/` 폴더 JSON 선택
4. Credential 연결:
   - **HTTP Request — Document Parse** → **Header Auth** (`Bearer` + Upstage API Key)
   - **Upstage Solar Chat for Agent** → **Upstage API**
   - **Google Docs / Drive / Gmail** → **Connect my account**
5. **Google Drive** 노드 `folderId` 변경
6. **Save** → 우측 상단 토글 **Active** ON
7. Webhook **Production URL**로 테스트

| 실습 | 답안 파일 |
|------|-----------|
| 1 | `답안/실습1_Webhook_PDF_업로드.json` |
| 2 | `답안/실습2_Document_Parse.json` |
| 3 | `답안/실습3_Solar_LLM_요약.json` |
| 4 | `답안/실습4_Google_Docs_생성.json` |
| 5 | `답안/실습5_Google_Drive_저장.json` |
| 6 | `답안/실습6_Gmail_전송.json` |
| 7 | `답안/실습7_종합_문서_Agent_파이프라인.json` |

---

## 자주 묻는 질문 (Cloud)

**Q. Upstage Document Parse 노드가 없어요.**  
A. n8n Cloud에서는 Document Parse Community Node를 **지원하지 않습니다.** 답안대로 **HTTP Request** 노드로 API를 호출하고, **Edit Fields - Extract Markdown** 노드로 `content.markdown`을 추출하세요.

**Q. HTTP Request에서 401 Unauthorized 오류가 납니다.**  
A. Header Auth Credential의 Value가 `Bearer YOUR_API_KEY` 형식인지 확인하세요. `Bearer`와 키 사이에 공백이 있어야 합니다.

**Q. HTTP Request에서 binary data 오류가 납니다.**  
A. Webhook form 필드명이 `file`인지, HTTP Request Body의 `document` 파라미터가 **Form Binary Data** → Input Field `file`로 설정되었는지 확인하세요.

**Q. Upstage Solar 노드가 검색되지 않아요.**  
A. **Settings → Community nodes**에서 `n8n-nodes-upstage`를 설치하고 새로고침하세요. Solar LLM만 Community Node가 필요합니다.

**Q. Google Credential에 Client ID를 입력하라고 나옵니다.**  
A. n8n Cloud에서는 **Connect my account** 버튼을 사용하세요. GCP Client ID/Secret 입력은 **셀프호스팅 전용**입니다.

**Q. Test URL은 되는데 Production URL이 안 됩니다.**  
A. 워크플로우가 **Active** 상태인지 확인하세요. Test URL(`/webhook-test/`)과 Production URL(`/webhook/`)은 다릅니다.

**Q. Webhook이 타임아웃됩니다.**  
A. Document Parse + LLM + Google 연동은 30초~2분 걸릴 수 있습니다. Cloud 플랜의 실행 시간 제한을 확인하세요. 테스트 PDF는 **짧은 문서**를 사용하세요.

**Q. Gmail이 스팸함으로 갑니다.**  
A. 테스트 시 발신·수신을 **같은 Gmail**로 하거나, 본인 계정으로만 테스트하세요.

**Q. 로컬 Docker 답안을 Cloud에 Import해도 되나요?**  
A. 네. 노드 구성은 동일합니다. 이 폴더(`n8n_문서_Agent_실습_Cloud`) 답안은 Cloud용 이름·ID로 정리되어 있습니다.

**Q. GCP 없이 Google 연동이 정말 되나요?**  
A. Cloud의 **Connect my account**가 기본입니다. GAS·SMTP 우회법도 동일하게 사용할 수 있습니다.

---

## 확장 과제 (선택)

- **Structured Output Parser**로 LLM 출력 JSON 구조화
- n8n Cloud **Form Trigger**로 PDF 업로드 UI 제공 (Webhook 대신)
- **Error Workflow**로 실패 시 관리자 알림
- Production URL을 외부 폼·앱에 연동
