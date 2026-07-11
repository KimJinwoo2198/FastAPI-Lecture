from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator


class IdeaCreate(BaseModel):
    """POST 요청 Body: 사용자가 보내야 하는 값."""

    model_config = ConfigDict(
        str_strip_whitespace=True,
        extra="forbid",
        json_schema_extra={
            "examples": [
                {
                    "title": "냉장고 재료 기반 레시피 추천",
                    "description": "남은 식재료를 입력하면 요리를 추천합니다.",
                    "team_size": 3,
                    "tags": ["food", "recommendation"],
                }
            ]
        },
    )

    title: str = Field(min_length=2, max_length=50, description="아이디어 이름")
    description: str = Field(min_length=10, max_length=500, description="해결할 문제")
    team_size: int = Field(default=1, ge=1, le=10, description="팀원 수")
    tags: list[str] = Field(default_factory=list, max_length=5)

    @field_validator("tags")
    @classmethod
    def normalize_tags(cls, tags: list[str]) -> list[str]:
        """Pydantic v2의 field_validator 예제."""
        normalized = [tag.strip().lower() for tag in tags if tag.strip()]
        return list(dict.fromkeys(normalized))


class IdeaUpdate(BaseModel):
    """PATCH 요청 Body: 보낸 값만 수정한다."""

    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")

    title: str | None = Field(default=None, min_length=2, max_length=50)
    description: str | None = Field(default=None, min_length=10, max_length=500)
    team_size: int | None = Field(default=None, ge=1, le=10)
    tags: list[str] | None = Field(default=None, max_length=5)


class IdeaResponse(BaseModel):
    """API 응답 모양: 내부 데이터 중 공개할 값만 선언한다."""

    id: int
    title: str
    description: str
    team_size: int
    tags: list[str]
    created_at: datetime


class MessageResponse(BaseModel):
    message: str

