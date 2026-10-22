# -*- coding: utf-8 -*-
"""
悟堂·东方解忧处 —— 统一 LLM 客户端与智能降级流式驱动 (PRD 4.0 儒释道升级版)
- 原生支持 OpenAI 规范接口（DeepSeek / 阿里通义千问 / 智谱 / Ollama）
- 异步 SSE 流式输出，支持儒释道三大宗师角色与三圣圆桌
- 完善的超时重试与本地高保真流式 Mock 降级机制
- 自动提炼生成【专属解脱卡印】
"""
import asyncio
import json
import re
from typing import AsyncGenerator, Dict, Any, List, Optional
from openai import AsyncOpenAI
from backend.config import settings
from backend.services.prompt_builder import (
    SYSTEM_PROMPT_TEMPLATE,
    build_system_prompt,
    build_user_prompt,
    get_school_key,
    MASTER_PERSONAS
)
from backend.services.rag_service import rag_service

class LLMService:
    def __init__(self):
        self._client: AsyncOpenAI = None
        self._client_loop = None

    def _get_client(self) -> AsyncOpenAI:
        """获取绑定到当前活跃事件循环的 AsyncOpenAI 客户端"""
        try:
            current_loop = asyncio.get_running_loop()
        except RuntimeError:
            current_loop = None

        if self._client is None or self._client_loop != current_loop:
            api_key = settings.LLM_API_KEY if settings.is_llm_configured else "mock-key"
            self._client = AsyncOpenAI(
                api_key=api_key,
                base_url=settings.LLM_BASE_URL,
                timeout=settings.LLM_TIMEOUT,
            )
            self._client_loop = current_loop
        return self._client

    async def stream_relief(
        self,
        user_text: str,
        scenario: str,
        matched_cards: Dict[str, Any],
        retrieved_classics: List[Dict[str, Any]],
        track: Optional[str] = "confucianism",
        master: Optional[str] = None,
        user_nickname: Optional[str] = "同修",
        pre_matched_zen_card: Optional[Dict[str, Any]] = None
    ) -> AsyncGenerator[str, None]:
        """
        生成四步/四维解惑核心流式生成器
        以 SSE (Server-Sent Events) 协议格式流式产出
        """
        accumulated_text = ""

        # 1. 尝试通过真实大模型生成
        if settings.is_llm_configured:
            try:
                sys_prompt = build_system_prompt(track, master)
                user_prompt = build_user_prompt(
                    user_text, scenario, matched_cards, retrieved_classics,
                    track=track, master=master, user_nickname=user_nickname
                )
                response = await self._get_client().chat.completions.create(
                    model=settings.LLM_MODEL,
                    messages=[
                        {"role": "system", "content": sys_prompt},
                        {"role": "user", "content": user_prompt},
                    ],
                    stream=True,
                    temperature=settings.LLM_TEMPERATURE,
                    max_tokens=settings.LLM_MAX_TOKENS,
                )

                async for chunk in response:
                    delta = chunk.choices[0].delta.content if chunk.choices else ""
                    if delta:
                        accumulated_text += delta
                        yield f"data: {json.dumps({'type': 'token', 'content': delta}, ensure_ascii=False)}\n\n"

                if not accumulated_text.strip():
                    raise RuntimeError("LLM 流式返回内容为空，启用高保真兜底生成")

                # 提取卡印并发送
                sig_data = self._extract_or_synthesize_signature(accumulated_text, matched_cards, retrieved_classics, track, master, user_nickname, pre_matched_zen_card=pre_matched_zen_card)
                yield f"data: {json.dumps({'type': 'card_signature', 'data': sig_data}, ensure_ascii=False)}\n\n"

                # 发送完成事件
                yield f"data: {json.dumps({'type': 'done'}, ensure_ascii=False)}\n\n"
                return
            except Exception as e:
                print(f"[!] 真实 LLM 调用异常，启用韧性降级: {e}")
                # 若开启降级则继续向下执行 fallback

        # 2. 离线/未配置 Key 时的韧性高保真流式生成器
        if settings.ENABLE_FALLBACK_STREAM:
            async for chunk in self._fallback_stream_generator(
                user_text, scenario, matched_cards, retrieved_classics,
                track=track, master=master, user_nickname=user_nickname,
                pre_matched_zen_card=pre_matched_zen_card
            ):
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
        track: Optional[str] = "confucianism",
        master: Optional[str] = None,
        user_nickname: Optional[str] = "同修",
        pre_matched_zen_card: Optional[Dict[str, Any]] = None
    ) -> AsyncGenerator[str, None]:
        """高质量本地韧性宗师解惑生成器（保证 100% 离线也具备丝滑流式体验）"""
        school_key = get_school_key(track)
        persona = MASTER_PERSONAS.get(school_key, MASTER_PERSONAS["confucianism"])

        wisdom = matched_cards.get("wisdom") or {}
        ws = wisdom.get("classic_source") or {}
        quote = ws.get("quote") or wisdom.get("original_text", "知止而后有定")
        book = ws.get("book") or wisdom.get("source_title", "大学")
        chapter = ws.get("chapter") or wisdom.get("source_section", "经一章")
        author = ws.get("author", persona["master_name"])
        interpretation = ws.get("translation") or wisdom.get("modern_interpretation", "知道停留在哪里，心才能定得下来。")

        action = matched_cards.get("action") or {}
        action_title = action.get("title", "今晚 5 分钟：把「事实」和「评价」分开写")
        action_steps = action.get("steps") or [
            "拿出一张白纸，中间划一道竖线。",
            "左边只写发生的事实，右边写当下的情绪与自我评判。",
            "合上本子，今晚先把心安顿好，明天再做微小一步。"
        ]

        if school_key == "daoism":
            empathy_text = f"你写下的心事，老夫静静读过。人世纷扰，皆因用力过猛而心神劳形。你能停步向内觉察，便已是回归本朴的契机。那些浮沉与得失，皆如过客，你并不孤单。"
            wisdom_text = f"《{book}·{chapter}》（{author}）云：\n「{quote}」\n\n{interpretation} 放到你当下的处境来看，世事变幻如流水，越是紧绷抓取，心越疲惫。退后一步，松开控制，道法自然，转机自现。"
            action_text = f"**【守静调息法】**\n- 闭目合眼，深呼吸三次，将注意力放归丹田与腹部起伏；\n- 关掉手中闪烁的屏幕，静坐五分钟，听一听窗外的风声与夜色；\n- 告诉自己：允许今晚的事情停留在这个状态，明天自有天地的节律。"
            mantra_text = "致虚守静，若水从容。不争于一时，方能逍遥于万里。"
            card_name = "守静" if len(wisdom.get("name", "")) < 2 else wisdom.get("name", "若水")[:2]
            eng_motto = "Rest in stillness, flow like water."
        elif school_key == "buddhism":
            empathy_text = f"善哉。你此刻所感受的困惑与焦灼，我悉知悉见。一切苦痛纠结，皆因执念深重心随境转。你能在尘劳中生起向内探寻之念，便是一抹珍贵的觉悟光明。"
            wisdom_text = f"《{book}·{chapter}》（{author}）开示道：\n「{quote}」\n\n{interpretation} 困扰你的痛苦并非坚固不可化解之实体，一切皆是因缘流转的梦幻泡影。不执着于过去，不安住于未来，当下即是清凉。"
            action_text = f"**【当下观照小功课】**\n- 轻轻把右手放在心口，感受胸膛的温热与呼吸起伏；\n- 默念：‘念头只是过客，我才是广阔的天空’，静待浊气呼出；\n- 喝一杯温开水，感恩这具承载生命的身体，放下今日所有的牵挂。"
            mantra_text = "应无所住，明心自安。凡所有相皆是虚妄，心平处万般清凉。"
            card_name = "无住" if len(wisdom.get("name", "")) < 2 else wisdom.get("name", "见性")[:2]
            eng_motto = "Abide nowhere to discover your true peace."
        elif school_key == "symposium":
            empathy_text = f"东方三圣在此，静听你所倾吐的心事。人生行路，既有责任之重，亦有顺逆之常，更有聚散之缘。你的迷茫，正是生命在呼唤更深邃智慧的明灯照亮。"
            wisdom_text = f"《{book}·{chapter}》（{author}）示道：\n「{quote}」\n\n{interpretation} 儒以立身，教你担当自立；道以养生，教你柔韧不争；释以修心，教你破相自在。三家圆融，天地自然宽广。"
            action_text = f"**【三教合参微行动】**\n- 儒行：写下一件今晚眼前能动手的微小善意动作；\n- 道观：推迟一个毫无意义的焦虑争执，松开紧绷；\n- 释歇：静坐深呼吸一分钟，安住当下，念念分明。"
            mantra_text = "立德修身以入世，致虚守静以逍遥，破执明心以解脱。"
            card_name = "圆融"
            eng_motto = "Harmony of three wisdoms illuminates life."
        else:
            empathy_text = f"求道者【{user_nickname}】，你写下的这件事，老夫反复体味。人在世间立身，遇到委屈、焦虑与阻碍在所难免。能有勇气在此审思自省，实乃进德修业的君子气象。"
            wisdom_text = f"《{book}·{chapter}》（{author}）谆谆告诫：\n「{quote}」\n\n{interpretation} 凡事向外求人、怪罪外界往往徒增内耗。把目光收回到自己身上，看清自己当下能主导的一小步，仁者不忧，勇者不惧。"
            action_text = f"**【事上磨练：分清事实与情绪】**\n- 拿出一张纸，左边写下客观发生的事实，右边写下主观的烦恼评判；\n- 将精力只放在左边可以动手改变的小事上；\n- 完成一个微动作后即刻就寝，明早再行日用之功。"
            mantra_text = "君子求诸己，仁者不忧。知行合一，当下便是立身处。"
            card_name = "克己" if len(wisdom.get("name", "")) < 2 else wisdom.get("name", "修己")[:2]
            eng_motto = "Self-restraint and right action bring true dignity."

        # 匹配 96 张东方智慧常道画廊中最契合的心象牌 (优先锁定预匹配结果，保证前后绝对一致)
        if pre_matched_zen_card and pre_matched_zen_card.get("card_id"):
            matched_zen_card = dict(pre_matched_zen_card)
        else:
            matched_zen_card = rag_service.match_zen96_card(
                user_text=user_text,
                track=track,
                card_name=card_name
            )

        full_text = (
            f"## 【闻心 · 先圣洞幽】\n{empathy_text}\n\n"
            f"## 【示道 · 宗师真诠】\n{wisdom_text}\n\n"
            f"## 【笃行 · 当下功课】\n{action_text}\n\n"
            f"## 【法印 · 专属定心偈】\n{mantra_text}\n\n"
            f"---\n"
            f"【解脱卡印】\n"
            f"- 卡名：{card_name}\n"
            f"- 定心偈：{mantra_text}\n"
            f"- 英文箴言：{eng_motto}\n"
            f"- 当下功课：{action_title}\n"
            f"- 契合觉察牌：{matched_zen_card.get('card_id', 'WUTANG-CARD-01')} {matched_zen_card.get('name', '静观')}\n"
            f"- 契合之由：{matched_zen_card.get('match_reason', '以此水墨画卷映照当下心象。')}\n"
        )

        # 模拟打字机流式输出 (按段/标点自然节奏分割)
        pieces = re.split(r"(?<=[，。！？\n])", full_text)
        for piece in pieces:
            if piece:
                yield f"data: {json.dumps({'type': 'token', 'content': piece}, ensure_ascii=False)}\n\n"
                await asyncio.sleep(0.035)  # 35ms 平滑打字延迟

        # 发送卡牌元数据签名包
        sig_data = {
            "card_name": card_name,
            "aphorism": mantra_text,
            "english_mantra": eng_motto,
            "action_title": action_title,
            "action_steps": action_steps,
            "classic_source": f"《{book}·{chapter}》（{author}）",
            "quote": quote,
            "interpretation": interpretation,
            "school": school_key,
            "master": persona["master_name"],
            "user_nickname": user_nickname,
            "matched_zen_card": matched_zen_card
        }
        yield f"data: {json.dumps({'type': 'card_signature', 'data': sig_data}, ensure_ascii=False)}\n\n"
        yield f"data: {json.dumps({'type': 'done'}, ensure_ascii=False)}\n\n"

    def _extract_or_synthesize_signature(
        self,
        full_text: str,
        matched_cards: Dict[str, Any],
        retrieved_classics: List[Dict[str, Any]],
        track: Optional[str],
        master: Optional[str],
        user_nickname: Optional[str],
        pre_matched_zen_card: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """从生成文本中提取或合成卡牌签名元数据"""
        school_key = get_school_key(track)
        persona = MASTER_PERSONAS.get(school_key, MASTER_PERSONAS["confucianism"])

        wisdom = matched_cards.get("wisdom") or {}
        ws = wisdom.get("classic_source") or {}
        action = matched_cards.get("action") or {}

        card_name = wisdom.get("name") or "克己"
        aphorism = "君子求诸己，立志而笃行。"
        english_mantra = "Self-restraint leads to peace."
        action_title = action.get("title", "静坐调息，记录眼前可控之事")

        # 正则尝试从文本末尾提取
        name_match = re.search(r"-\s*卡名[：:]\s*([^\n\r]+)", full_text)
        if name_match:
            card_name = name_match.group(1).strip()[:4]

        aph_match = re.search(r"-\s*定心偈[：:]\s*([^\n\r]+)", full_text)
        if aph_match:
            aphorism = aph_match.group(1).strip()

        eng_match = re.search(r"-\s*英文箴言[：:]\s*([^\n\r]+)", full_text)
        if eng_match:
            english_mantra = eng_match.group(1).strip()

        act_match = re.search(r"-\s*当下功课[：:]\s*([^\n\r]+)", full_text)
        if act_match:
            action_title = act_match.group(1).strip()

        quote = ws.get("quote") or wisdom.get("original_text", "知止而后有定")
        book = ws.get("book") or wisdom.get("source_title", "大学")
        chapter = ws.get("chapter") or wisdom.get("source_section", "经一章")
        author = ws.get("author", persona["master_name"])
        interpretation = ws.get("translation") or wisdom.get("modern_interpretation", "知止定静安虑得。")

        # 匹配 96 张东方智慧常道画廊中最契合的心象牌 (优先锁定预匹配结果，保证前后绝对一致)
        if pre_matched_zen_card and pre_matched_zen_card.get("card_id"):
            matched_zen_card = dict(pre_matched_zen_card)
        else:
            specified_card_id = None
            card_id_match = re.search(r"-\s*契合觉察牌[：:]\s*(WUTANG-CARD-\d+|\d+)", full_text)
            if card_id_match:
                specified_card_id = card_id_match.group(1).strip()
                if not specified_card_id.startswith("WUTANG-CARD-") and specified_card_id.isdigit():
                    specified_card_id = f"WUTANG-CARD-{int(specified_card_id):02d}"

            matched_zen_card = rag_service.match_zen96_card(
                user_text=full_text[:300],
                track=track,
                card_name=card_name,
                specified_card_id=specified_card_id
            )

        reason_match = re.search(r"-\s*契合之由[：:]\s*([^\n\r]+)", full_text)
        if reason_match and matched_zen_card:
            matched_zen_card["match_reason"] = reason_match.group(1).strip()

        return {
            "card_name": card_name,
            "aphorism": aphorism,
            "english_mantra": english_mantra,
            "action_title": action_title,
            "action_steps": action.get("steps") or ["闭目静坐呼吸", "记录可控之事", "安然安歇"],
            "classic_source": f"《{book}·{chapter}》（{author}）",
            "quote": quote,
            "interpretation": interpretation,
            "school": school_key,
            "master": persona["master_name"],
            "user_nickname": user_nickname or "同修",
            "matched_zen_card": matched_zen_card
        }

    def parse_markdown_four_step(self, text: str) -> Dict[str, Any]:
        """将生成的 Markdown 解忧文本解析为标准结构化字典（支持 3.0 与 4.0 标题）"""
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
            if not line_str:
                continue

            if line_str.startswith("---") or "【解脱卡印】" in line_str:
                current_sec = None
                continue

            # 仅当行为标题行时（以 #、*、数字标号或【 开头）才判定为小节切换
            is_heading_line = (
                line_str.startswith("#") or
                line_str.startswith("【") or
                line_str.startswith("**【") or
                bool(re.match(r"^0[1-4]\b", line_str))
            )

            if is_heading_line:
                if any(k in line_str for k in ["01", "听见了", "闻心", "洞幽"]):
                    current_sec = "empathy"
                    continue
                elif any(k in line_str for k in ["02", "古人有云", "示道", "真诠"]):
                    current_sec = "wisdom"
                    continue
                elif any(k in line_str for k in ["03", "试试这一招", "笃行", "当下功课", "功课", "微行动"]):
                    current_sec = "micro_action"
                    continue
                elif any(k in line_str for k in ["04", "读这一段", "法印", "定心偈", "定心"]):
                    current_sec = "further_reading"
                    continue

            if current_sec:
                parts[current_sec] += (line + "\n")

        for k in parts:
            if isinstance(parts[k], str):
                parts[k] = parts[k].strip()

        return parts

    async def organize_journal(self, raw_text: str) -> Dict[str, Any]:
        """
        AI 心事日记结构化提炼 (F-12)
        提炼：事件客观事实、脑海想法、情绪体验、可能需要、下一步选择
        """
        system_prompt = (
            "你是「悟堂·东方解忧处」的心事日记整理助手。\n"
            "用户写下了一段零散的日常心绪或经历，请帮他温和、清晰地整理成结构化要素。\n"
            "文风原则：温和平视、不指责、不说教、不贴病理标签。\n"
            "必须输出纯 JSON 对象，格式如下：\n"
            "{\n"
            '  "event_summary": "客观发生的事情摘要（30-60字）",\n'
            '  "thoughts": "当事人当时脑海里冒出的想法与评判",\n'
            '  "feelings": ["情绪词1", "情绪词2", "情绪词3"],\n'
            '  "possible_needs": ["深层需要1", "深层需要2"],\n'
            '  "next_step": "一个今晚可以尝试的 5 分钟微小行动"\n'
            "}"
        )
        if settings.is_llm_configured:
            try:
                resp = await self._get_client().chat.completions.create(
                    model=settings.LLM_MODEL,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": raw_text},
                    ],
                    temperature=0.3,
                    response_format={"type": "json_object"}
                )
                content = resp.choices[0].message.content
                data = json.loads(content)
                # 兼容可能字段名
                if "underlying_needs" in data and "possible_needs" not in data:
                    data["possible_needs"] = data["underlying_needs"]
                if "micro_action" in data and "next_step" not in data:
                    data["next_step"] = data["micro_action"]
                return data
            except Exception as e:
                print(f"[!] 真实 LLM 调用异常，启用降级日记整理: {e}")

        # 降级提炼
        return {
            "event_summary": raw_text[:50] + ("..." if len(raw_text) > 50 else ""),
            "thoughts": "觉得自己没做好，担心别人对自己的看法",
            "feelings": ["紧张", "自责", "不安"],
            "possible_needs": ["被接纳", "确定感", "安全边界"],
            "next_step": "今晚睡前将写好的字条合上，做3次深呼吸，告诉自己今天已经尽力了。"
        }

    async def practice_dialogue(
        self,
        scenario_title: str,
        ai_role: str,
        user_draft: str,
        history: List[Dict[str, str]]
    ) -> Dict[str, Any]:
        """情境练习室对话演练与 4 维微反馈 (F-15)"""
        system_prompt = (
            f"你是「悟堂·情境练习室」的对话陪练伙伴。\n"
            f"当前场景：{scenario_title}，你扮演：{ai_role}。\n"
            f"你需要：\n"
            f"1. 扮演该角色，根据用户的回复进行真实、生活化的下一轮对话回复 role_reply（40-80字）。\n"
            f"2. 对用户刚才的回复进行 4 维微反馈 feedback：boundary(边界)、tone(语气)、recommendation(建议)。\n"
            f"3. 给出 2 组更推荐的替代表达范式 alternatives。\n"
            f"必须输出纯 JSON 对象，格式如下：\n"
            "{\n"
            '  "role_reply": "角色回复内容",\n'
            '  "feedback": {\n'
            '    "boundary": "清晰/略微妥协/边界过硬",\n'
            '    "tone": "平和/略显生硬/过度自责",\n'
            '    "recommendation": "具体建议"\n'
            '  },\n'
            '  "alternatives": ["更温和坚定的替代表达1", "替代表达2"]\n'
            "}"
        )
        messages = [{"role": "system", "content": system_prompt}]
        for h in history:
            messages.append({"role": h.get("role", "user"), "content": h.get("content", "")})
        messages.append({"role": "user", "content": user_draft})

        if settings.is_llm_configured:
            try:
                resp = await self._get_client().chat.completions.create(
                    model=settings.LLM_MODEL,
                    messages=messages,
                    temperature=0.5,
                    response_format={"type": "json_object"}
                )
                data = json.loads(resp.choices[0].message.content)
                if "partner_reply" in data and "role_reply" not in data:
                    data["role_reply"] = data["partner_reply"]
                if "alternative_expressions" in data and "alternatives" not in data:
                    data["alternatives"] = data["alternative_expressions"]
                return data
            except Exception as e:
                print(f"[!] 真实 LLM 情境练习异常，启用降级: {e}")

        # 降级模拟
        return {
            "role_reply": "别呀，就帮我看十分钟，领导催得紧。你那两个模块晚上再弄呗，我先发给你？",
            "feedback": {
                "boundary": "清晰且守住底线",
                "tone": "温和坚定",
                "recommendation": "表达了实际困难的同时没有攻击对方，维持了良好的职场边界。"
            },
            "alternatives": [
                "手头任务今天确实走不开。如果特别紧急，建议先同步下组长协调其他人？",
                "我明白这事急，但今天真的无法分心。明天上午十点后我可以抽15分钟帮你看下。"
            ]
        }

    async def build_referral_summary(
        self,
        main_complaint: str,
        duration: str,
        assessment_score: Optional[int],
        target_specialist: str
    ) -> Dict[str, Any]:
        """授权专业转介沟通摘要生成 (F-17)"""
        system_prompt = (
            "你是「悟堂·心境健康中心」的专业转介沟通清单整理助手。\n"
            "请将用户近期填写的心理自评、心境记录要点与困扰描述，整理成一份适合带给执业心理咨询师或精神科医生的【首次面询沟通清单】。\n"
            "原则：客观陈述、不作医疗诊断、不贴标签、结构清晰、保护隐私。\n"
            "必须输出纯 JSON 对象，格式如下：\n"
            "{\n"
            '  "summary_title": "首次心理健康面询沟通清单",\n'
            '  "main_complaint": "主诉困扰简述（客观现象，不作诊断）",\n'
            '  "key_symptoms": ["主要症状表现1", "表现2"],\n'
            '  "recent_stressors": ["诱发与加重因素1", "因素2"],\n'
            '  "self_help_attempts": ["曾经尝试过的缓解方式"],\n'
            '  "questions_for_specialist": ["希望在面询中向专业人员确认的问题1", "问题2"],\n'
            '  "questions_for_professional": ["希望在面询中向专业人员确认的问题1", "问题2"]\n'
            "}"
        )
        payload = {
            "main_complaint": main_complaint,
            "duration": duration,
            "assessment_score": assessment_score,
            "target_specialist": target_specialist
        }
        if settings.is_llm_configured:
            try:
                resp = await self._get_client().chat.completions.create(
                    model=settings.LLM_MODEL,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": json.dumps(payload, ensure_ascii=False)},
                    ],
                    temperature=0.2,
                    response_format={"type": "json_object"}
                )
                data = json.loads(resp.choices[0].message.content)
                if "summary_title" not in data:
                    data["summary_title"] = "首次心理健康面询个人沟通清单"
                if "key_symptoms" not in data:
                    data["key_symptoms"] = data.get("recent_stressors", ["工作压力过载", "睡眠延迟"])
                if "questions_for_specialist" not in data:
                    data["questions_for_specialist"] = data.get("questions_for_professional", ["如何建立稳固心理边界？"])
                return data
            except Exception as e:
                print(f"[!] 转介清单生成异常: {e}")

        return {
            "summary_title": "首次心理健康面询个人沟通清单",
            "main_complaint": main_complaint or "近两周因工作压力与人际沟通感到较明显的心绪紧绷，偶有睡眠延迟与自我苛责。",
            "key_symptoms": ["工作压力过载", "入睡困难与情绪反刍", "自我苛责"],
            "recent_stressors": ["职场责任与多线程任务堆积", "不善于拒绝他人请求导致时间被侵占"],
            "self_help_attempts": ["尝试过记录情绪日记", "尝试过5分钟呼吸放松与减少深夜手机浏览"],
            "questions_for_specialist": [
                "在面对不合理要求时，如何建立更稳固的心理边界？",
                "目前的知觉压力状态，是否需要进一步安排系统的心理咨询？"
            ],
            "questions_for_professional": [
                "在面对不合理要求时，如何建立更稳固的心理边界？",
                "目前的知觉压力状态，是否需要进一步安排系统的心理咨询？"
            ]
        }

llm_service = LLMService()
