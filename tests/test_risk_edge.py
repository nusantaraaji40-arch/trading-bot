"""Tes fungsi murni risiko + edge (stdlib saja, tanpa jaringan).

Jalankan dari root repo: python3 tests/test_risk_edge.py
Keluar 0 = semua lolos.
"""


def edge(yes_ask, no_ask):
    return 1 - (yes_ask + no_ask)


def kill_switch_terpicu(rugi, modal=50000):
    return rugi >= 0.15 * modal


def cek_sl(harga, entry):
    return harga <= 0.95 * entry


def cek_tp(harga, entry):
    return harga >= 1.10 * entry


def main():
    # Edge: contoh terverifikasi dari run engine (edge -0,001 -> NO_TRADE).
    assert abs(edge(0.501, 0.500) - (-0.001)) < 1e-9
    assert edge(0.490, 0.490) > 0.01  # 0,02 -> kandidat
    assert not edge(0.501, 0.500) >= 0.01
    # Kill-switch 15% dari Rp50.000 = Rp7.500.
    assert kill_switch_terpicu(7500) is True
    assert kill_switch_terpicu(7499) is False
    # SL 5% dan TP 10%.
    assert cek_sl(950000, 1000000) is True
    assert cek_sl(950001, 1000000) is False
    assert cek_tp(1100000, 1000000) is True
    assert cek_tp(1099999, 1000000) is False
    print("Semua tes lolos.")


if __name__ == "__main__":
    main()
