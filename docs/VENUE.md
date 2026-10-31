# Detail 5 venue

Urutan pengerjaan, modal, dan routing payout yang diputuskan pemilik.
Semua venue mulai dari DEMO (paper trading, nol uang asli) sampai terbukti,
baru dipertimbangkan live modal kecil setelah parameter disetujui.

Ringkasan: modal Rp50.000 per venue, total Rp250.000. Kill-switch 15% per
venue (= Rp7.500): hentikan venue saat rugi mencapai batas itu. Stop loss
5%, take profit 10-15%.

| # | Venue | Modal | Status | Payout |
| --- | --- | --- | --- | --- |
| 1 | Indodax (spot) | Rp50.000 | Demo jalan | Tetap di akun Indodax |
| 2 | Polymarket | Rp50.000 (~$3 USDC Polygon) | Demo jalan | Bitget Wallet (USDC Polygon) |
| 3 | Forex MT4/5 | Rp50.000 (~$3) | Akun demo dulu | SeaBank (atau USDT bila broker mendukung) |
| 4 | Moomoo | Rp50.000 (~$3) | Paper trading dulu | SeaBank saja via SWIFT |
| 5 | Pump.fun | Rp50.000 (~$3 / ~0,03 SOL) | Demo data DexScreener | Bitget Wallet (Solana) |

Penarikan awal selalu manual dan disetujui pemilik, bukan otomatis oleh bot.

## 1. Indodax (spot)

- Demo sudah jalan di data publik live dengan saldo virtual Rp50.000
  (paper beli 0,00000711 BTC seharga Rp10.000 di harga ask, sisa Rp40.000).
- CCXT teruji live pada data publik (Indodax + Gate).
- Sebelum live: cek minimum order per pair. Live memakai Trade API key
  dari website (bukan password di chat), trade-only.
- Binance TIDAK dipakai atas permintaan pemilik, dihapus dari rencana.

## 2. Polymarket

- Demo paper di harga live (Gamma + CLOB), saldo virtual 1000 USDC.
- Edge = 1 - (YES ask + NO ask), ambang 0,01. Hanya market aktif yang
  dipakai; market kedaluwarsa disaring.
- Catatan kelayakan: biaya beli USDC + bridge bisa menggerus porsi besar
  dari modal ~$3. Hitung biaya dulu sebelum live.
- Tidak ada testnet resmi Polymarket; paper trading di harga live adalah
  jalur demo yang benar.

## 3. Forex MT4/5

- Mulai dari akun demo, lalu live micro/cent.
- Syarat live di modal ~$3: akun cent/micro dengan minimum deposit rendah.
- Broker dipilih yang mendukung penarikan SeaBank (dan USDT bila ada).
- Penarikan mengikuti jalur deposit (aturan AML broker).

## 4. Moomoo (saham AS/global)

- Via Moomoo OpenAPI + paper trading dulu. Gateway OpenD harus jalan di
  mesin bot.
- 8 market; IDX (Indonesia) TIDAK termasuk. Kelayakan residensi dicek
  saat daftar (kemungkinan entitas Singapura).
- Penarikan profit HANYA ke SeaBank via SWIFT. Biaya wire sekitar SGD 30
  (sekitar Rp350 ribu) jauh lebih besar dari modal — jangan tarik sebelum
  profit jauh lebih besar.
- Pajak (bukan saran pajak): non-residen AS tidak kena capital-gains AS;
  dividen dipotong 30%, 15% dengan W-8BEN (treaty Indonesia-AS); penghasilan
  dunia tetap dilaporkan di SPT 1770 Indonesia.

## 5. Pump.fun

- Demo memakai data DexScreener (tanpa wallet).
- Live wajib memakai wallet KHUSUS bot, terpisah dari simpanan utama,
  dana kecil saja. Seed phrase tidak pernah dikirim lewat chat.
- Catatan kelayakan: ukuran ~0,03 SOL rawan slippage dan fee relatif
  besar.
- Payout ke Bitget Wallet (Solana).
