from pathlib import Path
import json
import sys

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.hybrid_retriever import HybridRetriever

QUESTIONS = ROOT / "evaluation" / "questions.json"
OUT = ROOT / "evaluation" / "retrieval_runs.csv"


def main():
    questions = json.loads(QUESTIONS.read_text(encoding="utf-8"))
    retriever = HybridRetriever()
    rows = []

    for q in questions:
        hits = retriever.search(q["question"])
        rows.append({
            "question_id": q["id"],
            "question": q["question"],
            "retrieved_chunk_ids": "|".join(h["chunk"]["chunk_id"] for h in hits),
            "companies_covered": "|".join(dict.fromkeys(h["chunk"]["company_name"] for h in hits)),
            "pages": "|".join(str(h["chunk"]["page"]) for h in hits),
            "sections": "|".join(h["chunk"]["section"] for h in hits),
        })

    pd.DataFrame(rows).to_csv(OUT, index=False, encoding="utf-8-sig")
    print(f"检索记录已写入 {OUT}")


if __name__ == "__main__":
    main()
