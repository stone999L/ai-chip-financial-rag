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
    missing = manifest["report_url"].fillna("").eq("")
    if missing.any():
        names = "、".join(manifest.loc[missing, "company_name"].tolist())
        raise SystemExit(
            "以下公司尚未登记已核验的官方半年报 URL：" + names +
            "\n请先更新 data/reports_manifest.csv，再运行下载。"
        )

    session = requests.Session()
    session.headers.update({"User-Agent": "Mozilla/5.0 financial-rag-course-project"})

    for row in tqdm(manifest.to_dict("records"), desc="Downloading"):
        code = str(row["stock_code"])
        company = row["company_name"]
        period = row["report_period"]
        url = row["report_url"]
        out = RAW_DIR / f"{code}_{company}_{period}.pdf"
        if out.exists() and out.stat().st_size > 100_000:
            continue

        resp = session.get(url, timeout=60)
        resp.raise_for_status()
        ctype = resp.headers.get("content-type", "").lower()
        if "pdf" not in ctype and not resp.content.startswith(b"%PDF"):
            raise RuntimeError(f"{company} 下载结果不是 PDF: {url}")
        out.write_bytes(resp.content)

    print(f"完成。PDF 保存于 {RAW_DIR}")


if __name__ == "__main__":
    main()
