#!/usr/bin/env python3
"""Bot trading demo — satu siklus paper 5 venue (TANPA uang asli).

Orkestrator: menjalankan modul paper tiap venue secara berurutan,
lalu mencetak ringkasan dari ledger/posisi masing-masing.
TIDAK ADA order nyata, TIDAK ADA key/secret dibaca, TIDAK ADA
deposit, TIDAK ADA penarikan. Semua modul paper memakai data publik
gratis; kalau satu venue gagal dicek, venue lain tetap jalan dan
kegagalannya dicatat (bot tidak berhenti total karena satu venue).

Siklus per venue:
- Indodax: indodax_paper.py (guard: tidak beli ulang selagi OPEN)
  + indodax_exit.py (TP/SL/kill-switch).
- Polymarket: paper_exit.py bila posisi OPEN; bila CLOSED/tidak ada,
  paper_trade.py dulu lalu paper_exit.py.
- Forex MT5: mt5_paper.py (data ECB harian).
- Moomoo: moomoo_paper.py (data Yahoo Finance harian).
- Pump.fun: pumpfun_paper.py (data DexScreener).

Aturan demo (sama di semua venue): modal virtual Rp25.000,
trade pertama Rp5.000, SL 5%, TP 10%/15% (Indodax: TP 3% jual habis),
kill-switch 15%.
Jalankan: python3 bot-engine/demo_bot.py
"""

import json
import os
import subprocess
import sys
from datetime import datetime

try:
    from zoneinfo import ZoneInfo
    WIB = ZoneInfo("Asia/Jakarta")
except Exception:
    WIB = None

BASE = os.path.dirname(os.path.abspath(__file__))
WS = os.path.dirname(BASE)
PY = sys.executable


def now_wib():
    now = datetime.now(WIB) if WIB else datetime.now()
    return now.strftime("%Y-%m-%d %H:%M WIB")


def run_step(name, script, cwd):
    """Jalankan satu modul, kembalikan (ok, output). Tidak raise."""
    try:
        r = subprocess.run([PY, script], cwd=cwd, capture_output=True,
                           text=True, timeout=180)
        out = (r.stdout or "") + (r.stderr or "")
        return (r.returncode == 0, out.strip())
    except Exception as e:
        return (False, f"GAGAL menjalankan {script}: {type(e).__name__}: {e}")


def read_json(path):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return None


def cumulative_realized(history_path):
    """Jumlah P&L terealisasi kumulatif venue dari file riwayat.

    Hanya baris yang membawa pnl_idr (event EXIT/SL/TP) yang dijumlah;
    event OPEN/SKIP/CORRECTION tidak membawa pnl_idr sehingga otomatis
    terlewat. Bila file tidak ada, kembalian 0.0 (bukan error).
    """
    total = 0.0
    try:
        with open(history_path, "r", encoding="utf-8") as f:
            for line in f:
                try:
                    rec = json.loads(line)
                except ValueError:
                    continue
                pnl = rec.get("pnl_idr")
                if isinstance(pnl, (int, float)):
                    total += pnl
    except OSError:
        pass
    return round(total, 2)


def poly_status():
    pos = read_json(os.path.join(WS, "polymarket-bot", "paper_position.json"))
    if not pos:
        return ("-", "-", "-")
    cum = cumulative_realized(os.path.join(WS, "polymarket-bot",
                                           "paper_history.jsonl"))
    return (pos.get("status", "-"), pos.get("cash_idr", "-"), cum)


def indodax_status():
    pos = read_json(os.path.join(WS, "indodax-bot", "indodax_position.json"))
    if not pos:
        return ("-", "-", "-")
    cum = cumulative_realized(os.path.join(WS, "indodax-bot",
                                           "indodax_history.jsonl"))
    return (pos.get("status", "-"), pos.get("cash_idr", "-"), cum)


def ledger_status(venue_dir, ledger_name, history_name):
    led = read_json(os.path.join(WS, venue_dir, ledger_name))
    if not led:
        return ("-", "-", "-")
    pos = led.get("position") or {}
    cum = cumulative_realized(os.path.join(WS, venue_dir, history_name))
    return (pos.get("status", "-"), led.get("cash_idr", "-"), cum)


def main():
    print("=" * 60)
    print("BOT TRADING DEMO — SIKLUS PAPER 5 VENUE")
    print(f"Waktu: {now_wib()}")
    print("Mode: PAPER SAJA. Nol order nyata, nol deposit, nol penarikan.")
    print("=" * 60)
    failed = []

    print("\n[1/5] Indodax spot")
    for script in ("indodax_paper.py", "indodax_exit.py"):
        ok, out = run_step("Indodax", os.path.join(WS, "indodax-bot", script),
                           os.path.join(WS, "indodax-bot"))
        print(out if out else f"({script}: tanpa output)")
        if not ok:
            failed.append(f"Indodax/{script}")

    print("\n[2/5] Polymarket")
    pos = read_json(os.path.join(WS, "polymarket-bot", "paper_position.json"))
    steps = ["paper_exit.py"]
    if not pos or pos.get("status") not in ("OPEN", "PARTIAL"):
        steps = ["paper_trade.py", "paper_exit.py"]
    for script in steps:
        ok, out = run_step("Polymarket", os.path.join(WS, "polymarket-bot", script),
                           os.path.join(WS, "polymarket-bot"))
        print(out if out else f"({script}: tanpa output)")
        if not ok:
            failed.append(f"Polymarket/{script}")

    print("\n[3/5] Forex MT5")
    ok, out = run_step("MT5", os.path.join(WS, "forex-mt5", "mt5_paper.py"),
                       os.path.join(WS, "forex-mt5"))
    print(out if out else "(mt5_paper.py: tanpa output)")
    if not ok:
        failed.append("MT5/mt5_paper.py")

    print("\n[4/5] Moomoo")
    ok, out = run_step("Moomoo", os.path.join(WS, "moomoo-bot", "moomoo_paper.py"),
                       os.path.join(WS, "moomoo-bot"))
    print(out if out else "(moomoo_paper.py: tanpa output)")
    if not ok:
        failed.append("Moomoo/moomoo_paper.py")

    print("\n[5/5] Pump.fun")
    ok, out = run_step("Pump.fun", os.path.join(WS, "pumpfun-bot", "pumpfun_paper.py"),
                       os.path.join(WS, "pumpfun-bot"))
    print(out if out else "(pumpfun_paper.py: tanpa output)")
    if not ok:
        failed.append("Pump.fun/pumpfun_paper.py")

    rows = [
        ("Indodax",) + indodax_status(),
        ("Polymarket",) + poly_status(),
        ("Forex MT5",) + ledger_status("forex-mt5", "mt5_ledger.json",
                                       "mt5_paper_history.jsonl"),
        ("Moomoo",) + ledger_status("moomoo-bot", "moomoo_ledger.json",
                                    "moomoo_paper_history.jsonl"),
        ("Pump.fun",) + ledger_status("pumpfun-bot", "pumpfun_ledger.json",
                                      "pumpfun_paper_history.jsonl"),
    ]
    print("\n" + "=" * 60)
    print("RINGKASAN SIKLUS (kas saat ini + terealisasi kumulatif venue)")
    print(f"{'Venue':<12} {'Status':<8} {'Kas (Rp)':>12} {'Terealisasi (Rp)':>16}")
    for venue, status, cash, realized in rows:
        cash_s = f"{cash:,.0f}" if isinstance(cash, (int, float)) else str(cash)
        real_s = f"{realized:,.0f}" if isinstance(realized, (int, float)) else str(realized)
        print(f"{venue:<12} {str(status):<8} {cash_s:>12} {real_s:>16}")
    if failed:
        print(f"\nVenue/modul yang gagal dicek ({len(failed)}): {', '.join(failed)}")
        print("Siklus tetap selesai; perbaiki modul tersebut sebelum siklus berikut.")
    else:
        print("\nSemua venue berhasil dicek.")
    print("Deposit tetap TERKUNCI: demo belum memenuhi kriteria berhasil penuh.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
