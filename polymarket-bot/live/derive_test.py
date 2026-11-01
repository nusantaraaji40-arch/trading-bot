#!/usr/bin/env python3
"""Offline tests for derive_creds.py.

No network, no real secrets, no derivation is ever performed here.
The dummy value below is an obviously fake placeholder string, not a
real key; tests assert it never appears in the script's output.

What is tested:
  * CHECK mode presence words and not-ready exit code.
  * CHECK mode never prints the (dummy) key value.
  * DERIVE gate: missing --derive flag, or missing DERIVE_APPROVED=1,
    both refuse without touching the SDK.
  * DERIVE with flag + approval but no SDK installed refuses cleanly
    (run with `python -S` so site-packages cannot provide an SDK).
  * Guard env vars refuse the run.
  * Static guard: the script source contains no print of a secret
    env value, no file write of credentials, no archived
    py-clob-client import, and no order-placement call.

Deliberately NOT tested here (needs the owner's host + real SDK):
  * a successful DERIVE with the real SDK and the owner's real key —
    that runs only on the owner's machine and is verified there by
    CHECK output words, never by values. DERIVE success IS tested
    below, but against a fake SDK package in a temp dir, never
    against real credentials.
"""

import os
import subprocess
import sys
import tempfile
import unittest

SCRIPT = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                      "derive_creds.py")
DUMMY = "dummy-test-value-not-a-real-key"

STRIPPED = ("POLY_PRIVATE_KEY", "POLY_API_KEY", "POLY_SECRET",
            "POLY_PASSPHRASE", "DERIVE_APPROVED",
            "PRINT_SECRETS", "DUMP_SECRETS", "SHOW_SECRETS", "SAVE_SECRETS")


def clean_env(extra=None):
    env = {k: v for k, v in os.environ.items() if k not in STRIPPED}
    env.pop("PYTHONPATH", None)
    if extra:
        env.update(extra)
    return env


def run(args, env, use_no_site=False):
    cmd = [sys.executable]
    if use_no_site:
        cmd.append("-S")
    cmd += [SCRIPT] + args
    return subprocess.run(cmd, capture_output=True, text=True,
                          env=env, timeout=60)


class TestCheckMode(unittest.TestCase):
    def test_empty_env_is_not_ready(self):
        proc = run([], clean_env())
        self.assertEqual(proc.returncode, 1)
        self.assertIn("POLY_PRIVATE_KEY: absent", proc.stdout)
        self.assertIn("status: not-ready", proc.stdout)

    def test_check_never_prints_key_value(self):
        proc = run([], clean_env({"POLY_PRIVATE_KEY": DUMMY}))
        self.assertIn("POLY_PRIVATE_KEY: present", proc.stdout)
        self.assertNotIn(DUMMY, proc.stdout)
        self.assertNotIn(DUMMY, proc.stderr)


class TestDeriveGate(unittest.TestCase):
    def test_derive_without_approval_refused(self):
        proc = run(["--derive"], clean_env({"POLY_PRIVATE_KEY": DUMMY}))
        self.assertEqual(proc.returncode, 2)
        self.assertIn("refused", proc.stdout)
        self.assertNotIn(DUMMY, proc.stdout)
        self.assertNotIn(DUMMY, proc.stderr)

    def test_approval_without_flag_stays_in_check_mode(self):
        proc = run([], clean_env({"POLY_PRIVATE_KEY": DUMMY,
                                  "DERIVE_APPROVED": "1"}))
        self.assertNotIn("done", proc.stdout.splitlines())
        self.assertIn("status:", proc.stdout)

    def test_derive_without_sdk_refused_cleanly(self):
        proc = run(["--derive"],
                   clean_env({"POLY_PRIVATE_KEY": DUMMY,
                              "DERIVE_APPROVED": "1"}),
                   use_no_site=True)
        self.assertEqual(proc.returncode, 3)
        self.assertIn("not installed", proc.stdout)
        self.assertIn("install", proc.stdout.lower())
        self.assertNotIn(DUMMY, proc.stdout)
        self.assertNotIn(DUMMY, proc.stderr)


class TestGuardsAndSource(unittest.TestCase):
    def test_guard_env_refuses(self):
        proc = run([], clean_env({"PRINT_SECRETS": "1"}))
        self.assertEqual(proc.returncode, 2)
        self.assertIn("refused", proc.stdout)

    def test_source_never_prints_secret_values(self):
        with open(SCRIPT, "r", encoding="utf-8") as fh:
            source = fh.read()
        for line in source.splitlines():
            if "print(" in line:
                for forbidden in ("POLY_PRIVATE_KEY", "POLY_SECRET",
                                  "POLY_PASSPHRASE", "secret_value",
                                  "api_key_value", "private_key_value"):
                    self.assertNotIn(forbidden, line,
                                     "print line must not reference "
                                     "a secret value: %r" % line)
            if "open(" in line:
                self.assertNotIn("POLY_", line,
                                 "file open must not involve "
                                 "credentials: %r" % line)
        self.assertIn("SecureClient", source)
        self.assertNotIn("py_clob_client", source)
        # REGRESI bug CHECK host: modul impor lama tidak boleh dipakai
        # sebagai impor di mana pun. Namanya dibangun lewat gabungan
        # supaya berkas tes ini sendiri tidak mengandung literalnya.
        bad = "polymarket" + "_client"
        for pattern in ("from " + bad + " import",
                        "import " + bad,
                        'find_spec("' + bad + '")'):
            self.assertNotIn(pattern, source, pattern)

    def test_source_has_no_order_or_network_trade_calls(self):
        with open(SCRIPT, "r", encoding="utf-8") as fh:
            source = fh.read()
        for forbidden in ("place_order", "create_order", "submit_order",
                          "requests.", "urllib"):
            self.assertNotIn(forbidden, source)


# Fake SDK package for subprocess DERIVE tests. The address placeholder
# ADDR is replaced per test; values here are obviously fake.
FAKE_SDK_INIT = '''
from types import SimpleNamespace


class SecureClient:
    @classmethod
    def create(cls, private_key=None, wallet=None, **kwargs):
        return SimpleNamespace(
            wallet=wallet,
            credentials=SimpleNamespace(key="x", secret="y",
                                        passphrase="z"),
            close=lambda: None)
'''

FAKE_ETH_ACCOUNT = '''
from types import SimpleNamespace


class Account:
    @staticmethod
    def from_key(key):
        return SimpleNamespace(address="ADDR")
'''


class TestDeriveWithFakeSdk(unittest.TestCase):
    """DERIVE end-to-end melawan SDK palsu (subproses, offline).

    Paket palsu diletakkan di temp dir dan dimuat lewat PYTHONPATH,
    sehingga derive_creds.py yang asli diuji tanpa kunci nyata dan
    tanpa jaringan.
    """

    EXPECTED = "0x911379D40dc42d8198baA4f1b7bB29b71A7d3d72"

    def _pkgdir(self, address):
        tmp = tempfile.mkdtemp()
        os.makedirs(os.path.join(tmp, "polymarket"))
        with open(os.path.join(tmp, "polymarket", "__init__.py"),
                  "w") as f:
            f.write(FAKE_SDK_INIT)
        with open(os.path.join(tmp, "eth_account.py"), "w") as f:
            f.write(FAKE_ETH_ACCOUNT.replace("ADDR", address))
        return tmp

    def test_derive_success_with_fake_sdk(self):
        tmp = self._pkgdir(self.EXPECTED)
        env = clean_env({"POLY_PRIVATE_KEY": DUMMY,
                         "DERIVE_APPROVED": "1",
                         "PYTHONPATH": tmp})
        proc = run(["--derive"], env)
        self.assertEqual(proc.returncode, 0,
                         proc.stdout + proc.stderr)
        self.assertIn("done", proc.stdout)
        self.assertIn(self.EXPECTED, proc.stdout)
        self.assertIn("POLY_API_KEY produced", proc.stdout)
        self.assertIn("POLY_SECRET produced", proc.stdout)
        self.assertIn("POLY_PASSPHRASE produced", proc.stdout)
        self.assertNotIn(DUMMY, proc.stdout)
        self.assertNotIn(DUMMY, proc.stderr)

    def test_derive_address_mismatch_refused(self):
        tmp = self._pkgdir("0x0000000000000000000000000000000000000001")
        env = clean_env({"POLY_PRIVATE_KEY": DUMMY,
                         "DERIVE_APPROVED": "1",
                         "PYTHONPATH": tmp})
        proc = run(["--derive"], env)
        self.assertEqual(proc.returncode, 2)
        self.assertIn("refused", proc.stdout)
        self.assertNotIn(DUMMY, proc.stdout)
        self.assertNotIn(DUMMY, proc.stderr)


if __name__ == "__main__":
    unittest.main(verbosity=2)
