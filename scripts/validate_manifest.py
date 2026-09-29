from pathlib import Path
import sys
from urllib.parse import urlparse

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.config import MANIFEST_PATH

REQUIRED_COLUMNS = {
    "company_name",
    "stock_code",
    "exchange",
    "report_period",
    "report_title",
    "report_url",
    "source",
    "status",
}


def main() -> None:
    df = pd.read_csv(MANIFEST_PATH, dtype={"stock_code": str})
    errors = []
    warnings = []

    missing_cols = REQUIRED_COLUMNS - set(df.columns)
    if missing_cols:
        errors.append(f"缺少字段: {sorted(missing_cols)}")

    if len(df) < 10:
        errors.append(f"课程要求至少 10 家公司，当前只有 {len(df)} 家。")

    if df["stock_code"].duplicated().any():
        errors.append("证券代码存在重复。")

    if not df["report_period"].eq("2026H1").all():
        errors.append("样本报告期不统一，当前项目应统一为 2026H1。")

    verified = df["status"].eq("verified_full_report")
    for _, row in df[verified].iterrows():
        url = str(row.get("report_url") or "").strip()
        if not url or url.lower() == "nan":
            errors.append(f'{row["company_name"]}: 已标记 verified 但 URL 为空。')
            continue
        parsed = urlparse(url)
        if parsed.scheme not in {"http", "https"}:
            errors.append(f'{row["company_name"]}: URL 格式异常: {url}')
        if "摘要" in str(row["report_title"]):
            errors.append(f'{row["company_name"]}: 错把摘要作为全文。')

    pending = df[~verified]
    if not pending.empty:
        warnings.append(
            "尚未核验全文直链: " + "、".join(pending["company_name"].astype(str).tolist())
        )

    print(f"样本公司: {len(df)} 家")
    print(f"已核验全文直链: {int(verified.sum())} 家")
    print(f"待核验: {len(df) - int(verified.sum())} 家")

    for w in warnings:
        print("[warning]", w)

    if errors:
        for e in errors:
            print("[error]", e)
        raise SystemExit(1)

    print("manifest 结构检查通过。")


if __name__ == "__main__":
    main()
