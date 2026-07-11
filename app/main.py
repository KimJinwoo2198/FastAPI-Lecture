from datetime import UTC, datetime

from fastapi import FastAPI, HTTPException, Query, status

from app.schemas import IdeaCreate, IdeaResponse, IdeaUpdate, MessageResponse

app = FastAPI(
    title="Hackathon Idea API",
    description="FastAPI 기초 1회차: Path, Query, Body, Pydantic, 상태 코드",
    version="1.0.0",
)

# 1회차에는 DB 대신 메모리를 사용해 HTTP와 Pydantic에 집중합니다.
ideas: dict[int, IdeaResponse] = {}
next_id = 1


@app.get("/", tags=["기본"])
def root() -> dict[str, str]:
    return {"message": "Swagger 문서는 /docs에서 확인하세요."}


@app.get("/health", tags=["기본"])
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post(
    "/ideas",
    response_model=IdeaResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["아이디어"],
)
def create_idea(payload: IdeaCreate) -> IdeaResponse:
    """Body를 검증하고 새로운 아이디어를 생성합니다."""
    global next_id

    idea = IdeaResponse(
        id=next_id,
        created_at=datetime.now(UTC),
        **payload.model_dump(),
    )
    ideas[next_id] = idea
    next_id += 1
    return idea


@app.get("/ideas", response_model=list[IdeaResponse], tags=["아이디어"])
def list_ideas(
    keyword: str | None = Query(default=None, min_length=1, max_length=50),
    limit: int = Query(default=10, ge=1, le=100),
) -> list[IdeaResponse]:
    """Query Parameter로 검색하고 결과 개수를 제한합니다."""
    result = list(ideas.values())
    if keyword:
        lowered = keyword.lower()
        result = [idea for idea in result if lowered in idea.title.lower()]
    return result[:limit]


@app.get("/ideas/{idea_id}", response_model=IdeaResponse, tags=["아이디어"])
def get_idea(idea_id: int) -> IdeaResponse:
    """Path Parameter로 하나의 아이디어를 찾습니다."""
    idea = ideas.get(idea_id)
    if idea is None:
        raise HTTPException(status_code=404, detail="아이디어를 찾을 수 없습니다.")
    return idea


@app.patch("/ideas/{idea_id}", response_model=IdeaResponse, tags=["아이디어"])
def update_idea(idea_id: int, payload: IdeaUpdate) -> IdeaResponse:
    idea = ideas.get(idea_id)
    if idea is None:
        raise HTTPException(status_code=404, detail="아이디어를 찾을 수 없습니다.")

    # exclude_unset=True: 요청에서 생략한 필드는 기존 값을 유지합니다.
    updated = idea.model_copy(update=payload.model_dump(exclude_unset=True))
    ideas[idea_id] = updated
    return updated


@app.delete(
    "/ideas/{idea_id}",
    response_model=MessageResponse,
    tags=["아이디어"],
)
def delete_idea(idea_id: int) -> MessageResponse:
    if ideas.pop(idea_id, None) is None:
        raise HTTPException(status_code=404, detail="아이디어를 찾을 수 없습니다.")
    return MessageResponse(message="아이디어를 삭제했습니다.")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8000)
