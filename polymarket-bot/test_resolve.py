"""Tes resolution handler paper_exit (stdlib saja, tanpa jaringan).

Jalankan dari polymarket-bot/: python3 test_resolve.py
Keluar 0 = semua lolos.
"""

import sys

sys.path.insert(0, ".")
from paper_exit import decide_resolution, settle_value

FAILURES = []


def check(name, got, want):
    if got != want:
        FAILURES.append(f"{name}: dapat {got}, mau {want}")
    else:
        print(f"lolos: {name}")


def main():
    # YES menang: closed + harga decisif.
    check("YES menang",
          decide_resolution({"closed": True, "outcomePrices": ["1", "0"],
                             "umaResolutionStatus": "resolved"})[0],
          "YES")
    # NO menang: YES -> 0, NO -> 1.
    check("NO menang",
          decide_resolution({"closed": True, "outcomePrices": ["0", "1"],
                             "umaResolutionStatus": "resolved"})[0],
          "NO")
    # Ambang decisif 0,999 (harga pra-resolusi 0,9995 lolos).
    check("YES di 0,9995",
          decide_resolution({"closed": True,
                             "outcomePrices": ["0.9995", "0.0005"]})[0],
          "YES")
    check("NO di 0,9995",
          decide_resolution({"closed": True,
                             "outcomePrices": ["0.0005", "0.9995"]})[0],
          "NO")
    # Belum closed -> TIDAK settle (meski harga decisif).
    check("belum closed tidak settle",
          decide_resolution({"closed": False,
                             "outcomePrices": ["1", "0"]})[0],
          None)
    # Closed tapi harga belum decisif -> TIDAK settle.
    check("closed belum decisif tidak settle",
          decide_resolution({"closed": True,
                             "outcomePrices": ["0.5", "0.5"]})[0],
          None)
    # Harga rusak / hilang -> TIDAK settle.
    check("harga hilang tidak settle",
          decide_resolution({"closed": True})[0],
          None)
    check("harga rusak tidak settle",
          decide_resolution({"closed": True,
                             "outcomePrices": ["?", "0"]})[0],
          None)
    # Settle math: YES 10 lembar @ Rp18.148 = Rp181.480; NO = Rp0.
    check("settle YES", settle_value(10, "YES", 18148.0), 181480.0)
    check("settle NO", settle_value(10, "NO", 18148.0), 0.0)
    # Pembukuan settle NO: 10 lembar @ cost Rp145,03 -> P&L -Rp1.450,30.
    qty, cost = 10, 145.03
    pnl = round(settle_value(qty, "NO", 18148.0) - qty * cost, 2)
    check("P&L settle NO", pnl, -1450.30)
    # Pembukuan settle YES: proceeds - cost.
    pnl_yes = round(settle_value(qty, "YES", 18148.0) - qty * cost, 2)
    check("P&L settle YES", pnl_yes, 180029.70)

    if FAILURES:
        print("\nGAGAL:")
        for f in FAILURES:
            print(" -", f)
        return 1
    print("\nSemua tes resolusi lolos.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
