from pathlib import Path
import json
import sys

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.bm25_retriever import BM25Retriever
from src.vector_retriever import VectorRetriever
from src.hybrid_retriever import HybridRetriever

QUESTIONS = ROOT / "evaluation" / "questions.json"
OUT = ROOT / "evaluation" / "retrieval_runs.csv"


def ids(results):
    return "|".join(
        (x.get("chunk") or x["chunk"])["chunk_id"] for x in results
    )


def companies(results):
    ordered = []
    for x in results:
        c = (x.get("chunk") or x["chunk"])["company_name"]
        if c not in ordered:
            ordered.append(c)
    return ordered


def pages(results):
    return "|".join(str((x.get("chunk") or x["chunk"])["page"]) for x in results)


def required_companies(q, all_companies):
    v = q.get("companies")
    if v == "all":
        return list(all_companies)
    return list(v or [])


def coverage(retrieved, required):
    if not required:
        return None
    return len(set(retrieved) & set(required)) / len(set(required))


def main():
    questions = json.loads(QUESTIONS.read_text(encoding="utf-8"))

    bm25 = BM25Retriever()
    vector = VectorRetriever()
    hybrid = HybridRetriever()

    all_companies = []
    for chunk in bm25.chunks:
        name = chunk["company_name"]
        if name not in all_companies:
            all_companies.append(name)

    rows = []

    for q in questions:
        b = bm25.search(q["question"])
        v = vector.search(q["question"])
        h = hybrid.search(q["question"])

        b_companies = companies(b)
        v_companies = companies(v)
        h_companies = companies(h)
        required = required_companies(q, all_companies)

        rows.append({
            "question_id": q["id"],
            "question_type": q["type"],
            "question": q["question"],
            "required_companies": "|".join(required),
            "bm25_chunk_ids": ids(b),
            "bm25_companies": "|".join(b_companies),
            "bm25_company_coverage": coverage(b_companies, required),
            "vector_chunk_ids": ids(v),
            "vector_companies": "|".join(v_companies),
            "vector_company_coverage": coverage(v_companies, required),
            "hybrid_chunk_ids": ids(h),
            "hybrid_companies": "|".join(h_companies),
            "hybrid_company_coverage": coverage(h_companies, required),
            "hybrid_pages": pages(h),
        })

    df = pd.DataFrame(rows)
    df.to_csv(OUT, index=False, encoding="utf-8-sig")

    print(df[[
        "question_id",
        "bm25_company_coverage",
        "vector_company_coverage",
        "hybrid_company_coverage",
        "hybrid_companies",
    ]].to_string(index=False))
    print(f"检索记录已写入 {OUT}")


if __name__ == "__main__":
    main()
