# Pelengkap open source

Repo-repo di bawah ini BUKAN disalin ke repo ini. Masing-masing adalah
proyek besar milik orang lain dengan lisensinya sendiri, jadi yang
didokumentasikan di sini adalah identitas terverifikasi, fungsi, dan cara
memakainya bersama engine di repo ini. Semua repo di bawah terverifikasi
lewat GitHub pada 2026-11-01: publik, tidak diarsipkan, dan terakhir
diperbarui 31 Oktober 2026. Jumlah bintang dicatat per tanggal itu dan
bisa berubah; bintang menunjukkan popularitas, bukan profitabilitas.

## 1. Freqtrade — bot strategi kripto + backtest + ML

- Repo: [freqtrade/freqtrade](https://github.com/freqtrade/freqtrade)
- Bahasa: Python. Bintang: 56.218. Lisensi: GPL-3.0.
- Deskripsi resmi: "Free, open source crypto trading bot".
- Isi: strategi Python, backtesting, paper trading, dan modul FreqAI
  (machine learning yang melatih ulang dari data pasar). Mendukung 30+
  exchange lewat CCXT.
- Pelengkap untuk repo ini: gantikan atau bandingkan mesin strategi
  `unified_engine.py` dengan strategi Freqtrade yang sudah teruji, dan
  pakai backtester Freqtrade untuk menguji ide sebelum masuk engine ini.
  Cocok untuk venue Indodax/Gate (spot).

## 2. Hummingbot — market making dan arbitrase multi-venue

- Repo: [hummingbot/hummingbot](https://github.com/hummingbot/hummingbot)
- Bahasa: Python. Bintang: 20.875. Lisensi: Apache-2.0.
- Deskripsi resmi: "Open source software that helps you create and deploy
  high-frequency crypto trading bots".
- Isi: konektor 50+ exchange CEX dan DEX, strategi market making,
  arbitrase, dan lapisan agen AI (Condor).
- Pelengkap untuk repo ini: referensi arsitektur market making dan
  arbitrase lintas venue — bagian yang belum ada di engine ini, yang
  sekarang fokus ke eksekusi satu arah dengan filter tren dan risiko.

## 3. Jesse — riset strategi dan backtest yang ketat

- Repo: [jesse-ai/jesse](https://github.com/jesse-ai/jesse)
- Bahasa: Python. Bintang: 8.744. Lisensi: MIT.
- Deskripsi resmi: "An advanced crypto trading bot written in Python".
- Isi: framework riset strategi dengan backtesting tanpa look-ahead bias,
  optimasi, dan server MCP untuk agen AI.
- Pelengkap untuk repo ini: validasi strategi dengan standar Jesse
  (tanpa bias melihat ke depan, uji Monte Carlo) sebelum strategi
  apa pun naik ke mode live. Ini obat overfitting untuk backtest
  "ribuan percobaan" yang direncanakan repo ini.

## 4. TradingAgents — firma trading multi-agen LLM

- Repo: [TauricResearch/TradingAgents](https://github.com/TauricResearch/TradingAgents)
- Bahasa: Python. Bintang: 119.018. Lisensi: Apache-2.0.
- Deskripsi resmi: "TradingAgents: Multi-Agents LLM Financial Trading
  Framework".
- Isi: simulasi firma trading — analis fundamental, sentimen, berita,
  dan teknikal, lalu debat bull vs bear, proposal trader, veto tim
  risiko, dan persetujuan manajer portofolio. Dibangun dengan LangGraph.
- Pelengkap untuk repo ini: pola debat multi-analis yang direncanakan
  untuk modul analis engine ini (analisis berita dan sentimen sekarang
  masih kata kunci v1). Model NVIDIA NIM yang sudah terhubung bisa
  memainkan peran analis di pola seperti ini.

## 5. OctoBot — bot UI + Grid, DCA, dan mode AI

- Repo: [Drakkar-Software/OctoBot](https://github.com/Drakkar-Software/OctoBot)
- Bahasa: Python. Bintang: 6.879. Lisensi: GPL-3.0.
- Deskripsi resmi: "Free open source crypto trading bot to automate AI,
  Grid, DCA and TradingView strategies on Binance, Hyperliquid and 15+
  exchanges, with a simple interface."
- Isi: strategi Grid, DCA, sinyal TradingView, mode AI, dan paper
  trading, dengan antarmuka yang lebih ramah pemula.
- Pelengkap untuk repo ini: pembanding strategi Grid/DCA siap pakai dan
  referensi antarmuka — engine ini sekarang tanpa UI (dijalankan dari
  terminal, hasilnya dibaca dari dashboard statis).

## 6. CCXT — pustaka API exchange terpadu

- Repo: [ccxt/ccxt](https://github.com/ccxt/ccxt)
- Bahasa: Python (juga JavaScript/TypeScript, PHP, dan lainnya).
  Bintang: 44.650.
- Deskripsi resmi: "A unified trading API with more than 100 crypto
  exchanges and prediction markets".
- Isi: satu antarmuka untuk 100+ exchange dan prediction market.
- Pelengkap untuk repo ini: SUDAH dipakai — `bot-engine/ccxt_adapter.py`
  berdiri di atas CCXT (Indodax + Gate teruji live pada data publik).
  CCXT adalah alasan engine ini bisa menambah venue baru tanpa menulis
  konektor dari nol. Catatan: di VM dengan egress proxy, CCXT butuh
  `session.trust_env=True`.

## Catatan jujur

- Semua proyek di atas adalah alat riset dan belajar, bukan mesin
  pencetak uang. Penulisnya sendiri menyatakan hasil backtest tidak
  menjamin hasil live: biaya, slippage, dan perubahan rezim pasar
  menggerus hasil simulasi.
- Aturan pakai yang sama berlaku untuk semuanya: uji di paper trading
  dulu, verifikasi sendiri setiap angka, dan jangan memakai uang yang
  tidak siap hilang.
