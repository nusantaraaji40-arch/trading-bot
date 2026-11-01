"""Tes loop live (mock jaringan + mock SDK — TIDAK ADA order nyata,
TIDAK ADA jaringan privat, hanya nilai FAKE-*).

Jalankan: cd ~/workspace/polymarket-bot/live_loop_build &&
python3 test_loop.py
"""

import json
import os
import sys
import tempfile
import unittest
from types import SimpleNamespace
from unittest import mock

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import live_loop  # noqa: E402
import signals  # noqa: E402
from test_wiring import FakeClient  # noqa: E402

TOKEN_A = "11111111111111111111"
TOKEN_B = "22222222222222222222"


def updown_params():
    return {"modal_usd": 1.0, "first_trade_usd": 1.0, "sl_pct": 7.0,
            "sl_hard_cap_pct": 12.0, "tp_pct": 20.0,
            "kill_switch_pct": 15.0, "min_order_size": 5,
            "chain": "polygon", "collateral": "USDC"}


def ladder_params():
    return {"modal_usd": 1.0, "first_trade_usd": 1.0, "sl_pct": 7.0,
            "sl_hard_cap_pct": 12.0, "tp1_pct": 10.0, "tp2_pct": 15.0,
            "kill_switch_pct": 15.0, "min_order_size": 5,
            "chain": "polygon", "collateral": "USDC"}


class RecLogger:
    def __init__(self):
        self.lines = []

    def log(self, msg):
        self.lines.append(msg)

    def role(self, bro, name, msg):
        self.lines.append(f"[Bro {bro} {name}] {msg}")


def market(question="Bitcoin Up or Down on November 2?",
           outcomes=("Up", "Down"), token_ids=(TOKEN_A, TOKEN_B),
           liquidity=10000, end="2030-01-02T00:00:00Z",
           start="2030-01-01T00:00:00Z", min_size=5, fee_rate=0.07,
           fee_exp=1, accepting=True, active=True, closed=False,
           prices=("0.5", "0.5"), volume=5000, game=None):
    m = {"question": question, "outcomes": list(outcomes),
         "clobTokenIds": list(token_ids), "liquidity": liquidity,
         "endDate": end, "startDate": start, "orderMinSize": min_size,
         "feeSchedule": {"rate": fee_rate, "exponent": fee_exp},
         "feeType": "crypto_fees_v2", "active": active,
         "closed": closed, "acceptingOrders": accepting,
         "outcomePrices": list(prices), "volume24hr": volume}
    if game:
        m["gameStartTime"] = game
    return m


def position(entry=0.13, remaining=7, total=7, cash=0.0346,
             outcome_index=0, label="Up", token=TOKEN_A,
             lowest=None, last_ask=None, tp1=False):
    return {
        "market": "Bitcoin Up or Down on November 2?",
        "question": "Bitcoin Up or Down on November 2?",
        "token_id": token, "outcome_label": label,
        "outcome_index": outcome_index, "entry_ask": entry,
        "shares_total": total, "remaining": remaining,
        "cost_usd": round(entry * total, 4),
        "fee_usd": 0.0554,
        "cost_per_share": entry,
        "fee_buy_per_share": 0.0554 / total if total else 0,
        "fee_rate": 0.07, "fee_exponent": 1, "tp1_done": tp1,
        "last_bid": None, "last_ask": last_ask,
        "prev_ask": None,
        "lowest_ask": lowest if lowest is not None else entry,
        "end_iso": "2030-01-02T00:00:00Z", "start_iso": None,
        "sell_attempts": 0, "sell_method": None,
    }


class TestDecideExit(unittest.TestCase):
    def ex(self, entry, bid, ask, remaining=10, tp1=False, total=1.0,
           start=1.0, kind="updown", recovery=None, **kw):
        params = {"sl_pct": 7.0, "sl_hard_cap_pct": 12.0,
                  "tp_pct": 20.0, "tp1_pct": 10.0, "tp2_pct": 15.0,
                  "ks_pct": 15.0}
        params.update(kw)
        return live_loop.decide_exit(
            entry, bid, ask, remaining, tp1, total, start, kind=kind,
            recovery=recovery, **params)

    def test_tp_exact_boundary_triggers(self):
        self.assertEqual(self.ex(0.50, 0.59, 0.60)[:2],
                         ("SELL_ALL", 10))
        self.assertEqual(self.ex(0.50, 0.59, 0.60)[2], "TP")

    def test_tp_just_below_holds(self):
        self.assertEqual(self.ex(0.50, 0.59, 0.5999)[0], "HOLD")

    def test_sl_exact_boundary_sells(self):
        # 0.50 * (1 - 0.07) = 0.465 tepat.
        self.assertEqual(self.ex(0.50, 0.46, 0.465)[2], "SL")

    def test_sl_just_above_holds(self):
        self.assertEqual(self.ex(0.50, 0.46, 0.4651)[0], "HOLD")

    def test_sl_hold_with_clear_recovery(self):
        rec = {"momentum_positive": True, "signal_ok": True,
               "bounced": True, "all": True}
        self.assertEqual(self.ex(0.50, 0.46, 0.465, recovery=rec)[2],
                         "SL_HOLD")

    def test_sl_hold_requires_all_three(self):
        for missing in ("momentum_positive", "signal_ok", "bounced"):
            rec = {"momentum_positive": True, "signal_ok": True,
                   "bounced": True, "all": True}
            rec[missing] = False
            rec["all"] = False
            self.assertEqual(
                self.ex(0.50, 0.46, 0.465, recovery=rec)[2], "SL",
                f"gagal untuk {missing}=False")
        self.assertEqual(self.ex(0.50, 0.46, 0.465,
                                 recovery=None)[2], "SL")

    def test_hard_cap_exact_sells_despite_recovery(self):
        # 0.50 * (1 - 0.12) = 0.44 tepat — batas keras tanpa pengecualian.
        rec = {"momentum_positive": True, "signal_ok": True,
               "bounced": True, "all": True}
        self.assertEqual(self.ex(0.50, 0.43, 0.44, recovery=rec)[2],
                         "SL_HARD")

    def test_hard_cap_gap_sells_immediately(self):
        self.assertEqual(self.ex(0.50, 0.29, 0.30)[2], "SL_HARD")

    def test_ks_priority_over_tp_and_hard(self):
        # Total tepat di lantai KS (1.00 * 0.85) + ask di TP -> KS menang.
        self.assertEqual(self.ex(0.50, 0.59, 0.60, total=0.85)[2],
                         "KILL_SWITCH")
        self.assertEqual(self.ex(0.50, 0.29, 0.30, total=0.85)[2],
                         "KILL_SWITCH")

    def test_ladder_tp1_partial_and_tp2(self):
        action, qty, reason = self.ex(0.50, 0.54, 0.55, remaining=10,
                                      kind="ladder")
        self.assertEqual((action, qty, reason),
                         ("SELL_PARTIAL", 5, "TP1"))
        action, qty, reason = self.ex(0.50, 0.57, 0.575, remaining=5,
                                      tp1=True, kind="ladder")
        self.assertEqual((action, qty, reason),
                         ("SELL_ALL", 5, "TP2"))
        action, qty, reason = self.ex(0.50, 0.54, 0.55, remaining=1,
                                      kind="ladder")
        self.assertEqual((action, qty, reason),
                         ("SELL_ALL", 1, "TP1"))

    def test_trigger_falls_back_to_bid(self):
        self.assertEqual(self.ex(0.50, 0.60, None)[2], "TP")

    def test_no_prices_hold(self):
        self.assertEqual(self.ex(0.50, None, None)[0], "HOLD")

    def test_remaining_zero_hold(self):
        self.assertEqual(self.ex(0.50, 0.60, 0.60, remaining=0)[0],
                         "HOLD")


class TestRecoveryAndMomentum(unittest.TestCase):
    def test_recovery_all_true(self):
        r = live_loop.recovery_evidence(0.52, 0.50, 0.50, True)
        self.assertTrue(r["all"])
        self.assertTrue(r["momentum_positive"])
        self.assertTrue(r["bounced"])

    def test_recovery_bounce_below_2pct_fails(self):
        r = live_loop.recovery_evidence(0.505, 0.50, 0.50, True)
        self.assertFalse(r["bounced"])
        self.assertFalse(r["all"])

    def test_recovery_no_prev_no_history_fails(self):
        r = live_loop.recovery_evidence(0.52, None, 0.50, True)
        self.assertFalse(r["momentum_positive"])
        self.assertFalse(r["all"])

    def test_recovery_history_overrides_prev(self):
        r = live_loop.recovery_evidence(0.52, 0.53, 0.50, True,
                                        history_prices=[0.50, 0.52])
        self.assertTrue(r["momentum_positive"])

    def test_momentum_proxy_3pct_boundary(self):
        ok, _ = live_loop.momentum_gate(0.485, 0.50)
        self.assertFalse(ok)  # tepat 3% di bawah konsensus -> turun
        ok, _ = live_loop.momentum_gate(0.486, 0.50)
        self.assertTrue(ok)

    def test_momentum_history_drop(self):
        ok, _ = live_loop.momentum_gate(0.50, 0.50,
                                        history_prices=[0.50, 0.47])
        self.assertFalse(ok)
        ok, _ = live_loop.momentum_gate(0.50, 0.50,
                                        history_prices=[0.50, 0.49])
        self.assertTrue(ok)

    def test_momentum_no_data_safe_skip(self):
        ok, reason = live_loop.momentum_gate(0.50, None)
        self.assertFalse(ok)
        self.assertIn("tidak bisa dinilai", reason)


class TestDurationAndParse(unittest.TestCase):
    def test_minute_questions_rejected(self):
        for q in ("Bitcoin Up or Down in the next 15 minutes?",
                  "Bitcoin Up or Down - 15-minute?",
                  "Bitcoin Up or Down in the next 5 min?"):
            ok, reason = live_loop.updown_duration_ok(
                q, "2030-01-01T00:00:00Z", "2030-01-01T01:00:00Z")
            self.assertFalse(ok, q)
            self.assertIn("menitan", reason)

    def test_hourly_and_daily_accepted(self):
        ok, _ = live_loop.updown_duration_ok(
            "Bitcoin Up or Down on November 2?",
            "2030-01-01T00:00:00Z", "2030-01-01T01:00:00Z")
        self.assertTrue(ok)
        ok, _ = live_loop.updown_duration_ok(
            "Bitcoin Up or Down on November 2?",
            "2030-01-01T00:00:00Z", "2030-01-03T02:00:00Z")
        self.assertTrue(ok)

    def test_time_range_window_rejected(self):
        # Temuan dry-run 2026-11-02: judul rentang jam menitan lolos
        # karena tidak mengandung kata "min" dan startDate listing
        # bukan window event — rentang jam kini diparse sendiri.
        for q in ("Bitcoin Up or Down - November 1, 1:30PM-1:45PM ET",
                  "Bitcoin Up or Down - November 1, 11:30PM-12:15AM ET"):
            ok, reason = live_loop.updown_duration_ok(
                q, "2030-01-01T00:00:00Z", "2030-01-01T05:00:00Z")
            self.assertFalse(ok, q)
            self.assertIn("menit", reason)

    def test_time_range_hourly_accepted(self):
        for q in ("Bitcoin Up or Down - November 1, 1:00PM-2:00PM ET",
                  "Bitcoin Up or Down - November 1, 11:00PM-12:00AM ET"):
            ok, _ = live_loop.updown_duration_ok(
                q, "2030-01-01T00:00:00Z", "2030-01-01T05:00:00Z")
            self.assertTrue(ok, q)

    def test_short_duration_rejected(self):
        ok, _ = live_loop.updown_duration_ok(
            "Bitcoin Up or Down on November 2?",
            "2030-01-01T00:00:00Z", "2030-01-01T00:30:00Z")
        self.assertFalse(ok)

    def test_missing_start_falls_back_to_question(self):
        ok, _ = live_loop.updown_duration_ok(
            "Bitcoin Up or Down on November 2?", None,
            "2030-01-02T00:00:00Z")
        self.assertTrue(ok)

    def test_parse_market_valid(self):
        pm, reason = live_loop.parse_market(market())
        self.assertIsNotNone(pm)
        self.assertIsNone(reason)
        self.assertEqual(pm["outcome_prices"], [0.5, 0.5])
        self.assertEqual(pm["token_ids"], [TOKEN_A, TOKEN_B])

    def test_parse_market_string_fields(self):
        m = market()
        m["outcomes"] = '["Up", "Down"]'
        m["clobTokenIds"] = f'["{TOKEN_A}", "{TOKEN_B}"]'
        pm, _ = live_loop.parse_market(m)
        self.assertIsNotNone(pm)

    def test_parse_market_rejects(self):
        cases = []
        m = market()
        m["feeSchedule"] = {}
        cases.append(m)
        m = market()
        m["acceptingOrders"] = False
        cases.append(m)
        m = market()
        m["active"] = False
        cases.append(m)
        m = market()
        m["clobTokenIds"] = ["abc", TOKEN_B]
        cases.append(m)
        for m in cases:
            pm, reason = live_loop.parse_market(m)
            self.assertIsNone(pm)
            self.assertTrue(reason)


class TestParamsAndApproval(unittest.TestCase):
    def test_example_params_valid(self):
        path = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                            "loop_params.example.json")
        with open(path) as f:
            data = json.load(f)
        errors, warnings = live_loop.validate_loop_params(data)
        self.assertEqual(errors, [])
        # Aturan final: SL 7 + batas keras 12 di semua kategori.
        for cat in ("updown", "weather", "soccer"):
            self.assertEqual(data["categories"][cat]["sl_pct"], 7)
            self.assertEqual(data["categories"][cat]["sl_hard_cap_pct"],
                             12)

    def test_params_rejects(self):
        base = {"categories": {"updown": updown_params(),
                               "weather": ladder_params(),
                               "soccer": ladder_params()}}
        import copy
        d = copy.deepcopy(base)
        del d["categories"]["soccer"]
        errors, _ = live_loop.validate_loop_params(d)
        self.assertTrue(errors)
        d = copy.deepcopy(base)
        d["categories"]["updown"]["sl_hard_cap_pct"] = 7
        errors, _ = live_loop.validate_loop_params(d)
        self.assertTrue(any("sl_hard_cap_pct" in e for e in errors))
        d = copy.deepcopy(base)
        del d["categories"]["updown"]["sl_hard_cap_pct"]
        errors, _ = live_loop.validate_loop_params(d)
        self.assertTrue(any("sl_hard_cap_pct" in e for e in errors))
        d = copy.deepcopy(base)
        d["categories"]["updown"]["chain"] = "ethereum"
        errors, _ = live_loop.validate_loop_params(d)
        self.assertTrue(errors)
        d = copy.deepcopy(base)
        d["categories"]["updown"]["first_trade_usd"] = 2.0
        errors, _ = live_loop.validate_loop_params(d)
        self.assertTrue(errors)
        d = copy.deepcopy(base)
        d["categories"]["weather"]["tp2_pct"] = 5
        errors, _ = live_loop.validate_loop_params(d)
        self.assertTrue(errors)

    def test_approval_text_ok(self):
        good = ("Disetujui: Polymarket live 3 kategori, modal $1 per "
                "kategori, SL 7%, batas keras 12%, kill-switch 15%.")
        self.assertTrue(live_loop.approval_text_ok(good))
        good2 = "SL -7%, batas keras -12%, kill-switch 15%"
        self.assertTrue(live_loop.approval_text_ok(good2))
        old10 = "SL 10%, kill-switch 15%"
        self.assertFalse(live_loop.approval_text_ok(old10))
        old5 = "SL 5%, kill-switch 15%"
        self.assertFalse(live_loop.approval_text_ok(old5))
        no_ks = "SL 7%, batas keras 12%"
        self.assertFalse(live_loop.approval_text_ok(no_ks))


class TestSizingAndCash(unittest.TestCase):
    def test_buy_budget_hill_rule(self):
        self.assertEqual(live_loop.buy_budget(1.5, 1.0), 1.0)
        self.assertEqual(live_loop.buy_budget(0.7, 1.0), 0.7)

    def test_size_trade_exact(self):
        shares, cost, fee = live_loop.size_trade(1.0, 0.13, 0.07, 1, 5)
        self.assertEqual(shares, 7)
        self.assertAlmostEqual(cost, 0.91)
        self.assertAlmostEqual(fee, 0.0554, places=4)

    def test_size_trade_below_min_skipped(self):
        res = live_loop.size_trade(0.30, 0.13, 0.07, 1, 5)
        self.assertIsNone(res[0])
        self.assertIn("min order", res[1])

    def test_size_trade_expensive_side_skipped(self):
        res = live_loop.size_trade(1.0, 0.99, 0.07, 1, 5)
        self.assertIsNone(res[0])


class TestStateAtomic(unittest.TestCase):
    def test_round_trip_no_tmp_left(self):
        with tempfile.TemporaryDirectory() as d:
            path = os.path.join(d, "state_updown.json")
            st = live_loop.new_category_state("updown", 1.0)
            live_loop.atomic_write_json(path, st)
            with open(path) as f:
                back = json.load(f)
            self.assertEqual(back["category"], "updown")
            leftovers = [f for f in os.listdir(d) if ".tmp." in f]
            self.assertEqual(leftovers, [])

    def test_corrupt_state_flagged_not_traded(self):
        with tempfile.TemporaryDirectory() as d:
            path = os.path.join(d, "state_updown.json")
            with open(path, "w") as f:
                f.write("{bukan json")
            st = live_loop.load_state(d, "updown", 1.0)
            self.assertTrue(st["corrupt"])
            self.assertTrue(st["stopped"])


class TestGuardsAndVet(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        live_loop.CURRENT_STATE_DIR[0] = self.tmp.name
        live_loop.CURRENT_POLL[0] = 1
        self.log = RecLogger()

    def tearDown(self):
        self.tmp.cleanup()

    def test_buy_refused_when_open(self):
        c = FakeClient()
        st = live_loop.new_category_state("updown", 1.0)
        st["status"] = "OPEN"
        st["position"] = position()
        picked = {"market": "Q", "token_id": TOKEN_A, "shares": 7,
                  "ask": 0.13, "outcome_label": "Up"}
        posted, _ = live_loop.execute_buy(c, "updown", updown_params(),
                                          st, picked, self.log)
        self.assertFalse(posted)
        self.assertEqual(c.calls, [])

    def test_sell_refused_when_idle(self):
        c = FakeClient()
        st = live_loop.new_category_state("updown", 1.0)
        posted, _ = live_loop.execute_sell(
            c, "updown", updown_params(), st, 7, 0.15, 0.16, "TP",
            self.log)
        self.assertFalse(posted)
        self.assertEqual(c.calls, [])

    def test_vet_rules(self):
        m, _ = live_loop.parse_market(market())
        books = {0: (0.12, 0.13), 1: (0.86, 0.87)}
        side, info, reject = live_loop.bro3_vet("updown", m, books,
                                                None)
        self.assertEqual(side, 0)
        self.assertIsNone(reject)
        m2, _ = live_loop.parse_market(market(liquidity=400))
        _, _, reject = live_loop.bro3_vet("updown", m2, books, None)
        self.assertIn("likuiditas", reject)
        books_wide = {0: (0.40, 0.50), 1: (0.50, 0.60)}
        _, _, reject = live_loop.bro3_vet("updown", m, books_wide, None)
        self.assertIn("spread", reject)
        books_one = {0: (None, 0.13), 1: (None, None)}
        side, info, reject = live_loop.bro3_vet("updown", m, books_one,
                                                None)
        self.assertEqual(side, 0)
        self.assertTrue(info["one_sided"])
        _, _, reject = live_loop.bro3_vet("updown", m, books, TOKEN_A)
        self.assertIn("rotasi", reject)
        m_min, _ = live_loop.parse_market(market(
            question="Bitcoin Up or Down in the next 15 minutes?"))
        _, _, reject = live_loop.bro3_vet("updown", m_min, books, None)
        self.assertIn("menitan", reject)

    def test_rank_soccer_match_first(self):
        # "now" 44 jam sebelum game 2030-01-01T20:00 -> match<=48h.
        from datetime import datetime, timezone
        now = datetime(2029, 12, 31, tzinfo=timezone.utc).timestamp()
        m_match, _ = live_loop.parse_market(market(
            question="Will Real Madrid win?", volume=100,
            game="2030-01-01T20:00:00Z"))
        m_non, _ = live_loop.parse_market(market(
            question="Will Team X win?", volume=99999))
        ranked = live_loop.bro2_rank_candidates(
            "soccer", [m_non, m_match], now)
        self.assertEqual(ranked[0][1], "match<=48h")
        m_end, _ = live_loop.parse_market(market(
            end="2020-01-01T00:00:00Z"))
        ranked = live_loop.bro2_rank_candidates(
            "soccer", [m_end], now)
        self.assertEqual(ranked, [])


class TestResolution(unittest.TestCase):
    def test_win_loss_none(self):
        out, _ = live_loop.decide_resolution([0.9995, 0.0005], 0, True)
        self.assertEqual(out, "WIN")
        out, _ = live_loop.decide_resolution([0.9995, 0.0005], 1, True)
        self.assertEqual(out, "LOSS")
        out, _ = live_loop.decide_resolution([0.9995, 0.0005], 0, False)
        self.assertIsNone(out)
        out, _ = live_loop.decide_resolution([0.5, 0.5], 0, True)
        self.assertIsNone(out)


class TestVerifyPending(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        live_loop.CURRENT_STATE_DIR[0] = self.tmp.name
        live_loop.CURRENT_POLL[0] = 7
        self.log = RecLogger()

    def tearDown(self):
        self.tmp.cleanup()

    def _buy_state(self):
        st = live_loop.new_category_state("updown", 1.0)
        st["status"] = "PENDING_BUY"
        st["pending_order"] = {
            "kind": "BUY", "order_id": "B-1", "qty": 7, "price": 0.13,
            "reason": "BUY", "side": "BUY", "method": "limit",
            "attempts": 0,
            "response": {"ok": True, "status": "live",
                         "trade_count": 0},
            "candidate": {"market": "Q", "question": "Q",
                          "token_id": TOKEN_A, "outcome_label": "Up",
                          "outcome_index": 0, "fee_rate": 0.07,
                          "fee_exponent": 1, "fee_type": "x",
                          "end_iso": "2030-01-02T00:00:00Z",
                          "start_iso": None},
        }
        return st

    def test_buy_filled_via_positions(self):
        c = FakeClient()
        c.open_orders = []
        c.positions = [SimpleNamespace(asset_id=TOKEN_A,
                                       current_size="7")]
        st = self._buy_state()
        res = live_loop.verify_pending(c, "updown", updown_params(),
                                       st, self.log)
        self.assertEqual(res, "BUY_FILLED")
        self.assertEqual(st["status"], "OPEN")
        self.assertEqual(st["position"]["remaining"], 7)
        self.assertAlmostEqual(st["cash_usd"], 1.0 - 0.91 - 0.0554,
                               places=4)

    def test_buy_not_filled_via_positions(self):
        c = FakeClient()
        c.open_orders = []
        c.positions = []
        st = self._buy_state()
        res = live_loop.verify_pending(c, "updown", updown_params(),
                                       st, self.log)
        self.assertEqual(res, "BUY_NOT_FILLED")
        self.assertEqual(st["status"], "IDLE")
        self.assertIsNone(st["position"])

    def test_buy_resting_keeps_pending(self):
        c = FakeClient()
        c.open_orders = [SimpleNamespace(
            id="B-1", side="BUY", price=0.13, original_size="7",
            size_matched="0", status="live")]
        st = self._buy_state()
        res = live_loop.verify_pending(c, "updown", updown_params(),
                                       st, self.log)
        self.assertEqual(res, "PENDING")
        self.assertEqual(st["pending_order"]["attempts"], 1)

    def _sell_state(self):
        st = live_loop.new_category_state("updown", 1.0)
        st["cash_usd"] = 0.0346
        st["status"] = "PENDING_SELL"
        st["position"] = position()
        st["pending_order"] = {
            "kind": "SELL", "order_id": "S-1", "qty": 10,
            "price": 0.60, "reason": "TP", "side": "SELL",
            "method": "limit", "attempts": 0,
            "response": {"ok": True, "status": "matched",
                         "trade_count": 1},
        }
        return st

    def test_sell_filled_net_pnl(self):
        # Posisi test: 10 lembar @ 0.50, fee beli/lembar 0.0035.
        c = FakeClient()
        c.open_orders = []
        c.positions = []
        st = self._sell_state()
        st["position"] = position(entry=0.50, remaining=10, total=10,
                                  cash=0.0346)
        st["position"]["fee_buy_per_share"] = 0.0035
        res = live_loop.verify_pending(c, "updown", updown_params(),
                                       st, self.log)
        self.assertEqual(res, "SELL_FILLED")
        self.assertEqual(st["status"], "IDLE")
        # fee jual = 0.07*(0.6*0.4)*10 = 0.168; hasil = 6.0-0.168;
        # pnl = 5.832 - 10*(0.50+0.0035) = 0.797.
        self.assertAlmostEqual(st["cash_usd"], 0.0346 + 5.832, places=4)
        self.assertAlmostEqual(st["realized_usd"], 0.797, places=4)

    def test_sell_not_filled_keeps_position(self):
        c = FakeClient()
        c.open_orders = []
        c.positions = [SimpleNamespace(asset_id=TOKEN_A,
                                       current_size="10")]
        st = self._sell_state()
        res = live_loop.verify_pending(c, "updown", updown_params(),
                                       st, self.log)
        self.assertEqual(res, "SELL_NOT_FILLED")
        self.assertEqual(st["status"], "OPEN")
        self.assertIsNotNone(st["position"])
        self.assertIsNone(st["pending_order"])

    def test_sell_resting_switches_to_market(self):
        c = FakeClient()
        c.open_orders = [SimpleNamespace(
            id="S-1", side="SELL", price=0.60, original_size="10",
            size_matched="0", status="live")]
        st = self._sell_state()
        st["pending_order"]["attempts"] = 2  # +1 = 3 = batas
        with mock.patch.object(live_loop, "bro8_fetch_book",
                               return_value=(0.60, 0.61)):
            res = live_loop.verify_pending(c, "updown", updown_params(),
                                           st, self.log)
        self.assertEqual(res, "SELL_POSTED")
        self.assertEqual(st["status"], "PENDING_SELL")
        self.assertEqual(st["pending_order"]["method"], "market")
        kinds = [k for k, _ in c.calls]
        self.assertIn("cancel", kinds)
        self.assertIn("create_market", kinds)


class TestScreenPick(unittest.TestCase):
    def setUp(self):
        self.log = RecLogger()

    def _books(self):
        return {TOKEN_A: (0.12, 0.13), TOKEN_B: (0.86, 0.87)}

    def test_picks_good_skips_minute_and_low_liq(self):
        good = market(prices=("0.13", "0.87"), volume=9000)
        minute = market(
            question="Bitcoin Up or Down in the next 15 minutes?",
            volume=99999, prices=("0.13", "0.87"))
        low = market(question="Low liq coin?", liquidity=100,
                     volume=1, prices=("0.13", "0.87"))
        books = self._books()

        def fetch_markets(tag_id):
            return [minute, low, good]

        def fetch_book(tok):
            return books[tok]

        def gate(cat, q, e):
            return signals.SignalResult(ok=True, side=None,
                                        evidence=["test"],
                                        reason="test ok")

        st = live_loop.new_category_state("updown", 1.0)
        picked, reason = live_loop.bro1_screen_and_pick(
            "updown", updown_params(), st, self.log,
            fetcher_markets=fetch_markets, fetcher_book=fetch_book,
            signal_gate=gate)
        self.assertIsNotNone(picked)
        self.assertEqual(picked["token_id"], TOKEN_A)
        self.assertEqual(picked["shares"], 7)

    def test_signal_gate_blocks_buy(self):
        good = market(prices=("0.13", "0.87"))
        books = self._books()

        def gate(cat, q, e):
            return signals.SignalResult(ok=False, side=None,
                                        evidence=[],
                                        reason="tidak ada berita")

        st = live_loop.new_category_state("updown", 1.0)
        picked, reason = live_loop.bro1_screen_and_pick(
            "updown", updown_params(), st, self.log,
            fetcher_markets=lambda t: [good],
            fetcher_book=lambda tok: books[tok],
            signal_gate=gate)
        self.assertIsNone(picked)
        self.assertIn("sinyal", reason)

    def test_momentum_blocks_falling_side(self):
        # Ask 0.13 jauh di bawah konsensus 0.20 -> sisi jatuh.
        good = market(prices=("0.20", "0.80"))
        books = self._books()

        def gate(cat, q, e):
            return signals.SignalResult(ok=True, side=None,
                                        evidence=["test"],
                                        reason="test ok")

        st = live_loop.new_category_state("updown", 1.0)
        picked, reason = live_loop.bro1_screen_and_pick(
            "updown", updown_params(), st, self.log,
            fetcher_markets=lambda t: [good],
            fetcher_book=lambda tok: books[tok],
            signal_gate=gate)
        self.assertIsNone(picked)
        self.assertIn("momentum", reason)

    def test_rotation_excludes_last_token(self):
        good = market(prices=("0.13", "0.87"))
        books = self._books()

        def gate(cat, q, e):
            return signals.SignalResult(ok=True, side=None,
                                        evidence=["test"],
                                        reason="test ok")

        st = live_loop.new_category_state("updown", 1.0)
        st["last_token_id"] = TOKEN_A
        picked, reason = live_loop.bro1_screen_and_pick(
            "updown", updown_params(), st, self.log,
            fetcher_markets=lambda t: [good],
            fetcher_book=lambda tok: books[tok],
            signal_gate=gate)
        self.assertIsNone(picked)
        self.assertIn("rotasi", reason)


class TestBro7CheckPosition(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        live_loop.CURRENT_STATE_DIR[0] = self.tmp.name
        live_loop.CURRENT_POLL[0] = 3
        self.log = RecLogger()

    def tearDown(self):
        self.tmp.cleanup()

    def _state(self, **pos_kw):
        st = live_loop.new_category_state("updown", 1.0)
        st["cash_usd"] = 0.0346  # kas setelah beli 7 @ 0,13 + fee
        st["status"] = "OPEN"
        st["position"] = position(**pos_kw)
        return st

    def test_kill_switch(self):
        # Kas 0.0346 + 7 lembar @ bid 0.10 = 0.7346 <= lantai 0.85.
        c = FakeClient()
        st = self._state()
        with mock.patch.object(live_loop, "bro8_fetch_market_by_token",
                               return_value={}), \
                mock.patch.object(live_loop, "bro8_fetch_book",
                                  return_value=(0.10, 0.11)):
            res = live_loop.bro7_check_position(
                c, "updown", updown_params(), st, self.log, 3)
        self.assertEqual(res, "KILL_SWITCH")
        self.assertTrue(st["kill_switch_hit"])
        self.assertEqual(st["status"], "PENDING_SELL")
        self.assertEqual(st["pending_order"]["method"], "market")

    def test_sl_hold_with_recovery(self):
        # Zona SL: entry 0.13, ask 0.12 (di antara hard 0.1144 dan
        # SL 0.1209); total 0.0346 + 7*0.12 = 0.8746 > lantai KS 0.85.
        c = FakeClient()
        st = self._state(lowest=0.11, last_ask=0.115)
        gate_ok = signals.SignalResult(ok=True, side=None,
                                       evidence=["test"],
                                       reason="test ok")
        with mock.patch.object(live_loop, "bro8_fetch_market_by_token",
                               return_value={}), \
                mock.patch.object(live_loop, "bro8_fetch_book",
                                  return_value=(0.12, 0.12)), \
                mock.patch.object(live_loop, "bro4_signal_gate",
                                  return_value=gate_ok), \
                mock.patch.object(live_loop, "fetch_history_prices",
                                  return_value=[0.11, 0.12]):
            res = live_loop.bro7_check_position(
                c, "updown", updown_params(), st, self.log, 3)
        self.assertEqual(res, "SL_HOLD")
        self.assertEqual(st["status"], "OPEN")

    def test_sl_hard_sells_despite_recovery(self):
        # Total 0.50 + 7*0.06 = 0.92 > lantai KS; ask 0.07 < hard 0.1144.
        c = FakeClient()
        st = self._state()
        st["cash_usd"] = 0.50
        gate_ok = signals.SignalResult(ok=True, side=None,
                                       evidence=["test"],
                                       reason="test ok")
        with mock.patch.object(live_loop, "bro8_fetch_market_by_token",
                               return_value={}), \
                mock.patch.object(live_loop, "bro8_fetch_book",
                                  return_value=(0.06, 0.07)), \
                mock.patch.object(live_loop, "bro4_signal_gate",
                                  return_value=gate_ok), \
                mock.patch.object(live_loop, "fetch_history_prices",
                                  return_value=[0.06, 0.07]):
            res = live_loop.bro7_check_position(
                c, "updown", updown_params(), st, self.log, 3)
        self.assertEqual(res, "SELL_POSTED")
        self.assertEqual(st["pending_order"]["reason"], "SL_HARD")
        self.assertEqual(st["pending_order"]["method"], "market")

    def test_tp_limit_sell_posted(self):
        c = FakeClient()
        st = self._state()
        with mock.patch.object(live_loop, "bro8_fetch_market_by_token",
                               return_value={}), \
                mock.patch.object(live_loop, "bro8_fetch_book",
                                  return_value=(0.16, 0.17)):
            res = live_loop.bro7_check_position(
                c, "updown", updown_params(), st, self.log, 3)
        self.assertEqual(res, "SELL_POSTED")
        self.assertEqual(st["pending_order"]["reason"], "TP")
        self.assertEqual(st["pending_order"]["method"], "limit")

    def test_cannot_exit_without_bid(self):
        c = FakeClient()
        st = self._state()
        with mock.patch.object(live_loop, "bro8_fetch_market_by_token",
                               return_value={}), \
                mock.patch.object(live_loop, "bro8_fetch_book",
                                  return_value=(None, 0.13)):
            res = live_loop.bro7_check_position(
                c, "updown", updown_params(), st, self.log, 3)
        self.assertEqual(res, "CANNOT_EXIT")
        self.assertEqual(st["status"], "OPEN")

    def test_resolve_win_settles(self):
        c = FakeClient()
        st = self._state()
        mkt = {"closed": True, "outcomePrices": ["0.9995", "0.0005"]}
        with mock.patch.object(live_loop, "bro8_fetch_market_by_token",
                               return_value=mkt):
            res = live_loop.bro7_check_position(
                c, "updown", updown_params(), st, self.log, 3)
        self.assertEqual(res, "RESOLVED")
        self.assertEqual(st["status"], "IDLE")
        # Hasil 7.0 - biaya (7*0.13 + fee 0.0554) = 7.0 - 0.9654.
        self.assertAlmostEqual(st["cash_usd"], 0.0346 + 7.0, places=4)
        self.assertAlmostEqual(st["realized_usd"],
                               7.0 - (7 * 0.13 + 0.0554), places=4)


class TestModes(unittest.TestCase):
    def test_check_missing_params_returns_2(self):
        with tempfile.TemporaryDirectory() as d:
            log = RecLogger()
            code = live_loop.mode_check("/nonexistent", d, log)
            self.assertEqual(code, 2)

    def test_check_valid_no_key_returns_0(self):
        with tempfile.TemporaryDirectory() as d:
            params_path = os.path.join(d, "loop_params.json")
            approval_path = os.path.join(d, "LIVE_APPROVED_LOOP.txt")
            with open(params_path, "w") as f:
                json.dump({"categories": {
                    "updown": updown_params(),
                    "weather": ladder_params(),
                    "soccer": ladder_params()}}, f)
            with open(approval_path, "w") as f:
                f.write("Disetujui: SL 7%, batas keras 12%, "
                        "kill-switch 15%.")
            log = RecLogger()
            with mock.patch.object(live_loop, "http_get_json",
                                   return_value={"blocked": False}), \
                    mock.patch.object(live_loop.order_wiring,
                                      "sdk_available",
                                      return_value=True), \
                    mock.patch.dict(os.environ, {}, clear=True):
                code = live_loop.mode_check(d, d, log,
                                            params_path, approval_path)
            self.assertEqual(code, 0)

    def test_dry_run_explicit_never_posts(self):
        c = FakeClient()
        c.post_raises = AssertionError("POST saat DRY-RUN!")
        with tempfile.TemporaryDirectory() as d:
            log = RecLogger()
            args = SimpleNamespace(dry_token=TOKEN_A, dry_price=0.13,
                                   dry_size=7, dry_side="BUY")
            with mock.patch.dict(os.environ,
                                 {"POLY_PRIVATE_KEY": "FAKE-KEY-1"}), \
                    mock.patch.object(live_loop.order_wiring,
                                      "sdk_available",
                                      return_value=True), \
                    mock.patch.object(live_loop.order_wiring,
                                      "build_sdk_client",
                                      return_value=c), \
                    mock.patch.object(live_loop, "http_get_json",
                                      return_value={"blocked": False}):
                code = live_loop.mode_dry_run(d, d, log, args)
            self.assertEqual(code, 0)
            kinds = [k for k, _ in c.calls]
            self.assertNotIn("post", kinds)


if __name__ == "__main__":
    unittest.main(verbosity=1)
