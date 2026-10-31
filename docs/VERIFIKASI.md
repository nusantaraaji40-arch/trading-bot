# Verifikasi (2026-11-01)

Bukti pemeriksaan untuk isi repo ini. Yang diklaim di sini hanya hasil
pemeriksaan di bawah — bukan janji "nol bug selamanya".

## Yang diperiksa dan hasilnya

- Compile Python: semua file `.py` lolos `py_compile` tanpa error.
- Secret scan: tidak ditemukan API key, token, password, seed phrase,
  maupun alamat wallet di file mana pun yang di-push.
- `bot-engine/unified_engine.py`: run terakhir exit 0, 6/6 modul data ok,
  keputusan NO_TRADE karena filter bekerja (skor berita -3 memblokir).
- `indodax-bot/indodax_paper.py`: demo jalan di data publik live, saldo
  virtual Rp50.000 (beli 0,00000711 BTC Rp10.000 di ask, sisa Rp40.000).
- `polymarket-bot/paper_trade.py`: demo jalan di data Gamma + CLOB live,
  saldo virtual Rp50.000. Run 1 Nov 2026 ~05:07 WIB: beli 10 YES @ 0,013
  USDC (market "Will Bitcoin dip to $75,000 in October?"), biaya
  Rp2.357 pada kurs CoinGecko Rp18.129/USDC, sisa Rp47.643.
  Iterasi 1 Nov 2026 ~05:36 WIB: setiap trade kini ditambah ke riwayat
  append-only `paper_history.jsonl` (ledger utama tetap berisi trade
  terbaru); run terbaru mencatat trade yang sama (10 YES @ 0,013 USDC,
  Rp2.357, sisa Rp47.643) sebagai entri riwayat pertama.
- `polymarket-bot/paper_exit.py`: exit manager paper (TP bertangga:
  TP1 +10% jual separuh, TP2 +15% jual seluruh sisa; SL -5% dan
  kill-switch 15% jual seluruh sisa; prioritas kill-switch > SL >
  TP2 > TP1; trigger ask-ke-ask agar spread ~7,7% tidak memicu SL
  palsu, hasil jual dihitung di bid; book kosong = CANNOT_EXIT tanpa
  harga tebakan; posisi CLOSED tidak dibangkitkan ledger lama; trade
  baru menginisialisasi posisi baru otomatis). Run 1 Nov 2026 ~05:44
  WIB di book live: bid 0,010 / ask 0,011 menyentuh SL 0,0123 →
  SELL_ALL 10 lembar @ bid 0,010 = Rp1.813, P&L paper -Rp544, status
  CLOSED; run ulang memastikan posisi tetap CLOSED. Tes
  `tests/test_exit.py`: 13 tes lolos (10 decide_exit + 3 load_position);
  `tests/test_risk_edge.py` tetap lolos (regresi).
- `polymarket-bot/btc_edge_engine.py`: run 1 Nov 2026 ~05:07 WIB memindai
  2 market BTC, edge -0,001 keduanya → NO TRADE, saldo tetap Rp50.000.
  Iterasi 1 Nov 2026 ~05:36 WIB: setiap pindaian dicatat ke riwayat
  append-only `btc_edge_history.jsonl`; run terbaru: 2 market, edge
  terbaik -0,001, NO_TRADE beruntun 1, saldo Rp50.000.
- `bot-engine/ccxt_adapter.py`: Indodax dan Gate teruji live pada data
  publik. Tokocrypto diblokir 451 dari egress VM. Binance dihapus dari
  rencana atas permintaan pemilik.
- `tests/test_risk_edge.py`: tes fungsi murni (edge, kill-switch, SL/TP)
  lolos semua — jalankan dengan `python3 tests/test_risk_edge.py`.
- Repo target dikonfirmasi kosong sebelum push (0 commit, tanpa branch),
  sehingga snapshot ini adalah commit awal.

## Batasan v1 yang diketahui (jujur, bukan cacat tersembunyi)

- Sentimen berita masih kata kunci kasar (v1), bukan model bahasa.
- Pulsa sosial dari Stocktwits trending, bukan X API.
- Fill paper memakai harga ask; slippage dan fee live belum dimodelkan
  penuh.
- Dashboard `dashboard/index.html` memakai simulasi internal yang
  berlabel demo — BUKAN harga live. Script workspace memakai data live.
- Backtest ribuan percobaan belum ada di repo ini (rencana lanjutan).

## Yang tidak ikut push

- `__pycache__` dan file state JSON (ledger/state) tidak ikut — hanya
  kode, dokumen, dan dashboard yang di-push.
- File sync `.muse-github-snapshot-sync.json` tidak ikut (metadata
  lokal, bisa membocorkan path dan SHA).
