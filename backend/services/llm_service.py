# -*- coding: utf-8 -*-
"""
悟堂·东方解忧处 —— 统一 LLM 客户端与智能降级流式驱动
- 原生支持 OpenAI 规范接口（DeepSeek / 阿里通义千问 / 智谱 / Ollama）
- 异步 SSE 流式输出
- 完善的超时重试与本地高保真流式 Mock 降级机制
"""
import asyncio
import json
import re
from typing import AsyncGenerator, Dict, Any, List
from openai import AsyncOpenAI
from backend.config import settings
from backend.services.prompt_builder import SYSTEM_PROMPT_TEMPLATE, build_user_prompt

class LLMService:
    def __init__(self):
        self._client: AsyncOpenAI = None
        self._init_client()

    def _init_client(self):
        # 即使未配置 API Key 也初始化一个合法的客户端，确保调用时按需处理
        api_key = settings.LLM_API_KEY if settings.is_llm_configured else "mock-key"
        self._client = AsyncOpenAI(
            api_key=api_key,
            base_url=settings.LLM_BASE_URL,
            timeout=settings.LLM_TIMEOUT,
        )

    async def stream_relief(
        self,
        user_text: str,
        scenario: str,
        matched_cards: Dict[str, Any],
        retrieved_classics: List[Dict[str, Any]],
    ) -> AsyncGenerator[str, None]:
        """
        生成四步解忧方核心流式生成器
        以 SSE (Server-Sent Events) 协议格式流式产出
        """
        # 1. 尝试通过真实大模型生成
        if settings.is_llm_configured:
            try:
                user_prompt = build_user_prompt(user_text, scenario, matched_cards, retrieved_classics)
                response = await self._client.chat.completions.create(
                    model=settings.LLM_MODEL,
                    messages=[
                        {"role": "system", "content": SYSTEM_PROMPT_TEMPLATE},
                        {"role": "user", "content": user_prompt},
                    ],
                    stream=True,
                    temperature=settings.LLM_TEMPERATURE,
                    max_tokens=settings.LLM_MAX_TOKENS,
                )

                async for chunk in response:
                    delta = chunk.choices[0].delta.content if chunk.choices else ""
                    if delta:
                        yield f"data: {json.dumps({'type': 'token', 'content': delta}, ensure_ascii=False)}\n\n"
                
                # 发送完成事件
                yield f"data: {json.dumps({'type': 'done'}, ensure_ascii=False)}\n\n"
                return
            except Exception as e:
                print(f"[!] 真实 LLM 调用异常，启用韧性降级: {e}")
                # 若开启降级则继续向下执行 fallback

        # 2. 离线/未配置 Key 时的韧性高保真流式生成器
        if settings.ENABLE_FALLBACK_STREAM:
            async for chunk in self._fallback_stream_generator(user_text, scenario, matched_cards, retrieved_classics):
                yield chunk
        else:
            err_msg = "未配置有效 LLM_API_KEY 且已禁用 fallback 生成。"
            yield f"data: {json.dumps({'type': 'error', 'message': err_msg}, ensure_ascii=False)}\n\n"

    async def _fallback_stream_generator(
        self,
        user_text: str,
        scenario: str,
        matched_cards: Dict[str, Any],
        retrieved_classics: List[Dict[str, Any]],
    ) -> AsyncGenerator[str, None]:
        """高质量本地韧性解忧生成器（保证 100% 离线也具备丝滑流式体验）"""
        wisdom = matched_cards.get("wisdom") or {}
        ws = wisdom.get("classic_source") or {}
        quote = ws.get("quote") or wisdom.get("original_text", "知止而后有定")
        book = ws.get("book") or wisdom.get("source_title", "大学")
        chapter = ws.get("chapter") or wisdom.get("source_section", "经一章")
        author = ws.get("author", "先贤")
        interpretation = ws.get("translation") or wisdom.get("modern_interpretation", "知道停留在哪里，心才能定得下来。")

        action = matched_cards.get("action") or {}
        action_title = action.get("title", "今晚 5 分钟：把「事实」和「评价」分开写")
        action_steps = action.get("steps") or [
            "拿出一张白纸，中间划一道竖线。",
            "左边只写发生的事实，右边写当下的情绪与自我评判。",
            "合上本子，今晚先把心安顿好，明天再做微小一步。"
        ]

        full_text = (
            f"## 01 听见了\n"
            f"你写下的这件事，我静静读了几遍。在日常的纷扰里，能停下来觉察并整理自己的难处，这本身就需要莫大的勇气。"
            f"那些压在心头的千头万绪，我都听见了——你并不孤单，你的感受完全值得被温柔以待。\n\n"
            f"## 02 古人有云\n"
            f"《{book}·{chapter}》（{author}）曾有言：\n"
            f"「{quote}」\n\n"
            f"{interpretation} 放到你现在的处境来看，它想说的其实很简单：外界的波澜往往超出掌控，但向内安顿呼吸与注意力的主动权，始终在你手里。\n\n"
            f"## 03 试试这一招\n"
            f"**{action_title}**\n"
            + "\n".join([f"- {s}" for s in action_steps]) +
            f"\n\n## 04 读这一段\n"
            f"《{book}》开篇常读常新。今晚不必求深解，临睡前翻阅片刻，让心念随之自然沉淀即可。"
        )

        # 模拟打字机流式输出 (按段/标点自然节奏分割)
        pieces = re.split(r"(?<=[，。！？\n])", full_text)
        for piece in pieces:
            if piece:
                yield f"data: {json.dumps({'type': 'token', 'content': piece}, ensure_ascii=False)}\n\n"
                await asyncio.sleep(0.04)  # 40ms 平滑打字延迟

        yield f"data: {json.dumps({'type': 'done'}, ensure_ascii=False)}\n\n"

    def parse_markdown_four_step(self, text: str) -> Dict[str, Any]:
        """将生成的 Markdown 解忧文本解析为标准结构化字典"""
        parts = {
            "empathy": "",
            "wisdom": "",
            "micro_action": "",
            "further_reading": "",
            "raw_text": text
        }
        current_sec = None
        lines = text.split("\n")
        for line in lines:
            line_str = line.strip()
            if "01 听见了" in line_str:
                current_sec = "empathy"
                continue
            elif "02 古人有云" in line_str:
                current_sec = "wisdom"
                continue
            elif "03 试试这一招" in line_str:
                current_sec = "micro_action"
                continue
            elif "04 读这一段" in line_str:
                current_sec = "further_reading"
                continue
            
            if current_sec and line_str:
                parts[current_sec] += (line + "\n")

        for k in parts:
            if isinstance(parts[k], str):
                parts[k] = parts[k].strip()

        return parts

llm_service = LLMService()
