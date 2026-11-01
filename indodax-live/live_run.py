"""Live-run Indodax (spot) — PAKET PERSIAPAN, BUKAN PERINTAH TRADING.

Skrip ini TIDAK berisi API key atau secret apa pun. Key dibaca dari
environment (INDODAX_API_KEY, INDODAX_SECRET) di mesin yang menjalankan
skrip — mesin itulah yang memegang key, bukan repo ini, bukan chat.

Dua mode:
  check (default) : hanya baca — saldo privat, harga, dan limit min order.
                    TIDAK PERNAH membuat order.
  --live          : membuat SATU order beli pertama, HANYA jika SEMUA
                    gerbang lolos (lihat di bawah). Kalau satu gerbang
                    saja gagal, skrip berhenti tanpa order apa pun.

Gerbang live (semua wajib):
  1. Flag --live diberikan.
  2. Environment LIVE_TRADING=1.
  3. File LIVE_APPROVED.txt ada di folder skrip ini, berisi persetujuan
     pemilik (tanggal + pair + nominal yang disetujui).
  4. File params.json ada (salin dari params.example.json) dan lolos
     validasi: pair BTC/IDR atau ETH/IDR, modal Rp25.000,
     first_trade <= modal, SL 1-20%, TP bawah >= SL, TP atas >= TP bawah,
     kill-switch 5-30%.

Keamanan: skrip ini TIDAK mengandung pemanggilan withdraw dalam bentuk
apa pun. Key yang dipakai harus trade-only (View + Trade, TANPA
withdrawal). Nilai key/secret TIDAK PERNAH dicetak ke output.
"""

import argparse
import json
import os
import sys

try:
    import ccxt
except ImportError:
    print("ccxt belum terpasang. Jalankan: pip install ccxt==4.5.91")
    sys.exit(2)

PAIR_ALLOWLIST = ("BTC/IDR", "ETH/IDR")
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))


def rp(n):
    return f"Rp{n:,.0f}"


def load_exchange():
    key = os.environ.get("INDODAX_API_KEY", "")
    secret = os.environ.get("INDODAX_SECRET", "")
    if not key or not secret:
        print("INDODAX_API_KEY / INDODAX_SECRET belum diset di environment.")
        print("Set keduanya dulu (export), jangan tulis di file atau chat.")
        sys.exit(2)
    ex = ccxt.indodax({"apiKey": key, "secret": secret})
    # trust_env: pakai proxy environment bila ada (wajib di sebagian VM).
    try:
        ex.session.trust_env = True
    except Exception:
        pass
    print("API key terdeteksi dari environment (nilainya tidak dicetak).")
    return ex


def validate_params(path):
    try:
        with open(path) as f:
            p = json.load(f)
    except (OSError, ValueError) as e:
        print(f"params.json tidak bisa dibaca ({e}).")
        sys.exit(3)
    errors = []
    if p.get("pair") not in PAIR_ALLOWLIST:
        errors.append(f"pair harus salah satu dari {PAIR_ALLOWLIST}")
    if p.get("modal_idr") != 25000:
        errors.append("modal_idr harus 25000 (modal yang disepakati)")
    first = p.get("first_trade_idr", 0)
    if not (0 < first <= 25000):
        errors.append("first_trade_idr harus > 0 dan <= modal")
    sl = p.get("sl_pct", 0)
    if not (1 <= sl <= 20):
        errors.append("sl_pct harus 1-20")
    tp_low = p.get("tp_low_pct", 0)
    tp_high = p.get("tp_high_pct", 0)
    if not (tp_low >= sl and tp_high >= tp_low):
        errors.append("TP harus memenuhi: tp_low >= SL dan tp_high >= tp_low")
    ks = p.get("kill_switch_pct", 0)
    if not (5 <= ks <= 30):
        errors.append("kill_switch_pct harus 5-30")
    if errors:
        print("params.json DITOLAK:")
        for e in errors:
            print(f"  - {e}")
        sys.exit(3)
    return p


def check_gates():
    """Periksa semua gerbang live SEBELUM koneksi jaringan apa pun."""
    if os.environ.get("LIVE_TRADING") != "1":
        print("Gerbang live gagal: LIVE_TRADING=1 belum diset.")
        sys.exit(3)
    approved_path = os.path.join(SCRIPT_DIR, "LIVE_APPROVED.txt")
    if not os.path.isfile(approved_path):
        print("Gerbang live gagal: LIVE_APPROVED.txt tidak ditemukan.")
        print("File ini dibuat HANYA saat pemilik menyetujui parameter live.")
        sys.exit(3)
    with open(approved_path) as f:
        approval = f.read().strip().splitlines()
    print(f"Persetujuan tercatat: {approval[0] if approval else '(kosong)'}")
    params_path = os.path.join(SCRIPT_DIR, "params.json")
    if not os.path.isfile(params_path):
        print("Gerbang live gagal: params.json tidak ditemukan.")
        print("Salin params.example.json menjadi params.json setelah "
              "parameter disetujui.")
        sys.exit(3)
    return validate_params(params_path)


def mode_check(ex):
    print("Mode: CHECK (hanya baca, tanpa order).")
    balance = ex.fetch_balance()
    idr = balance.get("IDR", {}) or {}
    print(f"Saldo IDR: bebas {rp(idr.get('free', 0))} | "
          f"total {rp(idr.get('total', 0))}")
    for code in ("BTC", "ETH"):
        b = balance.get(code, {}) or {}
        if b.get("total"):
            print(f"Saldo {code}: {b['total']}")
    markets = ex.load_markets()
    ticker = ex.fetch_ticker("BTC/IDR")
    ask = ticker["ask"]
    print(f"BTC/IDR ask: {rp(ask)}")
    market = markets.get("BTC/IDR", {})
    limits = market.get("limits", {}) or {}
    amount_min = (limits.get("amount") or {}).get("min")
    cost_min = (limits.get("cost") or {}).get("min")
    print(f"Min order BTC/IDR: amount min {amount_min} | cost min {cost_min}")
    modal = 25000
    first = 5000
    print(f"Rencana: modal {rp(modal)}, beli pertama {rp(first)}, "
          f"kill-switch 15% ({rp(modal * 0.85)}).")
    if cost_min and first < cost_min:
        print(f"PERINGATAN: beli pertama {rp(first)} di bawah min cost "
              f"{rp(cost_min)} — nominal harus dinaikkan atau pair diganti.")
    else:
        print("Min order: nominal rencana memenuhi batas (atau batas tidak "
              "dipublikasikan exchange).")
    print("CHECK SELESAI. Nol order dibuat.")
    return 0


def mode_live(ex, params):
    pair = params["pair"]
    first = params["first_trade_idr"]
    ticker = ex.fetch_ticker(pair)
    ask = ticker["ask"]
    amount = first / ask
    print(f"Mode: LIVE — beli {rp(first)} {pair} @ {rp(ask)} "
          f"= {amount:.8f} koin (limit buy di ask).")
    order = ex.create_limit_buy_order(pair, amount, ask)
    print(f"Order terkirim: id {order.get('id')} | status "
          f"{order.get('status')}.")
    sl_price = ask * (1 - params["sl_pct"] / 100)
    tp_low_price = ask * (1 + params["tp_low_pct"] / 100)
    tp_high_price = ask * (1 + params["tp_high_pct"] / 100)
    ks_level = 25000 * (1 - params["kill_switch_pct"] / 100)
    print(f"Level pantau: SL {rp(sl_price)} | TP {rp(tp_low_price)}-"
          f"{rp(tp_high_price)} | kill-switch di saldo {rp(ks_level)}.")
    print("Satu order pertama selesai. Pemantauan SL/TP/kill-switch adalah "
          "langkah berikutnya, bukan bagian skrip ini.")
    return 0


def main():
    ap = argparse.ArgumentParser(description="Live-run Indodax (persiapan).")
    ap.add_argument("--live", action="store_true",
                    help="Aktifkan mode live (wajib lolos semua gerbang).")
    args = ap.parse_args()
    if args.live:
        params = check_gates()
    ex = load_exchange()
    if args.live:
        return mode_live(ex, params)
    return mode_check(ex)


if __name__ == "__main__":
    sys.exit(main())
