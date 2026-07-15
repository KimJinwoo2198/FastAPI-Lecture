from datetime import UTC, datetime

from fastapi import FastAPI, HTTPException, Query, status

from app.schemas import IdeaCreate, IdeaResponse, IdeaUpdate, MessageResponse

app = FastAPI(
    title="Hackathon Idea API",
    description="2회차 수업용 메모리 기반 CRUD",
    version="2.0.0",
)

# TODO: 2회차에서 아래 메모리 저장소를 SQLite로 교체합니다.
ideas: dict[int, IdeaResponse] = {}
next_id = 1


@app.get("/", tags=["기본"])
def root() -> dict[str, str]:
    return {"message": "현재 데이터는 메모리에만 저장됩니다."}


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
) -> list[IdeaResponse]:
    result = list(ideas.values())
    if keyword:
        lowered = keyword.lower()
        result = [idea for idea in result if lowered in idea.title.lower()]
    return result


@app.get("/ideas/{idea_id}", response_model=IdeaResponse, tags=["아이디어"])
def get_idea(idea_id: int) -> IdeaResponse:
    idea = ideas.get(idea_id)
    if idea is None:
        raise HTTPException(status_code=404, detail="아이디어를 찾을 수 없습니다.")
    return idea


@app.patch("/ideas/{idea_id}", response_model=IdeaResponse, tags=["아이디어"])
def update_idea(idea_id: int, payload: IdeaUpdate) -> IdeaResponse:
    idea = ideas.get(idea_id)
    if idea is None:
        raise HTTPException(status_code=404, detail="아이디어를 찾을 수 없습니다.")

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
