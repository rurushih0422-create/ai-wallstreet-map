#!/usr/bin/env python3
# 每天撈「現價 + 52週高」，算回檔%，產生回檔燈號 data.json
# 燈號規則：回檔 >20% = green（可分批）/ 10–20% = yellow（觀察）/ <10% = red（偏高別追）
import json, urllib.request, datetime, sys

# 前端比對用的「代號」: Yahoo 代號（台股給裸碼，下面自動試 .TW / .TWO）
TICKERS = {
    # 台股個股（上市/上櫃自動偵測）
    "2330": "2330", "2317": "2317", "3260": "3260", "3017": "3017",
    "2327": "2327", "2377": "2377", "3481": "3481", "2464": "2464",
    "2376": "2376", "3037": "3037", "2308": "2308", "2382": "2382",
    "3324": "3324", "2345": "2345", "1519": "1519", "2049": "2049",
    "6188": "6188", "4931": "4931", "4967": "4967", "3595": "3595",
    "8027": "8027", "2313": "2313", "2383": "2383", "6274": "6274",
    "3105": "3105", "8068": "8068", "4971": "4971", "6442": "6442",
    "4979": "4979", "3363": "3363", "3081": "3081",
    # 台股 ETF
    "0050": "0050", "00941": "00941", "00830": "00830", "00891": "00891",
    "00911": "00911", "00757": "00757", "00635U": "00635U",
    # 美股 ETF
    "QQQ": "QQQ", "VOO": "VOO", "VT": "VT", "XLK": "XLK", "VGT": "VGT",
    "IYW": "IYW", "SMH": "SMH", "SOXX": "SOXX", "AIQ": "AIQ", "BOTZ": "BOTZ",
    "IGV": "IGV", "QTUM": "QTUM", "CIBR": "CIBR", "IAU": "IAU", "GLD": "GLD",
    "IBIT": "IBIT", "SGOV": "SGOV",
    # 美股個股
    "Google": "GOOGL", "INFQ": "INFQ", "IONQ": "IONQ", "RGTI": "RGTI", "QBTS": "QBTS",
}

def _get(sym):
    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{sym}?range=1y&interval=1d"
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=20) as r:
        d = json.load(r)
    m = d["chart"]["result"][0]["meta"]
    return float(m["regularMarketPrice"]), float(m["fiftyTwoWeekHigh"])

def fetch(sym):
    # 純數字（台股）：先試 .TW（上市），失敗再試 .TWO（上櫃）
    if sym.replace("U", "").isdigit():
        try:
            return _get(sym + ".TW")
        except Exception:
            return _get(sym + ".TWO")
    return _get(sym)

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
