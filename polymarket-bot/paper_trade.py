"""Paper-trading demo Polymarket — kripto harian.

Membaca data PUBLIK saja (Gamma + CLOB). Tidak ada wallet, tidak ada
private key, tidak ada order nyata yang dikirim. Semua trade dicatat
di ledger virtual bersaldo awal 1000 USDC (uang mainan).
"""
import json
import sys
import time
import urllib.request
from datetime import datetime, timezone

GAMMA = "https://gamma-api.polymarket.com/markets"
CLOB_BOOK = "https://clob.polymarket.com/book"
VIRTUAL_START = 1000.0
LEDGER_PATH = "/home/hatch/workspace/polymarket-bot/paper_ledger.json"

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


def main():
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

    # Simulasi paper trade: beli 10 shares YES di harga ask
    shares = 10
    cost = shares * best_ask
    ledger = {
        "mode": "paper",
        "market": market.get("question"),
        "token_id": token_id,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "virtual_balance_start": VIRTUAL_START,
        "paper_trade": {
            "side": "BUY YES",
            "shares": shares,
            "price": best_ask,
            "cost": round(cost, 2),
        },
        "virtual_balance_after": round(VIRTUAL_START - cost, 2),
        "note": "Bukan order nyata. Tidak ada USDC asli yang bergerak.",
    }
    with open(LEDGER_PATH, "w") as f:
        json.dump(ledger, f, indent=2)
    print(f"Paper trade tercatat: beli {shares} YES @ {best_ask:.3f} "
          f"(biaya virtual {cost:.2f}). Saldo virtual tersisa: "
          f"{VIRTUAL_START - cost:.2f}. Ledger: {LEDGER_PATH}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
