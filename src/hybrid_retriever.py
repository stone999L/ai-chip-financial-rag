from .bm25_retriever import BM25Retriever
from .vector_retriever import VectorRetriever
from .config import FINAL_TOP_K


class HybridRetriever:
    def __init__(self):
        self.bm25 = BM25Retriever()
        self.vector = VectorRetriever()

    @staticmethod
    def _rrf(result_lists, k=60):
        merged = {}
        for results in result_lists:
            for rank, item in enumerate(results, start=1):
                cid = item["chunk"]["chunk_id"]
                if cid not in merged:
                    merged[cid] = {
                        "chunk": item["chunk"],
                        "rrf_score": 0.0,
                        "routes": [],
                    }
                merged[cid]["rrf_score"] += 1.0 / (k + rank)
                merged[cid]["routes"].append(
                    {"source": item["source"], "rank": rank, "raw_score": item["score"]}
                )
        return sorted(merged.values(), key=lambda x: x["rrf_score"], reverse=True)

    def search(self, query: str, final_top_k: int = FINAL_TOP_K):
        b = self.bm25.search(query)
        v = self.vector.search(query)
        return self._rrf([b, v])[:final_top_k]
