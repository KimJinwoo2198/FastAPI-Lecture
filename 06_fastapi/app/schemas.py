from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator


class IdeaCreate(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")

    title: str = Field(min_length=2, max_length=50, description="아이디어 이름")
    description: str = Field(min_length=10, max_length=500, description="해결할 문제")
    team_size: int = Field(default=1, ge=1, le=10, description="팀원 수")
    tags: list[str] = Field(default_factory=list, max_length=5)

    @field_validator("tags")
    @classmethod
    def normalize_tags(cls, tags: list[str]) -> list[str]:
        normalized = [tag.strip().lower() for tag in tags if tag.strip()]
        return list(dict.fromkeys(normalized))


class IdeaUpdate(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")

    title: str | None = Field(default=None, min_length=2, max_length=50)
    description: str | None = Field(default=None, min_length=10, max_length=500)
    team_size: int | None = Field(default=None, ge=1, le=10)
    tags: list[str] | None = Field(default=None, max_length=5)


class IdeaResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    description: str
    team_size: int
    tags: list[str]
    created_at: datetime


class MessageResponse(BaseModel):
    message: str


# 3회차 실습: AI 분석 API의 응답 모델을 이 아래에 추가합니다.
