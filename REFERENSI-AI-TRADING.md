# Referensi: 9 Repo + 1 Bonus buat AI Trading (Open Source)

Sumber bahan: video carousel TikTok **@OpensourceID** (pensource.id.lol),
"9 repo buat AI trading, open source — ada yang agent, model, dan bot,
dari riset sampai order live" (12 slide, dikirim pemilik 2026-11-01).
Angka bintang di bawah adalah **sesuai video**; angka live di GitHub
berubah seiring waktu, cek langsung bila perlu angka terkini.

Semua item di bawah gratis / open source, sesuai aturan proyek ini
(alat harus gratis, tanpa langganan berbayar). Dokumen ini REFERENSI
saja: bot live yang jalan tetap loop Indodax V2 + gerbang persetujuan
di repo ini — repo eksekusi live di bawah tidak menggantikannya.

## 01 — TradingAgents (Analisis, Multi-Agent)

- Repo: https://github.com/TauricResearch/TradingAgents
- Bahasa: Python · Lisensi: Apache-2.0 · Bintang (per video): 112 RB
- Biaya/akses: Gratis + API · Fungsi: Debat agent · Status: Simulasi
- Isi: analis dan peneliti AI saling debat sebelum memberi keputusan
  beli atau jual.
- Catatan video: bisa pakai model lokal lewat Ollama. Hasil bergantung
  model dan data.
- Kaitan proyek: sudah tercatat di COMPLEMENTS.md sebagai referensi.

## 02 — FinRobot (Analisis, Agent)

- Repo: https://github.com/AI4Finance-Foundation/FinRobot
- Bahasa: Python · Lisensi: Apache-2.0 · Bintang (per video): 8 RB
- Biaya/akses: Gratis + API · Akses: Desktop · Fungsi: Riset saham
- Status: Riset
- Isi: baca laporan keuangan, hitung valuasi, lalu susun laporan riset
  saham.
- Catatan video: ada aplikasi desktop buat riset ekuitas. Versi lama
  buat belajar.

## 03 — FinGPT (Analisis, Model)

- Repo: https://github.com/AI4Finance-Foundation/FinGPT
- Bahasa: Python · Lisensi: MIT · Bintang (per video): 21 RB
- Biaya/akses: Kode gratis · Fungsi: Sentimen · Status: Riset
- Isi: model bahasa keuangan buat baca berita, sentimen pasar, dan demo
  prediksi saham.
- Catatan video: ini model, bukan agent lengkap. Demo Forecaster ada
  di Hugging Face.

## 04 — Qlib (Backtest, AI Quant)

- Repo: https://github.com/microsoft/qlib
- Bahasa: Python · Lisensi: MIT · Bintang (per video): 49 RB
- Biaya/akses: Kode gratis · Fungsi: Backtest model · Status: Backtest
- Isi: platform Microsoft buat bikin, latih, dan backtest model prediksi
  saham.
- Catatan video: sisi agent lewat RD-Agent, repo terpisah buat cari
  faktor otomatis.

## 05 — pensource.id.lol (Kurasi, Web) — BONUS

- Situs: https://pensource.id.lol
- Biaya/akses: Gratis · Akses: Browser · Fungsi: Kurasi repo
- Status: Bonus
- Isi: rangkuman repo GitHub pilihan tiap hari, dalam Bahasa Indonesia.
- Catatan video: simpan repo favorit langsung dari browser.

## 06 — FinRL (Backtest, RL Agent)

- Repo: https://github.com/AI4Finance-Foundation/FinRL
- Bahasa: Python · Lisensi: MIT · Bintang (per video): 17 RB
- Biaya/akses: Kode gratis · Fungsi: Latih agent · Status: Backtest
- Isi: latih agent reinforcement learning, lalu uji di data pasar
  historis.
- Catatan video: ini versi edukasi. Versi live ada di repo FinRL-Trading.

## 07 — ai-hedge-fund (Simulasi, Multi-Agent)

- Repo: https://github.com/virattt/ai-hedge-fund
- Bahasa: Python · Lisensi: MIT · Bintang (per video): 44 RB
- Biaya/akses: Gratis + API · Fungsi: Paper trading · Status: Paper
- Isi: agent investor buat analisis saham, backtest, dan paper trading
  pakai uang tiruan.
- Catatan video: untuk edukasi, bukan buat trading dengan uang asli.

## 08 — Vibe-Trading (Eksekusi, Opsional)

- Repo: https://github.com/NORDU/Vibe-Trading
- Bahasa: Python · Lisensi: MIT · Bintang (per video): 56 RB
- Biaya/akses: Gratis + API · Akses: Web/lokal · Fungsi: Riset + order
- Status: Live opsional
- Isi: riset dan backtest lewat chat. Live trading opsional lewat broker
  yang kamu hubungkan.
- Catatan video: live harus diaktifkan sendiri. Ada batas order dan
  tombol stop.

## 09 — LangAlpha (Eksekusi, Opsional)

- Repo: https://github.com/ginix-ai/LangAlpha
- Bahasa: Python · Lisensi: Apache-2.0 · Bintang (per video): 1,8 RB
- Biaya/akses: Gratis + API · Akses: Web/lokal · Fungsi: Riset + order
- Status: Live opsional
- Isi: agent riset pasar dan laporan, dengan akses broker sesuai izin
  yang kamu atur.
- Catatan video: izin broker bisa read-only, paper, atau live sesuai
  dukungannya.

## 10 — Hummingbot (Eksekusi, Kripto)

- Repo: https://github.com/hummingbot/hummingbot
- Bahasa: Python · Lisensi: Apache-2.0 · Bintang (per video): 21 RB
- Biaya/akses: Kode gratis · Akses: Lokal · Fungsi: Eksekusi bot
- Status: Paper / live
- Isi: bot trading kripto. Bagian AI-nya lewat Condor, repo terpisah
  buat strategi agent.
- Catatan video: ada mode paper tanpa API key. Live butuh API key
  exchange.
- Kaitan proyek: sudah tercatat di COMPLEMENTS.md sebagai referensi.

## Ringkasan video

| Fungsi | Repo / situs | Status |
| --- | --- | --- |
| Debat agent | TradingAgents | Simulasi |
| Riset saham | FinRobot | Riset |
| Sentimen | FinGPT | Riset |
| Backtest model | Qlib | Backtest |
| Kurasi repo | pensource.id.lol | Bonus |
| Latih agent | FinRL | Backtest |
| Paper trading | ai-hedge-fund | Paper |
| Riset + order | Vibe-Trading | Live opsional |
| Riset + order | LangAlpha | Live opsional |
| Eksekusi bot | Hummingbot | Paper / live |

Pesan penutup video: pilih sesuai kebutuhan. Mulai riset dan simulasi
dulu. **Backtest bukan jaminan hasil nyata.**
