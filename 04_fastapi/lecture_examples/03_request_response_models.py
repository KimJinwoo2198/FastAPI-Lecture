from datetime import UTC, datetime

from fastapi import FastAPI, status
from pydantic import BaseModel, ConfigDict, Field

app = FastAPI(title="03. 요청 모델과 응답 모델")


class IdeaBase(BaseModel):
    title: str = Field(min_length=2, max_length=50)
    description: str = Field(min_length=10, max_length=500)
    team_size: int = Field(default=1, ge=1, le=10)


class IdeaCreate(IdeaBase):
    model_config = ConfigDict(extra="forbid")


class IdeaUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    title: str | None = Field(default=None, min_length=2, max_length=50)
    description: str | None = Field(default=None, min_length=10, max_length=500)
    team_size: int | None = Field(default=None, ge=1, le=10)


class IdeaResponse(IdeaBase):
    id: int
    created_at: datetime


idea = IdeaResponse(
    id=1,
    title="FastAPI 해커톤",
    description="두 시간 동안 핵심 API를 만들어봅니다.",
    team_size=3,
    created_at=datetime.now(UTC),
)


@app.post(
    "/ideas",
    response_model=IdeaResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_idea(payload: IdeaCreate) -> IdeaResponse:
    return IdeaResponse(id=1, created_at=datetime.now(UTC), **payload.model_dump())


@app.patch("/ideas/1", response_model=IdeaResponse)
def update_idea(payload: IdeaUpdate) -> IdeaResponse:
    global idea
    changes = payload.model_dump(exclude_unset=True)
    idea = idea.model_copy(update=changes)
    return idea


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8000)
