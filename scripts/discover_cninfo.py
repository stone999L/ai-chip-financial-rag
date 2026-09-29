from __future__ import annotations

import argparse
from pathlib import Path
import sys

import pandas as pd
import requests

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.config import MANIFEST_PATH

ANNOUNCEMENT_API = "https://www.cninfo.com.cn/new/hisAnnouncement/query"
TOP_SEARCH_API = "https://www.cninfo.com.cn/new/information/topSearch/query"

HEADERS = {
    "User-Agent": "Mozilla/5.0",
    "Referer": "https://www.cninfo.com.cn/",
    "X-Requested-With": "XMLHttpRequest",
}


def fallback_org_id(code: str) -> str:
    if code.startswith("6"):
        return f"gssh0{code}"
    if code.startswith(("8", "4")):
        return f"gsbj0{code}"
    return f"gssz0{code}"


def resolve_org_id(session: requests.Session, code: str) -> str:
    """Resolve CNINFO orgId; fall back to the stable exchange-code pattern."""
    try:
        r = session.post(
            TOP_SEARCH_API,
            headers=HEADERS,
            data={"keyWord": code, "maxNum": 10},
            timeout=30,
        )
        r.raise_for_status()
        payload = r.json()

        # CNINFO has returned both list and dict-shaped payloads over time.
        candidates = payload if isinstance(payload, list) else (
            payload.get("keyBoardList")
            or payload.get("data")
            or payload.get("result")
            or []
        )
        if isinstance(candidates, dict):
            candidates = candidates.get("list") or candidates.get("items") or []

        for item in candidates or []:
            sec_code = str(
                item.get("code")
                or item.get("secCode")
                or item.get("stockCode")
                or ""
            )
            org_id = str(
                item.get("orgId")
                or item.get("orgid")
                or item.get("orgID")
                or ""
            )
            if sec_code == code and org_id:
                return org_id
    except Exception as e:
        print(f"[orgid-warning] {code}: {e}")

    return fallback_org_id(code)


def query_cninfo(session: requests.Session, code: str, exchange: str):
    org_id = resolve_org_id(session, code)
    column = "szse" if exchange == "SZSE" else "sse"
    plate = "sz" if exchange == "SZSE" else "sh"

    data = {
        "pageNum": 1,
        "pageSize": 50,
        "column": column,
        "tabName": "fulltext",
        "plate": plate,
        "stock": f"{code},{org_id}",
        "searchkey": "2026年半年度报告",
        "secid": "",
        "category": "",
        "trade": "",
        "seDate": "2026-08-01~2026-09-10",
        "sortName": "",
        "sortType": "",
        "isHLtitle": "true",
    }
    r = session.post(ANNOUNCEMENT_API, headers=HEADERS, data=data, timeout=30)
    r.raise_for_status()
    payload = r.json()
    print(
        f"[query] code={code} exchange={exchange} orgId={org_id} "
        f"total={payload.get('totalAnnouncement', 'n/a')}"
    )
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

    session = requests.Session()
    session.headers.update(HEADERS)

    for row in df.to_dict("records"):
        code = str(row["stock_code"])
        company = row["company_name"]
        exchange = row["exchange"]

        try:
            items = query_cninfo(session, code, exchange)
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
