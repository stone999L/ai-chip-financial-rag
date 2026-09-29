import json

import numpy as np
from sentence_transformers import SentenceTransformer

from .config import INDEX_DIR, VECTOR_TOP_K, EMBEDDING_MODEL


class VectorRetriever:
    def __init__(self):
        self.vectors = np.load(INDEX_DIR / "vectors.npy")
        with (INDEX_DIR / "chunks.jsonl").open("r", encoding="utf-8") as f:
            self.chunks = [json.loads(line) for line in f]
        model_name_path = INDEX_DIR / "embedding_model.txt"
        model_name = model_name_path.read_text(encoding="utf-8").strip() if model_name_path.exists() else EMBEDDING_MODEL
        self.model = SentenceTransformer(model_name, trust_remote_code=True)

    def search(self, query: str, top_k: int = VECTOR_TOP_K):
        q = self.model.encode([query], normalize_embeddings=True)[0]
        scores = self.vectors @ q
        ids = np.argsort(scores)[::-1][:top_k]
        return [
            {"chunk": self.chunks[i], "score": float(scores[i]), "source": "vector"}
            for i in ids
        ]
