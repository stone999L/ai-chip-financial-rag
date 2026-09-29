from pathlib import Path
import json
import pickle
import sys

import jieba
import numpy as np
from rank_bm25 import BM25Okapi
from sentence_transformers import SentenceTransformer
from tqdm import tqdm

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.config import CHUNKS_JSONL, INDEX_DIR, EMBEDDING_MODEL


def load_chunks():
    with CHUNKS_JSONL.open("r", encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]


def retrieval_text(c):
    return (
        f'公司：{c["company_name"]}\n'
        f'章节：{c["section"]}\n'
        f'页码：{c["page"]}\n'
        f'{c["content"]}'
    )


def main() -> None:
    chunks = load_chunks()
    if not chunks:
        raise SystemExit("chunks.jsonl 为空，请先运行解析与切块。")

    texts = [retrieval_text(c) for c in chunks]

    tokenized = [list(jieba.cut(t)) for t in tqdm(texts, desc="BM25 tokenize")]
    bm25 = BM25Okapi(tokenized)
    with (INDEX_DIR / "bm25.pkl").open("wb") as f:
        pickle.dump(bm25, f)

    model = SentenceTransformer(EMBEDDING_MODEL, trust_remote_code=True)
    vectors = model.encode(
        texts,
        batch_size=16,
        normalize_embeddings=True,
        show_progress_bar=True,
    )
    vectors = np.asarray(vectors, dtype=np.float32)
    np.save(INDEX_DIR / "vectors.npy", vectors)

    with (INDEX_DIR / "chunks.jsonl").open("w", encoding="utf-8") as f:
        for c in chunks:
            f.write(json.dumps(c, ensure_ascii=False) + "\n")

    (INDEX_DIR / "embedding_model.txt").write_text(EMBEDDING_MODEL, encoding="utf-8")
    print(f"完成：{len(chunks)} 个块，向量维度 {vectors.shape[1]}")


if __name__ == "__main__":
    main()
