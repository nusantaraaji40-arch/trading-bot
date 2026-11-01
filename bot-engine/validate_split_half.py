#!/usr/bin/env python3
"""Validasi split-half param Forex dari sweep_backtest.py.

Tujuan: menjawab apakah 92 param yang lolos di sweep itu robust atau
kebetulan (multiple-testing: 154 param dicoba, sebagian lolos bisa
jadi noise). Caranya: tiap deret Forex dibagi dua jendela (paruh awal
= seleksi, paruh akhir = validasi yang TIDAK dipakai memilih param).
Param yang lolos di paruh seleksi diuji lagi di paruh validasi.
Kriteria sama: P&L > 0, drawdown maks < 10%, trade >= 25 per paruh
(sebanding dengan >= 50 untuk seluruh jendela).

Batas: validasi masih data historis yang sama (bukan data masa depan
yang belum dilihat); validasi masa depan sejati menunggu data baru
(Kurs ECB Senin, data intraday terminal).
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from sweep_backtest import PARAMS, forex_series, simulate, windows


def aggregate(series, win_list, params):
    agg = {}
    for label, days in series.items():
        wins = win_list(days)
        for train, test in wins:
            for sl, tp1, tp2 in params:
                m = simulate(test, sl, tp1, tp2)
                a = agg.setdefault((sl, tp1, tp2), {"pnl": 0.0, "trades": 0,
                                                   "wins": 0, "max_dd": 0.0})
                a["pnl"] += m["total_pnl_idr"]
                a["trades"] += m["trades"]
                a["wins"] += m["wins"]
                a["max_dd"] = max(a["max_dd"], m["max_drawdown"])
    return agg


def passes(a, min_trades):
    return a["pnl"] > 0 and a["max_dd"] < 0.10 and a["trades"] >= min_trades


def main():
    series = forex_series()
    print(f"Deret Forex: {len(series)} pair.")
    sel = aggregate(series, lambda d: windows(d)[:len(windows(d)) // 2], PARAMS)
    val = aggregate(series, lambda d: windows(d)[len(windows(d)) // 2:], PARAMS)
    selected = {k: v for k, v in sel.items() if passes(v, 25)}
    print(f"Paruh seleksi: {len(selected)} param lolos dari {len(PARAMS)}.")
    survived = []
    for k, s in selected.items():
        v = val[k]
        if passes(v, 25):
            survived.append((k, s, v))
    print(f"Paruh validasi: {len(survived)} dari {len(selected)} param seleksi "
          f"tetap lolos ({len(survived) / len(selected) * 100:.0f}% bila ada).")
    for (sl, tp1, tp2), s, v in sorted(survived, key=lambda x: x[2]["pnl"],
                                       reverse=True)[:10]:
        print(f"  SURVIVE SL {sl*100:.0f}%/TP1 {tp1*100:.0f}%/TP2 {tp2*100:.0f}%: "
              f"seleksi P&L Rp{s['pnl']:,.0f} ({s['trades']} trade, DD {s['max_dd']*100:.1f}%) | "
              f"validasi P&L Rp{v['pnl']:,.0f} ({v['trades']} trade, DD {v['max_dd']*100:.1f}%)")
    if not survived:
        print("  Tidak ada param seleksi yang bertahan di validasi — "
              "lolos sweep kemungkinan besar kebetulan (overfitting seleksi).")


if __name__ == "__main__":
    main()
