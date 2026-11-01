"""Tes fungsi murni decide_exit dari polymarket-bot/paper_exit.py.

Jalankan dari root repo: python3 tests/test_exit.py
Semua tes memakai angka buatan (tidak ada jaringan, tidak ada order).
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "polymarket-bot"))
from paper_exit import decide_exit  # noqa: E402

FAILURES = []


def check(name, got, want):
    if got != want:
        FAILURES.append(f"{name}: dapat {got}, mau {want}")
    else:
        print(f"lolos: {name}")


# Posisi acuan: entry ask 0,013, sisa 10, TP1 belum terjadi,
# total paper Rp49.818 (di atas kill-switch Rp21.250).
check("HOLD saat tidak ada level tersentuh",
      decide_exit(0.013, 0.012, 0.013, 10, False, 49818.0),
      ("HOLD", 0, "HOLD"))

check("TP1 menjual separuh",
      decide_exit(0.013, 0.0140, 0.0143, 10, False, 49818.0),
      ("SELL_PARTIAL", 5, "TP1"))

check("TP2 menjual seluruh sisa setelah TP1",
      decide_exit(0.013, 0.0148, 0.0150, 5, True, 49818.0),
      ("SELL_ALL", 5, "TP2"))

check("TP2 tidak aktif sebelum TP1",
      decide_exit(0.013, 0.0148, 0.0150, 10, False, 49818.0),
      ("SELL_PARTIAL", 5, "TP1"))

check("SL menjual seluruh sisa",
      decide_exit(0.013, 0.0120, 0.0123, 10, False, 49818.0),
      ("SELL_ALL", 10, "SL"))

check("Kill-switch mengalahkan TP1",
      decide_exit(0.013, 0.0140, 0.0143, 10, False, 21000.0),
      ("SELL_ALL", 10, "KILL_SWITCH"))

check("Kill-switch tepat di level ikut menjual",
      decide_exit(0.013, 0.012, 0.013, 10, False, 21250.0),
      ("SELL_ALL", 10, "KILL_SWITCH"))

check("TP1 sisa ganjil menjual floor",
      decide_exit(0.013, 0.0140, 0.0143, 3, False, 49818.0),
      ("SELL_PARTIAL", 1, "TP1"))

check("TP1 sisa 1 lembar menjual habis",
      decide_exit(0.013, 0.0140, 0.0143, 1, False, 49818.0),
      ("SELL_ALL", 1, "TP1"))

check("Posisi kosong tidak menjual",
      decide_exit(0.013, 0.0140, 0.0143, 0, False, 49818.0),
      ("HOLD", 0, "HOLD"))

if FAILURES:
    print("\nGAGAL:")
    for f in FAILURES:
        print(f"  - {f}")
    sys.exit(1)
print("\nSemua tes exit lolos.")
