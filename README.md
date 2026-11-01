# trading-bot

Bot trading demo multi-venue: Indodax, Polymarket, Forex MT4/5, Moomoo, dan
Pump.fun. Dibangun sebagai mesin paper trading (demo) — **nol order nyata**,
nol uang asli — sampai strategi terbukti, baru dipertimbangkan live modal
kecil setelah parameter disetujui pemiliknya.

## Status

- Mode: DEMO / PAPER TRADING. Semua eksekusi default-nya paper.
- Live terkunci ganda: environment `LIVE_TRADING=1` DAN file
  `LIVE_APPROVED.txt` harus ada bersamaan. Keduanya tidak ada di repo ini,
  jadi kode di sini tidak bisa mengeksekusi order nyata apa adanya.
- Bukan saran keuangan. Tidak ada jaminan profit. Bot apa pun bisa rugi,
  terutama di pasar volatil dan sideways.

## Urutan venue

1. Indodax (spot; demo dulu, lalu live Rp25.000)
2. Polymarket (demo di harga live; live kecil setelah Indodax)
3. Forex MT4/5 (akun demo dulu, lalu live micro/cent)
4. Moomoo (saham AS/global via OpenAPI; paper trading dulu)
5. Pump.fun (wallet khusus bot, dana kecil, terpisah dari simpanan utama)

## Modal dan risiko

- Modal per venue: Rp25.000. Total 5 venue: Rp125.000.
- Kill-switch 15% per venue (= Rp3.750): hentikan venue saat rugi mencapai
  batas itu.
- Filter bawaan engine: stop loss 5%, take profit 10-15%, hanya beli saat
  tren 24 jam naik, dan blokir trading saat skor berita negatif.
- Catatan kelayakan: cek minimum order per pair Indodax sebelum live;
  biaya beli USDC + bridge Polymarket bisa menggerus modal $3; Forex butuh
  akun cent/micro bermodal minimum rendah; penarikan Moomoo lewat wire
  (sekitar SGD 30) jauh lebih besar dari modal — jangan tarik sebelum profit
  jauh lebih besar; Pump.fun di ukuran ~0,03 SOL rawan slippage dan fee.

## Aturan biaya: semua alat gratis

Repo ini hanya memakai alat gratis, tanpa langganan berbayar: engine
sendiri + CCXT + API publik (CoinGecko free, DexScreener, RSS berita,
Stocktwits). Yang berbayar (Kavout, 3Commas paket penuh, Perplexity Pro,
Danelfin, Trade Ideas, TrendSpider, Tickeron) dicoret dari rencana.
Gratis = alatnya; modal live tetap uang pemilik.

## Yang tidak dipakai

- Binance: tidak dipakai atas permintaan pemilik, dan dihapus dari semua
  rencana. Komentar di `bot-engine/ccxt_adapter.py` mendokumentasikan
  keputusan ini.
- Manus, Antigravity, GenSpark: produk builder terpisah, bukan integrasi
  yang bisa disambungkan langsung sebagai model/API.

## Cara jalan

Python 3.10+.

```text
pip install -r requirements.txt
python3 bot-engine/unified_engine.py
```

- `unified_engine.py`: 9 modul — Indodax (major + basket sub-Rp500),
  Polymarket (hanya market aktif), kapitalisasi pasar CoinGecko,
  DexScreener, agen berita (RSS + sentimen kata kunci v1), pulsa sosial
  (Stocktwits trending), filter tren, risiko, dan lapisan eksekusi.
- `bot-engine/ccxt_adapter.py`: adapter CCXT (Indodax + Gate teruji live
  pada data publik). Catatan: di VM dengan egress proxy, CCXT butuh
  `session.trust_env=True`.
- `polymarket-bot/paper_trade.py` dan `btc_edge_engine.py`: paper trading
  Polymarket di data Gamma + CLOB live, dan mesin edge
  (edge = 1 - (YES ask + NO ask), ambang 0,01).
- `polymarket-bot/paper_exit.py`: exit manager paper — TP bertangga
  (+10% jual separuh, +15% jual sisa), SL -5%, kill-switch 15%,
  di harga CLOB live; tanpa order nyata.
- `indodax-bot/indodax_paper.py`: paper trading Indodax di data publik
  live dengan saldo virtual Rp25.000.
- `indodax-live/`: paket persiapan live-run Indodax (`live_run.py` mode
  check tanpa order + mode `--live` terkunci 4 gerbang, `params.example.json`,
  `README_LIVE_RUN.md`). Tanpa key di dalam file; key dibaca dari environment
  mesin pemegang key.
- `dashboard/`: snapshot dashboard statis (gaya panel terminal: model
  Bayesian, Edge + Spread, eksekusi Stoikov, metrik bot, kurva P&L).
  Buka `dashboard/index.html` di browser, atau deploy sebagai Hugging
  Face Space dengan SDK static.

## Keamanan

- Repo ini TIDAK berisi API key, token, password, seed phrase, atau
  alamat wallet apa pun. Key live (bila ada nanti) hanya lewat environment
  dan tidak pernah ditempel di chat atau di kode.
- Key exchange untuk live harus trade-only (tanpa withdrawal).
  Penarikan awal selalu manual dan disetujui pemilik, bukan otomatis.

## Pelengkap open source

Repo-repo open source lain yang melengkapi proyek ini (bukan disalin ke
sini) didokumentasikan lengkap di [COMPLEMENTS.md](COMPLEMENTS.md):
Freqtrade, Hummingbot, Jesse, TradingAgents, OctoBot, dan CCXT — beserta
fungsi masing-masing dan cara memakainya bersama engine ini.

## Dokumentasi

- [docs/ARSITEKTUR.md](docs/ARSITEKTUR.md): alur data, tabel modul, aturan
  keputusan, dan cara menambah venue.
- [docs/VENUE.md](docs/VENUE.md): detail 5 venue — status demo, modal,
  routing payout, dan catatan kelayakan per venue.
- [docs/VERIFIKASI.md](docs/VERIFIKASI.md): bukti pemeriksaan 2026-11-01
  (compile, secret scan, demo run) dan batasan v1 yang diketahui.
- [tests/test_risk_edge.py](tests/test_risk_edge.py): tes fungsi murni
  (edge, kill-switch, SL/TP) — jalankan dengan
  `python3 tests/test_risk_edge.py`.

## Lisensi

MIT. Lihat [LICENSE](LICENSE).
