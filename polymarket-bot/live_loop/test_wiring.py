"""Tes wiring order (mock SDK — TIDAK ADA jaringan privat, TIDAK ADA
order nyata, hanya nilai FAKE-*).

Jalankan: cd ~/workspace/polymarket-bot/live_loop_build &&
python3 test_wiring.py
"""

import io
import os
import sys
import unittest
from contextlib import redirect_stdout
from types import SimpleNamespace
from unittest import mock

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import order_wiring  # noqa: E402

SIGNER = order_wiring.SIGNER_WALLET_ADDRESS
PROFILE = order_wiring.PROFILE_WALLET_ADDRESS
TOKEN = "12345678901234567890"


class FakeSigned(SimpleNamespace):
    pass


class FakeResponse(SimpleNamespace):
    pass


class FakePage:
    def __init__(self, items):
        self.items = items


class FakePaginator:
    def __init__(self, items):
        self.items = items

    def first_page(self):
        return FakePage(self.items)

    def __iter__(self):
        yield FakePage(self.items)


class FakeClient:
    """Klien SDK palsu: mencatat semua panggilan, tanpa jaringan."""

    def __init__(self, wallet=SIGNER, passphrase="FAKE-PASSPHRASE-1"):
        self.calls = []
        self.wallet = wallet
        self.credentials = SimpleNamespace(
            key="FAKE-API-KEY-1", secret="FAKE-SECRET-1",
            passphrase=passphrase)
        self.open_orders = []
        self.positions = []
        self.post_raises = None
        self.place_response = None

    def _signed(self, kw):
        return FakeSigned(
            side=kw.get("side"), token_id=kw.get("token_id"),
            order_type=kw.get("order_type", "GTC"),
            maker=SIGNER, signer=SIGNER,
            maker_amount=1000, taker_amount=1000,
            expiration=9999999999, post_only=kw.get("post_only", False),
            signature="FAKE-SIGNATURE-XXX", salt=12345)

    def create_limit_order(self, **kw):
        self.calls.append(("create_limit", kw))
        return self._signed(kw)

    def create_market_order(self, **kw):
        self.calls.append(("create_market", kw))
        return self._signed(kw)

    def post_order(self, signed):
        if self.post_raises is not None:
            raise self.post_raises
        self.calls.append(("post", signed))
        return self.place_response or FakeResponse(
            order_id="FAKE-ORDER-1", status="matched", ok=True,
            making_amount="1.0", taking_amount="1.0",
            trade_ids=("FAKE-TRADE-1", "FAKE-TRADE-2"))

    def place_limit_order(self, **kw):
        self.calls.append(("place_limit", kw))
        return self.post_order(self._signed(kw))

    def place_market_order(self, **kw):
        self.calls.append(("place_market", kw))
        return self.post_order(self._signed(kw))

    def list_open_orders(self, token_id=None):
        self.calls.append(("list_open_orders", token_id))
        return FakePaginator(self.open_orders)

    def list_positions(self):
        self.calls.append(("list_positions", None))
        return FakePaginator(self.positions)

    def cancel_order(self, order_id):
        self.calls.append(("cancel", order_id))
        return True

    def close(self):
        pass


class FakeSecureCls:
    calls = []

    @classmethod
    def create(cls, private_key, wallet):
        cls.calls.append((private_key, wallet))
        return FakeClient(wallet=wallet)


class TestBuildAndValidate(unittest.TestCase):
    def test_limit_build_calls_client_exact_no_post(self):
        c = FakeClient()
        signed = order_wiring.build_limit_order(
            c, token_id=TOKEN, price=0.13, size=7, side="BUY")
        self.assertEqual(signed.side, "BUY")
        self.assertEqual([k for k, _ in c.calls], ["create_limit"])
        kw = c.calls[0][1]
        self.assertEqual(kw["token_id"], TOKEN)
        self.assertEqual(kw["price"], 0.13)
        self.assertEqual(kw["size"], 7)

    def test_limit_validation_rejects_before_client(self):
        c = FakeClient()
        bad = [(TOKEN, 0, 5, "BUY"), (TOKEN, 1, 5, "BUY"),
               (TOKEN, 0.5, 0, "BUY"), (TOKEN, 0.5, 5, "HOLD"),
               ("", 0.5, 5, "BUY"), ("abc", 0.5, 5, "BUY"),
               (TOKEN, 0.5, -1, "SELL")]
        for token_id, price, size, side in bad:
            with self.assertRaises(ValueError):
                order_wiring.build_limit_order(
                    c, token_id=token_id, price=price, size=size,
                    side=side)
        self.assertEqual(c.calls, [])

    def test_market_buy_uses_amount_sell_uses_shares(self):
        c = FakeClient()
        order_wiring.build_market_order(c, token_id=TOKEN, side="BUY",
                                        amount=1.0)
        self.assertEqual(c.calls[0][1]["amount"], 1.0)
        self.assertNotIn("shares", c.calls[0][1])
        order_wiring.build_market_order(c, token_id=TOKEN, side="SELL",
                                        shares=10)
        self.assertEqual(c.calls[1][1]["shares"], 10)
        self.assertNotIn("amount", c.calls[1][1])
        self.assertEqual(c.calls[1][1]["order_type"], "FAK")

    def test_market_validation_rejects_before_client(self):
        c = FakeClient()
        with self.assertRaises(ValueError):
            order_wiring.build_market_order(c, token_id=TOKEN,
                                            side="BUY")
        with self.assertRaises(ValueError):
            order_wiring.build_market_order(c, token_id=TOKEN,
                                            side="SELL")
        with self.assertRaises(ValueError):
            order_wiring.build_market_order(c, token_id=TOKEN,
                                            side="BUY", amount=1.0,
                                            shares=5)
        with self.assertRaises(ValueError):
            order_wiring.build_market_order(c, token_id=TOKEN,
                                            side="SELL", shares=5,
                                            amount=1.0)
        with self.assertRaises(ValueError):
            order_wiring.build_market_order(c, token_id=TOKEN,
                                            side="BUY", amount=1.0,
                                            order_type="GTC")
        self.assertEqual(c.calls, [])


class TestDryRun(unittest.TestCase):
    def test_dry_run_never_posts(self):
        c = FakeClient()
        c.post_raises = AssertionError("POST dipanggil saat DRY-RUN!")
        s = order_wiring.dry_run_limit_order(
            c, token_id=TOKEN, price=0.13, size=7, side="BUY")
        self.assertFalse(s["posted"])
        self.assertEqual(s["mode"], "DRY-RUN")
        s2 = order_wiring.dry_run_market_order(
            c, token_id=TOKEN, side="SELL", shares=7)
        self.assertFalse(s2["posted"])
        kinds = [k for k, _ in c.calls]
        self.assertNotIn("post", kinds)
        self.assertNotIn("place_limit", kinds)
        self.assertNotIn("place_market", kinds)

    def test_summarize_signed_excludes_signature_and_salt(self):
        c = FakeClient()
        signed = order_wiring.build_limit_order(
            c, token_id=TOKEN, price=0.5, size=5, side="SELL")
        s = order_wiring.summarize_signed(signed)
        self.assertNotIn("signature", s)
        self.assertNotIn("salt", s)
        blob = json_blob(s)
        self.assertNotIn("FAKE-SIGNATURE", blob)
        self.assertEqual(s["side"], "SELL")

    def test_post_returns_summary(self):
        c = FakeClient()
        signed = order_wiring.build_limit_order(
            c, token_id=TOKEN, price=0.5, size=5, side="BUY")
        s = order_wiring.post_signed_order(c, signed)
        self.assertEqual(s["order_id"], "FAKE-ORDER-1")
        self.assertEqual(s["status"], "matched")
        self.assertTrue(s["ok"])
        self.assertEqual(s["trade_count"], 2)

    def test_place_live_calls_place(self):
        c = FakeClient()
        s = order_wiring.place_limit_order_live(
            c, token_id=TOKEN, price=0.5, size=5, side="BUY")
        self.assertEqual(s["order_id"], "FAKE-ORDER-1")
        self.assertIn("place_limit", [k for k, _ in c.calls])


def json_blob(obj):
    import json
    return json.dumps(obj, default=str)


class TestBuildSdkClient(unittest.TestCase):
    def _run(self, derived):
        FakeSecureCls.calls = []
        with mock.patch.object(order_wiring, "sdk_available",
                               return_value=True), \
                mock.patch.object(order_wiring, "local_wallet_address",
                                  return_value=(derived, "ok")), \
                mock.patch.object(order_wiring,
                                  "_get_secure_client_class",
                                  return_value=FakeSecureCls), \
                redirect_stdout(io.StringIO()):
            return order_wiring.build_sdk_client("FAKE-PRIVATE-KEY-1")

    def test_signer_ok_builds(self):
        client = self._run(SIGNER)
        self.assertIsNotNone(client)
        self.assertEqual(FakeSecureCls.calls,
                         [("FAKE-PRIVATE-KEY-1", SIGNER)])

    def test_profile_derived_refused_without_create(self):
        # Regresi 2026-11-02: turunan == alamat PROFIL (bukan signer)
        # harus DITOLAK — hanya signer yang boleh jadi identitas.
        client = self._run(PROFILE)
        self.assertIsNone(client)
        self.assertEqual(FakeSecureCls.calls, [])

    def test_random_derived_refused_without_create(self):
        client = self._run("0x0000000000000000000000000000000000000001")
        self.assertIsNone(client)
        self.assertEqual(FakeSecureCls.calls, [])

    def test_incomplete_credentials_refused(self):
        FakeSecureCls.calls = []

        class IncompleteCls:
            @classmethod
            def create(cls, private_key, wallet):
                return FakeClient(wallet=wallet, passphrase=None)

        with mock.patch.object(order_wiring, "sdk_available",
                               return_value=True), \
                mock.patch.object(order_wiring, "local_wallet_address",
                                  return_value=(SIGNER, "ok")), \
                mock.patch.object(order_wiring,
                                  "_get_secure_client_class",
                                  return_value=IncompleteCls), \
                redirect_stdout(io.StringIO()):
            client = order_wiring.build_sdk_client("FAKE-PRIVATE-KEY-1")
        self.assertIsNone(client)


class TestVerifyPost(unittest.TestCase):
    def test_filled_market_verified(self):
        c = FakeClient()
        c.open_orders = []
        v = order_wiring.verify_post(
            c, token_id=TOKEN, order_id="FAKE-ORDER-1",
            response_summary={"ok": True, "status": "matched",
                              "trade_count": 2},
            expect="filled")
        self.assertTrue(v["verified"])

    def test_filled_market_still_open_not_verified(self):
        c = FakeClient()
        c.open_orders = [SimpleNamespace(
            id="FAKE-ORDER-1", side="SELL", price=0.5,
            original_size="10", size_matched="0", status="live")]
        v = order_wiring.verify_post(
            c, token_id=TOKEN, order_id="FAKE-ORDER-1",
            response_summary={"ok": True, "status": "live",
                              "trade_count": 0},
            expect="filled")
        self.assertFalse(v["verified"])

    def test_limit_resting_verified(self):
        c = FakeClient()
        c.open_orders = [SimpleNamespace(
            id="FAKE-ORDER-1", side="BUY", price=0.13,
            original_size="7", size_matched="0", status="live")]
        v = order_wiring.verify_post(
            c, token_id=TOKEN, order_id="FAKE-ORDER-1",
            response_summary={"ok": True, "status": "live",
                              "trade_count": 0},
            expect="resting-or-filled")
        self.assertTrue(v["verified"])

    def test_open_orders_read_failure_never_verified(self):
        c = FakeClient()

        def boom(token_id=None):
            raise RuntimeError("jaringan putus")

        c.list_open_orders = boom
        v = order_wiring.verify_post(
            c, token_id=TOKEN, order_id="FAKE-ORDER-1",
            response_summary={"ok": True, "status": "matched",
                              "trade_count": 2},
            expect="filled")
        self.assertFalse(v["verified"])
        self.assertIn("gagal", v["reason"])


class TestPositionsAndAdopt(unittest.TestCase):
    def test_position_size_tuple(self):
        c = FakeClient()
        c.positions = [SimpleNamespace(asset_id=TOKEN,
                                       current_size="7")]
        size, ok = order_wiring.position_size_for_token(c, TOKEN)
        self.assertTrue(ok)
        self.assertEqual(size, 7.0)
        size, ok = order_wiring.position_size_for_token(c, "999")
        self.assertTrue(ok)
        self.assertIsNone(size)

        def boom():
            raise RuntimeError("gagal")

        c.list_positions = boom
        size, ok = order_wiring.position_size_for_token(c, TOKEN)
        self.assertFalse(ok)
        self.assertIsNone(size)

    def test_adopt_posted_order(self):
        c = FakeClient()
        c.open_orders = [
            SimpleNamespace(id="X-1", side="SELL", price=0.5,
                            original_size="10", size_matched="0",
                            status="live"),
            SimpleNamespace(id="B-1", side="BUY", price=0.13,
                            original_size="7", size_matched="0",
                            status="live"),
        ]
        self.assertEqual(order_wiring.adopt_posted_order(
            c, TOKEN, "BUY", 0.13, 7), "B-1")
        self.assertIsNone(order_wiring.adopt_posted_order(
            c, TOKEN, "BUY", 0.14, 7))
        self.assertIsNone(order_wiring.adopt_posted_order(
            c, TOKEN, "BUY", 0.13, 8))


if __name__ == "__main__":
    unittest.main(verbosity=1)
