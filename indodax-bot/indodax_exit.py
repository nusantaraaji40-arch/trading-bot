#!/usr/bin/env python3
"""Exit manager paper Indodax spot (demo, tanpa uang asli).

Pasangan dari paper_trade.py: TP bertangga (TP1 +10% jual separuh,
TP2 +15% jual sisa), SL -5%, kill-switch 15% dari total modal virtual
(lantai Rp42.500), prioritas kill-switch > SL > TP2 > TP1.
Trigger diukur dari harga bid terhadap harga ask entry (spread BTC/IDR
sangat kecil, ~0,007%, jadi tidak ada risiko pemicu SL palsu seperti di
Polymarket); hasil jual dihitung di bid. Ticker gagal dibaca =
CANNOT_EXIT (tidak ada harga tebakan). Posisi CLOSED tidak pernah
dibangkitkan lagi; posisi baru hanya lahir dari trade baru paper_trade.
Nol order nyata; tidak ada login/API key.
"""

import json
import os
import sys
import urllib.request
from datetime import datetime, timezone

WORKSPACE = os.path.dirname(os.path.abspath(__file__))
LEDGER_PATH = os.path.join(WORKSPACE, "paper_ledger.json")
POSITION_PATH = os.path.join(WORKSPACE, "indodax_position.json")
HISTORY_PATH = os.path.join(WORKSPACE, "indodax_history.jsonl")

VIRTUAL_START_IDR = 50000.0
SL_PCT = 0.05
TP1_PCT = 0.10
TP2_PCT = 0.15
KILL_SWITCH_PCT = 0.15
API = "https://indodax.com/api"


def get_json(url, timeout=30):
    req = urllib.request.Request(url, headers={"User-Agent": "muse-paper-demo/1.0"})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read().decode("utf-8"))


def load_position():
    """Muat state; inisialisasi dari ledger lama bila belum ada."""
    try:
        with open(POSITION_PATH) as f:
            return json.load(f)
    except (OSError, ValueError):
        pass
    try:
        with open(LEDGER_PATH) as f:
            ledger = json.load(f)
    except (OSError, ValueError):
        return None
    trade = ledger.get("paper_trade")
    if not trade:
        return None
    return {
        "pair": trade["pair"],
        "side": "LONG",
        "status": "OPEN",
        "entry_ask": float(trade["ask_price"]),
        "coin_total": float(trade["coin_received"]),
        "coin_remaining": float(trade["coin_received"]),
        "cost_idr_total": float(trade["idr_spent"]),
        "cash_idr": float(ledger["virtual_balance_after_idr"]),
        "tp1_done": False,
        "realized_idr": 0.0,
    }


def save_position(pos):
    with open(POSITION_PATH, "w") as f:
        json.dump(pos, f, indent=2)


def append_history(event):
    try:
        with open(HISTORY_PATH, "a") as f:
            f.write(json.dumps(event) + "\n")
    except OSError:
        pass


def decide_exit(pos, bid):
    """Prioritas: kill-switch > SL > TP2 > TP1. Return (action, coin)."""
    remaining = pos["coin_remaining"]
    total = pos["cash_idr"] + remaining * bid
    if total <= VIRTUAL_START_IDR * (1.0 - KILL_SWITCH_PCT):
        return ("KILL_SWITCH", remaining)
    change = (bid - pos["entry_ask"]) / pos["entry_ask"]
    if change <= -SL_PCT:
        return ("SL", remaining)
    if change >= TP2_PCT:
        return ("TP2", remaining)
    if change >= TP1_PCT and not pos.get("tp1_done"):
        return ("TP1", remaining / 2.0)
    return ("HOLD", 0.0)


def main():
    pos = load_position()
    if pos is None:
        print("Tidak ada paper_ledger.json / trade — belum ada posisi paper.")
        return 2
    if pos.get("status") == "CLOSED":
        print(f"Posisi sudah CLOSED. Realisasi: Rp{pos['realized_idr']:,.0f}.")
        return 0
    try:
        tickers = get_json(f"{API}/tickers").get("tickers", {})
        t = tickers.get(pos["pair"]) or tickers.get("btc_idr")
        bid = float(t["buy"])
        ask = float(t["sell"])
    except Exception as e:
        print(f"CANNOT_EXIT: ticker gagal dibaca ({e}) — tidak ada harga tebakan.")
        return 0
    action, coin_sell = decide_exit(pos, bid)
    if action == "HOLD":
        value = pos["coin_remaining"] * bid
        change = (bid - pos["entry_ask"]) / pos["entry_ask"]
        print(f"HOLD: posisi {pos['coin_remaining']:.8f} BTC, nilai "
              f"Rp{value:,.0f} @ bid Rp{bid:,.0f}, perubahan "
              f"{change * 100:.3f}% (SL -5% / TP1 +10% / TP2 +15%).")
        save_position(pos)
        return 0
    proceeds = coin_sell * bid
    cost_part = pos["cost_idr_total"] * (coin_sell / pos["coin_total"])
    pnl = proceeds - cost_part
    pos["cash_idr"] += proceeds
    pos["coin_remaining"] -= coin_sell
    pos["realized_idr"] += pnl
    if action == "TP1":
        pos["tp1_done"] = True
        pos["status"] = "PARTIAL"
        print(f"TP1: jual separuh {coin_sell:.8f} BTC @ bid Rp{bid:,.0f} "
              f"= Rp{proceeds:,.0f}, P&L bagian Rp{pnl:,.0f}.")
    else:
        pos["status"] = "CLOSED"
        print(f"{action}: jual seluruh sisa {coin_sell:.8f} BTC @ bid "
              f"Rp{bid:,.0f} = Rp{proceeds:,.0f}, P&L Rp{pnl:,.0f}, "
              f"posisi CLOSED.")
    append_history({
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "event": action,
        "pair": pos["pair"],
        "coin_sold": coin_sell,
        "price_bid": bid,
        "proceeds_idr": round(proceeds, 2),
        "pnl_idr": round(pnl, 2),
        "remaining": pos["coin_remaining"],
    })
    save_position(pos)
    return 0


if __name__ == "__main__":
    sys.exit(main())
