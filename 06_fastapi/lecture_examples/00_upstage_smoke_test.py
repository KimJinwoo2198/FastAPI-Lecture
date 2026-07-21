import os

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

api_key = os.getenv("UPSTAGE_API_KEY")

if not api_key:
    raise RuntimeError("UPSTAGE_API_KEY 환경변수를 먼저 설정해주세요.")

client = OpenAI(
    api_key=api_key,
    base_url="https://api.upstage.ai/v1",
)

completion = client.chat.completions.create(
    model=os.getenv("UPSTAGE_MODEL", "solar-pro3"),
    messages=[
        {
            "role": "system",
            "content": "너는 현실적인 조언을 하는 한국어 해커톤 멘토다.",
        },
        {
            "role": "user",
            "content": "2일 해커톤에서 만들기 좋은 아이디어를 한 문장으로 추천해줘.",
        },
    ],
    max_tokens=200,
)

message = completion.choices[0].message.content

if message is None:
    raise RuntimeError("모델이 비어 있는 응답을 반환했습니다.")

print(message)

if completion.usage:
    print(f"입력 토큰: {completion.usage.prompt_tokens}")
    print(f"출력 토큰: {completion.usage.completion_tokens}")
