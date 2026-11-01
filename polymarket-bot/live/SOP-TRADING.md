# SOP TRADING — Bot Live Polymarket

**Berlaku untuk:** bot live Polymarket (`live_run.py` di folder ini).
**Status:** parameter live disetujui pemilik 2026-11-01 (lihat §1).
Persetujuan parameter BUKAN perintah mulai trading — trading baru
jalan setelah seluruh checklist pra-start §2 lolos.

**Prinsip utama:** tidak ada pasar yang mudah ditebak pasti. Yang
bot kerjakan adalah peluang dari data dan kabar nyata, bukan
jaminan menang. Dokumen ini tidak menjanjikan profit apa pun.

---

## 1. Parameter yang disetujui (JANGAN diubah tanpa persetujuan baru)

| Item | Nilai yang disetujui |
|---|---|
| Kategori live | Up/Down, cuaca, bola (3 kategori) |
| Modal | $1,00 per kategori — total $3,00; sisa $0,05 buffer di akun |
| Up/Down | TP +20% jual habis lalu rotasi; SL −5%; kill-switch 15% |
| Cuaca + bola | TP1 +10% jual separuh, TP2 +15% jual sisa; SL −5%; kill-switch 15% |
| Posisi | 1 posisi per kategori |
| Order minimum | 5 lembar (di bawah itu DITOLAK, bukan dibulatkan) |
| Fee | Fee taker diperhitungkan dari `feeSchedule` tiap market |
| Jenis order | Binary/spot saja — tanpa leverage, tanpa margin, tanpa futures |
| Penarikan | TIDAK ADA withdraw otomatis; penarikan manual dan disetujui pemilik |
| Wallet live | Akun utama, alamat publik Polygon: profil/deposit `0xc4bA60A94edBfeF6CD7177B6e6e02b1c2b17B4FB` (dana) + signer `0x911379D40dc42d8198baA4f1b7bB29b71A7d3d72` (identitas trading, yang dicek bot) |
| Dana | USDC jaringan Polygon, sudah ada di akun utama ($3,05) — tanpa transfer tambahan |
| Kredensial | Runtime re-derivation: bot derive ulang tiap jalan dari `POLY_PRIVATE_KEY` di environment host; tidak ada salinan kredensial API yang disimpan, tidak pernah dicetak |

**Aturan saring live (bagian dari persetujuan):** bot hanya membeli
pasar yang berdukung sinyal nyata — cuaca: prakiraan cuaca resmi;
bola: berita tim/form/jadwal; Up/Down: katalis berita yang jelas.
Pasar tanpa sinyal/kabar nyata di-SKIP, walau harganya murah.
Aturan harga termurah ala paper TIDAK berlaku untuk live.

**Prioritas trigger jual:** kill-switch > SL > TP2/TP20 > TP1.
Trigger diukur ask-ke-ask; hasil jual dihitung di bid.

---

## 2. Checklist pra-start (semua harus CENTANG sebelum Start)

- [ ] **Parameter = §1.** `params.json` dan `LIVE_APPROVED.txt`
      di folder bot sesuai persetujuan di atas, bukan contoh.
      `params.example.json` TIDAK PERNAH dipakai sebagai params live.
- [ ] **Private key siap di host.** `POLY_PRIVATE_KEY` diketik
      pemilik sendiri ke environment mesin host. Tidak pernah
      dikirim lewat chat, tidak pernah ditulis di repo, tidak
      pernah difoto. Kunci yang pernah terekspos harus dirotasi
      dulu sebelum dipakai live.
- [ ] **SDK terpasang.** `pip install -r requirements.txt`
      (`polymarket-client`) sudah jalan di host.
- [ ] **CHECK lolos.** `python3 live_run.py` (mode CHECK) melaporkan:
      private key ada, SDK terpasang, Gamma terbaca, params lolos
      — dengan nol order dan nol nilai rahasia tercetak.
- [ ] **Geoblock lolos DARI HOST.** `GET polymarket.com/api/geoblock`
      dari egress host yang akan menjalankan bot menyatakan
      allowed. Cek dari laptop TIDAK membuktikan host diizinkan.
      Bila blocked: PINDAHKAN proses, JANGAN pakai VPN/proxy
      untuk mengakali blokir geografis.
- [ ] **Saldo cukup.** Saldo akun utama ≥ $3,00 + buffer fee.
      Bila saldo kurang, JANGAN kurangi modal per kategori secara
      diam-diam — itu perubahan parameter (§7).
- [ ] **Wiring order terverifikasi di host.** Antarmuka order SDK
      sudah dibuktikan di host sebelum order pertama. Paket ini
      sengaja BERHENTI pada verifikasi state dan tidak menempatkan
      order sampai wiring itu terverifikasi.
- [ ] **Host tidak mengganggu loop lain.** Host Polymarket
      terpisah dari server loop Indodax. Bila suatu saat keduanya
      berbagi satu host: JANGAN ubah Startup Command loop yang
      sedang jalan — perubahan Startup menghentikan loop itu.
      Sampai jendela restart terencana (§5), server yang sedang
      jalan TIDAK diutak-atik.
- [ ] **Loop Indodax terpantau.** Bila ada jendela restart yang
      menyentuh server loop Indodax, catat waktunya: selama
      jendela itu posisi Indodax tanpa penjaga.

Bila SATU saja kotak tidak centang: JANGAN Start. Perbaiki dulu,
lalu ulang checklist dari awal.

---

## 3. Aturan runtime (selama bot jalan)

1. Bot hanya berjalan di dalam parameter §1. Tidak ada posisi kedua
   per kategori, tidak ada leverage, tidak ada order di luar
   kategori yang disetujui.
2. Bot hanya membeli pasar yang lolos aturan saring (§1). Tanpa
   prakiraan/berita/katalis = tidak beli.
3. Bot tidak pernah menarik dana (withdraw) sendiri.
4. Pemilik boleh menekan **Stop kapan saja** — menghentikan bot
   adalah hak pemilik, bukan kegagalan.
5. JANGAN ubah Startup Command, file parameter, atau file
   persetujuan saat loop live sedang jalan. Perubahan apa pun
   menunggu loop berhenti (§7).
6. JANGAN membuka panel/host lain untuk "memperbaiki" posisi yang
   sedang dijaga bot tanpa mencatatnya (§6) — dua pengendali
   bersamaan menyebabkan double order.

---

## 4. Monitoring (apa dicek, kapan)

**Setiap Start — verifikasi dari console (output saja, potong
bagian atas yang menampilkan perintah):**

- Yang harus muncul: private key ada (nama saja), SDK terpasang,
  gerbang lolos, dan "Kredensial berhasil diturunkan via SDK
  (nilai tidak dicetak, hanya di memori proses ini)".
- Baris persetujuan tercatat cocok dengan §1.
- Baris posisi terpantau: harga bid vs entry, persentase, dan
  status HOLD / TP / SL / KS.

**Selama jalan — cek console berkala:**

- Posisi masih terpantau (baris update tiap poll) dan status
  server tetap Online.
- Tidak ada baris error berulang. Satu baris error = catat dan
  amati; error berulang = hentikan loop dan masuk §5.
- Setiap TP/SL/KS yang tersentuh: pastikan ada baris jual dan
  verifikasi saldonya (§6), bukan sekadar baris trigger.

**Yang TIDAK perlu dicek tiap menit:** harga pasar di luar console
bot — bot yang memantau, bukan pemilik.

---

## 5. Respons insiden

### Loop berhenti / server Offline

1. JANGAN langsung tekan Start ulang.
2. Buka console, baca baris terakhir SEBELUM "Server marked as
   offline". Baris itu adalah diagnosis (contoh: gerbang gagal,
   kunci tidak terdeteksi, SDK tidak terpasang, error API).
3. Perbaiki penyebabnya sesuai baris itu, lalu Start ulang dan
   verifikasi seperti §4.
4. Bila penyebab tidak jelas dari console, laporkan baris-baris
   console (output saja, tanpa perintah) untuk diagnosis — jangan
   menebak-nebak dan jangan Start buta berulang.

### Respons error order

**ATURAN BESI — pelajaran dari kasus Indodax: respons error TIDAK
SAMA DENGAN tidak terisi.** Sebuah order pernah terisi penuh
padahal responsnya error. Karena itu:

1. Setelah respons error order apa pun: JANGAN retry otomatis,
   JANGAN kirim order pengganti.
2. Verifikasi dulu dari saldo dan riwayat order (order histories)
   apakah order itu terisi, terisi sebagian, atau tidak terisi.
3. Bot berhenti (ABORT_NO_RETRY) dan menyerahkan keputusan kepada
   pemilik. Tindakan berikutnya HANYA setelah verifikasi manual
   tercatat (§6).

### Kill-switch tersentuh

1. Loop menjual SEMUA posisi kategori itu dan BERHENTI untuk
   kategori tersebut.
2. Jangan nyalakan ulang kategori itu di hari yang sama tanpa
   persetujuan baru (§7) dan catatan penyebabnya (§6).

### Geoblock berubah menjadi blocked

1. Hentikan loop. Jangan pakai VPN/proxy.
2. Pindahkan proses ke host yang diizinkan, ulang checklist §2
   dari awal.

### Kunci terekspos (chat / screenshot / file)

1. Anggap kunci itu bocor. Hentikan loop bila sedang jalan.
2. Rotasi/ganti kunci di sisi penyedia, masukkan kunci baru lewat
   environment host saja, ulang checklist §2.
3. Hapus pesan/screenshot yang memuat kunci bila masih bisa.

---

## 6. Pencatatan (setiap keputusan/trade tercatat)

Setiap kejadian berikut dicatat (tanggal + jam WIB + nilai +
alasan), di ledger bot dan/atau catatan operasi:

- Persetujuan parameter dan setiap perubahannya (§7).
- Setiap BUY: kategori, market, sisi, harga, jumlah lembar, fee,
  dan sinyal yang meloloskannya (prakiraan/berita/katalis apa).
- Setiap SELL: trigger (TP1/TP2/TP20/SL/KS), harga bid, hasil.
- Setiap SKIP: market yang di-skip karena tanpa sinyal/kabar.
- Setiap error: responsnya, hasil verifikasi saldo/order history,
  dan keputusan lanjutannya.
- Setiap Start/Stop/restart: siapa yang menekan, mengapa, dan
  hasil verifikasi console sesudahnya.

**Tanpa catatan = tidak terjadi.** Keputusan yang tidak tercatat
tidak boleh dijadikan dasar perubahan parameter berikutnya.

---

## 7. Kontrol perubahan

- Mengubah parameter apa pun di §1 (kategori, modal, TP, SL,
  kill-switch, aturan saring) = PERSETUJUAN BARU dari pemilik.
  Tulis persetujuan baru (tanggal + nilai baru), buat
  `LIVE_APPROVED.txt` + `params.json` baru, ulang checklist §2.
- Mengubah kode bot = tes ulang penuh (`test_live.py` lolos
  semua) + CHECK mode lolos + verifikasi wiring di host, sebelum
  Start berikutnya.
- Mengubah host = ulang checklist §2 dari awal, termasuk cek
  geoblock dari egress host baru.
- Versi dokumen ini ikut dicatat saat berubah: perubahan SOP
  tanpa persetujuan pemilik tidak berlaku.

---

## 8. Yang SOP ini TIDAK janjikan

- Tidak ada jaminan profit, tidak ada pasar yang "pasti untung".
  Up/Down jangka pendek mendekati 50/50 dikurangi fee dan spread;
  cuaca dan bola pun hanya peluang dari data, bukan kepastian.
- Tidak ada klaim "nol bug selamanya". Yang dijanjikan SOP ini
  hanyalah: gerbang yang fail-closed, tidak ada retry buta, tidak
  ada withdraw otomatis, dan setiap keputusan tercatat sehingga
  bisa diaudit.
- Bila ada pihak yang menjanjikan profit pasti dari bot ini,
  abaikan — itu bukan bagian dari SOP ini.
