# -*- coding: utf-8 -*-
"""
悟堂·东方解忧处 —— AI 后台主程序 (FastAPI)
启动入口：python -m backend.app 或 uvicorn backend.app:app --reload
"""
import sys
from pathlib import Path

# 确保项目根目录在 sys.path 中
ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
import uvicorn

from backend.config import settings
from backend.routers.relief import router as relief_router
from backend.routers.wellbeing import router as wellbeing_router
from backend.routers.growth import router as growth_router
from backend.routers.card_export import router as card_export_router

app = FastAPI(
    title="悟堂·东方解忧处 AI 引擎",
    description="基于 RAG 权威考据典籍、官方 DeepSeek-v4-flash 与品牌文风铁律的解忧与个人成长支持服务 (PRD 3.0)",
    version="3.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# 配置 CORS 允许跨域（支持任意本地端口及静态单页面跨域访问）
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles

# 挂载静态资产目录（若存在）
assets_dir = ROOT / "frontend" / "assets"
if assets_dir.exists():
    app.mount("/assets", StaticFiles(directory=str(assets_dir)), name="assets")

# 挂载业务路由
app.include_router(relief_router)
app.include_router(wellbeing_router)
app.include_router(growth_router)
app.include_router(card_export_router)

@app.get("/", response_class=HTMLResponse)
async def root():
    index_file = ROOT / "frontend" / "index.html"
    if index_file.exists():
        return FileResponse(index_file)
    return HTMLResponse("<h1>悟堂前端正在构建中，请运行 python scripts/build_frontend.py</h1>")

@app.get("/status", response_class=HTMLResponse)
async def status_dashboard():
    return f"""
    <!DOCTYPE html>
    <html lang="zh-CN">
    <head>
        <meta charset="utf-8">
        <title>悟堂 · AI 后台服务</title>
        <style>
            body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; background: #F8F6F1; color: #2C2825; padding: 40px; line-height: 1.6; max-width: 680px; margin: auto; }}
            .card {{ background: #FFFFFF; border-radius: 12px; padding: 28px; box-shadow: 0 4px 20px rgba(0,0,0,0.06); border: 1px solid #E5DFD5; }}
            h1 {{ color: #8C3A2B; margin-top: 0; font-weight: 600; font-size: 24px; }}
            .tag {{ display: inline-block; padding: 4px 10px; background: #F2E8DC; color: #8C3A2B; border-radius: 20px; font-size: 13px; font-weight: 500; margin-bottom: 16px; }}
            .status-item {{ display: flex; justify-content: space-between; padding: 8px 0; border-bottom: 1px solid #F0ECE4; font-size: 14px; }}
            a.btn {{ display: inline-block; background: #8C3A2B; color: #FFF; text-decoration: none; padding: 10px 18px; border-radius: 6px; font-size: 14px; margin-top: 20px; margin-right: 10px; }}
            a.btn:hover {{ background: #732E22; }}
        </style>
    </head>
    <body>
        <div class="card">
            <span class="tag">悟堂 PRD 3.0 AI 服务引擎 (东方解忧 + 个人成长 + 心境健康)</span>
            <h1>🌿 悟堂 · 东方解忧处 AI 后台运行中</h1>
            <p style="color: #6B635B; font-size: 14px;">不说教，不预测；先接住，再看清，最后走一步。</p>
            
            <div class="status-item"><span>服务状态</span><strong style="color:#2E7D32;">● 正常运转中 (v3.0.0)</strong></div>
            <div class="status-item"><span>官方大模型驱动</span><strong>{'已连接官方 DeepSeek API' if settings.is_llm_configured else '韧性高保真流式生成模式'}</strong></div>
            <div class="status-item"><span>模型名称</span><code>{settings.LLM_MODEL}</code></div>
            <div class="status-item"><span>接口地址</span><code>{settings.LLM_BASE_URL}</code></div>
            <div class="status-item"><span>解忧流式端点</span><code>POST /api/relief/stream</code></div>
            <div class="status-item"><span>心境健康自评</span><code>GET /api/wellbeing/instruments ｜ POST /api/wellbeing/score</code></div>
            <div class="status-item"><span>专业资源导航</span><code>GET /api/resources</code></div>
            <div class="status-item"><span>AI 日记提炼</span><code>POST /api/journal/organize</code></div>
            <div class="status-item"><span>情境练习室</span><code>POST /api/practice/chat</code></div>
            <div class="status-item"><span>健康监测</span><a href="/api/health" target="_blank" style="color:#8C3A2B;">/api/health</a></div>
            
            <div style="margin-top:20px;">
                <a href="/" class="btn">进入悟堂解忧前端界面 →</a>
                <a href="/docs" class="btn" style="background:#5B21B6;" target="_blank">查看 Swagger API 文档 →</a>
            </div>
        </div>
    </body>
    </html>
    """

def run_server():
    print(f"\n=======================================================")
    print(f"🌿 悟堂·东方解忧处 AI 驱动后台启动中...")
    print(f"   地址: http://localhost:{settings.PORT}")
    print(f"   接口文档: http://localhost:{settings.PORT}/docs")
    print(f"   大模型状态: {'[真实 API 已激活]' if settings.is_llm_configured else '[韧性高保真流式模式]'}")
    print(f"=======================================================\n")
    uvicorn.run("backend.app:app", host=settings.HOST, port=settings.PORT, reload=settings.DEBUG)

if __name__ == "__main__":
    run_server()
