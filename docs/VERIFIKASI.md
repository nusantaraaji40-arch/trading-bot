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
- `dashboard/index.html` v3 (1 Nov 2026): 13 panel (tanpa JavaScript).
  Panel metrik diperbarui ke hasil terverifikasi terbaru: posisi paper
  Polymarket CLOSED via SL, P&L paper -Rp544, saldo paper efektif
  Rp49.456 (panel lama sempat menulis posisi 10 YES @ 0,009 USDC —
  sudah dikoreksi). Koreksi screening 1 Nov 2026: angka Rp47.099 yang
  sempat tertulis di sini dan di dashboard v3 salah hitung — kas yang
  benar setelah jual = 47.643,25 + hasil jual 1.812,86 = 49.456,11. Panel baru 13 memperkenalkan track Forex MT4/5
  (demo dulu; broker demo belum dipilih: OANDA demo via REST API atau
  MT5 via terminal + jembatan data). Parse HTML lolos, pindai secret
  bersih.
- `forex-mt5/mt5_paper.py` (1 Nov 2026): modul paper Forex MT5 — jalur
  MT5 dipilih pemilik. Data acuan harian gratis Frankfurter (ECB, tanpa
  key): EURUSD + USD/IDR untuk konversi rupiah; BUKAN tick real-time
  MT5, harga mid (spread/slippage belum dimodelkan). Run pertama:
  kurs ECB 2026-10-30 (EURUSD 1,11721, USD/IDR 18.148) → OPEN paper
  0,49 EUR senilai Rp10.000, sisa kas Rp40.000; SL 5% / TP 10%/15% /
  kill-switch 15% seperti venue lain; riwayat append-only
  `mt5_paper_history.jsonl`. `forex-mt5/MT5_BRIDGE.md` mendokumentasi
  jembatan terminal nanti (ekspor CSV → paket Python MetaTrader5 →
  HTTP lokal) dan syaratnya: terminal desktop yang tetap jalan
  (MT5 mobile tidak bisa dijembatani).
- `pumpfun-bot/pumpfun_paper.py` (1 Nov 2026): modul paper Pump.fun —
  data publik gratis DexScreener (tanpa key, tanpa koneksi chain; untuk
  demo, jaringan tidak menghalangi). Filter: hanya pair pumpfun/
  pumpswap dengan likuiditas >= $10.000 dan volume 24 jam >= $5.000;
  kalau tidak lolos, NO_TRADE. Run pertama: OPEN paper 11.987 INKKY
  (pumpswap) senilai Rp10.000 @ $0,000046, kas Rp40.000; SL 5% / TP
  10%/15% / kill-switch 15% seperti venue lain. Satu bug saat run
  pertama (pairs null dari DexScreener) sudah diperbaiki (`or []`) dan
  run ulang berhasil. `pumpfun-bot/PUMP_BRIDGE.md` mendokumentasi live
  nanti (Solana, wallet khusus bot terpisah dari simpanan utama, seed
  tidak pernah lewat chat, profit ke Bitget Wallet pemilik).
- Perbaikan celah full run 1 Nov 2026 (perintah pemilik: perbaiki
  langsung tanpa disuruh): `polymarket-bot/paper_trade.py` kini
  melewati beli baru selagi posisi OPEN/PARTIAL (beli baru dulu
  menimpa posisi lama karena exit manager init ulang dari ledger
  terbaru); posisi CLOSED tetap boleh beli baru.
  `indodax-bot/indodax_paper.py` kini punya riwayat append-only
  `indodax_history.jsonl` dan melewati beli ulang selagi posisi ada
  (laporan MTM saja) — dulu beli ulang menimpa ledger tanpa jejak.
- `indodax-bot/indodax_exit.py` (baru, 1 Nov 2026): exit manager
  Indodax — TP1 +10% jual separuh, TP2 +15% jual sisa, SL -5%,
  kill-switch 15%, prioritas kill-switch > SL > TP2 > TP1; trigger bid
  vs ask entry; ticker gagal = CANNOT_EXIT; CLOSED tidak dibangkitkan.
  Run pertama: init dari ledger lama, HOLD -0,150% (bid
  Rp1.405.017.000 vs ask entry Rp1.407.129.000).
- `forex-mt5/mt5_backtest.py` (baru, 1 Nov 2026): backtest EURUSD
  harian Frankfurter 469 hari (2024-12-31 s/d 2026-10-30) + grid 18
  kombinasi + walk-forward 70/30. Strategi tetap SL 5%/TP 10%/15%:
  latih 2 trade +Rp1.765, uji 2 trade +Rp6, keseluruhan 3 trade
  +Rp1.795, drawdown maks 1,0%. Peringatan overfitting aktif
  (parameter terbaik latih ≠ uji). Batas: tutup harian saja, harga
  mid, satu pair — sampel 3 trade = noise, BUKAN bukti profit; level
  5%/10%/15% terlalu lebar untuk data harian (trial bermakna butuh
  data intraday dari jembatan terminal).
- Perbaikan kas kumulatif Polymarket (full run 1 Nov 2026): total di
  paper_exit dulu = cash_after_buy + realized (SALAH — cost terhitung
  dua kali; sumber angka 47.099). Kini kas dilacak eksplisit
  (cash_idr = kas setelah beli + hasil jual) dan paper_trade trade
  baru mulai dari kas posisi CLOSED (bukan reset 50.000). State
  dikoreksi dengan jejak CORRECTION di riwayat: kas 49.456,11,
  setelah beli 48.005,86, total kini 49.275 (HOLD, terverifikasi).
- Perbaikan endpoint Pump.fun (full run 1 Nov 2026): pair_price dulu
  memakai /dex/tokens/ dengan alamat pair (salah) sehingga harga
  selalu SKIP. Kini /dex/pairs/solana/. Run ulang: SL -5% tersentuh
  (INKKY -9,55%) → SELL_ALL Rp9.045, P&L -Rp955, CLOSED, kas Rp49.045.
- Celah TERCATAT (belum diperbaiki): settlement posisi Polymarket
  saat market resolve — exit manager belum menangani resolve
  (YES=$1/$0); posisi yang dipegang melewati endDate bisa macet
  (CANNOT_EXIT saat book hilang) dan memblokir beli baru. Posisi
  Polymarket saat ini berakhir 11:00 WIB 1 Nov 2026; setelah resolve,
  hasilnya dicek dari sumber resmi dan posisinya diselesaikan dengan
  bukti — perbaikan berikutnya, sebelum langkah live apa pun.
- Modul paper Moomoo (1 Nov 2026): data Yahoo Finance harian AAPL
  (Stooq diblokir dari VM — halaman JS-check — diperbaiki langsung
  ke Yahoo); run pertama tutup 2026-10-30 $344,63 → OPEN 0,0016 AAPL
  Rp10.000, kas Rp40.000; SL/TP/KS sama. Jembatan live: gateway OpenD
  + akun (domisili dicek), payout SeaBank SWIFT saja, wire SGD 30.
- Sweep backtest multi-venue (1 Nov 2026): 44.506 percobaan (Forex
  26.950, saham 17.248, kripto-proxy 308) — Forex 92 param lolos
  kriteria (cluster SL 2%/TP1 12-15%, DD 4,4%); saham 0 lolos (DD
  19,5%); kripto-proxy 0 lolos (4 trade, noise; CoinGecko gratis
  dibatasi 365 hari). Polymarket/Pump.fun tidak bisa backtest (tidak
  ada deret historis gratis).
- Validasi split-half Forex (1 Nov 2026): 92/92 param seleksi tetap
  lolos di paruh validasi (100%) — sinyal lebih kuat dari sekadar
  lolos sweep, TAPI bias data harian tetap: SL 2% intraday tidak
  tertangkap (live bisa lebih buruk), spread/fee/swap belum
  dimodelkan, P&L jumlah jendela (rata-rata ~Rp157/jendela validasi).
  Belum "berhasil mutlak": butuh data intraday + biaya.
- Bot trading demo `bot-engine/demo_bot.py` (1 Nov 2026): orkestrator
  satu siklus paper 5 venue (subprocess per modul, guard
  anti-duplikat, ringkasan kas + terealisasi KUMULATIF dari riwayat
  — bukan hanya posisi berjalan, supaya rugi lama tidak hilang dari
  tabel). Siklus 1–2 terverifikasi: Indodax HOLD +0,024% (MTM +Rp2),
  Polymarket CANNOT_EXIT (book kosong pra-resolusi), MT5/Moomoo HOLD
  0%, Pump.fun 2 trade 2 SL (INKKY -955, BLUE -883, kumulatif
  -1.838).
- Status Polymarket pra-resolusi (1 Nov 2026 ~10:00 WIB): book CLOB
  token YES kosong → CANNOT_EXIT (posisi dipertahankan, tanpa harga
  tebakan). Market belum closed resmi (endDate 11:00 WIB), tapi harga
  sampel BTC Oktober 2026 min $76.360 (tidak ada sampel di bawahnya)
  dan pasar menghargai YES 0,05% — hasil faktual sangat condong NO
  (YES = $0 saat resolusi resmi). Posisi TIDAK diselesaikan prematur;
  diselesaikan setelah resolusi resmi dengan bukti.
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

- Perubahan modal 1 Nov 2026 ~10:18 WIB (keputusan user, demo + live): modal per venue Rp50.000 -> Rp25.000 (total 5 venue Rp250.000 -> Rp125.000), trade pertama Rp10.000 -> Rp5.000, kill-switch 15% per venue = Rp3.750 (lantai Rp21.250). Diterapkan ke semua modul paper, mesin edge/unified, backtest/sweep, paket live Indodax (params.example.json + gerbang validasi live_run.py), dan label dashboard. Migrasi: posisi paper yang sedang berjalan diselesaikan dengan ukuran lama (Indodax beli Rp10.000, MT5/Moomoo Rp10.000, Polymarket kas Rp48.006); siklus baru pakai modal Rp25.000, dan kas awal Polymarket dibatasi ke Rp25.000 (kelebihan dicatat sebagai penarikan paper, bukan dihapus diam-diam). Siklus demo 10:22 WIB memverifikasi rezim baru: Pump.fun beli pertama Rp5.000 (575,78 BLUE @ $0,0004785). Angka backtest/sweep rezim baru: MT5 469 hari +Rp898 (3 trade, tetap noise); sweep 44.506 percobaan, Forex tetap 92 param lolos (terbaik lolos SL 2%/TP1 12%/TP2 15%, P&L uji Rp10.043, 334 trade, DD 4,4%); validasi split-half tetap 92/92 lolos (validasi terbaik Rp7.142, 159 trade, DD 4,4%). Angka lama rezim Rp50.000 tetap tercatat di riwayat di atas. Catatan kelayakan: Rp25.000 ~ $1,38 — biaya beli USDC + bridge Polymarket dan wire Moomoo (SGD 30) makin dominan terhadap modal; cek min order Indodax dan akun cent/micro Forex makin kritis sebelum live. Live tetap terkunci.
- Resolution handler 1 Nov 2026 ~10:35 WIB (celah terakhir yang tercatat): paper_exit.py kini mengecek resolusi Gamma SEBELUM book — settle HANYA bila closed=True DAN outcomePrices decisif (>= 0,999 satu sisi), YES = $1/lembar, NO = $0/lembar, kurs CoinGecko live; gagal cek resolusi tidak memblokir cek exit biasa; posisi CLOSED tidak pernah di-settle ulang. Tes baru polymarket-bot/test_resolve.py (13 lolos) + test_exit 13 lolos + test_risk_edge lolos. Terhubung otomatis ke demo_bot (langkah Polymarket menjalankan paper_exit.py).
- Siklus demo 4 (10:35 WIB): resolver "Belum resolusi resmi" (benar — market berakhir 11:00 WIB) lalu book kembali (bid 0,003/ask 0,004) -> SL jual 10 @ bid 0,003 = Rp544, P&L -Rp906, CLOSED; kumulatif Polymarket -Rp1.450 (trade 1 -Rp544 + trade 2 -Rp906).
- Siklus demo 5 (10:37 WIB): cap modal terverifikasi langsung — kas 48.550 dibatasi ke 25.000 (kelebihan 23.550 dicatat penarikan paper) -> beli baru 10 YES @ 0,004 = Rp725, kas 24.275 -> resolver belum resolusi -> HOLD (SL 0,0038/TP1 0,0044, total 24.819 > kill-switch 21.250). Pump.fun BLUE HOLD -4,74% (nilai Rp4.763, SL -5% belum kena). Indodax/MT5/Moomoo HOLD. Unified engine + edge engine jalan tanpa error (unified live False; edge NO_TRADE beruntun 3, saldo virtual Rp25.000).
- Cron settlement 11:30 WIB diperbarui (jadwal tetap): posisi lama sudah CLOSED via SL — jangan settle ulang; settle hanya posisi OPEN bila market resolusi resmi; bila tidak ada posisi terbuka, lapor sekali lalu berhenti; follow-up 14:30 hanya bila posisi terbuka tapi belum resolusi.
- TP demo Indodax diubah 1 Nov 2026 ~10:47 WIB (keputusan user, Indodax SAJA): TP +3% jual habis (sebelumnya TP bertangga +10% jual separuh / +15% jual sisa); SL -5% dan kill-switch 15% tidak berubah. Venue lain tetap TP 10%/15%. Tes baru tests/test_indodax_exit.py (7 lolos: HOLD +0,26%, HOLD +2,9%, TP tepat +3% jual habis, TP +5% jual habis, SL -5%, kill-switch mengalahkan SL, kill-switch tepat di lantai). Posisi berjalan dicek live setelah perubahan: HOLD +0,24% (nilai Rp10.024 @ bid Rp1.410.502.000, belum 3% — tidak terjual prematur). Paket live Indodax TIDAK diubah (params.example.json tetap TP 10/15) — menunggu persetujuan parameter live tersendiri. Sweep Forex tidak terpengaruh (venue tidak berubah; Indodax tidak punya backtest — demonya adalah paper live).
- Paket live Indodax diubah 1 Nov 2026 ~11:00 WIB (keputusan user, live SAJA — demo tetap Rp25.000 per venue): modal live Rp30.000 ALL-IN untuk 1 koin (dulu Rp25.000 / beli pertama Rp5.000); gerbang validasi live_run.py + params.example.json + README ikut diubah (modal 30000, first_trade 30000, kill-switch 15% = Rp4.500, lantai Rp25.500). Sisa dana user adalah DANA DARURAT — tidak masuk modal trading dan tidak disentuh bot (key trade-only juga tidak bisa withdraw). Pair dan TP live MASIH menunggu konfirmasi eksplisit (proposal: BTC/IDR, TP 3% jual habis seperti demo). Belum ada deposit, belum ada order live.
