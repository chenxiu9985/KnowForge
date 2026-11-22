# KnowForge 架构

前端和后端各有自己的目录。开发时由 FastAPI 同时提供页面、静态资源和 JSON 接口，因此浏览器只需要访问一个地址。

```text
frontend/ 页面
    ↓ HTTP
backend/app/api/quizzes.py
    ├── 创建练习 → ai/workflow.py → ai/generation.py → 题目格式校验
    └── 提交答案 → quiz.py → 得分与解析
```

| 路径 | 职责 |
| --- | --- |
| [`backend/app/main.py`](../backend/app/main.py) | 创建应用、注册路由、服务前端页面和静态资源 |
| [`backend/app/api/quizzes.py`](../backend/app/api/quizzes.py) | 处理 HTTP 请求、保存最近的练习、把业务错误转成接口响应 |
| [`backend/app/quiz.py`](../backend/app/quiz.py) | 定义题目和提交格式，执行确定性的判分 |
| [`backend/app/ai/workflow.py`](../backend/app/ai/workflow.py) | 用 LangGraph 根据是否提供参考资料选择路径，并汇入出题节点 |
| [`backend/app/ai/generation.py`](../backend/app/ai/generation.py) | 用 LangChain 串起提示词、聊天模型和输出校验 |
| [`backend/app/ai/demo.py`](../backend/app/ai/demo.py) | 给离线模拟模型提供固定题库 |
| [`frontend/`](../frontend/) | 收集学习主题和答案，显示题目、得分与解析 |

浏览器通过 `GET /api/config` 获取当前模式和示例主题。`POST /api/quizzes` 接收 `topic` 和可选的 `notes`，返回练习 ID、题干和选项。`POST /api/quizzes/{id}/grade` 接收按题目顺序排列的答案，返回得分、正确答案和解析。完整字段见运行中的 `/docs`。

练习和答案按 ID 保存在当前进程内存中，最多保留最近 100 套。进程重启后需要重新生成。以后可以在出题前增加 RAG 检索节点，也可以把 Deep Agents 的练习规划与审题做成另一条流程，复用现有题目格式和判分逻辑。
