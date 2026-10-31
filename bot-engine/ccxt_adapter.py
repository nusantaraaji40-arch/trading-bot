"""CCXT adapter + stub integrasi platform AI (mode PAPER / read-only).

PENTING — temuan teknis VM ini:
  CCXT default trust_env=False sehingga SESI-NYA MELEWATI proxy egress VM
  dan koneksi TLS langsung gagal (WRONG_VERSION_NUMBER). Solusi: set
  trust_env=True pada session exchange agar lewat proxy egress yang sah.
  Tanpa ini, semua exchange gagal meski URL-nya bisa dibuka langsung.

Status per platform (terverifikasi 2026-11-01):
  - CCXT: TERPASANG, teruji live (indodax + gate OK; tokocrypto 451 dari
    egress VM ini, sama seperti binance dulu).
    Binance DIHAPUS dari rencana atas permintaan user (user tidak pakai
    Binance).
  - Kavout Signal DB API: ADA (feed sinyal K Score, saham AS, harian,
    berbayar $39/bln per sinyal). Stub di bawah: butuh KAVOUT_API_KEY.
  - 3Commas API: ADA (kelola DCA/Grid/Signal bot). Stub di bawah: butuh
    akun 3Commas + plan + 3COMMAS_API_KEY, dan API key exchange trade-only.
  - Tickeron: TIDAK ADA API publik -> platform eksternal saja.
  - Composer.trade: TIDAK MENDUKUNG non-US residents + dukungan kripto
    berakhir 31 Jan 2026 -> tidak bisa dipakai user Indonesia.
  - Capitalise.ai / Trade Ideas (Holly) / TrendSpider (Sidekick):
    platform terpisah (langganan + broker mitra), bukan modul kode yang
    ditanam. Sinyalnya dipakai lewat jalur resmi mereka (dashboard /
    webhook ke TradersPost / broker), bukan lewat engine ini.
"""
import json
import os

import ccxt

STATE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                          "ccxt_state.json")


def make_exchange(ex_id):
    ex = getattr(ccxt, ex_id)()
    ex.session.trust_env = True  # WAJIB di VM ini (lihat docstring)
    return ex


def fetch_public_tickers():
    out = {}
    for ex_id, sym in [("indodax", "BTC/IDR"), ("gate", "BTC/USDT"),
                       ("tokocrypto", "BTC/USDT")]:
        try:
            t = make_exchange(ex_id).fetch_ticker(sym)
            out[ex_id] = {"status": "ok", "symbol": sym, "last": t["last"],
                          "bid": t["bid"], "ask": t["ask"]}
        except Exception as e:  # noqa: BLE001 - laporkan, jangan crash
            out[ex_id] = {"status": "failed", "symbol": sym,
                          "error": f"{type(e).__name__}: {str(e)[:150]}"}
    return out


def kavout_stub():
    """Kavout Signal DB: GET /api?product_id=kscore_us&symbol=...&api_key=...
    Tanpa key -> status needs_key, TIDAK ADA DATA PALSU."""
    key = os.environ.get("KAVOUT_API_KEY")
    if not key:
        return {"status": "needs_key",
                "note": "Butuh KAVOUT_API_KEY (Signal DB, $39/bln per sinyal, "
                        "saham AS, refresh harian). Tanpa key, modul nonaktif."}
    return {"status": "configured",
            "note": "Key tersedia — pemanggilan live menunggu persetujuan user."}


def three_commas_stub():
    """3Commas API: api.3commas.io/ver1/bots, deals, smart_trades (HMAC).
    Tanpa key -> status needs_key."""
    key = os.environ.get("3COMMAS_API_KEY")
    if not key:
        return {"status": "needs_key",
                "note": "Butuh akun 3Commas + plan + 3COMMAS_API_KEY, dan API key "
                        "exchange trade-only (withdrawal NONAKTIF, IP whitelist)."}
    return {"status": "configured",
            "note": "Key tersedia — pembuatan bot live menunggu persetujuan user."}


def main():
    state = {"tickers_ccxt": fetch_public_tickers(),
             "kavout": kavout_stub(),
             "three_commas": three_commas_stub()}
    with open(STATE_PATH, "w") as f:
        json.dump(state, f, indent=2)
    print(json.dumps(state, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
