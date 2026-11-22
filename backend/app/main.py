from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from langchain_core.language_models import BaseChatModel

from .ai.generation import configured_model
from .api.quizzes import create_quiz_router

FRONTEND = Path(__file__).resolve().parents[2] / "frontend"


def create_app(model: BaseChatModel | None = None) -> FastAPI:
    app = FastAPI(title="KnowForge", description="主题出题和练习判分")
    app.include_router(create_quiz_router(model))
    app.mount("/static", StaticFiles(directory=FRONTEND / "assets"), name="static")

    @app.get("/", include_in_schema=False)
    async def index() -> FileResponse:
        return FileResponse(FRONTEND / "index.html")

    return app


app = create_app(configured_model())
