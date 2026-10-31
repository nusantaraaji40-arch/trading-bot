"""Unified Bot Engine v1 — SEMUA MODUL (mode PAPER, live DIGATED).

Modul:
  1. Indodax spot (data publik live) — keranjang utama + keranjang receh
  2. Polymarket (data publik live, read-only)
  3. Market cap CoinGecko (live, tanpa key)
  4. DexScreener (live, tanpa key)
  5. Agen berita (RSS publik + skor sentimen kata kunci v1)
  6. Social pulse (Stocktwits trending publik)
  7. Filter tren (arah 24 jam CoinGecko)
  8. Manajemen risiko: SL 5% / TP 10-15% / kill-switch 15% modal
  9. Execution layer: PAPER default. Live DINONAKTIFKAN secara default dan
     hanya bisa jalan bila SEMUA syarat terpenuhi:
       - env LIVE_TRADING=1, DAN
       - file LIVE_APPROVED.txt ada dan berisi parameter yang disetujui user, DAN
       - API key trade-only tersedia lewat jalur aman (bukan di file ini).
     Tanpa itu, fungsi live() menolak jalan. Tidak ada order nyata di run ini.

Jujur soal batasan v1:
  - Sentimen berita = skor kata kunci (bukan model bahasa besar).
  - Social pulse = daftar trending Stocktwits (bukan API X berbayar).
  - Paper trade memakai harga ask ticker (bukan fill order book penuh).
"""
import json
import os
import re
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timezone

BASE = os.path.dirname(os.path.abspath(__file__))
STATE_PATH = os.path.join(BASE, "unified_state.json")
LIVE_APPROVAL_PATH = os.path.join(BASE, "LIVE_APPROVED.txt")

# ---- Parameter risiko (disepakati) ----
SL = 0.05            # stop loss per trade
TP_LOW = 0.10        # take profit bawah
TP_HIGH = 0.15       # take profit atas
KILL_SWITCH = 0.15   # berhenti bila modal turun 15%
VIRTUAL_BALANCE = 50000.0
PAPER_TRADE_IDR = 10000.0

UA = {"User-Agent": "muse-unified-engine/1.0"}


def get_json(url, timeout=30):
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read().decode("utf-8"))


def get_text(url, timeout=30):
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return resp.read().decode("utf-8", errors="ignore")


def now_iso():
    return datetime.now(timezone.utc).isoformat()


# ================= 1. INDODAX =================
def mod_indodax():
    try:
        tickers = get_json("https://indodax.com/api/tickers").get("tickers", {})
        majors, receh = {}, []
        for pair in ("btc_idr", "eth_idr"):
            t = tickers.get(pair)
            if t:
                majors[pair] = {"bid": float(t["buy"]), "ask": float(t["sell"]),
                                "last": float(t["last"]),
                                "spread_pct": round((float(t["sell"]) - float(t["buy"])) / float(t["sell"]) * 100, 4)}
        for pair, t in tickers.items():
            if not pair.endswith("_idr"):
                continue
            try:
                last = float(t["last"])
                vol_coin = float(t.get("vol_" + pair.split("_")[0], 0) or 0)
            except (KeyError, TypeError, ValueError):
                continue
            if last < 500:  # keranjang receh: harga per koin < Rp500
                receh.append({"pair": pair, "last": last,
                              "idr_volume_approx": round(vol_coin * last),
                              "bid": float(t["buy"]), "ask": float(t["sell"])})
        receh.sort(key=lambda r: r["idr_volume_approx"], reverse=True)
        return {"status": "ok", "majors": majors, "receh_top5": receh[:5],
                "receh_count": len(receh)}
    except Exception as e:  # noqa: BLE001 - modul lain tetap jalan
        return {"status": "failed", "error": str(e)}


# ================= 2. POLYMARKET (read-only) =================
def mod_polymarket():
    try:
        events = get_json(
            "https://gamma-api.polymarket.com/events?tag_slug=bitcoin&closed=false&limit=50")
        btc = []
        for ev in events if isinstance(events, list) else []:
            title = ev.get("title", "")
            if "bitcoin" not in title.lower() and "btc" not in title.lower():
                continue
            for m in ev.get("markets", []):
                # Lewati market yang sudah tutup/kedaluwarsa (harga 0/1 semu)
                if m.get("closed"):
                    continue
                end = m.get("endDate") or ""
                if end and end < now_iso():
                    continue
                try:
                    prices = json.loads(m.get("outcomePrices", "[]"))
                except (TypeError, ValueError):
                    prices = []
                if not prices or prices[0] in ("0", "1"):
                    continue
                btc.append({"event": title[:80], "question": m.get("question", "")[:80],
                            "yes_price": prices[0] if len(prices) > 0 else None,
                            "no_price": prices[1] if len(prices) > 1 else None})
            if len(btc) >= 5:
                break
        return {"status": "ok", "btc_markets": btc}
    except Exception as e:  # noqa: BLE001
        return {"status": "failed", "error": str(e)}


# ================= 3. MARKET CAP (CoinGecko) =================
CG_IDS = {"bitcoin": "BTC", "ethereum": "ETH", "solana": "SOL", "shiba-inu": "SHIB"}


def mod_marketcap():
    try:
        ids = ",".join(CG_IDS.keys())
        data = get_json(
            f"https://api.coingecko.com/api/v3/coins/markets?vs_currency=usd"
            f"&ids={ids}&price_change_percentage=24h")
        out = {}
        for c in data:
            out[CG_IDS[c["id"]]] = {
                "price_usd": c["current_price"],
                "market_cap_usd": c["market_cap"],
                "change_24h_pct": round(c["price_change_percentage_24h"], 2),
                "trend": "up" if c["price_change_percentage_24h"] > 0 else "down",
            }
        return {"status": "ok", "coins": out}
    except Exception as e:  # noqa: BLE001
        return {"status": "failed", "error": str(e)}


# ================= 4. DEXSCREENER =================
def mod_dexscreener():
    try:
        data = get_json("https://api.dexscreener.com/latest/dex/search?q=SOL")
        pairs = []
        for p in data.get("pairs", [])[:3]:
            pairs.append({"chain": p.get("chainId"), "dex": p.get("dexId"),
                          "pair": f"{p.get('baseToken', {}).get('symbol')}/{p.get('quoteToken', {}).get('symbol')}",
                          "price_usd": p.get("priceUsd"),
                          "liq_usd": (p.get("liquidity") or {}).get("usd")})
        return {"status": "ok", "pairs_found": len(data.get("pairs", [])), "top3": pairs}
    except Exception as e:  # noqa: BLE001
        return {"status": "failed", "error": str(e)}


# ================= 5. AGEN BERITA (RSS + sentimen kata kunci v1) =================
POS_WORDS = ["surge", "rally", "bullish", "adoption", "approval", "record",
             "growth", "soar", "gain", "breakthrough", "partnership", "inflow"]
NEG_WORDS = ["crash", "hack", "lawsuit", "ban", "dump", "fear", "plunge",
             "fraud", "collapse", "selloff", "sell-off", "outflow", "warning"]
RSS_FEEDS = ["https://www.coindesk.com/arc/outboundfeeds/rss/",
             "https://cointelegraph.com/rss"]


def mod_news():
    headlines = []
    used = None
    for feed in RSS_FEEDS:
        try:
            root = ET.fromstring(get_text(feed))
            for item in root.iter("item"):
                title = item.findtext("title") or ""
                if title:
                    headlines.append(title.strip())
                if len(headlines) >= 10:
                    break
            if headlines:
                used = feed
                break
        except Exception:  # noqa: BLE001 - coba feed berikutnya
            continue
    if not headlines:
        return {"status": "failed", "error": "semua feed RSS gagal dijangkau"}
    score = 0
    for h in headlines:
        low = h.lower()
        score += sum(w in low for w in POS_WORDS)
        score -= sum(w in low for w in NEG_WORDS)
    if score >= 2:
        stance = "positif"
    elif score <= -2:
        stance = "negatif"
    else:
        stance = "netral"
    return {"status": "ok", "feed": used, "headlines_top5": headlines[:5],
            "sentiment_score": score, "stance": stance,
            "blocks_trading": score <= -3}


# ================= 6. SOCIAL PULSE (Stocktwits trending) =================
def mod_social():
    try:
        data = get_json("https://api.stocktwits.com/api/2/trending/symbols.json")
        symbols = [s.get("symbol") for s in data.get("symbols", [])]
        tracked = {"BTC.X": "BTC", "ETH.X": "ETH", "SHIB.X": "SHIB"}
        trending_tracked = [tracked[s] for s in symbols if s in tracked]
        return {"status": "ok", "trending_top10": symbols[:10],
                "tracked_trending": trending_tracked}
    except Exception as e:  # noqa: BLE001
        return {"status": "failed", "error": str(e)}


# ================= 7-9. KEPUTUSAN + EKSEKUSI =================
def live_gate_check():
    """Gerbang live: default TERKUNCI. Live hanya bila env + file approval ada."""
    if os.environ.get("LIVE_TRADING") != "1":
        return False, "LIVE_TRADING != 1 (default: paper)"
    if not os.path.exists(LIVE_APPROVAL_PATH):
        return False, "file LIVE_APPROVED.txt tidak ada"
    return True, "terbuka (env + approval ada)"


def live_trade_stub():
    """Stub eksekusi live: menolak jalan selama gerbang terkunci."""
    ok, reason = live_gate_check()
    if not ok:
        return {"live_enabled": False, "reason": reason,
                "orders_placed": 0,
                "note": "Tidak ada order nyata. Live butuh persetujuan eksplisit user + API key trade-only via jalur aman."}
    return {"live_enabled": True, "reason": reason,
            "orders_placed": 0,
            "note": "Gerbang terbuka, tapi modul order live belum diaktifkan di run ini."}


def main():
    state = {"timestamp": now_iso(), "mode": "paper", "modules": {}}
    state["modules"]["indodax"] = mod_indodax()
    state["modules"]["polymarket"] = mod_polymarket()
    state["modules"]["market_cap"] = mod_marketcap()
    state["modules"]["dexscreener"] = mod_dexscreener()
    state["modules"]["news_agent"] = mod_news()
    state["modules"]["social_pulse"] = mod_social()

    # ---- Mesin keputusan (keranjang utama: BTC) ----
    indo = state["modules"]["indodax"]
    mcap = state["modules"]["market_cap"]
    news = state["modules"]["news_agent"]
    social = state["modules"]["social_pulse"]
    decision = {"action": "NO_TRADE", "reasons": []}
    if indo.get("status") == "ok" and "btc_idr" in indo["majors"]:
        btc = indo["majors"]["btc_idr"]
        trend_up = (mcap.get("coins", {}).get("BTC", {}).get("trend") == "up") if mcap.get("status") == "ok" else None
        news_block = news.get("blocks_trading", False) if news.get("status") == "ok" else False
        hype = "BTC" in social.get("tracked_trending", []) if social.get("status") == "ok" else False
        if trend_up is False:
            decision["reasons"].append("tren BTC 24 jam turun -> tidak beli (ikut arus)")
        if news_block:
            decision["reasons"].append("sentimen berita sangat negatif -> jeda trading")
        if hype and news.get("stance") == "negatif":
            decision["reasons"].append("BTC trending + berita negatif -> hindari FOMO")
        if not decision["reasons"]:
            qty = PAPER_TRADE_IDR / btc["ask"]
            decision = {"action": "PAPER_BUY", "pair": "btc_idr",
                        "idr": PAPER_TRADE_IDR, "ask": btc["ask"],
                        "qty": round(qty, 8),
                        "sl_price": round(btc["ask"] * (1 - SL)),
                        "tp_low_price": round(btc["ask"] * (1 + TP_LOW)),
                        "tp_high_price": round(btc["ask"] * (1 + TP_HIGH)),
                        "kill_switch_balance": round(VIRTUAL_BALANCE * (1 - KILL_SWITCH)),
                        "reasons": ["tren naik", "berita tidak memblokir", "social tidak ekstrem"]}
    else:
        decision["reasons"].append("data Indodax BTC tidak tersedia")
    state["decision"] = decision
    state["risk"] = {"sl_pct": SL, "tp_low_pct": TP_LOW, "tp_high_pct": TP_HIGH,
                     "kill_switch_pct": KILL_SWITCH,
                     "virtual_balance": VIRTUAL_BALANCE}
    state["execution"] = live_trade_stub()

    with open(STATE_PATH, "w") as f:
        json.dump(state, f, indent=2)

    # ---- Ringkasan tercetak ----
    print("=" * 60)
    print("UNIFIED ENGINE v1 — ringkasan run", state["timestamp"])
    for name, mod in state["modules"].items():
        print(f"[{name}] {mod.get('status')}")
    if indo.get("status") == "ok":
        for p, v in indo["majors"].items():
            print(f"  Indodax {p}: bid Rp{v['bid']:,.0f} ask Rp{v['ask']:,.0f} spread {v['spread_pct']}%")
        print(f"  Keranjang receh (<Rp500): {indo['receh_count']} pair, top volume:")
        for r in indo["receh_top5"]:
            print(f"    {r['pair']}: Rp{r['last']:,.2f} vol~Rp{r['idr_volume_approx']:,.0f}")
    if mcap.get("status") == "ok":
        for s, v in mcap["coins"].items():
            print(f"  MCap {s}: ${v['price_usd']} mcap ${v['market_cap_usd']:,.0f} 24h {v['change_24h_pct']}% tren {v['trend']}")
    if state["modules"]["dexscreener"].get("status") == "ok":
        print(f"  DexScreener: {state['modules']['dexscreener']['pairs_found']} pair SOL ditemukan")
    if news.get("status") == "ok":
        print(f"  Berita: skor {news['sentiment_score']} ({news['stance']}) — {news['headlines_top5'][0][:90]}")
    if social.get("status") == "ok":
        print(f"  Social trending: {social['trending_top10'][:5]} | tracked: {social['tracked_trending']}")
    print(f"KEPUTUSAN: {decision['action']} — {'; '.join(decision['reasons'])}")
    if decision["action"] == "PAPER_BUY":
        print(f"  PAPER BUY Rp{decision['idr']:,.0f} {decision['pair']} @ Rp{decision['ask']:,.0f} "
              f"= {decision['qty']} koin | SL Rp{decision['sl_price']:,.0f} | "
              f"TP Rp{decision['tp_low_price']:,.0f}-Rp{decision['tp_high_price']:,.0f}")
    print(f"EKSEKUSI LIVE: {state['execution']['live_enabled']} — {state['execution']['reason']}")
    print(f"State tersimpan: {STATE_PATH}")
    print("=" * 60)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
