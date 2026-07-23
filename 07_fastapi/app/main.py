from datetime import UTC, datetime
from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException, Query, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.ai_service import analyze_idea_with_ai
from app.database import Base, engine, get_db
from app.models import Idea, IdeaAnalysis
from app.schemas import (
    IdeaAnalysisResponse,
    IdeaCreate,
    IdeaResponse,
    IdeaUpdate,
    MessageResponse,
)

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Hackathon Idea Coach",
    description="아이디어 CRUD와 Upstage AI 분석을 제공하는 FastAPI 백엔드입니다.",
    version="4.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DB = Annotated[Session, Depends(get_db)]


@app.get("/api-info", tags=["기본"])
def api_info() -> dict[str, str]:
    return {"message": "Hackathon Idea Coach API"}


@app.get("/health", tags=["기본"])
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post(
    "/ideas",
    response_model=IdeaResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["아이디어"],
)
def create_idea(payload: IdeaCreate, db: DB) -> Idea:
    idea = Idea(**payload.model_dump())
    db.add(idea)
    db.commit()
    db.refresh(idea)
    return idea


@app.get("/ideas", response_model=list[IdeaResponse], tags=["아이디어"])
def list_ideas(
    db: DB,
    keyword: str | None = Query(default=None, min_length=1, max_length=50),
) -> list[Idea]:
    statement = select(Idea).order_by(Idea.id.desc())
    if keyword:
        statement = statement.where(Idea.title.contains(keyword))
    return list(db.scalars(statement).all())


@app.get("/ideas/{idea_id}", response_model=IdeaResponse, tags=["아이디어"])
def get_idea(idea_id: int, db: DB) -> Idea:
    idea = db.get(Idea, idea_id)
    if idea is None:
        raise HTTPException(status_code=404, detail="아이디어를 찾을 수 없습니다.")
    return idea


@app.patch("/ideas/{idea_id}", response_model=IdeaResponse, tags=["아이디어"])
def update_idea(idea_id: int, payload: IdeaUpdate, db: DB) -> Idea:
    idea = db.get(Idea, idea_id)
    if idea is None:
        raise HTTPException(status_code=404, detail="아이디어를 찾을 수 없습니다.")

    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(idea, field, value)

    db.commit()
    db.refresh(idea)
    return idea


@app.delete("/ideas/{idea_id}", response_model=MessageResponse, tags=["아이디어"])
def delete_idea(idea_id: int, db: DB) -> MessageResponse:
    idea = db.get(Idea, idea_id)
    if idea is None:
        raise HTTPException(status_code=404, detail="아이디어를 찾을 수 없습니다.")

    analysis = db.scalar(
        select(IdeaAnalysis).where(IdeaAnalysis.idea_id == idea_id)
    )
    if analysis is not None:
        db.delete(analysis)

    db.delete(idea)
    db.commit()
    return MessageResponse(message="아이디어를 삭제했습니다.")


@app.post(
    "/ideas/{idea_id}/analyze",
    response_model=IdeaAnalysisResponse,
    tags=["AI 분석"],
)
def analyze_idea(
    idea_id: int,
    db: DB,
    force: bool = Query(default=False, description="기존 결과를 무시하고 다시 분석"),
) -> IdeaAnalysis:
    idea = db.get(Idea, idea_id)
    if idea is None:
        raise HTTPException(status_code=404, detail="아이디어를 찾을 수 없습니다.")

    analysis = db.scalar(
        select(IdeaAnalysis).where(IdeaAnalysis.idea_id == idea_id)
    )
    if analysis is not None and not force:
        return analysis

    try:
        result = analyze_idea_with_ai(idea)
    except Exception as error:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"AI 분석에 실패했습니다: {error}",
        ) from error

    created_at = datetime.now(UTC)
    if analysis is None:
        analysis = IdeaAnalysis(
            idea_id=idea.id,
            analysis=result.content,
            model=result.model,
            prompt_tokens=result.prompt_tokens,
            completion_tokens=result.completion_tokens,
            created_at=created_at,
        )
        db.add(analysis)
    else:
        analysis.analysis = result.content
        analysis.model = result.model
        analysis.prompt_tokens = result.prompt_tokens
        analysis.completion_tokens = result.completion_tokens
        analysis.created_at = created_at

    db.commit()
    db.refresh(analysis)
    return analysis


@app.get(
    "/ideas/{idea_id}/analysis",
    response_model=IdeaAnalysisResponse,
    tags=["AI 분석"],
)
def get_idea_analysis(idea_id: int, db: DB) -> IdeaAnalysis:
    analysis = db.scalar(
        select(IdeaAnalysis).where(IdeaAnalysis.idea_id == idea_id)
    )
    if analysis is None:
        raise HTTPException(status_code=404, detail="분석 결과를 찾을 수 없습니다.")
    return analysis
