from flask import Flask, jsonify, request
from flask_cors import CORS
import json
import os

# 导入双Agent
from agents.logic_agent import analyze_logic
from agents.reply_agent import generate_reply
from agents.personality_agent import analyze_personality

app = Flask(__name__)
CORS(app)

# 加载谜题数据
with open(os.path.join(os.path.dirname(__file__), 'data', 'puzzles.json'), 'r', encoding='utf-8') as f:
    PUZZLES_DATA = json.load(f)

@app.route('/api/topics', methods=['GET'])
def get_topics():
    """获取所有主题"""
    return jsonify(PUZZLES_DATA['topics'])

@app.route('/api/puzzles/<topic_id>', methods=['GET'])
def get_puzzles_by_topic(topic_id):
    """获取某主题下的谜题列表"""
    puzzles = [p for p in PUZZLES_DATA['puzzles'] if p['topic_id'] == topic_id]
    # 不返回汤底
    result = [{
        'id': p['id'],
        'title': p['title'],
        'soup_face': p['soup_face'],
        'difficulty': p['difficulty']
    } for p in puzzles]
    return jsonify(result)

@app.route('/api/puzzle/<puzzle_id>', methods=['GET'])
def get_puzzle(puzzle_id):
    """获取单个谜题详情（不含汤底）"""
    puzzle = next((p for p in PUZZLES_DATA['puzzles'] if p['id'] == puzzle_id), None)
    if not puzzle:
        return jsonify({'error': '谜题不存在'}), 404
    return jsonify({
        'id': puzzle['id'],
        'title': puzzle['title'],
        'soup_face': puzzle['soup_face'],
        'difficulty': puzzle['difficulty'],
        'hint_limit': puzzle['hint_limit']
    })

@app.route('/api/chat', methods=['POST'])
def chat():
    """对话接口 - 双Agent协同"""
    data = request.json
    puzzle_id = data.get('puzzle_id')
    user_question = data.get('question')
    history = data.get('history', [])

    puzzle = next((p for p in PUZZLES_DATA['puzzles'] if p['id'] == puzzle_id), None)
    if not puzzle:
        return jsonify({'error': '谜题不存在'}), 404

    # Agent 1: 逻辑判断（阿里云API）
    logic_result = analyze_logic(
        soup_bottom=puzzle['soup_bottom'],
        question=user_question,
        history=history
    )

    # 如果已经揭晓，直接返回汤底，跳过 Agent 2
    is_revealed = logic_result['judgement'] == '揭晓'

    if is_revealed:
        return jsonify({
            'judgement': '揭晓',
            'reply': f"🎉 真相揭晓：{puzzle['soup_bottom']}",
            'is_revealed': True,
            'soup_bottom': puzzle['soup_bottom']
        })

    # Agent 2: 回复生成（本地微调模型）
    reply_result = generate_reply(
        judgement=logic_result['judgement'],
        hint_level=logic_result['hint_level'],
        question=user_question,
        soup_face=puzzle['soup_face'],
        soup_bottom=puzzle['soup_bottom'],
        history=history
    )

    # 调试输出
    print(f"\n===== Agent 协作结果 =====")
    print(f"Agent 1 判断: {logic_result['judgement']}")
    print(f"Agent 2 回复: {reply_result}")
    print(f"最终返回的reply: {reply_result.get('reply', '请继续提问。')}")
    print("=" * 40 + "\n")

    # 使用 Agent 1 的判断 + Agent 2 的回复风格
    is_revealed = logic_result['judgement'] == '揭晓'

    return jsonify({
        'judgement': logic_result['judgement'],
        'reply': reply_result.get('reply', '请继续提问。'),
        'is_revealed': is_revealed,
        'soup_bottom': puzzle['soup_bottom'] if is_revealed else None  # 揭晓时返回汤底
    })

@app.route('/api/hint/<puzzle_id>', methods=['GET'])
def get_hint(puzzle_id):
    """获取提示"""
    puzzle = next((p for p in PUZZLES_DATA['puzzles'] if p['id'] == puzzle_id), None)
    if not puzzle:
        return jsonify({'error': '谜题不存在'}), 404

    # 获取提示索引（从请求参数读取）
    hint_index = int(request.args.get('index', 0))
    hints = puzzle.get('tips', [])

    # 返回对应索引的提示
    if hint_index < len(hints):
        return jsonify({'hint': hints[hint_index], 'total': len(hints)})
    else:
        return jsonify({'hint': '已用完所有提示', 'total': len(hints)})

@app.route('/api/reveal/<puzzle_id>', methods=['GET'])
def reveal_answer(puzzle_id):
    """揭示答案"""
    puzzle = next((p for p in PUZZLES_DATA['puzzles'] if p['id'] == puzzle_id), None)
    if not puzzle:
        return jsonify({'error': '谜题不存在'}), 404

    return jsonify({
        'soup_bottom': puzzle['soup_bottom'],
        'title': puzzle['title']
    })

@app.route('/api/personality', methods=['POST'])
def get_personality():
    """分析推理人格"""
    data = request.json
    puzzle_id = data.get('puzzle_id')
    history = data.get('history', [])

    puzzle = next((p for p in PUZZLES_DATA['puzzles'] if p['id'] == puzzle_id), None)
    if not puzzle:
        return jsonify({'error': '谜题不存在'}), 404

    result = analyze_personality(history, puzzle['soup_bottom'])
    return jsonify(result)

if __name__ == '__main__':
    app.run(debug=True, port=5001)