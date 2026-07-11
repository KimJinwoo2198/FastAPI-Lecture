from enum import StrEnum

from fastapi import FastAPI, status
from pydantic import BaseModel, ConfigDict, Field, field_validator

app = FastAPI(title="02. Pydantic v2")


class Difficulty(StrEnum):
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"


class IdeaCreate(BaseModel):
    model_config = ConfigDict(
        str_strip_whitespace=True,
        extra="forbid",
        json_schema_extra={
            "examples": [
                {
                    "title": "냉장고 레시피",
                    "description": "남은 식재료로 요리를 추천합니다.",
                    "team_size": 3,
                    "difficulty": "medium",
                    "tags": ["Food", "AI"],
                }
            ]
        },
    )

    title: str = Field(min_length=2, max_length=50)
    description: str = Field(min_length=10, max_length=500)
    team_size: int = Field(default=1, ge=1, le=10)
    difficulty: Difficulty = Difficulty.MEDIUM
    tags: list[str] = Field(default_factory=list, max_length=5)

    @field_validator("tags")
    @classmethod
    def normalize_tags(cls, tags: list[str]) -> list[str]:
        normalized = [tag.strip().lower() for tag in tags if tag.strip()]
        return list(dict.fromkeys(normalized))


@app.post("/ideas", status_code=status.HTTP_201_CREATED)
def create_idea(payload: IdeaCreate) -> dict[str, object]:
    """검증이 끝난 Pydantic 모델을 Python dict로 변환합니다."""
    return {
        "message": "Pydantic 검증을 통과했습니다.",
        "data": payload.model_dump(),
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8000)
