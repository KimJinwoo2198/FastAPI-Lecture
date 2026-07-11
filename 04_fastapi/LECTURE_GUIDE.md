# 1주차 강의 진행 가이드

각 예제는 앞 단계보다 개념을 하나씩 추가합니다. 강사는 완성 파일을 열어 설명하고, 일부 값을 바꾸거나 오류를 만들어 동작을 보여줍니다.

## 실행 준비

```bash
cd ~/Documents/Lecture_FastAPI/FastAPI-Lecture/04_fastapi
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

단계별 실행:

```bash
python lecture_examples/00_request_response.py
python lecture_examples/01_routing.py
python lecture_examples/02_pydantic_v2.py
python lecture_examples/03_request_response_models.py
python lecture_examples/04_list_api.py
python lecture_examples/05_errors.py
python lecture_examples/step06_app/main.py
```

IDE의 실행 버튼을 사용해도 됩니다. 서버를 바꿀 때는 기존 서버를 `Ctrl+C`로 종료합니다. 실행 후 브라우저에서 <http://127.0.0.1:8000/docs>를 직접 엽니다.

코드를 수정할 때 서버가 자동으로 다시 시작되는 개발 모드는 다음 명령으로 실행합니다.

```bash
fastapi dev lecture_examples/00_request_response.py
```

## 2시간 타임라인

| 시간 | 파일 | 핵심 개념 |
|---|---|---|
| 0:00~0:15 | `00_request_response.py` | 요청과 응답 해부 |
| 0:15~0:35 | `01_routing.py` | 라우팅, Path, Query, Header, Body |
| 0:35~1:00 | `02_pydantic_v2.py` | Pydantic v2 검증과 422 |
| 1:00~1:10 |  | 휴식 |
| 1:10~1:25 | `03_request_response_models.py` | 생성·수정·응답 모델 분리 |
| 1:25~1:40 | `04_list_api.py` | 검색·필터·정렬·페이지네이션 |
| 1:40~1:50 | `05_errors.py` | 404, 409, 비즈니스 오류 |
| 1:50~2:00 | `step06_app/` | APIRouter와 Depends, 구조 확장 |

## 단계별 질문

### 00. 요청과 응답 해부

- 클라이언트는 서버에 무엇을 보내는가?
- FastAPI 함수가 반환한 `dict`는 어떻게 JSON이 되는가?
- 상태 코드와 응답 Body는 각각 무엇을 설명하는가?

### 01. 라우팅

```text
Path   = 어떤 대상인가?
Query  = 어떻게 조회할 것인가?
Header = 요청에 관한 부가 정보는 무엇인가?
Body   = 어떤 데이터를 전달하는가?
```

`/labs/abc`와 `?detail=hello`를 직접 보내 타입 변환 실패를 확인합니다.

### 02. Pydantic v2

- 타입 힌트는 검증과 문서에 어떻게 사용되는가?
- `Field`는 타입만으로 부족한 규칙을 어떻게 표현하는가?
- `ConfigDict(extra="forbid")`가 없으면 오타 필드는 어떻게 되는가?
- `field_validator`는 언제 필요한가?
- `model_dump()`는 무엇을 반환하는가?

### 03. 요청과 응답 모델

- 생성할 때 사용자가 `id`를 보내지 않는 이유는?
- 수정 모델의 필드가 모두 선택값인 이유는?
- `exclude_unset=True`가 없으면 어떤 문제가 생기는가?
- 내부 데이터와 공개 응답을 분리해야 하는 이유는?

### 04. 목록 API

처리 순서를 바꾸며 결과 차이를 확인합니다.

```text
검색 → 필터 → 정렬 → 페이지네이션
```

페이지네이션을 먼저 적용하면 전체 데이터가 아닌 일부만 검색하게 됩니다.

### 05. 오류 처리

```text
422 = 요청 데이터의 모양이나 값이 잘못됨
404 = 요청한 대상이 없음
409 = 데이터는 유효하지만 서비스 규칙과 충돌
```

### 06. APIRouter와 Depends

- `main.py`는 앱 조립과 실행 진입점만 담당합니다.
- `APIRouter`는 관련 API를 묶습니다.
- `Depends`는 반복되는 입력이나 준비 작업을 재사용합니다.
- 2주차에는 `Depends`로 DB Session을 주입합니다.

## 실습 과제

1. `02_pydantic_v2.py`에 `contact_email: EmailStr | None`을 추가합니다.
2. `04_list_api.py`에 `min_team_size` 필터를 추가합니다.
3. `05_errors.py`에서 대소문자와 공백을 무시하고 중복 제목을 검사합니다.
4. `step06_app/dependencies.py`에 `max_limit=50` 규칙을 적용합니다.

`EmailStr` 실습 시에는 `email-validator` 설치가 추가로 필요하므로, 시간이 부족하면 제외합니다.
