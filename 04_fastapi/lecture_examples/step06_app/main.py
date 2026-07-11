from fastapi import FastAPI

from routers.ideas import router as ideas_router

app = FastAPI(title="06. APIRouter와 Depends")
app.include_router(ideas_router)


@app.get("/health", tags=["기본"])
def health() -> dict[str, str]:
    return {"status": "ok"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8000)
