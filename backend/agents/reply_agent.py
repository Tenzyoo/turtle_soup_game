"""
Agent 2: 回复师
使用本地微调模型生成回复
"""
import os
import sys
import json
import re
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../'))
from turtle_soup_model import TurtleSoupModel

MODEL_PATH = os.path.join(os.path.dirname(__file__), '../../turtle_soup_merged_1')
_model = None

def get_model():
    """懒加载模型"""
    global _model
    if _model is None:
        print("加载本地模型...")
        _model = TurtleSoupModel(MODEL_PATH)
        print("本地模型加载完成!")
    return _model

def generate_reply(
    judgement: str,
    hint_level: int,
    question: str,
    soup_face: str,
    soup_bottom: str,
    history: list
) -> dict:
    """
    使用微调模型生成回复（基于 Agent 1 的判断）

    Returns:
        {"reply": "..."}  # 只返回回复，不返回判断
    """
    model = get_model()

    # 构建系统提示，明确要求不输出判断词
    system_prompt = f"""你是海龟汤游戏主持人，负责生成简短引导回复。

【当前谜题】
【汤面】{soup_face}
【汤底】{soup_bottom}

【判断结果】
玩家问题判断为：{judgement}

【回复要求】
根据判断生成一句引导回复（15-30字）：
- "是"：鼓励继续追问（如：方向正确，继续深入）
- "否"：提示换个方向（如：不是这个方向，换个思路）
- "接近了"：暗示快接近真相（如：快接近真相了）
- "不相关"：说明无关（如：这个问题和真相无关）

【重要规则】
1. 不要输出判断词（是/否/接近了等），直接输出回复内容
2. 不要输出 JSON 格式
3. 只输出一句简短回复文本"""

    # 转换历史格式
    formatted_history = []
    for h in history[-6:]:
        if h.get("question"):
            formatted_history.append({"role": "user", "content": h["question"]})
        if h.get("response"):
            resp = h["response"] if isinstance(h["response"], dict) else {"reply": str(h["response"])}
            formatted_history.append({"role": "assistant", "content": resp.get("reply", "")})

    try:
        # 让模型输出回复文本
        result = model.chat(question, system_prompt, formatted_history)
        # 提取 reply
        reply_text = result.get("reply", "请继续提问") if isinstance(result, dict) else str(result)

        # 清理 thinking block（简化处理）
        thinking_markers = ['IMO_OPTIONS', 'ImplOptions', '〇〇〇', '<|begin_of_think|>', '']

        for marker in thinking_markers:
            if marker and marker in reply_text:
                idx = reply_text.find(marker)
                reply_text = reply_text[idx + len(marker):]
                break

        reply_text = reply_text.strip()
        chinese_match = re.search(r'[\u4e00-\u9fff]', reply_text)
        if chinese_match:
            reply_text = reply_text[chinese_match.start():]

        # 清理判断词前缀（"是 - "、"否 - " 等）
        prefixes = ["是 - ", "否 - ", "接近了 - ", "不相关 - ", "是。", "否。", "接近了。", "不相关。", "是 ", "否 "]
        for prefix in prefixes:
            if reply_text.startswith(prefix):
                reply_text = reply_text[len(prefix):].strip()

        # 清理空白和截断
        reply_text = reply_text.strip()
        if '\n' in reply_text:
            reply_text = reply_text.split('\n')[0].strip()
        if len(reply_text) > 50:
            reply_text = reply_text[:50]

        return {"reply": reply_text if reply_text else "请继续提问"}
    except Exception as e:
        print(f"模型推理失败: {e}")
        return generate_reply_mock(judgement, hint_level)

def generate_reply_mock(judgement: str, hint_level: int) -> dict:
    """Mock 回复（只返回回复文本）"""
    replies = {
        "是": "方向正确，继续深入。",
        "否": "不是这个方向，换个思路。",
        "接近了": "快接近真相了！",
        "不相关": "这个问题和真相无关。",
    }
    return {"reply": replies.get(judgement, "请继续提问。")}