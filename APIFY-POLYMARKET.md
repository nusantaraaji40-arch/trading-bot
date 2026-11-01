# APIFY UNTUK POLYMARKET — Panduan Keputusan Agen

Dokumen ini adalah katalog hasil screening Apify Store (1 Nov 2026, via API resmi
Apify) untuk kebutuhan trading Polymarket. Tujuannya satu: **membantu agen AI
memilih Actor yang tepat sebelum mengambil data, bukan menjamin profit.**

> ATURAN KERAS — TIDAK ADA KREDENSIAL DI REPO INI.
> API key Apify, key/secret CLOB Polymarket, seed phrase, dan password apa pun
> TIDAK PERNAH ditulis di repo ini, publik maupun privat. Kredensial hanya ada
> di Secure Vault / environment mesin yang menjalankan bot. Repo privat bukan
> brankas: privat tidak membuat key yang bocor menjadi aman.

## Gerbang biaya (berlaku untuk semua Actor)

1. Screening (cari di Store, baca detail Actor) = gratis.
2. Menjalankan Actor = BERBAYAR (per run / per hasil / per baris, tergantung
   Actor). Sebelum run berbayar pertama: cek harga di halaman Actor, sampaikan
   estimasi, tunggu persetujuan eksplisit user, dan pasang batas biaya
   (`maxTotalChargeUsd` sebagai parameter query untuk REST, bukan di input).
3. Jangan pernah menjalankan "semua Actor" sekaligus tanpa pilihan + batas.
4. Jangan menaruh batas biaya di dalam input Actor — itu field Actor, bukan
   batas tagihan.
5. Hasil run diambil lewat dataset ID yang dikembalikan, bukan dari respons
   pemanggilan Actor.

## Katalog terverifikasi (angka dari API Apify, 1 Nov 2026)

### 1. scrapemint/polymarket-market-monitor — PAKAI (pelacak kategori)
- Judul: Polymarket Prediction Market Tracker by Category.
- Fungsi: tarik market Polymarket per kategori/keyword/min volume/likuiditas/
  price move; JSON deduped dari Gamma API resmi.
- Statistik: 4.598 total run, 244 user.
- Cocok untuk: screening harian per kategori (kripto, cuaca, bola, politik).
- Catatan: dataset yang pernah dibaca berisi dominan politik — filter kategori
  wajib dipakai, jangan ambil mentah-mentah.

### 2. scrapemint/polymarket-scraper — PERTIMBANGKAN (order book + harga)
- Judul: Polymarket Trade Intelligence: Order Book and Prices.
- Fungsi: tarik banyak market per kategori/keyword/tag/slug/condition ID; satu
  baris per market (outcome, harga YES/NO, volume 24 jam, likuiditas, tanggal
  berakhir) + opsional order book, trade terakhir, histori harga.
- Statistik: 634 total run, 97 user, rating 5 (1 ulasan).
- Harga: pay per row (cek tarif halaman Actor sebelum run).
- Cocok untuk: data harga/book untuk mesin edge + spread.

### 3. logiover/polymarket-events-odds-ai-scraper — PERTIMBANGKAN (odds + AI)
- Judul: Polymarket Scraper - Prediction Market Odds API.
- Fungsi: event, odds, skor olahraga, analisis AI, dan sinyal tweet; ekspor
  CSV/JSON.
- Statistik: 349 total run, 72 user; 30 hari terakhir 37 run, 0 gagal.
- Cocok untuk: odds + sinyal sentimen pendamping. Analisis AI-nya adalah
  keluaran Actor pihak ketiga — perlakukan sebagai sinyal, bukan kebenaran.

### 4. scrapebench/kalshi-polymarket-prediction-market-scraper — PERTIMBANGKAN
- Judul: Kalshi & Polymarket Prediction Market Odds Scraper.
- Fungsi: odds, volume, likuiditas, dan settlement Kalshi + Polymarket dalam
  satu skema; market cuaca dipecah sampai kota, stasiun, dan bracket suhu.
- Statistik: 277 total run, 17 user; 30 hari terakhir 143 run, 3 gagal.
- Cocok untuk: perbandingan odds lintas platform dan data cuaca terstruktur.
- Perhatian: data Kalshi ≠ bisa trading di Kalshi (Kalshi exchange US).

### 5. congism/polymarket-kalshi-arb-finder — PERTIMBANGKAN DENGAN CATATAN
- Judul: Polymarket + Kalshi Arbitrage Finder.
- Fungsi: pindai market biner yang cocok di Polymarket + Kalshi (+ PredictIt)
  dan beri peringkat selisih harga.
- Statistik: 1.734 total run, 850 user.
- PERINGATAN: klaim "risk-free profit" adalah marketing Actor, BUKAN jaminan.
  Arb lintas platform bisa gagal karena fee, spread, likuiditas, sumber
  resolusi berbeda, dan akses Kalshi. Jangan pernah isi email/password Kalshi
  ke input Actor pihak ketiga.

### 6. parsebird/polymarket-scraper — BUKAN untuk odds
- Judul: Polymarket Leaderboard Scraper.
- Fungsi: peringkat leaderboard + profil trader (wallet, username, P&L,
  volume, posisi, trade terakhir).
- Statistik: 924 total run, 154 user.
- Cocok untuk: riset trader (whale watching) saja. Jangan dipakai sebagai
  sumber harga market.

### Berita (pendamping keputusan)
- easyapi/google-news-scraper — headline Google News per keyword/negara/
  bahasa; 384.600 total run, 2.769 user, rating 4,26.
- Alternatif: lhotanova/google-news-scraper, data_xplorer/google-news-scraper-fast
  (pay per event), xtracto/nytimes-scraper, architjn/yahoo-finance
  (info saham + berita).
- Cocok untuk: konteks berita di balik pergerakan odds. Berita ≠ sinyal beli.

## Aturan keputusan agen (ringkas)

1. Butuh daftar market per kategori → Actor 1 (filter kategori wajib).
2. Butuh harga/book/histori → Actor 2.
3. Butuh odds + sentimen → Actor 3 sebagai pendamping, bukan satu-satunya dasar.
4. Butuh banding Kalshi atau cuaca terstruktur → Actor 4.
5. Butuh kandidat arb → Actor 5, dengan peringatan di atas; eksekusi arb
   TIDAK OTOMATIS dan butuh persetujuan parameter terpisah.
6. Butuh riset trader → Actor 6.
7. Butuh konteks berita → Actor berita, keyword spesifik.
8. Tidak ada satu pun Actor di atas yang mengeksekusi order Polymarket.
   Eksekusi tetap lewat CLOB resmi dengan kredensial turunan wallet user
   (lihat MODEL-DAN-API-POLYMARKET.md) dan hanya setelah demo + persetujuan
   parameter eksplisit.

## Status

- Paper Polymarket yang berjalan di repo ini memakai Gamma + CLOB publik
  (tanpa Actor berbayar) dan sejauh ini belum profit — lihat paper_ledger dan
  paper_categories_history. Dokumen ini adalah persiapan, bukan bukti berhasil
  dan bukan persetujuan live.
- Akun Apify user yang terverifikasi sampai dokumen ini ditulis: 4 akun
  berbeda (satu konektor = satu key dalam satu waktu; ganti key = ganti akun).
  Nama akun tidak ditulis di sini karena akun bisa berganti sewaktu-waktu;
  yang berlaku adalah akun yang terverifikasi lewat `users/me` saat run.
