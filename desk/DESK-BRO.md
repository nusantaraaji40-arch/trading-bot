# DESK BRO v1 — Meja Trading Paper 8 Agen (GRATIS)

Meja trading paper yang meniru pembagian kerja "8 agen" dari video desk
trading: tiap agen punya satu tugas, satu verdict, dan tidak ada yang
bekerja sendirian tanpa gerbang. Ditulis dari nol untuk proyek ini
(bukan salinan konten video apa pun).

## Delapan agen

| Agen | Nama | Tugas | Keluaran |
|---|---|---|---|
| Bro 1 | CHIEF | Keputusan akhir | BUY / NO_TRADE / JUAL / TAHAN |
| Bro 2 | SCAN | Saring market aktif dari Gamma | Daftar kandidat |
| Bro 3 | VET | Saring scam/rug + syarat minimum | LOLOS / gagal + alasan |
| Bro 4 | SOCIAL | Skor kata kunci sentimen/berita | Skor (negatif = buruk) |
| Bro 5 | SIZE | Besar posisi | Jumlah lembar paper |
| Bro 6 | FILLS | Eksekusi PAPER ONLY | Entri ledger paper |
| Bro 7 | RISK | TP/SL/kill-switch | TP / SL / KILL_SWITCH / HOLD |
| Bro 8 | CRAWLER | Kumpul data publik gratis | Market + kurs |

Aturan Bro 6: **tidak pernah order nyata.** Satu-satunya "eksekusi" v1
adalah menulis entri paper ke `paper_desk_ledger.json`. Tidak ada wallet,
tidak ada tanda tangan, tidak ada key.

## Sumber data (gratis saja)

- Gamma API Polymarket (publik, tanpa key): daftar market aktif.
- CoinGecko gratis: kurs USDC/IDR untuk konversi paper ke rupiah.
- Judul berita/RSS (bila diumpankan ke Bro 4): hitung kata kunci saja,
  bukan model AI dan bukan prediksi.

Yang TIDAK dipakai v1: run Actor Apify (berbayar), API berbayar apa pun,
dan data dari sumber yang butuh login/key.

## Aturan paper (sama dengan aturan demo proyek)

- Modal virtual Rp25.000 per venue/aset; trade pertama Rp5.000.
- Bro 3 meloloskan market hanya bila: aktif, belum tutup, likuiditas
  >= $500, spread <= 20% (bila data spread ada), dan ada harga ask valid.
- Bro 5: anggaran = min(Rp5.000, kas); 0 lembar bila hasil < 5 lembar.
- Bro 7 (prioritas: kill-switch > SL > TP > HOLD):
  SL -5%, TP +15% jual habis, kill-switch bila total paper
  (kas + nilai posisi) <= Rp21.250.
- Trigger diukur ask-ke-ask; hasil jual dihitung di harga bid.
- Guard: tidak ada beli baru selagi posisi paper masih OPEN.
- Fee TIDAK dimodelkan di v1: P&L paper yang dilaporkan adalah P&L
  kotor sebelum fee. Jangan bandingkan langsung dengan P&L live.

## Cara menjalankan

```
python3 desk/bro_desk.py
```

Satu perintah = satu siklus, lalu berhenti. Keluaran: verdict tiap Bro
dan aksi akhir (BUY_PAPER / SELL_PAPER_xx / HOLD / NO_TRADE / NO_DATA).

Tes (tanpa jaringan):

```
python3 desk/test_bro_desk.py
```

## Yang v1 BISA dan TIDAK BISA

BISA:
- Menjalankan satu siklus paper end-to-end (cari → vet → ukur →
  putuskan → catat paper) dengan aturan yang eksplisit dan bisa dites.
- Berjalan dengan Python stdlib saja, ringan untuk server gratis 512MB.
- Melaporkan NO_TRADE / NO_DATA secara jujur saat data gagal atau
  gerbang tidak lolos — tidak menebak harga.

TIDAK BISA (jangan dianggap bisa):
- 24/7. Skrip ini one-shot. Jalan terus hanya bila user menjalankan
  loop ini di server miliknya sendiri. VM Muse tidak dipakai untuk live.
- Menjamin profit. Paper di proyek ini sejauh ini belum profit; v1
  adalah alat disiplin (aturan + gerbang), bukan mesin untung.
- Menggantikan modul venue yang sudah ada (paper_trade.py,
  paper_exit.py, dan modul venue lain tetap menjadi acuan per-venue;
  desk v1 memakai aturan generiknya sendiri untuk ledger desk).
- Memberi harga exit yang presisi: v1 memakai harga Gamma sebagai
  proksi bid karena market list Gamma tidak membawa order book.
  P&L exit v1 bersifat perkiraan dan cenderung optimistis dibanding
  book CLOB nyata. Untuk exit presisi, pakai paper_exit.py.

## Upgrade visual: belakangan, sesuai kesepakatan user

Tampilan "keren seperti gambar desk" TIDAK dibangun di v1. Urutan yang
disepakati: mesin dulu, tampilan belakangan — upgrade visual menyusul
setelah trade paper berhasil. Dokumen ini sengaja hanya berisi logika.
