# Moomoo — demo dan jembatan live nanti

Track saham AS/global ke-4. Demo dulu, tanpa uang asli, tanpa akun.

## Keadaan sekarang (demo)

- `moomoo_paper.py` berjalan di data publik gratis Yahoo Finance
  (harga tutup harian AAPL, tanpa key) + kurs Frankfurter. (Stooq
  dicoba dulu tapi diblokir dari VM ini: mengembalikan halaman
  JS-check, bukan CSV.) Bukan data real-time Moomoo; komisi/fee live
  belum dimodelkan.
- Aturan demo sama seperti venue lain: modal virtual Rp50.000, trade
  pertama Rp10.000, SL 5%, TP 10%/15%, kill-switch 15%.
- Kalau data gagal diambil, trade dilewati dan saldo tetap (tidak ada
  harga tebakan).

## Live nanti (belum mulai, terkunci seperti venue lain)

- Moomoo OpenAPI: butuh akun Moomoo + gateway OpenD yang jalan terus
  di mesin bot (gateway mati = data/order berhenti). Paper trading
  tersedia di OpenAPI untuk latihan sebelum live.
- Pembukaan akun tergantung domisili: Moomoo tidak mencakup saham
  Indonesia (IDX tidak ada di 8 pasarnya); kemungkinan entitas
  Singapura — dicek saat daftar, jangan diasumsikan lolos.
- Penarikan profit ke SeaBank SAJA via SWIFT (keputusan pemilik).
  Biaya wire Moomoo sekitar SGD 30 (biaya admin, bukan pajak) — jauh
  lebih besar dari modal Rp50.000, jadi JANGAN tarik sebelum profit
  jauh lebih besar. SeaBank menerima SWIFT (kode SSPIIDJAXXX, 1–3 hari
  kerja); biaya masuk SeaBank yang persis belum terverifikasi —
  konfirmasi ke SeaBank sebelum penarikan pertama.
- Pajak (bukan nasihat pajak): dividen saham AS dipotong 30%, 15%
  dengan W-8BEN (treaty Indonesia–AS); Indonesia memajaki penghasilan
  worldwide di SPT 1770 (progresif 5%–35%, kredit PPh Pasal 24).
- Penarikan awal selalu manual/disutujui pemilik, bukan otomatis.
- Live tetap terkunci sampai demo terbukti + parameter persis
  disetujui pemilik — sama seperti venue lain.
