"""练习的出题和判分接口。"""

from uuid import UUID, uuid4

from fastapi import APIRouter, HTTPException, status
from langchain_core.language_models import BaseChatModel

from ..ai.demo import DEMO_QUIZZES
from ..ai.generation import GenerationFailed, GenerationTimeout, InvalidQuizInput
from ..ai.workflow import build_quiz_workflow
from ..quiz import (
    Grade,
    QuizContent,
    QuizRequest,
    QuizResponse,
    Submission,
    VisibleQuestion,
    grade_quiz,
)

MAX_QUIZZES = 100


def create_quiz_router(model: BaseChatModel | None) -> APIRouter:
    router = APIRouter(prefix="/api")
    workflow = build_quiz_workflow(model)
    quizzes: dict[UUID, QuizContent] = {}

    @router.get("/config")
    async def config():
        return {"mode": "demo" if model is None else "deepseek", "topics": list(DEMO_QUIZZES)}

    @router.post("/quizzes", status_code=status.HTTP_201_CREATED)
    async def create_quiz(request: QuizRequest) -> QuizResponse:
        try:
            result = await workflow.ainvoke({"request": request})
        except InvalidQuizInput as exc:
            raise HTTPException(422, str(exc)) from exc
        except GenerationTimeout as exc:
            raise HTTPException(status.HTTP_504_GATEWAY_TIMEOUT, str(exc)) from exc
        except GenerationFailed as exc:
            raise HTTPException(status.HTTP_502_BAD_GATEWAY, str(exc)) from exc

        quiz = result["quiz"]
        quiz_id = uuid4()
        if len(quizzes) >= MAX_QUIZZES:
            del quizzes[next(iter(quizzes))]
        quizzes[quiz_id] = quiz

        return QuizResponse(
            id=quiz_id,
            topic=request.topic,
            questions=[
                VisibleQuestion(question=question.question, options=question.options)
                for question in quiz.questions
            ],
        )

    @router.post("/quizzes/{quiz_id}/grade")
    async def grade(quiz_id: UUID, submission: Submission) -> Grade:
        quiz = quizzes.get(quiz_id)
        if quiz is None:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "这套练习已失效，请重新生成。")
        return grade_quiz(quiz, submission)

    return router
