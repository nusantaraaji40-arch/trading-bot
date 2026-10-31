"""Engine demo v1 — Indodax spot (PAPER ONLY).

Membaca data PUBLIK saja (indodax.com/api). Tidak ada login, tidak ada
API key, tidak ada order nyata. Saldo virtual Rp50.000 dipakai supaya
demo mencerminkan modal live yang direncanakan user (Rp50.000).

Strategi v0 di sini murni mekanik demo: beli BTC senilai Rp10.000 di
harga ask terbaik, catat di ledger virtual. Bukan rekomendasi strategi.
Minimum order per pair di live wajib dicek ke dokumentasi/market
sebelum live — demo ini tidak mengasumsikannya.
"""
import json
import sys
import urllib.request
from datetime import datetime, timezone

API = "https://indodax.com/api"
VIRTUAL_START = 50000.0
BUY_IDR = 10000.0
LEDGER_PATH = "/home/hatch/workspace/indodax-bot/paper_ledger.json"
PAIRS = ["btc_idr", "eth_idr"]


def get_json(url, timeout=30):
    req = urllib.request.Request(url, headers={"User-Agent": "muse-paper-demo/1.0"})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read().decode("utf-8"))


def main():
    tickers = get_json(f"{API}/tickers").get("tickers", {})
    rows = []
    for pair in PAIRS:
        t = tickers.get(pair)
        if not t:
            print(f"{pair}: tidak ada di tickers")
            continue
        # ticker: last, buy (bid), sell (ask), high, low, vol_<coin>
        try:
            ask = float(t["sell"])
            bid = float(t["buy"])
            last = float(t["last"])
        except (KeyError, TypeError, ValueError):
            print(f"{pair}: format ticker tak dikenal: {t}")
            continue
        rows.append({"pair": pair, "bid": bid, "ask": ask, "last": last,
                     "spread": round(ask - bid, 2),
                     "spread_pct": round((ask - bid) / ask * 100, 4) if ask else None})
        print(f"{pair}: bid Rp{bid:,.0f} | ask Rp{ask:,.0f} | "
              f"last Rp{last:,.0f} | spread Rp{ask - bid:,.0f}")

    if not rows:
        print("Tidak ada pair yang bisa dibaca.")
        return 0

    # Paper trade: beli BTC Rp10.000 di harga ask
    btc = next((r for r in rows if r["pair"] == "btc_idr"), rows[0])
    btc_bought = BUY_IDR / btc["ask"]
    ledger = {
        "mode": "paper",
        "venue": "Indodax spot",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "virtual_balance_start_idr": VIRTUAL_START,
        "markets": rows,
        "paper_trade": {
            "pair": btc["pair"],
            "side": "BUY",
            "idr_spent": BUY_IDR,
            "ask_price": btc["ask"],
            "coin_received": btc_bought,
        },
        "virtual_balance_after_idr": VIRTUAL_START - BUY_IDR,
        "note": ("Bukan order nyata. Tidak ada rupiah/aset asli yang bergerak. "
                 "Demo tidak memakai login/API key. Minimum order live "
                 "wajib dicek sebelum live."),
    }
    with open(LEDGER_PATH, "w") as f:
        json.dump(ledger, f, indent=2)
    print(f"Paper trade tercatat: beli {btc_bought:.8f} {btc['pair']} "
          f"senilai Rp{BUY_IDR:,.0f} @ Rp{btc['ask']:,.0f}. "
          f"Saldo virtual tersisa: Rp{VIRTUAL_START - BUY_IDR:,.0f}. "
          f"Ledger: {LEDGER_PATH}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
