from pathlib import Path
import os

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
RAW_DIR = DATA_DIR / "raw"
PROCESSED_DIR = DATA_DIR / "processed"
INDEX_DIR = DATA_DIR / "index"

MANIFEST_PATH = DATA_DIR / "reports_manifest.csv"
PAGES_JSONL = PROCESSED_DIR / "pages.jsonl"
CHUNKS_JSONL = PROCESSED_DIR / "chunks.jsonl"

EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "BAAI/bge-small-zh-v1.5")
EMBED_BATCH_SIZE = int(os.getenv("EMBED_BATCH_SIZE", "32"))
BM25_TOP_K = int(os.getenv("BM25_TOP_K", "10"))
VECTOR_TOP_K = int(os.getenv("VECTOR_TOP_K", "10"))
FINAL_TOP_K = int(os.getenv("FINAL_TOP_K", "8"))

LLM_API_KEY = os.getenv("LLM_API_KEY", "")
LLM_BASE_URL = os.getenv("LLM_BASE_URL", "")
LLM_MODEL = os.getenv("LLM_MODEL", "")

for p in [RAW_DIR, PROCESSED_DIR, INDEX_DIR]:
    p.mkdir(parents=True, exist_ok=True)
