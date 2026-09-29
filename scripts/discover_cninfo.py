from __future__ import annotations

import argparse
from pathlib import Path
import sys

import pandas as pd
import requests

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.config import MANIFEST_PATH

API = "https://www.cninfo.com.cn/new/hisAnnouncement/query"


def query_cninfo(code: str):
    headers = {
        "User-Agent": "Mozilla/5.0",
        "Referer": "https://www.cninfo.com.cn/",
        "X-Requested-With": "XMLHttpRequest",
    }
    data = {
        "pageNum": 1,
        "pageSize": 50,
        "column": "szse",
        "tabName": "fulltext",
        "plate": "sz",
        "stock": code,
        "searchkey": "2026年半年度报告",
        "secid": "",
        "category": "",
        "trade": "",
        "seDate": "2026-08-01~2026-09-10",
        "sortName": "",
        "sortType": "",
        "isHLtitle": "true",
    }
    r = requests.post(API, headers=headers, data=data, timeout=30)
    r.raise_for_status()
    payload = r.json()
    return payload.get("announcements") or []


def clean_title(title: str) -> str:
    return (
        str(title)
        .replace("<em>", "")
        .replace("</em>", "")
        .replace(" ", "")
    )


def pick_full_report(items, code: str):
    candidates = []
    for item in items:
        title = clean_title(item.get("announcementTitle", ""))
        sec_code = str(item.get("secCode") or "")
        if sec_code and sec_code != code:
            continue
        if "2026年半年度报告" not in title:
            continue
        if any(x in title for x in ["摘要", "披露提示", "业绩说明会"]):
            continue
        adjunct = item.get("adjunctUrl") or ""
        if adjunct:
            candidates.append((title, adjunct))
    return candidates


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--only-pending", action="store_true")
    args = parser.parse_args()

    df = pd.read_csv(MANIFEST_PATH, dtype={"stock_code": str})
    if args.only_pending:
        df = df[~df["status"].eq("verified_full_report")]

    if df.empty:
        print("没有待发现链接的公司。")
        return

    for row in df.to_dict("records"):
        code = str(row["stock_code"])
        company = row["company_name"]
        if row["exchange"] != "SZSE":
            print(f"[skip] {company} {code}: 当前发现脚本只处理 SZSE/CNINFO。")
            continue
        try:
            items = query_cninfo(code)
            candidates = pick_full_report(items, code)
        except Exception as e:
            print(f"[error] {company} {code}: {e}")
            continue

        if not candidates:
            print(f"[not-found] {company} {code}")
            continue

        for title, adjunct in candidates:
            url = adjunct if adjunct.startswith("http") else "https://static.cninfo.com.cn/" + adjunct.lstrip("/")
            print(f"[found] {company} {code} | {title} | {url}")


if __name__ == "__main__":
    main()
