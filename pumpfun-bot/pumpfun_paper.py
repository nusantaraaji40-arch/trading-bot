#!/usr/bin/env python3
"""Paper trading Pump.fun (demo, tanpa uang asli, tanpa wallet).

Demo track Pump.fun (ke-5) memakai data publik gratis DexScreener
(tanpa key, tanpa koneksi chain — untuk demo, jaringan tidak
menghalangi apa-apa). Live Pump.fun nanti memang di Solana, tapi modul
paper ini tidak terhubung ke chain mana pun.

Filter kejujuran untuk ukuran demo Rp50.000 (~$3): hanya pair Pump.fun
(dexId pumpfun/pumpswap) dengan likuiditas >= $10.000 dan volume 24 jam
>= $5.000 yang boleh dibeli paper. Token meme tipis = slippage mematikan
di ukuran sekecil ini; kalau tidak ada yang lolos, keputusannya NO_TRADE
(bukan beli asal-asalan).

Aturan demo (sama seperti venue lain, dalam rupiah):
  modal virtual Rp50.000, trade pertama Rp10.000, SL 5%, TP 10%/15%,
  kill-switch 15% (lantai Rp42.500).
Kurs: USD/IDR live Frankfurter saat run; kalau kurs/data gagal
diambil, trade dilewati dan saldo tetap (tidak ada harga tebakan).
Nol order nyata; tidak ada wallet/keypair di modul ini.
"""

import json
import os
import urllib.request

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LEDGER_PATH = os.path.join(BASE_DIR, "pumpfun_ledger.json")
POSITION_PATH = os.path.join(BASE_DIR, "pumpfun_position.json")
HISTORY_PATH = os.path.join(BASE_DIR, "pumpfun_paper_history.jsonl")

VIRTUAL_START_IDR = 50000.0
FIRST_TRADE_IDR = 10000.0
SL_PCT = 0.05
TP1_PCT = 0.10
TP2_PCT = 0.15
KILL_SWITCH_PCT = 0.15
MIN_LIQUIDITY_USD = 10000.0
MIN_VOLUME_H24_USD = 5000.0
PUMP_DEX_IDS = {"pumpfun", "pumpswap"}
MAX_TOKENS_CHECKED = 15

PROFILES_URL = "https://api.dexscreener.com/token-profiles/latest/v1"
PAIRS_URL = "https://api.dexscreener.com/latest/dex/tokens/{}"
PAIR_URL = "https://api.dexscreener.com/latest/dex/pairs/solana/{}"
FRANKFURTER_URL = "https://api.frankfurter.app/latest?from=USD&to=IDR"


def fetch_json(url):
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "trading-bot-demo/1.0"})
        with urllib.request.urlopen(req, timeout=20) as resp:
            return json.load(resp)
    except Exception:
        return None


def load_json(path, default):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return default


def save_json(path, obj):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, indent=2, ensure_ascii=False)


def append_history(event):
    try:
        with open(HISTORY_PATH, "a", encoding="utf-8") as f:
            f.write(json.dumps(event, ensure_ascii=False) + "\n")
    except Exception:
        pass


def find_pump_pair():
    """Return pair dict terbaik yang lolos filter, atau (None, alasan)."""
    profiles = fetch_json(PROFILES_URL)
    if not profiles:
        return None, "fetch_profiles_failed"
    sol_tokens = [p for p in profiles if p.get("chainId") == "solana"]
    candidates = []
    for prof in sol_tokens[:MAX_TOKENS_CHECKED]:
        addr = prof.get("tokenAddress")
        if not addr:
            continue
        data = fetch_json(PAIRS_URL.format(addr))
        if not data:
            continue
        for pair in data.get("pairs") or []:
            if pair.get("dexId") not in PUMP_DEX_IDS:
                continue
            try:
                price = float(pair["priceUsd"])
                liq = float((pair.get("liquidity") or {}).get("usd") or 0)
                vol = float((pair.get("volume") or {}).get("h24") or 0)
            except Exception:
                continue
            if price <= 0 or liq < MIN_LIQUIDITY_USD or vol < MIN_VOLUME_H24_USD:
                continue
            candidates.append((vol, pair))
    if not candidates:
        return None, "no_pump_pair_passes_filter"
    candidates.sort(key=lambda x: x[0], reverse=True)
    return candidates[0][1], "ok"


def pair_price(pair_address):
    # Perbaikan 2026-11-01: dulu memakai endpoint /dex/tokens/ dengan
    # alamat PAIR (salah — endpoint itu untuk alamat TOKEN), sehingga
    # harga selalu gagal diambil dan run berakhir SKIP. Endpoint yang
    # benar untuk pair: /dex/pairs/solana/<pairAddress>.
    data = fetch_json(PAIR_URL.format(pair_address))
    if not data or not data.get("pairs"):
        return None
    try:
        return float(data["pairs"][0]["priceUsd"])
    except Exception:
        return None


def decide_exit(position, price_now, usd_idr_now, cash_idr):
    entry = position["entry_price_usd"]
    remaining = position["tokens_remaining"]
    value_remaining = remaining * price_now * usd_idr_now
    if cash_idr + value_remaining <= VIRTUAL_START_IDR * (1.0 - KILL_SWITCH_PCT):
        return ("KILL_SWITCH", remaining)
    change = (price_now - entry) / entry
    if change <= -SL_PCT:
        return ("SL", remaining)
    if change >= TP2_PCT:
        return ("TP2", remaining)
    if change >= TP1_PCT and not position.get("tp1_done"):
        return ("TP1", remaining / 2.0)
    return ("HOLD", 0.0)


def main():
    fx = fetch_json(FRANKFURTER_URL)
    ledger = load_json(LEDGER_PATH, {})
    position = load_json(POSITION_PATH, None)
    cash = float(ledger.get("cash_idr", VIRTUAL_START_IDR))
    if not fx:
        print("SKIP: kurs gagal diambil — trade dilewati, saldo tetap.")
        append_history({"event": "SKIP", "reason": "rate_fetch_failed"})
        return
    usd_idr = float(fx["rates"]["IDR"])

    if position is None or position.get("status") == "CLOSED":
        pair, reason = find_pump_pair()
        if pair is None:
            print(f"NO_TRADE: {reason} — tidak ada pair Pump.fun yang lolos filter likuiditas/volume.")
            print(json.dumps({"cash_idr": cash, "position": None}, ensure_ascii=False))
            append_history({"event": "NO_TRADE", "reason": reason})
            save_json(LEDGER_PATH, {"cash_idr": round(cash, 2), "position": None,
                                    "usd_idr": usd_idr, "source": "DexScreener + Frankfurter"})
            return
        price = float(pair["priceUsd"])
        symbol = pair.get("baseToken", {}).get("symbol", "?")
        tokens = (FIRST_TRADE_IDR / usd_idr) / price
        position = {
            "pair_address": pair.get("pairAddress"),
            "symbol": symbol,
            "dex": pair.get("dexId"),
            "side": "LONG",
            "status": "OPEN",
            "entry_price_usd": price,
            "entry_usd_idr": usd_idr,
            "tokens_total": tokens,
            "tokens_remaining": tokens,
            "cost_idr_total": FIRST_TRADE_IDR,
            "tp1_done": False,
            "realized_idr": 0.0,
        }
        cash -= FIRST_TRADE_IDR
        save_json(POSITION_PATH, position)
        print(f"OPEN: beli paper {tokens:.2f} {symbol} ({pair.get('dexId')}) senilai Rp{FIRST_TRADE_IDR:.0f} @ ${price}")
        append_history({"event": "OPEN", "symbol": symbol, "dex": pair.get("dexId"),
                        "entry_price_usd": price, "usd_idr": usd_idr, "cost_idr": FIRST_TRADE_IDR})
    else:
        price_now = pair_price(position["pair_address"])
        if price_now is None:
            print("SKIP: harga pair gagal diambil — posisi dibiarkan, saldo tetap.")
            append_history({"event": "SKIP", "reason": "price_fetch_failed"})
            return
        action, tok_sell = decide_exit(position, price_now, usd_idr, cash)
        if action == "HOLD":
            value = position["tokens_remaining"] * price_now * usd_idr
            change = (price_now - position["entry_price_usd"]) / position["entry_price_usd"]
            print(f"HOLD: posisi {position['tokens_remaining']:.2f} {position['symbol']}, nilai Rp{value:.0f}, perubahan {change * 100:.2f}% (SL -5% / TP1 +10% / TP2 +15%)")
        else:
            proceeds = tok_sell * price_now * usd_idr
            cost_part = position["cost_idr_total"] * (tok_sell / position["tokens_total"])
            pnl = proceeds - cost_part
            cash += proceeds
            position["tokens_remaining"] -= tok_sell
            position["realized_idr"] += pnl
            if action == "TP1":
                position["tp1_done"] = True
                print(f"TP1: jual separuh {tok_sell:.2f} {position['symbol']} @ ${price_now} = Rp{proceeds:.0f}, P&L bagian Rp{pnl:.0f}")
            else:
                position["status"] = "CLOSED"
                print(f"{action}: jual seluruh sisa {tok_sell:.2f} {position['symbol']} @ ${price_now} = Rp{proceeds:.0f}, P&L Rp{pnl:.0f}, posisi CLOSED")
            append_history({"event": action, "symbol": position["symbol"], "tokens_sold": tok_sell,
                            "price_usd": price_now, "proceeds_idr": proceeds, "pnl_idr": pnl})
            save_json(POSITION_PATH, position)

    ledger = {"cash_idr": round(cash, 2), "position": position,
              "usd_idr": usd_idr, "source": "DexScreener + Frankfurter"}
    save_json(LEDGER_PATH, ledger)
    print(json.dumps(ledger, ensure_ascii=False))


if __name__ == "__main__":
    main()
