from openai import OpenAI

from .config import LLM_API_KEY, LLM_BASE_URL, LLM_MODEL


def format_evidence(results):
    blocks = []
    for i, item in enumerate(results, start=1):
        c = item["chunk"]
        blocks.append(
            f"[{i}] {c['company_name']} | {c['report_period']} | {c['section']} | 第{c['page']}页 | {c['content_type']}\n"
            f"{c['content']}"
        )
    return "\n\n".join(blocks)


def answer_question(query: str, results):
    evidence = format_evidence(results)

    if not (LLM_API_KEY and LLM_MODEL):
        return (
            "当前未配置回答模型，因此处于“只展示证据”模式。\n\n"
            "检索证据如下：\n\n" + evidence
        )

    client = OpenAI(api_key=LLM_API_KEY, base_url=LLM_BASE_URL or None)
    prompt = f"""你是上市公司财报问答助手。
只能依据【证据】回答，不得使用证据之外的数字或事实。
如果证据不足，明确写“当前检索证据不足，无法确认”。
涉及数字时必须说明公司、报告期和口径。
答案中的事实后面用 [1] [2] 形式标出对应证据编号。

【问题】
{query}

【证据】
{evidence}
"""
    resp = client.chat.completions.create(
        model=LLM_MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=0,
    )
    return resp.choices[0].message.content
