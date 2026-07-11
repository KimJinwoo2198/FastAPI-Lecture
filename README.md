# FastAPI 기초 4회차

## 오늘의 완성 목표

Swagger에서 아래 흐름을 직접 실행합니다.

```text
아이디어 생성 → 목록/검색 → 단건 조회 → 수정 → 삭제
```

이번 예제는 DB 대신 메모리를 사용합니다. 서버를 재시작하면 데이터가 사라지는 것이 정상이며, HTTP 요청과 데이터 검증에 집중하기 위한 선택입니다.

## 사용 버전

- Python 3.10+
- FastAPI 0.139.0
- Pydantic 2.13.4

## 실행

```bash
cd ~/Documents/Lecture_FastAPI/04_fastapi
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python app/main.py
```

- API: http://127.0.0.1:8000
- Swagger UI: http://127.0.0.1:8000/docs
- ReDoc: http://127.0.0.1:8000/redoc

```bash
fastapi dev app/main.py
```
