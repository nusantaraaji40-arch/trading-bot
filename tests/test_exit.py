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
# total paper Rp49.818 (di atas kill-switch Rp42.500).
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
      decide_exit(0.013, 0.0140, 0.0143, 10, False, 42000.0),
      ("SELL_ALL", 10, "KILL_SWITCH"))

check("Kill-switch tepat di level ikut menjual",
      decide_exit(0.013, 0.012, 0.013, 10, False, 42500.0),
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

# --- Tes load_position (state file) ---
import json as _json  # noqa: E402
import tempfile as _tempfile  # noqa: E402
from paper_exit import load_position as _load_position  # noqa: E402


def _ledger(ts, market="M1", token="tok1", price=0.013, shares=10,
            cost=2356.75, cash=47643.25):
    return {"market": market, "token_id": token, "timestamp": ts,
            "paper_trade": {"shares": shares, "price_usdc": price,
                            "cost_idr": cost},
            "virtual_balance_after_idr": cash}


with _tempfile.TemporaryDirectory() as _d:
    _p = os.path.join(_d, "pos.json")
    _pos = _load_position(_ledger("2026-01-01T00:00:00+00:00"), _p)
    check("Init posisi dari ledger",
          (_pos["remaining"], _pos["status"],
           _pos["ledger_timestamp"]),
          (10, "OPEN", "2026-01-01T00:00:00+00:00"))
    # Simulasikan state CLOSED versi lama (tanpa ledger_timestamp,
    # last_check lebih baru dari ledger) — tidak boleh bangkit lagi.
    _closed = dict(_pos)
    _closed.pop("ledger_timestamp")
    _closed.update({"remaining": 0, "status": "CLOSED",
                    "last_check": "2026-01-01T01:00:00+00:00"})
    with open(_p, "w") as _f:
        _json.dump(_closed, _f)
    _pos2 = _load_position(_ledger("2026-01-01T00:00:00+00:00"), _p)
    check("Posisi CLOSED tidak dibangkitkan ledger lama",
          (_pos2["remaining"], _pos2["status"]), (0, "CLOSED"))
    # Ledger baru (trade baru setelah close) -> posisi baru.
    _pos3 = _load_position(
        _ledger("2026-01-02T00:00:00+00:00", market="M2", token="tok2",
                price=0.020, shares=4, cost=1000.0, cash=49000.0), _p)
    check("Ledger baru menginisialisasi posisi baru",
          (_pos3["market"], _pos3["remaining"], _pos3["status"]),
          ("M2", 4, "OPEN"))

if FAILURES:
    print("\nGAGAL:")
    for f in FAILURES:
        print(f"  - {f}")
    sys.exit(1)
print("\nSemua tes exit lolos.")
