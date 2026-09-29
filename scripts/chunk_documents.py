from pathlib import Path
import json
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.config import PAGES_JSONL, CHUNKS_JSONL

TARGET_CHARS = 900
OVERLAP_CHARS = 120


def split_text(text: str):
    text = text.strip()
    if not text:
        return []
    sentences = re.split(r"(?<=[。！？；])", text)
    chunks, cur = [], ""
    for sent in sentences:
        if len(cur) + len(sent) <= TARGET_CHARS or not cur:
            cur += sent
        else:
            chunks.append(cur.strip())
            overlap = cur[-OVERLAP_CHARS:] if len(cur) > OVERLAP_CHARS else cur
            cur = overlap + sent
    if cur.strip():
        chunks.append(cur.strip())
    return chunks


def main() -> None:
    CHUNKS_JSONL.parent.mkdir(parents=True, exist_ok=True)
    counter = 0

    with PAGES_JSONL.open("r", encoding="utf-8") as src, CHUNKS_JSONL.open("w", encoding="utf-8") as out:
        for line in src:
            page = json.loads(line)
            base = {
                "company_name": page["company_name"],
                "stock_code": page["stock_code"],
                "report_period": page["report_period"],
                "report_title": page["report_title"],
                "section": page["section"],
                "page": page["page"],
                "source_file": page["source_file"],
            }

            for i, chunk in enumerate(split_text(page["text"])):
                counter += 1
                rec = {
                    **base,
                    "chunk_id": f'{page["stock_code"]}_{page["report_period"]}_P{page["page"]:04d}_T{i:02d}',
                    "content_type": "text",
                    "content": chunk,
                }
                out.write(json.dumps(rec, ensure_ascii=False) + "\n")

            for j, table_text in enumerate(page.get("tables", [])):
                if not table_text.strip():
                    continue
                counter += 1
                rec = {
                    **base,
                    "chunk_id": f'{page["stock_code"]}_{page["report_period"]}_P{page["page"]:04d}_TABLE{j:02d}',
                    "content_type": "table",
                    "content": table_text,
                }
                out.write(json.dumps(rec, ensure_ascii=False) + "\n")

    print(f"完成。共生成 {counter} 个文本/表格块：{CHUNKS_JSONL}")


if __name__ == "__main__":
    main()
