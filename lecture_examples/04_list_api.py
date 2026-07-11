from datetime import UTC, datetime, timedelta
from enum import StrEnum
from typing import Annotated

from fastapi import FastAPI, Query
from pydantic import BaseModel

app = FastAPI(title="04. 검색, 필터, 정렬, 페이지네이션")


class SortOrder(StrEnum):
    LATEST = "latest"
    OLDEST = "oldest"


class IdeaResponse(BaseModel):
    id: int
    title: str
    team_size: int
    created_at: datetime


now = datetime.now(UTC)
ideas = [
    IdeaResponse(id=1, title="AI 여행 일정", team_size=2, created_at=now - timedelta(days=2)),
    IdeaResponse(id=2, title="냉장고 레시피", team_size=3, created_at=now - timedelta(days=1)),
    IdeaResponse(id=3, title="AI 이력서 분석", team_size=3, created_at=now),
]


@app.get("/ideas", response_model=list[IdeaResponse])
def list_ideas(
    keyword: Annotated[str | None, Query(min_length=1, max_length=50)] = None,
    team_size: Annotated[int | None, Query(ge=1, le=10)] = None,
    sort: SortOrder = SortOrder.LATEST,
    offset: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=100)] = 10,
) -> list[IdeaResponse]:
    result = ideas.copy()

    if keyword:
        lowered = keyword.lower()
        result = [idea for idea in result if lowered in idea.title.lower()]

    if team_size is not None:
        result = [idea for idea in result if idea.team_size == team_size]

    result.sort(
        key=lambda idea: idea.created_at,
        reverse=sort == SortOrder.LATEST,
    )

    return result[offset : offset + limit]


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8000)
