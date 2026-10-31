# Jembatan data MT5 (rencana)

Track Forex yang dipilih pemilik: **MT5**. Dokumen ini menjelaskan kenapa
modul paper `mt5_paper.py` untuk sementara memakai data acuan publik, dan
bagaimana terminal MT5 yang asli disambungkan nanti.

## Keadaan sekarang (demo)

- `mt5_paper.py` berjalan di data acuan harian gratis Frankfurter
  (referensi ECB, tanpa key): EURUSD + USD/IDR untuk konversi rupiah.
- Ini BUKAN tick real-time MT5. Harga yang dipakai harga mid harian;
  spread, slippage, dan swap live belum dimodelkan.
- Aturan demo sama seperti venue lain: modal virtual Rp50.000, trade
  pertama Rp10.000, SL 5%, TP 10%/15%, kill-switch 15% (lantai Rp42.500).
- Nol order nyata. Modul ini tidak terhubung ke terminal atau broker.

## Yang disiapkan pemilik (terminal MT5)

1. Unduh MT5 desktop (Windows; Mac lewat Wine — MT5 mobile tidak bisa
   dipasangi jembatan, jadi jembatan butuh terminal desktop).
2. Buka akun demo gratis di terminal: server demo MetaQuotes
   (MetaQuotes-Demo), tanpa deposit, tanpa broker. Pasangan utama: EURUSD.
3. Terminal harus tetap jalan saat jembatan aktif — terminal yang mati
   berarti data berhenti. Untuk 24 jam, terminal jalan di VPS (lihat
   hosting: Wispbyte/Oracle/Alibaba) atau PC yang selalu menyala.

## Jembatan nanti (saat terminal sudah jalan)

Pilihan standar, dari yang paling sederhana:

- **A. Ekspor CSV (paling mudah).** Expert Advisor/script MQL5 menulis
  harga EURUSD (bid/ask + waktu) ke file CSV tiap tick/detik; engine
  membaca file itu. Tidak butuh library khusus, tapi ada jeda file.
- **B. Paket Python MetaTrader5.** Di mesin yang sama dengan terminal
  (Windows), paket `MetaTrader5` (pip) login ke terminal dan mengambil
  tick + posisi langsung. Paket ini hanya jalan di Windows tempat
  terminal terpasang — tidak bisa dipanggil dari server lain.
- **C. API/HTTP lokal.** EA mengirim tick ke endpoint HTTP kecil di
  mesin engine. Paling fleksibel, paling banyak kode.

Urutan yang disarankan: A dulu untuk membuktikan aliran data, baru B/C
kalau butuh tick real-time penuh.

## Live nanti (belum mulai, terkunci seperti venue lain)

- Akun live wajib cent/micro dengan min deposit rendah (modal Rp50.000
  ≈ $3) — broker yang min depositnya di atas itu tidak layak.
- Kriteria broker (keputusan pemilik): mendukung penarikan ke SeaBank,
  dan kalau bisa penarikan USDT (TRC20/ERC20) ke Bitget Wallet.
- Penarikan awal selalu manual/disutujui pemilik, bukan otomatis.
- Live tetap terkunci sampai demo terbukti + parameter persis disetujui
  pemilik — sama seperti Indodax dan Polymarket.
