# 本地开发指南

下列命令都从仓库根目录运行。用现有的 Python 3.12 和 pip 即可。

```powershell
python -m pip install -r backend/requirements.txt
python -m uvicorn backend.app.main:app --reload
```

首页是 `http://127.0.0.1:8000/`。修改 `frontend/` 里的 HTML、CSS 或 JavaScript 后刷新浏览器即可。FastAPI 将 `frontend/assets/` 挂载到 `/static/`。

## 切换到 DeepSeek

默认模式使用固定题库。要测试自定义主题和参考资料，停止服务，在当前 PowerShell 会话设置环境变量，再启动：

```powershell
$env:KNOWFORGE_MODE = 'deepseek'
$env:DEEPSEEK_API_KEY = Read-Host 'DeepSeek API Key' -MaskInput
python -m uvicorn backend.app.main:app --reload
```

主题和参考资料会发送给 DeepSeek API。密钥由后端从环境变量读取。默认模型是 `deepseek-flash`，可以用 `KNOWFORGE_DEEPSEEK_MODEL` 指定其他已开通的模型。关闭该 PowerShell 会话，或在重启前将 `KNOWFORGE_MODE` 设为 `demo`，即可回到离线模式。

## 验证改动

```powershell
python -m unittest discover -s backend/tests -v
```

测试使用模拟模型，无需 API Key。改动页面时，再手动走一遍选主题、答题、提交和查看解析。若要改变用户可见行为，在 `openspec/changes/` 记下变更目标和验收场景，完成后把确认的行为并入 `openspec/specs/`。涉及页面交互的方案可以放在 `prototypes/`。
