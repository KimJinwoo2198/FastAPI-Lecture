# 3회차 실습 자료 — FastAPI에 Upstage AI 연결하기

## 오늘의 결과물

지난 시간에 만든 아이디어 CRUD에 AI 분석 기능을 추가합니다.

```text
사용자
  → POST /ideas/{idea_id}/analyze
  → FastAPI가 SQLite에서 아이디어 조회
  → Upstage Solar Pro 3 호출
  → 분석 결과와 토큰 사용량 수신
  → SQLite에 분석 결과 저장
  → 사용자에게 JSON 응답
```

완성할 API:

```http
POST /ideas/{idea_id}/analyze
GET  /ideas/{idea_id}/analysis
```

같은 분석을 반복 호출해 크레딧을 낭비하지 않도록 기존 결과를 재사용하고, 정말 다시 분석하고 싶을 때만 `force=true`를 사용합니다.

```http
POST /ideas/{idea_id}/analyze?force=true
```

응답 예시:

```json
{
  "idea_id": 1,
  "analysis": "## 한 줄 평가\n...",
  "model": "solar-pro3",
  "prompt_tokens": 198,
  "completion_tokens": 421,
  "analyzed_at": "2026-07-21T10:30:00Z"
}
```

## 1. 준비하기

Upstage Console에 가입하고 API Key를 발급받습니다.

- 콘솔: <https://console.upstage.ai/>
- API Key 화면: <https://console.upstage.ai/api-keys?api=chat>
- 사용량 확인: <https://console.upstage.ai/usage>
- 크레딧 확인: <https://console.upstage.ai/billing>

가입 프로모션으로 제공되는 $10 크레딧의 잔액과 유효기간은 본인 콘솔에서 직접 확인합니다. 크레딧 정책은 변경될 수 있습니다.

## 2. 프로젝트 실행 준비

프로젝트 폴더로 이동합니다.

```bash
cd 06_fastapi
```

macOS/Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
cp .env.example .env
```

Windows PowerShell:

```powershell
py -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
Copy-Item .env.example .env
```

`.env`를 열어 본인의 키를 입력합니다.

```env
UPSTAGE_API_KEY=up_본인의_키
UPSTAGE_MODEL=solar-pro3
```

주의:

- API Key를 Python 코드에 직접 적지 않습니다.
- `.env`를 GitHub에 올리지 않습니다.
- API Key를 화면 공유나 채팅에 노출하지 않습니다.
- 강사 키 하나를 여러 명이 같이 사용하지 않습니다.

## 3. Upstage 연결만 먼저 확인하기

FastAPI와 연결하기 전에 가장 작은 코드로 API Key가 정상인지 확인합니다.

```bash
python lecture_examples/00_upstage_smoke_test.py
```

정상이라면 모델의 답변과 입력·출력 토큰 수가 출력됩니다.

```text
입력 토큰: 31
출력 토큰: 48
```

여기까지 성공했다면 다음 네 가지가 정상입니다.

1. Python 패키지 설치
2. `.env` 파일 위치
3. API Key
4. Upstage 서버 연결

## 4. 왜 `from openai import OpenAI`를 사용할까?

Upstage Chat API가 OpenAI SDK와 호환되는 요청 형식을 제공하기 때문입니다.

```python
client = OpenAI(
    api_key=api_key,
    base_url="https://api.upstage.ai/v1",
)
```

여기서 실제 요청 목적지는 `base_url`이 결정합니다. 따라서 위 코드는 OpenAI 모델이 아니라 Upstage의 `solar-pro3` 모델을 호출합니다.

```python
completion = client.chat.completions.create(
    model="solar-pro3",
    messages=[...],
)
```

## 5. 메시지의 역할

```python
messages=[
    {
        "role": "system",
        "content": "너는 현실적인 한국어 해커톤 멘토다.",
    },
    {
        "role": "user",
        "content": "다음 아이디어를 분석해줘...",
    },
]
```

- `system`: 모델이 어떤 역할과 규칙을 따라야 하는지 설명합니다.
- `user`: 이번 요청에서 실제로 처리할 데이터를 전달합니다.
- `assistant`: 이전 모델 답변을 대화 문맥에 포함할 때 사용합니다. 오늘은 사용하지 않습니다.

## 6. 응답에서 자주 보는 값

```python
completion.choices[0].message.content
completion.model
completion.usage.prompt_tokens
completion.usage.completion_tokens
```

- `content`: 모델이 생성한 실제 답변
- `model`: 응답을 생성한 모델
- `prompt_tokens`: 요청에 사용된 입력 토큰
- `completion_tokens`: 답변에 사용된 출력 토큰

토큰은 모델이 텍스트를 처리하는 단위이며 API 비용과 관련됩니다. 정확한 비용은 콘솔의 최신 가격표와 Usage에서 확인합니다.

## 7. 실습용 아이디어

Swagger UI에서 먼저 아이디어를 생성합니다.

```json
{
  "title": "냉장고 구조대",
  "description": "냉장고 속 식재료와 유통기한을 기록하면 먼저 먹어야 할 재료와 가능한 요리를 추천합니다.",
  "team_size": 3,
  "tags": ["food", "ai", "mobile"]
}
```

```http
POST /ideas
```

생성된 `id`가 1이라면 다음 API를 실행합니다.

```http
POST /ideas/1/analyze
```

분석 후 별도의 분석 조회 API에서 결과가 남아 있는지 확인합니다.

```http
GET /ideas/1/analysis
```

같은 POST 요청을 한 번 더 실행하면 Upstage를 다시 호출하지 않고 저장된 결과를 반환합니다. 강제로 새 분석을 만들 때만 다음 요청을 사용합니다.

```http
POST /ideas/1/analyze?force=true
```

## 8. 왜 분석을 별도 테이블에 저장할까?

시작 템플릿의 `ideas` 테이블은 지난 시간 완성본 그대로 유지합니다. 수업 중 다음 테이블을 새로 추가합니다.

```text
ideas
  id, title, description, team_size, tags, created_at

idea_analyses
  id, idea_id, analysis, model,
  prompt_tokens, completion_tokens, analyzed_at
```

`idea_id`는 어떤 아이디어의 분석인지 연결합니다. 하나의 아이디어에는 최신 분석 하나만 저장하도록 `unique=True`를 사용합니다.

새 테이블은 `Base.metadata.create_all()`이 만들 수 있으므로 기존 `ideas` 테이블에 컬럼을 추가할 때처럼 DB를 초기화할 필요가 없습니다.

## 9. 최종 파일 역할

```text
app/
├── main.py          # FastAPI 라우팅과 HTTP 오류 변환
├── schemas.py       # API 요청·응답 모양
├── models.py        # ideas, idea_analyses 테이블
├── database.py      # Engine, Session, Depends
├── config.py        # .env 환경설정 읽기
└── ai_service.py    # Upstage 호출과 프롬프트
```

`main.py` 안에 모든 코드를 넣어도 동작은 합니다. 하지만 외부 API 호출을 `ai_service.py`에 분리하면 라우팅, AI 호출, 설정의 책임이 구분되어 코드를 찾고 바꾸기 쉬워집니다.

## 10. 실행 방법

로컬 개발 서버:

```bash
fastapi dev app/main.py
```

Swagger UI:

```text
http://127.0.0.1:8000/docs
```

Docker Compose:

```bash
docker compose up --build
```

Compose 실행 중에는 `app` 폴더가 컨테이너에 연결되어 Python 파일을 저장하면 개발 서버가 자동으로 다시 시작됩니다.

종료:

```bash
docker compose down
```

데이터까지 완전히 초기화할 때만 다음 명령을 사용합니다.

```bash
docker compose down -v
```

`-v`는 SQLite 데이터가 들어 있는 Docker Volume을 삭제합니다.

## 11. 자주 발생하는 오류

### `UPSTAGE_API_KEY가 설정되지 않았습니다`

- `.env` 파일이 `06_fastapi` 바로 아래에 있는지 확인합니다.
- 파일 이름이 `.env.txt`가 아닌지 확인합니다.
- Docker를 사용한다면 `.env` 수정 후 컨테이너를 다시 시작합니다.

### `401` 또는 `Upstage API 키를 확인해주세요`

- 키 앞뒤에 따옴표나 공백이 들어갔는지 확인합니다.
- 키를 새로 발급한 후 기존 키를 폐기합니다.
- 콘솔에서 프로젝트와 키 상태를 확인합니다.

### `429 Too Many Requests`

- 너무 짧은 시간에 여러 번 실행했는지 확인합니다.
- Usage와 크레딧 잔액을 확인합니다.
- 잠시 후 다시 요청합니다.

### `503 Upstage 서버에 연결할 수 없습니다`

- 인터넷 연결을 확인합니다.
- 회사·학교 네트워크에서 외부 API가 차단됐는지 확인합니다.
- 잠시 후 다시 시도합니다.

### `no such table: idea_analyses`

`IdeaAnalysis`가 `Base.metadata.create_all()` 실행 전에 import되는지 확인하고 서버를 다시 시작합니다.

```bash
docker compose restart
```

새 테이블 추가만으로는 기존 `ideas` 데이터를 삭제할 필요가 없습니다.

## 12. 시간이 남으면 하는 미션

다음 중 하나를 선택합니다.

1. `focus` 요청 필드를 추가해 수익성, 기술 난이도, 사용자 문제 중 하나에 집중하게 만들기
2. 분석 결과 삭제 API 만들기
3. `max_tokens`를 바꾸고 출력 토큰 수 비교하기
4. 프롬프트 형식을 바꾸고 분석 품질 비교하기
5. 아이디어가 수정되면 기존 분석을 자동 삭제하거나 오래된 결과로 표시하기

## 공식 문서

- [Upstage 시작하기](https://console.upstage.ai/docs/getting-started)
- [Upstage Chat 가이드](https://console.upstage.ai/docs/capabilities/generate/chat)
- [Upstage Chat API Reference](https://console.upstage.ai/api/chat)
- [Upstage API Key 예제](https://console.upstage.ai/api-keys?api=chat)
- [Upstage Billing](https://console.upstage.ai/billing)
