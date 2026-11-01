#!/usr/bin/env python3
"""Paper trading Forex MT5 (demo, tanpa uang asli).

Jalur demo track Forex yang dipilih pemilik: MT5. Modul ini berjalan di
data acuan publik gratis (Frankfurter / referensi harian ECB, tanpa key)
sampai jembatan terminal MT5 hidup — lihat MT5_BRIDGE.md. Bukan tick
real-time MT5, dan spread/slippage live belum dimodelkan (harga mid).

Aturan demo (sama seperti venue lain, dalam rupiah):
  modal virtual Rp25.000, trade pertama Rp5.000, SL 5%, TP 10%/15%,
  kill-switch 15% dari total modal (lantai Rp21.250).
Aturan kurs: harga non-IDR dikonversi ke rupiah memakai kurs live saat
run (Frankfurter USD/IDR); kalau kurs gagal diambil, paper trade
dilewati dan saldo tetap (tidak ada kurs tebakan).
Nol order nyata; tidak ada koneksi ke terminal/broker di modul ini.
"""

import json
import os
import urllib.request

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LEDGER_PATH = os.path.join(BASE_DIR, "mt5_ledger.json")
POSITION_PATH = os.path.join(BASE_DIR, "mt5_position.json")
HISTORY_PATH = os.path.join(BASE_DIR, "mt5_paper_history.jsonl")

VIRTUAL_START_IDR = 25000.0
FIRST_TRADE_IDR = 5000.0
PAIR = "EURUSD"
SL_PCT = 0.05
TP1_PCT = 0.10
TP2_PCT = 0.15
KILL_SWITCH_PCT = 0.15

FRANKFURTER_URL = "https://api.frankfurter.app/latest?from=USD&to=EUR,JPY,IDR"


def fetch_rates():
    """Return (eurusd, usd_idr, date) atau None kalau fetch gagal."""
    try:
        req = urllib.request.Request(
            FRANKFURTER_URL, headers={"User-Agent": "trading-bot-demo/1.0"}
        )
        with urllib.request.urlopen(req, timeout=20) as resp:
            data = json.load(resp)
        rates = data["rates"]
        usd_eur = float(rates["EUR"])
        usd_idr = float(rates["IDR"])
        if usd_eur <= 0 or usd_idr <= 0:
            return None
        return (1.0 / usd_eur, usd_idr, data.get("date"))
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


def decide_exit(position, eurusd_now, usd_idr_now, cash_idr):
    """Prioritas: kill-switch > SL > TP2 > TP1. Return (action, eur_to_sell)."""
    entry = position["entry_eurusd"]
    remaining = position["eur_remaining"]
    value_remaining = remaining * eurusd_now * usd_idr_now
    total_value = cash_idr + value_remaining
    if total_value <= VIRTUAL_START_IDR * (1.0 - KILL_SWITCH_PCT):
        return ("KILL_SWITCH", remaining)
    change = (eurusd_now - entry) / entry
    if change <= -SL_PCT:
        return ("SL", remaining)
    if change >= TP2_PCT:
        return ("TP2", remaining)
    if change >= TP1_PCT and not position.get("tp1_done"):
        return ("TP1", remaining / 2.0)
    return ("HOLD", 0.0)


def main():
    rates = fetch_rates()
    ledger = load_json(LEDGER_PATH, {})
    position = load_json(POSITION_PATH, None)
    cash = float(ledger.get("cash_idr", VIRTUAL_START_IDR))

    if rates is None:
        print("SKIP: kurs Frankfurter gagal diambil — trade dilewati, saldo tetap.")
        print(json.dumps({"cash_idr": cash, "position": position}, ensure_ascii=False))
        append_history({"event": "SKIP", "reason": "rate_fetch_failed"})
        return

    eurusd, usd_idr, rate_date = rates
    print(f"Kurs acuan ECB {rate_date}: EURUSD {eurusd:.5f}, USD/IDR {usd_idr:.2f} (mid, spread belum dimodelkan)")

    if position is None or position.get("status") == "CLOSED":
        usd_amount = FIRST_TRADE_IDR / usd_idr
        eur_amount = usd_amount / eurusd
        position = {
            "pair": PAIR,
            "side": "LONG",
            "status": "OPEN",
            "entry_eurusd": eurusd,
            "entry_usd_idr": usd_idr,
            "eur_total": eur_amount,
            "eur_remaining": eur_amount,
            "cost_idr_total": FIRST_TRADE_IDR,
            "tp1_done": False,
            "realized_idr": 0.0,
        }
        cash -= FIRST_TRADE_IDR
        save_json(POSITION_PATH, position)
        print(f"OPEN: beli paper {eur_amount:.2f} EUR ({PAIR}) senilai Rp{FIRST_TRADE_IDR:.0f} @ {eurusd:.5f}")
        append_history({"event": "OPEN", "pair": PAIR, "entry_eurusd": eurusd,
                        "usd_idr": usd_idr, "cost_idr": FIRST_TRADE_IDR})
    else:
        action, eur_sell = decide_exit(position, eurusd, usd_idr, cash)
        if action == "HOLD":
            value = position["eur_remaining"] * eurusd * usd_idr
            change = (eurusd - position["entry_eurusd"]) / position["entry_eurusd"]
            print(f"HOLD: posisi {position['eur_remaining']:.2f} EUR, nilai Rp{value:.0f}, perubahan {change * 100:.2f}% (SL -5% / TP1 +10% / TP2 +15%)")
        else:
            proceeds = eur_sell * eurusd * usd_idr
            cost_part = position["cost_idr_total"] * (eur_sell / position["eur_total"])
            pnl = proceeds - cost_part
            cash += proceeds
            position["eur_remaining"] -= eur_sell
            position["realized_idr"] += pnl
            if action == "TP1":
                position["tp1_done"] = True
                print(f"TP1: jual separuh {eur_sell:.2f} EUR @ {eurusd:.5f} = Rp{proceeds:.0f}, P&L bagian Rp{pnl:.0f}")
                append_history({"event": "TP1", "eur_sold": eur_sell, "price": eurusd, "proceeds_idr": proceeds, "pnl_idr": pnl})
            else:
                position["status"] = "CLOSED"
                print(f"{action}: jual seluruh sisa {eur_sell:.2f} EUR @ {eurusd:.5f} = Rp{proceeds:.0f}, P&L Rp{pnl:.0f}, posisi CLOSED")
                append_history({"event": action, "eur_sold": eur_sell, "price": eurusd, "proceeds_idr": proceeds, "pnl_idr": pnl})
            save_json(POSITION_PATH, position)

    ledger = {
        "pair": PAIR,
        "cash_idr": round(cash, 2),
        "position": position,
        "eurusd": eurusd,
        "usd_idr": usd_idr,
        "rate_date": rate_date,
        "source": "Frankfurter (ECB harian, mid)",
    }
    save_json(LEDGER_PATH, ledger)
    print(json.dumps(ledger, ensure_ascii=False))


if __name__ == "__main__":
    main()
