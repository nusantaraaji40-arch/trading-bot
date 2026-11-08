# Migrasi Loop Live Indodax: Wispbyte → Tencent

Dibuat 2026-11-09 WIB. Keputusan pemilik: **Pindahkan Indodax ke Tencent**
(dipilih via widget 2026-11-09 ~01:41 WIB). MEXC **dihentikan dulu** atas
permintaan pemilik — tidak ada deploy MEXC di paket ini.

## Yang TIDAK berubah (parameter live, disetujui 2026-11-01)

- Pair: BTC/IDR (loop bisa beli koin Indodax lain setelah posisi terjual,
  sesuai screening — sama seperti di Wispbyte)
- Beli maks **Rp20.000** per beli, buffer fee Rp500
- SL **30%**, TP **15%** jual habis, kill-switch lantai **Rp16.468**
- Poll **60 detik** saat pegang posisi, saring tiap **600 detik** saat kosong
- SPOT saja, tanpa leverage/margin/futures, TANPA withdraw
- Kode: `live_loop.py` — salinan persis dari yang jalan di Wispbyte
  (sha256 `de53d51b289949ef6cc3e79277d5479643e6f5c6095229c0263f73e883577805`,
  775 baris, stdlib saja, tanpa pip install, Python 3.10 di server cukup)

## Isi paket ini

| File | Keterangan |
|---|---|
| `live_loop.py` | Loop live, salinan persis (hash terverifikasi) |
| `test_loop.py` | Tes unit loop — lokal `ALL_PASS`, gerbang teruji |
| `loop_params.json` | Parameter di atas, siap dipakai |
| `LIVE_APPROVED.txt.example` | Template persetujuan — ganti nama jadi `LIVE_APPROVED.txt` HANYA di jendela migrasi |
| `.indodax_env.example` | Template env key — isi HANYA di server, `chmod 600` |
| `check_indodax.py` | Cek saldo baca-saja (signed), nol order — untuk tes Singapura → Indodax |
| `indodax-loop.service` | systemd, auto-restart 60 detik (Wispbyte tidak punya ini) |
| `.gitignore` | Blokir `.indodax_env`, `LIVE_APPROVED.txt`, log |

Tidak ada key/secret asli di paket ini. Tidak ada.

## Urutan migrasi (jangan dilompati)

### 0. Patokan live sekarang — BLOKIR, menunggu screenshot pemilik
Buka Wispbyte → konsol **My-trading-bot-5** → screenshot output terakhir
(posisi, entry, SL/TP, saldo). Kirim ke Muse. Tanpa patokan ini, kita
tidak bisa membuktikan Tencent membaca posisi yang sama. **Jangan tekan
Stop dulu.**

### 1. Salin paket ke server Tencent
Di terminal server (OrcaTerm, sudah login sebagai ubuntu):
```bash
mkdir -p ~/indodax-live
# cara A: git clone repo trading-bot, salin folder indodax-live-v2
# cara B: upload folder indodax-migrate/ ini ke ~/indodax-live (scp)
# cara C (fallback, bila clone tidak berisi folder loop): unduh zip paket
#   curl -L -o /tmp/indodax-migrate.zip "https://muse.ai/files/1405111536011103/1793748038365023/y3to6ru3hfs9ffjvn1jnjdfa/indodax-migrate.zip"
#   unzip -o /tmp/indodax-migrate.zip -d ~/ && mv ~/indodax-migrate/* ~/indodax-live/
#   (link berlaku s/d 2026-11-10 18:50 UTC, isi zip tanpa key/secret)
ls ~/indodax-live
```
Harus ada: `live_loop.py`, `loop_params.json`, `check_indodax.py`.

### 2. Tes aman (nol order, wajib lolos sebelum key dimasukkan)
```bash
cd ~/indodax-live
python3 live_loop.py
# Harus keluar: "INDODAX_API_KEY / INDODAX_SECRET belum diset" + exit 2
python3 -m unittest test_loop
# Harus keluar: ALL_PASS
```

### 3. Isi key di server (pemilik sendiri, tidak lewat chat)
```bash
cp .indodax_env.example ~/.indodax_env
nano ~/.indodax_env   # isi INDODAX_API_KEY + INDODAX_SECRET (trade-only)
chmod 600 ~/.indodax_env
set -a; source ~/.indodax_env; set +a
python3 check_indodax.py
# Harus keluar saldo IDR/BTC/ETH + "CHECK OK". Ini bukti Singapura bisa
# memanggil API Indodax bertanda tangan. Kalau GAGAL, STOP — jangan lanjut.
```
Key yang dipakai: key trade-only yang sama dengan yang dipakai Wispbyte
(View + Trade, tanpa withdraw). Jangan buat key baru tanpa alasan, dan
jangan kirim nilainya ke Muse.

### 4. Jendela pindah (cepat, satu rangkaian)
1. Di Wispbyte: tekan **Stop** pada My-trading-bot-5. Tunggu konsol
   berhenti, screenshot — pastikan tidak ada log baru.
2. Di Tencent, di folder `~/indodax-live`:
   ```bash
   cp LIVE_APPROVED.txt.example LIVE_APPROVED.txt
   sudo cp indodax-loop.service /etc/systemd/system/indodax-loop.service
   sudo systemctl daemon-reload
   sudo systemctl enable indodax-loop.service
   sudo systemctl start indodax-loop.service
   sleep 65; tail -30 ~/indodax-live/loop.log
   ```
3. Verifikasi poll pertama: banner "MODE: LOOP LIVE", aturan yang sama,
   dan baris posisi (koin + entry + SL/TP) **harus cocok dengan patokan
   langkah 0**. Kalau tidak cocok, STOP service Tencent dan laporkan —
   Wispbyte masih ada sebagai cadangan.
4. Jangan hapus Wispbyte. Jangan ubah Startup Command Wispbyte dulu.
   Simpan sebagai fallback sampai Tencent terbukti 1–2 siklus.

### 5. Pantau
`sudo systemctl status indodax-loop.service` dan `tail -f ~/indodax-live/loop.log`.
Loop Tencent auto-restart 60 detik kalau proses mati (lebih aman dari
Wispbyte). Server mati = loop berhenti, sama seperti sebelumnya.

## Risiko yang harus diakui pemilik

- **Jeda tanpa pantau:** antara Stop Wispbyte dan Start Tencent ada jeda
  beberapa menit. Bila harga menyentuh SL/TP/KS tepat di jeda itu, exit
  terlambat. Lakukan migrasi di jam tenang dan secepat mungkin.
- **Dua loop jalan bersamaan = order ganda.** Jangan pernah jalankan
  Wispbyte dan Tencent bersamaan dengan LIVE_TRADING=1. Satu saja.
- **API Singapura belum terbukti.** MEXC sudah terbukti dari server ini
  (`{}`), Indodax bertanda tangan belum — itulah gunanya langkah 3.
  Kalau langkah 3 gagal, migrasi dibatalkan dan loop tetap di Wispbyte.
- **Key diketik ulang.** Key harus diketik pemilik di server Tencent.
  Kalau salah ketik, check langkah 3 akan gagal — itu sengaja, supaya
  loop tidak jalan dengan key salah.

## Rollback

Kalau Tencent bermasalah setelah Start: `sudo systemctl stop
indodax-loop.service`, lalu Start kembali Wispbyte dengan Startup Command
lama (jangan diubah sebelum migrasi terbukti). Posisi di Indodax tidak
berubah karena migrasi — yang pindah hanya mesin yang memantaunya.
