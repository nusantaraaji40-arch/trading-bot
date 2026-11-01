"""Loop live Polymarket — 3 kategori dalam SATU proses jangka panjang.

Proses ini jalan TERUS setelah Start di server pemilik (24/7, bukan
one-shot): tiap poll ia memonitor posisi, menjual di trigger, lalu
menyaring pasar berikut. Tidak ada dependensi pada Muse — Muse tidak
jalan 24/7; server pemilik yang jalan. Bila proses di-Start ulang, ia
melanjutkan dari state JSON terakhir (tidak beli ganda, tidak lupa
posisi). Server harus tetap online; login panel tiap 10 hari agar
server gratis tidak berhenti (pengingat diajukan terpisah).

GAYA POSISI: SCALPING (konfirmasi user 2026-11-02).
- Pegang singkat: pasar jam-jaman (Up/Down BUKAN menitan), bukan
  posisi harian yang ditahan lama.
- TP +20% (Up/Down) langsung JUAL HABIS lalu ROTASI SEGERA: begitu
  penutupan TERVERIFIKASI dan state tersimpan, fase saring pada poll
  yang SAMA langsung mencari pasar berikut — tanpa jeda idle 600
  detik antara tutup dan saring berikut.
- SL -7% POTONG CEPAT: pecundang tidak ditahan berharap balik arah,
  KECUALI pengecualian tahan (di bawah) yang kondisinya definitif.
- BATAS KERAS -12%: posisi menyentuh -12% = JUAL APA PUN YANG
  TERJADI, tanpa pengecualian, tanpa menunggu potensi naik.
  Prioritas trigger: kill-switch total 15% > batas keras -12% >
  SL -7% (dengan pengecualian tahan) > TP.
- PENGECUALIAN TAHAN (definitif, bisa dites, bukan perasaan): posisi
  di zona SL (-7% sampai -12%) BOLEH ditahan HANYA bila ketiga
  syarat terpenuhi JELAS: (1) momentum jangka pendek sudah berbalik
  positif, (2) sinyal terbaru tidak negatif (gerbang sinyal kategori
  itu masih lolos untuk pasar posisi), (3) harga sudah memantul
  >= 2% dari titik terendah sejak entry. Bila satu syarat saja
  tidak terpenuhi JELAS -> default = JUAL di -7%.
- TIDAK ADA averaging down / tambah posisi pada posisi merugi:
  beli hanya bila kategori IDLE (tidak ada posisi, tidak ada
  pending). Satu posisi per kategori, selalu.
- TIDAK ADA menahan posisi melewati resolusi tanpa rencana keluar:
  cek resolusi jalan DULU tiap poll (closed=True + harga decisif
  >= 0,999 -> settle), sebelum cek book/exit.
- KEJUJURAN: keluar cepat TERGANTUNG likuiditas bid. Bila book
  kosong / tanpa bid, posisi berstatus CANNOT_EXIT dan loop menunggu
  bid muncul (tidak memaksakan jual di harga nol). Fee + spread
  menggerus untung kecil pada anggaran $1 — P&L dihitung BERSIH
  setelah estimasi fee sebelum diklaim untung.

ATURAN KAS (filosofi user: untung dikit-dikit jadi bukit, lalu gunung):
- Kas per kategori BERGULIR: modal awal + hasil realisasi (menang /
  kalah) menumpuk di kas kategori itu.
- Ukuran beli per trade = min(first_trade_usd, kas tersedia), dengan
  tetap mematuhi min order 5 + fee. Keuntungan MENUMPUK di kas
  (bukit), tetapi RISIKO PER TRADE TIDAK ikut membesar (tetap
  dibatasi first_trade_usd). Loop TIDAK PERNAH memakai seluruh kas
  yang membesar untuk satu beli.
- Bukit hanya terbentuk bila menang bersih melampaui kalah + fee
  dalam jangka panjang — BUKAN janji.

PARAMETER (persetujuan awal 23:22 WIB 2026-11-01, diubah user
2026-11-02): SL normal -7% + batas keras -12% untuk SEMUA kategori
(FINAL, terkonfirmasi 2026-11-02; MENGGANTIKAN SL 10% yang sempat
ditetapkan sebelumnya, dan SL 5% persetujuan awal). TP TIDAK berubah
(Up/Down +20% jual habis; cuaca/bola TP1 +10% separuh / TP2 +15%
sisa). Kill-switch total tetap 15% (pengaman level akun, berbeda
dari batas per trade). Prioritas: KS 15% > batas keras -12% >
SL -7% (dengan pengecualian tahan) > TP. File persetujuan deploy
(LIVE_APPROVED_LOOP.txt) WAJIB menulis KEDUA angka (SL 7% dan batas
keras 12%) + kill-switch 15% — gerbang menolak persetujuan yang
tidak menyebut ketiganya. File params.json + LIVE_APPROVED.txt paket
v4 di server TIDAK diubah (paket berbeda, verifikasinya sudah lolos).

PERAN AGEN (pola DESK BRO, sebagai fungsi kode + log per peran,
BUKAN panggilan model LLM berbayar, BUKAN key API baru):
- Bro 8 CRAWLER: kumpul data (Gamma + CLOB book).
- Bro 2 SCAN: cari + urutkan kandidat pasar.
- Bro 3 VET: filter (likuiditas, spread, tag, durasi, min order, fee).
- Bro 4 SOCIAL: gerbang sinyal (RSS berita / prakiraan cuaca).
- Bro 5 SIZE: ukuran posisi (budget bergulir + fee + min order).
- Bro 1 CHIEF: putusan akhir (beli hanya bila semua peran lolos).
- Bro 6 FILLS: eksekusi (bangun + post + verifikasi isi).
- Bro 7 RISK: trigger jual (KS > SL > TP) + kill-switch.

GERBANG LIVE (semua harus lolos SEBELUM order apa pun):
1. Flag --live. 2. Environment LIVE_TRADING=1.
3. File LIVE_APPROVED_LOOP.txt ada di folder skrip, berisi teks
   persetujuan yang menyebut SL 10% + kill-switch 15%.
4. File loop_params.json ada + valid (3 kategori, polygon, USDC).
5. Geoblock dari mesin ini = allowed (bukan VPN/proxy).
6. POLY_PRIVATE_KEY ada + SDK terpasang + alamat turunan = signer.
7. Tidak ada state kategori yang berstatus kill_switch_hit (KS yang
   sudah kena menghentikan loop sampai pemilik meninjau + mereset
   manual — restart otomatis tidak boleh menghidupkan kembali loop
   yang di-KS).

MODE:
- --check (default): cek gerbang + params + state, TANPA order,
  TANPA post. Keluar 0 = siap, 2 = konfigurasi belum lengkap,
  1 = verifikasi signer/state gagal.
- --dry-run: bangun + tanda tangani order, JANGAN POST. Bila
  --dry-token/--dry-price/--dry-size/--dry-side diberikan: uji
  antarmuka murni dengan order itu. Bila tidak: satu pass screening
  mekanis + sizing (tanpa gerbang sinyal — dry-run tidak membeli)
  lalu bangun + tanda tangani kandidat pertama. Tidak butuh
  LIVE_TRADING / file persetujuan (ini verifikasi pra-persetujuan).
  Keluar 0 = dry-run selesai (termasuk bila tidak ada kandidat).
- --live: gerbang penuh + loop selamanya. Keluar 0 = berhenti bersih
  (Ctrl+C / panel Stop), 4 = berhenti karena kill-switch, 2 = gerbang
  gagal, 1 = error fatal.

KEGAGALAN DEFAULT = SKIP / BERHENTI AMAN, bukan trading:
- Input luar tak dikenal (Gamma/CLOB/RSS/prakiraan) = SKIP + log,
  bukan crash, bukan beli buta.
- Error jaringan = tunggu poll berikut, bukan crash.
- Order error TIDAK di-retry buta: cek dulu (open orders + posisi),
  lalu coba metode lain bila perlu, lalu log + berhenti aman bila
  tetap gagal.
- Nol gagal TIDAK BISA dijamin — yang dijamin adalah gagal AMAN
  (skip/berhenti), bukan gagal merugikan.
"""

import argparse
import json
import math
import os
import re
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import order_wiring  # noqa: E402
import signals  # noqa: E402

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

GAMMA_MARKETS = "https://gamma-api.polymarket.com/markets"
CLOB_BOOK = "https://clob.polymarket.com/book"
GEOBLOCK_URL = "https://polymarket.com/api/geoblock"

USER_AGENT = "polymarket-live-loop/1.0"
TIMEOUT = 30

# Alamat publik akun utama (bukan rahasia). Dipakai hanya untuk
# identitas + log; private key TIDAK PERNAH ada di file ini.
SIGNER_WALLET_ADDRESS = order_wiring.SIGNER_WALLET_ADDRESS
PROFILE_WALLET_ADDRESS = order_wiring.PROFILE_WALLET_ADDRESS

CATEGORIES = {
    "updown": {"tag_id": 102127, "label": "Kripto Up or Down",
               "exit": "updown"},
    "weather": {"tag_id": 84, "label": "Cuaca", "exit": "ladder"},
    "soccer": {"tag_id": 100350, "label": "Bola", "exit": "ladder"},
}

# Ambang screening mekanis (didokumentasikan, bukan disembunyikan).
MIN_LIQUIDITY_USD = 500.0
MAX_SPREAD_PCT = 20.0
WARN_SPREAD_PCT = 10.0
MAX_CANDIDATES = 8
# Up/Down "jam-jaman": tolak yang menitan. Gamma startDate adalah
# waktu listing (bukan window event), jadi gerbang operatifnya:
# (a) pola "N min/menit" di pertanyaan -> tolak; (b) durasi
# end-start < 50 menit -> tolak; (c) rentang jam di judul
# ("1:30PM-1:45PM") -> hitung window-nya, < 50 menit -> tolak.
# Selebihnya (jam-jaman, harian) diterima — didokumentasikan apa
# adanya di README. (c) ditambahkan setelah temuan dry-run
# 2026-11-02: pasar 1:30PM-1:45PM lolos karena tidak mengandung
# kata "min" dan startDate listing-nya jauh dari window event.
UPDOWN_MIN_DURATION_MIN = 50.0
MINUTE_PATTERN = re.compile(r"\b\d+\s*(?:-|–)?\s*min(?:ute)?s?\b",
                            re.IGNORECASE)
TIME_RANGE_PATTERN = re.compile(
    r"(\d{1,2}):(\d{2})\s*([AP])\.?M\.?\s*[-–]\s*"
    r"(\d{1,2}):(\d{2})\s*([AP])\.?M\.?",
    re.IGNORECASE)

# Default parameter (CONTOH yang mengikuti persetujuan + perubahan
# FINAL user 2026-11-02: SL 7% + batas keras 12%). Nilai yang BERLAKU
# adalah loop_params.json milik pemilik saat deploy, bukan default ini.
DEFAULTS = {
    "updown": {"sl_pct": 7.0, "sl_hard_cap_pct": 12.0, "tp_pct": 20.0,
               "kill_switch_pct": 15.0},
    "weather": {"sl_pct": 7.0, "sl_hard_cap_pct": 12.0, "tp1_pct": 10.0,
                "tp2_pct": 15.0, "kill_switch_pct": 15.0},
    "soccer": {"sl_pct": 7.0, "sl_hard_cap_pct": 12.0, "tp1_pct": 10.0,
               "tp2_pct": 15.0, "kill_switch_pct": 15.0},
}

EPS = 1e-9
POLL_HOLDING_DEFAULT = 60
POLL_IDLE_DEFAULT = 600
MAX_PENDING_POLLS = 5
MAX_SELL_RESTING_POLLS = 3
KS_VERIFY_POLLS = 10
KS_VERIFY_SLEEP = 30


# --- Log -------------------------------------------------------------------

class Logger:
    """Log ke stdout + file loop.log (best-effort; gagal log tidak
    boleh menghentikan loop)."""

    def __init__(self, log_path=None):
        self.log_path = log_path

    def log(self, msg):
        line = f"[{datetime.now(timezone.utc).isoformat()}] {msg}"
        print(line, flush=True)
        if self.log_path:
            try:
                with open(self.log_path, "a") as f:
                    f.write(line + "\n")
            except Exception:
                pass

    def role(self, bro, name, msg):
        self.log(f"[Bro {bro} {name}] {msg}")


# --- HTTP publik ------------------------------------------------------------

def http_get_json(url, timeout=TIMEOUT):
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read().decode("utf-8"))


def parse_geoblock(payload):
    if isinstance(payload, dict):
        if payload.get("blocked") is True:
            return "blocked"
        if payload.get("blocked") is False:
            return "allowed"
    return "unknown"


# --- State (atomik) ----------------------------------------------------------

def state_path(state_dir, category):
    return os.path.join(state_dir, f"state_{category}.json")


def history_path(state_dir):
    return os.path.join(state_dir, "history.jsonl")


def new_category_state(category, modal_usd):
    return {
        "category": category,
        "status": "IDLE",  # IDLE | OPEN | PARTIAL | PENDING_BUY |
        # PENDING_SELL | STOPPED
        "cash_usd": round(float(modal_usd), 4),
        "realized_usd": 0.0,
        "position": None,
        "pending_order": None,
        "last_token_id": None,
        "last_close_poll": None,
        "stopped": False,
        "stop_reason": None,
        "kill_switch_hit": False,
        "corrupt": False,
        "updated": datetime.now(timezone.utc).isoformat(),
    }


def atomic_write_json(path, obj):
    """Tulis JSON secara atomik: file temp + ganti nama.

    Bila proses mati mendadak di tengah tulis, file lama tetap utuh
    (temp yang rusak tidak pernah menjadi state)."""
    tmp = f"{path}.tmp.{os.getpid()}"
    with open(tmp, "w") as f:
        json.dump(obj, f, indent=2)
        f.flush()
        os.fsync(f.fileno())
    os.replace(tmp, path)


def save_state(state_dir, st):
    st["updated"] = datetime.now(timezone.utc).isoformat()
    atomic_write_json(state_path(state_dir, st["category"]), st)


def load_state(state_dir, category, modal_usd):
    """Muat state; file tidak ada -> state baru; file RUSAK -> state
    bertanda corrupt (kategori itu TIDAK ditradingkan sampai pemilik
    memperbaiki/mereset manual — jangan menebak isi state rusak)."""
    path = state_path(state_dir, category)
    if not os.path.isfile(path):
        return new_category_state(category, modal_usd)
    try:
        with open(path) as f:
            st = json.load(f)
        if not isinstance(st, dict) or st.get("category") != category:
            raise ValueError("bentuk state tidak dikenal")
        for key, default in new_category_state(category, modal_usd).items():
            st.setdefault(key, default)
        return st
    except Exception as e:
        st = new_category_state(category, modal_usd)
        st["corrupt"] = True
        st["stopped"] = True
        st["stop_reason"] = f"state rusak ({type(e).__name__}) — " \
            "kategori tidak ditradingkan sampai diperbaiki manual"
        return st


def append_history(state_dir, record):
    record = dict(record)
    record["timestamp"] = datetime.now(timezone.utc).isoformat()
    try:
        with open(history_path(state_dir), "a") as f:
            f.write(json.dumps(record) + "\n")
    except Exception:
        pass


# --- Validasi params (murni, tanpa I/O) --------------------------------------

def _is_number(x):
    return isinstance(x, (int, float)) and not isinstance(x, bool)


def validate_loop_params(data):
    """Mengembalikan (errors, warnings). errors kosong = lolos.

    Aturan: objek; "categories" berisi ketiganya (updown, weather,
    soccer); tiap kategori: chain polygon, collateral USDC,
    modal_usd > 0, 0 < first_trade_usd <= modal_usd, sl 1-50,
    sl_hard_cap 1-50 DAN > sl_pct (batas keras harus lebih dalam
    dari SL normal, kalau tidak zona pengecualian tahan kosong),
    kill-switch 5-50, min_order_size int >= 1; updown: tp 1-50;
    weather/soccer: tp1 1-50, tp2 1-50, tp2 >= tp1. TP < SL =
    peringatan (bukan penolakan, cermin paket v4). Poll: holding
    >= 10 detik, idle >= 60 detik (bila diisi).
    """
    errors, warnings = [], []
    if not isinstance(data, dict):
        return ["params harus berupa objek JSON"], warnings
    cats = data.get("categories")
    if not isinstance(cats, dict):
        return ["params.categories harus berupa objek"], warnings
    for cat in ("updown", "weather", "soccer"):
        if cat not in cats:
            errors.append(f"kategori {cat} tidak ada di params")
            continue
        p = cats[cat]
        if not isinstance(p, dict):
            errors.append(f"params {cat} harus berupa objek")
            continue
        if p.get("chain") != "polygon":
            errors.append(f"{cat}: chain harus polygon")
        if p.get("collateral") != "USDC":
            errors.append(f"{cat}: collateral harus USDC")
        modal = p.get("modal_usd")
        if not _is_number(modal) or modal <= 0:
            errors.append(f"{cat}: modal_usd harus angka > 0")
        first = p.get("first_trade_usd")
        if not _is_number(first) or first <= 0:
            errors.append(f"{cat}: first_trade_usd harus angka > 0")
        elif _is_number(modal) and first > modal:
            errors.append(f"{cat}: first_trade_usd harus <= modal_usd")
        sl = p.get("sl_pct")
        if not _is_number(sl) or not (1 <= sl <= 50):
            errors.append(f"{cat}: sl_pct harus 1-50")
        hard = p.get("sl_hard_cap_pct")
        if not _is_number(hard) or not (1 <= hard <= 50):
            errors.append(f"{cat}: sl_hard_cap_pct harus 1-50")
        elif _is_number(sl) and hard <= sl:
            errors.append(f"{cat}: sl_hard_cap_pct harus > sl_pct "
                          "(batas keras lebih dalam dari SL normal)")
        ks = p.get("kill_switch_pct")
        if not _is_number(ks) or not (5 <= ks <= 50):
            errors.append(f"{cat}: kill_switch_pct harus 5-50")
        min_size = p.get("min_order_size")
        if not isinstance(min_size, int) or isinstance(min_size, bool) \
                or min_size < 1:
            errors.append(f"{cat}: min_order_size harus int >= 1")
        if cat == "updown":
            tp = p.get("tp_pct")
            if not _is_number(tp) or not (1 <= tp <= 50):
                errors.append(f"{cat}: tp_pct harus 1-50")
            elif _is_number(sl) and tp < sl:
                warnings.append(f"{cat}: TP {tp}% < SL {sl}% "
                                "(peringatan, bukan penolakan)")
        else:
            tp1, tp2 = p.get("tp1_pct"), p.get("tp2_pct")
            if not _is_number(tp1) or not (1 <= tp1 <= 50):
                errors.append(f"{cat}: tp1_pct harus 1-50")
            if not _is_number(tp2) or not (1 <= tp2 <= 50):
                errors.append(f"{cat}: tp2_pct harus 1-50")
            elif _is_number(tp1) and tp2 < tp1:
                errors.append(f"{cat}: tp2_pct harus >= tp1_pct")
            if _is_number(sl) and _is_number(tp1) and tp1 < sl:
                warnings.append(f"{cat}: TP1 {tp1}% < SL {sl}% "
                                "(peringatan, bukan penolakan)")
    for key, lo in (("poll_holding_s", 10), ("poll_idle_s", 60)):
        if key in data and (not isinstance(data[key], int)
                            or isinstance(data[key], bool)
                            or data[key] < lo):
            errors.append(f"{key} harus int >= {lo}")
    return errors, warnings


def load_loop_params(path):
    with open(path) as f:
        data = json.load(f)
    errors, warnings = validate_loop_params(data)
    return data, errors, warnings


# --- Gerbang live --------------------------------------------------------------

def approval_text_ok(text):
    """Persetujuan loop WAJIB menyebut SL 7% + batas keras 12% +
    kill-switch 15%.

    SL 7% + batas keras 12% adalah aturan rugi FINAL user 2026-11-02
    (menggantikan SL 10% yang sempat ditetapkan, dan SL 5%
    persetujuan awal). Persetujuan lama (v4, SL 5%) maupun teks yang
    hanya menyebut SL 10% TIDAK BOLEH dipakai untuk loop ini —
    gerbang menolaknya supaya parameter yang berjalan selalu sesuai
    persetujuan yang dibaca.
    """
    compact = re.sub(r"\s+", "", (text or "").lower())
    has_sl7 = "sl7%" in compact or "sl-7%" in compact
    has_hard12 = "12%" in compact
    has_ks15 = "15%" in compact
    return has_sl7 and has_hard12 and has_ks15


def check_gates(script_dir, state_dir, logger, params_path=None,
                approval_path=None):
    """Semua gerbang live. Mengembalikan (params, client) atau None
    (sudah log alasannya). Keluar: pemanggil memakai exit 2."""
    if os.environ.get("LIVE_TRADING") != "1":
        logger.log("Gerbang live gagal: LIVE_TRADING=1 belum diset.")
        return None
    approved_path = approval_path or os.path.join(
        script_dir, "LIVE_APPROVED_LOOP.txt")
    if not os.path.isfile(approved_path):
        logger.log("Gerbang live gagal: LIVE_APPROVED_LOOP.txt tidak "
                   "ditemukan di folder skrip (file persetujuan loop, "
                   "BERBEDA dari LIVE_APPROVED.txt paket v4).")
        return None
    with open(approved_path) as f:
        approval = f.read()
    logger.log(f"Persetujuan loop tercatat: {approval.strip()[:300]}")
    if not approval_text_ok(approval):
        logger.log("Gerbang live gagal: persetujuan loop harus menyebut "
                   "SL 7% + batas keras 12% + kill-switch 15% (aturan "
                   "rugi FINAL user 2026-11-02; persetujuan lama SL 5% "
                   "atau SL 10% tidak berlaku untuk loop ini).")
        return None
    params_path = params_path or os.path.join(script_dir,
                                              "loop_params.json")
    if not os.path.isfile(params_path):
        logger.log("Gerbang live gagal: loop_params.json tidak ditemukan "
                   "di folder skrip.")
        return None
    try:
        params, errors, warnings = load_loop_params(params_path)
    except Exception as e:
        logger.log(f"Gerbang live gagal: loop_params.json tidak bisa "
                   f"dibaca ({type(e).__name__}).")
        return None
    if errors:
        for e in errors:
            logger.log(f"loop_params.json DITOLAK: {e}")
        return None
    for w in warnings:
        logger.log(f"loop_params.json peringatan: {w}")
    try:
        payload = http_get_json(GEOBLOCK_URL, timeout=15)
        geo = parse_geoblock(payload)
    except Exception as e:
        logger.log(f"Gerbang live gagal: cek geoblock gagal "
                   f"({type(e).__name__}) — jangan lanjut tanpa bukti "
                   "geoblock.")
        return None
    logger.log(f"Geoblock dari mesin ini: {geo}.")
    if geo == "blocked":
        logger.log("Gerbang live gagal: mesin ini diblokir untuk order — "
                   "pindahkan proses, bukan dengan VPN/proxy.")
        return None
    private_key = os.environ.get(order_wiring.ENV_PRIVATE_KEY)
    if not private_key:
        logger.log("Gerbang live gagal: POLY_PRIVATE_KEY belum diset.")
        return None
    if not order_wiring.sdk_available():
        logger.log("Gerbang live gagal: SDK resmi (modul polymarket) "
                   "belum terpasang.")
        return None
    client = order_wiring.build_sdk_client(private_key)
    if client is None:
        logger.log("Gerbang live gagal: klien SDK tidak bisa dibangun "
                   "(cek log signer di atas).")
        return None
    # KS yang sudah kena menghentikan loop sampai ditinjau manual.
    for cat in CATEGORIES:
        modal = params["categories"][cat].get("modal_usd", 1.0)
        st = load_state(state_dir, cat, modal)
        if st.get("kill_switch_hit"):
            logger.log(f"Gerbang live gagal: kategori {cat} pernah kena "
                       "kill-switch — loop tidak di-Start ulang otomatis. "
                       "Tinjau state + posisi manual, lalu reset state "
                       "kategori itu bila memang ingin lanjut.")
            try:
                client.close()
            except Exception:
                pass
            return None
    logger.log("Semua gerbang live lolos.")
    return params, client


# --- Fungsi murni: trigger jual, resolusi, durasi, parse, sizing -----------

def decide_exit(entry_ask, bid, ask, remaining, tp1_done, total_value,
                start_value, *, kind, sl_pct, sl_hard_cap_pct,
                tp_pct=None, tp1_pct=None, tp2_pct=None, ks_pct=15.0,
                recovery=None):
    """Fungsi murni: (aksi, jumlah, alasan).

    Aksi: HOLD / SELL_PARTIAL / SELL_ALL. Alasan: HOLD / TP1 / TP2 /
    TP / SL / SL_HARD / SL_HOLD / KILL_SWITCH.
    Prioritas: KS (total kategori) > batas keras -12% (harga) >
    SL -7% (dengan pengecualian tahan) > TP2/TP > TP1.
    Trigger diukur ask-ke-ask (ask None -> pakai bid, dicatat
    pemanggil); hasil jual dihitung di BID. Epsilon float dipakai
    supaya harga TEPAT di level TP/SL/KS/batas keras tetap ke-trigger
    (bukan lolos karena 0.10*1.10 = 0.11000000000000001).

    recovery: dict {"momentum_positive": bool, "signal_ok": bool,
    "bounced": bool} atau None. Pengecualian tahan: di zona SL
    (di bawah level SL tapi di atas level batas keras), posisi
    DITAHAN (HOLD/SL_HOLD) HANYA bila recovery["all"] True —
    ketiga syarat terpenuhi JELAS. Bila recovery None atau satu
    syarat saja False -> default JUAL di SL. Di bawah level batas
    keras -> JUAL TANPA PENGECUALIAN (recovery diabaikan).
    """
    if remaining <= 0:
        return "HOLD", 0, "HOLD"
    trigger = ask if ask is not None else bid
    if trigger is None:
        return "HOLD", 0, "HOLD"
    if total_value <= start_value * (1 - ks_pct / 100) + EPS:
        return "SELL_ALL", remaining, "KILL_SWITCH"
    hard_level = entry_ask * (1 - sl_hard_cap_pct / 100)
    sl_level = entry_ask * (1 - sl_pct / 100)
    if trigger <= hard_level + EPS:
        return "SELL_ALL", remaining, "SL_HARD"
    if trigger <= sl_level + EPS:
        if isinstance(recovery, dict) and recovery.get("all") is True:
            return "HOLD", 0, "SL_HOLD"
        return "SELL_ALL", remaining, "SL"
    if kind == "updown":
        if tp_pct is not None and \
                trigger >= entry_ask * (1 + tp_pct / 100) - EPS:
            return "SELL_ALL", remaining, "TP"
    else:
        if tp1_done and tp2_pct is not None and \
                trigger >= entry_ask * (1 + tp2_pct / 100) - EPS:
            return "SELL_ALL", remaining, "TP2"
        if (not tp1_done) and tp1_pct is not None and \
                trigger >= entry_ask * (1 + tp1_pct / 100) - EPS:
            qty = remaining // 2 if remaining >= 2 else remaining
            action = "SELL_PARTIAL" if qty < remaining else "SELL_ALL"
            return action, qty, "TP1"
    return "HOLD", 0, "HOLD"


def recovery_evidence(current_ask, prev_ask, lowest_ask, signal_ok,
                      history_prices=None):
    """Bukti pemulihan untuk pengecualian tahan di zona SL (murni).

    Ketiga syarat harus True JELAS, kalau tidak -> tahan DITOLAK:
    (1) momentum_positive: histori harga (bila ada >= 2 titik)
    menunjukkan kenaikan (titik terakhir > titik pertama); bila
    histori tidak ada, pakai ask saat ini > ask poll sebelumnya;
    bila keduanya tidak ada -> False (tidak bisa dibuktikan).
    (2) signal_ok: gerbang sinyal kategori itu masih lolos untuk
    pasar posisi (katalis masih ada / prakiraan masih mendukung).
    (3) bounced: ask saat ini >= titik terendah sejak entry * 1,02
    (pantulan >= 2% dari titik terendah).
    Mengembalikan dict {momentum_positive, signal_ok, bounced, all,
    evidence (str)}.
    """
    if history_prices and len(history_prices) >= 2:
        try:
            momentum = float(history_prices[-1]) > float(
                history_prices[0])
        except (TypeError, ValueError):
            momentum = False
    elif prev_ask is not None and current_ask is not None:
        try:
            momentum = float(current_ask) > float(prev_ask)
        except (TypeError, ValueError):
            momentum = False
    else:
        momentum = False
    bounced = False
    if current_ask is not None and lowest_ask:
        try:
            bounced = float(current_ask) >= float(lowest_ask) * 1.02
        except (TypeError, ValueError):
            bounced = False
    signal_ok = bool(signal_ok)
    all_ok = bool(momentum and signal_ok and bounced)
    evidence = (f"momentum_positif={momentum}, sinyal_ok={signal_ok}, "
                f"pantulan_2pct={bounced} -> tahan="
                f"{'YA' if all_ok else 'TIDAK (default JUAL)'}")
    return {"momentum_positive": momentum, "signal_ok": signal_ok,
            "bounced": bounced, "all": all_ok, "evidence": evidence}


def momentum_gate(ask, last_price, *, history_prices=None,
                  drop_threshold=0.03, history_drop_threshold=0.05):
    """Filter pra-beli ANTI-SL (murni): tolak sisi yang sedang turun
    menuju zona SL.

    Mengembalikan (ok, bukti_str). ok=False -> JANGAN BELI.
    - Bila histori harga tersedia (>= 2 titik): sisi turun bila
      titik terakhir <= titik pertama * (1 - history_drop_threshold)
      (turun >= 5% dalam window histori).
    - Proksi (selalu dicoba bila last_price ada): sisi turun bila
      ask saat ini <= last_price * (1 - drop_threshold) (ask sudah
      > 3% di bawah konsensus terakhir = penjual menekan turun).
    - Bila TIDAK ADA histori DAN TIDAK ADA last_price: momentum
      tidak bisa dinilai -> TIDAK OK (default aman: SKIP, bukan beli
      buta).
    Ini filter probabilitas, BUKAN ramalan: ia mengurangi frekuensi
    kena SL, tidak bisa menghilangkan kena SL sepenuhnya.
    """
    bad_reasons = []
    any_signal = False
    if history_prices and len(history_prices) >= 2:
        try:
            first, last = float(history_prices[0]), float(
                history_prices[-1])
            any_signal = True
            drop = (last - first) / first if first else 0.0
            if drop <= -history_drop_threshold:
                bad_reasons.append(
                    f"histori turun {drop * 100:.1f}% "
                    f"(>= {history_drop_threshold * 100:.0f}%)")
        except (TypeError, ValueError):
            pass
    if last_price is not None and ask is not None:
        try:
            any_signal = True
            if float(ask) <= float(last_price) * (1 - drop_threshold):
                bad_reasons.append(
                    f"ask {float(ask):.3f} sudah "
                    f"{(1 - float(ask) / float(last_price)) * 100:.1f}% "
                    f"di bawah konsensus terakhir "
                    f"{float(last_price):.3f}")
        except (TypeError, ValueError, ZeroDivisionError):
            pass
    if not any_signal:
        return False, ("momentum tidak bisa dinilai (tidak ada histori "
                       "dan tidak ada harga konsensus) — SKIP aman")
    if bad_reasons:
        return False, "sisi sedang turun: " + "; ".join(bad_reasons)
    return True, "momentum tidak menunjukkan penurunan jelas"


def decide_resolution(prices, held_index, closed):
    """Settle HANYA bila closed=True DAN harga decisif (>= 0,999).

    Mengembalikan (hasil, bukti): hasil = "WIN" (sisi yang dipegang
    menang) / "LOSS" / None (belum resolusi resmi — jangan settle,
    jangan tebak).
    """
    evidence = {"closed": closed, "outcomePrices": prices,
                "held_index": held_index}
    if closed is not True:
        return None, evidence
    if not isinstance(prices, (list, tuple)) or len(prices) < 2:
        return None, evidence
    try:
        p0, p1 = float(prices[0]), float(prices[1])
    except (TypeError, ValueError):
        return None, evidence
    vals = [p0, p1]
    if vals[held_index] >= 0.999:
        return "WIN", evidence
    if vals[1 - held_index] >= 0.999:
        return "LOSS", evidence
    return None, evidence


def updown_duration_ok(question, start_iso, end_iso):
    """Gerbang durasi Up/Down: tolak yang MENITAN.

    Mengembalikan (ok, alasan). Tolak bila: (a) pertanyaan menyebut
    durasi menit ("15 min", "15-minute", ...); (b) durasi end-start
    bisa dihitung dan < 50 menit; (c) judul mengandung rentang jam
    ("1:30PM-1:45PM") yang window-nya < 50 menit — rentang jam
    adalah bukti window event, karena Gamma startDate adalah waktu
    listing, bukan window event. Selebihnya diterima (jam-jaman,
    harian) — didokumentasikan: gerbang operatifnya adalah "bukan
    menitan", bukan "tepat 60 menit".
    """
    q = question or ""
    if MINUTE_PATTERN.search(q):
        return False, "Up/Down menitan (pola menit di pertanyaan) — " \
                      "ditolak, hanya jam-jaman"
    m = TIME_RANGE_PATTERN.search(q)
    if m:
        sh, sm, sap, eh, em, eap = m.groups()

        def _to_min(h, mi, ap):
            h = int(h) % 12
            if ap.upper() == "P":
                h += 12
            return h * 60 + int(mi)

        start_min = _to_min(sh, sm, sap)
        end_min = _to_min(eh, em, eap)
        if end_min <= start_min:
            end_min += 24 * 60
        window = end_min - start_min
        if window < UPDOWN_MIN_DURATION_MIN:
            return False, f"Up/Down window {window:.0f} menit < " \
                          f"{UPDOWN_MIN_DURATION_MIN:.0f} menit — " \
                          "ditolak, hanya jam-jaman"
    start = parse_iso(start_iso)
    end = parse_iso(end_iso)
    if start is not None and end is not None:
        dur_min = (end - start) / 60.0
        if dur_min < UPDOWN_MIN_DURATION_MIN:
            return False, f"Up/Down durasi {dur_min:.0f} menit < " \
                          f"{UPDOWN_MIN_DURATION_MIN:.0f} menit — " \
                          "ditolak, hanya jam-jaman"
    return True, "durasi Up/Down lolos (bukan menitan)"


def parse_iso(ts):
    try:
        return datetime.fromisoformat(
            (ts or "").replace("Z", "+00:00")).timestamp()
    except (ValueError, TypeError):
        return None


def parse_market(m):
    """Validasi + normalisasi satu objek Gamma. Gagal -> (None, alasan).

    Bentuk tak dikenal = SKIP + log, bukan crash, bukan beli buta.
    Syarat: question str; outcomes 2 sisi; clobTokenIds >= 2;
    active True; closed False; acceptingOrders True; endDate bisa
    diparse; orderMinSize int; feeSchedule rate + exponent angka.
    """
    if not isinstance(m, dict):
        return None, "objek market bukan dict"
    question = m.get("question")
    if not isinstance(question, str) or not question.strip():
        return None, "question kosong / bukan string"
    outcomes = m.get("outcomes")
    if isinstance(outcomes, str):
        try:
            outcomes = json.loads(outcomes)
        except ValueError:
            outcomes = None
    if not isinstance(outcomes, list) or len(outcomes) < 2 or \
            not all(isinstance(o, str) for o in outcomes[:2]):
        return None, f"{question}: outcomes tidak bisa diparse"
    token_ids = m.get("clobTokenIds")
    if isinstance(token_ids, str):
        try:
            token_ids = json.loads(token_ids)
        except ValueError:
            token_ids = []
    if not isinstance(token_ids, list) or len(token_ids) < 2 or \
            not all(isinstance(t, str) and t.isdigit()
                    for t in token_ids[:2]):
        return None, f"{question}: tidak ada CLOB token id valid"
    if m.get("active") is not True:
        return None, f"{question}: tidak active"
    if m.get("closed") is not False:
        return None, f"{question}: sudah closed"
    if m.get("acceptingOrders") is not True:
        return None, f"{question}: tidak acceptingOrders"
    end_ts = parse_iso(m.get("endDate"))
    if end_ts is None:
        return None, f"{question}: endDate tidak bisa diparse"
    min_size_raw = m.get("orderMinSize")
    fee_sched = m.get("feeSchedule") or {}
    if min_size_raw is None or fee_sched.get("rate") is None \
            or fee_sched.get("exponent") is None:
        return None, f"{question}: tidak termodelkan (min order / " \
                     "feeSchedule tidak tersedia)"
    try:
        min_size = int(min_size_raw)
        fee_rate = float(fee_sched["rate"])
        fee_exp = float(fee_sched["exponent"])
    except (TypeError, ValueError):
        return None, f"{question}: min order / fee tidak valid"
    try:
        liq = float(m.get("liquidity") or m.get("liquidityNum") or 0)
    except (TypeError, ValueError):
        liq = 0.0
    outcome_prices = m.get("outcomePrices")
    if isinstance(outcome_prices, str):
        try:
            outcome_prices = json.loads(outcome_prices)
        except ValueError:
            outcome_prices = None
    prices = None
    if isinstance(outcome_prices, list) and len(outcome_prices) >= 2:
        try:
            prices = [float(outcome_prices[0]), float(outcome_prices[1])]
        except (TypeError, ValueError):
            prices = None
    return {
        "question": question,
        "outcomes": outcomes[:2],
        "token_ids": token_ids[:2],
        "liquidity_usd": liq,
        "end_ts": end_ts,
        "end_iso": m.get("endDate"),
        "start_iso": m.get("startDate"),
        "game_start_iso": m.get("gameStartTime"),
        "min_size": min_size,
        "fee_rate": fee_rate,
        "fee_exponent": fee_exp,
        "fee_type": m.get("feeType"),
        "volume24hr": m.get("volume24hr"),
        "outcome_prices": prices,
    }, None


def estimate_fee(price, shares, fee_rate, exponent):
    """Estimasi fee taker (USD): rate * (p*(1-p))^exponent * shares."""
    if price <= 0 or price >= 1:
        return 0.0
    return fee_rate * (price * (1 - price)) ** exponent * shares


def size_trade(cash_budget, ask, fee_rate, exponent, min_shares):
    """Sizing beli: lembar yang mampu dibeli dari budget (setelah fee).

    Mengembalikan (shares, cost_usd, fee_usd) atau (None, alasan).
    Budget di sini SUDAH = min(first_trade_usd, kas) (aturan bukit:
    risiko per trade dibatasi first_trade_usd walau kas membesar).
    """
    if ask is None or ask <= 0 or ask >= 1:
        return None, "ask tidak valid untuk sizing"
    fee_ps = estimate_fee(ask, 1, fee_rate, exponent)
    cost_ps = ask + fee_ps
    if cost_ps <= 0:
        return None, "biaya per lembar tidak valid"
    shares = math.floor(cash_budget / cost_ps + 1e-9)
    if shares < min_shares:
        return None, f"hanya mampu {shares} lembar < min order " \
                     f"{min_shares} (budget ${cash_budget:.2f}, ask " \
                     f"{ask:.3f}, fee/lembar ${fee_ps:.4f})"
    # Koreksi pembulatan: total tidak boleh melebihi budget.
    while shares >= min_shares:
        cost = shares * ask
        fee = estimate_fee(ask, shares, fee_rate, exponent)
        if cost + fee <= cash_budget + 1e-9:
            return shares, round(cost, 4), round(fee, 4)
        shares -= 1
    return None, f"total biaya melebihi budget ${cash_budget:.2f} " \
                 f"pada min order {min_shares}"


def buy_budget(cash_usd, first_trade_usd):
    """Budget satu beli (aturan bukit): min(first_trade, kas).

    Kas membesar tidak membesarkan risiko per trade; kas mengecil
    (setelah kalah) mengecilkan budget (tidak boleh beli melebihi
    kas yang ada)."""
    return min(float(first_trade_usd), float(cash_usd))


# --- Peran agen (Bro 1-8) ---------------------------------------------------

# Bro 8 CRAWLER: kumpul data publik (Gamma + CLOB book). Gagal baca =
# exception ke pemanggil (pemanggil: tunggu poll berikut, bukan crash).

def bro8_fetch_markets(tag_id, logger):
    url = (f"{GAMMA_MARKETS}?limit=100&active=true&closed=false"
           f"&tag_id={tag_id}&order=volume24hr&ascending=false")
    markets = http_get_json(url)
    if not isinstance(markets, list):
        raise ValueError("respons Gamma /markets bukan list")
    logger.role(8, "CRAWLER", f"Gamma tag {tag_id}: {len(markets)} market "
                              "diterima")
    return markets


def bro8_fetch_book(token_id):
    """Book CLOB -> (best_bid_atau_None, best_ask_atau_None).

    Gagal baca / bentuk tak dikenal -> (None, None) (bukan crash).
    Beli hanya butuh ASK; BID boleh kosong (book satu sisi)."""
    try:
        book = http_get_json(f"{CLOB_BOOK}?token_id={token_id}")
    except Exception:
        return None, None
    try:
        bids = book.get("bids", []) or []
        asks = book.get("asks", []) or []
        bid = max(float(b["price"]) for b in bids) if bids else None
        ask = min(float(a["price"]) for a in asks) if asks else None
    except Exception:
        return None, None
    return bid, ask


def bro8_fetch_market_by_token(token_id):
    """Satu market Gamma berdasarkan clob_token_ids (untuk cek
    resolusi + endDate posisi). Gagal -> {} (pemanggil lanjut tanpa
    bukti resolusi, bukan settle buta)."""
    try:
        markets = http_get_json(
            f"{GAMMA_MARKETS}?limit=1&clob_token_ids={token_id}",
            timeout=20)
        if isinstance(markets, list) and markets:
            return markets[0]
    except Exception:
        pass
    return {}


# Bro 2 SCAN: urutkan kandidat (tanpa jaringan).

def bro2_rank_candidates(category, parsed_markets, now_ts):
    """Urutkan kandidat yang sudah lolos parse_market.

    - Up/Down: volume 24 jam terbesar dulu (durasi menitan sudah
      ditolak di VET, bukan di sini).
    - Bola: match (gameStartTime ada + berakhir <= 48 jam) dulu,
      lalu match lain, lalu sisanya; masing-masing volume terbesar.
    - Cuaca: volume 24 jam terbesar dulu.
    Market sudah berakhir (end <= sekarang) dibuang.
    """
    scored = []
    for m in parsed_markets:
        hrs = (m["end_ts"] - now_ts) / 3600.0
        if hrs <= 0:
            continue
        try:
            vol = float(m.get("volume24hr") or 0)
        except (TypeError, ValueError):
            vol = 0.0
        if category == "soccer":
            has_game = parse_iso(m.get("game_start_iso")) is not None
            if has_game and hrs <= 48.0:
                rank, prio = 0, "match<=48h"
            elif has_game:
                rank, prio = 1, "match"
            else:
                rank, prio = 2, "non-match"
            scored.append(((rank, -vol), m, prio))
        elif category == "updown":
            scored.append(((0, -vol), m, "volume"))
        else:
            scored.append(((0, -vol), m, "volume"))
    scored.sort(key=lambda t: t[0])
    return [(m, prio) for _, m, prio in scored]


# Bro 3 VET: filter mekanis per kandidat (tanpa sinyal, tanpa sizing).

def bro3_vet(category, m, books, exclude_token_id):
    """VET satu kandidat. books = {index: (bid, ask)}.

    Mengembalikan (side_index_atau_None, info_dict, alasan_tolak).
    Sisi yang dipilih = sisi dengan ASK termurah (aturan value,
    BUKAN prediksi). Syarat beli = ada ASK; BID boleh kosong.
    """
    if category == "updown":
        ok, reason = updown_duration_ok(m["question"], m["start_iso"],
                                        m["end_iso"])
        if not ok:
            return None, {}, reason
    if m["liquidity_usd"] < MIN_LIQUIDITY_USD:
        return None, {}, f"likuiditas ${m['liquidity_usd']:,.0f} < " \
                         f"${MIN_LIQUIDITY_USD:,.0f}"
    if m["token_ids"][0] == exclude_token_id or \
            m["token_ids"][1] == exclude_token_id:
        return None, {}, "rotasi — market sama dengan terakhir yang " \
                         "diperdagangkan, dilewati"
    usable = {i: v for i, v in books.items() if v[1] is not None}
    if not usable:
        return None, {}, "tidak ada ask di kedua sisi (tidak bisa beli)"
    side = min(usable, key=lambda i: usable[i][1])
    bid, ask = usable[side]
    spread_pct = None
    one_sided = False
    if bid is not None:
        mid = (bid + ask) / 2
        spread_pct = (ask - bid) / mid * 100 if mid else 0.0
        if spread_pct > MAX_SPREAD_PCT:
            return None, {}, f"spread {spread_pct:.1f}% > " \
                             f"{MAX_SPREAD_PCT:.0f}%"
    else:
        one_sided = True
    info = {"side": side, "bid": bid, "ask": ask,
            "spread_pct": round(spread_pct, 1)
            if spread_pct is not None else None,
            "one_sided": one_sided}
    return side, info, None


# Bro 4 SOCIAL: gerbang sinyal (RSS / prakiraan). WAJIB lolos sebelum beli.

def bro4_signal_gate(category, question, end_iso, logger):
    """Gerbang sinyal per kategori. Mengembalikan SignalResult.

    Up/Down + bola: berita relevan = KATALIS (bukan arah). Tanpa
    berita relevan yang jelas -> JANGAN BELI. Cuaca: prakiraan
    mendukung YES -> boleh beli YES; selain itu SKIP.
    """
    if category == "weather":
        res = signals.weather_gate(question, end_iso)
        for ev in res.evidence:
            logger.role(4, "SOCIAL", f"bukti cuaca: {ev}")
        logger.role(4, "SOCIAL", f"cuaca: {res.reason}")
        return res
    keywords = signals.keywords_for_market(category, question)
    logger.role(4, "SOCIAL", f"kata kunci dari pertanyaan: {keywords}")
    res = signals.news_gate_for_category(category, keywords)
    for ev in res.evidence:
        logger.role(4, "SOCIAL", f"bukti berita: {ev}")
    logger.role(4, "SOCIAL", f"berita: {res.reason}")
    return res


# Bro 5 SIZE: ukuran posisi dari budget bergulir + fee + min order.

def bro5_size(cat_params, cash_usd, ask, fee_rate, fee_exp,
              market_min_size):
    """Mengembalikan (shares, cost, fee) atau (None, alasan).

    Budget = min(first_trade_usd, kas) — aturan bukit. Lembar harus
    >= max(min_order_size params, orderMinSize market)."""
    budget = buy_budget(cash_usd, cat_params["first_trade_usd"])
    need = max(int(cat_params["min_order_size"]), int(market_min_size))
    shares, cost, fee = (None, None, None)
    res = size_trade(budget, ask, fee_rate, fee_exp, need)
    if res[0] is None:
        return None, None, None, (f"SIZE tolak: {res[1]} "
                                  f"(budget ${budget:.2f} = "
                                  f"min(first_trade "
                                  f"${cat_params['first_trade_usd']:.2f}, "
                                  f"kas ${cash_usd:.2f}))")
    shares, cost, fee = res
    return shares, cost, fee, None


# Bro 1 CHIEF: putusan akhir beli (SCAN -> VET -> SIZE -> SOCIAL).

def bro1_screen_and_pick(category, cat_params, st, logger,
                         fetcher_markets=None, fetcher_book=None,
                         signal_gate=None, momentum_history=None):
    """Satu pass screening + putusan beli untuk satu kategori.

    Mengembalikan (picked_dict_atau_None, alasan_skip).
    picked = {market dict, side, bid, ask, spread_pct, one_sided,
    shares, cost_usd, fee_usd, signal_evidence}.
    Urutan: mekanis dulu (murah), sinyal terakhir (jaringan RSS) —
    supaya RSS tidak dipanggil untuk kandidat yang sudah pasti
    tidak bisa dibeli. Kandidat yang gagal dicatat alasannya
    (maks 3 terakhir di alasan skip) — tidak ada SKIP diam-diam.
    """
    tag_id = CATEGORIES[category]["tag_id"]
    now_ts = datetime.now(timezone.utc).timestamp()
    try:
        raw = (fetcher_markets(tag_id) if fetcher_markets
               else bro8_fetch_markets(tag_id, logger))
    except Exception as e:
        return None, f"CRAWLER gagal baca Gamma ({type(e).__name__}) — " \
                     "tunggu poll berikut"
    parsed, parse_reasons = [], []
    for m in raw:
        pm, reason = parse_market(m)
        if pm is None:
            parse_reasons.append(reason)
        else:
            parsed.append(pm)
    ranked = bro2_rank_candidates(category, parsed, now_ts)
    logger.role(2, "SCAN", f"{category}: {len(ranked)} kandidat lolos "
                           "filter dasar (active, belum closed, belum "
                           "berakhir)")
    if not ranked:
        return None, "tidak ada kandidat lolos filter dasar " \
                     "(active, belum closed, endDate > sekarang)"
    reasons = []
    for m, prio in ranked[:MAX_CANDIDATES]:
        books = {}
        for idx, tok in enumerate(m["token_ids"]):
            books[idx] = (fetcher_book(tok) if fetcher_book
                          else bro8_fetch_book(tok))
        side, info, reject = bro3_vet(category, m, books,
                                      st.get("last_token_id"))
        if reject:
            reasons.append(f"{m['question']}: {reject}")
            logger.role(3, "VET", f"tolak {m['question']}: {reject}")
            continue
        shares, cost, fee, size_reject = bro5_size(
            cat_params, st["cash_usd"], info["ask"], m["fee_rate"],
            m["fee_exponent"], m["min_size"])
        if size_reject:
            reasons.append(f"{m['question']}: {size_reject}")
            logger.role(5, "SIZE", f"tolak {m['question']}: "
                                   f"{size_reject}")
            continue
        # Filter pra-beli ANTI-SL (aturan user 2026-11-02): bila sisi
        # kandidat sedang turun menuju zona SL, JANGAN BELI.
        hist = None
        if momentum_history is not None:
            try:
                hist = momentum_history(m["token_ids"][info["side"]])
            except Exception:
                hist = None
        last_price = None
        if m.get("outcome_prices"):
            last_price = m["outcome_prices"][info["side"]]
        mom_ok, mom_evidence = momentum_gate(
            info["ask"], last_price, history_prices=hist)
        logger.role(4, "SOCIAL", f"momentum {m['question']}: "
                                 f"{mom_evidence}")
        if not mom_ok:
            reasons.append(f"{m['question']}: momentum tolak — "
                           f"{mom_evidence}")
            continue
        gate = (signal_gate(category, m["question"], m["end_iso"])
                if signal_gate else
                bro4_signal_gate(category, m["question"], m["end_iso"],
                                 logger))
        if not gate.ok:
            reasons.append(f"{m['question']}: sinyal tolak — "
                           f"{gate.reason}")
            continue
        if category == "weather" and gate.side != "YES":
            reasons.append(f"{m['question']}: sinyal cuaca tidak "
                           "mendukung YES — SKIP")
            continue
        if category == "weather" and m["outcomes"][info["side"]] != "Yes":
            # Gerbang cuaca hanya mendukung sisi YES; bila sisi
            # termurah bukan Yes, jangan beli sisi lain atas nama
            # sinyal YES.
            reasons.append(f"{m['question']}: sisi termurah "
                           f"({m['outcomes'][info['side']]}) bukan Yes "
                           "padahal sinyal hanya mendukung Yes — SKIP")
            continue
        picked = dict(m)
        picked.update({"market": m["question"],
                       "side": info["side"],
                       "outcome_label": m["outcomes"][info["side"]],
                       "token_id": m["token_ids"][info["side"]],
                       "bid": info["bid"], "ask": info["ask"],
                       "spread_pct": info["spread_pct"],
                       "one_sided": info["one_sided"],
                       "priority": prio, "shares": shares,
                       "cost_usd": cost, "fee_usd": fee,
                       "signal_evidence": gate.evidence})
        logger.role(1, "CHIEF", f"PUTUSAN BELI {category}: {shares} "
                                f"{picked['outcome_label']} @ "
                                f"{info['ask']:.3f} di "
                                f"'{m['question']}' (biaya "
                                f"${cost:.4f} + fee est ${fee:.4f})")
        return picked, None
    return None, ("tidak ada kandidat lolos cek vet/size/sinyal; "
                  "alasan terakhir: " + "; ".join(reasons[-3:]))


# Bro 6 FILLS: eksekusi + verifikasi isi ------------------------------------

def _pending_open_id(client, pend, token_id, logger):
    """Cari order pending di open orders.

    Mengembalikan (order_id_atau_None, open_orders_atau_None).
    Bila pend tidak punya order_id (respons post tanpa id), cari
    dengan pencocokan sisi+harga+ukuran (BUY) atau sisi+ukuran (SELL).
    open_orders None = baca gagal (bukan bukti apa-apa).
    """
    open_orders = order_wiring.list_open_orders_for_token(client,
                                                          token_id)
    if open_orders is None:
        return None, None
    if pend.get("order_id"):
        for o in open_orders:
            if o.get("order_id") == pend["order_id"]:
                return pend["order_id"], open_orders
        return None, open_orders
    for o in open_orders:
        if o.get("side") != pend.get("side"):
            continue
        try:
            o_size = float(o.get("original_size"))
        except (TypeError, ValueError):
            continue
        if abs(o_size - float(pend.get("qty", 0))) > 1e-9:
            continue
        if pend.get("kind") == "BUY":
            try:
                if abs(float(o.get("price")) -
                       float(pend.get("price"))) > 0.002:
                    continue
            except (TypeError, ValueError):
                continue
        return o.get("order_id"), open_orders
    return None, open_orders


def execute_buy(client, category, cat_params, st, picked, logger):
    """Eksekusi beli (limit di ask). Guard: kategori harus IDLE.

    Mengembalikan (posted_bool, catatan). posted=True berarti order
    terpasang dan status menjadi PENDING_BUY (isi diverifikasi poll
    berikut — BUKAN langsung OPEN). posted=False berarti tidak ada
    posisi baru (state tidak berubah kecuali sell_attempts n/a).
    """
    if st["status"] != "IDLE":
        return False, (f"guard: beli ditolak, kategori {category} "
                       f"berstatus {st['status']} (posisi/pending masih "
                       "ada — tidak ada posisi ganda)")
    token_id = picked["token_id"]
    shares, ask = picked["shares"], picked["ask"]
    try:
        signed = order_wiring.build_limit_order(
            client, token_id=token_id, price=ask, size=shares,
            side="BUY")
    except Exception as e:
        logger.role(6, "FILLS", f"beli gagal dibangun ({type(e).__name__}"
                                f": {e}) — tidak ada order, state IDLE")
        return False, f"bangun order beli gagal ({type(e).__name__})"
    try:
        summary = order_wiring.post_signed_order(client, signed)
        order_id = summary.get("order_id")
    except Exception as e:
        # Pelajaran Indodax: error post belum tentu tidak terpasang.
        adopted = order_wiring.adopt_posted_order(
            client, token_id, "BUY", ask, shares)
        if not adopted:
            logger.role(6, "FILLS", f"post beli error "
                                    f"({type(e).__name__}) + tidak ada "
                                    "order di book — dianggap tidak "
                                    "terpasang, state IDLE")
            return False, "post beli error tanpa bukti terpasang"
        order_id, summary = adopted, None
        logger.role(6, "FILLS", f"post beli error "
                                f"({type(e).__name__}) TAPI order "
                                "ditemukan di book — diadopsi sebagai "
                                "pending (order_id dari book)")
    if not order_id:
        adopted = order_wiring.adopt_posted_order(
            client, token_id, "BUY", ask, shares)
        order_id = adopted
    st["status"] = "PENDING_BUY"
    st["pending_order"] = {
        "kind": "BUY", "order_id": order_id, "qty": shares,
        "price": ask, "reason": "BUY", "side": "BUY",
        "method": "limit", "attempts": 0, "response": summary,
        "candidate": {k: picked[k] for k in (
            "market", "question", "token_id", "outcome_label",
            "outcome_index", "fee_rate", "fee_exponent", "fee_type",
            "end_iso", "start_iso")},
    }
    save_state_for(st)
    append_history_for(st, {"type": "BUY_POSTED", "category": category,
                            "market": picked["market"],
                            "side": picked["outcome_label"],
                            "shares": shares, "price_usdc": ask,
                            "order_id": order_id,
                            "response": summary})
    logger.role(6, "FILLS", f"beli terpasang (pending verifikasi): "
                            f"{shares} {picked['outcome_label']} @ "
                            f"{ask:.3f} di '{picked['market']}' "
                            f"(order_id {order_id})")
    return True, "beli terpasang, menunggu verifikasi isi"


def execute_sell(client, category, cat_params, st, qty, bid, ask, reason,
                 logger, force_method=None):
    """Eksekusi jual. TP/TP1/TP2 = limit di bid; SL/SL_HARD/KS = market
    FAK (segera, di bid terbaik — gap tidak ditunggu pulih).
    force_method="market" dipakai saat limit TP yang menggantung
    dialihkan ke market (kunci untung, jangan gantung).

    Mengembalikan (posted_bool, catatan). posted=False berarti posisi
    DIPERTAHANKAN (status tidak berubah) dan percobaan dicatat
    (poll berikut mencoba metode lain).
    """
    pos = st["position"]
    if pos is None or st["status"] not in ("OPEN", "PARTIAL"):
        return False, (f"guard: jual ditolak, kategori {category} "
                       f"tidak punya posisi OPEN/PARTIAL")
    token_id = pos["token_id"]
    method = force_method or (
        "limit" if reason in ("TP", "TP1", "TP2") else "market")
    try:
        if method == "limit":
            signed = order_wiring.build_limit_order(
                client, token_id=token_id, price=bid, size=qty,
                side="SELL")
        else:
            signed = order_wiring.build_market_order(
                client, token_id=token_id, side="SELL", shares=qty)
    except Exception as e:
        pos["sell_attempts"] = pos.get("sell_attempts", 0) + 1
        pos["sell_method"] = method
        save_state_for(st)
        logger.role(6, "FILLS", f"jual gagal dibangun "
                                f"({type(e).__name__}) — posisi "
                                "dipertahankan, coba lagi poll berikut")
        return False, f"bangun order jual gagal ({type(e).__name__})"
    try:
        summary = order_wiring.post_signed_order(client, signed)
        order_id = summary.get("order_id")
    except Exception as e:
        adopted = _adopt_sell_in_book(client, token_id, qty)
        if not adopted:
            pos["sell_attempts"] = pos.get("sell_attempts", 0) + 1
            pos["sell_method"] = method
            save_state_for(st)
            logger.role(6, "FILLS", f"post jual error "
                                    f"({type(e).__name__}) + tidak ada "
                                    "order jual di book — posisi "
                                    "dipertahankan, coba lagi poll "
                                    "berikut dengan metode lain")
            return False, "post jual error tanpa bukti terpasang"
        order_id, summary = adopted, None
        logger.role(6, "FILLS", f"post jual error "
                                f"({type(e).__name__}) TAPI order jual "
                                "ditemukan di book — diadopsi sebagai "
                                "pending")
    if not order_id:
        order_id = _adopt_sell_in_book(client, token_id, qty)
    st["status"] = "PENDING_SELL"
    st["pending_order"] = {
        "kind": "SELL", "order_id": order_id, "qty": qty,
        "price": bid, "reason": reason, "side": "SELL",
        "method": method, "attempts": 0, "response": summary,
    }
    save_state_for(st)
    append_history_for(st, {"type": "SELL_POSTED", "category": category,
                            "market": pos["market"], "reason": reason,
                            "qty": qty, "price_bid_usdc": bid,
                            "method": method, "order_id": order_id,
                            "response": summary})
    logger.role(6, "FILLS", f"jual terpasang (pending verifikasi): "
                            f"{qty} lembar ({reason}) via {method} @ "
                            f"bid {bid:.3f} (order_id {order_id})")
    return True, "jual terpasang, menunggu verifikasi isi"


def _adopt_sell_in_book(client, token_id, qty):
    """Cari order SELL di book dengan ukuran sama (untuk post error
    market/limit). Mengembalikan order_id atau None."""
    orders = order_wiring.list_open_orders_for_token(client, token_id)
    if not orders:
        return None
    for o in orders:
        if o.get("side") != "SELL":
            continue
        try:
            if abs(float(o.get("original_size")) - float(qty)) <= 1e-9:
                return o.get("order_id")
        except (TypeError, ValueError):
            continue
    return None


def _apply_buy_fill(st, qty, ask, candidate, logger):
    """Terapkan beli terverifikasi: posisi OPEN, kas dikurangi biaya
    + fee estimasi. Mengembalikan catatan."""
    cost = qty * ask
    fee = estimate_fee(ask, qty, candidate["fee_rate"],
                       candidate["fee_exponent"])
    st["position"] = {
        "market": candidate["market"],
        "question": candidate.get("question", candidate["market"]),
        "token_id": candidate["token_id"],
        "outcome_label": candidate["outcome_label"],
        "outcome_index": candidate["outcome_index"],
        "entry_ask": ask,
        "shares_total": qty,
        "remaining": qty,
        "cost_usd": round(cost, 4),
        "fee_usd": round(fee, 4),
        "cost_per_share": ask,
        # fee per lembar disimpan presisi penuh (bukan dibulatkan):
        # pembulatan 4 desimal di sini kehilangan ~$0,0001 per posisi
        # saat dikalikan kembali — total dibulatkan hanya untuk tampil.
        "fee_buy_per_share": fee / qty if qty else 0.0,
        "fee_rate": candidate["fee_rate"],
        "fee_exponent": candidate["fee_exponent"],
        "tp1_done": False,
        "last_bid": None,
        "last_ask": ask,
        "prev_ask": None,
        "lowest_ask": ask,
        "end_iso": candidate.get("end_iso"),
        "start_iso": candidate.get("start_iso"),
        "sell_attempts": 0,
        "sell_method": None,
    }
    st["cash_usd"] = round(st["cash_usd"] - cost - fee, 4)
    st["status"] = "OPEN"
    st["pending_order"] = None
    return (f"beli terverifikasi: {qty} {candidate['outcome_label']} @ "
            f"{ask:.3f} (biaya ${cost:.4f} + fee est ${fee:.4f}, kas "
            f"tersisa ${st['cash_usd']:.4f})")


def verify_pending(client, category, cat_params, st, logger):
    """Verifikasi satu pending order. Mengembalikan aksi string untuk
    log. Mengubah state + menyimpan (pemanggil TIDAK perlu save lagi,
    tapi boleh save ulang — idempotent).

    Aturan: respons post TIDAK PERNAH cukup sendirian (pelajaran
    Indodax). Bukti = open orders + (bila bisa dibaca) posisi.
    """
    pend = st["pending_order"]
    if not pend:
        return "NO_PENDING"
    token_id = (pend.get("candidate", {}) or {}).get("token_id") or \
        (st["position"] or {}).get("token_id")
    if not token_id:
        logger.role(6, "FILLS", "pending tanpa token_id — dibatalkan "
                                "aman (state tidak berubah selain "
                                "pending dihapus)")
        st["pending_order"] = None
        st["status"] = "IDLE" if st["position"] is None else st["status"]
        save_state_for(st)
        return "PENDING_DROPPED"
    found_id, open_orders = _pending_open_id(client, pend, token_id,
                                             logger)
    if open_orders is None:
        logger.role(6, "FILLS", "baca open orders gagal — pending "
                                "dipertahankan, verifikasi ulang poll "
                                "berikut (tidak disimpulkan apa-apa)")
        return "PENDING"
    if found_id:
        pend["order_id"] = found_id
        pend["attempts"] = pend.get("attempts", 0) + 1
        if pend["kind"] == "BUY":
            if pend["attempts"] >= MAX_PENDING_POLLS:
                ok, note = order_wiring.cancel_open_order(client,
                                                          found_id)
                st["pending_order"] = None
                st["status"] = "IDLE"
                save_state_for(st)
                append_history_for(st, {"type": "BUY_CANCELLED",
                                        "category": category,
                                        "order_id": found_id,
                                        "reason": "resting melebihi "
                                                  "batas poll"})
                logger.role(6, "FILLS", f"beli resting {pend['attempts']} "
                                        "poll — dibatalkan "
                                        f"(cancel: {note}), kembali IDLE")
                return "BUY_CANCELLED"
            save_state_for(st)
            logger.role(6, "FILLS", f"beli masih resting di book "
                                    f"(poll ke-{pend['attempts']}) — "
                                    "menunggu terisi")
            return "PENDING"
        # SELL resting (limit TP): setelah N poll, batalkan + jual
        # market SEGERA (kunci untung, jangan gantung). Bila cancel
        # gagal, JANGAN pasang market di atasnya (risiko jual ganda)
        # — tunda ke poll berikut.
        if pend["attempts"] >= MAX_SELL_RESTING_POLLS:
            ok, note = order_wiring.cancel_open_order(client, found_id)
            logger.role(6, "FILLS", f"jual limit resting "
                                    f"{pend['attempts']} poll — "
                                    f"cancel: {note}")
            pos = st["position"]
            if pos is None:
                st["pending_order"] = None
                st["status"] = "IDLE"
                save_state_for(st)
                return "SELL_ORPHAN"
            st["pending_order"] = None
            st["status"] = "PARTIAL" if pos["remaining"] < \
                pos["shares_total"] else "OPEN"
            save_state_for(st)
            if not ok:
                logger.role(6, "FILLS", "cancel gagal — market tidak "
                                        "dipasang di atas order lama "
                                        "(cegah jual ganda), coba lagi "
                                        "poll berikut")
                return "SELL_SWITCH_DEFERRED"
            fresh_bid, fresh_ask = bro8_fetch_book(pos["token_id"])
            if fresh_bid is None:
                logger.role(6, "FILLS", "book tanpa bid setelah cancel "
                                        "— market ditunda ke poll "
                                        "berikut (CANNOT_EXIT)")
                return "SELL_SWITCH_DEFERRED"
            posted, note = execute_sell(
                client, category, cat_params, st, pend["qty"],
                fresh_bid, fresh_ask, pend["reason"], logger,
                force_method="market")
            return "SELL_POSTED" if posted else "SELL_FAILED"
        save_state_for(st)
        logger.role(6, "FILLS", f"jual masih resting di book "
                                f"(poll ke-{pend['attempts']}) — "
                                "menunggu terisi")
        return "PENDING"
    # Order sudah tidak terbuka: terisi / batal / kill.
    size, read_ok = order_wiring.position_size_for_token(client,
                                                         token_id)
    resp = pend.get("response") or {}
    resp_matched = bool(resp.get("ok")) and (
        resp.get("status") == "matched" or resp.get("trade_count", 0) > 0)
    if pend["kind"] == "BUY":
        candidate = pend["candidate"]
        qty, ask = pend["qty"], pend["price"]
        if read_ok:
            held = float(size) if size is not None else 0.0
            if held >= qty - 1e-9:
                note = _apply_buy_fill(st, qty, ask, candidate, logger)
                save_state_for(st)
                append_history_for(st, {"type": "BUY_FILLED",
                                        "category": category,
                                        "market": candidate["market"],
                                        "shares": qty,
                                        "price_usdc": ask,
                                        "order_id": pend["order_id"]})
                logger.role(6, "FILLS", note)
                return "BUY_FILLED"
            if held <= 1e-9:
                st["pending_order"] = None
                st["status"] = "IDLE"
                save_state_for(st)
                append_history_for(st, {"type": "BUY_NOT_FILLED",
                                        "category": category,
                                        "order_id": pend["order_id"]})
                logger.role(6, "FILLS", "beli tidak terisi (order hilang "
                                        "tanpa posisi) — kembali IDLE, "
                                        "tidak ada posisi hantu")
                return "BUY_NOT_FILLED"
            held_int = int(held)
            note = _apply_buy_fill(st, held_int, ask, candidate, logger)
            save_state_for(st)
            append_history_for(st, {"type": "BUY_FILLED_PARTIAL",
                                    "category": category,
                                    "market": candidate["market"],
                                    "shares": held_int,
                                    "price_usdc": ask,
                                    "order_id": pend["order_id"]})
            logger.role(6, "FILLS", f"beli terisi sebagian: {note}")
            return "BUY_FILLED_PARTIAL"
        if resp_matched:
            note = _apply_buy_fill(st, qty, ask, candidate, logger)
            save_state_for(st)
            append_history_for(st, {"type": "BUY_FILLED",
                                    "category": category,
                                    "market": candidate["market"],
                                    "shares": qty, "price_usdc": ask,
                                    "order_id": pend["order_id"],
                                    "note": "posisi tidak terbaca — "
                                            "bukti respons matched"})
            logger.role(6, "FILLS", note + " (posisi tidak terbaca, "
                                          "bukti respons matched)")
            return "BUY_FILLED"
        pend["attempts"] = pend.get("attempts", 0) + 1
        if pend["attempts"] >= MAX_PENDING_POLLS:
            st["stopped"] = True
            st["stop_reason"] = ("beli tidak bisa diverifikasi setelah "
                                 f"{MAX_PENDING_POLLS} poll — periksa "
                                 "manual di Polymarket sebelum lanjut")
            st["status"] = "STOPPED"
            save_state_for(st)
            logger.role(6, "FILLS", "STOP kategori: beli tidak bisa "
                                    "diverifikasi (posisi tidak terbaca "
                                    "+ respons tanpa bukti trade) — "
                                    "periksa manual, jangan Start ulang "
                                    "kategori ini sebelum jelas")
            return "BUY_STUCK"
        save_state_for(st)
        logger.role(6, "FILLS", f"beli belum terverifikasi "
                                f"(poll ke-{pend['attempts']}) — "
                                "menunggu bukti")
        return "PENDING"
    # SELL: order hilang.
    pos = st["position"]
    if pos is None:
        st["pending_order"] = None
        st["status"] = "IDLE"
        save_state_for(st)
        logger.role(6, "FILLS", "pending jual tanpa posisi — dibersihkan")
        return "SELL_ORPHAN"
    before = pos["remaining"]
    qty = pend["qty"]
    bid = pend["price"]
    fee_sell = estimate_fee(bid, qty, pos["fee_rate"],
                            pos["fee_exponent"])
    if read_ok:
        held = float(size) if size is not None else 0.0
        sold = before - int(round(held))
        if sold <= 0:
            # Order hilang tapi posisi tidak berkurang: kill/batal
            # tanpa isi — posisi dipertahankan, coba lagi.
            pos["sell_attempts"] = pos.get("sell_attempts", 0) + 1
            st["pending_order"] = None
            st["status"] = "PARTIAL" if before < pos["shares_total"] \
                else "OPEN"
            save_state_for(st)
            logger.role(6, "FILLS", "jual tidak terisi (order hilang "
                                    "tapi posisi utuh) — posisi "
                                    "dipertahankan, coba lagi poll "
                                    "berikut")
            return "SELL_NOT_FILLED"
        return _apply_sell_fill(st, pos, sold, bid, fee_sell,
                                pend["reason"], category, logger)
    if resp_matched:
        return _apply_sell_fill(st, pos, qty, bid, fee_sell,
                                pend["reason"], category, logger,
                                assumed=True)
    pend["attempts"] = pend.get("attempts", 0) + 1
    if pend["attempts"] >= MAX_PENDING_POLLS:
        st["stopped"] = True
        st["stop_reason"] = ("jual tidak bisa diverifikasi setelah "
                             f"{MAX_PENDING_POLLS} poll — periksa "
                             "manual di Polymarket sebelum lanjut")
        st["status"] = "STOPPED"
        save_state_for(st)
        logger.role(6, "FILLS", "STOP kategori: jual tidak bisa "
                                "diverifikasi (posisi tidak terbaca + "
                                "respons tanpa bukti trade) — periksa "
                                "manual")
        return "SELL_STUCK"
    save_state_for(st)
    logger.role(6, "FILLS", f"jual belum terverifikasi "
                            f"(poll ke-{pend['attempts']}) — menunggu "
                            "bukti")
    return "PENDING"


def _apply_sell_fill(st, pos, sold, bid, fee_sell, reason, category,
                     logger, assumed=False):
    """Terapkan jual terverifikasi ke state + riwayat. Mengembalikan
    aksi string. P&L BERSIH setelah fee: hasil = qty*bid - fee_jual;
    P&L = hasil - qty*(cost_per_share + fee_buy_per_share)."""
    proceeds = sold * bid - fee_sell
    pnl = proceeds - sold * (pos["cost_per_share"] +
                             pos["fee_buy_per_share"])
    pos["remaining"] -= sold
    st["cash_usd"] = round(st["cash_usd"] + proceeds, 4)
    st["realized_usd"] = round(st["realized_usd"] + pnl, 4)
    if reason == "TP1":
        pos["tp1_done"] = True
    st["pending_order"] = None
    if pos["remaining"] <= 0:
        st["last_token_id"] = pos["token_id"]
        st["last_close_poll"] = CURRENT_POLL[0]
        st["position"] = None
        st["status"] = "IDLE"
        closed_note = "CLOSED"
    else:
        st["status"] = "PARTIAL"
        closed_note = f"PARTIAL (sisa {pos['remaining']})"
    save_state_for(st)
    append_history_for(st, {"type": "EXIT", "category": category,
                            "market": pos["market"], "reason": reason,
                            "qty": sold, "price_bid_usdc": bid,
                            "fee_usdc": round(fee_sell, 4),
                            "proceeds_usdc": round(proceeds, 4),
                            "pnl_usd": round(pnl, 4),
                            "remaining": pos["remaining"] if
                            st["position"] else 0,
                            "assumed_full_fill": assumed})
    logger.role(6, "FILLS", f"jual terverifikasi ({reason}): {sold} "
                            f"lembar @ bid {bid:.3f} (fee est "
                            f"${fee_sell:.4f}) = ${proceeds:.4f} | P&L "
                            f"bersih ${pnl:.4f} | kas "
                            f"${st['cash_usd']:.4f} | {closed_note}"
                            + (" (asumsi isi penuh — posisi tidak "
                               "terbaca)" if assumed else ""))
    if reason == "KILL_SWITCH":
        return "KS_FILLED"
    return "SELL_FILLED"


# Penanda state aktif untuk save_state_for / append_history_for.
CURRENT_STATE_DIR = [None]
CURRENT_POLL = [0]


def save_state_for(st):
    save_state(CURRENT_STATE_DIR[0], st)


def append_history_for(st, record):
    append_history(CURRENT_STATE_DIR[0], record)


# Bro 7 RISK: cek posisi tiap poll (resolusi dulu, lalu book, lalu trigger).

def fetch_history_prices(client, token_id):
    """Histori harga 1 jam terakhir via SDK (best-effort).

    Mengembalikan list[float] (tertua dulu) atau None bila gagal.
    Dipakai untuk bukti momentum pemulihan di zona SL."""
    try:
        end = int(time.time())
        start = end - 3600
        points = []
        for page in client.list_price_history(asset_id=token_id,
                                              start=start, end=end):
            for pt in page.items:
                price = getattr(pt, "price", None)
                if price is not None:
                    points.append(float(price))
        return points or None
    except Exception:
        return None


def bro7_check_position(client, category, cat_params, st, logger,
                        poll_index):
    """Satu cek posisi (RISK). Mengembalikan aksi string:
    NO_POSITION | RESOLVED | HOLD | SL_HOLD | CANNOT_EXIT |
    SELL_POSTED | SELL_FAILED | KILL_SWITCH | NO_BOOK.
    Mengubah + menyimpan state.
    """
    pos = st["position"]
    if pos is None or st["status"] not in ("OPEN", "PARTIAL"):
        return "NO_POSITION"
    token_id = pos["token_id"]
    # 1. Resolusi dulu (sebelum book): settle hanya bila resmi.
    market = bro8_fetch_market_by_token(token_id)
    prices_raw = market.get("outcomePrices")
    if isinstance(prices_raw, str):
        try:
            prices_raw = json.loads(prices_raw)
        except ValueError:
            prices_raw = None
    outcome, evidence = decide_resolution(
        prices_raw, pos["outcome_index"], market.get("closed"))
    if outcome:
        qty = pos["remaining"]
        proceeds = qty * 1.0 if outcome == "WIN" else 0.0
        pnl = proceeds - qty * (pos["cost_per_share"] +
                                pos["fee_buy_per_share"])
        st["cash_usd"] = round(st["cash_usd"] + proceeds, 4)
        st["realized_usd"] = round(st["realized_usd"] + pnl, 4)
        st["last_token_id"] = token_id
        st["last_close_poll"] = poll_index
        st["position"] = None
        st["status"] = "IDLE"
        save_state_for(st)
        append_history_for(st, {"type": "RESOLVE", "category": category,
                                "market": pos["market"],
                                "outcome": outcome, "qty": qty,
                                "proceeds_usdc": round(proceeds, 4),
                                "pnl_usd": round(pnl, 4),
                                "evidence": evidence})
        logger.role(7, "RISK", f"RESOLVED {outcome}: settle {qty} "
                               f"lembar = ${proceeds:.4f} | P&L bersih "
                               f"${pnl:.4f} | CLOSED")
        return "RESOLVED"
    # 2. Book segar (bukan harga basi).
    bid, ask = bro8_fetch_book(token_id)
    if bid is None:
        logger.role(7, "RISK", "CANNOT_EXIT: book tanpa bid — posisi "
                               "dipertahankan, menunggu bid (tidak "
                               "memaksakan jual di harga nol)")
        return "CANNOT_EXIT"
    # 3. Lacak titik terendah + ask sebelumnya (untuk bukti pulih).
    prev_ask = pos.get("last_ask")
    if ask is not None:
        if pos.get("lowest_ask") is None:
            pos["lowest_ask"] = ask
        else:
            pos["lowest_ask"] = min(pos["lowest_ask"], ask)
    pos["prev_ask"] = prev_ask
    pos["last_bid"] = bid
    pos["last_ask"] = ask
    total = st["cash_usd"] + pos["remaining"] * bid
    start_value = cat_params["modal_usd"]
    kind = CATEGORIES[category]["exit"]
    # 4. Bukti pemulihan HANYA bila trigger masuk zona SL (hemat RSS).
    recovery = None
    sl_level = pos["entry_ask"] * (1 - cat_params["sl_pct"] / 100)
    hard_level = pos["entry_ask"] * (
        1 - cat_params["sl_hard_cap_pct"] / 100)
    trigger = ask if ask is not None else bid
    if hard_level < trigger <= sl_level + EPS:
        gate = bro4_signal_gate(category, pos["market"],
                                pos.get("end_iso"), logger)
        hist = fetch_history_prices(client, token_id)
        recovery = recovery_evidence(ask, prev_ask, pos["lowest_ask"],
                                     gate.ok, hist)
        logger.role(7, "RISK", f"zona SL: bukti pemulihan — "
                               f"{recovery['evidence']}")
    action, qty, reason = decide_exit(
        pos["entry_ask"], bid, ask, pos["remaining"], pos["tp1_done"],
        total, start_value, kind=kind, sl_pct=cat_params["sl_pct"],
        sl_hard_cap_pct=cat_params["sl_hard_cap_pct"],
        tp_pct=cat_params.get("tp_pct"),
        tp1_pct=cat_params.get("tp1_pct"),
        tp2_pct=cat_params.get("tp2_pct"),
        ks_pct=cat_params["kill_switch_pct"], recovery=recovery)
    save_state_for(st)  # simpan pelacakan (lowest/prev) walau HOLD
    if action == "HOLD":
        logger.role(7, "RISK", f"{reason}: bid {bid:.3f} ask "
                               f"{ask if ask is not None else float('nan'):.3f} "
                               f"vs entry {pos['entry_ask']:.3f} | total "
                               f"${total:.4f} (kas ${st['cash_usd']:.4f} "
                               f"+ {pos['remaining']} lembar)")
        return reason
    if reason == "KILL_SWITCH":
        st["kill_switch_hit"] = True
        save_state_for(st)
    posted, note = execute_sell(client, category, cat_params, st, qty,
                                bid, ask, reason, logger)
    if posted:
        if reason == "KILL_SWITCH":
            return "KILL_SWITCH"
        return "SELL_POSTED"
    return "SELL_FAILED"


# --- Loop utama + mode -------------------------------------------------------

def run_loop(params, client, script_dir, state_dir, logger):
    """Loop live selamanya. Mengembalikan exit code:
    0 = berhenti bersih (Ctrl+C / panel Stop),
    4 = berhenti karena kill-switch (semua jual sudah diupayakan)."""
    CURRENT_STATE_DIR[0] = state_dir
    states = {}
    for cat in CATEGORIES:
        modal = params["categories"][cat]["modal_usd"]
        st = load_state(state_dir, cat, modal)
        states[cat] = st
        if st.get("corrupt"):
            logger.log(f"{cat}: state RUSAK — kategori tidak "
                       f"ditradingkan sampai diperbaiki manual "
                       f"({st.get('stop_reason')})")
        elif st.get("stopped"):
            logger.log(f"{cat}: STOPPED ({st.get('stop_reason')}) — "
                       "kategori tidak ditradingkan")
    holding_s = params.get("poll_holding_s", POLL_HOLDING_DEFAULT)
    idle_s = params.get("poll_idle_s", POLL_IDLE_DEFAULT)
    logger.log("MODE: LOOP LIVE (uang asli, SPOT saja, tanpa withdraw).")
    logger.log(f"Aturan: 1 posisi/kategori | SL -7% (tahan s.d. -12% "
               f"bila pulih jelas) | batas keras -12% | TP Up/Down "
               f"+20% jual habis, cuaca/bola TP1 +10%/TP2 +15% | "
               f"kill-switch total 15% | poll {holding_s} dtk pegang / "
               f"{idle_s} dtk idle.")
    logger.log(f"Wallet signer (publik): {SIGNER_WALLET_ADDRESS} | "
               f"profil/deposit (publik): {PROFILE_WALLET_ADDRESS}.")
    poll_index = 0
    ks_mode = False
    ks_polls = 0
    while True:
        poll_index += 1
        CURRENT_POLL[0] = poll_index
        try:
            if ks_mode:
                ks_polls += 1
                all_clear = True
                for cat, st in states.items():
                    if st["status"] in ("PENDING_BUY", "PENDING_SELL"):
                        try:
                            verify_pending(client, cat,
                                           params["categories"][cat],
                                           st, logger)
                        except Exception as e:
                            logger.log(f"KS-verifikasi {cat} error "
                                       f"({type(e).__name__}) — tunggu "
                                       "poll berikut")
                            all_clear = False
                        if st["status"] in ("PENDING_BUY",
                                            "PENDING_SELL"):
                            all_clear = False
                if all_clear:
                    for st in states.values():
                        save_state_for(st)
                    logger.log("KILL-SWITCH: semua jual terverifikasi — "
                               "loop BERHENTI (exit 4). Tinjau sebelum "
                               "Start ulang.")
                    return 4
                if ks_polls >= KS_VERIFY_POLLS:
                    logger.log("KILL-SWITCH: jual belum terverifikasi "
                               f"setelah {KS_VERIFY_POLLS} poll — loop "
                               "BERHENTI (exit 4). PEMILIK HARUS "
                               "memeriksa posisi manual: mungkin masih "
                               "terbuka.")
                    return 4
                time.sleep(KS_VERIFY_SLEEP)
                continue
            # Fase A — monitor / verifikasi / jual (RISK + FILLS).
            ks_triggered = False
            for cat in ("updown", "weather", "soccer"):
                st = states[cat]
                if st.get("corrupt") or st.get("stopped"):
                    continue
                try:
                    if st["status"] in ("PENDING_BUY", "PENDING_SELL"):
                        verify_pending(client, cat,
                                       params["categories"][cat],
                                       st, logger)
                    elif st["status"] in ("OPEN", "PARTIAL"):
                        res = bro7_check_position(
                            client, cat, params["categories"][cat],
                            st, logger, poll_index)
                        if res == "KILL_SWITCH":
                            ks_triggered = True
                except Exception as e:
                    logger.log(f"error kategori {cat} fase monitor "
                               f"({type(e).__name__}: {e}) — tunggu poll "
                               "berikut, bukan crash")
            if ks_triggered:
                for cat, st in states.items():
                    if st["status"] in ("OPEN", "PARTIAL") and \
                            st["position"]:
                        pos = st["position"]
                        bid, ask = bro8_fetch_book(pos["token_id"])
                        if bid is not None:
                            try:
                                execute_sell(
                                    client, cat,
                                    params["categories"][cat], st,
                                    pos["remaining"], bid, ask,
                                    "KILL_SWITCH", logger)
                            except Exception as e:
                                logger.log(f"KS-jual {cat} error "
                                           f"({type(e).__name__}) — "
                                           "dicoba lagi di mode KS")
                for st in states.values():
                    save_state_for(st)
                logger.log("KILL-SWITCH: pemicu di satu kategori — "
                           "semua posisi dijual (best-effort) + loop "
                           "masuk mode verifikasi KS (tanpa beli baru).")
                ks_mode = True
                ks_polls = 0
                continue
            # Fase B — saring + beli (CHIEF). Kategori yang baru
            # CLOSED di Fase A poll ini LANGSUNG disaring (rotasi
            # segera scalping) — state CLOSED sudah tersimpan atomik
            # sebelum fase ini, jadi tutup dan buka tidak tercampur.
            for cat in ("updown", "weather", "soccer"):
                st = states[cat]
                if st.get("corrupt") or st.get("stopped"):
                    continue
                if st["status"] != "IDLE":
                    continue
                try:
                    picked, reason = bro1_screen_and_pick(
                        cat, params["categories"][cat], st, logger,
                        momentum_history=lambda tok: fetch_history_prices(
                            client, tok))
                    if picked:
                        execute_buy(client, cat,
                                    params["categories"][cat], st,
                                    picked, logger)
                    else:
                        logger.log(f"{cat}: SKIP beli — {reason}")
                except Exception as e:
                    logger.log(f"error kategori {cat} fase saring "
                               f"({type(e).__name__}: {e}) — tunggu poll "
                               "berikut, bukan crash")
            summary = "; ".join(
                f"{cat}:{states[cat]['status']}/kas "
                f"${states[cat]['cash_usd']:.2f}"
                for cat in CATEGORIES)
            logger.log(f"poll #{poll_index} selesai: {summary}")
            any_busy = any(st["status"] in (
                "OPEN", "PARTIAL", "PENDING_BUY", "PENDING_SELL")
                for st in states.values())
            time.sleep(holding_s if any_busy else idle_s)
        except KeyboardInterrupt:
            for st in states.values():
                try:
                    save_state_for(st)
                except Exception:
                    pass
            logger.log("loop dihentikan pemilik (Ctrl+C / panel Stop) "
                       "— state tersimpan.")
            return 0


def mode_check(script_dir, state_dir, logger, params_path=None,
               approval_path=None):
    """CHECK: gerbang + params + state, TANPA order, TANPA post.

    Keluar 0 = siap (kunci boleh belum dimasukkan — verifikasi signer
    menunggu kunci), 2 = konfigurasi belum lengkap, 1 = verifikasi
    signer/state gagal."""
    params_path = params_path or os.path.join(script_dir,
                                              "loop_params.json")
    approval_path = approval_path or os.path.join(
        script_dir, "LIVE_APPROVED_LOOP.txt")
    if not os.path.isfile(params_path):
        logger.log("CHECK: loop_params.json tidak ditemukan.")
        return 2
    try:
        params, errors, warnings = load_loop_params(params_path)
    except Exception as e:
        logger.log(f"CHECK: loop_params.json tidak bisa dibaca "
                   f"({type(e).__name__}).")
        return 2
    if errors:
        for e in errors:
            logger.log(f"CHECK params DITOLAK: {e}")
        return 2
    for w in warnings:
        logger.log(f"CHECK params peringatan: {w}")
    if not os.path.isfile(approval_path):
        logger.log("CHECK: LIVE_APPROVED_LOOP.txt tidak ditemukan "
                   "(file persetujuan loop, berbeda dari v4).")
        return 2
    with open(approval_path) as f:
        approval = f.read()
    logger.log(f"CHECK persetujuan loop: {approval.strip()[:300]}")
    if not approval_text_ok(approval):
        logger.log("CHECK: persetujuan loop harus menyebut SL 7% + "
                   "batas keras 12% + kill-switch 15%.")
        return 2
    try:
        geo = parse_geoblock(http_get_json(GEOBLOCK_URL, timeout=15))
    except Exception as e:
        geo = f"gagal dicek ({type(e).__name__})"
    logger.log(f"CHECK geoblock dari mesin ini: {geo}.")
    if geo == "blocked":
        logger.log("CHECK PERINGATAN: mesin ini diblokir untuk order — "
                   "mode live akan ditolak di sini.")
    logger.log(f"CHECK SDK resmi (modul polymarket): "
               f"{'terpasang' if order_wiring.sdk_available() else 'TIDAK TERPASANG'}")
    private_key = os.environ.get(order_wiring.ENV_PRIVATE_KEY)
    logger.log(f"CHECK POLY_PRIVATE_KEY: "
               f"{'ada' if private_key else 'TIDAK ADA'} "
               "(nilai tidak dicetak).")
    if private_key:
        client = order_wiring.build_sdk_client(private_key)
        if client is None:
            logger.log("CHECK GAGAL: klien SDK tidak bisa dibangun "
                       "(alamat turunan bukan signer / SDK error).")
            return 1
        logger.log("CHECK: klien SDK berhasil dibangun (derive "
                   "in-memory, nilai tidak dicetak).")
        try:
            client.close()
        except Exception:
            pass
    else:
        logger.log("CHECK: verifikasi signer menunggu kunci dimasukkan "
                   "pemilik ke environment.")
    for cat in CATEGORIES:
        modal = params["categories"][cat]["modal_usd"]
        st = load_state(state_dir, cat, modal)
        flag = ""
        if st.get("corrupt"):
            flag = " (RUSAK — tidak ditradingkan)"
        elif st.get("stopped"):
            flag = f" (STOPPED: {st.get('stop_reason')})"
        elif st.get("kill_switch_hit"):
            flag = " (PERNAH KENA KILL-SWITCH — live ditolak)"
        logger.log(f"CHECK state {cat}: {st['status']}, kas "
                   f"${st['cash_usd']:.4f}{flag}")
    logger.log("CHECK SELESAI. Nol order dibuat.")
    return 0


def mode_dry_run(script_dir, state_dir, logger, args):
    """DRY-RUN: bangun + tanda tangani, JANGAN POST.

    Tidak butuh LIVE_TRADING / file persetujuan (verifikasi
    pra-persetujuan). Butuh kunci + SDK + signer (untuk tanda tangan
    nyata). Keluar 0 = dry-run selesai (termasuk bila tidak ada
    kandidat), 2 = kunci/SDK/geoblock belum siap, 1 = signer gagal."""
    private_key = os.environ.get(order_wiring.ENV_PRIVATE_KEY)
    if not private_key:
        logger.log("DRY-RUN gagal: POLY_PRIVATE_KEY belum diset.")
        return 2
    if not order_wiring.sdk_available():
        logger.log("DRY-RUN gagal: SDK resmi belum terpasang.")
        return 2
    client = order_wiring.build_sdk_client(private_key)
    if client is None:
        logger.log("DRY-RUN gagal: klien SDK tidak bisa dibangun.")
        return 1
    try:
        try:
            geo = parse_geoblock(http_get_json(GEOBLOCK_URL,
                                               timeout=15))
        except Exception:
            geo = "gagal dicek"
        logger.log(f"DRY-RUN geoblock dari mesin ini: {geo} "
                   "(info saja — dry-run tidak mem-post).")
        if args.dry_token and args.dry_price is not None \
                and args.dry_size is not None:
            side = (args.dry_side or "BUY").upper()
            summary = order_wiring.dry_run_limit_order(
                client, token_id=args.dry_token, price=args.dry_price,
                size=args.dry_size, side=side)
            logger.log(f"DRY-RUN order eksplisit: {summary}")
            logger.log("DRY-RUN SELESAI. Nol order dibuat (tidak POST).")
            return 0
        # Satu pass screening mekanis + sizing + momentum proksi
        # (tanpa gerbang sinyal — dry-run tidak membeli, jadi tidak
        # perlu RSS; sinyal tetap diuji di mode live).
        logger.log("DRY-RUN: screening mekanis (sinyal dilewati — "
                   "dry-run tidak membeli).")
        for cat in CATEGORIES:
            st = {"cash_usd": 1.0, "last_token_id": None}
            cat_params = dict(DEFAULTS[cat])
            cat_params.update({"modal_usd": 1.0,
                               "first_trade_usd": 1.0,
                               "min_order_size": 5, "chain": "polygon",
                               "collateral": "USDC"})
            try:
                picked, reason = bro1_screen_and_pick(
                    cat, cat_params, st, logger,
                    signal_gate=lambda c, q, e: signals.SignalResult(
                        ok=True, side=None, evidence=[
                            "dry-run: gerbang sinyal dilewati"],
                        reason="dry-run"))
            except Exception as e:
                logger.log(f"DRY-RUN {cat}: screening error "
                           f"({type(e).__name__}) — lanjut kategori "
                           "berikut")
                continue
            if not picked:
                logger.log(f"DRY-RUN {cat}: tidak ada kandidat — "
                           f"{reason}")
                continue
            summary = order_wiring.dry_run_limit_order(
                client, token_id=picked["token_id"],
                price=picked["ask"], size=picked["shares"], side="BUY")
            logger.log(f"DRY-RUN {cat}: kandidat "
                       f"'{picked['market']}' -> {summary}")
            logger.log("DRY-RUN SELESAI. Nol order dibuat (tidak POST).")
            return 0
        logger.log("DRY-RUN SELESAI: tidak ada kandidat di semua "
                   "kategori. Nol order dibuat (tidak POST).")
        return 0
    finally:
        try:
            client.close()
        except Exception:
            pass


def main(argv=None):
    ap = argparse.ArgumentParser(
        description="Polymarket LIVE loop — 3 kategori, satu proses.")
    ap.add_argument("--live", action="store_true",
                    help="Loop live (wajib lolos semua gerbang).")
    ap.add_argument("--dry-run", action="store_true",
                    help="Bangun + tanda tangani saja, JANGAN POST.")
    ap.add_argument("--check", action="store_true",
                    help="Cek gerbang + params + state, tanpa order.")
    ap.add_argument("--dry-token", default=None,
                    help="DRY-RUN eksplisit: token_id CLOB.")
    ap.add_argument("--dry-price", default=None, type=float,
                    help="DRY-RUN eksplisit: harga limit.")
    ap.add_argument("--dry-size", default=None, type=float,
                    help="DRY-RUN eksplisit: jumlah lembar.")
    ap.add_argument("--dry-side", default="BUY",
                    help="DRY-RUN eksplisit: BUY/SELL.")
    ap.add_argument("--state-dir", default=None,
                    help="Folder state (default: <skrip>/state).")
    ap.add_argument("--params", default=None,
                    help="Path loop_params.json (default: "
                         "<skrip>/loop_params.json).")
    ap.add_argument("--approval", default=None,
                    help="Path LIVE_APPROVED_LOOP.txt (default: "
                         "<skrip>/LIVE_APPROVED_LOOP.txt).")
    args = ap.parse_args(argv)
    state_dir = args.state_dir or os.path.join(SCRIPT_DIR, "state")
    os.makedirs(state_dir, exist_ok=True)
    logger = Logger(os.path.join(state_dir, "loop.log"))
    CURRENT_STATE_DIR[0] = state_dir
    if args.live:
        gated = check_gates(SCRIPT_DIR, state_dir, logger,
                            args.params, args.approval)
        if gated is None:
            return 2
        params, client = gated
        try:
            return run_loop(params, client, SCRIPT_DIR, state_dir,
                            logger)
        finally:
            try:
                client.close()
            except Exception:
                pass
    if args.dry_run:
        return mode_dry_run(SCRIPT_DIR, state_dir, logger, args)
    return mode_check(SCRIPT_DIR, state_dir, logger,
                      args.params, args.approval)


if __name__ == "__main__":
    sys.exit(main())
