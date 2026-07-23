from dataclasses import dataclass

from openai import OpenAI

from app.config import get_settings
from app.models import Idea


@dataclass(frozen=True)
class AnalysisResult:
    content: str
    model: str
    prompt_tokens: int
    completion_tokens: int


def analyze_idea_with_ai(idea: Idea) -> AnalysisResult:
    settings = get_settings()

    if not settings.UPSTAGE_API_KEY:
        raise ValueError("UPSTAGE_API_KEY가 설정되지 않았습니다.")

    client = OpenAI(
        api_key=settings.UPSTAGE_API_KEY,
        base_url=settings.UPSTAGE_API_URL,
        timeout=30.0,
        max_retries=1,
    )

    tags = ", ".join(idea.tags) if idea.tags else "없음"
    completion = client.chat.completions.create(
        model=settings.UPSTAGE_MODEL,
        messages=[
            {
                "role": "system",
                "content": (
                    "너는 2일짜리 해커톤을 여러 번 멘토링한 멘토다. "
                    "아이디어를 무조건 칭찬하지 말고 제한된 시간 안에 시연 가능한 "
                    "MVP를 만들 수 있도록 구체적으로 조언한다. 반드시 다음 순서의 "
                    "Markdown으로 답한다: ## 한 줄 평가, ## 대상 사용자와 문제, "
                    "## 강점, ## 위험 요소, ## 2일 MVP 범위, ## 바로 할 일 3가지."
                ),
            },
            {
                "role": "user",
                "content": (
                    "다음 아이디어를 해커톤 관점에서 분석해줘.\n\n"
                    "<idea>\n"
                    f"제목: {idea.title}\n"
                    f"설명: {idea.description}\n"
                    f"팀 크기: {idea.team_size}\n"
                    f"태그: {tags}\n"
                    "</idea>"
                ),
            },
        ],
        temperature=0.2,
        max_tokens=900,
    )

    content = completion.choices[0].message.content
    if not content:
        raise ValueError("AI가 빈 분석 결과를 반환했습니다.")

    return AnalysisResult(
        content=content,
        model=completion.model,
        prompt_tokens=completion.usage.prompt_tokens if completion.usage else 0,
        completion_tokens=completion.usage.completion_tokens if completion.usage else 0,
    )
