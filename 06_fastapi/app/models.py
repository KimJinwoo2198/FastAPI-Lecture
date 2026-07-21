from datetime import datetime

from sqlalchemy import JSON, DateTime, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class Idea(Base):
    __tablename__ = "ideas"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String(50), nullable=False)
    description: Mapped[str] = mapped_column(String(500), nullable=False)
    team_size: Mapped[int] = mapped_column(default=1, nullable=False)
    tags: Mapped[list[str]] = mapped_column(JSON, default=list, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )


# 3회차 실습: 이 아래에 AI 분석 결과를 저장할 IdeaAnalysis 모델을 추가합니다.
