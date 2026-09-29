import json
import pickle

import jieba
import numpy as np

from .config import INDEX_DIR, BM25_TOP_K


class BM25Retriever:
    def __init__(self):
        with (INDEX_DIR / "bm25.pkl").open("rb") as f:
            self.index = pickle.load(f)
        with (INDEX_DIR / "chunks.jsonl").open("r", encoding="utf-8") as f:
            self.chunks = [json.loads(line) for line in f]

    def search(self, query: str, top_k: int = BM25_TOP_K):
        tokens = list(jieba.cut(query))
        scores = np.asarray(self.index.get_scores(tokens))
        ids = np.argsort(scores)[::-1][:top_k]
        return [
            {"chunk": self.chunks[i], "score": float(scores[i]), "source": "bm25"}
            for i in ids
        ]
