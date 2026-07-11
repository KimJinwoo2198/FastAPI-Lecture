from typing import Annotated

from fastapi import APIRouter, Depends
from pydantic import BaseModel

from dependencies import Pagination

router = APIRouter(prefix="/ideas", tags=["아이디어"])


class IdeaResponse(BaseModel):
    id: int
    title: str


ideas = [
    IdeaResponse(id=1, title="AI 여행 일정"),
    IdeaResponse(id=2, title="냉장고 레시피"),
    IdeaResponse(id=3, title="AI 이력서 분석"),
]


@router.get("", response_model=list[IdeaResponse])
def list_ideas(
    pagination: Annotated[Pagination, Depends()],
) -> list[IdeaResponse]:
    return ideas[pagination.offset : pagination.offset + pagination.limit]


@router.get("/{idea_id}", response_model=IdeaResponse)
def get_idea(idea_id: int) -> IdeaResponse:
    return ideas[idea_id - 1]
