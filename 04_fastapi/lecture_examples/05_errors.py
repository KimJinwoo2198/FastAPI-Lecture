from datetime import UTC, datetime

from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, ConfigDict, Field

app = FastAPI(title="05. 상태 코드와 오류 처리")


class IdeaCreate(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")

    title: str = Field(min_length=2, max_length=50)
    description: str = Field(min_length=10, max_length=500)


class IdeaResponse(IdeaCreate):
    id: int
    created_at: datetime


ideas: dict[int, IdeaResponse] = {}
next_id = 1


@app.post(
    "/ideas",
    response_model=IdeaResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_idea(payload: IdeaCreate) -> IdeaResponse:
    global next_id

    normalized_title = payload.title.casefold()
    if any(idea.title.casefold() == normalized_title for idea in ideas.values()):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="같은 제목의 아이디어가 존재합니다.",
        )

    idea = IdeaResponse(
        id=next_id,
        created_at=datetime.now(UTC),
        **payload.model_dump(),
    )
    ideas[next_id] = idea
    next_id += 1
    return idea


@app.get("/ideas/{idea_id}", response_model=IdeaResponse)
def get_idea(idea_id: int) -> IdeaResponse:
    idea = ideas.get(idea_id)
    if idea is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="아이디어를 찾을 수 없습니다.",
        )
    return idea


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8000)
