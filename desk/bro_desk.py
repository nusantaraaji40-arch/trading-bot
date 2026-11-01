#!/usr/bin/env python3
"""DESK BRO v1 — meja trading paper 8 agen, GRATIS dan PAPER ONLY.

Satu siklus paper: tiap Bro mencetak verdict-nya. Bro 6 hanya mencatat
paper (bukan order nyata) bila semua gerbang lolos; bila tidak, NO_TRADE.

Delapan agen (penamaan user):
- Bro 1 CHIEF   : keputusan akhir beli/jual/tahan.
- Bro 2 SCAN    : menyaring market yang bergerak.
- Bro 3 VET     : menyaring scam/rug dan syarat likuiditas/volume.
- Bro 4 SOCIAL  : konteks sentimen/berita dari kata kunci saja.
- Bro 5 SIZE    : besar posisi sesuai aturan yang disetujui.
- Bro 6 FILLS   : eksekusi PAPER ONLY (tulis ledger, tidak pernah order).
- Bro 7 RISK    : aturan TP/SL/kill-switch.
- Bro 8 CRAWLER : kumpul data dari sumber publik gratis saja.

ATURAN KERAS:
- PAPER ONLY. Tidak ada order nyata, tidak ada tanda tangan wallet,
  tidak ada API key, tidak ada kredensial apa pun di file ini.
- Sumber data gratis saja: Gamma/CLOB publik Polymarket, CoinGecko
  gratis. TIDAK ADA run Actor Apify (berbayar) dan TIDAK ADA API
  berbayar di sini.
- Modal demo: Rp25.000 per venue/aset, trade pertama Rp5.000.
  Biaya (fee) TIDAK dimodelkan di v1 — P&L paper di sini adalah
  P&L kotor sebelum fee, dan itu ditulis jelas di laporan.
- Skrip ini ONE-SHOT (satu siklus lalu berhenti). Operasi 24/7
  TIDAK diklaim: jalan terus hanya bila user menjalankan loop ini
  di server miliknya sendiri (mis. Wispbyte gratis). VM Muse tidak
  pernah dipakai untuk live.

Jalankan: python3 desk/bro_desk.py
State paper: desk/paper_desk_ledger.json (dibuat saat ada paper buy
pertama; file state tidak dimaksudkan ikut push repo).
Kode keluar: 0 = siklus selesai (termasuk NO_TRADE/HOLD),
2 = data publik gagal diambil (siklus dilewati, bukan ditebak).
"""

import json
import os
import sys
import urllib.request
from datetime import datetime, timezone

# ---------------------------------------------------------------- aturan
CAPITAL_IDR = 25000
FIRST_TRADE_IDR = 5000
KILL_SWITCH_FLOOR_IDR = 21250  # 25000 - 15%
SL_PCT = 5.0
TP_PCT = 15.0
MIN_LIQUIDITY_USD = 500.0
MAX_SPREAD_PCT = 20.0
MIN_SHARES = 5

GAMMA = "https://gamma-api.polymarket.com/markets"
COINGECKO_USDC_IDR = ("https://api.coingecko.com/api/v3/simple/price"
                      "?ids=usd-coin&vs_currencies=idr")

BASE = os.path.dirname(os.path.abspath(__file__))
DEFAULT_STATE = os.path.join(BASE, "paper_desk_ledger.json")

# Kata kunci sentimen (Bro 4) — hitung kemunculan saja, bukan model AI.
POSITIVE_WORDS = ("naik", "bullish", "untung", "profit", "rekor", "menang",
                  "rise", "gain", "surge", "bull", "win", "record")
NEGATIVE_WORDS = ("turun", "bearish", "rugi", "scam", "rug", "hack",
                  "fall", "loss", "crash", "bear", "fraud", "exploit")


def now_iso():
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


# ---------------------------------------------------------------- Bro 8
def fetch_json(url, timeout=15):
    req = urllib.request.Request(url, headers={"User-Agent": "desk-bro-v1"})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read().decode("utf-8"))


def fetch_gamma_markets(limit=50):
    """Bro 8: ambil market aktif dari Gamma publik (tanpa key)."""
    data = fetch_json(GAMMA + "?active=true&closed=false&limit=%d" % limit)
    if isinstance(data, dict):
        return data.get("data", data)
    return data


def fetch_usdc_idr():
    """Bro 8: kurs CoinGecko gratis. Gagal -> None (siklus dilewati)."""
    data = fetch_json(COINGECKO_USDC_IDR)
    try:
        return float(data["usd-coin"]["idr"])
    except (KeyError, TypeError, ValueError):
        return None


# ---------------------------------------------------------------- Bro 4
def social_score(headlines):
    """Skor kata kunci: +1 per kata positif, -1 per kata negatif.

    `headlines` = list string (judul berita/RSS). Bukan prediksi,
    hanya konteks: skor <= -3 dianggap sentimen buruk.
    """
    score = 0
    for text in headlines or []:
        low = text.lower()
        for word in POSITIVE_WORDS:
            if word in low:
                score += 1
        for word in NEGATIVE_WORDS:
            if word in low:
                score -= 1
    return score


# ---------------------------------------------------------------- Bro 2
def scan_candidates(markets):
    """Bro 2: urutkan market aktif dari Gamma berdasarkan likuiditas.

    Mengembalikan list kandidat (dict Gamma) yang aktif dan belum tutup.
    """
    out = []
    for market in markets or []:
        if market.get("closed"):
            continue
        if market.get("active") is False:
            continue
        out.append(market)
    try:
        out.sort(key=lambda m: float(m.get("liquidity") or 0), reverse=True)
    except (TypeError, ValueError):
        pass
    return out


def cheapest_ask(market):
    """Harga ask termurah dari outcomePrices (sisi YES/NO).

    Gamma tidak memberi order book; v1 memakai outcomePrices sebagai
    proksi harga. Bila tidak ada harga yang valid -> None.
    """
    prices = market.get("outcomePrices")
    if isinstance(prices, str):
        try:
            prices = json.loads(prices)
        except ValueError:
            return None
    if not isinstance(prices, list):
        return None
    valid = []
    for price in prices:
        try:
            value = float(price)
        except (TypeError, ValueError):
            continue
        if 0 < value < 1:
            valid.append(value)
    return min(valid) if valid else None


# ---------------------------------------------------------------- Bro 3
def vet_market(market):
    """Bro 3: loloskan hanya market yang memenuhi syarat minimum.

    Mengembalikan (lolos: bool, alasan: list[str]).
    """
    reasons = []
    if market.get("closed"):
        reasons.append("market sudah tutup")
    if market.get("active") is False:
        reasons.append("market tidak aktif")
    try:
        liquidity = float(market.get("liquidity") or 0)
    except (TypeError, ValueError):
        liquidity = 0
    if liquidity < MIN_LIQUIDITY_USD:
        reasons.append("likuiditas < $%.0f" % MIN_LIQUIDITY_USD)
    spread = market.get("spread_pct")
    if spread is not None:
        try:
            if float(spread) > MAX_SPREAD_PCT:
                reasons.append("spread > %.0f%%" % MAX_SPREAD_PCT)
        except (TypeError, ValueError):
            pass
    if cheapest_ask(market) is None:
        reasons.append("tidak ada harga ask valid")
    return (not reasons, reasons)


# ---------------------------------------------------------------- Bro 5
def size_trade(cash_idr, price_idr_per_share):
    """Bro 5: jumlah lembar paper dari anggaran trade pertama.

    Anggaran = min(Rp5.000, kas). 0 bila harga tidak valid, kas tidak
    cukup, atau hasil < 5 lembar (minimum order).
    """
    if price_idr_per_share is None or price_idr_per_share <= 0:
        return 0
    budget = min(FIRST_TRADE_IDR, cash_idr)
    shares = int(budget // price_idr_per_share)
    if shares < MIN_SHARES:
        return 0
    return shares


# ---------------------------------------------------------------- Bro 7
def risk_decision(entry_ask, current_ask, current_bid,
                  cash_idr, position_value_at_bid_idr):
    """Bro 7: TP/SL/kill-switch untuk posisi paper yang sedang OPEN.

    Prioritas: kill-switch > SL > TP > HOLD (paling protektif menang).
    Trigger diukur ask-ke-ask (seperti paper_exit.py); hasil jual
    dihitung di BID. current_bid None -> CANNOT_EXIT (tanpa tebakan).
    """
    if current_bid is None:
        return "CANNOT_EXIT"
    if cash_idr + position_value_at_bid_idr <= KILL_SWITCH_FLOOR_IDR:
        return "KILL_SWITCH"
    if entry_ask is None or entry_ask <= 0 or current_ask is None:
        return "HOLD"
    change_pct = (current_ask - entry_ask) / entry_ask * 100.0
    if change_pct <= -SL_PCT:
        return "SL"
    if change_pct >= TP_PCT:
        return "TP"
    return "HOLD"


# ---------------------------------------------------------------- Bro 1
def chief_decision(gates):
    """Bro 1: keputusan akhir dari semua gerbang.

    `gates` = dict berisi scanned, vetted, social_ok, sized, no_open,
    data_ok (bool). Semua harus True untuk BUY, selain itu NO_TRADE.
    """
    failed = [name for name, ok in gates.items() if not ok]
    if failed:
        return ("NO_TRADE", "gerbang gagal: " + ", ".join(sorted(failed)))
    return ("BUY", "semua gerbang lolos")


# ------------------------------------------------------------ state paper
def load_state(path):
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as handle:
            return json.load(handle)
    return {"cash_idr": CAPITAL_IDR, "position": None, "history": []}


def save_state(path, state):
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as handle:
        json.dump(state, handle, indent=1, ensure_ascii=False)
    os.replace(tmp, path)


# ------------------------------------------------------------ satu siklus
def run_cycle(state_path=DEFAULT_STATE, markets=None, rate=None,
              headlines=None):
    """Jalankan satu siklus desk. Mengembalikan dict laporan siklus.

    `markets`, `rate`, `headlines` boleh diinjeksikan (untuk tes);
    bila None, diambil dari sumber publik gratis.
    """
    report = {"time": now_iso(), "bros": {}, "action": "NO_TRADE"}
    state = load_state(state_path)
    cash = float(state["cash_idr"])
    position = state["position"]

    # Bro 8 — kumpul data.
    try:
        if markets is None:
            markets = fetch_gamma_markets()
        if rate is None:
            rate = fetch_usdc_idr()
    except Exception as exc:  # jaringan gagal: jangan tebak data
        report["bros"]["Bro 8 CRAWLER"] = "NO_DATA (%s)" % exc
        report["action"] = "NO_DATA"
        return report
    if rate is None:
        report["bros"]["Bro 8 CRAWLER"] = "NO_DATA (kurs gagal)"
        report["action"] = "NO_DATA"
        return report
    report["bros"]["Bro 8 CRAWLER"] = (
        "OK: %d market, kurs Rp%.0f/USDC" % (len(markets or []), rate))

    # Posisi OPEN: cek exit dulu (Bro 7), tidak beli baru selagi OPEN.
    if position is not None:
        current = None
        for market in markets or []:
            if market.get("conditionId") == position.get("condition_id"):
                current = market
                break
        if current is None:
            report["bros"]["Bro 7 RISK"] = "CANNOT_EXIT (market tidak ketemu)"
            report["action"] = "HOLD"
            return report
        ask = cheapest_ask(current)
        # KETERBATASAN v1: Gamma market list tidak membawa order book,
        # jadi harga ask dipakai sebagai proksi bid. P&L exit v1 dengan
        # demikian bersifat perkiraan (cenderung optimistis) dibanding
        # book CLOB nyata yang dipakai paper_exit.py. Lihat DESK-BRO.md.
        bid = ask
        value_at_bid = position["shares"] * bid * rate if bid else 0
        decision = risk_decision(position["entry_ask"], ask, bid,
                                 cash, value_at_bid)
        report["bros"]["Bro 7 RISK"] = decision
        if decision in ("TP", "SL", "KILL_SWITCH"):
            proceeds = position["shares"] * bid * rate
            realized = proceeds - position["entry_cost_idr"]
            state["cash_idr"] = cash + proceeds
            state["history"].append({
                "type": "SELL_PAPER", "reason": decision,
                "question": position["question"],
                "shares": position["shares"], "proceeds_idr": proceeds,
                "realized_idr": realized, "time": now_iso()})
            state["position"] = None
            save_state(state_path, state)
            report["action"] = "SELL_PAPER_" + decision
            report["realized_idr"] = realized
            report["bros"]["Bro 6 FILLS"] = (
                "PAPER SELL %d lembar = Rp%.0f (realized Rp%.0f)"
                % (position["shares"], proceeds, realized))
            report["bros"]["Bro 1 CHIEF"] = "JUAL (paper): " + decision
        elif decision == "CANNOT_EXIT":
            report["action"] = "CANNOT_EXIT"
        else:
            report["action"] = "HOLD"
            report["bros"]["Bro 1 CHIEF"] = "TAHAN posisi paper"
        return report

    # Tidak ada posisi: cari kandidat baru.
    candidates = scan_candidates(markets)
    report["bros"]["Bro 2 SCAN"] = (
        "OK: %d kandidat" % len(candidates) if candidates
        else "NO_TRADE (tidak ada kandidat)")
    score = social_score(headlines)
    report["bros"]["Bro 4 SOCIAL"] = "skor %d" % score
    social_ok = score > -3

    chosen = None
    for market in candidates:
        ok, reasons = vet_market(market)
        if ok:
            chosen = market
            break
    if chosen is None:
        report["bros"]["Bro 3 VET"] = "NO_TRADE (semua kandidat gagal vet)"
        report["bros"]["Bro 1 CHIEF"] = "NO_TRADE (vet)"
        return report
    report["bros"]["Bro 3 VET"] = "LOLOS: %s" % chosen.get("question")

    ask = cheapest_ask(chosen)
    price_idr = ask * rate if ask else None
    shares = size_trade(cash, price_idr)
    report["bros"]["Bro 5 SIZE"] = (
        "%d lembar @ Rp%.0f" % (shares, price_idr)
        if shares else "NO_TRADE (di bawah minimum 5 lembar)")
    gates = {"scanned": bool(candidates), "vetted": True,
             "social_ok": social_ok, "sized": shares > 0,
             "no_open": True, "data_ok": True}
    verdict, reason = chief_decision(gates)
    report["bros"]["Bro 1 CHIEF"] = "%s (%s)" % (verdict, reason)
    if verdict != "BUY":
        return report

    # Bro 6 — PAPER ONLY: tulis ledger, tidak pernah order nyata.
    cost = shares * ask * rate
    state["cash_idr"] = cash - cost
    state["position"] = {
        "question": chosen.get("question"),
        "condition_id": chosen.get("conditionId"),
        "shares": shares, "entry_ask": ask,
        "entry_cost_idr": cost, "rate": rate}
    state["history"].append({
        "type": "BUY_PAPER", "question": chosen.get("question"),
        "shares": shares, "ask": ask, "cost_idr": cost, "time": now_iso()})
    save_state(state_path, state)
    report["action"] = "BUY_PAPER"
    report["bros"]["Bro 6 FILLS"] = (
        "PAPER BUY %d lembar @ %.3f = Rp%.0f" % (shares, ask, cost))
    return report


def main():
    report = run_cycle()
    print("=== DESK BRO v1 — siklus paper %s ===" % report["time"])
    for name in ("Bro 8 CRAWLER", "Bro 2 SCAN", "Bro 3 VET", "Bro 4 SOCIAL",
                 "Bro 5 SIZE", "Bro 7 RISK", "Bro 6 FILLS", "Bro 1 CHIEF"):
        if name in report["bros"]:
            print("%s: %s" % (name, report["bros"][name]))
    print("AKSI: %s" % report["action"])
    if "realized_idr" in report:
        print("REALIZED PAPER: Rp%.0f (kotor, sebelum fee)" % report["realized_idr"])
    print("CATATAN: paper only — bukan order nyata, bukan jaminan profit.")
    return 0 if report["action"] != "NO_DATA" else 2


if __name__ == "__main__":
    sys.exit(main())
