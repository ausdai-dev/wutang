# -*- coding: utf-8 -*-
"""
悟堂·东方解忧处 —— AI 后台配置中心
支持任何 OpenAI 兼容协议的大模型（DeepSeek、阿里云百炼通义千问、智谱清言、Ollama 等）
"""
import os
from pathlib import Path
from pydantic import BaseModel
from dotenv import load_dotenv

# 加载 .env 文件（优先寻找 backend/.env，其次项目根目录 .env）
BASE_DIR = Path(__file__).resolve().parent
ROOT_DIR = BASE_DIR.parent

env_paths = [BASE_DIR / ".env", ROOT_DIR / ".env"]
for p in env_paths:
    if p.exists():
        load_dotenv(p)
        break

class Settings(BaseModel):
    # 服务配置
    HOST: str = os.getenv("WUTANG_HOST", "0.0.0.0")
    PORT: int = int(os.getenv("WUTANG_PORT", "8000"))
    DEBUG: bool = os.getenv("WUTANG_DEBUG", "false").lower() == "true"

    # 大模型 API 配置（OpenAI 兼容规范 - 官方 DeepSeek）
    LLM_API_KEY: str = os.getenv("LLM_API_KEY", "").strip()
    LLM_BASE_URL: str = os.getenv("LLM_BASE_URL", "https://api.deepseek.com").strip()
    LLM_MODEL: str = os.getenv("LLM_MODEL", "deepseek-v4-flash").strip()
    LLM_TIMEOUT: float = float(os.getenv("LLM_TIMEOUT", "30.0"))
    LLM_TEMPERATURE: float = float(os.getenv("LLM_TEMPERATURE", "0.7"))
    LLM_MAX_TOKENS: int = int(os.getenv("LLM_MAX_TOKENS", "1500"))

    # 兜底与降级开关：未配置 API Key 或请求超时时，是否启用高质量离线解忧引擎流式生成
    ENABLE_FALLBACK_STREAM: bool = os.getenv("ENABLE_FALLBACK_STREAM", "true").lower() == "true"

    # 路径配置
    ASSETS_DIR: Path = ROOT_DIR / "frontend" / "assets"
    KNOWLEDGE_DIR: Path = ROOT_DIR / "knowledge"

    @property
    def is_llm_configured(self) -> bool:
        """检查是否已配置有效的大模型 Key"""
        return bool(self.LLM_API_KEY and not self.LLM_API_KEY.startswith("your-") and len(self.LLM_API_KEY) > 8)

settings = Settings()
