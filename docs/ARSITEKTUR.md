# Arsitektur engine

Repo ini adalah mesin paper trading (demo) multi-venue. Prinsipnya: demo
dulu, eksekusi paper sebagai default, dan live terkunci ganda sehingga kode
di sini tidak bisa mengeksekusi order nyata apa adanya.

## Alur data

```text
Indodax API publik / CCXT ─┐
Polymarket Gamma + CLOB ────┤
CoinGecko (free) ────────────┤
DexScreener ─────────────────┼─> modul ─> filter ─> risiko ─> eksekusi paper ─> dashboard
RSS berita ──────────────────┤
Stocktwits trending ─────────┘
```

## Tabel modul

| File | Peran | Sumber data | Status |
| --- | --- | --- | --- |
| `bot-engine/unified_engine.py` | 9 modul: Indodax, Polymarket, CoinGecko, DexScreener, berita, sosial, filter tren, risiko, eksekusi | API publik + CCXT | Run terakhir exit 0, 6/6 modul data ok |
| `bot-engine/ccxt_adapter.py` | Adapter CCXT (Indodax + Gate) | CCXT, data publik | Teruji live pada data publik |
| `polymarket-bot/paper_trade.py` | Paper trading Polymarket | Gamma + CLOB live | Demo jalan, saldo virtual Rp50.000 |
| `polymarket-bot/btc_edge_engine.py` | Mesin edge BTC | CLOB live | Edge = 1 - (YES ask + NO ask), ambang 0,01 |
| `indodax-bot/indodax_paper.py` | Paper trading Indodax | API publik live | Demo jalan, saldo virtual Rp50.000 |
| `dashboard/index.html` | Snapshot dashboard statis | Simulasi internal (berlabel demo, bukan harga live) | Statis, buka di browser |

Catatan: `session.trust_env=True` wajib untuk CCXT di VM dengan egress
proxy, kalau tidak koneksi gagal (SSL WRONG_VERSION_NUMBER).

## Aturan keputusan

Beli hanya jika SEMUA filter lolos:

1. Tren 24 jam naik.
2. Skor berita tidak negatif.
3. Edge memenuhi ambang (Polymarket: >= 0,01).
4. Risiko: stop loss 5%, take profit 10-15%, kill-switch 15% per venue.

Jika satu filter gagal, keputusan = NO_TRADE. Contoh run terakhir yang
terverifikasi: skor berita -3 sehingga mesin memutuskan NO_TRADE — filter
bekerja sesuai desain, bukan error.

## Lapisan eksekusi

- Default: paper. Fill paper memakai harga ask.
- Live terkunci ganda: environment `LIVE_TRADING=1` DAN file
  `LIVE_APPROVED.txt` harus ada bersamaan. Keduanya tidak ada di repo ini.
- Key live (bila ada nanti) hanya lewat environment, trade-only, tanpa
  withdrawal. Penarikan awal selalu manual dan disetujui pemilik.

## Yang belum ada di repo ini

- Modul khusus Forex, Moomoo, dan Pump.fun (baru tercakup lewat engine
  gabungan dan rencana venue di `docs/VENUE.md`); modul khusus menyusul
  setelah demo venue 1-2 stabil.
- Backtest ribuan percobaan (rencana lanjutan, bukan klaim yang sudah
  jalan).
- Order live apa pun, penandatanganan wallet, dan kunci apa pun.

## Cara menambah venue

Tambah modul sumber data baru, daftarkan ke filter dan lapisan risiko,
tanpa mengubah lapisan eksekusi. Uji modul baru dengan data publik dulu
sebelum menggabungkannya ke keputusan beli.
