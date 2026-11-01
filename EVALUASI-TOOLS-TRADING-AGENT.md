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

**Catatan jujur:** judul carousel bilang 7 tool, tapi hanya **6 tool yang terlihat di materi**. Slide ke-7 tidak ada di materi yang dikirim — masuk daftar BELUM JELAS di akhir dokumen, bukan dikarang.

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
- **Bahasa:** tidak tampil di hasil fetch. **Lisensi:** tidak tampil di hasil fetch (README hanya menautkan file LICENSE tanpa menyebut tipenya di teks yang terambil).
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
- **Bahasa:** tidak tampil sebagai label bahasa di hasil fetch (badge README menyebut Python 3.14; direktori `src/free_claude_code` juga Python). **Lisensi:** metadata GitHub "Other (NOASSERTION)" — badge README menampilkan "License: AGPL v3". **Ada perbedaan label antara metadata GitHub dan badge README — cek file LICENSE sebelum dipakai serius.**
- **Bintang terverifikasi:** 65.557 (forks 10.216).
- **Biaya:** kode gratis; klaim README "1.3B+ free tokens" tergantung provider dan bisa berubah — bukan jaminan gratis tanpa batas.
- **Relevansi:** SEDANG — penghemat biaya harness coding (router ke tier gratis), bukan komponen trading.
- **Portabilitas:** ringan; proxy lokal.
- **Verdict:** PERTIMBANGKAN — berguna untuk menekan biaya coding agent; bukan fondasi trading agent.
- **Hubungan dengan OpenClaude (D4):** BERBEDA, jangan disamakan. Free Claude Code adalah proksi/router yang mengarahkan banyak harness ke banyak provider; OpenClaude adalah satu CLI coding-agent mandiri.
- **Catatan:** screenshot TikTok batch pertama "Free Claude Code" (fabie6) kini teridentifikasi sebagai repo ini — bukan lagi item tak jelas.

### D4. OpenClaude — https://github.com/Gitlawb/openclaude (kini Twigpine/openclaude)
- **Fungsi:** CLI coding-agent terminal open source multi-model (OpenAI-compatible, Gemini, GitHub Models, Codex, Ollama, dll.) dengan satu workflow terminal: prompt, tools, agents, MCP, slash command, streaming.
- **Bahasa:** tidak tampil di hasil fetch (sumber sekunder: TypeScript). **Lisensi:** metadata GitHub "Other (NOASSERTION)" — sumber sekunder menyebut lisensi MIT berlaku untuk modifikasi komunitas, sementara kode turunan Anthropic tetap milik Anthropic. Status lisensinya tidak sesederhana "MIT murni".
- **Bintang terverifikasi:** 34.236 (forks 9.128).
- **Biaya:** kode gratis; jalan bisa pakai model lokal gratis atau API berbayar.
- **Relevansi:** SEDANG — coding agent seperti Open Code/Aider, bukan komponen trading.
- **Portabilitas:** terminal; ringan.
- **Verdict:** LEWATI — untuk proyek ini, karena: (1) **atribusi video salah** — repo `gnanam1990/openclaude` tidak ditemukan (satu-satunya repo gnanam1990 yang muncul adalah `gnanam1990/argus`, 3 stars); repo openclaude yang benar adalah Gitlawb→Twigpine; (2) proyek pindah (paket npm lama `@gitlawb/openclaude` "no longer updated", pindah ke `@twigpine/openclaude`); (3) **risiko legal/kepercayaan menurut sumber sekunder**: proyek ini berangkat dari codebase Claude Code yang bocor lewat npm source map 31 Maret 2026 dan sempat tersangkut isu DMCA terhadap mirror/fork lain; README menyatakan tidak berafiliasi dengan Anthropic. Klaim video "25.4k stars, 8.2k forks" plausibel sebagai angka lama (sumber sekunder mencatat 26,4k/8,4k; 33.282/9.084 per 15 Sep 2026; kini 34.236/9.128). Pakai Open Code atau Aider saja — lebih bersih.

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

### D7. Carousel @okaashish #3–#7 — BELUM TERIDENTIFIKASI
- Carousel "7 Alternatives to Claude Code, 100% Free and Local" — yang terkonfirmasi hanya #1 Open Code (D1) dan #2 Aider (D2). **Slide #3–#7 belum teridentifikasi dari materi**: pencarian judul carousel dan nama akun tidak mengembalikan salinan/daftar isi carousel itu. Tidak dikarang dari daftar generik lain (daftar "7 alternatif gratis" generik yang beredar berisi nama-nama lain, tapi itu bukan bukti isi carousel ini — dan dua di antaranya kini sudah berubah status: Roo Code tutup, Continue read-only setelah diakuisisi Cursor).
- **Yang dibutuhkan:** screenshot/slide #3–#7 dari user, atau pembukaan carousel lewat browser live. Lihat daftar BELUM JELAS di akhir dokumen.

---

## E. Agen trading & tools Polymarket

**Peringatan umum bagian ini:** hampir semua tool eksekusi di sini menyentuh private key/wallet bila dipakai live. Aturannya tetap: paper/simulator dulu, kunci trade-only (bukan withdrawal), dan tidak ada order nyata tanpa persetujuan eksplisit user. Copy trading = mengikuti trader lain — risikonya ikut menanggung kesalahan trader itu.

### E1. Nocturne — https://github.com/Gajesh2007/ai-trading-agent
- **Fungsi:** "Nocturne: AI Trading Agent on Hyperliquid" — agen AI memakai LLM untuk menganalisis data pasar real-time dari TAAPI, mengambil keputusan buy/sell/hold, dan mengeksekusi trade di Hyperliquid DEX, berjalan dalam loop kontinu dengan TP/SL.
- **Bahasa:** tidak tampil di hasil fetch (indikasi README: Python — `src/main.py`, `poetry`, Dockerfile). **Lisensi:** tidak tampil di hasil fetch (tidak ada file LICENSE di root yang terdaftar). **Bintang terverifikasi:** 555 (klaim video 543 sudah terlampaui).
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
- **Yang dibutuhkan:** link video atau tangkapan layar daftar lengkapnya dari user, supaya repo ke-6 bisa diverifikasi langsung. Entri ini ditulis eksplisit supaya tidak ada yang hilang diam-diam.

---

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
| **OpenClaude** (D4) | Atribusi video salah (gnanam1990/openclaude tidak ditemukan); pindah org/paket; risiko legal/kepercayaan dari asal-usul codebase (sumber sekunder: bocoran + DMCA). Pakai Open Code/Aider |
| **pensource.id.lol** (A10) | Gagal diverifikasi (fetch gagal tanpa status HTTP); isinya tidak diketahui |

## Daftar yang BELUM JELAS (perlu materi lebih jelas dari user)

1. **Slide ke-7 carousel regularbasis.studio** — judul bilang 7 tool, hanya 6 yang terlihat di materi.
2. **Slide #3–#7 carousel @okaashish** — hanya #1 Open Code dan #2 Aider terkonfirmasi; 5 slide lain belum teridentifikasi dari materi.
3. **Repo ke-6 video hedge fund Kashi** — video mengklaim 6, baru 5 kartu terkonfirmasi (Nautilus, Hummingbot, skfolio, Freqtrade, Kronos). Butuh link video / screenshot daftar lengkap.
4. **Screenshot "MATTPOCOCK SKILLS" / "4 repo github yang wajib lo install"** (TikTok, batch pertama) — yang terbaca hanya header, teks pencarian "cara install repo di github", caption, dan "Kumpulan skills"; ke-4 nama repo tidak terbaca (area video gelap/kecil). Perlu kiriman yang lebih jelas bila mau dievaluasi penuh.
5. **Atribusi OpenClaude ke gnanam1990** — repo `gnanam1990/openclaude` tidak ditemukan; yang ada hanya `gnanam1990/argus` (3 stars). Atribusi video kemungkinan salah.
6. **Isi situs valuecell.ai** — fetch situs gagal dimuat; hanya penyebutannya di README ValueCell yang terkonfirmasi.
7. **Lisensi Free Claude Code** — metadata GitHub "NOASSERTION" vs badge README "AGPL v3"; cek file LICENSE sebelum dipakai serius.
8. **Lisensi Nocturne & Daytona** — tidak tampil di hasil fetch (Nocturne: tidak ada file LICENSE di root yang terdaftar; Daytona: README hanya menautkan file LICENSE).
9. **Isi pensource.id.lol** — fetch gagal; perlu pengecekan browser live bila isinya memang dibutuhkan.

## Penutup

Total **52 tool/repo unik** dievaluasi (10 dari carousel OpensourceID + 6 dari regularbasis + 14 baru dari carousel @adityagnwann + 6 dari batch coding-agent + 12 dari batch trading/Polymarket + 4 baru dari video hedge fund; duplikat digabung: Docling 1x, Vibe-Trading 1x, Hummingbot 1x, TradingAgents 1x, ai-hedge-fund 1x).

Pola yang paling berulang di semua materi: **paper mode dulu, risk gate, dan simulasi ribuan outcome** — tiga hal yang sudah sejalan dengan aturan demo user (demo dulu, tanpa order nyata sampai berhasil dan disetujui). Tool termahal bukan lisensinya (semua gratis) melainkan **biaya API LLM** — untuk menekan biaya: pakai model lokal (Ollama/LM Studio) untuk loop rutin, headroom untuk kompres konteks, dan mem0 agar agen tidak mengulang riset yang sama.

*Angka bintang snapshot 1 November 2026. Dokumen ini murni evaluasi — tidak ada order, kunci, atau dana yang disentuh.*
