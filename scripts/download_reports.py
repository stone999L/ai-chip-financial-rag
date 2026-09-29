from pathlib import Path
import sys

import pandas as pd
import requests
from tqdm import tqdm

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.config import MANIFEST_PATH, RAW_DIR


def main() -> None:
    manifest = pd.read_csv(MANIFEST_PATH, dtype={"stock_code": str})
    session = requests.Session()
    session.headers.update({"User-Agent": "Mozilla/5.0 financial-rag-course-project"})

    downloaded = 0
    skipped = []

    for row in tqdm(manifest.to_dict("records"), desc="Downloading"):
        url = str(row.get("report_url") or "").strip()
        company = row["company_name"]
        if not url or url.lower() == "nan":
            skipped.append(company)
            continue

        code = str(row["stock_code"])
        period = row["report_period"]
        out = RAW_DIR / f"{code}_{company}_{period}.pdf"

        if out.exists() and out.stat().st_size > 100_000:
            continue

        resp = session.get(url, timeout=90)
        resp.raise_for_status()
        ctype = resp.headers.get("content-type", "").lower()
        if "pdf" not in ctype and not resp.content.startswith(b"%PDF"):
            raise RuntimeError(f"{company} 下载结果不是 PDF: {url}")

        out.write_bytes(resp.content)
        downloaded += 1

    print(f"本次新下载 {downloaded} 份 PDF，保存于 {RAW_DIR}")
    if skipped:
        print("以下公司因尚未登记已核验 PDF URL 而跳过：" + "、".join(skipped))


if __name__ == "__main__":
    main()
