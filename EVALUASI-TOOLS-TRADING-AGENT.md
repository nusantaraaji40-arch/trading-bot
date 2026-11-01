# Evaluasi Tools & Repo untuk AI Assistant Trading Agent

Dokumen ini mengevaluasi SEMUA tools/repo dari materi yang dikirim user (carousel TikTok, video, screenshot) untuk keperluan membangun **AI assistant trading agent** milik user. Tidak ada yang dilewati: duplikat digabung, yang tidak teridentifikasi ditulis apa adanya (bukan dikarang).

> Catatan: dokumen ini ditulis agar bisa dipindah mentah-mentah ke repo `trading-bot` sebagai dokumen evaluasi. Dokumen pendamping batch pertama ada di `REFERENSI-AI-TRADING.md` (file saudara di repo yang sama).

## Kriteria penilaian

1. **Gratis / open source saja.** Tanpa langganan berbayar. Dibedakan jelas antara "kode gratis" (lisensi open source) vs "butuh API berbayar untuk jalan" (tool-nya gratis, tapi pemakaian model LLM-nya bayar per token).
2. **Relevansi untuk AI assistant TRADING AGENT** (bukan sekadar chatbot): framework agent, memori, riset, backtest, eksekusi, monitoring, sandbox, kompres konteks, RAG, prompt/tooling. Nilai: **TINGGI / SEDANG / RENDAH**.
3. **Portabilitas multi-host.** User memakai hosting beda-beda (VPS kecil seperti Wispbyte 512 MB, laptop, dst). Dicatat: bisa self-host/Docker? butuh GPU? butuh RAM besar? terkunci ke satu cloud/host? Cocok untuk VPS kecil atau tidak?
4. **Risiko dicatat.** Termasuk: repo diarsipkan/tidak di-maintain, kode belum diaudit, menyentuh private key/wallet, copy trading (mengikuti trader lain), telemetri default, dan framing proyek yang sensitif.

## Cara verifikasi

- Angka bintang, lisensi, dan status arsip **diverifikasi langsung dari halaman GitHub** masing-masing repo (fetch 1 November 2026, ~09:19–09:24 UTC). Angka slide/carousel **tidak** dipakai — beberapa terbukti kedaluwarsa atau salah (contoh: Open Code diklaim 156k, faktanya 223.691; org Vibe-Trading di video lama salah; org LangAlpha dan OpenMontage salah satu huruf).
- Bila repo tidak ditemukan di URL yang diklaim, ditulis "tidak ditemukan" dan dicari lokasi pindahnya; bila tetap tidak ketemu, masuk daftar BELUM JELAS.
- **Batasan fetch yang jujur:** hasil fetch halaman GitHub **tidak menampilkan panel bahasa** untuk repo mana pun, jadi kolom bahasa di dokumen ini ditulis "tidak tampil di hasil fetch" untuk semua item — bukan ditebak dari ekstensi file. Di mana README secara eksplisit menyebut stack, itu dicatat terpisah sebagai "indikasi README".
- **Batasan materi:** gambar/video batch tambahan tidak tersedia sebagai file di sesi riset ini, jadi inventaris batch tambahan bersandar pada checklist materi + verifikasi live tiap repo yang teridentifikasi. Item yang tidak bisa dikaitkan ke repo mana pun ditulis "belum teridentifikasi dari frame", bukan dikarang.
- Angka bintang adalah snapshot saat fetch dan bisa berubah. Catatan dari sumber sekunder (bukan dari halaman repo) selalu ditandai sebagai "catatan sekunder".
- **Screening gambar 1 Nov 2026:** 157 file gambar batch 16:17–16:20 WIB dibaca satu per satu (audit trail di `SCREENING.md` di working copy; 6 duplikat digabung, 0 gagal baca). Item baru di bagian G diverifikasi lewat GitHub API (snapshot 1 Nov 2026, ~10:00–10:10 UTC); satu repo (ComfyUI, G45) diverifikasi lewat fetch halaman repo karena API pencarian tidak mengembalikannya. Klaim angka di gambar tidak dipakai sebagai fakta.

## Format tiap entri

Nama + link GitHub, fungsi (1–2 kalimat), bahasa, lisensi, bintang terverifikasi, biaya, relevansi, portabilitas, verdict (**PAKAI / PERTIMBANGKAN / LEWATI**).

---

## A. Carousel OpensourceID — verdict singkat

Batch ini SUDAH didokumentasikan lengkap di `REFERENSI-AI-TRADING.md` (9 repo + 1 bonus, bintang sesuai video). Di bawah ini hanya verdict singkat per item + koreksi dari verifikasi ulang. Dua item yang dulu 404 (Vibe-Trading, LangAlpha) kini teridentifikasi dan mendapat entri lengkap di sini.

### A1. TradingAgents — https://github.com/TauricResearch/TradingAgents
- **Fungsi:** Framework multi-agen LLM untuk trading finansial (riset, debat agen, keputusan).
- **Bahasa:** tidak tampil di hasil fetch. **Lisensi:** Apache-2.0. **Bintang terverifikasi:** 119.198.
- **Biaya:** kode gratis; jalan butuh API LLM berbayar.
- **Relevansi:** TINGGI — kerangka agen trading paling terkenal, tapi fokus riset (README: bukan saran finansial/trading).
- **Portabilitas:** Python, self-host; ringan untuk riset, tapi biaya LLM yang jadi beban.
- **Verdict:** PERTIMBANGKAN — referensi desain multi-agen terbaik; bukan eksekutor siap pakai.

### A2. FinRobot — https://github.com/AI4Finance-Foundation/FinRobot
- **Fungsi:** Platform agen AI open source untuk aplikasi finansial berbasis LLM.
- **Bahasa:** tidak tampil di hasil fetch. **Lisensi:** Apache-2.0. **Bintang terverifikasi:** 8.347.
- **Biaya:** kode gratis; jalan butuh API LLM berbayar.
- **Relevansi:** SEDANG — platform agen finansial umum; V0 edukasi (bukan produksi), V1 web app, V2 desktop (disebut production system), V3 dalam pengembangan.
- **Portabilitas:** V2 desktop (macOS Apple Silicon saja, belum notarized) — kurang cocok untuk VPS kecil.
- **Verdict:** PERTIMBANGKAN — pantau V2/V3; bukan fondasi utama saat ini.

### A3. FinGPT — https://github.com/AI4Finance-Foundation/FinGPT
- **Fungsi:** Model bahasa besar finansial open source (bukan agen eksekusi).
- **Bahasa:** tidak tampil di hasil fetch. **Lisensi:** MIT. **Bintang terverifikasi:** 21.504.
- **Biaya:** kode gratis; inferensi butuh GPU/API bila model besar dipakai.
- **Relevansi:** SEDANG — model finansial, bukan agent framework; "What's New" README terakhir tampil November 2023 (observasi saja, bukan vonis tak di-maintain).
- **Portabilitas:** butuh resource besar untuk model penuh; tidak cocok VPS 512 MB.
- **Verdict:** PERTIMBANGKAN — sebagai referensi model finansial, bukan komponen bot.

### A4. Qlib — https://github.com/microsoft/qlib
- **Fungsi:** Platform investasi kuantitatif berorientasi AI (riset factor, backtest, eksekusi workflow).
- **Bahasa:** tidak tampil di hasil fetch. **Lisensi:** MIT. **Bintang terverifikasi:** 49.886.
- **Biaya:** kode gratis; jalan tanpa LLM (komputasi lokal).
- **Relevansi:** TINGGI — tulang punggung riset quant: data, factor, model, backtest.
- **Portabilitas:** Python; berjalan di laptop/VPS menengah; peringatan README: ada perubahan artifact-loading yang tidak backward-compatible (loading dibatasi default; cek izin writer/storage sebelum `trusted=True`).
- **Verdict:** PAKAI — modul riset quant utama (bersama skfolio untuk risiko).

### A5. FinRL — https://github.com/AI4Finance-Foundation/FinRL
- **Fungsi:** Framework reinforcement learning untuk trading finansial.
- **Bahasa:** tidak tampil di hasil fetch. **Lisensi:** MIT. **Bintang terverifikasi:** 16.939.
- **Biaya:** kode gratis; training RL butuh komputasi (GPU membantu, tidak wajib untuk skala kecil).
- **Relevansi:** TINGGI untuk riset RL trading; README mengarahkan sistem modern/produksi ke FinRL-X / FinRL-Trading, repo ini dipertahankan untuk edukasi/riset klasik.
- **Portabilitas:** Python; training berat tidak cocok VPS 512 MB, inferensi ringan bisa.
- **Verdict:** PERTIMBANGKAN — untuk riset RL; produksi lihat FinRL-X.

### A6. ai-hedge-fund — https://github.com/virattt/ai-hedge-fund
- **Fungsi:** Tim agen AI hedge fund (proof of concept): 12 persona investor berdebat lalu mengambil keputusan.
- **Bahasa:** tidak tampil di hasil fetch. **Lisensi:** MIT. **Bintang terverifikasi:** 64.408.
- **Biaya:** kode gratis; jalan butuh API LLM berbayar.
- **Relevansi:** TINGGI — pola multi-agen + paper mode; disclaimer: edukasi/riset saja, sistem ini **tidak benar-benar trading** (tidak place real trade — deliberate).
- **Portabilitas:** Python, self-host; ringan (yang berat hanya biaya LLM).
- **Verdict:** PAKAI — referensi desain tim agen + paper mode; jangan dikira eksekutor.

### A7. Hummingbot — https://github.com/hummingbot/hummingbot
- **Fungsi:** Software open source untuk membuat dan menjalankan bot trading kripto frekuensi tinggi; ada harness AI "Condor" untuk strategi agentic.
- **Bahasa:** tidak tampil di hasil fetch. **Lisensi:** Apache-2.0. **Bintang terverifikasi:** 20.887.
- **Biaya:** kode gratis; jalan tanpa LLM (strategi klasik) atau dengan LLM bila pakai Condor.
- **Relevansi:** TINGGI — eksekusi kripto nyata + backtest; fokus HFT/market-making, bukan spot santai.
- **Portabilitas:** Docker; berjalan di VPS kecil untuk strategi ringan.
- **Verdict:** PERTIMBANGKAN — eksekutor kripto serius; gabung dengan Freqtrade, jangan pakai keduanya sekaligus tanpa alasan.

### A8. Vibe-Trading — https://github.com/HKUDS/Vibe-Trading — ENTRI LENGKAP
- **Fungsi:** "Your Personal Trading Agent" — agen trading multi-agen yang bisa self-improving, backtesting, dan lintas pasar.
- **Bahasa:** tidak tampil di hasil fetch (indikasi README: Python; topik mencakup `mcp`, `multi-agent`). **Lisensi:** MIT. **Bintang terverifikasi:** 37.322 (forks 6.036).
- **Biaya:** kode gratis; jalan butuh API LLM berbayar untuk bagian agennya.
- **Relevansi:** TINGGI — agen trading mandiri + backtest + lintas pasar; README menyebut konektor MT5, mode TAP untuk isolasi kredensial, dan Docker.
- **Portabilitas:** Docker; self-host; cek bobot resource sebelum live di VPS 512 MB.
- **Verdict:** PAKAI — kandidat kerangka agen trading utama. **Koreksi penting:** org yang benar adalah **HKUDS**, bukan NORDU seperti tertulis di video batch lama (URL NORDU 404 — itu sebabnya batch pertama gagal memverifikasi item ini). Carousel lain mengklaim 37.0k stars — terkonfirmasi (kini 37.322).
- **Risiko:** seperti semua agen eksekusi — paper-trade dulu sebelum dana nyata.

### A9. LangAlpha — https://github.com/ginlix-ai/LangAlpha — ENTRI LENGKAP
- **Fungsi:** Harness open source bergaya "Claude Code untuk pasar finansial": agen AI meriset pasar, membangun tesis, dan berdagang di akun broker sendiri dalam batas izin yang ditetapkan user.
- **Bahasa:** tidak tampil di hasil fetch (indikasi README: Python 3.13+). **Lisensi:** Apache-2.0. **Bintang terverifikasi:** 2.220 (forks 373).
- **Biaya:** kode gratis; jalan butuh API LLM berbayar.
- **Relevansi:** TINGGI — agen trading otonom dengan broker nyata; README terbaru mencantumkan agentic trading dengan Robinhood, Interactive Brokers, **moomoo** (paper trading moomoo), dan Webull. Relevan khusus untuk rencana venue Moomoo user.
- **Portabilitas:** self-host; ringan (beban utama biaya LLM).
- **Verdict:** PERTIMBANGKAN — sangat relevan, tapi proyek sangat baru (dibuat 2026-01-18) dan ada alert sekunder CVE-2026-109440 (prompt injection) untuk versi ≤2026.09.07 — **wajib cek/patch sebelum pemakaian live apa pun**. **Koreksi penting:** org yang benar adalah **ginlix-ai** (dengan huruf "l" tambahan), bukan `ginix-ai` seperti di slide lama (URL lama 404).

### A10. pensource.id.lol — https://pensource.id.lol
- **Fungsi:** situs kurasi (bukan repo GitHub) — isinya tidak bisa dilaporkan karena fetch gagal.
- **Bahasa/lisensi/bintang:** tidak berlaku (bukan repo); status fetch: **tetap gagal diverifikasi** (tool fetch gagal tanpa status HTTP, percobaan ulang tidak dilakukan sesuai aturan; bukan bukti situs mati).
- **Biaya:** tidak diketahui.
- **Relevansi:** RENDAH untuk trading agent (kurasi, bukan tool).
- **Portabilitas:** tidak berlaku.
- **Verdict:** LEWATI — sampai isinya bisa diverifikasi lewat browser live; bukan komponen apa pun.

---

## B. Carousel regularbasis.studio — "7 open source AI tools"

**Catatan jujur (TERSELESAIKAN lewat screening gambar 1 Nov 2026):** judul carousel bilang 7 tool, tapi set ini hanya berisi **6 tool**. Buktinya dari slide bernomor: cover 01/08 + 6 slide tool 02/08–07/08 + penutup 08/08. **Slide ke-7 (07/08) adalah Archon (B6)** — terkonfirmasi di slice C screening (file temp_image_623A8657…). Jadi tidak ada tool ke-7 yang hilang; judul "7" kelebihan hitung. Item ini DIHAPUS dari daftar BELUM JELAS.

### B1. BrowserUse — https://github.com/browser-use/browser-use
- **Fungsi:** Library Python open source untuk agen browser AI (agen yang menjelajah dan bertindak di web).
- **Bahasa:** tidak tampil di hasil fetch. **Lisensi:** MIT. **Bintang terverifikasi:** 119.720.
- **Biaya:** library gratis (MIT); produk cloud-nya berbayar (README menyebut $0,02/jam browser) — pakai library self-host, bukan cloud.
- **Relevansi:** SEDANG — berguna untuk riset web otomatis (ambil data situs, pantau halaman), bukan inti trading.
- **Portabilitas:** Python; browser headless butuh RAM lebih dari skrip biasa; masih oke di laptop/VPS menengah, mepet di 512 MB bila banyak tab.
- **Verdict:** PERTIMBANGKAN — modul riset web opsional.

### B2. Dify — https://github.com/langgenius/dify
- **Fungsi:** Platform untuk membangun workflow agentic dan pipeline RAG dengan dukungan banyak model/tool dalam satu workspace kolaboratif; bisa cloud, VPC, atau self-host.
- **Bahasa:** tidak tampil di hasil fetch. **Lisensi:** sidebar GitHub "Other (NOASSERTION)" — README menjelaskan Dify Open Source License, berbasis Apache 2.0 **dengan syarat tambahan** (bukan Apache-2.0 murni).
- **Bintang terverifikasi:** 160.134.
- **Biaya:** kode gratis; jalan butuh API LLM berbayar (atau model lokal).
- **Relevansi:** TINGGI — orkestrasi agen + RAG dalam satu tempat; cocok sebagai "papan kontrol" analis.
- **Portabilitas:** self-host via Docker + database (Postgres, Redis, dsb) — **tidak cocok VPS 512 MB**; cocok laptop/VPS menengah ke atas.
- **Verdict:** PERTIMBANGKAN — bagus untuk orkestrasi, tapi jangan dipaksakan ke VPS kecil; alternatif ringan: rakit sendiri dari mem0 + GPT Researcher.

### B3. GPT Researcher — https://github.com/assafelovic/gpt-researcher
- **Fungsi:** Agen otonom yang melakukan riset mendalam atas topik apa pun memakai LLM apa pun.
- **Bahasa:** tidak tampil di hasil fetch. **Lisensi:** Apache-2.0. **Bintang terverifikasi:** 30.412.
- **Biaya:** kode gratis; jalan butuh API LLM berbayar (atau model lokal).
- **Relevansi:** TINGGI — modul riset untuk analis trading (berita, laporan, sentimen) sebelum keputusan.
- **Portabilitas:** Python, self-host; ringan (beban utama biaya LLM).
- **Verdict:** PAKAI — modul riset analis.

### B4. Docling — https://github.com/docling-project/docling
- **Fungsi:** "Get your documents ready for gen AI" — mengubah dokumen (PDF, dsb) menjadi data siap pakai untuk AI.
- **Bahasa:** tidak tampil di hasil fetch. **Lisensi:** MIT. **Bintang terverifikasi:** 69.941.
- **Biaya:** kode gratis; jalan lokal tanpa LLM.
- **Relevansi:** SEDANG — parsing laporan/whitepaper/dokumen untuk RAG analis.
- **Portabilitas:** Python 3.10+ (dukungan Python 3.9 dihentikan di docling 2.70.0); proyek di bawah LF AI & Data Foundation, dimulai IBM Research Zurich.
- **Verdict:** PERTIMBANGKAN — dipakai bila analis butuh baca dokumen berat; kalau hanya RSS/berita, tidak wajib.
- **Catatan gabung:** URL lama `DS4SD/docling` me-redirect ke `docling-project/docling` (bintang/commit/fork identik). Carousel @adityagnwann memakai URL baru yang sama — **satu tool, dihitung sekali**.

### B5. Storm — https://github.com/stanford-oval/storm
- **Fungsi:** Sistem kurasi pengetahuan berbasis LLM yang meriset topik dan menghasilkan laporan panjang berbukti (dengan sitasi).
- **Bahasa:** tidak tampil di hasil fetch. **Lisensi:** MIT. **Bintang terverifikasi:** 31.762.
- **Biaya:** kode gratis; jalan butuh API LLM berbayar.
- **Relevansi:** SEDANG — riset mendalam untuk laporan pasar; tumpang tindih dengan GPT Researcher.
- **Portabilitas:** Python, self-host; ringan (beban utama biaya LLM).
- **Verdict:** PERTIMBANGKAN — pilih salah satu dari GPT Researcher vs Storm untuk riset, jangan keduanya.
- **Observasi (bukan vonis):** entri "Latest News" README terakhir bertanggal 2025/01.

### B6. Archon — https://github.com/coleam00/archon
- **Fungsi:** "Harness builder" open source pertama untuk AI coding — membuat coding AI deterministik dan bisa diulang.
- **Bahasa:** tidak tampil di hasil fetch. **Lisensi:** MIT. **Bintang terverifikasi:** 23.794.
- **Biaya:** kode gratis; jalan butuh API LLM berbayar.
- **Relevansi:** SEDANG — tooling untuk membangun/mengelola agen coding (termasuk RAG di versi lama), bukan komponen trading.
- **Portabilitas:** self-host; versi saat ini berubah total — versi Python lama (task management + RAG) hanya tersimpan di branch `archive/v1-task-management-rag`; branch default adalah `dev`, bukan `main`.
- **Verdict:** PERTIMBANGKAN — untuk disiplin pengembangan bot; perhatikan telemetri (ada bagian Telemetry di README; opt-out via `ARCHON_TELEMETRY_DISABLED=1` / `DO_NOT_TRACK=1`).

---

## C. Carousel @adityagnwann — 15 item (Docling digabung ke B4)

### C1. hermes-agent — https://github.com/NousResearch/hermes-agent
- **Fungsi:** Agen yang "tumbuh bersama user" — agen self-improving dengan learning loop bawaan.
- **Bahasa:** tidak tampil di hasil fetch. **Lisensi:** MIT. **Bintang terverifikasi:** 259.301.
- **Biaya:** kode gratis; jalan butuh API LLM berbayar (atau model lokal Hermes).
- **Relevansi:** TINGGI — pola memori + belajar dari pengalaman agen; bisa diadopsi untuk agen trading yang belajar dari trade sebelumnya.
- **Portabilitas:** self-host; ringan (beban utama biaya LLM).
- **Verdict:** PERTIMBANGKAN — pola belajarnya berharga; sebagai fondasi agen umum, bersaing dengan eliza (lihat E4).

### C2. OpenSpec — https://github.com/Fission-AI/OpenSpec
- **Fungsi:** Spec-driven development (SDD) untuk AI coding assistant — tulis spesifikasi dulu, agen yang mengerjakan.
- **Bahasa:** tidak tampil di hasil fetch. **Lisensi:** MIT. **Bintang terverifikasi:** 73.563.
- **Biaya:** kode gratis; jalan butuh API LLM berbayar (via coding agent).
- **Relevansi:** SEDANG — disiplin pengembangan: spesifikasi strategi/risiko sebelum kode bot ditulis.
- **Portabilitas:** ringan; jalan di mana saja coding agent jalan.
- **Verdict:** PERTIMBANGKAN — pakai bersama spec-kit (C12) pilih salah satu; OpenSpec lebih fokus ke workflow SDD.

### C3. caveman — https://github.com/JuliusBrussee/caveman
- **Fungsi:** Skill + proxy viral untuk coding agent yang memangkas pemakaian token hingga 65% dengan gaya bicara "caveman".
- **Bahasa:** tidak tampil di hasil fetch. **Lisensi:** Apache-2.0 (panel; root juga punya file LICENSE dan LICENSE-MIT). **Bintang terverifikasi:** 116.592.
- **Biaya:** kode gratis; justru menghemat biaya LLM.
- **Relevansi:** SEDANG — kompres/hemat konteks untuk agen; gaya bicara "caveman" adalah gimmick, nilai nyatanya di pemangkasan token.
- **Portabilitas:** ringan; proxy lokal.
- **Verdict:** PERTIMBANGKAN — hemat biaya; tapi untuk trading agent, headroom (C7) lebih tepat sasaran (kompres output tool/log/RAG).

### C4. Scrapling — https://github.com/D4Vinci/Scrapling
- **Fungsi:** Framework web scraping adaptif — dari satu request sampai crawl skala penuh.
- **Bahasa:** tidak tampil di hasil fetch. **Lisensi:** BSD-3-Clause. **Bintang terverifikasi:** 91.297.
- **Biaya:** kode gratis; jalan lokal.
- **Relevansi:** SEDANG — ambil data web untuk riset (harga, berita, halaman proyek) bila API resmi tidak ada.
- **Portabilitas:** Python; ringan sampai menengah tergantung skala crawl.
- **Verdict:** PERTIMBANGKAN — cadangan bila sumber data tidak punya API; hormati robots/ToS sumber.

### C5. PageIndex — https://github.com/VectifyAI/PageIndex
- **Fungsi:** "Document Index for vectorless reasoning-based RAG" — RAG berbasis penalaran tanpa vektor.
- **Bahasa:** tidak tampil di hasil fetch. **Lisensi:** MIT. **Bintang terverifikasi:** 39.936.
- **Biaya:** kode gratis; jalan butuh API LLM berbayar untuk penalaran.
- **Relevansi:** SEDANG — alternatif RAG dokumen untuk analis (tanpa database vektor).
- **Portabilitas:** ringan; self-host.
- **Verdict:** PERTIMBANGKAN — bila RAG vektor terasa berat, ini alternatif; jangan dipakai bersama Dify sekaligus tanpa alasan.

### C6. mem0 — https://github.com/mem0ai/mem0
- **Fungsi:** Lapisan memori untuk agen AI — infrastruktur memori drop-in agar konteks agen bertahan antar sesi.
- **Bahasa:** tidak tampil di hasil fetch. **Lisensi:** Apache-2.0. **Bintang terverifikasi:** 68.201.
- **Biaya:** kode gratis; ada opsi cloud berbayar — pakai self-host agar tetap gratis.
- **Relevansi:** TINGGI — agen trading butuh ingat: posisi lama, alasan trade, kesalahan masa lalu, preferensi user. Tanpa memori, agen mengulang kesalahan yang sama.
- **Portabilitas:** self-host tersedia; ringan.
- **Verdict:** PAKAI — lapisan memori utama agen trading.

### C7. headroom — https://github.com/headroomlabs-ai/headroom
- **Fungsi:** Mengompres output tool, log, file, dan chunk RAG sebelum sampai ke LLM — menghemat token dengan jawaban yang sama.
- **Bahasa:** tidak tampil di hasil fetch. **Lisensi:** Apache-2.0. **Bintang terverifikasi:** 78.496.
- **Biaya:** kode gratis; justru menghemat biaya LLM.
- **Relevansi:** TINGGI — agen trading rakus konteks (order book, log, berita); kompres konteks = biaya turun + respons lebih cepat (user minta keputusan cepat).
- **Portabilitas:** ringan; self-host.
- **Verdict:** PAKAI — kompres konteks utama; pasangan alami mem0.

### C8. Daytona — https://github.com/daytonaio/daytona
- **Fungsi:** Infrastruktur aman dan elastis untuk menjalankan kode hasil AI (sandbox eksekusi).
- **Bahasa:** tidak tampil di hasil fetch. **Lisensi:** tidak terdeteksi API GitHub 1 Nov 2026 (README hanya menautkan file LICENSE tanpa menyebut tipenya).
- **Bintang terverifikasi:** 71.411.
- **Biaya:** kode gratis (saat masih di-maintain).
- **Relevansi:** SEDANG — sandbox untuk eksekusi kode agen; relevan untuk keamanan, bukan untuk trading itu sendiri.
- **Portabilitas:** infrastruktur berat (butuh orkestrasi kontainer) — bukan untuk VPS 512 MB.
- **Verdict:** LEWATI — **peringatan besar: repo berstatus "Public archive", banner README: "This repository is no longer maintained. As of June 2026, Daytona's core development has moved to a private codebase. This repository will receive no further updates, fixes, or releases."** Jangan jadikan dependensi baru tanpa rencana fork/dukungan sendiri.

### C9. TrendRadar — https://github.com/sansan0/TrendRadar
- **Fungsi:** Monitor opini publik & tren berbasis AI dengan agregasi multi-platform, RSS, dan smart alert.
- **Bahasa:** tidak tampil di hasil fetch. **Lisensi:** GPL-3.0. **Bintang terverifikasi:** 63.340.
- **Biaya:** kode gratis; jalan butuh API LLM berbayar untuk bagian AI-nya.
- **Relevansi:** SEDANG — sentimen/tren pasar untuk analis (pelengkap berita, bukan sinyal beli/jual mentah).
- **Portabilitas:** self-host; menengah (agregasi multi-platform).
- **Verdict:** PERTIMBANGKAN — modul sentimen opsional; repo bertipe template (bukan peringatan).

### C10. Fabric — https://github.com/danielmiessler/Fabric
- **Fungsi:** Framework open source untuk augmentasi manusia memakai AI lewat sistem prompt modular crowdsourced.
- **Bahasa:** tidak tampil di hasil fetch. **Lisensi:** MIT. **Bintang terverifikasi:** 44.516.
- **Biaya:** kode gratis; jalan butuh API LLM berbayar.
- **Relevansi:** SEDANG — koleksi pola prompt untuk analis (ringkas berita, ekstrak sinyal) — tooling prompt, bukan agen.
- **Portabilitas:** ringan; jalan di mana saja.
- **Verdict:** PERTIMBANGKAN — perpustakaan prompt analis; bukan fondasi.

### C11. spec-kit — https://github.com/github/spec-kit
- **Fungsi:** Toolkit untuk memulai spec-driven development (SDD) atau proses dev lain bersama coding agent.
- **Bahasa:** tidak tampil di hasil fetch. **Lisensi:** MIT. **Bintang terverifikasi:** 144.602.
- **Biaya:** kode gratis; jalan butuh API LLM berbayar (via coding agent).
- **Relevansi:** SEDANG — sama seperti OpenSpec (C2): disiplin spesifikasi sebelum kode.
- **Portabilitas:** ringan.
- **Verdict:** PERTIMBANGKAN — pilih salah satu dari OpenSpec vs spec-kit; spec-kit dari GitHub sendiri, OpenSpec lebih fokus workflow.

### C12. hyperframes — https://github.com/heygen-com/hyperframes
- **Fungsi:** "Write HTML, render video" — dibuat untuk agen (HTML jadi video).
- **Bahasa:** tidak tampil di hasil fetch. **Lisensi:** Apache-2.0. **Bintang terverifikasi:** 76.737.
- **Biaya:** kode gratis; render video butuh komputasi.
- **Relevansi:** RENDAH — produksi video, bukan trading. (Berguna untuk konten affiliate user, bukan untuk bot trading.)
- **Portabilitas:** render video berat — bukan untuk VPS kecil.
- **Verdict:** LEWATI — untuk trading agent. (Boleh dilirik terpisah untuk konten, bukan di stack ini.)

### C13. OpenMontage — https://github.com/calesthio/OpenMontage — ENTRI LENGKAP (koreksi URL)
- **Fungsi:** Sistem produksi video agentic open source pertama: mengubah asisten coding AI menjadi studio video lengkap (riset, naskah, aset, voiceover, editing, render) lewat 12 pipeline produksi.
- **Bahasa:** tidak tampil di hasil fetch. **Lisensi:** AGPL-3.0 (copyleft kuat — relevan bila dipakai sebagai layanan jaringan). **Bintang terverifikasi:** 74.133 (forks 9.723).
- **Biaya:** kode gratis; jalan butuh API LLM + komputasi render.
- **Relevansi:** RENDAH — produksi video, bukan trading.
- **Portabilitas:** berat (render video) — bukan untuk VPS kecil.
- **Verdict:** LEWATI — untuk trading agent. **Koreksi penting:** user yang benar adalah **calesthio** (dengan huruf "h"), bukan `calestio` seperti di slide lama (URL lama 404). Angka bintang di artikel sekunder bervariasi (29K–72.326); angka halaman GitHub saat fetch (74.133) yang dipakai.

### C14. AI Engineering Hub — https://github.com/patchy631/ai-engineering-hub
- **Fungsi:** Tutorial mendalam tentang LLM, RAG, dan aplikasi agen AI dunia nyata.
- **Bahasa:** tidak tampil di hasil fetch. **Lisensi:** MIT. **Bintang terverifikasi:** 39.638.
- **Biaya:** gratis (materi belajar).
- **Relevansi:** SEDANG — bahan belajar membangun agen, bukan komponen yang dijalankan bot.
- **Portabilitas:** tidak berlaku (repo tutorial).
- **Verdict:** PERTIMBANGKAN — sebagai referensi belajar tim; bukan bagian stack runtime.

---

## D. Coding-agent tools — carousel @okaashish, Free Claude Code, OpenClaude, G0d M0d3, day-trader-skill

### D1. Open Code — https://github.com/anomalyco/opencode
- **Fungsi:** "The open source coding agent" — agen coding terminal open-source yang model-agnostic (75+ provider, termasuk model lokal) dengan TUI, aplikasi desktop (beta), dan agen built-in build/plan.
- **Bahasa:** tidak tampil di hasil fetch (sumber sekunder: TypeScript/Bun). **Lisensi:** MIT. **Bintang terverifikasi:** 223.691 (forks 30.060).
- **Biaya:** kode gratis; jalan bisa pakai model lokal gratis atau API berbayar.
- **Relevansi:** SEDANG — ini alat untuk **membangun** bot (coding agent), bukan komponen bot itu sendiri. Nilainya: user bisa membangun/mengubah bot dengan agen ini.
- **Portabilitas:** terminal; ringan; self-host.
- **Verdict:** PERTIMBANGKAN — coding agent utama untuk pengembangan bot.
- **Koreksi & jebakan nama:** klaim carousel "156k stars" sudah kedaluwarsa (kini 223.691, jauh lebih tinggi). Org lama `sst/opencode` pindah nama menjadi Anomaly (path lama redirect). Ada proyek Go lama bernama sama (`opencode-ai/opencode`, kini Crush oleh Charm) yang diarsipkan — **bukan yang ini**.

### D2. Aider — https://github.com/Aider-AI/aider
- **Fungsi:** "AI pair programming in your terminal" — pair programming dengan LLM di terminal, dengan pemetaan codebase, integrasi Git, dan dukungan model cloud maupun lokal.
- **Bahasa:** tidak tampil di hasil fetch. **Lisensi:** Apache-2.0. **Bintang terverifikasi:** 49.866 (forks 5.121).
- **Biaya:** kode gratis; jalan bisa pakai model lokal gratis atau API berbayar.
- **Relevansi:** SEDANG — alat pengembangan bot (pair programming), bukan komponen runtime.
- **Portabilitas:** terminal; ringan.
- **Verdict:** PERTIMBANGKAN — alternatif/pelengkap Open Code untuk coding; pilih salah satu sebagai harian.
- **Catatan sekunder (bukan vonis halaman repo):** beberapa panduan 2026 menyebut rilisnya melambat (rilis terakhir yang dikutip v0.86.x, 2025/awal 2026) — halaman GitHub sendiri tidak menandainya dormant/archived.

### D3. Free Claude Code — https://github.com/Alishahryar1/free-claude-code
- **Fungsi:** Proksi/router open source yang memungkinkan harness coding-agent (Claude Code, Codex, Antigravity, VSCode, Pi, OpenCode, plus 6 harness lain — total 12 di README) dipakai lewat berbagai provider, termasuk tier gratis, dari terminal/aplikasi/IDE/HP/browser.
- **Bahasa:** tidak tampil sebagai label bahasa di hasil fetch (badge README menyebut Python 3.14; direktori `src/free_claude_code` juga Python). **Lisensi:** metadata GitHub "Other (NOASSERTION)" — badge README TIDAK KONSISTEN: satu tangkapan lama menampilkan "License: AGPL v3", sementara frame video Richo (IMG_8350, screening 1 Nov 2026) menampilkan badge "MIT license". **Cek file LICENSE sebelum dipakai serius — label lisensi repo ini tidak bisa dikutip satu versi saja.**
- **Bintang terverifikasi:** 65.557 (forks 10.216).
- **Biaya:** kode gratis; klaim README "1.3B+ free tokens" tergantung provider dan bisa berubah — bukan jaminan gratis tanpa batas.
- **Relevansi:** SEDANG — penghemat biaya harness coding (router ke tier gratis), bukan komponen trading.
- **Portabilitas:** ringan; proxy lokal.
- **Verdict:** PERTIMBANGKAN — berguna untuk menekan biaya coding agent; bukan fondasi trading agent.
- **Hubungan dengan OpenClaude (D4):** BERBEDA, jangan disamakan. Free Claude Code adalah proksi/router yang mengarahkan banyak harness ke banyak provider; OpenClaude adalah satu CLI coding-agent mandiri.
- **Catatan:** screenshot TikTok batch pertama "Free Claude Code" (fabie6) kini teridentifikasi sebagai repo ini — bukan lagi item tak jelas.

### D4. OpenClaude — https://github.com/Gitlawb/openclaude (pemilik saat video; lokasi kini tidak terkonfirmasi)
- **Fungsi:** CLI coding-agent terminal open source multi-model (OpenAI-compatible, Gemini, GitHub Models, Codex, Ollama, dll.) dengan satu workflow terminal: prompt, tools, agents, MCP, slash command, streaming.
- **Bahasa:** tidak tampil di hasil fetch (sumber sekunder: TypeScript). **Lisensi:** metadata GitHub "Other (NOASSERTION)" — sumber sekunder menyebut lisensi MIT berlaku untuk modifikasi komunitas, sementara kode turunan Anthropic tetap milik Anthropic. Status lisensinya tidak sesederhana "MIT murni".
- **Bintang terverifikasi:** 34.236 (forks 9.128).
- **Biaya:** kode gratis; jalan bisa pakai model lokal gratis atau API berbayar.
- **Relevansi:** SEDANG — coding agent seperti Open Code/Aider, bukan komponen trading.
- **Portabilitas:** terminal; ringan.
- **Verdict:** LEWATI — untuk proyek ini, karena: (1) **atribusi video TERBUKTI salah dan kini terkoreksi** — `gnanam1990/openclaude` bukan repo pemiliknya; dua frame independen dari screening 1 Nov 2026 membuktikan pemilik saat video adalah **Gitlawb**: IMG_8322 (Pandu Rijal: header …/openclaude + situs openclaude.gitlawb.com + baris commit "gnanam1990" — gnanam1990 adalah penulis commit terakhir yang tampil, bukan pemilik) dan IMG_8332 (Aditya: header eksplisit "Gitlawb / openclaude"). Pencarian GitHub 1 Nov 2026 TIDAK mengembalikan repo Gitlawb/openclaude maupun Twigpine/openclaude (kemungkinan pindah/dihapus/diprivat; rujukan pihak ketiga ke @twigpine/openclaude tidak mengembalikan repo) — **lokasi repo kini tidak terkonfirmasi**; (2) proyek pindah (paket npm lama `@gitlawb/openclaude` "no longer updated", pindah ke `@twigpine/openclaude`); (3) **risiko legal/kepercayaan menurut sumber sekunder**: proyek ini berangkat dari codebase Claude Code yang bocor lewat npm source map 31 Maret 2026 dan sempat tersangkut isu DMCA terhadap mirror/fork lain; README menyatakan tidak berafiliasi dengan Anthropic. Klaim video "25.4k stars, 8.2k forks" plausibel sebagai angka lama (sumber sekunder mencatat 26,4k/8,4k; 33.282/9.084 per 15 Sep 2026; kini 34.236/9.128). Pakai Open Code atau Aider saja — lebih bersih.

### D5. G0DM0D3 / GOD MODE — https://github.com/elder-plinius/G0DM0D3
- **Fungsi:** "LIBERATED AI CHAT" — antarmuka chat multi-model open source untuk red-teaming, riset kognisi, dan interaksi AI "liberated": 60 model OpenRouter terdaftar + hingga 44 model Venice + model lokal; mode GODMODE CLASSIC (5 kombinasi model+prompt berlomba paralel) dan ULTRAPLINIAN (evaluasi multi-model 12–60 model); ada mesin red-team Parseltongue (33 teknik perturbasi input) dan AutoTune.
- **Bahasa:** tidak tampil di hasil fetch (stack README: inti UI satu file `index.html` vanilla HTML/CSS/JS; opsional frontend React/Next.js di `src/` dan API server Node/Express di `api/`). **Lisensi:** AGPL-3.0 (terverifikasi). **Bintang terverifikasi:** 12.067 (forks 2.825). Tidak diarsipkan. Live di godmod3.ai.
- **Biaya — KOREKSI JUJUR atas klaim video "gratis":** alatnya gratis (AGPL-3.0), tapi **model via OpenRouter itu BAYAR per token** (butuh key OpenRouter/Venice sendiri; model gratis OpenRouter memang ada, tapi tidak semua 50+/60 model gratis). Yang benar-benar gratis hanya jalur model lokal (Ollama, LM Studio, llama.cpp, vLLM). Jangan anggap "akses 50+ model gratis" sebagai gratis tanpa batas.
- **Relevansi:** RENDAH — ini frontend chat multi-model, **bukan alat trading**. Framing proyek adalah riset jailbreak/red-team ("fully jailbroken, no guardrails"; GODMODE CLASSIC memakai "battle-tested jailbreak prompt").
- **Portabilitas:** sangat ringan — inti UI satu `index.html` tanpa build step, bisa dibuka langsung di browser atau di-serve statis; cocok untuk VPS kecil sekalipun.
- **Verdict:** LEWATI — sebagai komponen trading agent. Pemakaian terbatas yang masih masuk akal: frontend multi-model untuk analis membandingkan jawaban beberapa model, **dengan catatan**: biaya API OpenRouter + telemetri (lihat di bawah). Tetap dimasukkan di dokumen ini karena user minta tanpa tersisa.
- **Telemetri (terkonfirmasi README):** telemetri aplikasi berupa metadata aktif secara default (ID sesi acak, timestamp, model/mode/tier, timing, skor, panjang konten, konfigurasi pipeline — **tidak sengaja** mencakup teks prompt, respons, gambar, atau API key). Bisa dimatikan lewat No-Log Mode atau Local-only mode (Local-only juga mengecualikan panggilan OpenRouter/Venice). Perhatian: saat telemetri aktif, prompt mentah sempat dikirim ke model auxilier lewat provider untuk menghasilkan label harm-taxonomy (hanya labelnya yang masuk event telemetri). Riwayat chat tersimpan di `localStorage` browser (tanpa akun/cloud sync).

### D6. day-trader-skill — https://github.com/Jakeschincariol/day-trader-skill
- **Fungsi:** Paket 11 skill Claude untuk day trading saham AS: scan ribuan chart, pantau berita, atur entry/exit, simulasi Time Machine, cek risiko/budget, eksekusi via broker, alert, analis earnings, dan pelacak trade Kongres (Pelosi).
- **Bahasa:** tidak tampil di hasil fetch (sumber sekunder: Python 100%; tools-nya script Python standar). **Lisensi:** MIT. **Bintang terverifikasi:** 4.075 (forks 958).
- **Biaya:** kode gratis; data gratis (Yahoo Finance, Nasdaq Trader, SEC EDGAR, House Clerk); jalan butuh Claude/API LLM; Python 3.8+, tanpa pip install.
- **Relevansi:** TINGGI — bukan karena saham AS-nya (bukan venue user), tapi karena **polanya**: Time Machine ("replays every possible outcome… 10.000 simulated sessions plus every past time the setup fired" — contoh TSLA di README: 10.000 replay dari candle 5-menit 59 sesi terakhir, verdict "close to a coin flip"), risk gate (`/trader-risk` harus PASS), paper trading default, dan "No trade goes through until you say yes" (hanya `/trader-broker` yang bisa mengarah ke order, setelah konfirmasi eksplisit). Pola ini persis yang dibutuhkan bot user: simulasi ribuan outcome + gerbang risiko + paper default + konfirmasi.
- **Portabilitas:** ringan; script Python.
- **Verdict:** PAKAI — sebagai referensi desain (Time Machine + risk gate + paper default), diadaptasi ke venue user (Indodax, Polymarket, Forex, Moomoo, Pump.fun). Bukan bot otomatis: ini skill riset/proses untuk Claude; proyek sangat baru (dibuat 2026-10-20; sumber 23 Okt 2026 mencatat baru 637 stars, kini 4.075). README menegaskan bukan saran finansial.

### D7. Carousel @okaashish #3–#7 — TERSELESAIKAN lewat screening gambar 1 Nov 2026
- Daftar lengkap carousel "7 Alternatives to Claude Code, 100% Free and Local" kini terbukti: **#1 Open Code (D1), #2 Aider (D2), #3 Plandex (G1), #4 Void (G2), #5 Zed (G3), #6 Cline (G4), #7 Kilo Code (G5)**.
- **Rantai bukti:** slide rekap slice C (file temp_image_0124398C…, "SAVE THESE GITHUB REPOS:") mencantumkan ketujuh URL bernomor; slide individual mengonfirmasi #1 (slice C), #4 Void (slice C, 28.7k★ klaim), #5 Zed (slice C, 82.1k★ klaim), #7 Kilo Code (slice C, 19k★ klaim), #2 Aider (slice D, 44.4k★), #3 Plandex (slice D, 15.3k★) dan #6 Cline (slice D, 61.4k★). Kejujuran atribusi: slide #3/#6 di slice D tidak mencetak judul carousel — penautannya via akun @okaashish yang sama + gaya visual + nomor urut yang cocok dengan rekap (bukti kuat, bukan 100% eksplisit); slide #3/#6 juga tidak menampilkan URL GitHub di gambar — URL-nya diverifikasi live lewat API (lihat G1, G4).
- Item ini DIHAPUS dari daftar BELUM JELAS.

---

## E. Agen trading & tools Polymarket

**Peringatan umum bagian ini:** hampir semua tool eksekusi di sini menyentuh private key/wallet bila dipakai live. Aturannya tetap: paper/simulator dulu, kunci trade-only (bukan withdrawal), dan tidak ada order nyata tanpa persetujuan eksplisit user. Copy trading = mengikuti trader lain — risikonya ikut menanggung kesalahan trader itu.

### E1. Nocturne — https://github.com/Gajesh2007/ai-trading-agent
- **Fungsi:** "Nocturne: AI Trading Agent on Hyperliquid" — agen AI memakai LLM untuk menganalisis data pasar real-time dari TAAPI, mengambil keputusan buy/sell/hold, dan mengeksekusi trade di Hyperliquid DEX, berjalan dalam loop kontinu dengan TP/SL.
- **Bahasa:** tidak tampil di hasil fetch (indikasi README: Python — `src/main.py`, `poetry`, Dockerfile). **Lisensi:** tidak terdeteksi API GitHub 1 Nov 2026 (tidak ada file LICENSE) — konsisten dengan catatan lama "tidak tampil di hasil fetch". **Bintang terverifikasi:** 555 (klaim video 543 sudah terlampaui).
- **Biaya:** kode gratis; jalan butuh API: TAAPI + LLM (OpenRouter) berbayar; eksekusi di Hyperliquid butuh dana.
- **Relevansi:** TINGGI — pola agen eksekusi lengkap (analisis → keputusan → eksekusi → TP/SL → loop).
- **Portabilitas:** Docker; Python; self-host.
- **Verdict:** PERTIMBANGKAN — pola loop + TP/SL-nya bisa diadopsi; tapi **peringatan README terkonfirmasi verbatim: "There is no guarantee of any returns. This code has not been audited. Please use at your own risk."** Jangan pakai mentah-mentah untuk dana nyata. **Risiko kunci:** env memakai `HYPERLIQUID_PRIVATE_KEY` untuk eksekusi live. Jangan tertukar dengan `Gajesh2007/ai-trading-agent-v2` (proyek TypeScript terpisah, bukan Nocturne). Catatan: "Nocturne" adalah nama proyek di dalam repo `ai-trading-agent`, bukan nama repo. Hyperliquid bukan venue user saat ini — ambil polanya, bukan venue-nya.

### E2. OpenAlice — https://github.com/TraderAlice/OpenAlice
- **Fungsi:** "Your one-person Wall Street" — orkestrator AI untuk trading saham, kripto, komoditas, forex, dan makro, dari riset sampai entry, manajemen posisi, dan exit; berjalan lokal dengan workspace file-driven.
- **Bahasa:** tidak tampil di hasil fetch. **Lisensi:** AGPL-3.0. **Bintang terverifikasi:** 7.403 (forks 1.156; klaim video 7,3k terkonfirmasi).
- **Biaya:** kode gratis; jalan butuh API LLM berbayar.
- **Relevansi:** TINGGI — orkestrator trading multi-aset + file-driven (agen lokal yang bisa diaudit file-nya).
- **Portabilitas:** lokal; self-host; situs openalice.ai.
- **Verdict:** PERTIMBANGKAN — arsitektur orkestratornya kuat, tapi eksekusi trading berstatus **beta** di README ("Start with simulator, paper, demo, or testnet accounts… no guarantees of correctness, reliability, profitability"); kredensial broker "sealed at rest" secara lokal. AGPL-3.0 copyleft — perhatikan bila dipakai sebagai layanan jaringan.

### E3. ValueCell — https://github.com/valuecell-ai/valuecell
- **Fungsi:** Platform multi-agen komunitas untuk aplikasi finansial: tim agen investasi AI untuk pilih saham, riset, tracking pasar, dan eksekusi trade (DeepResearch Agent, Strategy Agent, News Retrieval Agent).
- **Bahasa:** tidak tampil di hasil fetch (indikasi README: aplikasi berbasis Python + frontend; badge Python 3.12+ tampil — klaim Python 3.12+ terkonfirmasi lewat badge). **Lisensi:** Apache-2.0 (sesuai klaim). **Bintang terverifikasi:** 11.039 (forks 1.805).
- **Biaya:** kode gratis; jalan butuh API LLM berbayar.
- **Relevansi:** TINGGI — multi-agen finansial end-to-end (riset → strategi → eksekusi).
- **Portabilitas:** self-host; Python 3.12+.
- **Verdict:** PERTIMBANGKAN — arsitektur multi-agennya relevan; klaim data lokal terkonfirmasi verbatim: "The system keeps all your sensitive information stored locally on your device" dan "The app stores secrets locally on your device and will not send them to any third party over the internet." **Batasan:** live trading saat ini hanya kontrak/perpetual (spot diimplementasikan sebagai kontrak 1x); bursa teruji: Binance, Hyperliquid, OKX; Coinbase/Gate.io/MEXC baru sebagian teruji. **Catatan untuk user: Binance sudah dicoret dari rencana user — relevansi ValueCell di sini adalah arsitekturnya, bukan jalur Binance-nya.** Isi situs valuecell.ai sendiri gagal diverifikasi (fetch situs gagal dimuat; hanya penyebutannya di README yang terkonfirmasi).

### E4. eliza — https://github.com/elizaOS/eliza
- **Fungsi:** Sistem operasi agen open source: runtime agen otonom dengan personality, memory, plugin, dan operasi wallet non-custodial EVM/Solana.
- **Bahasa:** tidak tampil di hasil fetch (README menyebutnya "open-source TypeScript framework"). **Lisensi:** MIT. **Bintang terverifikasi:** 19.748 (forks 5.856; klaim carousel 19k terkonfirmasi).
- **Biaya:** kode gratis; jalan butuh API LLM berbayar.
- **Relevansi:** TINGGI — fondasi agen umum (personality + memory + wallet); trading hanya satu kemampuan via plugin, bukan bot trading siap pakai.
- **Portabilitas:** self-host; branch default `develop` (bukan `main`); kontribusi pihak ketiga/registry kini ditolak maintainer (fokus first-party).
- **Verdict:** PERTIMBANGKAN — fondasi agen umum terkuat di daftar ini; tapi butuh plugin trading sendiri. Bersaing dengan Vibe-Trading (A8) sebagai kerangka utama — pilih satu.

### E5. RD-Agent — https://github.com/microsoft/RD-Agent
- **Fungsi:** Framework Microsoft untuk mengotomasi R&D berbasis data dan model dengan agen LLM ("R" mengusulkan ide, "D" mengimplementasikannya).
- **Bahasa:** tidak tampil di hasil fetch (indikasi README: Python 3.10/3.11, `pip install rdagent`, hanya Linux). **Lisensi:** MIT. **Bintang terverifikasi:** 15.164 (forks 2.017; klaim carousel 14k terkonfirmasi).
- **Biaya:** kode gratis; jalan butuh API LLM berbayar.
- **Relevansi:** TINGGI untuk riset — **peringatan tugas BENAR: ini BUKAN bot trading.** Ini framework R&D umum (MLE-bench, Kaggle, data science, fine-tuning). Skenario quant-nya, RD-Agent(Q), adalah satu aplikasi: menulis dan menguji quant factor/model — riset saja, bukan eksekusi order live.
- **Portabilitas:** Linux saja; self-host.
- **Verdict:** PERTIMBANGKAN — untuk riset factor/model quant (pelengkap Qlib); jangan dimasukkan ke daftar bot eksekusi.

### E6. prediction-market-agent — https://github.com/gnosis/prediction-market-agent
- **Fungsi:** Library untuk menjelajahi framework AI agent lewat contoh agen betting di prediction market (Omen/Presagio, Manifold, dan Polymarket), dibangun di atas `prediction-market-agent-tooling`.
- **Bahasa:** tidak tampil di hasil fetch (indikasi README: Python 3.11, `uv`). **Lisensi:** LGPL-3.0 (sesuai klaim). **Bintang terverifikasi:** 90 (forks 27).
- **Biaya:** kode gratis; jalan butuh API LLM berbayar; betting butuh dana.
- **Relevansi:** SEDANG — contoh agen prediction market (termasuk Polymarket); proyek riset/eksperimen framework, bukan produk trading jadi (banyak agen contoh, beberapa deployment Streamlit sudah deprecated).
- **Portabilitas:** Python; ringan.
- **Verdict:** PERTIMBANGKAN — referensi agen Polymarket; kecil (90 stars) tapi aktif.
- **Risiko kunci:** menjalankan agen betting memakai `.env` dengan `BET_FROM_PRIVATE_KEY` + `OPENAI_API_KEY`.

### E7. py-clob-client — https://github.com/Polymarket/py-clob-client
- **Fungsi:** Klien Python resmi untuk Polymarket CLOB (central limit order book).
- **Bahasa:** tidak tampil di hasil fetch (indikasi README: Python 3.9+, paket `py_clob_client`). **Lisensi:** MIT. **Bintang terverifikasi:** 1.224 (klaim carousel 1,1k terkonfirmasi, kini lebih tinggi).
- **Biaya:** kode gratis.
- **Relevansi:** TINGGI secara topik (SDK resmi Polymarket) — tapi **statusnya membatalkan relevansi praktis**.
- **Portabilitas:** Python; ringan.
- **Verdict:** LEWATI — **peringatan penting: repo DIARSIPKAN dan TIDAK FUNGSIONAL.** README diawali peringatan verbatim: "This repository has been archived and is no longer maintained. The client is no longer functional and should not be used for new or existing integrations. Please migrate to our new unified SDK: https://github.com/Polymarket/py-sdk". Jangan dipakai untuk integrasi baru — penggantinya py-sdk (di luar materi, perlu verifikasi terpisah bila mau dipakai).
- **Risiko kunci (bila tetap dibaca sebagai referensi):** mode trading memakai `PRIVATE_KEY` + funder/proxy address (chain Polygon 137) + allowance USDC/conditional token; mode baca saja (Level 0, tanpa auth) tersedia untuk harga/order book.

### E8. Polymarket Agents — https://github.com/Polymarket/agents
- **Fungsi:** Framework resmi untuk membangun AI agent yang trading otonom di Polymarket, dengan LLM, ChromaDB (RAG), dan CLI.
- **Bahasa:** tidak tampil di hasil fetch (indikasi README: Python 3.9, CLI `scripts/python/cli.py`). **Lisensi:** MIT. **Bintang terverifikasi:** 3.808 (klaim carousel 600+ terkonfirmasi, kini jauh lebih tinggi).
- **Biaya:** kode gratis; jalan butuh API LLM berbayar.
- **Relevansi:** TINGGI secara topik (framework agen resmi Polymarket) — tapi statusnya sama seperti E7.
- **Portabilitas:** Python; ringan.
- **Verdict:** LEWATI — **juga DIARSIPKAN** (Public archive; hanya 7 commit). Ini warisan, bukan framework aktif yang di-maintain. Jangan jadikan fondasi baru; polanya (LLM + ChromaDB RAG + CLI) bisa ditiru dengan komponen aktif (mem0 + GPT Researcher + py-sdk).
- **Risiko kunci:** `.env` memakai `POLYGON_WALLET_PRIVATE_KEY` + wallet harus diisi USDC; CLI bisa eksekusi trade. README juga mencatat ToS melarang trading oleh US persons / yurisdiksi terbatas.

### E9. Polymarket Terminal — https://github.com/direkturcrypto/polymarket-terminal
- **Fungsi:** Terminal trading otomatis Polymarket: maker rebate market maker (strategi utama, pasar 15-menit BTC/ETH/SOL Up-or-Down), copy trader, dan orderbook sniper.
- **Bahasa:** tidak tampil di hasil fetch (indikasi README: Node.js 18+, `src/*.js`, npm). **Lisensi:** MIT (tertulis di README; kolom License tidak tampil di panel detail). **Bintang terverifikasi:** 295 (klaim carousel 319 — kini sedikit lebih rendah; wajar karena snapshot berbeda waktu).
- **Biaya:** kode gratis; trading butuh dana USDC.e.
- **Relevansi:** TINGGI — tool Polymarket paling praktis di daftar ini (strategi jadi + mode simulasi per strategi).
- **Portabilitas:** Node.js; ringan; self-host.
- **Verdict:** PERTIMBANGKAN — khusus venue Polymarket; README menekankan tes simulasi dulu. Klaim "merge YES+NO" terkonfirmasi (merge via kontrak CTF).
- **Risiko kunci:** butuh EOA private key untuk signing + proxy wallet terdanai USDC.e di Polygon; mode sim tersedia tanpa order nyata. **Copy trading = mengikuti trader lain** — risikonya ikut menanggung kesalahan trader itu; pakai mode sim dulu dan pahami strateginya.

### E10. OctoBot Prediction Market — https://github.com/Drakkar-Software/OctoBot-Prediction-Market
- **Fungsi:** Bot Polymarket open source ber-GUI untuk copy trading dan arbitrage, dengan paper trading dan dukungan Kalshi mendatang.
- **Bahasa:** tidak tampil di hasil fetch (indikasi README: Python, `start.py`). **Lisensi:** GPL-3.0. **Bintang terverifikasi:** 120 (klaim carousel 500+ **tidak** terkonfirmasi — angka kini jauh lebih rendah; jangan pakai klaim 500+).
- **Biaya:** kode gratis; paper trading gratis.
- **Relevansi:** SEDANG — GUI + paper trading menarik untuk pemula Polymarket, tapi fitur utama masih WIP.
- **Portabilitas:** Docker terkonfirmasi (`docker run ... -p 80:5001 ... drakkarsoftware/octobot:predictionmarket-stable`, port kontainer 5001 sesuai klaim); kebutuhan minimal: 1 CPU, RAM 250 MB, disk 1 GB — **cocok untuk VPS kecil**.
- **Verdict:** PERTIMBANGKAN — untuk GUI + paper trading Polymarket; jangan anggap copy/arbitrage sudah jadi (README menandainya 🚧 / "under development").
- **Risiko kunci:** live trading menyentuh kunci, tapi dengan klaim self-custody (kunci tidak pernah meninggalkan perangkat). README menekankan uji paper dulu sebelum dana nyata.

### E11. poly-maker — https://github.com/warproxxx/poly-maker
- **Fungsi:** Bot market-making maker-only untuk Polymarket CLOB V2 (fokus pasar politik) dengan strategi fair-value + inventory-skew, risk cap, dan kill-switch harian.
- **Bahasa:** tidak tampil di hasil fetch (indikasi README: Python 3.12+, `uv`). **Lisensi:** MIT. **Bintang terverifikasi:** 1.517 (klaim carousel 200+ terkonfirmasi, kini jauh lebih tinggi).
- **Biaya:** kode gratis; market-making butuh dana.
- **Relevansi:** TINGGI — market maker Polymarket dengan risk cap + kill-switch (pola pengaman yang sejalan dengan bot user).
- **Portabilitas:** Python; ringan; self-host.
- **Verdict:** PERTIMBANGKAN — khusus venue Polymarket; mode `--paper` tersedia tanpa order; ada peringatan "bisa rugi, bukan produk profit pasti".
- **Koreksi:** README saat ini **tidak menyebut Google Sheets sama sekali** — konfigurasi lewat **file TOML lokal (`config/`) + SQLite**, bukan Sheets (klaim Sheets hanya muncul di entri daftar Awesome, kemungkinan deskripsi lama). Fitur `poly_merger` hemat gas tidak tampil dengan nama itu di README yang difetch; yang ada adalah "merger (EOA path)" dan catatan merge via Safe/proxy belum di-wire (exit sementara via limit sell). Bot ini memakai `py-clob-client-v2` (bukan klien lama yang diarsipkan).
- **Risiko kunci:** `.env` berisi `PK` (private key signer wallet) + `BROWSER_ADDRESS`; deployment lengkap = repo + `.env` + wallet terdanai.

### E12. Awesome Polymarket Tools — https://github.com/harish-garg/Awesome-Polymarket-Tools
- **Fungsi:** Daftar kurasi tool Polymarket untuk trader, developer, dan peneliti (bukan tool eksekusi).
- **Bahasa:** tidak tampil (wajar: repo ini hanya berisi `README.md`, tanpa kode). **Lisensi:** CC0 (waiver hak cipta di README; kolom License tidak tampil di panel detail). **Bintang terverifikasi:** 177 (forks 89; hanya 3 commit; dibuat 2025-12-12).
- **Biaya:** gratis (daftar tautan).
- **Relevansi:** SEDANG — referensi direktori: SDK resmi, ekstensi browser, analytics/Dune, whale tracker (PolyTrack, Polywhaler), copy bot, sniper list, MCP, Telegram bot.
- **Portabilitas:** tidak berlaku (dokumen).
- **Verdict:** PERTIMBANGKAN — sebagai daftar cek; **wajib cek tiap tautan satu per satu** karena daftar ini masih menautkan `py-clob-client` (yang kini diarsipkan/tidak fungsional) dan mendeskripsikan poly-maker sebagai "Google Sheets configuration" (sudah kedaluwarsa per E11). Repo ini sendiri tidak menyentuh kunci sama sekali; risiko kunci tergantung tool yang dipilih dari daftar itu.

---

## F. Video "6 GITHUB REPOS THAT LET YOU RUN A HEDGE FUND" (Data Scientist | Kashi)

### F1. Nautilus Trader — https://github.com/nautechsystems/nautilus_trader
- **Fungsi:** Engine trading production-grade berbasis Rust dengan arsitektur event-driven deterministik untuk riset, simulasi, dan eksekusi live multi-aset/multi-venue.
- **Bahasa:** tidak tampil di hasil fetch (deskripsi menyebutnya "Rust-native" dengan Python sebagai control plane — ini bukan klaim kolom bahasa). **Lisensi:** LGPL-3.0. **Bintang terverifikasi:** 31.119 (forks 4.195).
- **Biaya:** kode gratis; jalan tanpa LLM.
- **Relevansi:** TINGGI — engine paling serius di daftar ini untuk backtest deterministik + eksekusi live.
- **Portabilitas:** Rust + Python; butuh setup lebih berat dari bot Python biasa; branch default `develop`; v1 hanya menerima backport keamanan kritis selama transisi v2. Cocok laptop/VPS menengah, bukan andalan VPS 512 MB untuk live.
- **Verdict:** PERTIMBANGKAN — engine jangka panjang bila bot naik kelas; untuk demo sekarang, Freqtrade lebih ringan.

### F2. skfolio — https://github.com/skfolio/skfolio
- **Fungsi:** Library Python untuk optimasi portofolio, konstruksi factor model, dan manajemen risiko berbasis scikit-learn.
- **Bahasa:** tidak tampil di hasil fetch (deskripsi menyebutnya library Python di atas scikit-learn). **Lisensi:** BSD-3-Clause. **Bintang terverifikasi:** 2.573 (forks 294).
- **Biaya:** kode gratis; jalan lokal.
- **Relevansi:** TINGGI — manajemen risiko/portofolio adalah bagian yang paling sering hilang dari bot amatir (alokasi, drawdown, kill-switch berbasis portofolio).
- **Portabilitas:** Python; ringan.
- **Verdict:** PAKAI — modul risiko/portofolio (pasangan Qlib untuk riset quant). Ada penawaran enterprise support/SLA dari Skfolio Labs, tapi library-nya sendiri open source.

### F3. Freqtrade — https://github.com/freqtrade/freqtrade
- **Fungsi:** Bot trading kripto gratis dan open source yang mendukung banyak exchange, dikendalikan via Telegram atau webUI, lengkap dengan backtesting, plotting, dan optimasi strategi ML (FreqAI).
- **Bahasa:** tidak tampil di hasil fetch (README menyebut bot ditulis dalam Python, Python 3.12+). **Lisensi:** GPL-3.0. **Bintang terverifikasi:** 56.233 (forks 11.638).
- **Biaya:** kode gratis; jalan tanpa LLM (FreqAI opsional).
- **Relevansi:** TINGGI — backtest + eksekusi kripto paling matang di daftar ini; README sendiri menegaskan: perangkat lunak untuk edukasi, selalu mulai dari Dry-Run sebelum uang asli.
- **Portabilitas:** Python; Docker; berjalan di VPS kecil untuk strategi ringan; Telegram/webUI untuk monitoring.
- **Verdict:** PAKAI — eksekutor + backtest kripto utama (dry-run dulu). GPL-3.0 copyleft — perhatikan bila kode turunan didistribusikan. Cek dukungan exchange yang dipakai user sebelum live (Freqtrade memakai CCXT; Indodax ada di CCXT, tapi verifikasi pair/endpoint tetap wajib).

### F4. Kronos — https://github.com/shiyu-coder/Kronos
- **Fungsi:** Model fondasi open source pertama untuk candlestick finansial (K-line), dilatih pada data dari 45+ exchange global untuk forecasting harga/volume.
- **Bahasa:** tidak tampil di hasil fetch (instalasi memakai Python 3.10+; model dimuat dari Hugging Face Hub NeoQuasar). **Lisensi:** MIT. **Bintang terverifikasi:** 44.857 (forks 7.419).
- **Biaya:** kode gratis; inferensi model butuh komputasi (GPU membantu untuk model besar).
- **Relevansi:** TINGGI sebagai "otak prediksi" — tapi **koreksi klasifikasi penting: Kronos BUKAN framework/engine trading.** README-nya sendiri menyatakan pipeline backtest-nya hanya demo sederhana, bukan sistem trading production-ready, dan butuh optimasi portofolio + manajemen risiko sebelum dipakai.
- **Portabilitas:** model mini (4,1M), small (24,7M), base (102,3M) terbuka; model large (499,2M) tidak dirilis open source. Inferensi model kecil bisa di CPU; training butuh GPU.
- **Verdict:** PERTIMBANGKAN — sebagai modul forecasting (dipasangkan dengan skfolio untuk risiko + Freqtrade untuk eksekusi), bukan sebagai bot jadi. Dibuat 2025-07-01, diterima AAAI 2026. Disambiguasi: sempat muncul fork `sepvej/Kronos` di pencarian, tapi repo kanonisnya `shiyu-coder/Kronos`.

### F5. Hummingbot — sudah dievaluasi di A7
- Masuk video ini juga — **digabung, tidak ganda**. Lihat entri A7 (20.887★, Apache-2.0, PERTIMBANGKAN).

### F6. Repo ke-6 video Kashi — BELUM TERIDENTIFIKASI DARI MATERI YANG DIKIRIM
- **Status eksplisit:** video mengklaim 6 repo, tapi dari materi yang dikirim baru **5 kartu terkonfirmasi**: Nautilus Trader (F1), Hummingbot (A7/F5), skfolio (F2), Freqtrade (F3), Kronos (F4).
- **Usaha identifikasi yang sudah dilakukan:** pencarian beberapa varian ("6 GitHub repos run a hedge fund", nama creator "Kashi", kombinasi kelima nama repo) tidak menemukan daftar lengkap video tersebut. Hasil yang muncul adalah artikel/stack lain (mis. QuantFrame "Four Repos, Four Desks": Kronos + skfolio + NautilusTrader + Vibe-Trading, dan daftar bot kripto umum) yang tidak cocok dengan komposisi video ini.
- **Tidak dikarang:** kandidat seperti Qlib/TradingAgents/ai-hedge-fund TIDAK ditebak sebagai repo ke-6 karena tidak ada bukti mengaitkannya dengan video itu.
- **Hasil screening gambar 1 Nov 2026 (157 file):** hanya 5 kartu yang sama dari video yang sama yang muncul — IMG_8303.jpg (Kronos), IMG_8304.jpg (Freqtrade), IMG_8305.jpg (skfolio), IMG_8306.jpg (Nautilus), IMG_8307.jpg (Hummingbot), dengan angka interaksi identik (438/46/488/53). Tidak ada kartu ke-6, daftar lengkap, atau nama kandidat di file mana pun. Penampakan Nautilus/Kronos di slice B/C berasal dari video TikTok lain, bukan bukti untuk #6. Tetap BELUM TERIDENTIFIKASI.
- **Yang dibutuhkan:** link video atau tangkapan layar daftar lengkapnya dari user, supaya repo ke-6 bisa diverifikasi langsung. Entri ini ditulis eksplisit supaya tidak ada yang hilang diam-diam.

---

## G. Hasil screening gambar 1 Nov 2026 — temuan baru

**Catatan screening (1 Nov 2026):** 157 file gambar dibaca satu per satu (audit trail
lengkap di `SCREENING.md` di working copy). Duplikat file digabung (6 file), 0 gagal baca,
0 item murni tak terbaca. Bagian ini menambahkan **47 repo + 4 observasi non-repo**
(G1–G51) dengan angka live dari GitHub API (snapshot 1 Nov 2026, ~10:00–10:10 UTC;
ComfyUI via fetch halaman repo). **Stack rekomendasi di bawah TIDAK diubah oleh
screening ini** — kandidat tambahan yang layak dipertimbangkan di putaran berikut:
Firecrawl (G33, riset web), last30days-skill (G38, riset sentimen termasuk Polymarket),
MiroFish (G37, prediksi), 9Router (G21, lapisan model), markitdown (G27, alternatif Docling).
Semua entri lama di atas dipertahankan apa adanya.

### G-A. Coding agent & tooling

### G1. Plandex — https://github.com/plandex-ai/plandex — okaashish #3
- **Fungsi:** Coding agent terminal untuk codebase besar (konteks sampai 2M token).
- **Bahasa:** Go. **Lisensi:** MIT. **Bintang terverifikasi:** 15.873. Tidak diarsipkan.
- **Biaya:** kode gratis; jalan bisa pakai model lokal atau API berbayar.
- **Relevansi:** SEDANG — tooling coding agent, bukan komponen trading.
- **Portabilitas:** terminal; ringan.
- **Verdict:** PERTIMBANGKAN — alternatif coding agent untuk codebase besar. Catatan slide: "Plandex Cloud is winding down" (layanan cloud-nya saja; CLI open source tetap). Slide tidak menampilkan URL GitHub — URL diverifikasi live lewat API + rekap okaashish.

### G2. Void — https://github.com/voideditor/void — okaashish #4
- **Fungsi:** Alternatif Cursor open source (editor + agen AI).
- **Bahasa:** TypeScript. **Lisensi:** Apache-2.0. **Bintang terverifikasi:** 28.725. **DIARSIPKAN (archived=True).**
- **Biaya:** kode gratis.
- **Relevansi:** SEDANG sebagai editor, tapi statusnya membatalkan pemakaian baru.
- **Portabilitas:** desktop; ringan.
- **Verdict:** LEWATI — repo diarsipkan; jangan jadikan dependensi baru. (Klaim slide 28.7k terkonfirmasi angkanya, tapi bukan statusnya.)

### G3. Zed — https://github.com/zed-industries/zed — okaashish #5
- **Fungsi:** Editor kode cepat (Rust) dengan agen AI terintegrasi.
- **Bahasa:** Rust. **Lisensi:** tidak terdeteksi API (NOASSERTION; Zed memakai multi-lisensi — cek file LICENSE). **Bintang terverifikasi:** 92.476. Tidak diarsipkan.
- **Biaya:** kode gratis; fitur AI bisa butuh API berbayar.
- **Relevansi:** SEDANG — tooling pengembangan bot.
- **Portabilitas:** desktop (macOS/Linux); ringan dan cepat.
- **Verdict:** PERTIMBANGKAN — editor alternatif bila butuh kecepatan; bukan komponen trading.

### G4. Cline — https://github.com/cline/cline — okaashish #6
- **Fungsi:** Coding agent di VS Code (autonomous coding dengan tools, file, terminal).
- **Bahasa:** TypeScript. **Lisensi:** Apache-2.0. **Bintang terverifikasi:** 71.142. Tidak diarsipkan.
- **Biaya:** kode gratis; jalan butuh API LLM berbayar (atau model lokal).
- **Relevansi:** SEDANG — tooling coding agent.
- **Portabilitas:** ekstensi VS Code; ringan.
- **Verdict:** PERTIMBANGKAN — pelengkap/pesaing Open Code & Aider di dalam IDE. Slide tidak menampilkan URL GitHub — URL diverifikasi live lewat API + rekap okaashish.

### G5. Kilo Code — https://github.com/Kilo-Org/kilocode — okaashish #7
- **Fungsi:** Coding agent open source untuk VS Code, JetBrains, dan CLI (500+ model).
- **Bahasa:** TypeScript. **Lisensi:** MIT. **Bintang terverifikasi:** 27.821. Tidak diarsipkan.
- **Biaya:** kode gratis; jalan butuh API LLM berbayar (atau model lokal).
- **Relevansi:** SEDANG — tooling coding agent.
- **Portabilitas:** ekstensi/CLI; ringan.
- **Verdict:** PERTIMBANGKAN — satu lagi kandidat coding agent; pilih satu sebagai harian, jangan menumpuk.

### G6. mattpocock/skills — https://github.com/mattpocock/skills
- **Fungsi:** Kumpulan skill untuk coding agent (folder skills: deprecated, engineering, in-progress, misc, personal, productivity).
- **Bahasa:** Shell. **Lisensi:** MIT. **Bintang terverifikasi:** 308.790. Tidak diarsipkan.
- **Biaya:** gratis.
- **Relevansi:** SEDANG — pola skill untuk agen (relevan sebagai referensi desain skill bot, bukan trading langsung).
- **Portabilitas:** file markdown/shell; ringan.
- **Verdict:** PERTIMBANGKAN — sebagai referensi struktur skill agen. **Koreksi penting:** ini SATU repo, bukan 4 repo seperti framing lama ("4 repo github yang wajib lo install") — yang terlihat di frame (IMG_8401-2) adalah satu halaman repo dengan 6 kategori folder di dalamnya; video Satria Bahari menghitungnya sebagai #6 dari 6.

### G7. everything-claude-code — https://github.com/WorldFlowAI/everything-claude-code (kandidat terkuat; owner tidak terbaca di gambar)
- **Fungsi:** Toolkit Claude Code: agents, commands, skills, rules, dan hooks untuk pengembangan berbantuan AI.
- **Bahasa:** JavaScript. **Lisensi:** tidak terdeteksi API (null). **Bintang terverifikasi:** 5.704. Tidak diarsipkan.
- **Biaya:** gratis.
- **Relevansi:** SEDANG — tooling Claude Code.
- **Portabilitas:** ringan.
- **Verdict:** PERTIMBANGKAN — dengan caveat: frame video hanya menampilkan committer affaan-m, bukan pemilik repo; WorldFlowAI adalah kandidat terkuat via kecocokan deskripsi, BUKAN terbukti dari gambar. Konfirmasi owner sebelum dipakai serius.

### G8. claude-code-best-practice — https://github.com/shanraisshan/claude-code-best-practice
- **Fungsi:** Panduan dan praktik terbaik Claude Code (plus trik bolt.new: awali URL repo dengan `bolt.new/` untuk membukanya di Bolt).
- **Bahasa:** HTML. **Lisensi:** MIT. **Bintang terverifikasi:** 68.394. Tidak diarsipkan.
- **Biaya:** gratis.
- **Relevansi:** SEDANG — panduan proses pengembangan agen.
- **Portabilitas:** dokumen; ringan.
- **Verdict:** PERTIMBANGKAN — sebagai panduan, bukan komponen.

### G9. planning-with-files — https://github.com/OthmanAdi/planning-with-files
- **Fungsi:** Skill Claude Code untuk planning persisten berbasis file markdown (pola ala Manus: rencana hidup di file, bukan hanya di konteks).
- **Bahasa:** Shell. **Lisensi:** MIT. **Bintang terverifikasi:** 27.803. Tidak diarsipkan.
- **Biaya:** gratis.
- **Relevansi:** SEDANG — pola planning ini relevan untuk agen trading (rencana/keputusan tercatat di file, bisa diaudit — sejalan dengan ledger paper bot user).
- **Portabilitas:** ringan.
- **Verdict:** PERTIMBANGKAN — pola planning-nya layak ditiru. (Klaim slide 260★ sudah sangat kedaluwarsa.)

### G10. codex-plugin-cc — https://github.com/openai/codex-plugin-cc
- **Fungsi:** Plugin resmi OpenAI yang menghubungkan Codex ke Claude Code.
- **Bahasa:** JavaScript. **Lisensi:** Apache-2.0. **Bintang terverifikasi:** 34.779. Tidak diarsipkan.
- **Biaya:** kode gratis; jalan butuh API model berbayar.
- **Relevansi:** SEDANG — jembatan antar-harness coding agent.
- **Portabilitas:** ringan.
- **Verdict:** PERTIMBANGKAN — bila workflow memakai Codex + Claude Code bersamaan.

### G11. andrej-karpathy-skills — https://github.com/multica-ai/andrej-karpathy-skills
- **Fungsi:** Satu file CLAUDE.md berisi observasi/gaya kerja Andrej Karpathy untuk coding agent; README juga menyebut proyek baru Multica (platform menjalankan/mengelola coding agent dengan skill reusable).
- **Bahasa:** tidak tampil (file markdown). **Lisensi:** tidak terdeteksi API (klaim slide: MIT). **Bintang terverifikasi:** 227.688. Tidak diarsipkan.
- **Biaya:** gratis.
- **Relevansi:** SEDANG — panduan gaya kerja agen coding.
- **Portabilitas:** satu file; ringan.
- **Verdict:** PERTIMBANGKAN — sebagai referensi gaya, bukan komponen.

### G12. prompt-master — https://github.com/nidhinjs/prompt-master
- **Fungsi:** Skill Claude untuk menulis prompt yang akurat.
- **Bahasa:** tidak tampil di hasil API. **Lisensi:** MIT. **Bintang terverifikasi:** 15.345. Tidak diarsipkan.
- **Biaya:** gratis.
- **Relevansi:** RENDAH–SEDANG — prompt engineering umum.
- **Portabilitas:** ringan.
- **Verdict:** PERTIMBANGKAN — untuk kualitas prompt analis; bukan komponen trading. (Konflik di gambar dicatat: layar 7.997★ vs klaim lisan "11K".)

### G13. ECC — https://github.com/affaan-m/ECC
- **Fungsi:** Setup universal Claude Code: 68 agents, 291 skills, 61 hooks, dan security scanner (klaim slide); instalasi via `npx ecc-universal@2.2.1 setup`; diklaim pemenang hackathon Anthropic (klaim slide).
- **Bahasa:** JavaScript. **Lisensi:** MIT. **Bintang terverifikasi:** 294.325. Tidak diarsipkan.
- **Biaya:** gratis.
- **Relevansi:** SEDANG — tooling setup coding agent.
- **Portabilitas:** ringan (katalog besar — pilih workflow yang dipakai, jangan semua).
- **Verdict:** PERTIMBANGKAN — sebagai starter pack; risiko katalog raksasa: konteks membengkak bila semua skill dimuat (pakai headroom / pilih workflow).

### G14. REA — https://github.com/morluto/rea
- **Fungsi:** Jembatan MCP + CLI dari Claude Code/Cursor ke toolchain reverse-engineering (decompiler) untuk membedah cara kerja aplikasi.
- **Bahasa:** TypeScript. **Lisensi:** MIT. **Bintang terverifikasi:** 416.701. Tidak diarsipkan.
- **Biaya:** kode gratis.
- **Relevansi:** RENDAH untuk trading agent — ini tool reverse engineering, bukan komponen trading.
- **Portabilitas:** ringan.
- **Verdict:** LEWATI — untuk trading agent. Alasan: relevansi trading nyaris nol, dan tool dual-use (membongkar aplikasi orang lain) dengan risiko keamanan/penyalahgunaan; slide sumber sendiri memberi disclaimer "buat belajar, bukan buat nyolong". Jangan dimasukkan ke pipeline bot.
- **Catatan:** klaim video "170 ribu+ star" sudah terlampaui jauh (kini 416.701); klaim REA "7.019★" di video lain adalah angka lama/parsial, bukan total.

### G15. security-audit-skill — https://github.com/cloudflare/security-audit-skill
- **Fungsi:** Skill coding-agent untuk audit keamanan multi-fase dengan temuan machine-readable yang diverifikasi independen.
- **Bahasa:** JavaScript. **Lisensi:** MIT. **Bintang terverifikasi:** 55.748. Tidak diarsipkan.
- **Biaya:** gratis.
- **Relevansi:** SEDANG — audit keamanan kode bot sendiri sebelum live (sejalan dengan gerbang pengaman bot user).
- **Portabilitas:** ringan.
- **Verdict:** PERTIMBANGKAN — untuk audit kode bot. (Klaim video 15.072 = bintang/minggu, bukan total.)

### G16. T3 Code — https://github.com/pingdotgg/t3code
- **Fungsi:** Harness control surface (aplikasi mobile/web/Electron) untuk mengendalikan Claude Code, Codex, Cursor, Grok Build, OpenCode, dan Antigravity.
- **Bahasa:** TypeScript. **Lisensi:** MIT. **Bintang terverifikasi:** 36.326. Tidak diarsipkan.
- **Biaya:** kode gratis; jalan butuh subscription harness/model.
- **Relevansi:** SEDANG — monitoring/kontrol agen dari HP (relevan dengan gaya user yang bekerja dari HP).
- **Portabilitas:** mobile/web/desktop.
- **Verdict:** PERTIMBANGKAN — untuk kontrol agen jarak jauh; bukan komponen trading.

### G17. agent-browser — https://github.com/vercel-labs/agent-browser
- **Fungsi:** CLI browser automation untuk agen AI (agen menjelajah web lewat CLI).
- **Bahasa:** Rust. **Lisensi:** Apache-2.0. **Bintang terverifikasi:** 45.073. Tidak diarsipkan.
- **Biaya:** kode gratis.
- **Relevansi:** SEDANG — riset/monitoring berbasis browser untuk analis; eksekusi trading tetap via API, bukan browser.
- **Portabilitas:** CLI; ringan.
- **Verdict:** PERTIMBANGKAN — pelengkap BrowserUse (B1) untuk riset; pilih satu.

### G18. OpenMythos — https://github.com/kyegomez/OpenMythos
- **Fungsi:** Rekonstruksi teoretis arsitektur Claude Mythos (bukan model jadi).
- **Bahasa:** Python. **Lisensi:** MIT. **Bintang terverifikasi:** 14.914. Tidak diarsipkan.
- **Biaya:** gratis.
- **Relevansi:** RENDAH — riset arsitektur; klaim video "beats Claude Mythos" tidak terbukti dari repo ini.
- **Portabilitas:** Python; ringan.
- **Verdict:** LEWATI — bukan model yang bisa dipakai, bukan komponen trading. (Angka frame konflik: 10.4k vs 7.4k; live 14.914.)

### G19. No AI Slop — https://github.com/petergyang/no-ai-slop
- **Fungsi:** Menghapus 20+ pola "AI slop" dari tulisan apa pun.
- **Bahasa:** Python. **Lisensi:** MIT. **Bintang terverifikasi:** 13.009. Tidak diarsipkan.
- **Biaya:** gratis.
- **Relevansi:** RENDAH — kualitas tulisan, bukan trading.
- **Portabilitas:** ringan.
- **Verdict:** LEWATI — untuk trading agent. (Berguna untuk konten affiliate user, bukan untuk bot.)

### G20. AI Job Search — https://github.com/ai-job-search-dev/ai-job-search
- **Fungsi:** Framework cari kerja yang jalan di mesin sendiri, dibangun di atas Claude Code: menilai lowongan, menyesuaikan CV, menulis surat lamaran, persiapan interview.
- **Bahasa:** Python. **Lisensi:** MIT. **Bintang terverifikasi:** 68.547. Tidak diarsipkan.
- **Biaya:** kode gratis; jalan butuh API LLM.
- **Relevansi:** RENDAH — bukan trading.
- **Portabilitas:** ringan.
- **Verdict:** LEWATI — untuk trading agent. (Deskripsi API cocok persis dengan frame video; nama repo tidak terlihat di frame.)

### G21. 9Router — https://github.com/decolua/9router
- **Fungsi:** Router multi-provider: satu endpoint untuk Claude Code, Codex, Cursor, Cline, Copilot, Antigravity ke 40+ provider (termasuk gratis), auto-fallback saat kuota habis, klaim hemat token.
- **Bahasa:** JavaScript. **Lisensi:** MIT. **Bintang terverifikasi:** 31.782. Tidak diarsipkan.
- **Biaya:** kode gratis; provider gratis/berbayar tergantung pilihan.
- **Relevansi:** SEDANG–TINGGI — lapisan model untuk analis (hemat biaya/kuota LLM, sejalan dengan aturan gratis user).
- **Portabilitas:** ringan; self-host.
- **Verdict:** PERTIMBANGKAN — kandidat lapisan model analis. Catatan keamanan: kunci API model melewati router — pahami risikonya; JANGAN pernah merutekan kunci wallet/private key lewat router apa pun.

### G22. CodeGraph — https://github.com/colbymchenry/codegraph
- **Fungsi:** Knowledge graph kode pre-index yang auto-sync saat kode berubah, untuk Claude Code, Codex, Gemini, Cursor, OpenCode, Antigravity, Kiro, CoPilot, Hermes Agent.
- **Bahasa:** TypeScript. **Lisensi:** MIT. **Bintang terverifikasi:** 76.111. Tidak diarsipkan.
- **Biaya:** kode gratis.
- **Relevansi:** SEDANG — hemat token coding agent (konteks kode siap pakai).
- **Portabilitas:** ringan.
- **Verdict:** PERTIMBANGKAN — pelengkap/pesaing GRAPHIFY (G39) untuk konteks kode; pilih satu.

### G23. Open Notebook — https://github.com/lfnovo/open-notebook (kandidat terkuat; nama repo tidak terlihat di frame)
- **Fungsi:** Implementasi open source NotebookLM: PDF/video/situs/catatan menjadi sumber yang bisa di-chat, diringkas, dan dijadikan podcast.
- **Bahasa:** TypeScript. **Lisensi:** MIT. **Bintang terverifikasi:** 41.215. Tidak diarsipkan.
- **Biaya:** kode gratis; jalan butuh API LLM.
- **Relevansi:** SEDANG — riset dokumen untuk analis (laporan, berita, riset pasar).
- **Portabilitas:** self-host; ringan–menengah.
- **Verdict:** PERTIMBANGKAN — dengan caveat: identifikasi via kecocokan deskripsi persis, bukan URL di gambar.

### G24. Anthropic-Cybersecurity-Skills — https://github.com/mukul975/Anthropic-Cybersecurity-Skills
- **Fungsi:** 817 skill keamanan siber untuk Claude (audit, threat modeling, secure code review, dst).
- **Bahasa:** Python. **Lisensi:** Apache-2.0. **Bintang terverifikasi:** 35.373. Tidak diarsipkan.
- **Biaya:** gratis.
- **Relevansi:** SEDANG — audit keamanan kode bot (pelengkap G15).
- **Portabilitas:** ringan.
- **Verdict:** PERTIMBANGKAN — untuk audit keamanan. **Peringatan:** proyek KOMUNITAS, bukan resmi Anthropic (sesuai disclaimernya sendiri) — jangan dikira dukungan resmi.

### G25. openclaw — https://github.com/openclaw/openclaw
- **Fungsi:** Platform agen AI open source (struktur repo: agents, apps, extensions, docs, skills; gateway + runtime agen).
- **Bahasa:** TypeScript. **Lisensi:** MIT. **Bintang terverifikasi:** 393.598. Tidak diarsipkan.
- **Biaya:** kode gratis; jalan butuh API LLM.
- **Relevansi:** SEDANG — platform agen umum (pesaing eliza/OpenAlice sebagai fondasi agen).
- **Portabilitas:** self-host.
- **Verdict:** PERTIMBANGKAN — sebagai fondasi agen alternatif. **Caveat frame:** teks overlay video ("APLIKASI INI BISA MENGUBAH REPOSITORI GITHUB MENJADI PROMPT") mungkin menjelaskan tool lain, bukan repo latar — repo dan overlay TIDAK digabung otomatis di sini.

### G26. i-have-adhd — https://github.com/ayghri/i-have-adhd
- **Fungsi:** Plugin Claude Code: jawaban dulu, penjelasan belakangan (gaya kerja cepat, 142 baris).
- **Bahasa:** Python. **Lisensi:** MIT. **Bintang terverifikasi:** 59.633. Tidak diarsipkan.
- **Biaya:** gratis.
- **Relevansi:** RENDAH–SEDANG — tooling gaya kerja agen (sejalan dengan permintaan user: keputusan cepat).
- **Portabilitas:** sangat ringan.
- **Verdict:** PERTIMBANGKAN — kecil dan ringan; nilai utamanya gaya, bukan kemampuan baru.

### G-B. Dokumen, RAG & data

### G27. markitdown — https://github.com/microsoft/markitdown
- **Fungsi:** Konverter file (PDF, Office, HTML, dll) ke Markdown (`pip install 'markitdown[all]'`).
- **Bahasa:** Python. **Lisensi:** MIT. **Bintang terverifikasi:** 193.308. Tidak diarsipkan.
- **Biaya:** gratis.
- **Relevansi:** SEDANG — parsing dokumen untuk RAG analis, sekelas Docling (B4) tapi repo berbeda.
- **Portabilitas:** Python; ringan; cocok VPS kecil.
- **Verdict:** PERTIMBANGKAN — alternatif/pelengkap Docling untuk pipeline RAG. (Dua slide berbeda di slice D: kartu repo + demo perintah — bukan duplikat.)

### G28. WeKnora — https://github.com/Tencent/WeKnora
- **Fungsi:** Platform pengetahuan LLM: dokumen mentah menjadi basis pengetahuan yang bisa dikueri + reasoning agent + Wiki yang memelihara diri.
- **Bahasa:** Go. **Lisensi:** tidak terdeteksi API (NOASSERTION). **Bintang terverifikasi:** 36.148. Tidak diarsipkan.
- **Biaya:** kode gratis; jalan butuh model (lokal/API).
- **Relevansi:** SEDANG — RAG analis yang lebih berat dari markitdown/Docling.
- **Portabilitas:** butuh Docker + model — setup terberat di set ini; bukan untuk VPS 512 MB.
- **Verdict:** PERTIMBANGKAN — bila RAG analis naik kelas ke laptop/VPS menengah; bukan prioritas.

### G29. archify — https://github.com/tt-a1i/archify
- **Fungsi:** Skill agen untuk diagram arsitektur, workflow, sequence, data-flow, dan lifecycle yang terverifikasi (`npx skills add tt-a1i/archify -g`).
- **Bahasa:** JavaScript. **Lisensi:** Apache-2.0. **Bintang terverifikasi:** 92.238. Tidak diarsipkan.
- **Biaya:** gratis.
- **Relevansi:** RENDAH–SEDANG — visualisasi/dokumentasi codebase bot.
- **Portabilitas:** ringan.
- **Verdict:** PERTIMBANGKAN — untuk dokumentasi arsitektur bot; bukan komponen runtime.

### G30. minimind — https://github.com/jingyaogong/minimind
- **Fungsi:** Latih LLM 64M parameter dari nol dalam ~2 jam (klaim) — proyek edukasi.
- **Bahasa:** Python. **Lisensi:** Apache-2.0. **Bintang terverifikasi:** 64.711. Tidak diarsipkan.
- **Biaya:** kode gratis; training butuh GPU (3090 disarankan di slide).
- **Relevansi:** RENDAH — edukasi; bukan model produksi untuk analis.
- **Portabilitas:** butuh GPU untuk training; tidak cocok VPS kecil.
- **Verdict:** LEWATI — untuk trading agent. (Nilai edukasi saja.)

### G31. OpenMAIC — https://github.com/THU-MAIC/OpenMAIC
- **Fungsi:** Kelas multi-agen interaktif open source (lingkungan belajar dengan banyak agen).
- **Bahasa:** TypeScript. **Lisensi:** MIT. **Bintang terverifikasi:** 42.333. Tidak diarsipkan.
- **Biaya:** kode gratis; jalan butuh API key model (Azure OpenAI dll) = biaya.
- **Relevansi:** RENDAH — edukasi, bukan trading.
- **Portabilitas:** menengah.
- **Verdict:** LEWATI — untuk trading agent (edukasi + biaya API).

### G32. freellmapi — https://github.com/tashfeenahmed/freellmapi
- **Fungsi:** 34 provider LLM gratis dan 635 endpoint model gratis di balik satu API /v1.
- **Bahasa:** TypeScript. **Lisensi:** MIT. **Bintang terverifikasi:** 45.364. Tidak diarsipkan.
- **Biaya:** kode gratis; provider gratis (kuota/keandalan tidak terjamin).
- **Relevansi:** SEDANG — lapisan model gratis untuk analis (pesaing 9Router G21).
- **Portabilitas:** ringan; self-host.
- **Verdict:** PERTIMBANGKAN — dengan catatan repo sendiri: "personal experimentation only". Jangan untuk order; uji keandalan dulu sebelum dipakai analis rutin.

### G33. Firecrawl — https://github.com/firecrawl/firecrawl
- **Fungsi:** Ubah website menjadi data bersih siap-AI (crawl, scrape, extract, search).
- **Bahasa:** TypeScript. **Lisensi:** AGPL-3.0. **Bintang terverifikasi:** 197.514. Tidak diarsipkan.
- **Biaya:** kode gratis (self-host); layanan cloud-nya berbayar.
- **Relevansi:** SEDANG–TINGGI — riset web analis (berita, laporan, data pasar dari web).
- **Portabilitas:** self-host (Docker); menengah.
- **Verdict:** PERTIMBANGKAN — kandidat kuat lapisan riset analis. Catatan: AGPL-3.0 copyleft — perhatikan bila dipakai sebagai layanan jaringan.

### G34. public-apis — https://github.com/public-apis/public-apis
- **Fungsi:** Direktori ribuan API publik gratis, terkategori (keuangan, cuaca, kripto, dll).
- **Bahasa:** Python. **Lisensi:** MIT. **Bintang terverifikasi:** 493.917. Tidak diarsipkan.
- **Biaya:** gratis (daftar).
- **Relevansi:** SEDANG — sumber data gratis untuk analis (CoinGecko, Open-Meteo, dll sudah dipakai bot user).
- **Portabilitas:** tidak berlaku (dokumen).
- **Verdict:** PERTIMBANGKAN — sebagai referensi sumber data; cek tiap API satu per satu (gratis ≠ tanpa batas).

### G35. Awesome Public Datasets — https://github.com/awesomedata/awesome-public-datasets
- **Fungsi:** Direktori dataset publik (termasuk sebutan Indonesia Data Portal di frame).
- **Bahasa:** tidak tampil (daftar). **Lisensi:** MIT. **Bintang terverifikasi:** 79.891. Tidak diarsipkan.
- **Biaya:** gratis (daftar).
- **Relevansi:** SEDANG–RENDAH — data riset/backtest.
- **Portabilitas:** tidak berlaku (dokumen).
- **Verdict:** PERTIMBANGKAN — sebagai referensi dataset; org tidak terbaca di frame, URL diverifikasi live lewat API.

### G36. awesome-selfhosted — https://github.com/awesome-selfhosted/awesome-selfhosted
- **Fungsi:** Direktori software self-host (bukan tool eksekusi).
- **Bahasa:** tidak tampil (daftar). **Lisensi:** tidak terdeteksi API (NOASSERTION). **Bintang terverifikasi:** 332.560. Tidak diarsipkan.
- **Biaya:** gratis (daftar).
- **Relevansi:** RENDAH — referensi hosting mandiri untuk komponen bot.
- **Portabilitas:** tidak berlaku (dokumen).
- **Verdict:** PERTIMBANGKAN — sebagai referensi hosting; beda dengan E12 (Awesome Polymarket Tools).

### G37. MiroFish — https://github.com/666ghj/MiroFish
- **Fungsi:** "A Simple and Universal Swarm Intelligence Engine, Predicting Anything" — engine prediksi multi-agen (berita, kebijakan, sinyal finansial).
- **Bahasa:** Python. **Lisensi:** AGPL-3.0. **Bintang terverifikasi:** 83.152. Tidak diarsipkan.
- **Biaya:** kode gratis; jalan butuh model/API.
- **Relevansi:** SEDANG–TINGGI — prediksi adalah inti riset prediction market (Polymarket).
- **Portabilitas:** Python; ringan–menengah.
- **Verdict:** PERTIMBANGKAN — menarik untuk riset Polymarket; klaim prediksi WAJIB divalidasi paper dulu (seperti semua modul prediksi). **Koreksi org:** 666ghj, bukan 666gh seperti terbaca awal (klon yang merujuk 666ghj mengonfirmasinya).

### G38. last30days-skill — https://github.com/mvanhorn/last30days-skill
- **Fungsi:** Skill agen untuk riset topik 30 hari terakhir di Reddit, X, YouTube, HN, Polymarket, dan web, lalu sintesis ringkasan berdasar bukti.
- **Bahasa:** Python. **Lisensi:** MIT. **Bintang terverifikasi:** 66.171. Tidak diarsipkan.
- **Biaya:** gratis (skill); jalan butuh API LLM.
- **Relevansi:** TINGGI — riset sentimen/berita termasuk Polymarket, langsung mengisi lapisan analis bot.
- **Portabilitas:** ringan.
- **Verdict:** PERTIMBANGKAN — kandidat kuat lapisan riset. **Koreksi org:** mvanhorn (address bar di frame) benar; overlay video "mvan231" salah.

### G39. GRAPHIFY — https://github.com/Graphify-Labs/graphify
- **Fungsi:** Ubah codebase beserta docs, skema SQL, config, dan PDF menjadi knowledge graph yang bisa dikueri; skill /graphify untuk Claude Code, Cursor, Codex, Gemini CLI.
- **Bahasa:** Python. **Lisensi:** Apache-2.0. **Bintang terverifikasi:** 140.220. Tidak diarsipkan.
- **Biaya:** kode gratis.
- **Relevansi:** SEDANG — konteks codebase untuk coding agent (pesaing CodeGraph G22).
- **Portabilitas:** ringan–menengah.
- **Verdict:** PERTIMBANGKAN — pilih satu vs CodeGraph. (Klaim video 6.903 = bintang/minggu.)

### G-C. Agen umum & finansial

### G40. cindy — https://github.com/makecindy/cindy
- **Fungsi:** Agen AI open source siap pakai (desktop + mobile).
- **Bahasa:** TypeScript. **Lisensi:** Apache-2.0. **Bintang terverifikasi:** 8.867. Tidak diarsipkan.
- **Biaya:** kode gratis; jalan butuh API LLM.
- **Relevansi:** SEDANG — agen umum; bukan khusus trading.
- **Portabilitas:** desktop/mobile; ringan.
- **Verdict:** PERTIMBANGKAN — sebagai agen umum alternatif; bukan fondasi trading.

### G41. ORCA — https://github.com/stablyai/orca
- **Fungsi:** Tempat kerja multi-agen: jalankan banyak coding agent (Grok Bot, Claude Code, dll) dengan subscription sendiri; desktop, mobile, remote runtime.
- **Bahasa:** TypeScript. **Lisensi:** MIT. **Bintang terverifikasi:** 112.009. Tidak diarsipkan.
- **Biaya:** kode gratis; jalan butuh subscription model.
- **Relevansi:** SEDANG — orkestrasi banyak agen (berguna bila bot memakai beberapa harness).
- **Portabilitas:** desktop/mobile/remote.
- **Verdict:** PERTIMBANGKAN — untuk orkestrasi agen. (Klaim video 9.622 = bintang/minggu; fungsi tidak terbaca di frame — deskripsi API yang dipakai.)

### G42. financial-services — https://github.com/anthropics/financial-services
- **Fungsi:** Agen, skill, dan konektor resmi Anthropic untuk finansial (investment banking, equity research, private equity, wealth management).
- **Bahasa:** Python. **Lisensi:** Apache-2.0. **Bintang terverifikasi:** 40.961. Tidak diarsipkan.
- **Biaya:** kode gratis; jalan butuh Claude/API.
- **Relevansi:** SEDANG–TINGGI — referensi desain agen finansial (riset, analisis, workflow) — bukan eksekutor dan bukan saran investasi.
- **Portabilitas:** ringan.
- **Verdict:** PERTIMBANGKAN — sebagai referensi desain agen finansial; perlu Claude untuk jalan penuh.

### G-D. Konten & media

### G43. Recordly — https://github.com/webadderallorg/Recordly
- **Fungsi:** Perekam layar untuk video demo (zoom kursor, webcam bubble, output MP4/GIF).
- **Bahasa:** TypeScript. **Lisensi:** tidak terdeteksi API (NOASSERTION). **Bintang terverifikasi:** 35.754. Tidak diarsipkan.
- **Biaya:** gratis.
- **Relevansi:** RENDAH — alat konten, bukan trading.
- **Portabilitas:** desktop.
- **Verdict:** LEWATI — untuk trading agent. (Berguna untuk konten demo/affiliate user.)

### G44. marketingskills — https://github.com/coreyhaines31/marketingskills
- **Fungsi:** 50 skill marketing untuk agen (cro, email, dll).
- **Bahasa:** JavaScript. **Lisensi:** MIT. **Bintang terverifikasi:** 57.739. Tidak diarsipkan.
- **Biaya:** gratis.
- **Relevansi:** RENDAH — konten/affiliate, bukan trading.
- **Portabilitas:** ringan.
- **Verdict:** LEWATI — untuk trading agent. (Berguna untuk konten affiliate user — format promo 85 karakter tetap aturan user, bukan tool ini.)

### G45. ComfyUI — https://github.com/Comfy-Org/ComfyUI (dulu comfyanonymous/ComfyUI; redirect aktif)
- **Fungsi:** Engine node graph gambar/video: Stable Diffusion, Flux, Wan, dll, inferensi lokal dengan workflow visual.
- **Bahasa:** Python. **Lisensi:** GPL-3.0. **Bintang terverifikasi:** 144.412 (via fetch halaman repo — API pencarian tidak mengembalikannya). Tidak diarsipkan.
- **Biaya:** kode gratis; jalan butuh GPU (model besar) atau CPU (lambat).
- **Relevansi:** RENDAH — konten visual, bukan trading.
- **Portabilitas:** butuh GPU untuk nyaman; tidak cocok VPS 512 MB.
- **Verdict:** LEWATI — untuk trading agent. (Berguna untuk konten affiliate user — foto/video AI memakai produk — bukan untuk bot.)

### G46. shadcn/ui — https://github.com/shadcn-ui/ui
- **Fungsi:** Library komponen UI (bukan agen, bukan tool trading).
- **Bahasa:** TypeScript. **Lisensi:** MIT. **Bintang terverifikasi:** 127.091. Tidak diarsipkan.
- **Biaya:** gratis.
- **Relevansi:** RENDAH — frontend dashboard.
- **Portabilitas:** web.
- **Verdict:** LEWATI — untuk trading agent. (Berguna bila user membangun dashboard sendiri.)

### G-E. Bot X/Grok & observasi non-repo

### G47. OpenMausBot — https://github.com/milind-soni/OpenMausBot
- **Fungsi:** Alternatif Grok Bot open source (VM yang bisa dipakai bot), situs www.openmausbot.com.
- **Bahasa:** TypeScript. **Lisensi:** Apache-2.0. **Bintang terverifikasi:** 10.025. Tidak diarsipkan.
- **Biaya:** kode gratis.
- **Relevansi:** RENDAH — bot X, bukan trading.
- **Portabilitas:** ringan.
- **Verdict:** LEWATI — untuk trading agent.

### G48. grokbot.dev — OBSERVASI (situs direktori, bukan repo)
- **Fungsi:** Direktori 402 setup Grok Bot siap pakai (satu entri "Fable 5.1 Oracle" terlihat di dalam direktori).
- **Biaya:** direktori (gratis dilihat).
- **Relevansi:** RENDAH — ekosistem bot X/Grok, bukan trading agent user.
- **Verdict:** LEWATI — untuk trading agent. (Dicatat supaya tidak hilang; bukan entri repo.)

### G49. Origin Pilot / Origin Quantum — OBSERVASI (produk, bukan repo)
- **Fungsi:** Komputer kuantum Tiongkok (produk hardware, bukan software open source).
- **Relevansi:** RENDAH — bukan alat trading, bukan repo.
- **Verdict:** LEWATI — bukan komponen apa pun. (Dicatat supaya tidak hilang.)

### G50. Claude Fable 5.5 news — OBSERVASI (slide berita, bukan repo)
- **Fungsi:** Jejak rilis Fable 5.5 yang beredar: ID "fable-5.5" di Cursor, codename "claude-onigiri-eap" di Artificial Analysis, 6 codename early-access di Devin CLI, commit "Co-authored-by: Fable 5.5" di T3 Code, entri azure_ai/claude-fable-5-5 di LiteLLM (klaim slide).
- **Relevansi:** RENDAH — rumor rilis; bukan model/repo yang bisa dipakai.
- **Verdict:** LEWATI — bukan komponen. Jangan pakai slide ini sebagai bukti rilis atau sebagai model.

### G51. Claude system-prompt files — OBSERVASI (file klaim bocoran, owner tidak terbaca)
- **Fungsi:** Kumpulan file yang diklaim sebagai system prompt Claude (claude-fable-5.md, claude-fable-5.1.md, dst) — owner/repo TIDAK terbaca di kedua frame.
- **Relevansi:** RENDAH + RISIKO — keaslian tidak terverifikasi; file prompt bocoran bisa berisi instruksi jahat atau teks yang dimodifikasi.
- **Verdict:** LEWATI — jangan dijalankan mentah-mentah, jangan dipakai sebagai prompt bot. (Dicatat supaya tidak hilang; bukan entri repo.)

## Rekomendasi stack gabungan (maks 7, saling melengkapi)

Stack ini dirancang untuk trading agent user: multi-venue (Indodax, Polymarket, Forex MT5, Moomoo, Pump.fun), demo/paper dulu, hosting dari VPS kecil sampai laptop, dan semua komponen gratis (biaya LLM tetap ada bila pakai model berbayar — pakai model lokal/Ollama bila mau nol biaya API).

| # | Tool | Peran di stack | Kenapa dipilih |
|---|---|---|---|
| 1 | **Vibe-Trading** (A8) | Kerangka agen trading utama | Multi-agen + backtest + lintas pasar + konektor MT5 + mode TAP isolasi kredensial; paper-trade dulu |
| 2 | **Freqtrade** (F3) | Backtest + eksekusi kripto | Paling matang untuk kripto; dry-run wajib; Telegram/webUI untuk monitoring |
| 3 | **mem0** (C6) | Memori agen | Agen ingat posisi, alasan trade, dan kesalahan lama — tanpa ini agen mengulang kesalahan |
| 4 | **headroom** (C7) | Kompres konteks | Hemat token + keputusan lebih cepat (user minta keputusan cepat) |
| 5 | **GPT Researcher** (B3) | Riset analis | Riset berita/laporan sebelum keputusan; pilih satu vs Storm, jangan keduanya |
| 6 | **skfolio** (F2) | Risiko + optimasi portofolio | Alokasi, drawdown, kill-switch berbasis portofolio; pasangan Qlib untuk riset quant |
| 7 | **day-trader-skill** (D6) | Referensi desain | Pola Time Machine (10.000 simulasi) + risk gate + paper default + konfirmasi eksplisit — diadaptasi ke venue user |

Catatan stack:
- **Qlib** (A4) dan **RD-Agent** (E5) adalah cadangan riset quant bila stack di atas butuh riset factor lebih dalam.
- **eliza** (E4) atau **OpenAlice** (E2) adalah alternatif kerangka agen bila Vibe-Trading tidak cocok — pilih satu kerangka utama, jangan menumpuk.
- **Polymarket** di dalam stack: pakai **poly-maker** (E11, market-making + paper) atau **polymarket-terminal** (E9, strategi jadi + sim) sebagai modul venue, dengan SDK baru **py-sdk** (pengganti py-clob-client yang diarsipkan) bila perlu integrasi sendiri — py-sdk perlu verifikasi terpisah karena tidak ada di materi.
- **Yang sengaja tidak masuk stack:** semua yang LEWATI di bawah, plus Dify (terlalu berat untuk VPS kecil) dan G0DM0D3 (bukan alat trading).

## Daftar yang DILEWATI + alasannya

| Tool | Alasan dilewati |
|---|---|
| **Daytona** (C8) | Diarsipkan; pengembangan inti pindah ke codebase privat Juni 2026, tanpa update/fix/rilis lagi |
| **py-clob-client** (E7) | Diarsipkan + tidak fungsional; migrasi resmi ke py-sdk |
| **Polymarket/agents** (E8) | Diarsipkan; warisan, bukan framework aktif |
| **hyperframes** (C12) | Produksi video, bukan trading |
| **OpenMontage** (C13) | Produksi video, bukan trading |
| **G0DM0D3** (D5) | Frontend chat multi-model berframing jailbreak/red-team, bukan alat trading; model OpenRouter bayar per token (klaim "gratis" menyesatkan); telemetri default on |
| **OpenClaude** (D4) | Atribusi video TERBUKTI salah (pemilik saat video = Gitlawb, bukan gnanam1990 — gnanam1990 hanya penulis commit yang tampil); lokasi repo kini tidak terkonfirmasi via pencarian; pindah org/paket; risiko legal/kepercayaan dari asal-usul codebase (sumber sekunder: bocoran + DMCA). Pakai Open Code/Aider |
| **pensource.id.lol** (A10) | Gagal diverifikasi (fetch gagal tanpa status HTTP); isinya tidak diketahui |
| **Void** (G2) | Diarsipkan (terkonfirmasi live via API 1 Nov 2026) |
| **REA** (G14) | Relevansi trading RENDAH + dual-use reverse engineering; bukan komponen trading |
| **OpenMythos** (G18) | Rekonstruksi teoretis arsitektur, bukan model jadi |
| **No AI Slop** (G19) | Kualitas tulisan, bukan trading |
| **AI Job Search** (G20) | Framework cari kerja, bukan trading |
| **minimind** (G30) | Edukasi latih LLM + butuh GPU |
| **OpenMAIC** (G31) | Edukasi + butuh API key model berbayar |
| **Recordly** (G43) | Perekam layar konten, bukan trading |
| **marketingskills** (G44) | Skill marketing/konten, bukan trading |
| **ComfyUI** (G45) | Engine gambar/video + butuh GPU; konten, bukan trading |
| **shadcn/ui** (G46) | Library komponen UI, bukan trading |
| **OpenMausBot** (G47) | Bot X/Grok, bukan trading |
| **grokbot.dev** (G48) | Direktori bot Grok, bukan trading |
| **Origin Pilot** (G49) | Produk komputer kuantum, bukan repo/alat trading |
| **Fable 5.5 news** (G50) | Slide rumor rilis, bukan repo/model |
| **system-prompt files** (G51) | Klaim bocoran tak terverifikasi + risiko instruksi jahat |

## Daftar yang BELUM JELAS (perlu materi lebih jelas dari user)

Yang tersisa hanya **3 item**. Tujuh item lama DISELESAIKAN lewat screening gambar
1 Nov 2026 (bukti di `SCREENING.md`): slide ke-7 regularbasis (= Archon B6, bukan
tool baru), slide #3–#7 okaashish (= Plandex, Void, Zed, Cline, Kilo Code — G1–G5),
screenshot MATTPOCOCK SKILLS (= satu repo mattpocock/skills, G6 — bukan 4 repo),
atribusi OpenClaude (= Gitlawb, bukan gnanam1990; lokasi kini tak terkonfirmasi),
lisensi Free Claude Code (= API NOASSERTION + badge README tidak konsisten AGPL v3
vs MIT — cek file LICENSE), lisensi Nocturne (= tidak terdeteksi API), lisensi
Daytona (= tidak terdeteksi API + arsip terkonfirmasi).

1. **Repo ke-6 video hedge fund Kashi** — video mengklaim 6, baru 5 kartu terkonfirmasi (Nautilus, Hummingbot, skfolio, Freqtrade, Kronos). Screening 157 file hanya menemukan 5 kartu yang sama dari video yang sama (IMG_8303.jpg–IMG_8307.jpg); tidak ada kartu ke-6 di file mana pun. Butuh link video / screenshot daftar lengkap.
2. **Isi situs valuecell.ai** — fetch situs gagal dimuat; hanya penyebutannya di README ValueCell yang terkonfirmasi.
3. **Isi situs pensource.id.lol** — fetch gagal; perlu pengecekan browser live bila isinya memang dibutuhkan.

## Penutup

Total **99 tool/repo unik** dievaluasi (52 lama + 47 baru dari screening gambar 1 Nov 2026, bagian G; duplikat digabung: Docling 1x, Vibe-Trading 1x, Hummingbot 1x, TradingAgents 1x, ai-hedge-fund 1x, plus pengulangan lintas slice di screening: public-apis, REA, markitdown, i-have-adhd, marketingskills, Recordly, hyperframes, karpathy-skills). Di luar 99 itu: 4 observasi non-repo (G48–G51) dan 1 item yang tetap belum teridentifikasi (F6, repo ke-6 video Kashi).

Pola yang paling berulang di semua materi: **paper mode dulu, risk gate, dan simulasi ribuan outcome** — tiga hal yang sudah sejalan dengan aturan demo user (demo dulu, tanpa order nyata sampai berhasil dan disetujui). Tool termahal bukan lisensinya (semua gratis) melainkan **biaya API LLM** — untuk menekan biaya: pakai model lokal (Ollama/LM Studio) untuk loop rutin, headroom untuk kompres konteks, dan mem0 agar agen tidak mengulang riset yang sama.

*Angka bintang snapshot 1 November 2026. Dokumen ini murni evaluasi — tidak ada order, kunci, atau dana yang disentuh.*
