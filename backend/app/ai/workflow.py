"""LangGraph 通过请求中的资料决定出题路径。"""

from typing import Literal, NotRequired, TypedDict

from langchain_core.language_models import BaseChatModel
from langgraph.graph import END, START, StateGraph

from ..quiz import QuizContent, QuizRequest
from .generation import generate_quiz


class QuizState(TypedDict):
    request: QuizRequest
    source_rule: NotRequired[str]
    quiz: NotRequired[QuizContent]


def _select_source(state: QuizState) -> Literal["topic_only", "with_notes"]:
    return "with_notes" if state["request"].notes else "topic_only"


def _topic_only(_: QuizState) -> dict[str, str]:
    return {"source_rule": "根据学习主题和可靠的基础知识出题。"}


def _with_notes(_: QuizState) -> dict[str, str]:
    return {"source_rule": "依据参考资料出题。让每题解析指出支撑答案的资料内容。"}


def build_quiz_workflow(model: BaseChatModel | None = None):
    async def generate(state: QuizState) -> dict[str, QuizContent]:
        request = state["request"]
        quiz = await generate_quiz(request.topic, request.notes, state["source_rule"], model)
        return {"quiz": quiz}

    graph = StateGraph(QuizState)
    graph.add_node("topic_only", _topic_only)
    graph.add_node("with_notes", _with_notes)
    graph.add_node("generate", generate)
    graph.add_conditional_edges(START, _select_source)
    graph.add_edge("topic_only", "generate")
    graph.add_edge("with_notes", "generate")
    graph.add_edge("generate", END)
    return graph.compile()
