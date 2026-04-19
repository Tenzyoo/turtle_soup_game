"""
推理人格分析器
根据用户对话历史分析推理风格和探索风格
"""
import json
import os
import re
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import ANTHROPIC_API_KEY, ANTHROPIC_BASE_URL, LOGIC_MODEL
from anthropic import Anthropic

# 加载人格定义
PERSONALITY_FILE = os.path.join(os.path.dirname(__file__), '../personal.json')
with open(PERSONALITY_FILE, 'r', encoding='utf-8') as f:
    PERSONALITY_DATA = json.load(f)

PROFILES = PERSONALITY_DATA['turtle_soup_personality_system']['personality_profiles']
DIMENSIONS = PERSONALITY_DATA['turtle_soup_personality_system']['dimension_definitions']

client = None

def init_client():
    """初始化API客户端"""
    global client
    api_key = os.environ.get("ANTHROPIC_API_KEY", ANTHROPIC_API_KEY)
    base_url = os.environ.get("ANTHROPIC_BASE_URL", ANTHROPIC_BASE_URL)
    client = Anthropic(api_key=api_key, base_url=base_url)

def analyze_personality(history: list, soup_bottom: str) -> dict:
    """
    分析用户推理人格

    Args:
        history: 用户对话历史
        soup_bottom: 汤底真相

    Returns:
        {
            "personality_id": "lawful_cautious",
            "name": "地毯式搜查官",
            "description": "...",
            "evaluation": "...",
            "tags": [...],
            "inference_score": 1,  # 1=逻辑, 2=中立, 3=混乱
            "exploration_score": 1,  # 1=谨慎, 2=中立, 3=突击
            "reason": "分析理由"
        }
    """
    if client is None:
        init_client()

    # 提取用户问题
    questions = [h.get('question', '') for h in history if h.get('question')]
    if not questions:
        # 默认返回均衡游侠
        return get_profile("neutral_neutral", "无足够对话数据，默认显示")

    prompt = f"""你是推理人格分析师，根据用户的提问风格判断其推理人格。

【汤底真相】
{soup_bottom}

【用户提问记录】（共{len(questions)}条）
{chr(10).join([f'{i+1}. {q}' for i, q in enumerate(questions)])}

【分析维度】
1. 推理风格（inference_style）：
   - 逻辑(lawful, score=1)：提问基于已确认事实，因果链条紧密，关键词：既然、那么、如果...是否意味着
   - 中立(neutral, score=2)：提问合理，偶尔跳跃
   - 混乱(chaotic, score=3)：提问跳跃，关注点多变无序

2. 探索风格（exploration_style）：
   - 谨慎(cautious, score=1)：只确认基础事实（环境、性别、物品）
   - 中立(neutral, score=2)：适度提出假设，线索关联
   - 突击(aggressive, score=3)：直接抛出复合型假说、真相断言

【分析要点】
- 统计用户提问的类型分布（基础确认 vs 假设验证 vs 直接猜测）
- 分析提问的逻辑连贯性
- 判断风险偏好（保守试探 vs 大胆突击）

直接输出JSON：
{{"inference_style": "lawful|neutral|chaotic", "inference_score": 1|2|3, "exploration_style": "cautious|neutral|aggressive", "exploration_score": 1|2|3, "reason": "简要分析理由（50字内）"}}"""

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

        # 解析 JSON
        if "{" in content and "}" in content:
            json_str = content[content.find("{"):content.rfind("}")+1]
            result = json.loads(json_str)

            # 组合人格ID
            personality_id = f"{result['inference_style']}_{result['exploration_style']}"
            return get_profile(personality_id, result.get('reason', ''))

    except Exception as e:
        print(f"性格分析API错误: {e}")

    # 降级：简单规则判断
    return simple_analysis(questions, soup_bottom)

def get_profile(personality_id: str, reason: str) -> dict:
    """获取人格详情"""
    profile = next((p for p in PROFILES if p['id'] == personality_id), PROFILES[4])  # 默认均衡游侠

    # 解析ID获取分数
    parts = personality_id.split('_')
    inference_map = {'lawful': 1, 'neutral': 2, 'chaotic': 3}
    exploration_map = {'cautious': 1, 'neutral': 2, 'aggressive': 3}

    return {
        "personality_id": profile['id'],
        "name": profile['name'],
        "description": profile['description'],
        "evaluation": profile['evaluation'],
        "tags": profile['tags'],
        "inference_style": parts[0],
        "inference_score": inference_map.get(parts[0], 2),
        "exploration_style": parts[1],
        "exploration_score": exploration_map.get(parts[1], 2),
        "reason": reason
    }

def simple_analysis(questions: list, soup_bottom: str) -> dict:
    """简单规则分析（降级方案）"""
    # 关键词统计
    logical_keywords = ['既然', '那么', '由于', '如果', '是否意味着', '所以']
    cautious_keywords = ['是', '否', '有没有', '是不是', '性别', '环境', '时间', '地点']
    aggressive_keywords = ['是...吗', '真相是', '我觉得', '应该是', '肯定', '一定']

    logical_count = sum(1 for q in questions if any(kw in q for kw in logical_keywords))
    aggressive_count = sum(1 for q in questions if any(kw in q for kw in aggressive_keywords))

    # 判断推理风格
    if logical_count >= len(questions) * 0.3:
        inference_style = 'lawful'
        inference_score = 1
    elif any('跳跃' in q or '乱' in q for q in questions):
        inference_style = 'chaotic'
        inference_score = 3
    else:
        inference_style = 'neutral'
        inference_score = 2

    # 判断探索风格
    if aggressive_count >= len(questions) * 0.4:
        exploration_style = 'aggressive'
        exploration_score = 3
    elif len(questions) > 10 and aggressive_count == 0:
        exploration_style = 'cautious'
        exploration_score = 1
    else:
        exploration_style = 'neutral'
        exploration_score = 2

    personality_id = f"{inference_style}_{exploration_style}"
    return get_profile(personality_id, "基于提问关键词统计分析")