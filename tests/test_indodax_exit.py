"""Tes exit manager paper Indodax (stdlib saja, tanpa jaringan).

Jalankan dari indodax-bot/: python3 test_indodax_exit.py
Keluar 0 = semua lolos.
"""

import sys

sys.path.insert(0, ".")
from indodax_exit import decide_exit

FAILURES = []


def check(name, got, want):
    if got != want:
        FAILURES.append(f"{name}: dapat {got}, mau {want}")
    else:
        print(f"lolos: {name}")


def pos(entry_ask=1407129000.0, coin=0.00000711, cash=40000.0):
    return {"entry_ask": entry_ask, "coin_remaining": coin,
            "cash_idr": cash, "coin_total": coin,
            "cost_idr_total": 10000.0}


def main():
    # Posisi berjalan saat ini: +0,26% -> HOLD (belum 3%).
    check("HOLD di +0,26%",
          decide_exit(pos(), 1410784000.0), ("HOLD", 0.0))
    # Di bawah TP (2,9%) -> HOLD.
    check("HOLD di +2,9%",
          decide_exit(pos(), 1407129000.0 * 1.029), ("HOLD", 0.0))
    # Tepat +3% -> TP jual HABIS (bukan separuh).
    p = pos()
    check("TP tepat +3% jual habis",
          decide_exit(p, 1407129000.0 * 1.03), ("TP", p["coin_remaining"]))
    # Di atas +3% (+5%) -> TP jual habis juga.
    p = pos()
    check("TP di +5% jual habis",
          decide_exit(p, 1407129000.0 * 1.05), ("TP", p["coin_remaining"]))
    # SL -5% -> jual habis.
    p = pos()
    check("SL -5%",
          decide_exit(p, 1407129000.0 * 0.95), ("SL", p["coin_remaining"]))
    # Kill-switch mengalahkan SL: total <= Rp21.250.
    p = pos(cash=10000.0)
    check("kill-switch mengalahkan SL",
          decide_exit(p, 1407129000.0 * 0.90),
          ("KILL_SWITCH", p["coin_remaining"]))
    # Kill-switch tepat di lantai ikut menjual.
    # total = cash + coin*bid = 21.250 -> bid = (21250-10000)/coin.
    p = pos(cash=10000.0)
    bid_ks = (21250.0 - 10000.0) / p["coin_remaining"]
    check("kill-switch tepat di lantai",
          decide_exit(p, bid_ks), ("KILL_SWITCH", p["coin_remaining"]))

    if FAILURES:
        print("\nGAGAL:")
        for f in FAILURES:
            print(" -", f)
        return 1
    print("\nSemua tes exit Indodax lolos.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
