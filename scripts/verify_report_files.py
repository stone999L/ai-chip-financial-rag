from pathlib import Path
import io
import sys

import fitz
import pandas as pd
import requests

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.config import MANIFEST_PATH


def main() -> None:
    df = pd.read_csv(MANIFEST_PATH, dtype={"stock_code": str})
    df = df[df["status"].eq("verified_full_report")]
    if df.empty:
        raise SystemExit("没有已核验报告可检查。")

    s = requests.Session()
    s.headers.update({"User-Agent": "Mozilla/5.0 financial-rag-course-project"})

    errors = []
    for row in df.to_dict("records"):
        company = row["company_name"]
        code = str(row["stock_code"])
        url = str(row["report_url"]).strip()
        try:
            r = s.get(url, timeout=90)
            r.raise_for_status()
            data = r.content
            if not data.startswith(b"%PDF"):
                raise RuntimeError("响应不是 PDF")
            if len(data) < 50_000:
                raise RuntimeError(f"PDF 过小: {len(data)} bytes")

            doc = fitz.open(stream=data, filetype="pdf")
            sample = "\n".join(doc[i].get_text("text") for i in range(min(5, len(doc))))
            pages = len(doc)
            doc.close()

            normalized = sample.replace(" ", "").replace("\n", "")
            if "2026" not in normalized or "半年度报告" not in normalized:
                raise RuntimeError("前 5 页未识别到“2026/半年度报告”")
            if company not in normalized and code not in normalized:
                raise RuntimeError("前 5 页未识别到公司名或证券代码")

            print(f"[ok] {company} {code} | pages={pages} | bytes={len(data)} | {url}")
        except Exception as e:
            errors.append(f"{company} {code}: {e}")
            print(f"[error] {company} {code}: {e}")

    print(f"checked={len(df)} errors={len(errors)}")
    if errors:
        raise SystemExit("\n".join(errors))


if __name__ == "__main__":
    main()
