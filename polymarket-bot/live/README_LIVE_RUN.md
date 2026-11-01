# Polymarket LIVE bot — paket kode persiapan

**Status: KODE SAJA. Tidak berjalan, tidak trading, tidak ada order.**
Parameter live sudah disetujui pemilik 2026-11-01 (kategori Up/Down +
cuaca + bola; modal $1,00/kategori; TP/SL/kill-switch per kategori;
aturan saring berita/prakiraan — lihat `SOP-TRADING.md`). Persetujuan
parameter BUKAN perintah mulai trading: trading tetap menunggu host
yang diizinkan + verifikasi wiring order SDK + cek geoblock dari
host itu. Paket ini ada supaya kode yang dipakai sudah punya gerbang,
aturan risiko, dan aturan verifikasi yang benar — bukan dirakit
terburu-buru saat itu.

## Isi paket

| File | Isi |
|---|---|
| `live_run.py` | Mode CHECK (default) + mode LIVE bergembok gerbang. Kredensial di-derive ulang tiap jalan dari `POLY_PRIVATE_KEY` (in-memory, tidak dicetak, tidak disimpan). |
| `derive_creds.py` | Alat cek/derive kredensial (CHECK default; DERIVE bergembok). Opsional sebagai pra-cek host; bot tidak lagi butuh salinan kredensial tersimpan. |
| `derive_test.py` | Tes offline alat derive. |
| `params.example.json` | CONTOH parameter saja — bukan persetujuan. |
| `test_live.py` | Tes offline (stdlib unittest, tanpa jaringan, tanpa secret). |
| `requirements.txt` | Yang diinstal host (`polymarket-client`); selebihnya stdlib. |
| `SOP-TRADING.md` | Prosedur operasi standar live (checklist, aturan runtime, monitoring, respons insiden, pencatatan). |

File yang SENGAJA TIDAK ADA di paket ini: `LIVE_APPROVED.txt` dan
`params.json`. Keduanya hanya dibuat pemilik saat menyetujui live.
Tanpa keduanya, mode live mustahil jalan.

## Mode CHECK (default, aman dijalankan kapan saja)

```bash
python3 live_run.py
```

CHECK hanya melakukan, tanpa order, tanpa request privat, tanpa
menurunkan kredensial (derive hanya terjadi di mode live setelah
gerbang lolos):

1. Melaporkan kehadiran environment (nama saja — nilai tidak pernah
   dicetak): `POLY_PRIVATE_KEY`, plus status SDK resmi
   (modul `polymarket` terpasang / tidak; nama paket pip-nya
   `polymarket-client`). Nama kredensial API tersimpan
   (`POLY_API_KEY` dkk.), bila ada, dilaporkan hanya
   sebagai catatan bahwa nilainya DIABAIKAN bot.
2. Mengecek geoblock dari mesin ini: `GET polymarket.com/api/geoblock`.
3. Membaca satu market publik dari Gamma (keyless).
4. Memvalidasi `params.json` bila ada (bila tidak ada, itu wajar).

CHECK selesai dengan nol order, nol kredensial diturunkan, nol
request privat, nol nilai rahasia dicetak.

## Gerbang mode LIVE (semua wajib, sebelum request order apa pun)

```bash
LIVE_TRADING=1 python3 live_run.py --live
```

Mode live menolak (keluar, nol order) bila SATU saja gagal:

1. Flag `--live` tidak diberikan.
2. `LIVE_TRADING=1` tidak diset di environment.
3. `LIVE_APPROVED.txt` tidak ada di folder skrip.
4. `params.json` tidak ada atau gagal validasi.
5. Geoblock dari mesin ini menyatakan blocked ATAU tidak dapat
   dipastikan (fail-closed).
6. `POLY_PRIVATE_KEY` tidak ada di environment, atau SDK resmi
   (modul `polymarket`) belum terpasang di mesin ini. Kredensial
   API tersimpan (`POLY_API_KEY`/`POLY_SECRET`/`POLY_PASSPHRASE`)
   TIDAK LAGI cukup — bot mengabaikan nilainya dan derive ulang
   dari private key tiap jalan.

Kode keluar: `0` selesai, `1` gagal operasional (nol order baru),
`2` kredensial/SDK tidak lengkap (mode live), `3` gerbang/params
ditolak.

## Validasi params

- `category` harus salah satu dari: `updown`, `weather`, `soccer`.
- `chain` harus `polygon`, `collateral` harus `USDC` (aset funding
  yang dipakai: USDC jaringan Polygon).
- `modal_usd` > 0; `0 < first_trade_usd <= modal_usd`.
- `sl_pct` 1–50; TP 1–50 (`tp_pct` untuk updown, `tp1_pct`/`tp2_pct`
  untuk weather/soccer dengan `tp2_pct >= tp1_pct`).
- `kill_switch_pct` 5–50.
- `min_order_size` minimal 5 (order di bawah itu DITOLAK, bukan
  dibulatkan ke atas secara diam-diam).
- `TP < SL` hanya peringatan, bukan penolakan.

## Aturan risiko (cermin modul paper)

- Up/Down: TP +20% jual habis, lalu rotasi ke market lain; SL −5%;
  kill-switch 15%.
- Cuaca + bola: TP bertangga +10% jual separuh, +15% jual sisa;
  SL −5%; kill-switch 15%.
- Prioritas bila beberapa trigger bersamaan:
  **kill-switch > SL > TP2/TP20 > TP1**.
- Trigger jual diukur ask-ke-ask (spread tidak memicu SL palsu);
  hasil jual dihitung di bid.
- Fee dimodelkan dari `feeSchedule` tiap market (seperti modul
  paper); order di bawah `orderMinSize` 5 lembar ditolak.
- Binary/spot saja. Tanpa leverage, tanpa margin, tanpa futures.
  Tidak ada pemanggilan withdraw dalam bentuk apa pun.

## Aturan besi setelah error order

**Respons error TIDAK MEMBUKTIKAN tidak terjadi fill.** Pelajaran
ini sudah dibayar mahal di venue lain: sebuah order pernah terisi
padahal responsnya error. Karena itu, setelah error apa pun, paket
ini TIDAK PERNAH me-retry otomatis. Ia membaca ulang state
(saldo/order) dan BERHENTI, menyerahkan verifikasi manual kepada
pemilik sebelum tindakan apa pun berikutnya.

## Kredensial: runtime re-derivation dari private key

Polymarket tidak punya API key gaya daftar-isi-formulir. Autentikasi
trading ada dua lapis:

- **L1:** wallet menandatangani pesan EIP-712 `ClobAuth`, lalu SDK
  resmi menurunkan `apiKey` + `secret` + `passphrase`.
- **L2:** setiap request privat ditandatangani HMAC-SHA256; setiap
  order juga membawa tanda tangan wallet sendiri.

SDK resmi Python: paket pip **`polymarket-client` 0.15.0** (repo
Polymarket/py-sdk), modul impor **`polymarket`**, klien
**`polymarket.SecureClient`**. Entry point derive yang benar:
**`SecureClient.create(private_key, wallet)`** — di dalamnya SDK
menandatangani pesan L1 `ClobAuth` (EIP-712, chain 137), memanggil
endpoint create/derive, lalu memvalidasi kredensial. Versi 0.15.0
ini terbukti terpasang di host (log pip 2026-11-01:
`polymarket-client` 0.15.0 + `eth-account` 0.13.7).
**Jangan** pakai `py-clob-client` — paket itu diarsipkan dan order
V1-nya ditolak sejak CLOB V2 live.

**Pola baru (dipilih pemilik 2026-11-01: "bot derive ulang tiap
jalan"):** tidak ada salinan kredensial API yang disimpan di mana
pun. Setiap kali bot jalan, ia menurunkan ketiga nilai itu dari
`POLY_PRIVATE_KEY` lewat SDK resmi, memakainya untuk membangun
klien, dan tidak pernah mencetak, menulis ke file, atau menyimpannya
di luar memori proses itu. Bila environment kebetulan berisi
`POLY_API_KEY`/`POLY_SECRET`/`POLY_PASSPHRASE` lama, nilainya
sengaja DIABAIKAN — gerbang tetap menuntut private key.

Langkah pemilik (di mesin yang akan menjalankan bot, BUKAN di chat):

1. Instal `polymarket-client` dari `requirements.txt`.
2. Ketik `POLY_PRIVATE_KEY` wallet live ke environment mesin itu
   sendiri (akun utama). Akun ini berstruktur signer + deposit:
   kunci mengendalikan alamat signer
   (`0x911379D40dc42d8198baA4f1b7bB29b71A7d3d72`, identitas
   trading yang dicek bot), dana berada di alamat profil
   (`0xc4bA60A94edBfeF6CD7177B6e6e02b1c2b17B4FB`). Wallet bot
   Bitget lama diparkir dan TIDAK dipakai untuk live.
3. Jalankan CHECK (`python3 live_run.py`): harus melaporkan private
   key ada + SDK terpasang, tanpa nilai apa pun tercetak. Alat
   `derive_creds.py` (mode CHECK) bisa dipakai sebagai pra-cek
   tambahan: kesiapan derive + kecocokan alamat, juga tanpa nilai.
4. Jangan pernah menulis private key atau nilai kredensial ke file
   repo, chat, screenshot, atau halaman startup yang difoto.
   Private key tidak pernah dicetak skrip ini — hanya "ada /
   tidak ada". Kunci yang pernah terekspos di chat/screenshot
   harus diganti (rotasi) sebelum dipakai live.

Catatan kejujuran: perbaikan impor SDK ini (modul `polymarket`,
bukan nama impor lama yang salah) sudah dites offline dengan mock,
tetapi derive dengan kunci asli belum pernah dieksekusi di mesin
ini maupun di host. CHECK lama di host melaporkan SDK tidak
terpasang karena bug nama impor tersebut, padahal pip sudah
memasang paketnya — setelah upload ulang, CHECK di host harus
melaporkan SDK terpasang; bila tidak, jangan menebak, laporkan
outputnya. Konstruksi klien juga dijaga: bot hanya memanggil
create() setelah alamat lokal terverifikasi cocok dengan wallet
signer (akun berstruktur signer + deposit, bukan kasus EOA
murni), sehingga tidak ada efek on-chain dari langkah
verifikasi; untuk tipe wallet non-EOA yang belum ter-deploy,
create() bisa men-deploy deposit wallet, jadi verifikasi lokal
adalah gerbang wajib, bukan opsional. Wiring order tetap belum
ditambahkan dan mode_live tetap berhenti setelah verifikasi state,
tanpa order.

## Geoblock: tanpa pengelakan

Bila endpoint geoblock menyatakan mesin ini blocked, mode live
menolak dan skrip berhenti. **Jangan** memakai VPN, proxy, atau
cara apa pun untuk mengakali blokir geografis. Solusi yang benar
adalah memindahkan proses ke mesin yang diizinkan, lalu cek
geoblock lagi dari mesin itu.

## Yang paket ini TIDAK lakukan

- Tidak menempatkan order apa pun pada mode CHECK.
- Tidak menempatkan order pada mode LIVE sampai semua gerbang
  lolos DAN antarmuka order SDK terverifikasi di mesin host
  (siklus live paket ini berhenti pada verifikasi state — itu
  disengaja, bukan bug).
- Tidak mengklaim live berjalan atau menguntungkan. Parameter
  disetujui pemilik, tetapi trading belum jalan sampai host +
  wiring + geoblock terverifikasi. Tidak ada klaim profit di paket
  ini, dan tidak boleh ada.
- Tidak menyentuh ledger/state paper, tidak mengubah modul paper,
  tidak menyentuh folder rilis GitHub.
