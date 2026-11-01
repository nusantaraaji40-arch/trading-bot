#!/usr/bin/env python3
"""Tes DESK BRO v1 — tanpa jaringan, tanpa uang nyata.

Jalankan: python3 desk/test_bro_desk.py
Semua cek harus PASS. Bila satu gagal, skrip berhenti dengan
AssertionError dan nama cek yang gagal.
"""

import os
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bro_desk as desk

GOOD = {"question": "Contoh market?", "active": True, "closed": False,
        "liquidity": 5000.0, "conditionId": "cond-1",
        "outcomePrices": ["0.05", "0.95"]}


def check(name, cond):
    assert cond, "GAGAL: " + name
    print("PASS: " + name)


def main():
    # 1. Bro 3 menolak likuiditas rendah.
    low = dict(GOOD, liquidity=100.0)
    ok, _ = desk.vet_market(low)
    check("Bro 3 menolak likuiditas < $500", not ok)

    # 2. Bro 3 meloloskan market yang memenuhi syarat.
    ok, _ = desk.vet_market(GOOD)
    check("Bro 3 meloloskan market bagus", ok)

    # 3. Bro 3 menolak market yang sudah tutup.
    closed = dict(GOOD, closed=True)
    ok, _ = desk.vet_market(closed)
    check("Bro 3 menolak market tutup", not ok)

    # 4. Bro 5 membatasi ke anggaran trade pertama (Rp5.000).
    shares = desk.size_trade(25000, 900.0)
    check("Bro 5: Rp5.000 / Rp900 = 5 lembar", shares == 5)

    # 5. Bro 5 mengembalikan 0 bila di bawah minimum 5 lembar.
    check("Bro 5: 0 bila < 5 lembar", desk.size_trade(25000, 2000.0) == 0)

    # 6. Bro 7 memicu SL saat ask turun 5% atau lebih.
    check("Bro 7: SL pada -5%",
          desk.risk_decision(0.05, 0.0475, 0.047, 25000, 1000.0) == "SL")

    # 7. Bro 7 memicu TP saat ask naik 15% atau lebih.
    check("Bro 7: TP pada +15%",
          desk.risk_decision(0.05, 0.0575, 0.057, 25000, 1000.0) == "TP")

    # 8. Bro 7: kill-switch menang atas SL bila total <= Rp21.250.
    check("Bro 7: kill-switch mengalahkan SL",
          desk.risk_decision(0.05, 0.0475, 0.047, 20000, 1000.0)
          == "KILL_SWITCH")

    # 9. Bro 1 NO_TRADE bila satu gerbang gagal (mis. sentimen buruk).
    verdict, _ = desk.chief_decision(
        {"scanned": True, "vetted": True, "social_ok": False,
         "sized": True, "no_open": True, "data_ok": True})
    check("Bro 1: NO_TRADE bila sentimen buruk", verdict == "NO_TRADE")

    # 10. Bro 4: skor negatif untuk headline buruk, positif untuk baik.
    check("Bro 4: skor sentimen",
          desk.social_score(["Harga naik, rekor baru"])
          > desk.social_score(["Scam rug, harga crash"]))

    # 11. Siklus penuh paper (data injeksi, tanpa jaringan): beli lalu TP.
    with tempfile.TemporaryDirectory() as tmp:
        state_path = os.path.join(tmp, "ledger.json")
        market = dict(GOOD)
        report = desk.run_cycle(state_path, markets=[market], rate=18000.0,
                                headlines=[])
        check("Siklus beli: BUY_PAPER", report["action"] == "BUY_PAPER")
        state = desk.load_state(state_path)
        check("Ledger: posisi OPEN 5 lembar",
              state["position"] is not None
              and state["position"]["shares"] == 5)
        up = dict(GOOD, outcomePrices=["0.06", "0.94"])
        report2 = desk.run_cycle(state_path, markets=[up], rate=18000.0,
                                 headlines=[])
        check("Siklus jual: SELL_PAPER_TP",
              report2["action"] == "SELL_PAPER_TP")
        state2 = desk.load_state(state_path)
        check("Ledger: posisi CLOSED dan kas naik",
              state2["position"] is None and state2["cash_idr"] > 25000)
        check("Realized paper positif di contoh ini",
              report2["realized_idr"] > 0)

    print("SEMUA TES LOLOS")


if __name__ == "__main__":
    main()
