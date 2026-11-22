from typing import Annotated, Literal
from uuid import UUID

from pydantic import BaseModel, Field, StringConstraints, field_validator

QUESTION_COUNT = 3
Choice = Literal["A", "B", "C"]
Text = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1)]


class QuizRequest(BaseModel):
    topic: Annotated[Text, Field(max_length=120)]
    notes: Annotated[str, StringConstraints(strip_whitespace=True, max_length=4000)] = ""


class VisibleQuestion(BaseModel):
    question: Text
    options: Annotated[list[Text], Field(min_length=3, max_length=3)]

    @field_validator("options")
    @classmethod
    def distinct_options(cls, options: list[str]) -> list[str]:
        if len({option.casefold() for option in options}) != len(options):
            raise ValueError("选项不能重复")
        return options


class Question(VisibleQuestion):
    answer: Choice
    explanation: Text


class QuizContent(BaseModel):
    questions: Annotated[list[Question], Field(min_length=QUESTION_COUNT, max_length=QUESTION_COUNT)]


class QuizResponse(BaseModel):
    id: UUID
    topic: str
    questions: list[VisibleQuestion]


class Submission(BaseModel):
    answers: Annotated[list[Choice], Field(min_length=QUESTION_COUNT, max_length=QUESTION_COUNT)]


class AnswerResult(BaseModel):
    selected: Choice
    answer: Choice
    correct: bool
    explanation: str


class Grade(BaseModel):
    score: int
    total: int
    results: list[AnswerResult]


def grade_quiz(quiz: QuizContent, submission: Submission) -> Grade:
    results = [
        AnswerResult(
            selected=selected,
            answer=question.answer,
            correct=selected == question.answer,
            explanation=question.explanation,
        )
        for question, selected in zip(quiz.questions, submission.answers, strict=True)
    ]
    return Grade(score=sum(result.correct for result in results), total=len(results), results=results)
