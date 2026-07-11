from typing import Annotated

from fastapi import Body, FastAPI, Header, Path, Query

app = FastAPI(title="01. FastAPI 라우팅")


@app.get("/labs")
def list_labs(
    keyword: Annotated[str | None, Query(min_length=1, max_length=30)] = None,
    limit: Annotated[int, Query(ge=1, le=100)] = 10,
) -> dict[str, object]:
    """함수 매개변수 중 경로에 없는 기본 자료형은 Query가 됩니다."""
    return {"keyword": keyword, "limit": limit}


@app.get("/labs/{lab_id}")
def get_lab(
    lab_id: Annotated[int, Path(ge=1)],
    detail: bool = False,
) -> dict[str, object]:
    """경로에 선언된 이름은 Path Parameter가 됩니다."""
    return {"lab_id": lab_id, "detail": detail}


@app.post("/labs")
def create_lab(
    title: Annotated[str, Body(embed=True, min_length=2)],
    x_client_name: Annotated[str | None, Header()] = None,
) -> dict[str, object]:
    """Body와 Header를 명시적으로 선언한 예제입니다."""
    return {"title": title, "requested_by": x_client_name}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8000)
