"""
测试问答流程 - 使用 Anthropic SDK
"""
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

import anthropic
from app.config import get_settings

settings = get_settings()

def test_llm():
    """测试 Anthropic LLM 调用"""
    print("=== 测试 Anthropic LLM ===")

    client = anthropic.Anthropic(
        base_url=settings.anthropic_base_url,
        api_key=settings.anthropic_auth_token,
    )

    # 简单测试
    prompt = """你是一个住建领域知识助手。

【知识内容】
建设工程竣工验收需要满足以下条件：
1. 完成工程设计和合同约定的各项内容
2. 有完整的技术档案和施工管理资料
3. 有工程使用的主要建筑材料合格证明

【用户问题】
建设工程竣工验收需要哪些条件？

请根据知识内容给出简洁的回答。"""

    print(f"Prompt 长度: {len(prompt)} 字符")

    message = client.messages.create(
        model=settings.anthropic_default_haiku_model,
        max_tokens=1024,
        messages=[
            {"role": "user", "content": prompt}
        ]
    )

    print(f"模型: {settings.anthropic_default_haiku_model}")
    print(f"Tokens: input={message.usage.input_tokens}, output={message.usage.output_tokens}")
    print(f"Content blocks: {len(message.content)}")

    # 打印所有 content block
    for i, block in enumerate(message.content):
        print(f"  Block {i}: {block}")
        print(f"    type: {type(block).__name__}")
        print(f"    attrs: {list(block.model_dump().keys())}")

    # 从 message.content 提取文本
    # 可能是 list of ContentBlock 或类似结构
    content = ""
    if hasattr(message.content, '__iter__'):
        for block in message.content:
            block_dict = block if isinstance(block, dict) else block.model_dump()
            if block_dict.get('type') == 'text':
                content = block_dict.get('text', '')
                break

    if content:
        print(f"\n回答:\n{content}")
    else:
        # 尝试其他方式
        print(f"\n[DEBUG] message.content: {message.content}")

    return content

def main():
    print("开始测试 LLM 问答流程...\n")

    try:
        answer = test_llm()
        print("\n[OK] LLM 测试成功!")
    except Exception as e:
        print(f"\n[FAIL] 测试失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()