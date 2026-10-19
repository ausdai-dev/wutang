# 悟堂·东方解忧处 —— AI 后台服务驱动引擎

基于 **FastAPI + OpenAI 兼容协议 + RAG 权威考据 + 工业级双轨安全风控** 构建的专业解忧服务后端。

---

## 🌟 核心特性

1. **统一 OpenAI 规范支持**：无缝对接 DeepSeek、阿里云百炼（通义千问）、智谱清言、Ollama 本地私有化部署等。
2. **根绝 LLM 伪名言幻觉 (RAG Grounding)**：
   - 典籍出处严格锚定项目内部经严密考据的 **500 条权威典籍库**与三张解忧卡牌库（心境牌、东方智慧牌、微行动牌）。
   - 大模型专注用于温和共情与落地 5 分钟微行动拆解，绝不信口开河编造假古文。
3. **F-07 工业化双轨安全风控 (Guardrails)**：
   - **48 个高危绝对阻断词**与 **12 组隐蔽危机正则**：自伤/危机意念毫秒级拦截，输出温和非评判关怀与全国救援热线，绝不泄露普通卡片与典籍。
   - **70 个边界复核转介词**：针对临床精神用药、重症及玄学算命进行明确边界声明并指引专业就医。
4. **SSE 流式响应与弹性降级**：
   - `POST /api/relief/stream` 提供毫秒级首字延迟打字机体验。
   - 零配置即开即用：未填 API Key 时自动启用高保真流式生成器，方便前后端无缝联调。
5. **双向容灾与平滑降级**：
   - 前端启动时自动探测后端服务，后端开启时走实时 AI 流式；若后端未开启，自动无缝回退到纯前端离线规则引擎。

---

## 🚀 快速启动

### 1. 安装依赖（已由工程完成）
```bash
pip install -r backend/requirements.txt
```

### 2. 配置大模型 API（可选）
复制 `backend/.env.example` 为 `backend/.env`，根据需要填入 API Key：
```env
# 示例：使用 DeepSeek (推荐)
LLM_BASE_URL=https://api.deepseek.com/v1
LLM_MODEL=deepseek-chat
LLM_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```
> 若不配置 API Key，服务会自动运行在**高保真韧性流式模式**，所有接口与前端联调均可直接正常体验。

### 3. 一键启动后端服务
```bash
python -m backend.app
# 或使用 uvicorn
uvicorn backend.app:app --host 0.0.0.0 --port 8000 --reload
```

启动后可在浏览器访问：
- **服务首页与状态**：`http://localhost:8000/`
- **交互式 API 文档 (Swagger)**：`http://localhost:8000/docs`
- **健康检测接口**：`http://localhost:8000/api/health`

### 4. 运行全套端到端质量测试
```bash
python scripts/test_ai_backend.py
```

---

## 📡 核心 API 端点一览

| 端点 | 方法 | 说明 |
| :--- | :--- | :--- |
| `/api/relief/stream` | `POST` | **核心流式 SSE 接口**：输入心事文本，推流元数据（匹配卡牌）与实时生成 Token |
| `/api/relief/generate` | `POST` | **完整结构化 JSON 接口**：返回四步解忧结构化字段，用于批处理或文章生成 |
| `/api/health` | `GET` | 服务健康检查、已加载典籍数与当前模型状态 |
