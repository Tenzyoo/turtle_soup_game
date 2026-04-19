"""
Agent 1: 逻辑分析师
使用阿里云Qwen API判断玩家问题是否接近真相
"""
import os
import json
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import ANTHROPIC_API_KEY, ANTHROPIC_BASE_URL, LOGIC_MODEL
from anthropic import Anthropic

client = None

def init_client():
    """初始化API客户端"""
    global client
    api_key = os.environ.get("ANTHROPIC_API_KEY", ANTHROPIC_API_KEY)
    base_url = os.environ.get("ANTHROPIC_BASE_URL", ANTHROPIC_BASE_URL)
    client = Anthropic(api_key=api_key, base_url=base_url)

def analyze_logic(soup_bottom: str, question: str, history: list) -> dict:
    """分析玩家问题"""
    if client is None:
        init_client()

    prompt = f"""你是海龟汤游戏的逻辑分析师。

【汤底真相】
{soup_bottom}

【判断规则】（优先级从高到低）
1. "揭晓"：玩家已经说出核心真相（如直接确认关键身份/事件），游戏结束
2. "是"：问题方向正确，触及关键点，在正确追问
3. "接近了"：触及真相边缘，离真相很近
4. "否"：方向错误，与真相无关
5. "不相关"：完全无关

【示例】
汤底"小王是机器人，充电5分钟"
- 问"小王是机器人吗？" → 揭晓（直接确认核心真相）
- 问"小王不吃饭？" → 是（正确方向）
- 问"小王有什么异常？" → 接近了

【历史对话】
{format_history(history)}

【当前问题】
{question}

直接输出JSON：
{{"judgement": "是|否|接近了|不相关|揭晓", "reason": "理由", "hint_level": 0-3}}"""

    try:
        response = client.messages.create(
            model=LOGIC_MODEL,
            max_tokens=200,
            messages=[{"role": "user", "content": prompt}]
        )

        # 提取文本
        content = ""
        for block in response.content:
            if hasattr(block, 'text'):
                content += block.text

        # 从响应中提取 JSON
        if '{"judgement"' in str(response.content):
            raw = str(response.content)
            start = raw.rfind('{"judgement"')
            end = raw.rfind('}') + 1
            if start >= 0 and end > start:
                content = raw[start:end]

        print(f"Agent 1 API响应: {content}")

        # 解析 JSON
        if "{" in content and "}" in content:
            json_str = content[content.find("{"):content.rfind("}")+1]
            result = json.loads(json_str)
            result["hint_level"] = int(result.get("hint_level", 0))
            return result

    except Exception as e:
        print(f"Agent 1 API错误: {e}，使用 Mock")

    # Mock 降级：检查是否猜出核心真相
    soup_keywords = extract_keywords(soup_bottom)
    question_lower = question.lower()

    # 如果问题包含核心关键词，判断为揭晓
    hit_count = sum(1 for kw in soup_keywords if kw in question_lower)
    if hit_count >= 2:
        return {"judgement": "揭晓", "reason": "触及核心真相", "hint_level": 3}
    elif hit_count == 1:
        # 检查是否是确认性问题（"是...吗？"格式）
        if "吗" in question and any(kw in question for kw in soup_keywords[:3]):
            return {"judgement": "揭晓", "reason": "确认核心真相", "hint_level": 3}
        return {"judgement": "接近了", "reason": "触及关键概念", "hint_level": 2}
    elif is_related(question, soup_bottom):
        return {"judgement": "是", "reason": "方向正确", "hint_level": 1}
    else:
        return {"judgement": "否", "reason": "方向错误", "hint_level": 0}

def extract_keywords(soup_bottom: str) -> list:
    """从汤底提取核心关键词"""
    # 常见海龟汤核心概念
    common_keywords = [
        "机器人", "充电", "假账", "辞职", "良心", "奖金",
        "海龟汤", "荒岛", "父亲", "肉", "自杀",
        "出轨", "调钟", "欺骗", "真相", "死亡"
    ]
    found = [kw for kw in common_keywords if kw in soup_bottom]
    return found

def is_related(question: str, soup_bottom: str) -> bool:
    """判断问题是否相关"""
    related_words = [
        "自杀", "死亡", "杀", "汤", "味道", "窗", "钟",
        "加班", "辞职", "奖金", "机器人", "充电", "吃饭",
        "休息", "为什么", "怎么", "什么"
    ]
    return any(w in question for w in related_words)

def format_history(history: list) -> str:
    """格式化历史对话"""
    if not history:
        return "（无历史）"
    lines = []
    for h in history[-6:]:
        if h.get("question"):
            lines.append(f"玩家: {h['question']}")
        if h.get("response"):
            resp = h["response"] if isinstance(h["response"], dict) else {"reply": str(h["response"])}
            lines.append(f"主持人: {resp.get('reply', '')}")
    return "\n".join(lines)