#!/usr/bin/env python3
"""Paper trading Moomoo (demo, tanpa uang asli, tanpa akun).

Track saham AS/global ke-4. Modul ini berjalan di data publik gratis
Yahoo Finance (harga tutup harian, tanpa key) sampai gateway OpenD
Moomoo hidup — lihat MOOMOO_BRIDGE.md. (Stooq dicoba dulu tapi
diblokir dari VM ini: mengembalikan halaman JS-check, bukan CSV.)
Bukan data real-time Moomoo, dan komisi/fee live belum dimodelkan.

Aturan demo (sama seperti venue lain, dalam rupiah):
  modal virtual Rp25.000, trade pertama Rp5.000, SL 5%, TP 10%/15%,
  kill-switch 15% (lantai Rp21.250).
Kurs: USD/IDR live Frankfurter saat run; kalau data gagal diambil,
trade dilewati dan saldo tetap (tidak ada harga tebakan).
Nol order nyata; tidak ada akun/gateway di modul ini.
"""

import json
import os
import urllib.request

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LEDGER_PATH = os.path.join(BASE_DIR, "moomoo_ledger.json")
POSITION_PATH = os.path.join(BASE_DIR, "moomoo_position.json")
HISTORY_PATH = os.path.join(BASE_DIR, "moomoo_paper_history.jsonl")

VIRTUAL_START_IDR = 25000.0
FIRST_TRADE_IDR = 5000.0
SYMBOL = "AAPL"
SL_PCT = 0.05
TP1_PCT = 0.10
TP2_PCT = 0.15
KILL_SWITCH_PCT = 0.15

STOOQ_URL = None  # Stooq diblokir dari VM ini (halaman JS-check)
YAHOO_URL = "https://query1.finance.yahoo.com/v8/finance/chart/AAPL?range=5d&interval=1d"
FRANKFURTER_URL = "https://api.frankfurter.app/latest?from=USD&to=IDR"


def fetch_json(url):
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "trading-bot-demo/1.0"})
        with urllib.request.urlopen(req, timeout=20) as resp:
            return json.load(resp)
    except Exception:
        return None


def fetch_aapl_close():
    """Return (date, close_usd) terakhir dari Yahoo Finance, atau None."""
    try:
        req = urllib.request.Request(
            YAHOO_URL,
            headers={"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/120 Safari/537.36"})
        with urllib.request.urlopen(req, timeout=20) as resp:
            data = json.load(resp)
        res = data["chart"]["result"][0]
        closes = res["indicators"]["quote"][0]["close"]
        stamps = res["timestamp"]
        pairs = [(s, c) for s, c in zip(stamps, closes) if c is not None]
        if not pairs:
            return None
        stamp, close = pairs[-1]
        from datetime import datetime, timezone
        date = datetime.fromtimestamp(stamp, tz=timezone.utc).strftime("%Y-%m-%d")
        return (date, float(close))
    except Exception:
        return None


def load_json(path, default):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return default


def save_json(path, obj):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, indent=2, ensure_ascii=False)


def append_history(event):
    try:
        with open(HISTORY_PATH, "a", encoding="utf-8") as f:
            f.write(json.dumps(event, ensure_ascii=False) + "\n")
    except Exception:
        pass


def decide_exit(position, price_now, usd_idr_now, cash_idr):
    entry = position["entry_price_usd"]
    remaining = position["shares_remaining"]
    value_remaining = remaining * price_now * usd_idr_now
    if cash_idr + value_remaining <= VIRTUAL_START_IDR * (1.0 - KILL_SWITCH_PCT):
        return ("KILL_SWITCH", remaining)
    change = (price_now - entry) / entry
    if change <= -SL_PCT:
        return ("SL", remaining)
    if change >= TP2_PCT:
        return ("TP2", remaining)
    if change >= TP1_PCT and not position.get("tp1_done"):
        return ("TP1", remaining / 2.0)
    return ("HOLD", 0.0)


def main():
    fx = fetch_json(FRANKFURTER_URL)
    quote = fetch_aapl_close()
    ledger = load_json(LEDGER_PATH, {})
    position = load_json(POSITION_PATH, None)
    cash = float(ledger.get("cash_idr", VIRTUAL_START_IDR))
    if not fx or not quote:
        print("SKIP: data gagal diambil — trade dilewati, saldo tetap.")
        append_history({"event": "SKIP", "reason": "data_fetch_failed"})
        return
    usd_idr = float(fx["rates"]["IDR"])
    date, close = quote
    print(f"Harga acuan Yahoo Finance {date}: {SYMBOL} tutup ${close:.2f} (harian, komisi belum dimodelkan)")

    if position is None or position.get("status") == "CLOSED":
        shares = (FIRST_TRADE_IDR / usd_idr) / close
        position = {
            "symbol": SYMBOL,
            "side": "LONG",
            "status": "OPEN",
            "entry_price_usd": close,
            "entry_usd_idr": usd_idr,
            "shares_total": shares,
            "shares_remaining": shares,
            "cost_idr_total": FIRST_TRADE_IDR,
            "tp1_done": False,
            "realized_idr": 0.0,
        }
        cash -= FIRST_TRADE_IDR
        save_json(POSITION_PATH, position)
        print(f"OPEN: beli paper {shares:.4f} {SYMBOL} senilai Rp{FIRST_TRADE_IDR:.0f} @ ${close:.2f}")
        append_history({"event": "OPEN", "symbol": SYMBOL, "entry_price_usd": close,
                        "usd_idr": usd_idr, "cost_idr": FIRST_TRADE_IDR})
    else:
        action, sh_sell = decide_exit(position, close, usd_idr, cash)
        if action == "HOLD":
            value = position["shares_remaining"] * close * usd_idr
            change = (close - position["entry_price_usd"]) / position["entry_price_usd"]
            print(f"HOLD: posisi {position['shares_remaining']:.4f} {SYMBOL}, nilai Rp{value:.0f}, perubahan {change * 100:.2f}% (SL -5% / TP1 +10% / TP2 +15%)")
        else:
            proceeds = sh_sell * close * usd_idr
            cost_part = position["cost_idr_total"] * (sh_sell / position["shares_total"])
            pnl = proceeds - cost_part
            cash += proceeds
            position["shares_remaining"] -= sh_sell
            position["realized_idr"] += pnl
            if action == "TP1":
                position["tp1_done"] = True
                print(f"TP1: jual separuh {sh_sell:.4f} {SYMBOL} @ ${close:.2f} = Rp{proceeds:.0f}, P&L bagian Rp{pnl:.0f}")
            else:
                position["status"] = "CLOSED"
                print(f"{action}: jual seluruh sisa {sh_sell:.4f} {SYMBOL} @ ${close:.2f} = Rp{proceeds:.0f}, P&L Rp{pnl:.0f}, posisi CLOSED")
            append_history({"event": action, "symbol": SYMBOL, "shares_sold": sh_sell,
                            "price_usd": close, "proceeds_idr": proceeds, "pnl_idr": pnl})
            save_json(POSITION_PATH, position)

    ledger = {"symbol": SYMBOL, "cash_idr": round(cash, 2), "position": position,
              "price_usd": close, "price_date": date, "usd_idr": usd_idr,
              "source": "Yahoo Finance (harian) + Frankfurter"}
    save_json(LEDGER_PATH, ledger)
    print(json.dumps(ledger, ensure_ascii=False))


if __name__ == "__main__":
    main()
