#!/usr/bin/env python3
"""Cek saldo Indodax (BACA SAJA, tanpa order) dari server Tencent.

Memakai fungsi signing + get_balances yang sama persis dengan live_loop.py,
jadi tes ini membuktikan server Singapura bisa memanggil API Indodax
bertanda tangan — sebelum loop live apa pun dijalankan.

Pakai:
  set -a; source ~/.indodax_env; set +a
  python3 check_indodax.py
  # LIVE_TRADING sengaja TIDAK dipakai di sini; skrip ini tidak pernah order.

Output hanya saldo IDR/BTC/ETH (free/total). Nilai key TIDAK PERNAH dicetak.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from live_loop import get_balances, load_keys  # noqa: E402


def main():
    key, secret = load_keys()
    balances, _payload = get_balances(key, secret)
    if balances is None:
        print("CHECK GAGAL: saldo tidak terbaca (key / jaringan / API).")
        print("JANGAN lanjut migrasi. Kirim pesan error ini (tanpa key) ke Muse.")
        return 2
    for code in ("IDR", "BTC", "ETH"):
        free, total = balances.get(code, (None, None))
        print(f"{code}: free={free} total={total}")
    print("CHECK OK: saldo terbaca, nol order dibuat.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
