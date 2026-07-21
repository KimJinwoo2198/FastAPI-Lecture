from datetime import UTC, datetime
from typing import Annotated

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import Base, engine, get_db
from app.models import Idea
from app.schemas import (
    IdeaCreate,
    IdeaResponse,
    IdeaUpdate,
    IdeaResponse,
)

from fastapi import Depends, FastAPI, HTTPException, Query, status

from app.schemas import IdeaCreate, IdeaResponse, IdeaUpdate, MessageResponse

app = FastAPI(
    title="Hackathon Idea API",
    description="2회차 수업용 메모리 기반 CRUD",
    version="2.0.0",
)

Base.metadata.create_all(bind=engine)
DB = Annotated[Session, Depends(get_db)]


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
def create_idea(payload: IdeaCreate, db: DB) -> IdeaResponse:
    idea = Idea(**payload.model_dump())
    
    db.add(idea)
    db.commit()
    db.refresh(idea)

    return idea


@app.get("/ideas", response_model=list[IdeaResponse], tags=["아이디어"])
def list_ideas(
    db: DB,
    keyword: str | None = Query(default=None, min_length=1, max_length=50),
) -> list[IdeaResponse]:
    statement = select(Idea).order_by(Idea.id.desc())
    
    if keyword:
        statement = statement.where(Idea.title.contains(keyword))
    
    return list(db.scalars(statement).all())


@app.get("/ideas/{idea_id}", response_model=IdeaResponse, tags=["아이디어"])
def get_idea(idea_id: int, db: DB) -> IdeaResponse:
    idea = db.get(Idea, idea_id)
    
    if idea is None:
        raise HTTPException(status_code=404, detail="아이디어를 찾을 수 없습니다.")
    return idea


@app.patch("/ideas/{idea_id}", response_model=IdeaResponse, tags=["아이디어"])
def update_idea(idea_id: int, payload: IdeaUpdate, db: DB) -> IdeaResponse:
    idea = db.get(Idea, idea_id)
    
    if idea is None:
        raise HTTPException(status_code=404, detail="아이디어를 찾을 수 없습니다.")
    
    changes = payload.model_dump(exclude_unset=True)
    
    for field, value in changes.items():
        setattr(idea, field, value)
    
    db.commit()
    db.refresh(idea)
    
    return idea

@app.delete(
    "/ideas/{idea_id}",
    response_model=MessageResponse,
    tags=["아이디어"],
)
def delete_idea(idea_id: int) -> MessageResponse:
    if ideas.pop(idea_id, None) is None:
        raise HTTPException(status_code=404, detail="아이디어를 찾을 수 없습니다.")
    return MessageResponse(message="아이디어를 삭제했습니다.")
