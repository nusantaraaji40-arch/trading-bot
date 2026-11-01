#!/usr/bin/env python3
"""Backtest MT5 EURUSD (demo, tanpa uang asli) + grid percobaan.

Mesin percobaan untuk tuntutan 'puluhan ribu percobaan': satu modul
ini menjalankan strategi tangga SL/TP di data historis harian gratis
Frankfurter (ECB, tanpa key) dan mengulanginya di grid parameter.
Grid kecil di sini (SL x TP1 x TP2) membuktikan mekanik sweep; skala
ke puluhan ribu dicapai dengan menambah pair, jendela walk-forward,
dan kombinasi parameter — bukan dengan mengubah hasil.

Batas kejujuran: data hanya harga TUTUP harian (sentuhan SL/TP di
tengah hari tidak tertangkap), harga mid (spread/fee/swap tidak
dimodelkan), satu pair (EURUSD). Walk-forward 70/30 dipakai supaya
parameter terbaik di latih diuji lagi di data yang belum dilihat —
parameter yang hanya bagus di latih = overfitting, bukan keberhasilan.
"""

import json
import os
import urllib.request

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
RESULT_PATH = os.path.join(BASE_DIR, "mt5_backtest_result.json")

START = "2025-01-01"
END = "2026-10-30"
URL = (f"https://api.frankfurter.app/{START}..{END}"
       "?from=USD&to=EUR,IDR")
CASH_START = 25000.0
TRADE_IDR = 5000.0
KS_FLOOR = CASH_START * 0.85
FIXED = (0.05, 0.10, 0.15)
GRID_SL = (0.03, 0.05, 0.07)
GRID_TP1 = (0.05, 0.10, 0.15)
GRID_TP2 = (0.10, 0.15, 0.20)


def fetch_days():
    req = urllib.request.Request(URL, headers={"User-Agent": "trading-bot-demo/1.0"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        data = json.load(resp)
    days = []
    for date in sorted(data["rates"]):
        r = data["rates"][date]
        eur_usd = 1.0 / float(r["EUR"])
        days.append((date, eur_usd, float(r["IDR"])))
    return days


def simulate(days, sl, tp1, tp2):
    """Satu run strategi di urutan hari. Return metrik + daftar trade."""
    cash = CASH_START
    trades = []
    peak = CASH_START
    max_dd = 0.0
    open_pos = None  # (entry_eurusd, entry_usd_idr, eur_remaining, eur_total, tp1_done, cost_idr)
    i = 0
    while i < len(days):
        date, eurusd, usd_idr = days[i]
        equity = cash + (open_pos[2] * eurusd * usd_idr if open_pos else 0.0)
        peak = max(peak, equity)
        max_dd = max(max_dd, (peak - equity) / peak if peak else 0.0)
        if open_pos is None:
            eur = (TRADE_IDR / usd_idr) / eurusd
            open_pos = (eurusd, usd_idr, eur, eur, False, TRADE_IDR)
            cash -= TRADE_IDR
            i += 1
            continue
        entry, _, remaining, total, tp1_done, cost = open_pos
        change = (eurusd - entry) / entry
        action = None
        if equity <= KS_FLOOR:
            action = "KILL_SWITCH"
        elif change <= -sl:
            action = "SL"
        elif change >= tp2:
            action = "TP2"
        elif change >= tp1 and not tp1_done:
            action = "TP1"
        if action is None:
            i += 1
            continue
        sell = remaining if action != "TP1" else remaining / 2.0
        proceeds = sell * eurusd * usd_idr
        pnl = proceeds - cost * (sell / total)
        cash += proceeds
        remaining -= sell
        trades.append({"event": action, "date": date, "pnl_idr": round(pnl, 2)})
        if action == "TP1":
            open_pos = (entry, open_pos[1], remaining, total, True, cost)
            i += 1
        else:
            open_pos = None
            if action == "KILL_SWITCH":
                break
            i += 1
    if open_pos is not None:
        date, eurusd, usd_idr = days[-1]
        entry, _, remaining, total, _, cost = open_pos
        proceeds = remaining * eurusd * usd_idr
        pnl = proceeds - cost * (remaining / total)
        cash += proceeds
        trades.append({"event": "TIME_EXIT", "date": date, "pnl_idr": round(pnl, 2)})
    closed = [t for t in trades if t["event"] != "TP1"]
    wins = sum(1 for t in closed if t["pnl_idr"] > 0)
    total_pnl = round(sum(t["pnl_idr"] for t in trades), 2)
    return {
        "trades": len(closed),
        "events": len(trades),
        "wins": wins,
        "win_rate": round(wins / len(closed), 4) if closed else 0.0,
        "total_pnl_idr": total_pnl,
        "final_equity": round(cash, 2),
        "max_drawdown": round(max_dd, 4),
        "time_exits": sum(1 for t in trades if t["event"] == "TIME_EXIT"),
    }


def main():
    days = fetch_days()
    print(f"Data: {len(days)} hari bursa ({days[0][0]} s/d {days[-1][0]}).")
    cut = int(len(days) * 0.7)
    train, test = days[:cut], days[cut:]
    print(f"Walk-forward: latih {len(train)} hari, uji {len(test)} hari.")
    result = {"days": len(days), "train_days": len(train), "test_days": len(test)}
    for name, seg in (("train", train), ("test", test), ("overall", days)):
        result["fixed_" + name] = simulate(seg, *FIXED)
        print(f"Strategi tetap SL 5%/TP 10%/15% [{name}]: "
              f"{result['fixed_' + name]['trades']} trade, "
              f"win rate {result['fixed_' + name]['win_rate'] * 100:.1f}%, "
              f"P&L Rp{result['fixed_' + name]['total_pnl_idr']:,.0f}, "
              f"drawdown maks {result['fixed_' + name]['max_drawdown'] * 100:.1f}%.")
    grid = []
    for sl in GRID_SL:
        for tp1 in GRID_TP1:
            for tp2 in GRID_TP2:
                if tp2 <= tp1:
                    continue
                m_train = simulate(train, sl, tp1, tp2)
                m_test = simulate(test, sl, tp1, tp2)
                grid.append({"sl": sl, "tp1": tp1, "tp2": tp2,
                             "train_pnl": m_train["total_pnl_idr"],
                             "test_pnl": m_test["total_pnl_idr"],
                             "test_trades": m_test["trades"]})
    best_train = max(grid, key=lambda g: g["train_pnl"])
    best_test = max(grid, key=lambda g: g["test_pnl"])
    print(f"Grid {len(grid)} kombinasi: terbaik-latih SL {best_train['sl']*100:.0f}%/"
          f"TP1 {best_train['tp1']*100:.0f}%/TP2 {best_train['tp2']*100:.0f}% "
          f"(P&L latih Rp{best_train['train_pnl']:,.0f}, P&L uji Rp{best_train['test_pnl']:,.0f}); "
          f"terbaik-uji SL {best_test['sl']*100:.0f}%/TP1 {best_test['tp1']*100:.0f}%/"
          f"TP2 {best_test['tp2']*100:.0f}% (P&L uji Rp{best_test['test_pnl']:,.0f}).")
    if (best_train["sl"], best_train["tp1"], best_train["tp2"]) != \
       (best_test["sl"], best_test["tp1"], best_test["tp2"]):
        print("Peringatan overfitting: parameter terbaik di latih BERBEDA "
              "dengan yang terbaik di uji — jangan pakai parameter latih "
              "mentah-mentah untuk live.")
    result["grid"] = grid
    result["best_train"] = best_train
    result["best_test"] = best_test
    with open(RESULT_PATH, "w") as f:
        json.dump(result, f, indent=2)
    print(f"Hasil lengkap: {RESULT_PATH}")


if __name__ == "__main__":
    main()
