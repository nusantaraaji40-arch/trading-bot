#!/usr/bin/env python3
"""Tes unit loop live (mocked, tanpa network, tanpa key asli).

Jalankan: python3 test_loop.py  (harus mencetak ALL_PASS)
File ini TIDAK ikut zip deploy (staging saja).
"""

import importlib.util
import json
import os
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location(
    "live_loop", os.path.join(HERE, "live_loop.py"))
loop = importlib.util.module_from_spec(spec)
spec.loader.exec_module(loop)

FAILS = []


def check(name, cond):
    print(("PASS " if cond else "FAIL ") + name)
    if not cond:
        FAILS.append(name)


# 1. Trigger: prioritas KS > SL > TP
cfg = dict(loop.DEFAULTS)
check("trigger TP", loop.decide_trigger(1622022100, 1410454000, 25000, cfg) == "TP")
check("trigger SL", loop.decide_trigger(987317800, 1410454000, 25000, cfg) == "SL")
check("trigger KS menang atas SL",
      loop.decide_trigger(900000000, 1410454000, 16000, cfg) == "KS")
check("trigger HOLD",
      loop.decide_trigger(1412504000, 1410454000, 25000, cfg) is None)
check("trigger entry None hanya KS",
      loop.decide_trigger(1500000000, None, 16000, cfg) == "KS")
check("trigger entry None tanpa KS",
      loop.decide_trigger(1500000000, None, 25000, cfg) is None)
check("trigger bid None tanpa KS",
      loop.decide_trigger(None, 1410454000, 25000, cfg) is None)

# 2. Nominal beli
check("buy cap 20000", loop.compute_buy_idr(28249, cfg) == 20000)
check("buy menyesuaikan saldo",
      loop.compute_buy_idr(19272, cfg) == int((19272 - 500) / 1.002))
check("buy di bawah min -> None", loop.compute_buy_idr(10500, cfg) is None)
check("buy saldo kecil -> None", loop.compute_buy_idr(5000, cfg) is None)
check("buy saldo None -> None", loop.compute_buy_idr(None, cfg) is None)

# 3. Screening (mocked public_json)
sample_cg = [
    {"symbol": "btc", "market_cap": 1000, "price_change_percentage_24h": 2.0},
    {"symbol": "eth", "market_cap": 900, "price_change_percentage_24h": -1.0},
    {"symbol": "sol", "market_cap": 800, "price_change_percentage_24h": 5.0},
    {"symbol": "usdt", "market_cap": 950, "price_change_percentage_24h": 0.01},
    {"symbol": "doge", "market_cap": 700, "price_change_percentage_24h": 3.0},
    {"symbol": "xyz", "market_cap": 600, "price_change_percentage_24h": 9.0},
]
sample_pairs = {
    "BTC": {"pair_id": "btcidr", "min_cost": 10000, "min_traded": 7e-06},
    "ETH": {"pair_id": "ethidr", "min_cost": 10000, "min_traded": 0.001},
    "SOL": {"pair_id": "solidr", "min_cost": 10000, "min_traded": 0.01},
    "DOGE": {"pair_id": "dogeidr", "min_cost": 10000, "min_traded": 1.0},
}
orig_public = loop.public_json
loop.public_json = lambda url: (200, sample_cg)
universe, pick, note = loop.screen_universe(sample_pairs)
check("screen universe isi", universe is not None and len(universe) == 4)
check("screen buang stablecoin",
      all(x["symbol"] != "USDT" for x in universe))
check("screen buang non-Indodax",
      all(x["symbol"] != "XYZ" for x in universe))
check("screen pick momentum tertinggi",
      pick is not None and pick["symbol"] == "SOL")
sample_neg = [dict(c, price_change_percentage_24h=-abs(c["price_change_percentage_24h"]) or -1.0)
              for c in sample_cg]
loop.public_json = lambda url: (200, sample_neg)
universe2, pick2, note2 = loop.screen_universe(sample_pairs)
check("screen semua negatif -> tidak beli", pick2 is None)
loop.public_json = orig_public

# 4. Parser fill riwayat
fills = []
loop._collect_fills([
    {"side": "BUY", "price": "1400000000", "qty": "0.00001417",
     "status": "FILLED", "time": 100},
    {"side": "BUY", "price": "1410454000", "qty": "0.00001417",
     "status": "FILLED", "time": 200},
    {"side": "BUY", "price": "1500000000", "qty": "0.00001",
     "status": "CANCELED", "time": 300},
    {"side": "SELL", "price": "1600000000", "qty": "0.00001417",
     "status": "FILLED", "time": 400},
], fills)
buys = [f for f in fills if f[0] == "BUY"]
buys.sort(key=lambda f: (f[3] is not None, f[3] or 0))
check("fill BUY terbaru (cancel dilewati)",
      buys and buys[-1][1] == 1410454000.0)
fills2 = []
loop._collect_fills({"data": [
    {"side": "BUY", "price": 1300000000, "executedQty": 0.00002,
     "time": 50}]}, fills2)
check("fill nested data", fills2 and fills2[0][1] == 1300000000.0)

# 5. Entry dari riwayat (mocked v2_get)
orig_v2 = loop.v2_get


def fake_v2_ok(key, secret, path, params):
    if path == "/api/v2/myTrades":
        return 200, [{"side": "BUY", "price": "1410454000",
                      "qty": "0.00001417", "time": 123}]
    return 404, {"error": "not found"}


loop.v2_get = fake_v2_ok
entry, src = loop.get_entry_price("K", "S", "btcidr")
check("entry dari myTrades", entry == 1410454000.0 and src == "/api/v2/myTrades")


def fake_v2_hist(key, secret, path, params):
    if path == "/api/v2/myTrades":
        return 400, {"code": -1002, "msg": "bad"}
    if path == "/api/v2/order/histories":
        return 200, {"data": [{"side": "BUY", "price": "1405000000",
                               "qty": "0.00001", "status": "FILLED",
                               "time": 99}]}
    return 404, {}


loop.v2_get = fake_v2_hist
entry2, src2 = loop.get_entry_price("K", "S", "btcidr")
check("entry fallback ke histories",
      entry2 == 1405000000.0 and src2 == "/api/v2/order/histories")
loop.v2_get = lambda k, s, p, pr: (400, {"code": -1002})
entry3, src3 = loop.get_entry_price("K", "S", "btcidr")
check("entry gagal semua -> None", entry3 is None and src3 is None)
loop.v2_get = orig_v2

# 6. Format qty + verifikasi saldo
check("qty_str normal", loop.qty_str(0.00001417) == "0.00001417")
check("qty_str strip nol", loop.qty_str(0.00001) == "0.00001")
check("qty_str nol", loop.qty_str(0.0) == "0")
before = {"BTC": (0.00001417, 0.00001417), "IDR": (5309, 5309)}
after_sold = {"BTC": (0, 0), "IDR": (25000, 25000)}
after_open = {"BTC": (0, 0.00001417), "IDR": (5309, 5309)}
check("verify sold benar", loop.verify_sold(before, after_sold, "BTC", 7e-06))
check("verify open order BUKAN sold",
      not loop.verify_sold(before, after_open, "BTC", 7e-06))
after_buy = {"BTC": (0.00001417, 0.00001417)}
check("verify bought benar",
      loop.verify_bought({"BTC": (0, 0)}, after_buy, "BTC", 0.00001417))
check("verify bought kurang -> gagal",
      not loop.verify_bought({"BTC": (0, 0)}, after_buy, "BTC", 0.00002))

# 7. Gerbang (env + temp dir)
os.environ["INDODAX_API_KEY"] = "DUMMY"
os.environ["INDODAX_SECRET"] = "DUMMY"
os.environ.pop("LIVE_TRADING", None)
check("gerbang tanpa LIVE_TRADING -> 2", loop.main() == 2)
os.environ["LIVE_TRADING"] = "1"
tmp = tempfile.mkdtemp()
old_dir = loop.SCRIPT_DIR
loop.SCRIPT_DIR = tmp
check("gerbang tanpa LIVE_APPROVED -> 2", loop.main() == 2)
with open(os.path.join(tmp, "LIVE_APPROVED.txt"), "w") as f:
    f.write("Disetujui TEST\n")
with open(os.path.join(tmp, "loop_params.json"), "w") as f:
    json.dump({"sl_pct": 60}, f)
try:
    loop.load_loop_params()
    check("loop_params invalid ditolak", False)
except SystemExit as e:
    check("loop_params invalid ditolak", e.code == 3)
with open(os.path.join(tmp, "loop_params.json"), "w") as f:
    json.dump({"sl_pct": 25, "max_buy_idr": 15000}, f)
cfg2 = loop.load_loop_params()
check("loop_params valid override",
      cfg2["sl_pct"] == 25 and cfg2["max_buy_idr"] == 15000
      and cfg2["tp_pct"] == 15)
loop.SCRIPT_DIR = old_dir

print()
if FAILS:
    print(f"GAGAL: {len(FAILS)} -> {FAILS}")
    sys.exit(1)
print("ALL_PASS")
