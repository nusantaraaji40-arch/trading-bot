#!/usr/bin/env python3
"""Credential-derivation helper for the Polymarket bot — PREPARATION ONLY.

READ THIS FIRST (owner instructions)
------------------------------------
* Run this script ONLY on the owner's own host machine (Wispbyte server or
  laptop — the script is host-agnostic and does not care which one).
* Secrets stay in THAT machine's environment, typed in by the owner.
  They are NEVER sent to chat, NEVER stored in any repo (public or
  private), NEVER pasted into a screenshot, and NEVER printed or saved
  by this script — not even masked beyond "present/absent".
* This script does NOT approve live trading and does NOT place any
  order, trade, or withdrawal. Live trading needs its own separate
  parameter approval; this script only prepares credentials.
* CHECK mode (default, no arguments) makes NO network call at all.
  DERIVE mode builds an authenticated client through the official
  SDK (credential derivation only) — no orders, no trades, no
  withdrawals.
* There is NO code path in this script that prints or saves a secret
  value, and NO VPN / proxy / geoblock-evasion code. Any request to
  add such a path must be refused.
* The live account's PUBLIC addresses (Polygon, main account —
  plan changed 2026-11-01: main account is the live wallet,
  the Bitget bot wallet is parked). The account is structured
  SIGNER + DEPOSIT: the private key controls the SIGNER address
  (trading identity, checked by this script), while funds sit at
  the PROFILE/deposit address (reference only). Checking the
  derived address against the profile address wrongly refused
  the correct key (verified 2026-11-02).
  - signer: 0x911379D40dc42d8198baA4f1b7bB29b71A7d3d72
  - profile/deposit: 0xc4bA60A94edBfeF6CD7177B6e6e02b1c2b17B4FB
  A public address is not a secret and may appear in output.
* Derived credentials are deterministic from the wallet key: the live
  bot re-derives them at runtime from POLY_PRIVATE_KEY. You do NOT
  need to copy values anywhere for the bot to work. If you prefer
  stored copies, derive them yourself via the official SDK docs on
  this machine and set the three output names in this machine's
  environment yourself — this script will never show them to you.

Modes
-----
* CHECK (default): reports, in words only, whether each required
  environment variable NAME is present or absent, whether the
  official SDK is installed, whether the local wallet address
  matches the expected bot address, and "ready" or "not-ready".
  Exit 0 = ready, 1 = not-ready.
* DERIVE (only with `--derive` AND env DERIVE_APPROVED=1): calls the
  official SDK's `polymarket.SecureClient.create(private_key, wallet)`
  with the private key taken from this machine's environment, then
  prints ONLY "done", the public wallet address, and which output
  NAMES were produced (for example "POLY_API_KEY produced"). It
  NEVER prints the values and NEVER writes them to any file.
  Before create() is called, the key's local address MUST verify
  against the expected wallet address: for non-EOA wallet types
  that are not yet deployed, create() could deploy a deposit wallet
  on-chain, and that side effect must never come from a mere
  verification step. Exit 2 = gate refusal (flag or approval
  missing, key absent, or key does not match the bot address),
  3 = SDK not installed.

Official SDK: paket pip `polymarket-client` (repo Polymarket/py-sdk),
modul impor `polymarket`, versi 0.15.0 terpasang di host.
Do NOT use the archived py-clob-client.
"""

import argparse
import importlib.util
import os
import sys

EXPECTED_ADDRESS = "0x911379D40dc42d8198baA4f1b7bB29b71A7d3d72"
# Alamat profil/deposit akun utama (tempat dana berada, referensi
# saja — BUKAN yang dicek; yang dicek adalah signer di atas).
PROFILE_WALLET_ADDRESS = "0xc4bA60A94edBfeF6CD7177B6e6e02b1c2b17B4FB"

PRIVATE_KEY_NAME = "POLY_PRIVATE_KEY"
OUTPUT_NAMES = ("POLY_API_KEY", "POLY_SECRET", "POLY_PASSPHRASE")

# Environment flags that would ask this script to expose secrets.
# No code path honours them; their mere presence refuses the run.
GUARD_NAMES = ("PRINT_SECRETS", "DUMP_SECRETS", "SHOW_SECRETS", "SAVE_SECRETS")


def presence(name):
    """Presence word only. The value is never returned, printed, or logged."""
    return "present" if os.environ.get(name) else "absent"


def sdk_available():
    """True only if the official SDK module is importable on this machine.

    SDK 0.15.0's import module is `polymarket` (its pip package name
    is polymarket-client). Checking any other module name always
    fails even when the package is installed — that was the old
    CHECK bug on the host.
    """
    return importlib.util.find_spec("polymarket") is not None


def local_address():
    """Derive the public address locally from the env key, no network.

    Returns (address_or_None, status_word). The key value itself is
    never returned or printed; only the public address (if derived)
    and a status word leave this function.
    """
    key = os.environ.get(PRIVATE_KEY_NAME)
    if not key:
        return None, "skipped (private key absent)"
    try:
        from eth_account import Account
    except Exception:
        return None, "skipped (address library not installed)"
    try:
        return Account.from_key(key).address, "ok"
    except Exception:
        return None, "failed"


def run_check():
    """CHECK mode: words only, no network, no derivation, no orders."""
    print("%s: %s" % (PRIVATE_KEY_NAME, presence(PRIVATE_KEY_NAME)))
    for name in OUTPUT_NAMES:
        print("%s: %s" % (name, presence(name)))
    print("SDK (modul polymarket): %s"
          % ("installed" if sdk_available() else "not installed"))

    address, status = local_address()
    if address:
        print("wallet address: %s" % address)
        match = "yes" if address.lower() == EXPECTED_ADDRESS.lower() else "no"
        print("address match: %s" % match)
    else:
        print("wallet address: not checked (%s)" % status)
        print("address match: unknown")

    if all(presence(name) == "present" for name in OUTPUT_NAMES):
        print("note: derived credential names are present in this "
              "machine's environment, but the live bot IGNORES stored "
              "values and re-derives from the private key each run")

    missing = []
    if presence(PRIVATE_KEY_NAME) != "present":
        missing.append("private key absent")
    if not sdk_available():
        missing.append("SDK not installed")
    if address is None:
        missing.append("address not verified")
    elif address.lower() != EXPECTED_ADDRESS.lower():
        missing.append("address mismatch")

    ready = not missing
    print("status: %s" % ("ready" if ready else "not-ready"))
    if missing:
        print("missing: %s" % ", ".join(missing))
    return 0 if ready else 1


def run_derive():
    """DERIVE mode: gated, SDK-only, values never printed or saved."""
    if os.environ.get("DERIVE_APPROVED") != "1":
        print("derive refused: --derive flag and DERIVE_APPROVED=1 "
              "are both required")
        return 2

    key = os.environ.get(PRIVATE_KEY_NAME)
    if not key:
        print("derive refused: %s is absent in this machine's environment"
              % PRIVATE_KEY_NAME)
        return 2

    try:
        from polymarket import SecureClient
    except Exception:
        print("polymarket is not installed on this machine.")
        print("install it first (pip install polymarket-client, or: "
              "pip install -r requirements.txt in this directory), "
              "then re-run this script.")
        return 3

    # Local address MUST verify before create() is called: for
    # non-EOA wallet types that are not yet deployed, create()
    # could deploy a deposit wallet on-chain, and that side effect
    # must never come from a verification step. The approved live
    # wallet is the signer's own wallet (EOA case), so a verified
    # match means create() performs no deployment.
    address, _status = local_address()
    if address is None or address.lower() != EXPECTED_ADDRESS.lower():
        print("derive refused: key does not match the expected bot "
              "wallet address (or the address could not be verified "
              "locally)")
        return 2

    # Real entry point of SDK 0.15.0: SecureClient.create derives
    # the credentials internally (L1 ClobAuth signature + the
    # create/derive endpoint) and validates them. If the installed
    # SDK version expects different arguments it raises, and the
    # failure below reports no values — check the installed SDK's
    # docs on the host instead of editing this to print values.
    try:
        client = SecureClient.create(private_key=key,
                                     wallet=EXPECTED_ADDRESS)
    except Exception:
        print("derive failed: the official SDK reported an error "
              "(details omitted, no values shown)")
        return 1

    try:
        creds = client.credentials
        # Presence by NAME only — values are inspected for truthiness
        # but never assigned to a printed variable, logged, or saved.
        produced = {
            "POLY_API_KEY": bool(getattr(creds, "key", None)),
            "POLY_SECRET": bool(getattr(creds, "secret", None)),
            "POLY_PASSPHRASE": bool(getattr(creds, "passphrase", None)),
        }
    finally:
        try:
            client.close()
        except Exception:
            pass
    if not all(produced.values()):
        print("derive incomplete: not all expected credential names "
              "were produced")
        return 1

    print("done")
    print("wallet address: %s" % address)
    for name in OUTPUT_NAMES:
        print("%s produced" % name)
    print("note: this script does not print or save any credential value.")
    print("owner: the live bot re-derives credentials at runtime from "
          "%s, so no stored copies are needed." % PRIVATE_KEY_NAME)
    return 0


def main(argv=None):
    # Refuse outright if asked to expose secrets. No such code path
    # exists; this guard only makes the refusal explicit and early.
    for guard in GUARD_NAMES:
        if os.environ.get(guard):
            print("refused: this script never prints or saves secret values")
            return 2

    parser = argparse.ArgumentParser(
        description="Polymarket credential helper (CHECK by default; "
                    "DERIVE only with --derive and DERIVE_APPROVED=1).")
    parser.add_argument(
        "--derive", action="store_true",
        help="derive CLOB credentials via the official SDK "
             "(also requires env DERIVE_APPROVED=1)")
    args = parser.parse_args(argv)

    if args.derive:
        return run_derive()
    return run_check()


if __name__ == "__main__":
    sys.exit(main())
