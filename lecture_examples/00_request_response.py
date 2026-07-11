from fastapi import FastAPI, Response, status

app = FastAPI(title="00. HTTP 요청과 응답 해부")


@app.get("/")
def root() -> dict[str, str]:
    """Python dict는 JSON 응답 Body로 변환됩니다."""
    return {"message": "Hello, FastAPI!"}


@app.get("/request-anatomy")
def request_anatomy() -> dict[str, object]:
    return {
        "request": {
            "method": "GET",
            "path": "/request-anatomy",
            "query": "?keyword=fastapi",
            "headers": {"Accept": "application/json"},
            "body": None,
        },
        "response": {
            "status_code": 200,
            "headers": {"Content-Type": "application/json"},
            "body": {"message": "응답 데이터"},
        },
    }


@app.post("/responses", status_code=status.HTTP_201_CREATED)
def create_response(response: Response) -> dict[str, str]:
    """응답 상태 코드와 Header도 직접 설정할 수 있습니다."""
    response.headers["X-Lecture-Step"] = "00"
    return {"message": "새로운 데이터를 만들었습니다."}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8000)
