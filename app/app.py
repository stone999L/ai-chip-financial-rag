from pathlib import Path
import sys

import streamlit as st

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.hybrid_retriever import HybridRetriever
from src.qa import answer_question

st.set_page_config(page_title="AI 芯片财报 RAG", layout="wide")
st.title("国产算力与智能芯片财报问答知识库")
st.caption("BM25 + 向量检索；答案尽量回链到公司、报告期、章节和页码。")


@st.cache_resource
def get_retriever():
    return HybridRetriever()


query = st.text_area(
    "请输入问题",
    value="寒武纪 2026 年上半年营业收入及同比变化是多少？",
    height=90,
)

if st.button("检索并回答", type="primary"):
    try:
        retriever = get_retriever()
        results = retriever.search(query)

        st.subheader("回答")
        st.write(answer_question(query, results))

        st.subheader("召回证据")
        for i, item in enumerate(results, start=1):
            c = item["chunk"]
            with st.expander(
                f"[{i}] {c['company_name']} · {c['section']} · 第{c['page']}页 · {c['content_type']}"
            ):
                st.write(c["content"])
                if c.get("report_url"):
                    st.markdown(f"[打开报告原文 PDF]({c['report_url']})")
                st.json({
                    "chunk_id": c["chunk_id"],
                    "company": c["company_name"],
                    "stock_code": c["stock_code"],
                    "report_period": c["report_period"],
                    "section": c["section"],
                    "page": c["page"],
                    "disclosure_source": c.get("disclosure_source", ""),
                    "report_url": c.get("report_url", ""),
                    "routes": item["routes"],
                    "rrf_score": item["rrf_score"],
                })
    except FileNotFoundError:
        st.error("尚未建立索引。请先依次运行下载、解析、切块和 build_index.py。")
