#!/usr/bin/env python3
"""Sweep backtest multi-venue: puluhan ribu percobaan strategi tangga SL/TP.

Venue dengan deret historis gratis: Forex (Frankfurter, 7 pair USD),
saham AS (Yahoo Finance, 7 simbol), kripto (CoinGecko vs IDR, 2 koin —
PROXY untuk pair Indodax, bukan order book Indodax).
Polymarket dan Pump.fun TIDAK ikut sweep: tidak ada deret historis
gratis untuk keduanya; demonya adalah modul paper live (harga live,
bukan backtest).

Mekanik strategi SAMA PERSIS dengan forex-mt5/mt5_backtest.py
(simulate): trade berurutan, modal virtual Rp25.000 per jendela,
trade Rp5.000, TP1 jual separuh, TP2/SL/Kill-switch jual sisa,
TIME_EXIT menutup posisi terbuka di akhir jendela.
Jendela walk-forward: latih 250 hari bursa, uji 60 hari, geser 60 hari.
Grid: SL {2,3,4,5,6,7,8}% x TP1 {3,5,7,10,12,15}% x TP2 {6,10,15,20,25}%
dengan TP2>TP1 = 154 kombinasi.
Kriteria LOLOS per venue: P&L uji > 0 DAN drawdown maks uji < 10% DAN
trade uji >= 50 (sampel bermakna). Parameter terbaik-latih yang beda
dengan terbaik-uji = overfitting, bukan keberhasilan.

Batas kejujuran: harga TUTUP harian saja (sentuhan SL/TP intraday
tidak tertangkap), harga mid (spread/fee/swap/komisi tidak dimodelkan).
"""

import json
import os
import urllib.request
from datetime import datetime, timezone

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
RESULT_PATH = os.path.join(BASE_DIR, "sweep_backtest_result.json")

CASH_START = 25000.0
TRADE_IDR = 5000.0
KS_FLOOR = CASH_START * 0.85
TRAIN_DAYS = 250
TEST_DAYS = 60
STEP_DAYS = 60

GRID_SL = (0.02, 0.03, 0.04, 0.05, 0.06, 0.07, 0.08)
GRID_TP1 = (0.03, 0.05, 0.07, 0.10, 0.12, 0.15)
GRID_TP2 = (0.06, 0.10, 0.15, 0.20, 0.25)
PARAMS = [(sl, tp1, tp2) for sl in GRID_SL for tp1 in GRID_TP1
          for tp2 in GRID_TP2 if tp2 > tp1]

UA = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/120 Safari/537.36"}


def fetch_json(url, timeout=30):
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.load(resp)


def simulate(days, sl, tp1, tp2):
    """Satu run strategi di urutan (tanggal, harga, fx). days: list
    (date, price, fx) dengan nilai posisi = unit * price * fx."""
    cash = CASH_START
    trades = []
    peak = CASH_START
    max_dd = 0.0
    open_pos = None
    i = 0
    while i < len(days):
        date, price, fx = days[i]
        equity = cash + (open_pos[2] * price * fx if open_pos else 0.0)
        peak = max(peak, equity)
        max_dd = max(max_dd, (peak - equity) / peak if peak else 0.0)
        if open_pos is None:
            units = (TRADE_IDR / fx) / price
            open_pos = (price, units, units, False, TRADE_IDR)
            cash -= TRADE_IDR
            i += 1
            continue
        entry, remaining, total, tp1_done, cost = open_pos
        change = (price - entry) / entry
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
        proceeds = sell * price * fx
        pnl = proceeds - cost * (sell / total)
        cash += proceeds
        remaining -= sell
        trades.append({"event": action, "date": date, "pnl_idr": round(pnl, 2)})
        if action == "TP1":
            open_pos = (entry, remaining, total, True, cost)
            i += 1
        else:
            open_pos = None
            if action == "KILL_SWITCH":
                break
            i += 1
    if open_pos is not None:
        date, price, fx = days[-1]
        entry, remaining, total, _, cost = open_pos
        proceeds = remaining * price * fx
        pnl = proceeds - cost * (remaining / total)
        cash += proceeds
        trades.append({"event": "TIME_EXIT", "date": date, "pnl_idr": round(pnl, 2)})
    closed = [t for t in trades if t["event"] != "TP1"]
    wins = sum(1 for t in closed if t["pnl_idr"] > 0)
    return {"trades": len(closed), "wins": wins,
            "total_pnl_idr": round(sum(t["pnl_idr"] for t in trades), 2),
            "max_drawdown": round(max_dd, 4)}


def windows(days):
    """Daftar (train, test) dari deret penuh."""
    out = []
    start = 0
    while start + TRAIN_DAYS + TEST_DAYS <= len(days):
        out.append((days[start:start + TRAIN_DAYS],
                    days[start + TRAIN_DAYS:start + TRAIN_DAYS + TEST_DAYS]))
        start += STEP_DAYS
    return out


def sweep_venue(name, series):
    """series: dict label -> list (date, price, fx). Return ringkasan."""
    agg = {}
    n_windows = 0
    for label, days in series.items():
        wins = windows(days)
        n_windows = max(n_windows, len(wins))
        for train, test in wins:
            for sl, tp1, tp2 in PARAMS:
                m_train = simulate(train, sl, tp1, tp2)
                m_test = simulate(test, sl, tp1, tp2)
                key = (sl, tp1, tp2)
                a = agg.setdefault(key, {"train_pnl": 0.0, "test_pnl": 0.0,
                                         "test_trades": 0, "test_wins": 0,
                                         "test_max_dd": 0.0})
                a["train_pnl"] += m_train["total_pnl_idr"]
                a["test_pnl"] += m_test["total_pnl_idr"]
                a["test_trades"] += m_test["trades"]
                a["test_wins"] += m_test["wins"]
                a["test_max_dd"] = max(a["test_max_dd"], m_test["max_drawdown"])
    rows = [{"sl": k[0], "tp1": k[1], "tp2": k[2], **v} for k, v in agg.items()]
    trials = len(series) * n_windows * len(PARAMS) if series else 0
    best_train = max(rows, key=lambda r: r["train_pnl"]) if rows else None
    best_test = max(rows, key=lambda r: r["test_pnl"]) if rows else None
    passed = [r for r in rows if r["test_pnl"] > 0 and r["test_max_dd"] < 0.10
              and r["test_trades"] >= 50]
    return {"series": len(series), "windows_per_series": n_windows,
            "params": len(PARAMS), "trials": trials, "grid": rows,
            "best_train": best_train, "best_test": best_test,
            "passed": passed}


def forex_series():
    data = fetch_json("https://api.frankfurter.app/2020-01-01..2026-10-30"
                      "?from=EUR&to=USD,GBP,JPY,CHF,AUD,CAD,NZD,IDR")
    rates = data["rates"]
    dates = sorted(rates)
    usd_idr = {}
    for d in dates:
        r = rates[d]
        usd_idr[d] = float(r["IDR"]) / float(r["USD"])
    out = {name: [] for name in
           ("EURUSD", "GBPUSD", "USDJPY", "USDCHF", "AUDUSD", "USDCAD", "NZDUSD")}
    for d in dates:
        r = rates[d]
        usd, gbp, jpy = float(r["USD"]), float(r["GBP"]), float(r["JPY"])
        chf, aud, cad, nzd = float(r["CHF"]), float(r["AUD"]), float(r["CAD"]), float(r["NZD"])
        vals = {"EURUSD": usd, "GBPUSD": usd / gbp, "USDJPY": jpy / usd,
                "USDCHF": chf / usd, "AUDUSD": usd / aud, "USDCAD": cad / usd,
                "NZDUSD": usd / nzd}
        for name, price in vals.items():
            out[name].append((d, price, usd_idr[d]))
    return out


def stock_series():
    symbols = ["AAPL", "MSFT", "NVDA", "GOOGL", "AMZN", "META", "TSLA"]
    fx_data = fetch_json("https://api.frankfurter.app/2020-01-01..2026-10-30"
                         "?from=EUR&to=USD,IDR")
    fx_dates = sorted(fx_data["rates"])
    fx_map = {}
    for d in fx_dates:
        r = fx_data["rates"][d]
        fx_map[d] = float(r["IDR"]) / float(r["USD"])
    out = {}
    for sym in symbols:
        data = fetch_json(f"https://query1.finance.yahoo.com/v8/finance/chart/{sym}"
                          "?range=5y&interval=1d")
        res = data["chart"]["result"][0]
        closes = res["indicators"]["quote"][0]["close"]
        stamps = res["timestamp"]
        days = []
        last_fx = None
        for s, c in zip(stamps, closes):
            if c is None:
                continue
            date = datetime.fromtimestamp(s, tz=timezone.utc).strftime("%Y-%m-%d")
            fx = fx_map.get(date, last_fx)
            if fx is None:
                continue
            last_fx = fx
            days.append((date, float(c), fx))
        days.sort()
        out[sym] = days
    return out


def crypto_series():
    out = {}
    for coin in ("bitcoin", "ethereum"):
        # CoinGecko gratis membatasi rentang historis (401 error 10012
        # untuk 1825 hari); 365 hari adalah batas tier publik.
        data = fetch_json(f"https://api.coingecko.com/api/v3/coins/{coin}/market_chart"
                          "?vs_currency=idr&days=365&interval=daily")
        days = []
        for ms, price in data["prices"]:
            date = datetime.fromtimestamp(ms / 1000, tz=timezone.utc).strftime("%Y-%m-%d")
            days.append((date, float(price), 1.0))
        days.sort()
        out[coin] = days
    return out


def main():
    result = {"params": len(PARAMS), "venues": {}}
    total_trials = 0
    for name, loader in (("forex", forex_series), ("stocks", stock_series),
                         ("crypto_proxy_indodax", crypto_series)):
        try:
            series = loader()
        except Exception as e:
            print(f"{name}: data gagal diambil ({type(e).__name__}) — venue dilewati.")
            result["venues"][name] = {"skipped": True, "error": type(e).__name__}
            continue
        summary = sweep_venue(name, series)
        result["venues"][name] = summary
        total_trials += summary["trials"]
        bt = summary["best_test"]
        print(f"{name}: {summary['series']} deret x {summary['windows_per_series']} jendela "
              f"x {summary['params']} param = {summary['trials']} percobaan; "
              f"terbaik-uji SL {bt['sl']*100:.0f}%/TP1 {bt['tp1']*100:.0f}%/TP2 {bt['tp2']*100:.0f}% "
              f"(P&L uji Rp{bt['test_pnl']:,.0f}, {bt['test_trades']} trade, "
              f"DD {bt['test_max_dd']*100:.1f}%) — LOLOS: {len(summary['passed'])} param.")
    result["total_trials"] = total_trials
    print(f"TOTAL percobaan: {total_trials}")
    with open(RESULT_PATH, "w") as f:
        json.dump(result, f, indent=2)
    print(f"Hasil lengkap: {RESULT_PATH}")


if __name__ == "__main__":
    main()
