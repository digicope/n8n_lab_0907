# n8n 기초 Workflow 실습 (무료 · 가입 불필요)

> **교육 과정:** 생성형 AI 활용 교육   
> **특징:** Discord, Gmail, OpenWeatherMap 등 **별도 사이트 가입·API Key 없이** 진행  
> **사용 API:** [JSONPlaceholder](https://jsonplaceholder.typicode.com) (무료 공개 테스트 API)  
> **답안 위치:** `답안/` 폴더의 개별 JSON 파일 → n8n **Import from File**로 바로 가져오기

---

## 사전 준비


| 항목         | 내용                                              |
| ---------- | ----------------------------------------------- |
| n8n        | Cloud 무료 체험 또는 로컬 설치 ([n8n.io](https://n8n.io)) |
| Credential | **불필요** (공개 API만 사용)                            |
| 인터넷        | HTTP Request 노드 실행 시 필요                         |


### 이번 실습에서 배우는 것

- 워크플로우 만들기 · 노드 연결 · 실행
- **Manual Trigger** — 버튼으로 수동 실행
- **Edit Fields (Set)** — 데이터 생성·수정
- **HTTP Request** — 공개 API 호출
- **IF** — 조건 분기
- **Merge** — 두 데이터 합치기
- **Code** — JavaScript로 데이터 가공

---



## 실습 1. 첫 워크플로우 — 데이터 만들기



### 목표

노드를 연결하고, 버튼 한 번으로 메시지 데이터를 만듭니다.

### 요구사항

```
Manual Trigger → Edit Fields → No Operation
```


| 노드               | 설정                                                  |
| ---------------- | --------------------------------------------------- |
| **Edit Fields**  | `name` = `홍길동`, `message` = `n8n 첫 실습입니다!` (고정 문자열) |
| **No Operation** | (설정 없음 — 결과 확인용)                                    |




### 확인 사항

- [ ] 노드 3개가 왼쪽→오른쪽으로 연결되었는가?
- [ ] **Test workflow** 실행 후 Edit Fields 출력에 `name`, `message`가 보이는가?



### 힌트

- Edit Fields 추가: 검색창에 `Edit Fields` 또는 `Set` 입력
- No Operation은 데이터를 그대로 통과시키며, 마지막 노드 출력을 확인할 때 사용

---



## 실습 2. 공개 API 호출 — HTTP Request



### 목표

인터넷의 공개 API에서 게시글 1건을 가져옵니다. **회원가입·API Key 불필요**

### 요구사항

```
Manual Trigger → HTTP Request
```


| 노드               | 설정                                                  |
| ---------------- | --------------------------------------------------- |
| **HTTP Request** | Method: `GET`                                       |
|                  | URL: `https://jsonplaceholder.typicode.com/posts/1` |




### 확인 사항

- [ ] 실행 후 출력 JSON에 `title`, `body`, `userId` 필드가 있는가?
- [ ] `id` 값이 `1`인가?



### 힌트

- JSONPlaceholder는 개발용 무료 API입니다
- Authentication 설정은 **None** 으로 둡니다

---



## 실습 3. 데이터 걸러내기 — Limit + Edit Fields



### 목표

게시글 10건을 가져온 뒤 **3건만** 남기고, 필요한 필드만 추출합니다.

### 요구사항

```
Manual Trigger → HTTP Request → Limit → Edit Fields
```


| 노드               | 설정                                                           |
| ---------------- | ------------------------------------------------------------ |
| **HTTP Request** | GET `https://jsonplaceholder.typicode.com/posts`             |
| **Limit**        | Max Items: `3`                                               |
| **Edit Fields**  | `postId` = `={{ $json.id }}`, `title` = `={{ $json.title }}` |




### 확인 사항

- [ ] 최종 출력 아이템이 **3개**인가?
- [ ] 각 아이템에 `postId`, `title`만 있는가?



### 힌트

- `/posts` (끝에 숫자 없음)는 게시글 목록(배열)을 반환합니다
- Expression 입력: 필드 옆 **fx** 클릭 → `={{ $json.필드명 }}`

---



## 실습 4. 조건 분기 — IF 노드



### 목표

점수에 따라 **합격 / 불합격** 메시지를 다르게 만듭니다.

### 요구사항

```
Manual Trigger → Edit Fields → IF → (true) Edit Fields1
                              → (false) Edit Fields2
```


| 노드                       | 설정                                           |
| ------------------------ | -------------------------------------------- |
| **Edit Fields**          | `score` = `75` (숫자 Number 타입)                |
| **IF**                   | `{{ $json.score }}` **is greater than or equal to** `60` |
| **Edit Fields1** (true)  | `result` = `합격`                              |
| **Edit Fields2** (false) | `result` = `불합격`                             |



### 확인 사항

- [ ] score=75일 때 **합격** 분기로 가는가?
- [ ] score를 50으로 바꾸면 **불합격** 분기로 가는가?



### 힌트

- IF 노드에는 **true**, **false** 두 개의 출력 포트가 있습니다
- 각 포트에 Edit Fields 노드를 따로 연결합니다

---



## 실습 5. 병렬 실행 + Merge



### 목표

두 사용자 정보를 **동시에** 가져와 하나의 메시지로 합칩니다.

### 요구사항

```
                    → HTTP Request (users/1) ──┐
Manual Trigger ─────┤                          ├→ Merge → Edit Fields
                    → HTTP Request1 (users/2) ─┘
```


| 노드                | 설정                                                     |
| ----------------- | ------------------------------------------------------ |
| **HTTP Request**  | GET `https://jsonplaceholder.typicode.com/users/1`     |
| **Edit Fields**   | `user1` = `={{ $json.name }}`                          |
| **HTTP Request1** | GET `https://jsonplaceholder.typicode.com/users/2`     |
| **Edit Fields1**  | `user2` = `={{ $json.name }}`                          |
| **Merge**         | Mode: **Combine**, Combine By: **Position**            |
| **Edit Fields2**  | `summary` = `={{ $json.user1 + ' & ' + $json.user2 }}` |


```
                         → HTTP Request → Edit Fields ──┐
Manual Trigger ─────────┤                               ├→ Merge → Edit Fields2
                         → HTTP Request1 → Edit Fields1 ┘
```



### 확인 사항

- [ ] Manual Trigger에서 **두 HTTP Request로 분기**되는가?
- [ ] Merge Input 1 = users/1, Input 2 = users/2 인가?
- [ ] 최종 `summary`에 두 사람 이름이 포함되는가?



### 힌트

- Trigger에서 나가는 화살표를 드래그해 노드 2개에 각각 연결
- Merge는 Input 1, Input 2 순서가 중요합니다

---



## 실습 6. Code 노드로 가공하기



### 목표

JavaScript 코드로 API 응답을 직접 가공합니다.

### 요구사항

```
Manual Trigger → HTTP Request → Code
```


| 노드               | 설정                                                 |
| ---------------- | -------------------------------------------------- |
| **HTTP Request** | GET `https://jsonplaceholder.typicode.com/posts/1` |
| **Code**         | 아래 로직 구현                                           |


**Code 노드 JavaScript (요구 로직)**

- 입력 게시글의 `title`을 가져옴
- `wordCount` = 제목을 공백 기준으로 나눈 단어 수
- `upperTitle` = 제목을 대문자로 변환
- 위 두 필드를 포함한 객체 반환



### 확인 사항

- [ ] 출력에 `wordCount`, `upperTitle` 필드가 있는가?
- [ ] `upperTitle`이 원본 title의 대문자 버전인가?



### 힌트

```javascript
const title = $input.first().json.title;
return [{
  json: {
    title,
    wordCount: title.split(' ').length,
    upperTitle: title.toUpperCase()
  }
}];
```

---



## 체크 포인트


| 실습     | 배점       | 핵심 평가                    |
| ------ | -------- | ------------------------ |
| 실습 1   | 10점      | 노드 연결, Set 고정값           |
| 실습 2   | 15점      | HTTP Request GET, 공개 API |
| 실습 3   | 15점      | Limit, Expression        |
| 실습 4   | 20점      | IF 조건 분기                 |
| 실습 5   | 20점      | 병렬 분기, Merge             |
| 실습 6   | 20점      | Code 노드 JavaScript       |
| **합계** | **100점** |                          |


---



## Import 방법

1. n8n → **Workflows** → **⋯** → **Import from File**
2. `답안/` 폴더에서 해당 실습 JSON 선택
3. **Test workflow** 로 실행·출력 확인


| 실습  | 답안 파일                   |
| --- | ----------------------- |
| 1   | `답안/실습1_첫_워크플로우.json`   |
| 2   | `답안/실습2_공개_API_호출.json` |
| 3   | `답안/실습3_데이터_걸러내기.json`  |
| 4   | `답안/실습4_조건_분기.json`     |
| 5   | `답안/실습5_병렬_Merge.json`  |
| 6   | `답안/실습6_Code_노드.json`   |


---



## 자주 묻는 질문

**Q. Credential을 연결해야 하나요?**  
A. 아니요. 이번 실습은 모두 Credential 없이 진행합니다.

**Q. JSONPlaceholder가 안 되면?**  
A. 인터넷 연결을 확인하세요. 회사 방화벽에서 차단될 수 있습니다.

**Q. 답안을 그대로 Import해도 되나요?**  
A. 학습 초기에는 Import 후 노드 설정을 하나씩 열어보며 비교하는 것을 권장합니다.
