#!/usr/bin/env python3
"""
训练数据格式转换脚本
- 可读格式 → 紧凑JSONL（训练用）
- 紧凑JSONL → 可读格式（编辑用）
"""

import json
import sys

def to_jsonl(input_file, output_file):
    """可读JSON数组 → 紧凑JSONL"""
    with open(input_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    with open(output_file, 'w', encoding='utf-8') as f:
        for item in data:
            # 紧凑格式，无缩进
            line = json.dumps(item, ensure_ascii=False, separators=(',', ': '))
            f.write(line + '\n')

    print(f"转换完成: {len(data)} 条数据写入 {output_file}")

def to_readable(input_file, output_file):
    """紧凑JSONL → 可读JSON数组"""
    data = []
    with open(input_file, 'r', encoding='utf-8') as f:
        for line in f:
            if line.strip():
                data.append(json.loads(line))

    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"转换完成: {len(data)} 条数据写入 {output_file}")

def validate(input_file):
    """验证数据格式"""
    errors = []
    valid_judgements = {"是", "否", "接近了", "不相关", "待定"}

    with open(input_file, 'r', encoding='utf-8') as f:
        for i, line in enumerate(f, 1):
            if not line.strip():
                continue
            try:
                item = json.loads(line)
                for msg in item.get("messages", []):
                    if msg["role"] == "assistant":
                        content = json.loads(msg["content"])
                        # 检查字段
                        if set(content.keys()) != {"judgement", "reply"}:
                            errors.append(f"行{i}: 字段错误 {content.keys()}")
                        # 检查枚举值
                        if content["judgement"] not in valid_judgements:
                            errors.append(f"行{i}: 枚举值错误 '{content['judgement']}'")
                        # 检查回复长度
                        if len(content["reply"]) > 50:
                            errors.append(f"行{i}: 回复过长 ({len(content['reply'])}字)")
            except json.JSONDecodeError as e:
                errors.append(f"行{i}: JSON解析错误 {e}")

    if errors:
        print("发现错误:")
        for err in errors:
            print(f"  - {err}")
    else:
        print("✅ 数据格式正确")

def to_llama_factory(input_file, output_file):
    """OpenAI messages格式 → LLaMA-Factory ShareGPT格式"""
    with open(input_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    converted = []
    for item in data:
        conversations = []
        for msg in item.get("messages", []):
            # 转换role到from
            role_map = {
                "system": "system",
                "user": "human",
                "assistant": "gpt"
            }
            from_role = role_map.get(msg["role"], msg["role"])
            conversations.append({
                "from": from_role,
                "value": msg["content"]
            })
        converted.append({"conversations": conversations})

    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(converted, f, ensure_ascii=False, indent=2)

    print(f"转换完成: {len(converted)} 条数据写入 {output_file}")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("用法:")
        print("  转为训练格式:   python convert_data.py to_jsonl train_data_readable.json train_data.jsonl")
        print("  转为编辑格式:   python convert_data.py to_readable train_data.jsonl train_data_readable.json")
        print("  转为LLaMA格式:  python convert_data.py to_llama_factory train_data_readable.json train_data_llama_factory.json")
        print("  验证数据:       python convert_data.py validate train_data.jsonl")
        sys.exit(1)

    cmd = sys.argv[1]
    if cmd == "to_jsonl":
        to_jsonl(sys.argv[2], sys.argv[3])
    elif cmd == "to_readable":
        to_readable(sys.argv[2], sys.argv[3])
    elif cmd == "to_llama_factory":
        to_llama_factory(sys.argv[2], sys.argv[3])
    elif cmd == "validate":
        validate(sys.argv[2])
    else:
        print(f"未知命令: {cmd}")