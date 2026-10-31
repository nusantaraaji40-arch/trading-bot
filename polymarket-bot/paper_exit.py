"""Exit manager paper Polymarket — logika jual TP/SL lengkap (PAPER ONLY).

Membaca posisi paper terbaru dari paper_ledger.json, mengecek harga LIVE
(CLOB book + kurs CoinGecko), lalu memutuskan: HOLD, jual sebagian (TP1),
atau jual semua (TP2 / SL / kill-switch). TIDAK ADA order nyata, TIDAK
ADA pemanggilan withdraw, TIDAK ADA key/secret di file ini.

Keputusan desain (penting, dibaca dulu):
- Trigger diukur ask-ke-ask: level TP/SL dibandingkan dengan ASK saat
  ini terhadap ASK entry yang tercatat. Alasannya: spread market ini
  0,001 pada harga 0,013 (sekitar 7,7%) LEBIH BESAR dari SL 5% — kalau
  trigger diukur bid lawan ask entry, posisi akan langsung kena SL
  karena spread saja, padahal harga belum bergerak. Hasil jual tetap
  dihitung di BID (yang benar-benar diterima penjual), jadi P&L yang
  dilaporkan adalah P&L nyata setelah spread.
- TP bertangga (parsial): TP1 +10% menjual SEPARUH sisa; TP2 +15%
  menjual SELURUH sisa (hanya setelah TP1). SL -5% menjual seluruh
  sisa. Kill-switch 15% menjual seluruh sisa bila total nilai paper
  (kas + posisi di harga bid) jatuh ke level kill-switch.
- Prioritas bila beberapa trigger bersamaan: kill-switch > SL > TP2
  > TP1 (yang paling protektif menang).
- Book kosong / tidak tersedia: TIDAK BISA EXIT — posisi dipertahankan
  dan dilaporkan, tanpa harga tebakan. Market yang sudah resolusi
  tidak diselesaikan dari tebakan; penyelesaiannya dicek terpisah.

State posisi: paper_position.json (workspace). Riwayat exit ditambah
ke paper_history.jsonl (hanya aksi jual; cek HOLD tidak mengotori
riwayat). File state JSON tidak ikut push repo.

Posisi yang dilacak = trade terbaru di paper_ledger.json. Bila ledger
lebih baru dari state posisi yang tersimpan (trade baru setelah posisi
lama CLOSED), state diinisialisasi ulang otomatis dari ledger baru.
Posisi CLOSED dari ledger yang sama TIDAK pernah dibangkitkan lagi.

Kode keluar: 0 = ok (termasuk HOLD / CLOSED / CANNOT_EXIT),
2 = konfigurasi tidak lengkap (tidak ada ledger / kurs gagal),
1 = error tak terduga.
"""

import json
import os
import sys
import urllib.request
from datetime import datetime, timezone

CLOB_BOOK = "https://clob.polymarket.com/book"
COINGECKO_USDC_IDR = ("https://api.coingecko.com/api/v3/simple/price"
                       "?ids=usd-coin&vs_currencies=idr")
WORKSPACE = "/home/hatch/workspace/polymarket-bot"
LEDGER_PATH = os.path.join(WORKSPACE, "paper_ledger.json")
POSITION_PATH = os.path.join(WORKSPACE, "paper_position.json")
HISTORY_PATH = os.path.join(WORKSPACE, "paper_history.jsonl")

START_IDR = 50000.0
SL_PCT = 5.0
TP1_PCT = 10.0
TP2_PCT = 15.0
KILL_SWITCH_PCT = 15.0


def get_json(url, timeout=30):
    req = urllib.request.Request(url, headers={"User-Agent": "muse-paper-demo/1.0"})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read().decode("utf-8"))


def decide_exit(entry_ask, bid, ask, remaining, tp1_done, total_value_idr,
                start_idr=START_IDR, kill_switch_pct=KILL_SWITCH_PCT,
                sl_pct=SL_PCT, tp1_pct=TP1_PCT, tp2_pct=TP2_PCT):
    """Fungsi murni: (aksi, jumlah, alasan).

    Aksi: 'HOLD', 'SELL_PARTIAL', 'SELL_ALL'. Alasan: 'HOLD',
    'TP1', 'TP2', 'SL', 'KILL_SWITCH'.
    """
    if remaining <= 0:
        return "HOLD", 0, "HOLD"
    if total_value_idr <= start_idr * (1 - kill_switch_pct / 100):
        return "SELL_ALL", remaining, "KILL_SWITCH"
    if ask <= entry_ask * (1 - sl_pct / 100):
        return "SELL_ALL", remaining, "SL"
    if tp1_done and ask >= entry_ask * (1 + tp2_pct / 100):
        return "SELL_ALL", remaining, "TP2"
    if (not tp1_done) and ask >= entry_ask * (1 + tp1_pct / 100):
        qty = remaining // 2 if remaining >= 2 else remaining
        action = "SELL_PARTIAL" if qty < remaining else "SELL_ALL"
        return action, qty, "TP1"
    return "HOLD", 0, "HOLD"


def load_position(ledger, position_path=POSITION_PATH):
    """Muat state posisi; inisialisasi dari ledger bila belum ada atau
    bila ledger lebih baru (trade baru setelah posisi lama CLOSED).

    Posisi CLOSED dari ledger yang sama tidak pernah dibangkitkan lagi:
    ledger lama (timestamp <= last_check) selalu mengembalikan state
    tersimpan.
    """
    if os.path.isfile(position_path):
        with open(position_path) as f:
            pos = json.load(f)
        if pos.get("ledger_timestamp") is not None:
            if pos["ledger_timestamp"] == ledger["timestamp"]:
                return pos
        elif pos.get("last_check") is not None:
            if ledger["timestamp"] <= pos["last_check"]:
                return pos
    trade = ledger["paper_trade"]
    shares = int(trade["shares"])
    return {
        "market": ledger["market"],
        "token_id": ledger["token_id"],
        "ledger_timestamp": ledger["timestamp"],
        "entry_ask": trade["price_usdc"],
        "shares_total": shares,
        "remaining": shares,
        "cost_per_share_idr": round(trade["cost_idr"] / shares, 2),
        "cash_after_buy_idr": ledger["virtual_balance_after_idr"],
        "realized_idr": 0.0,
        "tp1_done": False,
        "status": "OPEN",
        "last_check": None,
    }


def save_position(pos):
    with open(POSITION_PATH, "w") as f:
        json.dump(pos, f, indent=2)


def append_history(record):
    try:
        with open(HISTORY_PATH, "a") as f:
            f.write(json.dumps(record) + "\n")
    except OSError as e:
        print(f"Riwayat exit gagal ditambah ({e}).")


def main():
    if not os.path.isfile(LEDGER_PATH):
        print("Tidak ada paper_ledger.json — belum ada posisi paper.")
        return 2
    with open(LEDGER_PATH) as f:
        ledger = json.load(f)
    if ledger.get("paper_trade") is None:
        print("Ledger terakhir tidak berisi trade (trade dilewati).")
        return 2
    pos = load_position(ledger)
    if pos["remaining"] <= 0:
        print(f"Posisi sudah CLOSED. Realisasi: Rp{pos['realized_idr']:,.0f}.")
        return 0

    try:
        rate = float(get_json(COINGECKO_USDC_IDR, timeout=20)["usd-coin"]["idr"])
    except Exception as e:
        print(f"Kurs USDC/IDR gagal diambil ({e}); exit ditunda.")
        return 2
    try:
        book = get_json(f"{CLOB_BOOK}?token_id={pos['token_id']}")
    except Exception as e:
        print(f"Book gagal diambil ({e}); exit ditunda.")
        return 2
    bids = book.get("bids", [])
    asks = book.get("asks", [])
    if not bids or not asks:
        print("CANNOT_EXIT: book kosong/tidak tersedia — posisi "
              "dipertahankan, tanpa harga tebakan.")
        pos["last_check"] = datetime.now(timezone.utc).isoformat()
        save_position(pos)
        return 0
    bid = max(float(b["price"]) for b in bids)
    ask = min(float(a["price"]) for a in asks)
    mid = (bid + ask) / 2
    spread_pct = (ask - bid) / mid * 100 if mid else 0

    entry = pos["entry_ask"]
    sl_price = entry * (1 - SL_PCT / 100)
    tp1_price = entry * (1 + TP1_PCT / 100)
    tp2_price = entry * (1 + TP2_PCT / 100)
    position_value = pos["remaining"] * bid * rate
    total = pos["cash_after_buy_idr"] + pos["realized_idr"] + position_value
    ks_level = START_IDR * (1 - KILL_SWITCH_PCT / 100)

    print(f"Market: {pos['market']}")
    print(f"Bid: {bid:.3f} | Ask: {ask:.3f} | Mid: {mid:.4f} | "
          f"Spread: {spread_pct:.1f}% | Kurs: Rp{rate:,.0f}/USDC")
    print(f"Entry ask: {entry:.3f} | SL: {sl_price:.4f} | TP1: {tp1_price:.4f} "
          f"| TP2: {tp2_price:.4f} | Kill-switch: {ks_level:,.0f}")
    print(f"Sisa: {pos['remaining']} lembar | Nilai posisi (bid): "
          f"Rp{position_value:,.0f} | Total paper: Rp{total:,.0f}")
    if spread_pct > 10:
        print("PERINGATAN: spread lebar (>10%) — hasil jual bisa jauh di "
              "bawah level trigger.")

    action, qty, reason = decide_exit(
        entry, bid, ask, pos["remaining"], pos["tp1_done"], total)
    now = datetime.now(timezone.utc).isoformat()
    pos["last_check"] = now
    pos["last_bid"] = bid
    pos["last_ask"] = ask
    if action == "HOLD":
        save_position(pos)
        print("Keputusan: HOLD — tidak ada level yang tersentuh.")
        return 0
    proceeds_usdc = qty * bid
    proceeds_idr = proceeds_usdc * rate
    pnl_idr = round(proceeds_idr - qty * pos["cost_per_share_idr"], 2)
    pos["remaining"] -= qty
    pos["realized_idr"] = round(pos["realized_idr"] + pnl_idr, 2)
    if reason == "TP1":
        pos["tp1_done"] = True
    pos["status"] = "CLOSED" if pos["remaining"] == 0 else "PARTIAL"
    save_position(pos)
    append_history({
        "type": "EXIT",
        "timestamp": now,
        "market": pos["market"],
        "reason": reason,
        "qty": qty,
        "price_bid_usdc": bid,
        "proceeds_usdc": round(proceeds_usdc, 4),
        "proceeds_idr": round(proceeds_idr, 2),
        "pnl_idr": pnl_idr,
        "remaining": pos["remaining"],
    })
    print(f"Keputusan: {action} {qty} lembar ({reason}) @ bid {bid:.3f} "
          f"USDC = Rp{proceeds_idr:,.0f} | P&L aksi: Rp{pnl_idr:,.0f} | "
          f"Sisa: {pos['remaining']} | Status: {pos['status']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
