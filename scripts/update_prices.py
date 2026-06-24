#!/usr/bin/env python3
"""
更新 data.json 股價資料
用法：python3 scripts/update_prices.py
"""
import urllib.request, json, time, os

SYMBOLS = {
    # 台股個股
    "2330":"2330.TW","2317":"2317.TW","3260":"3260.TW","3017":"3017.TW",
    "2327":"2327.TW","2377":"2377.TW","3481":"3481.TW","2464":"2464.TW",
    "2376":"2376.TW","3037":"3037.TW","2308":"2308.TW","2382":"2382.TW",
    "3324":"3324.TW","2345":"2345.TW","1519":"1519.TW","2049":"2049.TW",
    "6188":"6188.TW","4931":"4931.TW","4967":"4967.TW","3595":"3595.TW",
    "8027":"8027.TW","2313":"2313.TW","2383":"2383.TW","6274":"6274.TW",
    "3105":"3105.TW","8068":"8068.TW","4971":"4971.TW","6442":"6442.TW",
    "4979":"4979.TW","3363":"3363.TW","3081":"3081.TW",
    # 台股 ETF
    "0050":"0050.TW","00941":"00941.TW","00830":"00830.TW","00891":"00891.TW",
    "00911":"00911.TW","00757":"00757.TW","00635U":"00635U.TW",
    # 美股 ETF / 個股
    "QQQ":"QQQ","VOO":"VOO","VT":"VT","XLK":"XLK","VGT":"VGT","IYW":"IYW",
    "SMH":"SMH","SOXX":"SOXX","AIQ":"AIQ","BOTZ":"BOTZ","IGV":"IGV",
    "QTUM":"QTUM","CIBR":"CIBR","IAU":"IAU","GLD":"GLD","IBIT":"IBIT",
    "SGOV":"SGOV","Google":"GOOGL","INFQ":"INFQ","IONQ":"IONQ",
    "RGTI":"RGTI","QBTS":"QBTS","LSCC":"LSCC",
}

TW_KEYS = {k for k, v in SYMBOLS.items() if v.endswith(".TW")}
HEADERS = {"User-Agent": "Mozilla/5.0"}

def fetch(sym):
    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{sym}?interval=1d&range=5d"
    req = urllib.request.Request(url, headers=HEADERS)
    with urllib.request.urlopen(req, timeout=8) as r:
        d = json.loads(r.read())
    meta = d['chart']['result'][0]['meta']
    price = meta.get('regularMarketPrice') or meta.get('previousClose')
    high52 = meta.get('fiftyTwoWeekHigh')
    prev = meta.get('chartPreviousClose') or meta.get('previousClose')
    chg1d = round((price - prev) / prev * 100, 1) if prev and price else 0
    return price, high52, chg1d

def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    data_path = os.path.join(script_dir, '..', 'data.json')

    with open(data_path) as f:
        existing = json.load(f)
    old_items = existing['items']

    fresh = {}
    for key, sym in SYMBOLS.items():
        try:
            price, high52, chg1d = fetch(sym)
            if price and high52:
                dd = round((high52 - price) / high52 * 100, 1)
                fresh[key] = {"price": round(price, 2), "high": round(high52, 2),
                              "dd": dd, "chg1d": chg1d}
                print(f"✓ {key:8s}  {price:>8.2f}  dd:{dd:>5.1f}%  1d:{chg1d:>+5.1f}%")
            else:
                print(f"✗ {key}: no price")
        except Exception as e:
            print(f"✗ {key} ({sym}): {e}")
        time.sleep(0.15)

    # 基準計算（VOO = 美股，0050 = 台股）
    voo_old = old_items.get('VOO', {}).get('price', fresh.get('VOO', {}).get('price', 1))
    tw_old  = old_items.get('0050', {}).get('price', fresh.get('0050', {}).get('price', 1))
    voo_new = fresh.get('VOO', {}).get('price', voo_old)
    tw_new  = fresh.get('0050', {}).get('price', tw_old)
    voo_chg = (voo_new - voo_old) / voo_old * 100
    tw_chg  = (tw_new  - tw_old)  / tw_old  * 100

    new_items = dict(old_items)
    for key, fd in fresh.items():
        old_price = old_items.get(key, {}).get('price', fd['price'])
        stock_chg = (fd['price'] - old_price) / old_price * 100
        rs = round(stock_chg - (tw_chg if key in TW_KEYS else voo_chg), 1)
        light = "green" if fd['dd'] > 20 else ("yellow" if fd['dd'] >= 7 else "red")
        new_items[key] = {
            "price": fd['price'], "high": fd['high'], "dd": fd['dd'],
            "light": light, "r20": fd['chg1d'], "rs": rs
        }

    from datetime import datetime
    result = {
        "updated": datetime.now().strftime("%Y-%m-%d %H:%M") + " (台北時間)",
        "bench": {"tw": round(tw_chg, 1), "us": round(voo_chg, 1)},
        "items": new_items
    }
    with open(data_path, 'w') as f:
        json.dump(result, f, ensure_ascii=False, separators=(',', ':'))

    js_path = os.path.join(script_dir, '..', 'data.js')
    with open(js_path, 'w') as f:
        f.write('window.__STOCK_DATA__=' + json.dumps(result, ensure_ascii=False, separators=(',', ':')) + ';')

    print(f"\n✅ data.json + data.js 更新完成（{len(fresh)}/{len(SYMBOLS)} 筆）")
    print(f"   台股大盤: {tw_chg:+.1f}%  美股大盤: {voo_chg:+.1f}%")

if __name__ == '__main__':
    main()
