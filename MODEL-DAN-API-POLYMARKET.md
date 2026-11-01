# Model AI Tertutup vs Open + API Key Polymarket Sampai ke Akar

Dokumen ini menjawab tuntas: apakah model Claude (Fable, Opus, Mythos) dan OpenAI (GPT-6 Astra, Sol, Luna) itu open source, apa itu "Neurobro", repo open source apa yang sepadan, dan bagaimana sebenarnya cara kerja API key Polymarket. Snapshot riset: 1 November 2026. Nama model dan harga berubah cepat — cek ulang sumber resmi sebelum keluar uang.

> Catatan cara baca: klaim yang diverifikasi dari halaman resmi ditulis apa adanya; klaim dari panduan/berita pihak ketiga ditandai **(sekunder)**. Yang tidak terkonfirmasi ditulis "belum terkonfirmasi", bukan dikarang.

---

## 1. Model Claude — Fable, Opus, Mythos: TIDAK open source

Jawaban singkat: **semua model Claude itu tertutup (proprietary) milik Anthropic.** Bobot modelnya tidak dipublikasikan dan tidak bisa diunduh. Yang bisa dipakai hanya lewat jalur resmi di bawah.

### Lineup saat ini

| Model | Posisi | Siapa bisa pakai |
|---|---|---|
| Claude Fable 5.1 | Paling kuat yang terbuka untuk semua pelanggan; penalaran berat + agen jangka panjang | Semua pelanggan |
| Claude Opus 5.5 | Coding agen jangka panjang + knowledge work | Semua pelanggan |
| Claude Sonnet 5.5 | Kombinasi kecepatan + kecerdasan terbaik (seimbang) | Semua pelanggan |
| Claude Haiku 5.5 | Tugas bervolume tinggi, cepat, murah (klasifikasi, ekstraksi, routing) | Semua pelanggan |
| Claude Mythos 5.1 | Model yang sama dengan Fable 5.1 tapi dengan sebagian safeguard dilonggarkan | Hanya organisasi terverifikasi lewat program trusted-access Anthropic |

Sumber lineup: panduan nama model Anthropic yang memverifikasi ke halaman model Anthropic (per Oktober 2026) — Fable 5.1, Opus 5.5, Sonnet 5.5, Haiku 5.5 sebagai model saat ini, plus Mythos 5.1 hanya untuk organisasi terverifikasi.

- https://nightschoolai.com/anthropic-model-names-explained
- https://www.lindy.ai/blog/what-is-claude-ai

### Jalur akses resmi

1. **claude.ai** — chatbot web/aplikasi (ada paket gratis + berbayar).
2. **API Anthropic** — untuk developer, pakai API key Anthropic.
3. **Amazon Bedrock** — Claude lewat cloud AWS.
4. **Google Cloud Vertex AI** — Claude lewat cloud Google.
5. **Microsoft Foundry** — juga tercatat sebagai penyedia (sekunder).

### Apa artinya "tertutup" di sini

- **Bobot tidak dirilis.** "Anthropic does not publish Claude weights. All Claude usage requires an API key" — dan semua inferensi berjalan di infrastruktur Anthropic atau mitra cloud yang disetujui, bukan di mesin sendiri.
  - https://kilo.ai/models/by/anthropic
  - https://www.lowcode.agency/blog/claude-vs-llama
- **Tidak ada repo GitHub resmi berisi modelnya.** Yang ada di GitHub hanya perkakas di sekitar model (SDK, contoh kode, plugin) — bukan bobot atau kode pelatihan model itu sendiri. Jadi kalau ada repo mengklaim "Claude open source", itu bukan Claude asli.
- **Harga API (sekunder, Oktober 2026, per 1 juta token input/output):** Haiku 5.5 $0,10/$0,50 (naik jadi $0,50/$2,50 untuk prompt di atas 100 ribu token), Sonnet 5.5 $2/$10, Opus 5.5 $4/$20, Fable 5.1 $10/$50.
  - https://unfilteredai.medium.com/which-claude-model-to-use-haiku-sonnet-opus-or-fable-and-how-to-stop-hitting-your-limit-44828c6a6920

### Kesimpulan bagian ini

Claude = bayar per pemakaian lewat API/chatbot/mitra cloud. Tidak bisa di-self-host, tidak bisa diunduh, tidak bisa dimasukkan ke repo sebagai model. Untuk keperluan trading agent gratis, Claude bukan jalurnya — jalurnya adalah model open-weight di bagian 4.

---

## 2. Model OpenAI — GPT-6 Astra, GPT-6.1 Sol, GPT-6 Luna: TIDAK open source

Jawaban singkat: **ketiga model GPT-6 itu tertutup milik OpenAI.** Ketiganya terkonfirmasi namanya dalam pengumuman Google Cloud 21 Oktober 2026 (bukan sekadar rumor) — tapi semuanya tetap closed-source.

### Tiga modelnya (per pengumuman Google Cloud, 21 Oktober 2026)

| Model | Peran menurut Google Cloud |
|---|---|
| GPT-6 Astra | Pekerjaan berat: coding, computer use, pekerjaan profesional, riset ilmiah |
| GPT-6.1 Sol | Kecerdasan mendekati Astra dengan biaya lebih rendah (agentic coding, computer use, pekerjaan profesional) |
| GPT-6 Luna | Cepat dan hemat biaya untuk pekerjaan sehari-hari dalam volume besar |

Status akses saat pengumuman: **private preview untuk pelanggan enterprise terpilih** di Google Cloud Model Garden, dibeli lewat Google Cloud Marketplace dan ditagih dalam satu invoice Google Cloud. Harga publik belum diumumkan saat itu, dan general availability direncanakan "dalam beberapa minggu ke depan" (per laporan Oktober 2026). Microsoft tetap mitra cloud utama OpenAI; model yang sama juga tersedia lewat Azure, AWS Bedrock, dan Oracle (sekunder).

- https://www.unite.ai/google-cloud-adds-openais-gpt-astra-and-gpt-6-models-to-model-garden/
- https://www.neoteo.com/en/openais-gpt-6-models-enter-google-cloud-private-preview
- https://www.gurujicorp.org/blog/openai-google-cloud-model-garden-2026.html

### Bukti "tertutup"-nya

- Google sendiri menyebut ketiganya sebagai "leading closed source LLMs" dalam pengumumannya (sekunder, mengutip post Google).
- "The weights remain closed — GPT-6 Astra, Sol, and Luna are served through APIs, never downloaded." Bobot tidak pernah bisa diunduh; yang ada hanya akses API.
  - https://forkast.news/openai-models-land-on-google-cloud-frontier-distribution-goes-multi-cloud-while-the-watts-stay-exclusive/
- Satu varian penulisan nama: sebagian sumber menulis "GPT-Astra" (tanpa angka 6). Modelnya sama; dokumen ini memakai "GPT-6 Astra" karena itu penulisan mayoritas.

### Pengecualian penting: OpenAI PUNYA model open-weight sungguhan

Jangan sampai ketukar: di luar keluarga GPT-6 yang tertutup, OpenAI merilis **gpt-oss-120b dan gpt-oss-20b** — dan ini benar-benar open-weight:

- **Lisensi Apache 2.0** (boleh dipakai, diubah, didistribusikan, termasuk komersial, tunduk pada usage policy gpt-oss).
- **Tidak tersedia lewat API OpenAI maupun ChatGPT** — hanya bisa jalan di infrastruktur sendiri atau hosting provider.
- **Ukuran:** gpt-oss-120b muat di satu GPU 80 GB (mis. H100); gpt-oss-20b jalan di sekitar 16 GB memori.
- **Cara jalan:** stack inferensi terbuka umum seperti vLLM, Ollama, dan llama.cpp.

Sumber resmi OpenAI:

- https://help.openai.com/en/articles/11870455-openai-open-weight-models-gpt-oss
- https://docs.api.nvidia.com/nim/reference/openai-gpt-oss-20b

### Kesimpulan bagian ini

GPT-6 Astra/Sol/Luna = API berbayar, tertutup, dan saat riset ini masih private preview di Google Cloud. Kalau mau "rasa OpenAI" tapi gratis dan bisa diunduh, yang benar adalah **gpt-oss**, bukan GPT-6.

---

## 3. Istilah "Neurobro": BUKAN model fondasi seperti Claude/GPT

Hasil pencarian sampai ke akar: **tidak ada model fondasi bernama "Neurobro" yang setara dengan Claude atau GPT.** Yang ditemukan dengan nama itu adalah produk lain — dan ini penting supaya tidak salah beli/salah pasang.

### Yang benar-benar ditemukan bernama Neurobro

**Neurobro (neurobro.ai)** adalah ekosistem trading berbasis AI untuk trader ritel, bukan model bahasa:

- Aplikasi mobile + platform web + terminal untuk riset pasar (kripto, saham, forex, komoditas).
- NeuroWallet (wallet non-custodial bawaan) dan NeuroAPI (akses REST ke "otak" Neurobro).
- **Nevron**: framework agen AI open-source berbahasa Python dari tim Neurobro (organisasi GitHub axioma-ai-labs) — ini framework agen, bukan model fondasi.
- Ada token kripto **BRO** yang terkait proyek ini — token bukan model, dan bukan investasi.

Sumber:

- https://neurobro.ai/products/
- https://axioma-ai-labs.github.io/nevron/
- https://holder.io/coins/bro-8-13/gbp/rate/ (sekunder: deskripsi ekosistem + GitHub axioma-ai-labs)

### Kehati-hatian soal Neurobro

- CertiK mencatat proyek ini **tidak diaudit dan tidak terverifikasi oleh CertiK** (sekunder).
- Satu tracker pihak ketiga menandai aktivitas GitHub organisasinya rendah (sekunder, tidak pasti) — jadi jangan anggap proyek ini matang hanya karena namanya mirip "neuro" + "bro".
- Intinya: Neurobro tidak bisa menggantikan Claude/GPT sebagai "otak" bot. Kalau tujuannya cari model, lihat bagian 4.

### Kandidat lain yang dicek (karena bunyinya mirip)

| Kandidat | Hasil |
|---|---|
| **Nemotron (NVIDIA)** | ADA dan nyata — keluarga model open-weight NVIDIA (lihat bagian 4). Paling mungkin jadi maksud ucapan kalau yang didengar mirip "neuro". |
| **"Model baru" (salah dengar voice-to-text)** | Hipotesis yang belum terbukti — tidak ada bukti mengaitkan frasa ini ke satu proyek spesifik. Ditulis sebagai hipotesis saja, bukan kesimpulan. |
| **NeuroCode / NeuroCore** | Proyek solo/tidak terkait yang muncul di pencarian — bukan model fondasi, tidak relevan. |

**Verdict bagian ini: "Neurobro" sebagai model = tidak teridentifikasi.** Yang ada adalah ekosistem trading Neurobro + framework Nevron. Kalau yang dimaksud user adalah sesuatu yang lain (mis. dari satu video/postingan tertentu), kirim link/frame sumbernya supaya bisa diverifikasi langsung.

---

## 4. Repo open source "seperti" model-model di atas (ringkas + cross-reference)

Bagian ini sengaja singkat: detail tool agen sudah lengkap di dokumen evaluasi repo (`EVALUASI-TOOLS-TRADING-AGENT.md`), jadi di sini hanya peta model + cara jalan gratisnya, tanpa duplikasi.

### Istilah yang wajib diluruskan dulu

**"Open-weight" ≠ "open source" strict.** Menurut definisi Open Source AI (OSI), open source sejati menuntut kebebasan pakai, pelajari, ubah, dan bagikan, plus informasi soal data latih dan kode. Kebanyakan model populer hanya "open-weight": bobotnya bisa diunduh dan dijalankan, tunduk pada lisensi masing-masing. Untuk urusan legal, yang penting adalah isi file lisensi checkpoint yang diunduh, bukan labelnya.

### Model open-weight yang benar-benar bisa diunduh

| Keluarga | Pembuat | Lisensi (per panduan sekunder, Okt 2026 — cek file lisensi checkpoint) |
|---|---|---|
| gpt-oss-120b / 20b | OpenAI | Apache 2.0 (resmi, lihat bagian 2) |
| Qwen (mis. Qwen3.x) | Alibaba | Apache 2.0 |
| Mistral (mis. Mistral Small/Large) | Mistral AI | Apache 2.0 |
| Gemma (mis. Gemma 4) | Google | Apache 2.0 |
| DeepSeek (mis. DeepSeek V4) | DeepSeek | MIT |
| Llama | Meta | Lisensi komunitas custom — menurut OSI ini BUKAN open source (ada batasan pemakaian + acceptable use policy) |
| Nemotron 3 | NVIDIA | Lisensi NVIDIA Open Model (custom, bukan Apache/MIT) untuk bobot; kode Apache 2.0. Ada klausul: lisensi gugur otomatis bila guardrail model diakali tanpa perlindungan pengganti yang sepadan |
| Nemotron 3.5 Bolt | NVIDIA | OpenMDW-1.1 |

Sumber sekunder (rangkuman lisensi dari kartu model resmi, Oktober 2026):

- https://www.cognativ.com/blog/open-source-ai-models-local-deployment/
- https://www.emergentmind.com/topics/nemotron-3-family
- https://catalog.ngc.nvidia.com/orgs/nim/nvidia/models/nemotron-3.5-bolt-e4b-4gb/-

### Cara jalan gratis di mesin sendiri

| Runner | Cocok untuk | Lisensi / biaya |
|---|---|---|
| **Ollama** | Paling cepat mulai (satu perintah, CLI + API) | MIT, gratis |
| **LM Studio** | Paling mudah (aplikasi desktop, klik-klik, chat window) | Gratis dipakai (proprietary) |
| **llama.cpp** | Mesin mentah di balik banyak runner; kontrol penuh, jalan di CPU juga | MIT, gratis |
| **vLLM** | Serving produksi (throughput tinggi, multi-user) | Apache 2.0, gratis |

Semua runner di atas mengekspos endpoint yang kompatibel dengan API OpenAI, jadi kode yang biasa memanggil API OpenAI bisa diarahkan ke URL lokal. Setelah model diunduh sekali, model jalan offline — satu-satunya biaya adalah listrik dan perangkat yang sudah dimiliki (sekunder).

- https://induwara.lk/tools/ai-local-llm-runtime-comparison
- https://aurigait.com/blog/how-to-run-an-llm-locally/

### Framework agen open source (cross-reference, tidak diduplikasi)

Untuk kerangka agennya (bukan modelnya), pakai hasil evaluasi yang sudah ada di repo: **Open Code, Aider, eliza, OpenAlice, Vibe-Trading**, dan kawan-kawan — lengkap dengan verdict PAKAI/PERTIMBANGKAN/LEWATI di `EVALUASI-TOOLS-TRADING-AGENT.md`. Pola yang disarankan: model open-weight lokal (bagian atas) + framework agen dari dokumen evaluasi + paper trading dulu. Jangan pasang model tertutup berbayar sebagai fondasi kalau syaratnya "alat harus gratis".

---

## 5. API Key Polymarket sampai ke akar

### Poin 0: Polymarket TIDAK punya "API key" gaya signup biasa

Tidak ada halaman dashboard tempat kamu klik "Create API Key" seperti di OpenAI atau Anthropic. Yang ada adalah **kredensial yang diturunkan dari wallet** (lihat alur di bawah). Dan kabar baiknya: **membaca data publik tidak butuh key sama sekali** — market discovery (Gamma), order book dan harga (CLOB), serta posisi publik (Data API) bisa diakses tanpa kredensial. Kredensial baru dibutuhkan saat trading (order privat).

Tiga API Polymarket (sekunder, dari dokumentasi resmi):

| API | Host | Fungsi | Butuh key? |
|---|---|---|---|
| Gamma | gamma-api.polymarket.com | Cari market/event + metadata | Tidak (baca publik) |
| CLOB | clob.polymarket.com | Order book, harga, pasang/batal order | Ya, untuk order privat |
| Data API | data-api.polymarket.com | Posisi, riwayat trade, holder, open interest | Tidak (baca publik) |

### Poin 1: Alur auth dua lapis (L1 + L2) — ini "akarnya"

**Lapis 1 (L1) — buktikan kamu pemilik wallet.** Wallet menandatangani pesan EIP-712 dengan private key, secara lokal, tanpa pernah mengirim private key itu ke server mana pun:

- Domain pesan: `ClobAuthDomain`, versi `1`, chain ID `137` (Polygon).
- Isi pesan (`ClobAuth`): alamat wallet, timestamp, nonce (default `0`), dan kalimat tetap: *"This message attests that I control the given wallet"*.
- Header L1: `POLY_ADDRESS`, `POLY_SIGNATURE`, `POLY_TIMESTAMP`, `POLY_NONCE`.
- Endpoint: `POST /auth/api-key` (buat kredensial baru) atau `GET /auth/derive-api-key` (turunkan kredensial yang sudah ada).
- Hasilnya: **tiga kredensial L2: apiKey + secret + passphrase**.

**Lapis 2 (L2) — tandatangani tiap request privat.** Setiap request privat (pasang order, batal order, dsb.) ditandatangani HMAC-SHA256 memakai secret, atas gabungan timestamp + method HTTP (huruf besar) + path + body persis. Header L2:

- `POLY_ADDRESS`, `POLY_SIGNATURE` (tanda tangan HMAC), `POLY_TIMESTAMP`, `POLY_API_KEY`, `POLY_PASSPHRASE`.

**Order itu sendiri masih ditandatangani wallet secara terpisah** (tanda tangan order ≠ tanda tangan request L2). Jadi totalnya ada tiga tanda tangan yang berperan: L1 (sekali, untuk melahirkan kredensial), L2 (tiap request privat), dan tanda tangan order (tiap order).

Kenapa dua lapis? Supaya bot sehari-hari hanya memakai kredensial L2, **tanpa mengekspos private key di tiap trade**. Private key hanya dipakai sekali saat L1.

Sumber:

- https://docs.polymarket.com/developers/CLOB/quickstart.md (resmi, dicek langsung)
- https://predictionhero.com/insights/polymarket-api-guide (sekunder: detail L1/L2, endpoint, header)
- https://blog.predictefy.com/polymarket-api-key (sekunder: triple kredensial, "keep all secrets server-side")

### Poin 2: SDK yang benar dipakai sekarang (JANGAN py-clob-client)

- **SDK terpadu resmi saat ini:** paket Python `polymarket-client` dan paket TypeScript `@polymarket/client` (repo GitHub Polymarket/py-sdk). Contoh resmi Python: `AsyncSecureClient.create` dengan private key + alamat wallet dari environment; contoh TypeScript: `createSecureClient` dari `@polymarket/client`.
  - https://docs.polymarket.com/developers/CLOB/quickstart.md
- **JANGAN pakai `py-clob-client`.** Repo itu diarsipkan dan tidak fungsional; README-nya sendiri mengarahkan migrasi ke SDK baru. Alur order V1-nya sudah tidak diterima produksi sejak CLOB V2 live (28 April 2026). `py-clob-client-v2` sempat jadi jembatan V2, tapi panduan terbaru mengarahkan proyek baru ke SDK terpadu.
  - https://launchpoly.com/blog/polymarket-api-complete-guide (sekunder)
  - https://agentbets.ai/compare/kalshi-vs-polymarket/ (sekunder)

### Poin 3: Dana dan gas

- **Trading berjalan di Polygon (chain ID 137).** Secara historis, kolateral Polymarket adalah **USDC di Polygon**, dan gas jaringan Polygon dibayar dengan **POL**.
- **Perubahan penting 2026 (wajib cek ulang):** panduan 2026 menyebut CLOB V2 (live 28 April 2026) memakai token kolateral baru **pUSD**, dan quickstart resmi terbaru (dicek 1 November 2026) mencontohkan "siapkan setidaknya 10 pUSD" sebelum order pertama. Artinya: **sebelum isi dana untuk live, cek halaman deposit resmi saat itu juga** — jangan berasumsi kolateralnya masih USDC.
- **Gas-less hanya lewat jalur khusus (sekunder):** transaksi tanpa gas hanya tersedia bila memakai proxy wallet + relayer Polygon Polymarket. Kalau pakai wallet EOA biasa sebagai akun trading, wallet itu harus didanai untuk trading sekaligus membayar gas.
- **Opsi lanjutan (resmi, dari quickstart):** session keys — signer terpisah yang bisa pasang/batal order tanpa memakai owner key. Berguna untuk bot, tapi pelajari halaman session keys resmi dulu sebelum dipakai.

### Poin 4: Hubungan dengan dokumen evaluasi

Modul venue Polymarket di stack evaluasi (`EVALUASI-TOOLS-TRADING-AGENT.md`) memakai pola yang sama: **poly-maker** (market-making + mode paper) atau **polymarket-terminal** (strategi jadi + simulasi) sebagai modul venue, dengan SDK terpadu baru bila perlu integrasi sendiri. Yang dilewati di sana tetap dilewati di sini: py-clob-client dan Polymarket/agents yang diarsipkan.

> ⚠️ **KOTAK PERINGATAN KEAMANAN — API KEY POLYMARKET (WAJIB DIBACA SEBELUM LIVE)**
>
> 1. **Private key wallet, apiKey, secret, dan passphrase TIDAK PERNAH masuk chat, TIDAK PERNAH masuk repo publik, dan TIDAK PERNAH disimpan Muse.** Polanya sama persis seperti key Indodax: hanya di environment mesin/server milik user sendiri.
> 2. **Pakai wallet khusus bot, terpisah dari simpanan utama, dengan dana kecil saja.** Wallet bot ini yang menandatangani L1 dan memegang dana trading. Jangan pernah memakai wallet simpanan utama untuk bot.
> 3. **Private key hanya menandatangani secara lokal.** Private key tidak pernah dikirim ke Polymarket atau ke server aplikasi mana pun — yang dikirim hanya tanda tangannya (L1) dan tanda tangan HMAC (L2). Kalau ada tutorial yang memintamu menempel private key ke formulir web/chat/repo, itu tidak aman — berhenti.
> 4. **Kalau kredensial bocor, segera cabut dan ganti.** Turunkan ulang kredensial dari wallet yang aman (derive ulang), pindahkan dana dari wallet yang terekspos, dan anggap kredensial lama sudah tidak aman. Jangan menunggu.
> 5. **Paper/simulator dulu, tanpa kecuali.** Tidak ada order nyata tanpa persetujuan eksplisit user dengan parameter yang disetujui — sama seperti gerbang live Indodax.
> 6. **Jangan mengakali blokir geografis.** Polymarket punya jalur internasional (Polygon) dan jalur AS yang teregulasi (CFTC, KYC, settlement USD). Pengguna di Indonesia memakai jalur internasional; memakai VPN untuk mengakses jalur yang diblokir melanggar ketentuan layanan.

---

## Tabel ringkas: Tertutup vs Open

| Model / proyek | Pembuat | Status | Akses |
|---|---|---|---|
| Claude Fable 5.1, Opus 5.5, Sonnet 5.5, Haiku 5.5 | Anthropic | **Tertutup** | claude.ai, API Anthropic, Bedrock, Vertex AI |
| Claude Mythos 5.1 | Anthropic | **Tertutup** (terbatas) | Hanya organisasi terverifikasi (trusted-access) |
| GPT-6 Astra, GPT-6.1 Sol, GPT-6 Luna | OpenAI | **Tertutup** | ChatGPT/API OpenAI, Google Cloud Model Garden (private preview), Azure/AWS/Oracle |
| gpt-oss-120b / 20b | OpenAI | **Open-weight** (Apache 2.0) | Unduh + jalan lokal (vLLM/Ollama/llama.cpp) |
| Llama | Meta | **Open-weight**, lisensi custom (bukan OSI open source) | Unduh + jalan lokal |
| Qwen, Mistral, Gemma | Alibaba, Mistral AI, Google | **Open-weight** (Apache 2.0, per sekunder) | Unduh + jalan lokal |
| DeepSeek | DeepSeek | **Open-weight** (MIT, per sekunder) | Unduh + jalan lokal |
| Nemotron 3 / 3.5 Bolt | NVIDIA | **Open-weight** (lisensi NVIDIA / OpenMDW-1.1) | Unduh + jalan lokal |
| Neurobro | axioma-ai-labs | **Bukan model** — ekosistem trading + token + framework Nevron | neurobro.ai (produk, bukan bobot model) |

---

## Masih belum jelas

1. **GPT-6.1 Terra:** satu daftar sekunder menyebutnya sebagai model flagship keempat (bersama Astra, Sol, Luna), tapi namanya tidak muncul dalam liputan pengumuman Google 21 Oktober 2026 — statusnya belum terkonfirmasi, tidak diselidiki lebih jauh di dokumen ini.
2. **Kolateral Polymarket untuk akun baru:** quickstart resmi terbaru mencontohkan pUSD, sementara materi lama memakai USDC. Kepastiannya harus dicek di halaman deposit resmi pada saat integrasi.
3. **"Neurobro" versi user:** kalau yang dimaksud user adalah sumber spesifik (video/postingan tertentu), kirim link/frame-nya — pencarian umum hanya menemukan ekosistem trading Neurobro, bukan model.
4. **Harga dan ketersediaan GPT-6 di Google Cloud:** saat pengecekan sekunder 27 Oktober 2026, belum ada harga publik dan akses masih private preview (formulir minat tidak menjamin akses).
5. **Detail lisensi per checkpoint:** tabel bagian 4 memakai rangkuman sekunder — selalu baca file lisensi checkpoint yang diunduh sebelum dipakai komersial.
6. **Session keys Polymarket:** hanya disebut sebagai opsi lanjutan dari quickstart resmi; detail implementasinya belum didalami di dokumen ini.

---

## Tambahan: API Polymarket dari docs resmi (dibaca 1 Nov 2026)

Sumber: https://docs.polymarket.com/getting-started/api dan https://docs.polymarket.com/api-reference/predictions/overview

### Daftar API (host)

| API | Host | Fungsi | Butuh key? |
|---|---|---|---|
| Gamma | gamma-api.polymarket.com | Cari event/market + metadata | Tidak (publik) |
| CLOB | clob.polymarket.com | State market live, pasang/kelola order | Ya, untuk order privat |
| Data API | data-api.polymarket.com | Aktivitas akun & market setelah trading (v2: cursor pagination + envelope respons bersama) | Tidak untuk baca publik |
| Relayer | relayer-v2.polymarket.com | Kirim transaksi wallet yang didukung TANPA harus memegang POL untuk gas | — |
| WebSocket | — | Stream realtime: market, account, sports, RFQ events | Channel market publik tanpa key; channel akun butuh kredensial L2 |
| Bridge | bridge.polymarket.com | Isi dana & tarik dana pakai aset yang didukung | — |

### Yang dikonfirmasi ulang dari docs resmi

- Auth tetap dua lapis: L1 (wallet tanda tangan EIP-712 → buat/turunkan kredensial) + L2 (HMAC-SHA256, header POLY_ADDRESS, POLY_SIGNATURE, POLY_TIMESTAMP, POLY_API_KEY, POLY_PASSPHRASE). Order memakai L2 + tanda tangan wallet terpisah.
- Docs menyarankan pakai SDK resmi bila runtime didukung; integrasi langsung (REST/WebSocket mentah) dipakai bila runtime tidak didukung SDK, butuh kontrol penuh atas signing/header/retry, atau endpoint belum ada di SDK.
- Sebelum integrasi, docs mengingatkan dua hal: (1) rate limit per service/endpoint — wajib dicek, (2) geographic restrictions — cek di mana order placement tersedia (pengguna Indonesia memakai jalur internasional; tanpa VPN untuk mengakali blokir).

### Kaitannya dengan persiapan bot kita

- Demo/paper saat ini sudah benar jalurnya: Gamma + baca CLOB publik (tanpa key).
- Live nanti: kredensial L2 dari wallet khusus bot sendiri (bukan key temuan), funding lewat Bridge (cek kolateral saat itu: USDC vs pUSD), Relayer sebagai opsi bila tidak mau pegang POL untuk gas, WebSocket sebagai pengganti polling untuk harga/book realtime (keputusan lebih cepat), Data API v2 untuk posisi/riwayat.
- Detail nama channel WebSocket tidak tampil di teks kedua halaman ini — hanya kategorinya (market, account, sports, RFQ). Bila modul WebSocket dibangun, baca halaman CLOB WebSocket docs secara khusus.

---

## Tambahan: repo pihak ketiga bitquery/polymarket-api (dibaca 1 Nov 2026)

Sumber: https://github.com/bitquery/polymarket-api

**Apa ini (dan apa bukan):** SDK Node.js (npm `polymarket-api`) dari Bitquery untuk menarik DATA Polymarket lewat GraphQL Bitquery — BUKAN API resmi Polymarket dan BUKAN SDK resmi (yang resmi: `polymarket-client` Python / `@polymarket/client` TypeScript). Judulnya "polymarket-api" sehingga mudah dikira resmi — ini contoh persis soal judul vs isi.

**Fakta repo (terverifikasi dari halaman GitHub):** publik, tidak diarsipkan, bukan fork; 9 bintang, 6 fork, 5 commit, dibuat 20 Nov 2025; lisensi ISC; JavaScript/Node.js (TypeScript-ready).

**Fungsi (hanya baca data, TIDAK bisa order):** query + stream (WebSocket) untuk: market/question baru, prediksi yang sudah resolved, position splits, payout per alamat, semua trade, trade per token, trade per user. Cocok untuk: discovery market baru, tracking resolusi, monitoring trade user tertentu (whale), payout tracking.

**Syarat pakai:** butuh Bitquery OAuth token (daftar akun Bitquery gratis + ambil access token). Jadi ini menambah dependensi pihak ketiga + token + rate limit Bitquery sendiri — berbeda dari API publik resmi Polymarket (Gamma/CLOB baca publik) yang tanpa key. Akun gratis ada, tapi limitnya wajib dicek sebelum dipakai di loop (README sendiri mengingatkan rate limiting + retry logic).

**Verdict: PERTIMBANGKAN sebagai pelengkap data saja, bukan fondasi.** Alasan: (1) read-only — tidak menggantikan CLOB untuk eksekusi live; (2) pihak ketiga — datanya lewat GraphQL Bitquery, bukan sumber resmi; (3) komunitas kecil (9 bintang, 5 commit) — risiko maintenance; (4) stack kita Python stdlib — SDK ini Node.js, jadi pemakaiannya sebagai service terpisah atau referensi query GraphQL, bukan plug-in langsung. Yang paling berguna buat kita: streamResolvedQuestions (deteksi resolusi market lebih cepat daripada polling Gamma) dan getTradesByUser (pantau whale). Token Bitquery pun sama aturannya: hanya di environment mesin sendiri, tidak pernah di chat/repo.

---

## Tambahan: panduan Dwellir (sekunder, dibaca 1 Nov 2026)

Sumber: https://www.dwellir.com/guides/polymarket-api-guide

**Nilai:** panduan sekunder yang bagus dan konsisten dengan docs resmi (penulis mengklaim public reads dicek langsung ke live API). Poin-poin yang menambah dokumen ini:

- Tabel key yang jelas: tanpa key (Gamma, Data API, harga/book CLOB, market WebSocket); kredensial CLOB turunan wallet (order, user WebSocket); Relayer API key (Settings → API Keys → Relayer, untuk operasi gasless); Builder API key (Settings → Builders, untuk membuat Deposit Wallet bagi user sendiri — BUKAN untuk trading akun sendiri); Polymarket US Key ID + Secret (portal polymarket.us/developer setelah KYC, exchange terpisah).
- Geoblock: endpoint GET polymarket.com/api/geoblock mengembalikan blocked/country/region/ip; dicek dari server yang akan mengirim order (bukan laptop); bila blocked, pindahkan proses ke server di region yang diizinkan — ini pilihan deployment, BUKAN VPN untuk mengakali blokir.
- Praktik order: butuh tick_size + neg_risk dari market; contoh client memakai PRIVATE_KEY dari environment + create_or_derive_api_key(); funder + signature_type (0 bare, 1 Proxy, 2 Safe; akun Deposit Wallet per 4 Mei 2026 memakai SecureClient SDK terpadu).
- CLOB V2 (28 Apr 2026): kolateral pUSD, order signing berubah, legacy py-clob-client pensiun; panduan memakai py-clob-client-v2 tapi mencatat SDK terpadu polymarket-client yang direkomendasikan untuk proyek baru.
- Catatan produk: panduan ini dari penyedia RPC Dwellir dan mempromosikan dashboard-nya (free Polygon key via DWELLIR_POLYGON_URL) untuk baca on-chain (saldo, settlement). RPC key itu terpisah dari kredensial Polymarket; API resmi (Gamma/CLOB/Data) tidak butuh RPC. Bila butuh baca on-chain, RPC publik lain juga bisa — tidak wajib Dwellir.
- Pesan keamanan yang sejalan: "Keep the secret and passphrase on your server."

**Verdict: PAKAI sebagai referensi sekunder** (di bawah docs resmi). Tidak ada yang bertentangan dengan dokumen ini; ia justru memperjelas bedanya Builder key vs kredensial CLOB — beda yang dikacaukan panduan Traderbotz di bawah.

---

## Tambahan: panduan Traderbotz (DITOLAK — jangan diikuti)

Sumber: https://www.traderbotz.com/how-to/api-keys/polymarket/

**Apa ini:** halaman how-to dari platform bot pihak ketiga (TraderBotz), bukan docs resmi. Isinya bermasalah dan bertentangan dengan docs resmi + aturan keamanan kita:

1. **Mengacaukan Builder key dengan kredensial trading.** Halaman ini menyuruh ambil "Builder API key" dari portal developer lalu ditempel ke TraderBotz untuk trading. Padahal Builder key gunanya membuat Deposit Wallet bagi user sendiri, BUKAN trading akun sendiri di CLOB. Kredensial trading CLOB adalah triple turunan wallet (L1→L2), hal yang berbeda.
2. **Klaim "satu key untuk US dan World" itu salah.** Polymarket US adalah exchange terpisah (CFTC) dengan Key ID + Secret sendiri (signature Ed25519) yang TIDAK berlaku di CLOB polymarket.com — ditegaskan panduan Dwellir dan docs resmi.
3. **Menyuruh VPN untuk live world-scope.** Halaman ini menyatakan bot live world-scope butuh VPN (cloud VPN engine / WireGuard self-hosted). Itu persis pengakalan blokir geografis yang TIDAK kita lakukan. Jalur yang benar: cek geoblock dari server, dan bila blocked, jangan trading dari sana — bukan VPN.
4. **Penitipan kredensial ke pihak ketiga.** Halaman ini menyuruh menempel key + secret ke TraderBotz ("stored encrypted"). Aturan kita: kredensial hanya di environment mesin/server sendiri, tidak pernah dititipkan ke platform pihak ketiga, chat, email, atau repo.

**Verdict: LEWATI.** Jangan pakai TraderBotz, jangan tempel kredensial ke sana, jangan pakai VPN untuk trading world-scope. Halaman ini dicantumkan di sini sebagai contoh panduan pihak ketiga yang menyesatkan, supaya tidak ada yang mengikutinya diam-diam.
