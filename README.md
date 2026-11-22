# KnowForge

KnowForge 是一个用来学习 LangChain、LangGraph 和 Deep Agents 的本地练习项目。目前支持主题出题、答题和复盘。

## 本地启动

从仓库根目录用 Python 3.12 和 pip 启动：

```powershell
python -m pip install -r backend/requirements.txt
python -m uvicorn backend.app.main:app --reload
```

打开 [练习页面](http://127.0.0.1:8000)，从四个示例主题中选一个开始练习。默认使用离线题库。FastAPI 同时提供页面和接口，一条命令就能启动，接口文档在 [/docs](http://127.0.0.1:8000/docs)。

## 项目目录

```text
KnowForge/
├── backend/              FastAPI、AI 出题、判分、Python 依赖与测试
│   ├── app/
│   │   ├── api/          HTTP 路由
│   │   └── ai/           LangChain 出题链与 LangGraph 工作流
│   └── tests/
├── frontend/             练习页面和静态资源
├── docs/                 架构说明和本地开发指南
├── openspec/             当前功能规格和后续变更提案
├── prototypes/           用户流程和页面原型
└── .github/              持续集成配置
```

- 想读懂出题链路，先看 [架构说明](docs/architecture.md)。
- 想接入 DeepSeek 或改代码，先看 [本地开发指南](docs/development.md)。
- 想了解产品行为和验收场景，查看 [练习规格](openspec/specs/quiz-practice/spec.md) 和 [页面流程](prototypes/quiz-flow.md)。

## 运行测试

```powershell
python -m unittest discover -s backend/tests -v
```
