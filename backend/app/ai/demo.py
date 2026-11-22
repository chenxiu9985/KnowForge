"""固定题库，让浏览器和出题链都能在没有 API Key 时运行。"""

from ..quiz import Choice, Question, QuizContent


def _question(text: str, options: tuple[str, str, str], answer: Choice, explanation: str) -> Question:
    return Question(question=text, options=list(options), answer=answer, explanation=explanation)


DEMO_QUIZZES = {
    "Python asyncio": QuizContent(questions=[
        _question(
            "在协程中，通常怎样等待 asyncio.sleep(1) 完成？",
            ("直接调用 asyncio.sleep(1)", "使用 await asyncio.sleep(1)", "使用 time.sleep(1)"),
            "B", "await 会暂停当前协程，把执行机会交还给事件循环。time.sleep 会阻塞当前线程。",
        ),
        _question(
            "在运行中的事件循环里，哪个函数可以把一个协程安排成独立任务？",
            ("asyncio.run", "asyncio.sleep", "asyncio.create_task"),
            "C", "asyncio.create_task 把协程包装成 Task，并安排它在当前事件循环中运行。",
        ),
        _question(
            "两个协程都在等待独立的网络请求，为什么同时启动它们通常更快？",
            ("一个等待网络时，另一个可以继续推进", "每个协程自动绑定一个 CPU 核", "事件循环会跳过网络请求"),
            "A", "协程等待 I/O 时可以让出执行权，事件循环便能推进其他任务。",
        ),
    ]),
    "LangChain": QuizContent(questions=[
        _question(
            "在 prompt | model | parser 中，哪个环节把模型结果转为应用可用的数据？",
            ("prompt", "model", "parser"),
            "C", "parser 读取模型输出并将其转换成声明的数据结构。",
        ),
        _question(
            "将用户主题代入 ChatPromptTemplate，直接得到的是什么？",
            ("待发送给模型的消息", "模型生成的题目", "最终得分"),
            "A", "提示词模板根据变量组织消息，之后才由聊天模型生成回复。",
        ),
        _question(
            "Pydantic 校验通过后，关于一道生成的单选题可以确定什么？",
            ("答案一定符合事实", "输出满足声明的字段和字段约束", "题目一定来自指定资料"),
            "B", "结构校验能检查字段和约束，题目内容是否正确仍需独立验证。",
        ),
    ]),
    "LangGraph": QuizContent(questions=[
        _question(
            "同一个出题流程要根据是否有参考资料选择不同路径，应该用什么？",
            ("条件边", "固定边", "输出解析器"),
            "A", "条件边根据当前状态决定接下来执行哪个节点。",
        ),
        _question(
            "LangGraph 的节点执行完后，通常通过什么把结果交给后续节点？",
            ("直接调用所有后续节点", "返回需要更新的状态字段", "写入环境变量"),
            "B", "节点返回状态更新，图运行时把这些更新合并进共享状态。",
        ),
        _question(
            "想在中断后继续同一个工作流线程，通常应使用什么？",
            ("新的提示词模板", "更高的模型温度", "配置 checkpointer 并复用 thread_id"),
            "C", "checkpointer 保存线程的图状态，thread_id 用于定位需要继续的线程。",
        ),
    ]),
    "Deep Agents": QuizContent(questions=[
        _question(
            "哪项任务最适合先尝试 Deep Agents 的规划和委派能力？",
            ("把一个字符串转成大写", "根据多份资料规划题库，并委派子 Agent 审题", "计算三道题的总分"),
            "B", "规划和委派适合需要拆解、收集资料、独立复核的多步骤任务。",
        ),
        _question(
            "把资料整理委派给子 Agent，有什么直接好处？",
            ("子 Agent 保证没有事实错误", "每次模型调用都不收费", "整理过程可以使用独立上下文，主 Agent 接收精简结果"),
            "C", "子 Agent 在独立上下文中工作，有助于减少主 Agent 需要保存的中间信息。",
        ),
        _question(
            "Deep Agents 的虚拟文件系统可以用来做什么？",
            ("把长资料和中间产物放到文件里，需要时再读", "自动校验每道题的事实", "让语言模型无需接收任何上下文"),
            "A", "虚拟文件工具可保存和按需读取中间内容，有助于管理上下文。",
        ),
    ]),
}
