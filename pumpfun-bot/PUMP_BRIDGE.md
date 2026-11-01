# Pump.fun — demo dan jembatan live nanti

Track ke-5. Demo dulu, tanpa uang asli, tanpa wallet.

## Keadaan sekarang (demo)

- `pumpfun_paper.py` berjalan di data publik gratis DexScreener (tanpa
  key, tanpa koneksi chain). Untuk demo, jaringan tidak menghalangi
  apa-apa: yang dipakai hanya harga, likuiditas, dan volume publik.
- Filter kejujuran: hanya pair Pump.fun (dexId pumpfun/pumpswap) dengan
  likuiditas >= $10.000 dan volume 24 jam >= $5.000 yang boleh dibeli
  paper. Token meme tipis = slippage mematikan di ukuran Rp10.000
  (~$0,55); kalau tidak ada yang lolos, keputusannya NO_TRADE.
- Aturan demo sama seperti venue lain: modal virtual Rp50.000, trade
  pertama Rp10.000, SL 5%, TP 10%/15%, kill-switch 15%.
- Peringatan khas meme: token bisa rug / jatuh ke nol dalam menit.
  Paper tidak memodelkan rug, pajak jual-beli, dan prioritas fee Solana.

## Live nanti (belum mulai, terkunci seperti venue lain)

- Pump.fun hidup di Solana. Itu sifat platformnya, bukan pilihan —
  kalau mau meme launchpad lain di chain lain, itu venue berbeda.
- Bot TIDAK menggerakkan aplikasi Bitget Wallet di HP pemilik, dan
  aplikasi wallet TIDAK disambungkan ke Muse. Yang dipakai nanti:
  wallet khusus bot (keypair baru, terpisah dari simpanan utama, dana
  kecil saja) yang menandatangani transaksi on-chain.
- Seed phrase wallet khusus bot TIDAK PERNAH dikirim lewat chat, tidak
  disimpan di repo, tidak disimpan di Muse. Pemilik yang menyiapkan
  wallet itu nanti (Bitget Wallet boleh dipakai untuk membuat/menyimpan
  keypair-nya, tapi kunci signing bot tetap terpisah dari wallet utama).
- Teknis live: paket `@pump-fun/pump-sdk` (beli/jual bonding curve +
  PumpSwap), SOL untuk fee, slippage diset eksplisit, dan penarikan
  profit ke Bitget Wallet pemilik (alamat Solana pemilik untuk
  MENERIMA hasil saja — bukan untuk signing bot).
- Penarikan awal selalu manual/disutujui pemilik, bukan otomatis.
- Live tetap terkunci sampai demo terbukti + parameter persis disetujui
  pemilik — sama seperti venue lain.
