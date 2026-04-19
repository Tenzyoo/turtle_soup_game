"""
海龟汤微调模型调用封装
"""
import json
import re
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer


class TurtleSoupModel:
    def __init__(self, model_path: str):
        self.tokenizer = AutoTokenizer.from_pretrained(model_path)
        self.model = AutoModelForCausalLM.from_pretrained(
            model_path,
            torch_dtype=torch.bfloat16,
            device_map='auto',
        )

    def chat(self, question: str, system_prompt: str, history: list = None) -> dict:
        """
        Args:
            question: 玩家当前问题
            system_prompt: 包含汤面+汤底的系统提示
            history: 历史对话列表

        Returns:
            dict: {"reply": "..."} 或 {"judgement": "...", "reply": "..."}
        """
        messages = [{"role": "system", "content": system_prompt}]
        if history:
            messages.extend(history)
        messages.append({"role": "user", "content": question})

        text = self.tokenizer.apply_chat_template(
            messages, tokenize=False, add_generation_prompt=True, thinking=False
        )
        inputs = self.tokenizer(text, return_tensors='pt').to(self.model.device)

        with torch.no_grad():
            outputs = self.model.generate(
                **inputs,
                max_new_tokens=128,
                do_sample=True,
                temperature=0.7,
                top_p=0.9,
                pad_token_id=self.tokenizer.eos_token_id
            )

        raw = self.tokenizer.decode(outputs[0], skip_special_tokens=True)

        print(f"\n========== 本地模型完整原始输出 ==========")
        print(raw)
        print("=" * 40)

        # 步骤1: 提取 assistant 最后的回复
        if 'assistant' in raw.lower():
            parts = raw.split('assistant')
            last_part = parts[-1].strip()
            if 'user' in last_part.lower():
                last_part = last_part.split('user')[0].strip()
            raw = last_part

        print(f"步骤1-assistant后: {repr(raw)}")

        # 步骤2: 清理特殊标记
        raw = raw.replace('<|im_end|>', '').replace('<|im_start|>', '').strip()

        # 步骤3: 跳过 thinking block（简化处理）
        thinking_markers = ['IMO_OPTIONS', 'ImplOptions', '〇〇〇', '<|begin_of_think|>', '']

        for marker in thinking_markers:
            if marker and marker in raw:
                idx = raw.find(marker)
                raw = raw[idx + len(marker):]
                break

        # 步骤4: 找第一个中文字符开始的内容
        raw = raw.strip()
        chinese_match = re.search(r'[\u4e00-\u9fff]', raw)
        if chinese_match:
            raw = raw[chinese_match.start():]

        # 只取第一行
        if '\n' in raw:
            raw = raw.split('\n')[0].strip()

        # 限制长度
        if len(raw) > 50:
            raw = raw[:50]

        print(f"步骤4-最终提取: {repr(raw)}")
        print("=" * 40 + "\n")

        # 步骤5: 尝试解析 JSON
        match = re.search(r'\{.*\}', raw, re.DOTALL)
        if match:
            try:
                result = json.loads(match.group(0))
                if 'judgement' in result and 'reply' in result:
                    return result
            except json.JSONDecodeError:
                pass

        # 步骤6: 不是 JSON，直接返回文本作为 reply
        if raw and len(raw) > 0 and raw not in ['system', 'user', 'assistant', '']:
            return {"reply": raw}

        return {"reply": "请继续提问"}