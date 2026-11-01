"""Paper-trading demo Polymarket — kripto harian.

Membaca data PUBLIK saja (Gamma + CLOB). Tidak ada wallet, tidak ada
private key, tidak ada order nyata yang dikirim. Semua trade dicatat
di ledger virtual bersaldo awal Rp25.000 (uang mainan, rupiah — sesuai
aturan demo user). Harga market Polymarket tetap dalam USDC; konversi
ke rupiah memakai kurs live CoinGecko (USDC/IDR) saat run, bukan kurs
tebakan. Kalau kurs tidak bisa diambil, paper trade dilewati dan saldo
tetap Rp50.000. Setiap trade juga ditambah ke paper_history.jsonl
(riwayat append-only; ledger utama tetap berisi trade terbaru saja).
"""
import json
import sys
import time
import urllib.request
from datetime import datetime, timezone

GAMMA = "https://gamma-api.polymarket.com/markets"
CLOB_BOOK = "https://clob.polymarket.com/book"
COINGECKO_USDC_IDR = ("https://api.coingecko.com/api/v3/simple/price"
                       "?ids=usd-coin&vs_currencies=idr")
VIRTUAL_START_IDR = 25000.0
LEDGER_PATH = "/home/hatch/workspace/polymarket-bot/paper_ledger.json"
HISTORY_PATH = "/home/hatch/workspace/polymarket-bot/paper_history.jsonl"
POSITION_PATH = "/home/hatch/workspace/polymarket-bot/paper_position.json"

CRYPTO_WORDS = ("bitcoin", "btc", "ethereum", "eth", "solana", "sol",
                "crypto", "xrp", "dogecoin", "doge")


def get_json(url, timeout=30):
    req = urllib.request.Request(url, headers={"User-Agent": "muse-paper-demo/1.0"})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read().decode("utf-8"))


def pick_daily_crypto_market():
    url = (GAMMA + "?limit=100&active=true&closed=false"
           "&order=volume24hr&ascending=false")
    markets = get_json(url)
    now = time.time()
    candidates = []
    for m in markets:
        q = (m.get("question") or "").lower()
        if not any(w in q for w in CRYPTO_WORDS):
            continue
        try:
            end = datetime.fromisoformat(
                (m.get("endDate") or "").replace("Z", "+00:00")).timestamp()
        except ValueError:
            continue
        # "Harian": berakhir dalam 48 jam ke depan
        if 0 < end - now <= 48 * 3600:
            candidates.append((float(m.get("volume24hr") or 0), m))
    if not candidates:
        return None
    candidates.sort(key=lambda t: t[0], reverse=True)
    return candidates[0][1]


def fetch_usdc_idr_rate():
    """Kurs live USDC/IDR dari CoinGecko; None kalau gagal (tanpa tebakan)."""
    try:
        data = get_json(COINGECKO_USDC_IDR, timeout=20)
        return float(data["usd-coin"]["idr"])
    except Exception as e:
        print(f"Kurs USDC/IDR gagal diambil ({e}); paper trade dilewati.")
        return None


def append_history(record):
    """Tambah satu baris riwayat (JSONL). Gagal tulis = peringatan saja,
    tidak menggagalkan run."""
    try:
        with open(HISTORY_PATH, "a") as f:
            f.write(json.dumps(record) + "\n")
    except OSError as e:
        print(f"Riwayat gagal ditambah ({e}); ledger terbaru tetap tersimpan.")


def main():
    # Celah yang diperbaiki 2026-11-01: jangan beli baru selagi posisi
    # paper masih OPEN/PARTIAL — beli baru akan menimpa posisi lama
    # karena exit manager menginisialisasi ulang dari ledger terbaru.
    # Posisi CLOSED (atau belum ada posisi) boleh beli baru.
    try:
        with open(POSITION_PATH) as f:
            pos = json.load(f)
        if pos.get("status") in ("OPEN", "PARTIAL"):
            print(f"Posisi paper masih {pos['status']} di market "
                  f"\"{pos.get('market')}\" — beli baru dilewati supaya "
                  f"posisi tidak tertimpa. Jalankan paper_exit.py untuk "
                  f"mengecek posisi itu.")
            return 0
    except (OSError, ValueError):
        pos = None
    # Perbaikan kas kumulatif 2026-11-01: trade baru mulai dari kas
    # terakhir posisi CLOSED (bukan reset — reset dulu menghapus
    # kerugian terealisasi -Rp544 dari pembukuan).
    # Perubahan modal 2026-11-01 (Rp50.000 -> Rp25.000 per venue):
    # kas siklus baru dibatasi ke modal berjalan; kelebihan dianggap
    # penarikan paper (dicatat di log, bukan dihapus diam-diam).
    start_cash = VIRTUAL_START_IDR
    if pos and pos.get("status") == "CLOSED":
        if "cash_idr" in pos:
            start_cash = float(pos["cash_idr"])
        else:
            sold = int(pos.get("shares_total", 0)) - int(pos.get("remaining", 0))
            start_cash = round(
                float(pos.get("cash_after_buy_idr", VIRTUAL_START_IDR))
                + float(pos.get("realized_idr", 0.0))
                + sold * float(pos.get("cost_per_share_idr", 0.0)), 2)
        if start_cash > VIRTUAL_START_IDR:
            print(f"Kas siklus baru dibatasi ke modal Rp{VIRTUAL_START_IDR:,.0f} "
                  f"(kelebihan Rp{start_cash - VIRTUAL_START_IDR:,.0f} "
                  f"dianggap penarikan paper).")
            start_cash = VIRTUAL_START_IDR
    market = pick_daily_crypto_market()
    if not market:
        print("Tidak ada market kripto harian aktif yang ditemukan saat ini.")
        return 0
    print("Market:", market.get("question"))
    print("Berakhir:", market.get("endDate"))
    print("Volume 24j:", market.get("volume24hr"))

    token_ids = market.get("clobTokenIds")
    if isinstance(token_ids, str):
        token_ids = json.loads(token_ids)
    if not token_ids:
        print("Market ini tidak punya CLOB token id.")
        return 0
    token_id = token_ids[0]
    book = get_json(f"{CLOB_BOOK}?token_id={token_id}")
    bids = book.get("bids", [])
    asks = book.get("asks", [])
    if not bids or not asks:
        print("Order book kosong untuk token ini.")
        return 0
    best_bid = max(float(b["price"]) for b in bids)
    best_ask = min(float(a["price"]) for a in asks)
    mid = (best_bid + best_ask) / 2
    print(f"Best bid: {best_bid:.3f} | Best ask: {best_ask:.3f} "
          f"| Mid: {mid:.3f} | Spread: {best_ask - best_bid:.3f}")

    # Simulasi paper trade: beli 10 shares YES di harga ask (USDC),
    # dicatat dalam rupiah memakai kurs live CoinGecko saat run.
    shares = 10
    cost_usdc = shares * best_ask
    rate = fetch_usdc_idr_rate()
    if rate is None:
        ledger = {
            "mode": "paper",
            "market": market.get("question"),
            "token_id": token_id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "virtual_balance_start_idr": start_cash,
            "paper_trade": None,
            "trade_skipped_reason": "kurs USDC/IDR tidak tersedia",
            "virtual_balance_after_idr": start_cash,
            "note": ("Bukan order nyata. Tidak ada USDC asli yang bergerak; "
                     "saldo demo dalam rupiah."),
        }
        with open(LEDGER_PATH, "w") as f:
            json.dump(ledger, f, indent=2)
        print(f"Paper trade dilewati (tanpa kurs). Saldo virtual tetap: "
              f"Rp{start_cash:,.0f}. Ledger: {LEDGER_PATH}")
        return 0
    cost_idr = cost_usdc * rate
    ledger = {
        "mode": "paper",
        "market": market.get("question"),
        "token_id": token_id,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "virtual_balance_start_idr": start_cash,
        "usdc_idr_rate": rate,
        "paper_trade": {
            "side": "BUY YES",
            "shares": shares,
            "price_usdc": best_ask,
            "cost_usdc": round(cost_usdc, 4),
            "cost_idr": round(cost_idr, 2),
        },
        "virtual_balance_after_idr": round(start_cash - cost_idr, 2),
        "note": ("Bukan order nyata. Tidak ada USDC asli yang bergerak; "
                 "saldo demo dalam rupiah."),
    }
    with open(LEDGER_PATH, "w") as f:
        json.dump(ledger, f, indent=2)
    append_history({
        "timestamp": ledger["timestamp"],
        "market": ledger["market"],
        "side": "BUY YES",
        "shares": shares,
        "price_usdc": best_ask,
        "cost_usdc": round(cost_usdc, 4),
        "cost_idr": round(cost_idr, 2),
        "usdc_idr_rate": rate,
        "virtual_balance_after_idr": ledger["virtual_balance_after_idr"],
    })
    print(f"Paper trade tercatat: beli {shares} YES @ {best_ask:.3f} USDC "
          f"(biaya virtual Rp{cost_idr:,.0f}, kurs Rp{rate:,.0f}/USDC). "
          f"Saldo virtual tersisa: Rp{start_cash - cost_idr:,.0f}. "
          f"Ledger: {LEDGER_PATH}. Riwayat ditambah ke {HISTORY_PATH}.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
