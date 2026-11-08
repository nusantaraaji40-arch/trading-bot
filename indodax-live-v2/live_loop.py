#!/usr/bin/env python3
"""Loop otomatis live Indodax SPOT (Trade API V2) — SATU file mandiri.

Alur (berurutan, 1 posisi dalam satu waktu):
  1. Baca saldo + posisi (koin yang dipegang).
  2. Jika ada posisi: pantau harga tiap poll_seconds. Jual HABIS saat:
     - TP: bid >= entry * (1 + TP%)            (default 15%)
     - SL: bid <= entry * (1 - SL%)            (default 30%)
     - Kill-switch: total saldo (IDR + nilai posisi di bid) <= lantai
       kill-switch (default Rp16.468). Prioritas: KS > SL > TP.
     Jual TP pakai LIMIT di bid; SL/KS pakai MARKET (segera).
     Setiap jual DIVERIFIKASI via saldo (pelajaran 13:04: respons error
     belum tentu tidak terisi; saldo yang menentukan).
  3. Jika tidak ada posisi: saring universe (CoinGecko top-50 ->
     filter listing Indodax -> buang stablecoin -> 10 momentum terbaik +
     10 kapitalisasi terbesar), pilih momentum tertinggi. Bila tidak ada
     momentum positif, TUNGGU (tidak beli).
  4. Beli 1 koin terbaik (LIMIT di ask, modal = min(max_buy_idr,
     saldo bebas - buffer fee), verifikasi via saldo), lalu kembali
     memantau.
  5. Kill-switch global: jual SEMUA + BERHENTI (tidak lanjut siklus).

Keamanan: SPOT saja (tanpa leverage/margin/futures/likuidasi), TANPA
pemanggilan withdraw dalam bentuk apa pun, nilai key/secret TIDAK
PERNAH dicetak. Loop HANYA jalan bila LIVE_TRADING=1 di environment
DAN LIVE_APPROVED.txt ada di folder skrip. Hentikan kapan saja dengan
tombol Stop di panel (panel tidak me-restart otomatis).

Aturan default = yang disetujui pemilik 2026-11-01 (lihat banner saat
start). Bila loop_params.json ada di folder skrip, nilainya MENGGANTI
default (harus lolos validasi); bila tidak ada, default dipakai.
File loop_params.example.json mendokumentasikan formatnya.
"""

import hashlib
import hmac
import json
import os
import sys
import time
import traceback
import urllib.error
import urllib.parse
import urllib.request

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_URL = os.environ.get("INDODAX_V2_BASE_URL", "https://api.indodax.com")
PUBLIC_URL = "https://indodax.com"
USER_AGENT = ("Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
              "(KHTML, like Gecko) Chrome/126.0 Safari/537.36")
TIMEOUT = 30

# Harga order 13:04 (acuan BILA riwayat tak terbaca, khusus BTC/IDR).
BTC_FALLBACK_ENTRY = 1410454000

DEFAULTS = {
    "max_buy_idr": 20000,
    "fee_buffer_idr": 500,
    "sl_pct": 30,
    "tp_pct": 15,
    "ks_floor_idr": 16468,
    "poll_seconds": 60,
    "idle_screen_seconds": 600,
}

STABLECOINS = {"USDT", "USDC", "DAI", "USDE", "FDUSD", "TUSD", "USDP",
               "USD1", "PYUSD", "USDD", "USTC", "EURC", "XAUT"}

CG_URL = ("https://api.coingecko.com/api/v3/coins/markets"
          "?vs_currency=usd&order=market_cap_desc&per_page=50&page=1"
          "&price_change_percentage=24h")


def rp(n):
    if n is None:
        return "-"
    try:
        return f"Rp{float(n):,.0f}"
    except (TypeError, ValueError):
        return f"Rp{n}"


def load_keys():
    key = os.environ.get("INDODAX_API_KEY", "")
    secret = os.environ.get("INDODAX_SECRET", "")
    if not key or not secret:
        print("INDODAX_API_KEY / INDODAX_SECRET belum diset di environment.")
        print("Set keduanya dulu (export), jangan tulis di file atau chat.")
        sys.exit(2)
    print("API key terdeteksi dari environment (nilainya tidak dicetak).")
    return key, secret


def _quote(value):
    """Encode gaya JavaScript encodeURIComponent."""
    return urllib.parse.quote(str(value), safe="ABCDEFGHIJKLMNOPQRSTUVWXYZ"
                              "abcdefghijklmnopqrstuvwxyz0123456789-_.!~*'()")


def _sign(key, secret, params):
    """params: list [(k, v)] urutan tetap. Nonce milidetik ditambah di akhir."""
    ordered = list(params) + [("nonce", str(int(time.time() * 1000)))]
    canonical = "&".join(f"{_quote(k)}={_quote(v)}" for k, v in ordered)
    sig = hmac.new(secret.encode(), canonical.encode(),
                   hashlib.sha256).hexdigest()
    headers = {"User-Agent": USER_AGENT, "X-APIKEY": key, "Sign": sig}
    return canonical, headers


def _try_json(raw):
    try:
        return json.loads(raw)
    except ValueError:
        return {"_raw": raw[:500]}


def http_json(method, url, headers, body=None):
    """Satu request HTTP, mengembalikan (status, json-atau-teks)."""
    data = body.encode() if body is not None else None
    req = urllib.request.Request(url, data=data, headers=headers,
                                 method=method)
    try:
        with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
            raw = resp.read().decode("utf-8", "replace")
            return resp.status, _try_json(raw)
    except urllib.error.HTTPError as e:
        raw = e.read().decode("utf-8", "replace")
        return e.code, _try_json(raw)
    except Exception as e:
        return 0, {"_transport_error": f"{type(e).__name__}: {e}"}


def _is_error(status, payload):
    if isinstance(payload, dict):
        if payload.get("_transport_error"):
            return True
        if payload.get("is_error") is True:
            return True
        if payload.get("error"):
            return True
        if payload.get("success") == 0:
            return True
        code = payload.get("code")
        if isinstance(code, (int, float)) and code < 0:
            return True
    return not (200 <= status < 300)


def v2_get(key, secret, path, params):
    canonical, headers = _sign(key, secret, params)
    url = BASE_URL + path + "?" + canonical
    return http_json("GET", url, headers)


def v2_post(key, secret, path, params):
    canonical, headers = _sign(key, secret, params)
    headers["Content-Type"] = "application/x-www-form-urlencoded"
    url = BASE_URL + path
    return http_json("POST", url, headers, body=canonical)


def public_json(url):
    return http_json("GET", url, {"User-Agent": USER_AGENT})


def _num(value):
    try:
        if value is None or value == "":
            return None
        return float(value)
    except (TypeError, ValueError):
        return None


def _find_balances(node, out):
    """Kumpulkan saldo dari berbagai bentuk respons V2 secara defensif.

    Mengisi out[CODE] = (free, total). Bentuk yang dikenali: list item
    {asset|coin|currency, free|available, locked|total|balance}, dict
    bersarang {data|result|return|balances}, dan dict datar."""
    if isinstance(node, list):
        for item in node:
            _find_balances(item, out)
        return
    if not isinstance(node, dict):
        return
    for k in ("data", "result", "return", "balances", "balance", "assets"):
        if k in node:
            _find_balances(node[k], out)
    code = node.get("asset") or node.get("coin") or node.get("currency")
    if code and isinstance(code, str):
        code = code.upper()
        free = _num(node.get("free"))
        if free is None:
            free = _num(node.get("available"))
        locked = _num(node.get("locked"))
        total = _num(node.get("total"))
        if total is None:
            total = _num(node.get("balance"))
        if total is None and free is not None and locked is not None:
            total = free + locked
        if free is not None or total is not None:
            out[code] = (free, total)
        return
    for code_key, val in node.items():
        if not isinstance(code_key, str):
            continue
        code_up = code_key.upper()
        if code_up not in ("IDR", "BTC", "ETH"):
            continue
        if isinstance(val, dict):
            free = _num(val.get("free"))
            if free is None:
                free = _num(val.get("available"))
            locked = _num(val.get("locked"))
            total = _num(val.get("total"))
            if total is None:
                total = _num(val.get("balance"))
            if total is None and free is not None and locked is not None:
                total = free + locked
            if free is not None or total is not None:
                out[code_up] = (free, total)
        else:
            total = _num(val)
            if total is not None:
                out[code_up] = (None, total)


def qty_str(amount):
    return f"{amount:.8f}".rstrip("0").rstrip(".")


def get_balances(key, secret):
    """Kembalikan (balances_dict, payload) atau (None, payload) bila gagal."""
    status, payload = v2_get(key, secret, "/api/v2/account", [])
    if _is_error(status, payload):
        return None, payload
    balances = {}
    _find_balances(payload, balances)
    return balances, payload


def get_ticker(pair_id):
    """Kembalikan (bid, ask) atau (None, None) bila gagal."""
    status, payload = public_json(PUBLIC_URL + f"/api/ticker/{pair_id}")
    if _is_error(status, payload) or not isinstance(payload, dict):
        return None, None
    t = payload.get("ticker", {})
    if not isinstance(t, dict):
        return None, None
    return _num(t.get("buy")), _num(t.get("sell"))


def get_pairs():
    """Kembalikan {BASE: {pair_id, min_cost, min_traded}} (pair /IDR saja)."""
    status, payload = public_json(PUBLIC_URL + "/api/pairs")
    if _is_error(status, payload) or not isinstance(payload, list):
        return {}
    out = {}
    for item in payload:
        if not isinstance(item, dict):
            continue
        pid = item.get("id")
        if not isinstance(pid, str) or not pid.endswith("idr"):
            continue
        base = pid[:-3].upper()
        out[base] = {
            "pair_id": pid,
            "min_cost": _num(item.get("trade_min_base_currency")),
            "min_traded": _num(item.get("trade_min_traded_currency")),
        }
    return out


def _collect_fills(node, out):
    """Kumpulkan (side, price, qty, time) dari riwayat order/trade."""
    if isinstance(node, list):
        for item in node:
            _collect_fills(item, out)
        return
    if not isinstance(node, dict):
        return
    for k in ("data", "result", "return", "trades", "orders", "list",
              "history"):
        if k in node:
            _collect_fills(node[k], out)
    side = node.get("side")
    if not (side and isinstance(side, str)):
        return
    price = _num(node.get("price"))
    if price is None:
        price = _num(node.get("executedPrice")) or _num(node.get("avgPrice"))
    qty = _num(node.get("qty"))
    if qty is None:
        qty = _num(node.get("quantity"))
    if qty is None:
        qty = _num(node.get("executedQty"))
    if qty is None:
        qty = _num(node.get("origQty"))
    if not price or not qty:
        return
    st = node.get("status")
    if st is not None and str(st).upper() not in (
            "FILLED", "PARTIALLY_FILLED", "CLOSED", "DONE", "SUCCESS"):
        return
    t = (_num(node.get("time")) or _num(node.get("timestamp"))
         or _num(node.get("updateTime")))
    out.append((side.upper(), price, qty, t))


def get_entry_price(key, secret, pair_id):
    """Harga fill BUY terbaru untuk pair, atau (None, None) bila tak ketemu.

    Mencoba myTrades lalu order histories. Bentuk respons tidak pasti,
    jadi parser defensif; kegagalan di sini TIDAK menggagalkan loop
    (pemanggil memakai fallback / mode kill-switch saja)."""
    for path in ("/api/v2/myTrades", "/api/v2/order/histories"):
        status, payload = v2_get(key, secret, path, [("symbol", pair_id)])
        if _is_error(status, payload):
            continue
        fills = []
        _collect_fills(payload, fills)
        buys = [f for f in fills if f[0] == "BUY"]
        if not buys:
            continue
        buys.sort(key=lambda f: (f[3] is not None, f[3] or 0))
        return buys[-1][1], path
    return None, None


def screen_universe(pairs):
    """Saring universe dari CoinGecko + listing Indodax.

    Kembalikan (universe, pick, catatan). Universe = 10 momentum
    terbaik + 10 kapitalisasi terbesar (dedup, maks 20). Pick = momentum
    tertinggi bila > 0%, else None (tidak beli)."""
    status, cg = public_json(CG_URL)
    if _is_error(status, cg) or not isinstance(cg, list):
        return None, None, "CoinGecko gagal dibaca"
    if not pairs:
        return None, None, "Daftar pair Indodax gagal dibaca"
    cands = []
    for c in cg:
        if not isinstance(c, dict):
            continue
        sym = (c.get("symbol") or "").upper()
        if not sym or sym in STABLECOINS:
            continue
        if sym not in pairs:
            continue
        chg = _num(c.get("price_change_percentage_24h"))
        mc = _num(c.get("market_cap"))
        if chg is None or mc is None:
            continue
        cands.append({
            "symbol": sym,
            "pair_id": pairs[sym]["pair_id"],
            "min_cost": pairs[sym]["min_cost"],
            "min_traded": pairs[sym]["min_traded"],
            "change": chg,
            "mcap": mc,
        })
    if not cands:
        return [], None, "Tidak ada koin universe yang lolos filter"
    best = sorted(cands, key=lambda x: x["change"], reverse=True)[:10]
    stable = sorted(cands, key=lambda x: x["mcap"], reverse=True)[:10]
    universe = []
    seen = set()
    for x in best + stable:
        if x["symbol"] not in seen:
            seen.add(x["symbol"])
            universe.append(x)
    pick = best[0] if best and best[0]["change"] > 0 else None
    note = "" if pick else "Momentum terbaik <= 0% — tunggu (tidak beli)"
    return universe, pick, note


def compute_buy_idr(free_idr, cfg):
    """Nominal beli: min(max_buy, (bebas - buffer) / 1.002); None bila < 10rb."""
    if free_idr is None:
        return None
    buy = int((free_idr - cfg["fee_buffer_idr"]) / 1.002)
    buy = min(cfg["max_buy_idr"], buy)
    if buy < 10000:
        return None
    return buy


def decide_trigger(bid, entry, total_idr, cfg):
    """Prioritas: KS > SL > TP. Kembalikan 'KS'/'SL'/'TP'/None.

    Bila entry None, SL/TP tidak bisa dihitung (hanya KS). Bila bid None,
    SL/TP dilewati. Bila total None, KS dilewati (data tak lengkap)."""
    sl = tp = False
    if entry is not None and bid is not None:
        sl_line = entry * (1 - cfg["sl_pct"] / 100)
        tp_line = entry * (1 + cfg["tp_pct"] / 100)
        # Epsilon 1e-9 relatif: harga tepat di garis tetap terpicu meski
        # ada galat floating point (1e-9 * Rp1,4M = ~Rp1,4 — diabaikan).
        if bid <= sl_line * (1 + 1e-9):
            sl = True
        if bid >= tp_line * (1 - 1e-9):
            tp = True
    if total_idr is not None and total_idr <= cfg["ks_floor_idr"]:
        return "KS"
    if sl:
        return "SL"
    if tp:
        return "TP"
    return None


def _bal_total(bal, coin):
    if coin not in bal:
        return 0
    free, total = bal[coin]
    if total is not None:
        return total
    return free or 0


def verify_sold(bal_before, bal_after, coin, min_traded):
    """Terjual bila sisa < min_traded (debu) atau < 1% dari sebelumnya.

    Memakai TOTAL (bukan free): order jual yang masih terbuka memindah
    koin ke locked (total tetap) — itu BELUM terjual."""
    before = _bal_total(bal_before, coin)
    after = _bal_total(bal_after, coin)
    if min_traded is not None and after < min_traded:
        return True
    if before > 0 and after < before * 0.01:
        return True
    return False


def verify_bought(bal_before, bal_after, coin, expected_qty):
    """Terbeli bila pertambahan total >= 99% dari qty yang diharapkan."""
    gained = _bal_total(bal_after, coin) - _bal_total(bal_before, coin)
    return gained >= expected_qty * 0.99


def place_limit(key, secret, pair_id, side, qty, price):
    params = [
        ("symbol", pair_id),
        ("side", side),
        ("quantity", qty_str(qty)),
        ("quoteOrderQty", "0"),
        ("type", "LIMIT"),
        ("price", str(int(price))),
        ("newClientOrderId", ""),
        ("selfTradePreventionMode", "EXPIRE_MAKER"),
        ("timeInForce", ""),
    ]
    return v2_post(key, secret, "/api/v2/order", params)


def place_market(key, secret, pair_id, side, qty):
    params = [
        ("symbol", pair_id),
        ("side", side),
        ("quantity", qty_str(qty)),
        ("quoteOrderQty", "0"),
        ("type", "MARKET"),
        ("newClientOrderId", ""),
    ]
    return v2_post(key, secret, "/api/v2/order", params)


def do_sell(key, secret, pair_id, qty, bid, method, bal_before, min_traded):
    """Kirim order jual + verifikasi via saldo. Kembalikan True bila terverifikasi.

    method: 'LIMIT' (pakai bid) atau 'MARKET'. Bila respons error TAPI
    saldo membuktikan terisi, dianggap BERHASIL (pelajaran 13:04)."""
    if method == "LIMIT" and bid:
        st, pl = place_limit(key, secret, pair_id, "SELL", qty, bid)
    else:
        method = "MARKET"
        st, pl = place_market(key, secret, pair_id, "SELL", qty)
    if _is_error(st, pl):
        print(f"Respons jual ({method}) HTTP {st}: "
              f"{json.dumps(pl, ensure_ascii=False)[:300]}")
    bal_after, _ = get_balances(key, secret)
    if bal_after is None:
        print("Verifikasi jual gagal (saldo tidak terbaca) — anggap BELUM terjual.")
        return False
    coin = pair_id[:-3].upper() if pair_id.endswith("idr") else pair_id.upper()
    if verify_sold(bal_before, bal_after, coin, min_traded):
        if _is_error(st, pl):
            print("Respons error TAPI saldo membuktikan TERJUAL — "
                  "dianggap BERHASIL (pelajaran 13:04).")
        return True
    return False


def load_loop_params():
    """Aturan loop: default (disetujui) + override opsional loop_params.json."""
    cfg = dict(DEFAULTS)
    path = os.path.join(SCRIPT_DIR, "loop_params.json")
    if not os.path.exists(path):
        print("loop_params.json tidak ada — pakai aturan default (disetujui).")
        return cfg
    try:
        with open(path) as f:
            user = json.load(f)
        for k in cfg:
            if k in user:
                cfg[k] = user[k]
    except Exception as e:
        print(f"loop_params.json tidak bisa dibaca ({e}) — pakai default.")
        return cfg
    errs = []
    if not (1 <= cfg["sl_pct"] <= 50):
        errs.append("sl_pct harus 1-50")
    if not (1 <= cfg["tp_pct"] <= 50):
        errs.append("tp_pct harus 1-50")
    if not (cfg["ks_floor_idr"] > 0):
        errs.append("ks_floor_idr harus > 0")
    if not (cfg["max_buy_idr"] > 0):
        errs.append("max_buy_idr harus > 0")
    if not (cfg["poll_seconds"] >= 10):
        errs.append("poll_seconds minimal 10")
    if not (cfg["idle_screen_seconds"] >= 60):
        errs.append("idle_screen_seconds minimal 60")
    if errs:
        print("loop_params.json DITOLAK:", "; ".join(errs))
        sys.exit(3)
    print("loop_params.json dipakai (mengganti default).")
    return cfg


def main():
    key, secret = load_keys()
    if os.environ.get("LIVE_TRADING") != "1":
        print("LIVE_TRADING=1 belum diset — loop live TIDAK jalan (aman).")
        print("Tambahkan export LIVE_TRADING='1'; di Startup Command "
              "untuk mengaktifkan.")
        return 2
    approved_path = os.path.join(SCRIPT_DIR, "LIVE_APPROVED.txt")
    if not os.path.exists(approved_path):
        print("Gerbang loop gagal: LIVE_APPROVED.txt tidak ditemukan.")
        return 2
    with open(approved_path) as f:
        approval_lines = f.read().strip().splitlines()
    print(f"Persetujuan tercatat: "
          f"{approval_lines[0] if approval_lines else '(kosong)'}")
    cfg = load_loop_params()
    print("MODE: LOOP LIVE (uang asli, SPOT saja, tanpa withdraw).")
    print(f"Aturan: 1 posisi | beli maks {rp(cfg['max_buy_idr'])} | "
          f"SL {cfg['sl_pct']}% | TP {cfg['tp_pct']}% jual habis | "
          f"lantai kill-switch {rp(cfg['ks_floor_idr'])} | "
          f"poll {cfg['poll_seconds']} dtk | saring idle "
          f"{cfg['idle_screen_seconds']} dtk.")
    print("PERINGATAN: loop ini MENJUAL + MEMBELI otomatis selama berjalan.")
    print("Hentikan kapan saja dengan tombol Stop di panel.")
    pairs = get_pairs()
    if not pairs:
        print("Peringatan: daftar pair gagal dibaca saat start "
              "(akan dicoba lagi tiap saring).")
    sell_override = {}
    entry_cache = {}
    warned_unknown = set()
    last_screen = 0
    while True:
        try:
            balances, _ = get_balances(key, secret)
            if balances is None:
                print("Baca saldo gagal — tunggu poll berikutnya.")
                time.sleep(cfg["poll_seconds"])
                continue
            idr_free = balances.get("IDR", (0, 0))[0] or 0
            idr_total_raw = balances.get("IDR", (0, 0))[1]
            idr_total = idr_total_raw if idr_total_raw is not None else idr_free
            positions = []
            for coin, (free, total) in balances.items():
                if coin == "IDR":
                    continue
                qty = total if total is not None else (free or 0)
                if qty <= 0:
                    continue
                locked = 0
                if free is not None and total is not None:
                    locked = max(0, total - free)
                info = pairs.get(coin)
                if info is not None and info.get("min_traded") is not None \
                        and qty < info["min_traded"]:
                    continue  # debu di bawah min traded — diabaikan
                positions.append((coin, qty, locked, info))
            if positions:
                bids = {}
                total_ok = True
                total_val = idr_total
                for coin, qty, locked, info in positions:
                    pid = (info["pair_id"] if info else coin.lower() + "idr")
                    if info is None and coin not in warned_unknown:
                        warned_unknown.add(coin)
                        print(f"Peringatan: {coin} tidak punya pair /IDR "
                              f"yang dikenal — tidak bisa dijual loop.")
                    bid, _ask = get_ticker(pid)
                    if bid is None:
                        total_ok = False
                    else:
                        bids[coin] = bid
                        total_val += qty * bid
                if not total_ok:
                    total_val = None
                    print("Total tidak lengkap (ada harga gagal dibaca) — "
                          "kill-switch dilewati poll ini.")
                if total_val is not None \
                        and total_val <= cfg["ks_floor_idr"]:
                    print(f"KILL-SWITCH: total {rp(total_val)} <= lantai "
                          f"{rp(cfg['ks_floor_idr'])} — jual SEMUA.")
                    for coin, qty, locked, info in positions:
                        if locked > 0:
                            print(f"{coin}: order terbuka — tunggu "
                                  f"(tidak menumpuk order baru).")
                            continue
                        if info is None:
                            continue
                        pid = info["pair_id"]
                        ok = do_sell(key, secret, pid, qty, bids.get(coin),
                                     "MARKET", balances,
                                     info.get("min_traded"))
                        print(f"KILL-SWITCH jual {coin}: "
                              f"{'TERVERIFIKASI' if ok else 'BELUM terverifikasi'}")
                        nb, _ = get_balances(key, secret)
                        if nb is not None:
                            balances = nb
                    # berhenti hanya bila sudah tidak ada posisi tradeable
                    nb, _ = get_balances(key, secret)
                    if nb is not None:
                        balances = nb
                    still = False
                    for coin, (free, total) in balances.items():
                        if coin == "IDR":
                            continue
                        qty = total if total is not None else (free or 0)
                        info = pairs.get(coin)
                        if info is not None and info.get("min_traded") \
                                is not None and qty < info["min_traded"]:
                            continue
                        if qty > 0 and info is not None:
                            still = True
                    if not still:
                        print("KILL-SWITCH SELESAI — loop berhenti "
                              "(tidak lanjut siklus).")
                        return 0
                    print("Kill-switch belum tuntas — coba lagi poll berikutnya.")
                    time.sleep(cfg["poll_seconds"])
                    continue
                for coin, qty, locked, info in positions:
                    if locked > 0:
                        print(f"{coin}: order terbuka — tunggu "
                              f"(tidak menumpuk order baru).")
                        continue
                    if info is None:
                        continue
                    pid = info["pair_id"]
                    bid = bids.get(coin)
                    if bid is None:
                        bid, _ask = get_ticker(pid)
                        if bid is None:
                            print(f"Harga {coin} gagal dibaca — lewati poll ini.")
                            continue
                    if coin not in entry_cache:
                        entry, src = get_entry_price(key, secret, pid)
                        if entry is None and coin == "BTC":
                            entry, src = BTC_FALLBACK_ENTRY, "asumsi (order 13:04)"
                        entry_cache[coin] = (entry, src)
                    entry, src = entry_cache[coin]
                    trig = decide_trigger(bid, entry, None, cfg)
                    if trig is None:
                        pct = (f"{(bid - entry) / entry * 100:+.2f}%"
                               if entry else "-")
                        print(f"{coin} bid {rp(bid)} | entry "
                              f"{rp(entry) if entry else '-'} ({src}) | "
                              f"{pct} | total "
                              f"{rp(total_val) if total_val is not None else '-'}")
                        continue
                    method = sell_override.get(pid) or \
                        ("LIMIT" if trig == "TP" else "MARKET")
                    print(f"{trig} {coin}: bid {rp(bid)} vs entry "
                          f"{rp(entry)} — jual {method}.")
                    ok = do_sell(key, secret, pid, qty, bid, method,
                                 balances, info.get("min_traded"))
                    if ok:
                        print(f"TERJUAL {coin} ({trig}).")
                        entry_cache.pop(coin, None)
                        sell_override.pop(pid, None)
                        nb, _ = get_balances(key, secret)
                        if nb is not None:
                            balances = nb
                    else:
                        print(f"Jual {coin} BELUM terverifikasi — coba metode "
                              f"lain poll berikutnya.")
                        sell_override[pid] = ("MARKET" if method == "LIMIT"
                                              else "LIMIT")
                time.sleep(cfg["poll_seconds"])
            else:
                now = time.time()
                if now - last_screen >= cfg["idle_screen_seconds"]:
                    last_screen = now
                    fresh = get_pairs()
                    if fresh:
                        pairs = fresh
                    universe, pick, note = screen_universe(pairs)
                    if universe is None:
                        print(f"Saring gagal: {note} — tunggu.")
                    elif pick is None:
                        print(f"Saring: universe {len(universe)} koin — {note}.")
                    else:
                        print(f"Saring: pick {pick['symbol']} "
                              f"({pick['change']:+.2f}% 24j) dari "
                              f"{len(universe)} koin.")
                        buy_idr = compute_buy_idr(idr_free, cfg)
                        if buy_idr is None:
                            print(f"Saldo bebas {rp(idr_free)} tidak cukup "
                                  f"untuk beli (min Rp10.000) — tunggu.")
                        elif pick["min_cost"] is not None \
                                and buy_idr < pick["min_cost"]:
                            print(f"Beli {pick['symbol']} dilewati: nominal "
                                  f"{rp(buy_idr)} < min cost "
                                  f"{rp(pick['min_cost'])}.")
                        else:
                            _bid, ask = get_ticker(pick["pair_id"])
                            if ask is None:
                                print(f"Ask {pick['symbol']} gagal dibaca — tunggu.")
                            else:
                                qty = int((buy_idr / ask) * 1e8) / 1e8
                                if qty <= 0 or (pick["min_traded"] is not None
                                               and qty < pick["min_traded"]):
                                    print(f"Beli {pick['symbol']} dilewati: "
                                          f"qty {qty} < min traded.")
                                else:
                                    bal_before, _ = get_balances(key, secret)
                                    if bal_before is None:
                                        bal_before = balances
                                    st, pl = place_limit(
                                        key, secret, pick["pair_id"], "BUY",
                                        qty, ask)
                                    print(f"Order beli {pick['symbol']}: {qty} "
                                          f"@ {rp(ask)} (HTTP {st}).")
                                    if _is_error(st, pl):
                                        print(f"Respons beli: "
                                              f"{json.dumps(pl, ensure_ascii=False)[:300]}")
                                    bal_after, _ = get_balances(key, secret)
                                    if bal_after is None:
                                        bal_after = bal_before
                                    if verify_bought(bal_before, bal_after,
                                                    pick["symbol"], qty):
                                        print(f"TERBELI {pick['symbol']} {qty} "
                                              f"@ ~{rp(ask)}.")
                                        entry_cache[pick["symbol"]] = (
                                            ask, "order loop")
                                        if _is_error(st, pl):
                                            print("Respons error TAPI saldo "
                                                  "membuktikan TERBELI — "
                                                  "dianggap BERHASIL "
                                                  "(pelajaran 13:04).")
                                    else:
                                        print(f"Beli {pick['symbol']} BELUM "
                                              f"terverifikasi via saldo — "
                                              f"tunggu saring berikutnya.")
                time.sleep(cfg["poll_seconds"])
        except KeyboardInterrupt:
            print("Loop dihentikan (KeyboardInterrupt).")
            return 0
        except Exception as e:
            traceback.print_exc()
            print(f"ERROR tak terduga: {e} — lanjut poll berikutnya.")
            time.sleep(cfg["poll_seconds"])
    return 0


if __name__ == "__main__":
    sys.exit(main())
