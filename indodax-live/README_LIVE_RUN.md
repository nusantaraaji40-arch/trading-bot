# Paket live-run Indodax (persiapan)

Paket ini menyiapkan eksekusi live Indodax **tanpa mengeksekusi apa pun
sekarang**. Tidak ada API key, secret, atau order di dalam file-file ini.
Live tetap terkunci sampai parameter disetujui pemilik.

## Kenapa paket ini dijalankan dari mesin pemegang key

API Indodax tidak bisa disambungkan langsung ke Muse: tiap request harus
ditandatangani signature turunan dari secret key, dan signature itu
tidak bisa direproduksi Muse. Jadi live-run dijalankan dari mesin yang
memegang key (PC/VPS pemilik), dengan key dibaca dari environment.

## Isi paket

- `live_run.py` — runner: mode `check` (baca saja) dan mode `--live`
  (satu order beli pertama, terkunci 4 gerbang).
- `params.example.json` — contoh parameter. Salin menjadi `params.json`
  HANYA setelah parameter disetujui.
- File yang TIDAK ADA di repo (dan tidak boleh di-commit):
  `params.json`, `LIVE_APPROVED.txt`, dan file `.env` apa pun — ketiganya
  dilindungi `.gitignore`.

## Prasyarat

- Python 3.11+, `pip install ccxt==4.5.91` (sama dengan
  `requirements.txt` repo).
- Trade API key Indodax dengan permission **View + Trade, TANPA
  withdrawal** (dibuat di website Indodax, Menu → Trade API, V2).
- Key disimpan di environment mesin, bukan di file:
  `export INDODAX_API_KEY=...` dan `export INDODAX_SECRET=...`.
  Jangan kirim key/secret lewat chat, jangan commit ke repo.

## Mode check (aman, tanpa order)

```bash
python3 live_run.py
```

Yang dilakukan: baca saldo privat (membuktikan key jalan), baca harga
BTC/IDR, baca limit min order, dan menilai apakah rencana (modal
Rp25.000, beli pertama Rp5.000, kill-switch 15% = Rp3.750) memenuhi
batas exchange. Nol order dibuat.

## Mode live (terkunci 4 gerbang)

Semua wajib lolos, kalau tidak skrip berhenti tanpa order:

1. Flag `--live`.
2. Environment `LIVE_TRADING=1`.
3. File `LIVE_APPROVED.txt` di folder ini, berisi persetujuan pemilik
   (tanggal + pair + nominal yang disetujui).
4. File `params.json` (dari contoh) yang lolos validasi: pair BTC/IDR
   atau ETH/IDR, modal Rp25.000, beli pertama <= modal, SL 1–20%,
   TP bawah >= SL, TP atas >= TP bawah, kill-switch 5–30%.

```bash
LIVE_TRADING=1 python3 live_run.py --live
```

Yang dilakukan: SATU limit buy pertama sebesar `first_trade_idr` di
harga ask, lalu mencetak id order, level SL/TP, dan level kill-switch.
Pemantauan dan penjualan berikutnya adalah langkah terpisah.

## Keamanan

- Skrip ini **tidak mengandung pemanggilan withdraw** dalam bentuk apa
  pun, dan key yang dipakai harus trade-only.
- Nilai key/secret **tidak pernah dicetak** ke output.
- Modal yang disepakati: Rp25.000 per venue; kill-switch 15%
  (= Rp3.750) berlaku per venue.
- Deposit Rp25.000 ke Indodax hanya dilakukan saat live sudah disetujui,
  bukan sekarang (saldo akun saat persiapan: 0 IDR).
