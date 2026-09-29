from pathlib import Path
import argparse
import json
import re
import sys

import fitz
import pdfplumber
import pandas as pd
from tqdm import tqdm

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.config import MANIFEST_PATH, RAW_DIR, PAGES_JSONL


SECTION_RE = re.compile(r"^(第[一二三四五六七八九十百0-9]+节[^\n]{0,40})", re.M)


def normalize_text(text: str) -> str:
    text = text.replace("\u3000", " ")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def extract_section(text: str, current: str) -> str:
    m = SECTION_RE.search(text)
    return m.group(1).strip() if m else current


def table_to_text(table) -> str:
    if not table:
        return ""
    rows = []
    for row in table:
        cells = ["" if c is None else str(c).replace("\n", " ").strip() for c in row]
        if any(cells):
            rows.append(" | ".join(cells))
    return "\n".join(rows)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--company", action="append", help="仅解析指定公司，可重复传入")
    parser.add_argument("--max-pages", type=int, default=0, help="每份报告最多解析页数；0 表示全部")
    args = parser.parse_args()

    manifest = pd.read_csv(MANIFEST_PATH, dtype={"stock_code": str})
    if args.company:
        wanted = set(args.company)
        manifest = manifest[manifest["company_name"].isin(wanted)]
        missing_names = wanted - set(manifest["company_name"])
        if missing_names:
            raise SystemExit("清单中不存在公司：" + "、".join(sorted(missing_names)))

    PAGES_JSONL.parent.mkdir(parents=True, exist_ok=True)

    with PAGES_JSONL.open("w", encoding="utf-8") as out:
        for row in manifest.to_dict("records"):
            code = str(row["stock_code"])
            company = row["company_name"]
            period = row["report_period"]
            pdf_path = RAW_DIR / f"{code}_{company}_{period}.pdf"
            if not pdf_path.exists():
                print(f"[skip] 未找到 {pdf_path.name}")
                continue

            doc = fitz.open(pdf_path)
            page_count = len(doc)
            if args.max_pages and args.max_pages > 0:
                page_count = min(page_count, args.max_pages)

            current_section = "未识别章节"

            with pdfplumber.open(pdf_path) as plumber_pdf:
                for idx in tqdm(range(page_count), desc=f"Parsing {company}", leave=False):
                    page_no = idx + 1
                    text = normalize_text(doc[idx].get_text("text"))
                    current_section = extract_section(text, current_section)

                    tables_text = []
                    try:
                        for table in plumber_pdf.pages[idx].extract_tables() or []:
                            t = table_to_text(table)
                            if t:
                                tables_text.append(t)
                    except Exception:
                        pass

                    record = {
                        "company_name": company,
                        "stock_code": code,
                        "report_period": period,
                        "report_title": row["report_title"],
                        "page": page_no,
                        "section": current_section,
                        "text": text,
                        "tables": tables_text,
                        "source_file": pdf_path.name,
                        "report_url": row.get("report_url", ""),
                        "disclosure_source": row.get("source", ""),
                    }
                    out.write(json.dumps(record, ensure_ascii=False) + "\n")

            doc.close()

    print(f"完成。逐页解析结果：{PAGES_JSONL}")


if __name__ == "__main__":
    main()
