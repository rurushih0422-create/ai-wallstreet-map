#!/usr/bin/env python3
# 每天撈「現價 + 52週高」，算回檔%，產生回檔燈號 data.json
# 燈號規則：回檔 >20% = green（可分批）/ 10–20% = yellow（觀察）/ <10% = red（偏高別追）
import json, urllib.request, datetime, sys

# 前端比對用的「代號」: Yahoo 代號
TICKERS = {
    # 台股個股
    "2330": "2330.TW", "2317": "2317.TW", "3260": "3260.TW", "3017": "3017.TW",
    "2327": "2327.TW", "2377": "2377.TW", "3481": "3481.TW", "2464": "2464.TW",
    "2376": "2376.TW", "3037": "3037.TW",
    # 台股 ETF
    "0050": "0050.TW", "00941": "00941.TW", "00830": "00830.TW", "00891": "00891.TW",
    "00911": "00911.TW", "00757": "00757.TW", "00635U": "00635U.TW",
    # 美股 ETF
    "QQQ": "QQQ", "XLK": "XLK", "VGT": "VGT", "IYW": "IYW", "SMH": "SMH", "SOXX": "SOXX",
    "AIQ": "AIQ", "BOTZ": "BOTZ", "IGV": "IGV", "QTUM": "QTUM", "CIBR": "CIBR",
    "IAU": "IAU", "GLD": "GLD", "IBIT": "IBIT", "SGOV": "SGOV",
    # 美股個股
    "Google": "GOOGL", "INFQ": "INFQ",
}

def fetch(sym):
    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{sym}?range=1y&interval=1d"
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=20) as r:
        d = json.load(r)
    m = d["chart"]["result"][0]["meta"]
    return float(m["regularMarketPrice"]), float(m["fiftyTwoWeekHigh"])

items = {}
fail = []
for code, sym in TICKERS.items():
    try:
        price, high = fetch(sym)
        dd = round((high - price) / high * 100, 1) if high else 0.0
        light = "green" if dd > 20 else ("yellow" if dd >= 10 else "red")
        items[code] = {"price": price, "high": high, "dd": dd, "light": light}
    except Exception as e:
        fail.append(code)

out = {"updated": datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC"), "items": items}
with open("data.json", "w", encoding="utf-8") as f:
    json.dump(out, f, ensure_ascii=False)
print(f"OK: {len(items)} items, failed: {fail}")
