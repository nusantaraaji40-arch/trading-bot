"""Engine demo v1 — Polymarket BTC jangka pendek (PAPER ONLY).

Membaca data PUBLIK saja (Gamma + CLOB). Tidak ada wallet, tidak ada
private key, tidak ada order nyata. Strategi v0 yang dipakai di sini
adalah arbitrase spread yang jujur: kalau harga ask YES + ask NO < 1,
membeli kedua sisi dan memegang sampai resolusi secara teori mengunci
selisihnya (sebelum fee). Kalau tidak ada edge, tidak ada trade —
itu perilaku yang benar, bukan bug.

Threshold edge 0.01 dipakai sebagai asumsi kasar untuk menutup taker
fee (besaran fee per-market di CLOB V2 tidak kami asumsikan nol).
Setiap pindaian dicatat ke btc_edge_history.jsonl (riwayat append-only:
jumlah market, edge terbaik, jumlah paper trade, saldo) sehingga tren
edge dan rentetan NO_TRADE bisa dibaca dari run ke run.
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
OUT = "/home/hatch/workspace/polymarket-bot/btc_engine_state.json"
HISTORY_PATH = "/home/hatch/workspace/polymarket-bot/btc_edge_history.jsonl"
VIRTUAL_START_IDR = 25000.0
EDGE_THRESHOLD = 0.01


def get_json(url, timeout=30):
    req = urllib.request.Request(url, headers={"User-Agent": "muse-paper-demo/1.0"})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read().decode("utf-8"))


def best_ask(book):
    asks = book.get("asks", [])
    if not asks:
        return None
    return min(float(a["price"]) for a in asks)


def best_bid(book):
    bids = book.get("bids", [])
    if not bids:
        return None
    return max(float(b["price"]) for b in bids)


def fetch_usdc_idr_rate():
    """Kurs live USDC/IDR dari CoinGecko; None kalau gagal (tanpa tebakan)."""
    try:
        data = get_json(COINGECKO_USDC_IDR, timeout=20)
        return float(data["usd-coin"]["idr"])
    except Exception as e:
        print(f"Kurs USDC/IDR gagal diambil ({e}); simulasi trade dilewati.")
        return None


def append_history(record):
    """Tambah satu baris riwayat (JSONL). Gagal tulis = peringatan saja."""
    try:
        with open(HISTORY_PATH, "a") as f:
            f.write(json.dumps(record) + "\n")
    except OSError as e:
        print(f"Riwayat pindaian gagal ditambah ({e}).")


def history_stats():
    """(jumlah_pindaian, edge_terbaik, no_trade_beruntun) dari riwayat."""
    try:
        with open(HISTORY_PATH) as f:
            rows = [json.loads(line) for line in f if line.strip()]
    except (OSError, ValueError):
        return 0, None, 0
    if not rows:
        return 0, None, 0
    edges = [r["best_edge"] for r in rows if r.get("best_edge") is not None]
    best = max(edges) if edges else None
    streak = 0
    for r in reversed(rows):
        if r.get("paper_trades", 0) == 0:
            streak += 1
        else:
            break
    return len(rows), best, streak


def fetch_active_markets():
    out = []
    for offset in (0, 100):
        url = (GAMMA + f"?limit=100&offset={offset}&active=true&closed=false"
               "&order=volume24hr&ascending=false")
        out.extend(get_json(url))
    return out


def main():
    markets = fetch_active_markets()
    now = time.time()
    rows = []
    for m in markets:
        q = (m.get("question") or "")
        ql = q.lower()
        if "bitcoin" not in ql and "btc" not in ql:
            continue
        try:
            end = datetime.fromisoformat(
                (m.get("endDate") or "").replace("Z", "+00:00")).timestamp()
        except ValueError:
            continue
        if not (0 < end - now <= 48 * 3600):
            continue
        token_ids = m.get("clobTokenIds")
        if isinstance(token_ids, str):
            try:
                token_ids = json.loads(token_ids)
            except ValueError:
                continue
        if not token_ids or len(token_ids) < 2:
            continue
        try:
            book_yes = get_json(f"{CLOB_BOOK}?token_id={token_ids[0]}")
            book_no = get_json(f"{CLOB_BOOK}?token_id={token_ids[1]}")
        except Exception as e:
            print(f"skip {q}: book gagal ({e})")
            continue
        ya, na = best_ask(book_yes), best_ask(book_no)
        yb, nb = best_bid(book_yes), best_bid(book_no)
        if ya is None or na is None:
            continue
        edge = 1.0 - (ya + na)
        rows.append({
            "question": q,
            "endDate": m.get("endDate"),
            "volume24hr": m.get("volume24hr"),
            "yes_ask": ya, "no_ask": na,
            "yes_bid": yb, "no_bid": nb,
            "edge": round(edge, 4),
            "decision": ("PAPER BUY BOTH" if edge > EDGE_THRESHOLD
                         else "NO TRADE (no edge)"),
        })
    rows.sort(key=lambda r: r["edge"], reverse=True)
    # Simulasi saldo dalam rupiah; harga market tetap USDC, konversi
    # memakai kurs live CoinGecko saat run. Tanpa kurs, trade dilewati.
    rate = fetch_usdc_idr_rate()
    trades = []
    balance = VIRTUAL_START_IDR
    for r in rows[:5]:
        if r["decision"] != "PAPER BUY BOTH":
            continue
        if rate is None:
            continue
        # Simulasi: beli 10 YES + 10 NO di harga ask; nilai resolusi = 10 USDC
        cost_usdc = 10 * r["yes_ask"] + 10 * r["no_ask"]
        cost_idr = cost_usdc * rate
        expected_idr = 10.0 * rate
        profit_idr = round(expected_idr - cost_idr, 2)
        trades.append({"market": r["question"],
                       "cost_usdc": round(cost_usdc, 4),
                       "cost_idr": round(cost_idr, 2),
                       "expected_value_at_resolution_idr": round(expected_idr, 2),
                       "paper_profit_before_fees_idr": profit_idr})
        balance = round(balance + profit_idr, 2)
    state = {
        "mode": "paper",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "virtual_balance_start_idr": VIRTUAL_START_IDR,
        "virtual_balance_now_idr": balance,
        "usdc_idr_rate": rate,
        "edge_threshold": EDGE_THRESHOLD,
        "markets_scanned": len(rows),
        "markets": rows[:10],
        "paper_trades": trades,
        "note": ("Bukan order nyata. Tidak ada USDC asli yang bergerak; "
                 "saldo demo dalam rupiah. "
                 "Edge = 1 - (ask YES + ask NO); fee live tidak dihitung "
                 "di sini, jadi threshold 0.01 dipakai sebagai penyangga."),
    }
    with open(OUT, "w") as f:
        json.dump(state, f, indent=2)
    best_edge = max((r["edge"] for r in rows), default=None)
    append_history({
        "timestamp": state["generated_at"],
        "markets_scanned": len(rows),
        "best_edge": best_edge,
        "paper_trades": len(trades),
        "virtual_balance_now_idr": balance,
    })
    print(f"Market BTC jangka pendek terpindai: {len(rows)}")
    for r in rows[:10]:
        print(f"- {r['question'][:70]} | YES ask {r['yes_ask']} | "
              f"NO ask {r['no_ask']} | edge {r['edge']} | {r['decision']}")
    print(f"Paper trades: {len(trades)} | Saldo virtual: Rp{balance:,.0f} | {OUT}")
    n, best_ever, streak = history_stats()
    print(f"Riwayat pindaian: {n} entri | edge terbaik {best_ever} | "
          f"NO_TRADE beruntun: {streak}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
