import re
import requests

PAGES = {
    "景嘉微_sina": "https://money.finance.sina.com.cn/corp/view/vCB_AllBulletinDetail.php?id=12510663&stockid=300474",
    "国科微_sina": "https://money.finance.sina.com.cn/corp/view/vCB_AllBulletinDetail.php?id=12571545&stockid=300672",
    "景嘉微_stockstar": "https://stock.stockstar.com/notice/SN2026082000037976.shtml",
    "国科微_stockstar": "https://wap.stockstar.com/detail/SN2026082800049268",
}

PATTERNS = [
    r'https?://[^"\'<> ]+\.PDF',
    r'https?:\\/\\/[^"\'<> ]+\.PDF',
    r'https?://[^"\'<> ]+\.pdf',
    r'https?:\\/\\/[^"\'<> ]+\.pdf',
]

headers = {"User-Agent": "Mozilla/5.0"}

for name, url in PAGES.items():
    try:
        r = requests.get(url, headers=headers, timeout=30)
        print(f"[page] {name} status={r.status_code} bytes={len(r.content)}")
        text = r.text
        found = set()
        for pat in PATTERNS:
            for m in re.findall(pat, text, flags=re.I):
                found.add(m.replace("\\/", "/"))
        for link in sorted(found):
            if any(host in link for host in ["cninfo", "szse", "sse", "dfcfw"]):
                print(f"[pdf] {name} | {link}")
    except Exception as e:
        print(f"[error] {name}: {e}")
