"""Tes offline paket live Polymarket — stdlib unittest saja.

TIDAK ADA jaringan, TIDAK ADA secret, TIDAK ADA order.
Semua tes memakai fungsi murni atau direktori sementara + environment
tiruan. Jalankan:  python3 test_live.py
"""

import json
import os
import sys
import tempfile
import unittest
from unittest import mock

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import live_run  # noqa: E402


def valid_updown():
    return {"category": "updown", "chain": "polygon", "collateral": "USDC",
            "modal_usd": 25.0, "first_trade_usd": 5.0, "sl_pct": 5.0,
            "tp_pct": 20.0, "kill_switch_pct": 15.0, "min_order_size": 5}


def valid_ladder():
    p = valid_updown()
    p.update({"category": "weather", "tp1_pct": 10.0, "tp2_pct": 15.0})
    p.pop("tp_pct")
    return p


class TestParamsValidation(unittest.TestCase):
    def test_example_file_passes(self):
        here = os.path.dirname(os.path.abspath(__file__))
        with open(os.path.join(here, "params.example.json")) as f:
            p = json.load(f)
        errors, _ = live_run.validate_params_data(p)
        self.assertEqual(errors, [])

    def test_valid_updown_and_ladder(self):
        for p in (valid_updown(), valid_ladder()):
            errors, _ = live_run.validate_params_data(p)
            self.assertEqual(errors, [], p)

    def test_rejects_bad_category_chain_collateral(self):
        for key, bad in (("category", "politics"), ("chain", "ethereum"),
                         ("collateral", "pUSD")):
            p = valid_updown()
            p[key] = bad
            errors, _ = live_run.validate_params_data(p)
            self.assertTrue(errors, key)

    def test_modal_and_first_trade(self):
        p = valid_updown()
        p["modal_usd"] = 0
        self.assertTrue(live_run.validate_params_data(p)[0])
        p = valid_updown()
        p["first_trade_usd"] = 0
        self.assertTrue(live_run.validate_params_data(p)[0])
        p = valid_updown()
        p["first_trade_usd"] = 25.0  # == modal: boleh
        self.assertEqual(live_run.validate_params_data(p)[0], [])
        p = valid_updown()
        p["first_trade_usd"] = 25.01  # > modal: tolak
        self.assertTrue(live_run.validate_params_data(p)[0])

    def test_sl_tp_ks_boundaries(self):
        # Batas bawah/atas inklusif lolos, di luar ditolak.
        for field, lo_ok, hi_ok, lo_bad, hi_bad in (
                ("sl_pct", 1, 50, 0, 51),
                ("tp_pct", 1, 50, 0, 51),
                ("kill_switch_pct", 5, 50, 4, 51)):
            for val, ok in ((lo_ok, True), (hi_ok, True),
                            (lo_bad, False), (hi_bad, False)):
                p = valid_updown()
                p[field] = val
                errors, _ = live_run.validate_params_data(p)
                self.assertEqual(errors == [], ok, (field, val))

    def test_tp_below_sl_is_warning_not_rejection(self):
        p = valid_updown()
        p["tp_pct"] = 3.0  # < SL 5: peringatan, bukan error
        errors, warnings = live_run.validate_params_data(p)
        self.assertEqual(errors, [])
        self.assertTrue(warnings)

    def test_ladder_tp2_below_tp1_rejected(self):
        p = valid_ladder()
        p["tp2_pct"] = 9.0
        self.assertTrue(live_run.validate_params_data(p)[0])

    def test_min_order_size_floor(self):
        p = valid_updown()
        p["min_order_size"] = 4
        self.assertTrue(live_run.validate_params_data(p)[0])


class TestGeoblockParsing(unittest.TestCase):
    def test_blocked_allowed_unknown(self):
        self.assertEqual(live_run.parse_geoblock({"blocked": True}),
                         "blocked")
        self.assertEqual(live_run.parse_geoblock({"blocked": False}),
                         "allowed")
        self.assertEqual(live_run.parse_geoblock({}), "unknown")
        self.assertEqual(
            live_run.parse_geoblock({"_transport_error": "boom"}),
            "unknown")
        self.assertEqual(live_run.parse_geoblock("bukan-dict"), "unknown")


class TestGates(unittest.TestCase):
    def _setup(self, tmp, with_approved=True, with_params=True,
               params=None):
        if with_approved:
            with open(os.path.join(tmp, "LIVE_APPROVED.txt"), "w") as f:
                f.write("Disetujui contoh (tes saja, bukan persetujuan).")
        if with_params:
            with open(os.path.join(tmp, "params.json"), "w") as f:
                json.dump(params if params is not None else valid_updown(),
                          f)

    def _env(self, extra=None):
        # Model baru: SATU-SATUNYA rahasia adalah private key.
        # Kredensial API tersimpan TIDAK LAGI dibaca bot.
        env = {"LIVE_TRADING": "1",
               "POLY_PRIVATE_KEY": "kunci-tiruan-untuk-tes"}
        if extra:
            env.update(extra)
        return env

    def _geoblock_allowed(self):
        return mock.patch.object(
            live_run, "http_get_json",
            return_value=(200, {"blocked": False}))

    def _sdk_ok(self):
        return mock.patch.object(live_run, "sdk_available",
                                 return_value=True)

    def test_missing_live_trading_env_blocks(self):
        with tempfile.TemporaryDirectory() as tmp:
            self._setup(tmp)
            env = self._env()
            del env["LIVE_TRADING"]
            with mock.patch.dict(os.environ, env, clear=True):
                with self.assertRaises(SystemExit) as cm:
                    live_run.check_gates(tmp)
                self.assertEqual(cm.exception.code, 3)

    def test_missing_approval_file_blocks(self):
        with tempfile.TemporaryDirectory() as tmp:
            self._setup(tmp, with_approved=False)
            with mock.patch.dict(os.environ, self._env(), clear=True):
                with self.assertRaises(SystemExit) as cm:
                    live_run.check_gates(tmp)
                self.assertEqual(cm.exception.code, 3)

    def test_missing_params_file_blocks(self):
        with tempfile.TemporaryDirectory() as tmp:
            self._setup(tmp, with_params=False)
            with mock.patch.dict(os.environ, self._env(), clear=True):
                with self.assertRaises(SystemExit) as cm:
                    live_run.check_gates(tmp)
                self.assertEqual(cm.exception.code, 3)

    def test_invalid_params_blocks(self):
        with tempfile.TemporaryDirectory() as tmp:
            bad = valid_updown()
            bad["sl_pct"] = 99
            self._setup(tmp, params=bad)
            with mock.patch.dict(os.environ, self._env(), clear=True):
                with self.assertRaises(SystemExit) as cm:
                    live_run.check_gates(tmp)
                self.assertEqual(cm.exception.code, 3)

    def test_blocked_geoblock_blocks(self):
        with tempfile.TemporaryDirectory() as tmp:
            self._setup(tmp)
            with mock.patch.dict(os.environ, self._env(), clear=True), \
                    mock.patch.object(
                        live_run, "http_get_json",
                        return_value=(200, {"blocked": True})):
                with self.assertRaises(SystemExit) as cm:
                    live_run.check_gates(tmp)
                self.assertEqual(cm.exception.code, 3)

    def test_unknown_geoblock_blocks_fail_closed(self):
        with tempfile.TemporaryDirectory() as tmp:
            self._setup(tmp)
            with mock.patch.dict(os.environ, self._env(), clear=True), \
                    mock.patch.object(
                        live_run, "http_get_json",
                        return_value=(0, {"_transport_error": "boom"})):
                with self.assertRaises(SystemExit) as cm:
                    live_run.check_gates(tmp)
                self.assertEqual(cm.exception.code, 3)

    def test_missing_credential_blocks(self):
        with tempfile.TemporaryDirectory() as tmp:
            self._setup(tmp)
            env = self._env()
            del env["POLY_PRIVATE_KEY"]
            with mock.patch.dict(os.environ, env, clear=True), \
                    self._geoblock_allowed():
                with self.assertRaises(SystemExit) as cm:
                    live_run.check_gates(tmp)
                self.assertEqual(cm.exception.code, 2)

    def test_stored_api_creds_alone_do_not_pass_gates(self):
        # REGRESI pola baru: tiga nilai API tersimpan saja (tanpa
        # private key) TIDAK LAGI cukup — gerbang harus menolak.
        with tempfile.TemporaryDirectory() as tmp:
            self._setup(tmp)
            env = {"LIVE_TRADING": "1", "POLY_API_KEY": "x",
                   "POLY_SECRET": "x", "POLY_PASSPHRASE": "x",
                   "POLY_ADDRESS": "x"}
            with mock.patch.dict(os.environ, env, clear=True), \
                    self._geoblock_allowed():
                with self.assertRaises(SystemExit) as cm:
                    live_run.check_gates(tmp)
                self.assertEqual(cm.exception.code, 2)

    def test_missing_sdk_blocks(self):
        with tempfile.TemporaryDirectory() as tmp:
            self._setup(tmp)
            with mock.patch.dict(os.environ, self._env(), clear=True), \
                    self._geoblock_allowed(), \
                    mock.patch.object(live_run, "sdk_available",
                                      return_value=False):
                with self.assertRaises(SystemExit) as cm:
                    live_run.check_gates(tmp)
                self.assertEqual(cm.exception.code, 2)

    def test_all_gates_pass_returns_params(self):
        with tempfile.TemporaryDirectory() as tmp:
            self._setup(tmp)
            with mock.patch.dict(os.environ, self._env(), clear=True), \
                    self._geoblock_allowed(), self._sdk_ok():
                params = live_run.check_gates(tmp)
            self.assertEqual(params["category"], "updown")


class TestExitPriority(unittest.TestCase):
    def test_kill_switch_beats_sl_and_tp(self):
        # Nilai total di bawah KS sekaligus ask di bawah SL dan di atas
        # TP: yang menang harus KILL_SWITCH.
        action, qty, reason = live_run.decide_exit(
            entry_ask=0.10, ask=0.13, bid=0.12, remaining=10,
            tp1_done=True, total_value=80.0, start_value=100.0,
            category="updown", sl_pct=5.0, tp_pct=20.0,
            kill_switch_pct=15.0)
        self.assertEqual((action, reason), ("SELL_ALL", "KILL_SWITCH"))
        self.assertEqual(qty, 10)

    def test_sl_beats_tp(self):
        # Ask di bawah SL sekaligus di atas TP tidak mungkin bersamaan
        # untuk satu entry; uji SL murni di sini, TP murni di bawah.
        action, _, reason = live_run.decide_exit(
            entry_ask=0.10, ask=0.094, bid=0.09, remaining=10,
            tp1_done=False, total_value=100.0, start_value=100.0,
            category="updown", sl_pct=5.0, tp_pct=20.0)
        self.assertEqual((action, reason), ("SELL_ALL", "SL"))

    def test_tp20_sell_all_for_updown(self):
        action, qty, reason = live_run.decide_exit(
            entry_ask=0.10, ask=0.12, bid=0.11, remaining=10,
            tp1_done=False, total_value=100.0, start_value=100.0,
            category="updown", sl_pct=5.0, tp_pct=20.0)
        self.assertEqual((action, qty, reason), ("SELL_ALL", 10, "TP20"))

    def test_ladder_tp2_beats_tp1_and_tp1_is_partial(self):
        action, qty, reason = live_run.decide_exit(
            entry_ask=0.10, ask=0.115, bid=0.11, remaining=10,
            tp1_done=True, total_value=100.0, start_value=100.0,
            category="weather", sl_pct=5.0, tp1_pct=10.0, tp2_pct=15.0)
        self.assertEqual((action, qty, reason), ("SELL_ALL", 10, "TP2"))
        action, qty, reason = live_run.decide_exit(
            entry_ask=0.10, ask=0.11, bid=0.105, remaining=10,
            tp1_done=False, total_value=100.0, start_value=100.0,
            category="weather", sl_pct=5.0, tp1_pct=10.0, tp2_pct=15.0)
        self.assertEqual((action, qty, reason), ("SELL_PARTIAL", 5, "TP1"))

    def test_hold_when_nothing_triggered(self):
        action, qty, reason = live_run.decide_exit(
            entry_ask=0.10, ask=0.10, bid=0.099, remaining=10,
            tp1_done=False, total_value=100.0, start_value=100.0,
            category="updown", sl_pct=5.0, tp_pct=20.0)
        self.assertEqual((action, qty, reason), ("HOLD", 0, "HOLD"))


class TestMinOrderSize(unittest.TestCase):
    def test_below_minimum_rejected_not_rounded(self):
        self.assertEqual(live_run.enforce_min_size(4), 0)
        self.assertEqual(live_run.enforce_min_size(5), 5)
        self.assertEqual(live_run.enforce_min_size(12), 12)

    def test_exit_blocked_when_remaining_below_minimum(self):
        action, qty, reason = live_run.decide_exit(
            entry_ask=0.10, ask=0.094, bid=0.09, remaining=4,
            tp1_done=False, total_value=100.0, start_value=100.0,
            category="updown", sl_pct=5.0, tp_pct=20.0)
        self.assertEqual(action, "BLOCKED_MIN_SIZE")
        self.assertEqual(qty, 0)
        self.assertIn("MIN_SIZE", reason)


class TestNeverRetry(unittest.TestCase):
    def test_should_retry_is_always_false(self):
        self.assertIs(live_run.should_retry_after_error(), False)

    def test_error_path_always_aborts_regardless_of_state(self):
        for state in ({"orders": []}, {"orders": ["x"]},
                      {"error": "timeout"}, None, {}):
            action, _ = live_run.decide_after_order_error(state)
            self.assertEqual(action, "ABORT_NO_RETRY")


class TestRuntimeRederivation(unittest.TestCase):
    """Pola baru: derive tiap jalan via SecureClient.create SDK nyata.

    SDK dipalsukan lewat sys.modules dengan modul bernama
    `polymarket` (nama impor SDK 0.15.0 yang benar) berisi kelas
    SecureClient dengan factory create() seperti aslinya.
    Nilai-nilai di sini adalah tiruan yang jelas-jelas palsu,
    bukan rahasia siapa pun.
    """

    def _install_fake(self, client=None, create_raises=False):
        """Pasang modul `polymarket` palsu; kembalikan (old, kelas)."""
        import types

        class FakeSecureClient:
            calls = []

            def __init__(self, wallet, credentials):
                self.wallet = wallet
                self.credentials = credentials

            @classmethod
            def create(cls, private_key=None, wallet=None, **_kwargs):
                cls.calls.append((private_key, wallet))
                if create_raises:
                    raise RuntimeError("boom")
                return client

        mod = types.ModuleType("polymarket")
        mod.SecureClient = FakeSecureClient
        old = sys.modules.get("polymarket")
        sys.modules["polymarket"] = mod
        return old, FakeSecureClient

    def _restore(self, old):
        if old is None:
            sys.modules.pop("polymarket", None)
        else:
            sys.modules["polymarket"] = old

    def _client(self, wallet, key="K", secret="S", passphrase="P"):
        from types import SimpleNamespace
        return SimpleNamespace(
            wallet=wallet,
            credentials=SimpleNamespace(key=key, secret=secret,
                                        passphrase=passphrase))

    def _ok_env(self):
        return {"POLY_PRIVATE_KEY": "FAKE-PRIVATE-KEY-1"}

    def _address_ok(self):
        return mock.patch.object(
            live_run, "local_wallet_address",
            return_value=(live_run.SIGNER_WALLET_ADDRESS, "ok"))

    def _sdk_ok(self):
        return mock.patch.object(live_run, "sdk_available",
                                 return_value=True)

    def test_create_success_builds_client_without_printing_values(self):
        import io
        from contextlib import redirect_stdout
        fake = self._client(live_run.SIGNER_WALLET_ADDRESS,
                            key="FAKE-API-KEY-1", secret="FAKE-SECRET-1",
                            passphrase="FAKE-PASSPHRASE-1")
        old, fake_cls = self._install_fake(client=fake)
        try:
            with mock.patch.dict(os.environ, self._ok_env(), clear=True), \
                    self._address_ok(), self._sdk_ok():
                buf = io.StringIO()
                with redirect_stdout(buf):
                    client = live_run.build_sdk_client()
                out = buf.getvalue()
            self.assertIs(client, fake)
            self.assertEqual(fake_cls.calls,
                             [("FAKE-PRIVATE-KEY-1",
                               live_run.SIGNER_WALLET_ADDRESS)])
            for secret in ("FAKE-PRIVATE-KEY-1", "FAKE-API-KEY-1",
                           "FAKE-SECRET-1", "FAKE-PASSPHRASE-1"):
                self.assertNotIn(secret, out)
        finally:
            self._restore(old)

    def test_create_failure_returns_none(self):
        old, _ = self._install_fake(create_raises=True)
        try:
            with mock.patch.dict(os.environ, self._ok_env(), clear=True), \
                    self._address_ok(), self._sdk_ok():
                self.assertIsNone(live_run.build_sdk_client())
        finally:
            self._restore(old)

    def test_missing_secure_client_returns_none(self):
        import types
        mod = types.ModuleType("polymarket")  # tanpa SecureClient
        old = sys.modules.get("polymarket")
        sys.modules["polymarket"] = mod
        try:
            with mock.patch.dict(os.environ, self._ok_env(), clear=True), \
                    self._address_ok(), self._sdk_ok():
                self.assertIsNone(live_run.build_sdk_client())
        finally:
            self._restore(old)

    def test_no_sdk_returns_none(self):
        with mock.patch.dict(os.environ, self._ok_env(), clear=True), \
                mock.patch.object(live_run, "sdk_available",
                                  return_value=False):
            self.assertIsNone(live_run.build_sdk_client())

    def test_incomplete_credentials_returns_none(self):
        fake = self._client(live_run.SIGNER_WALLET_ADDRESS, passphrase=None)
        old, _ = self._install_fake(client=fake)
        try:
            with mock.patch.dict(os.environ, self._ok_env(), clear=True), \
                    self._address_ok(), self._sdk_ok():
                self.assertIsNone(live_run.build_sdk_client())
        finally:
            self._restore(old)

    def test_client_wallet_mismatch_returns_none(self):
        fake = self._client("0x0000000000000000000000000000000000000001")
        old, _ = self._install_fake(client=fake)
        try:
            with mock.patch.dict(os.environ, self._ok_env(), clear=True), \
                    self._address_ok(), self._sdk_ok():
                self.assertIsNone(live_run.build_sdk_client())
        finally:
            self._restore(old)

    def test_address_mismatch_returns_none_without_creating(self):
        fake = self._client(live_run.SIGNER_WALLET_ADDRESS)
        old, fake_cls = self._install_fake(client=fake)
        try:
            with mock.patch.dict(os.environ, self._ok_env(), clear=True), \
                    mock.patch.object(
                        live_run, "local_wallet_address",
                        return_value=("0x000000000000000000000000000000"
                                      "0000000000", "ok")), self._sdk_ok():
                self.assertIsNone(live_run.build_sdk_client())
            self.assertEqual(fake_cls.calls, [])
        finally:
            self._restore(old)

    def test_profile_address_derived_returns_none_without_creating(self):
        # Regresi 2026-11-02: akun berstruktur signer + deposit.
        # Alamat turunan yang sama dengan alamat PROFIL/deposit
        # (bukan signer) harus DITOLAK — hanya signer yang boleh
        # menjadi identitas trading.
        fake = self._client(live_run.SIGNER_WALLET_ADDRESS)
        old, fake_cls = self._install_fake(client=fake)
        try:
            with mock.patch.dict(os.environ, self._ok_env(), clear=True), \
                    mock.patch.object(
                        live_run, "local_wallet_address",
                        return_value=(live_run.LIVE_WALLET_ADDRESS,
                                      "ok")), self._sdk_ok():
                self.assertIsNone(live_run.build_sdk_client())
            self.assertEqual(fake_cls.calls, [])
        finally:
            self._restore(old)

    def test_address_unverified_returns_none_without_creating(self):
        # Penjaga efek samping: tanpa verifikasi alamat lokal, jangan
        # panggil create() sama sekali (create untuk wallet non-EOA
        # yang belum ter-deploy bisa men-deploy on-chain).
        fake = self._client(live_run.SIGNER_WALLET_ADDRESS)
        old, fake_cls = self._install_fake(client=fake)
        try:
            with mock.patch.dict(os.environ, self._ok_env(), clear=True), \
                    mock.patch.object(
                        live_run, "local_wallet_address",
                        return_value=(None, "skipped")), self._sdk_ok():
                self.assertIsNone(live_run.build_sdk_client())
            self.assertEqual(fake_cls.calls, [])
        finally:
            self._restore(old)

    def test_no_private_key_returns_none(self):
        with mock.patch.dict(os.environ, {}, clear=True):
            self.assertIsNone(live_run.build_sdk_client())


class TestVerifyStateViaSdk(unittest.TestCase):
    def _paginator(self, items=None, raises=False):
        from types import SimpleNamespace

        class Paginator:
            def first_page(self):
                if raises:
                    raise RuntimeError("boom")
                return SimpleNamespace(items=tuple(items or ()))

        return Paginator()

    def test_counts_open_orders(self):
        from types import SimpleNamespace
        client = SimpleNamespace(
            list_open_orders=lambda: self._paginator(items=(1, 2, 3)))
        self.assertEqual(live_run.verify_state_via_sdk(client),
                         {"orders": 3})

    def test_missing_reader_is_unknown(self):
        from types import SimpleNamespace
        self.assertEqual(live_run.verify_state_via_sdk(SimpleNamespace()),
                         {"orders": "unknown"})

    def test_reader_error_is_reported_not_raised(self):
        from types import SimpleNamespace
        client = SimpleNamespace(
            list_open_orders=lambda: self._paginator(raises=True))
        state = live_run.verify_state_via_sdk(client)
        self.assertIn("error", state)

    def test_none_client_is_none(self):
        self.assertIsNone(live_run.verify_state_via_sdk(None))


class TestOldSdkModuleIsGone(unittest.TestCase):
    """REGRESI bug CHECK host: modul impor lama tidak boleh dipakai.

    Nama modul lama dibangun lewat penggabungan supaya berkas tes
    ini sendiri tidak mengandung literalnya; yang dipindai adalah
    pola impor (from/import/find_spec), bukan sekadar penyebutan
    nama paket pip (tanda hubung) di dokumen.
    """

    def test_no_old_module_import_in_live_files(self):
        import re
        bad = "polymarket" + "_client"
        pattern = re.compile(
            r"(?:from\s+" + bad + r"\s+import|import\s+" + bad +
            r"\b|find_spec\(\"" + bad + r"\"\)|sys\.modules\[\"" +
            bad + r"\"\])")
        here = os.path.dirname(os.path.abspath(__file__))
        for name in ("live_run.py", "derive_creds.py", "test_live.py",
                     "derive_test.py"):
            with open(os.path.join(here, name)) as f:
                source = f.read()
            self.assertEqual(pattern.findall(source), [], name)

    def test_no_old_client_names_in_production_files(self):
        # Nama-nama lama dibangun lewat gabungan supaya berkas tes
        # ini sendiri tidak mengandung literalnya.
        here = os.path.dirname(os.path.abspath(__file__))
        for name in ("live_run.py", "derive_creds.py"):
            with open(os.path.join(here, name)) as f:
                source = f.read()
            for gone in ("Clob" + "Client",
                         "createOrDerive" + "ApiKey",
                         "create_or_derive" + "_api_key"):
                self.assertNotIn(gone, source, (name, gone))


class TestCheckModeNeverPrintsSecrets(unittest.TestCase):
    def test_check_reports_presence_only(self):
        import io
        from contextlib import redirect_stdout
        fake_key = "TOPSECRET-PRIVATE-KEY-VALUE-UNTUK-TES"
        env = {"POLY_PRIVATE_KEY": fake_key}
        with mock.patch.dict(os.environ, env, clear=True), \
                mock.patch.object(
                    live_run, "http_get_json",
                    side_effect=[(200, {"blocked": False}),
                                 (200, [{"id": "m1"}])]):
            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = live_run.mode_check()
            out = buf.getvalue()
        self.assertEqual(rc, 0)
        self.assertNotIn(fake_key, out)
        self.assertIn("POLY_PRIVATE_KEY: ada", out)
        self.assertIn("Nol order dibuat", out)


if __name__ == "__main__":
    unittest.main(verbosity=2)
