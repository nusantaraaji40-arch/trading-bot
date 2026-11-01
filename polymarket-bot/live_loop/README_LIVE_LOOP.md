# Loop Live Polymarket — 3 Kategori (v5, build)

Loop trading live Polymarket untuk 3 kategori dalam **satu proses**:
`updown` (Up/Down jam-jaman), `weather` (cuaca), `soccer` (bola).
Satu posisi per kategori, modal $1,00 per kategori, gaya **scalping**:
pegang singkat, TP langsung jual habis lalu rotasi segera, SL potong cepat.

> **STATUS: KODE + TES + VERIFIKASI SAJA. Loop ini BELUM berjalan dan
> BELUM trading.** Start live nyata butuh persetujuan eksplisit user
> tersendiri setelah verifikasi host (CHECK + DRY-RUN) lolos. Jangan
> mengklaim loop ini jalan/trading sebelum itu terjadi.
>
> Paket ini **berbeda** dari paket verifikasi v4 di
> `polymarket-bot/live/` (one-shot, tanpa wiring order). File v4 tidak
> diubah oleh paket ini.

## Isi paket

| File | Isi |
| --- | --- |
| `live_loop.py` | Loop utama: gerbang, state per kategori, 8 peran Bro, monitor, jual/beli terverifikasi, kill-switch, mode CHECK / DRY-RUN / LIVE. |
| `order_wiring.py` | Lapisan order SDK resmi: bangun + tanda tangani + kirim order (limit/market), DRY-RUN tanpa POST, verifikasi isi lewat order book + posisi. |
| `signals.py` | Sinyal gratis tanpa key: RSS berita (Up/Down + bola) dan Open-Meteo (cuaca). Sinyal adalah GERBANG beli, bukan skor tambahan. |
| `loop_params.example.json` | CONTOH params 3 kategori. Bukan persetujuan. |
| `test_loop.py` | 60 tes loop (mock jaringan + mock SDK). |
| `test_wiring.py` | 18 tes wiring (mock SDK). |
| `README_LIVE_LOOP.md` | Dokumen ini. |
| `requirements.txt` | (dibuat saat pemaketan) `polymarket-client` — satu-satunya dependensi luar; sisanya stdlib. |

Struktur ini siap di-push ke repo GitHub publik (tanpa secret apa pun —
hanya dua alamat publik di bawah + nilai `FAKE-*` di tes). Pemilik
repo yang mem-push setelah verifikasi + kartu persetujuan.

## Alamat (publik, aman dicatat)

- **SIGNER** (identitas trading, yang dicek kode):
  `0x911379D40dc42d8198baA4f1b7bB29b71A7d3d72`
- **PROFIL/deposit** (tempat dana, referensi saja):
  `0xc4bA60A94edBfeF6CD7177B6e6e02b1c2b17B4FB`

Private key **tidak pernah** ada di file mana pun. Pemilik mengetiknya
sendiri ke environment mesin host (Startup Command server), persis pola
Indodax. Bot menurunkan kredensial CLOB dari private key itu setiap
kali jalan (runtime re-derivation), di memori saja, tidak pernah
dicetak/ditulis.

## Parameter FINAL (keputusan user 2026-11-02)

| Aturan | Nilai |
| --- | --- |
| Modal per kategori | $1,00 (total $3,00) |
| Posisi | 1 per kategori |
| Min order | 5 lembar |
| Up/Down | TP +20% jual habis lalu rotasi; |
| Cuaca + bola | TP1 +10% separuh, TP2 +15% sisa |
| **SL normal** | **−7% semua kategori** |
| **Batas keras** | **−12% semua kategori, tanpa pengecualian** |
| Kill-switch | 15% (level akun: total kas + nilai posisi ≤ 85% modal awal kategori) |
| Fee | taker diperhitungkan sebelum beli |
| Jenis | binary/spot saja, tanpa leverage, tanpa withdraw otomatis |

**Riwayat SL (jangan tertukar):** persetujuan awal 23:22 WIB 2026-11-01
memakai SL −5%; user 2026-11-02 mengubah ke SL −10%; lalu user
**01:11 WIB 2026-11-02 mengonfirmasi aturan FINAL: SL −7% + batas keras
−12%**. File persetujuan deploy (`LIVE_APPROVED_LOOP.txt`) **harus
menulis KEDUA angka (7% dan 12%)** — teks lama (SL 5% atau SL 10% saja)
**ditolak** oleh gerbang loop. File `params.json` +
`LIVE_APPROVED.txt` lama di server (paket v4, sudah lolos) **tidak
diubah** — itu paket berbeda.

**Prioritas trigger:** kill-switch total 15% > batas keras −12% >
SL −7% (dengan pengecualian tahan) > TP2/TP > TP1.

## Aturan rugi: SL −7% + pengecualian tahan + batas keras −12%

Posisi menyentuh −7% = **JUAL**, kecuali **pengecualian tahan**: bila di
−7% masih ada potensi naik yang **JELAS**, boleh ditahan. "Jelas"
didefinisikan definitif di kode (`recovery_evidence`) — ketiga kaki
harus terpenuhi sekaligus, kalau tidak → default JUAL:

1. **Momentum berbalik positif** — histori harga 1 jam terakhir naik
   (titik terakhir > titik pertama), atau bila tanpa histori, ask saat
   ini > ask poll sebelumnya.
2. **Sinyal terbaru tidak negatif** — gerbang sinyal kategori untuk
   pasar posisi itu masih lolos (berita/prakiraan masih mendukung).
3. **Pantulan dari titik terendah** — ask saat ini ≥ titik terendah
   sejak entry × 1,02 (pantulan minimal 2%).

Menyentuh **−12% = JUAL APA PUN YANG TERJADI**, tanpa pengecualian,
tanpa menunggu potensi naik. Bila harga melompati −12% karena book
tipis (gap), jual segera di bid terbaik — jangan tunggu pulih.

## Filter pra-beli anti-SL (aturan terpisah, tetap berlaku)

Sebelum membeli, loop menilai tren jangka pendek sisi kandidat dari
data CLOB/Gamma yang tersedia + arah book (`momentum_gate`):

- histori harga turun ≥ 5% dalam jendelanya, ATAU
- ask sudah ≥ 3% di bawah harga konsensus terakhir (`outcomePrices`),

maka beli di-**SKIP** + alasan dicatat di log.

**Jujur:** ini filter probabilitas, bukan ramalan. Ia mengurangi
frekuensi kena SL, **tidak bisa menghilangkan kena SL sepenuhnya**.
Pasar bisa berbalik setelah lolos filter.

## Ritme scalping

- Pegang posisi singkat: pasar **jam-jaman** (Up/Down), bukan harian.
  Up/Down menitan **ditolak** (pola "15 min"/"15-minute", durasi
  < 50 menit, ATAU rentang jam di judul yang window-nya < 50 menit,
  mis. "1:30PM-1:45PM" — perbaikan v6 setelah dry-run 2026-11-02
  menemukan pasar 15 menit lolos karena judulnya tidak mengandung
  kata "min" dan startDate Gamma adalah waktu listing, bukan window
  event).
- TP +20% (Up/Down) langsung **jual habis**, lalu **rotasi segera**:
  kategori yang CLOSED di Fase A poll yang sama langsung disaring
  lagi di Fase B poll yang sama — tanpa jeda idle yang lama.
- SL potong cepat: tidak ada menahan pecundang berharap balik arah.
- **Tidak ada averaging down** — tidak pernah tambah posisi merugi.
- **Tidak ada menahan posisi melewati resolusi tanpa rencana keluar** —
  resolusi dicek dulu setiap poll; settle hanya bila Gamma
  `closed=True` DAN harga decisif (≥ 0,999 satu sisi).
- **Keluar cepat TERGANTUNG likuiditas bid.** Bila book kosong/tanpa
  bid, posisi berstatus `CANNOT_EXIT` dan loop menunggu bid — tidak
  pernah memaksakan jual di harga nol.

## Aturan kas: untung dikit-dikit jadi bukit

Kas per kategori **bergulir**: modal awal + hasil realisasi (menang
maupun kalah) menumpuk di kas kategori itu.

- Ukuran beli per trade = `min(first_trade_usd, kas tersedia)`,
  tetap mematuhi min order 5 + fee.
- Keuntungan **menumpuk** di kas (bukit), tetapi **risiko per trade
  tidak ikut membesar** — tetap dibatasi `first_trade_usd`.
- Jangan pernah memakai seluruh kas yang membesar untuk satu beli.

Contoh angka: menang +20% dari $1 = **$0,20 kotor sebelum fee/spread**;
kalah −7% = potong cepat −$0,07 kotor. Bukit hanya terbentuk bila
**menang bersih melampaui kalah + fee dalam jangka panjang** — itu
bukan janji. Fee + spread menggerus untung kecil pada anggaran $1,
jadi hitung bersih setelah fee sebelum klaim untung.

## Peran agen (Bro 1–8, modul kode — BUKAN LLM berbayar)

| Peran | Tugas di loop |
| --- | --- |
| Bro 8 CRAWLER | Ambil pasar Gamma per tag + book CLOB + histori harga. |
| Bro 2 SCAN | Urutkan kandidat (bola: match ≤ 48 jam dulu; lainnya volume). |
| Bro 3 VET | Filter mekanis: durasi, likuiditas ≥ $500, spread ≤ 20%, aktif + acceptingOrders, rotasi (bukan pasar terakhir), sisi ask termurah. |
| Bro 4 SOCIAL | Gerbang sinyal: RSS berita (Up/Down + bola), Open-Meteo (cuaca). |
| Bro 5 SIZE | Anggaran = min(first_trade, kas); ukuran = floor(anggaran / biaya per lembar incl. fee), minimal min order. |
| Bro 1 CHIEF | Putusan akhir: mekanis → ukuran → momentum anti-SL → sinyal → (cuaca: hanya sisi Yes). |
| Bro 6 FILLS | Eksekusi: bangun + kirim, verifikasi isi lewat book + posisi, alih metode bila limit menggantung. |
| Bro 7 RISK | Monitor posisi: resolusi → book segar → recovery → trigger KS > hard > SL > TP. |

Setiap peran menulis log berawalan `[Bro N NAMA]` sehingga alasan
setiap keputusan/SKIP/error bisa dilacak.

## Sinyal berita: GERBANG beli (bukan skor tambahan)

- **Up/Down + bola:** tanpa berita relevan yang jelas → **JANGAN
  BELI**. Multi-sumber RSS gratis: Google News RSS (per kata kunci),
  CoinDesk RSS, Cointelegraph RSS (kripto), BBC Sport Football RSS
  (bola). Kata kunci dicocokkan ke pasar: Bitcoin untuk Up/Down BTC,
  nama tim untuk bola (dari "Will <TIM> win ...").
- Bukti berita (**judul + sumber**) dicatat di log keputusan.
- **RSS gagal diakses = sinyal tidak tersedia = SKIP.** Feed OK tapi
  tidak ada kata kunci cocok = SKIP.
- **Cuaca:** Open-Meteo tanpa key (geocoding + forecast). Hanya sisi
  YES yang boleh dibeli, dan hanya bila |prakiraan − target| ≤ 2,0°C.
  Tidak ada beli sisi NO untuk cuaca. Fetch/gagal parse = SKIP.

**Batasan jujur:** kata kunci = keberadaan katalis, **bukan prediksi
arah**. Berita mengurangi tebak-tebakan, **bukan jaminan untung**.
Prakiraan Open-Meteo adalah model, bukan kebenaran resmi; ambang ±2°C
adalah filter plausibilitas, bukan prakiraan akurat. RSS bisa lambat,
dibatasi, atau berubah format → loop SKIP dengan aman, bukan beli
buta.

## Hardening: gagal AMAN, bukan gagal merugikan

Tidak ada sistem yang dijamin nol gagal. Yang dijamin loop ini adalah
**gagal AMAN** (skip/berhenti), bukan gagal merugikan:

- **Tidak meleset:** trigger dicek tiap poll dari ask/bid **segar**
  (bukan harga basi); hitung TP/SL/KS dengan epsilon float; harga
  tepat di batas **ke-trigger** (dibuktikan tes batas persis); pasar
  salah kategori/tag/durasi tidak pernah dibeli.
- **Tidak cacat:** semua input eksternal divalidasi — bentuk tak
  dikenal = SKIP + log, bukan crash dan bukan beli buta; state ditulis
  **atomik** (file temp + fsync + ganti nama) supaya tidak rusak bila
  proses mati mendadak; state korup = kategori berhenti sampai pemilik
  perbaiki manual; guard 1 posisi per kategori (beli ditolak bila
  posisi masih OPEN/PARTIAL/PENDING).
- **Tidak lemah:** setiap jual/beli **diverifikasi** lewat order book
  + posisi sebelum langkah berikut — respons sukses/error mentah
  tidak pernah dipercaya begitu saja (pelajaran Indodax: respons
  error order tidak sama dengan tidak terisi). Order error **tidak
  di-retry buta**: cek dulu (adopsi dari book bila sudah ter-posting),
  lalu coba metode lain (limit menggantung → market), lalu log +
  berhenti aman bila tetap gagal. Kill-switch menjual semua +
  menghentikan loop. Error jaringan = tunggu poll berikut, bukan
  crash.
- **Tidak gagal diam-diam:** setiap keputusan + setiap SKIP + setiap
  error dicatat ke log dengan alasan (termasuk bukti sinyal). Mode
  gagal default = SKIP/BERHENTI AMAN, bukan trading.

## 24/7: proses jangka panjang di server user

Loop dirancang jalan terus setelah Start di server user (bukan
one-shot):

- State per kategori tersimpan di file JSON (`state/state_<kategori>.json`)
  + `state/history.jsonl` (append-only). Bila proses di-Start ulang,
  ia **melanjutkan dari state terakhir**: tidak beli ganda, tidak lupa
  posisi, tidak lupa kas.
- Poll 60 detik saat memegang posisi / 600 detik saat idle.
- **Tidak ada dependensi pada Muse** — Muse tidak jalan 24/7; loop di
  server user yang jalan.
- **Server harus tetap online.** Panel gratis berhenti bila tidak
  login: pemilik login panel **tiap 10 hari** (pengingat diajukan
  terpisah). Tidak ada auto-restart: bila server berhenti, loop
  berhenti — pemilik Start ulang dan loop melanjutkan dari state.

## Deploy (pemilik yang menjalankan, satu langkah per satu)

1. Upload zip paket ini ke server Polymarket (server #2) dan ekstrak
   di root.
2. Salin `loop_params.example.json` menjadi `loop_params.json`
   (sesuaikan bila perlu — tetapi SL 7% + batas keras 12% + KS 15%
   adalah aturan FINAL, jangan diubah tanpa persetujuan baru).
3. Buat `LIVE_APPROVED_LOOP.txt` — file persetujuan **terpisah** dari
   `LIVE_APPROVED.txt` v4 (paket berbeda, tidak boleh bentrok).
   Isinya harus menyebut: 3 kategori, modal $1 per kategori,
   **SL 7%, batas keras 12%, kill-switch 15%**, TP Up/Down +20% jual
   habis, TP cuaca/bola +10%/+15%, min order 5, tanpa leverage, tanpa
   withdraw otomatis. (Gerbang menolak teks lama SL 5%/SL 10%.)
4. Startup Command server: tambahkan export
   `POLY_PRIVATE_KEY` (diketik pemilik sendiri, jangan dikirim ke
   siapa pun) + `LIVE_TRADING=1`, lalu jalankan `live_loop.py`.
5. **Verifikasi berurutan — jangan loncat:**
   - `python live_loop.py --check` (atau Start tanpa flag):
     gerbang + geoblock + SDK + signer, nol order. Harus exit 0.
   - `python live_loop.py --dry-run`: bangun + tanda tangani order
     dengan kunci nyata, **JANGAN POST**. Harus exit 0, ringkasan
     bertanda `posted: false`.
   - **Live hanya setelah persetujuan eksplisit user tersendiri.**
     Start dengan `--live`. Stop kapan saja lewat tombol Stop panel.
6. Pantau `state/loop.log`: setiap keputusan, SKIP, dan error ada
   alasannya. Bila loop berhenti karena kill-switch, **jangan
   Start ulang buta** — periksa posisi manual dulu, lalu reset state
   bila perlu.

## Batasan yang masih terbuka (jujur)

- **Order wiring belum pernah dieksekusi dengan kunci nyata.**
  DRY-RUN di host adalah pembuktian pertama (bangun + tanda tangan,
  tanpa POST). Live posting baru setelah DRY-RUN lolos + persetujuan
  eksplisit.
- **Harga isi (fill) riil bisa berbeda dari harga order.** Biaya entry
  dicatat di harga order (ask) + estimasi fee; P&L adalah estimasi
  bersih fee, bukan angka pasti bursa. Perbaikan masa depan: baca
  harga isi pasti dari `list_trades`.
- **Bukti posisi bersifat best-effort.** Posisi CLOB berjangkar pada
  proxy wallet; kueri dari signer bisa kosong — karena itu posisi
  hanya dipakai sebagai bukti pendukung, bukan satu-satunya penentu
  (penentu utama = order book + respons).
- **Verifikasi jual memakai harga bid saat keputusan** untuk hasil
  (bukan nominal making/taking respons, yang semantiknya belum
  terdokumentasi pasti di SDK).
- **DRY-RUN melewati gerbang sinyal** (ia tidak membeli) — sinyal
  nyata baru diuji di live.
- **Tidak ada pembatalan order limit yang menggantung di luar loop.**
  Bila loop mati saat order limit menggantung, pemilik memeriksa
  manual sebelum Start ulang (state PENDING tersimpan).
- **Likuiditas $1:** sisi dengan ask tinggi (mis. ~$0,50) tidak muat
  min order 5 + fee → di-SKIP. Itu benar, bukan bug.
- **Server gratis:** tanpa auto-restart, tanpa jaminan uptime dari
  panel. Login 10 hari adalah tanggung jawab pemilik.
