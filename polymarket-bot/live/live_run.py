"""Polymarket LIVE bot — PAKET KODE SAJA, BUKAN BOT YANG BERJALAN.

PERINGATAN PALING PENTING: paket ini TIDAK PERNAH menempatkan order
nyata dengan sendirinya. Live trading BELUM disetujui, kredensial
BELUM ADA, dan file ini tidak berisi kredensial apa pun. Kode mode
live di bawah hanya bisa berjalan setelah SEMUA gerbang lolos DAN
pemilik menyetujui parameter secara eksplisit. Sampai saat itu, paket
ini adalah persiapan dan alat cek saja.

Dua mode:
  check (default) : hanya baca — kehadiran environment (nama saja,
                    BUKAN nilainya), status geoblock dari mesin ini,
                    bacaan pasar publik Gamma, dan validasi params
                    bila params.json ada. TIDAK PERNAH membuat order,
                    TIDAK PERNAH menurunkan kredensial, TIDAK PERNAH
                    mengirim request privat.
  --live          : HANYA jika SEMUA gerbang lolos SEBELUM koneksi
                    jaringan apa pun yang bisa berujung order. Satu
                    gerbang gagal = berhenti, nol order.

Gerbang live (semua wajib, diperiksa sebelum request order apa pun):
  1. Flag --live diberikan.
  2. Environment LIVE_TRADING=1.
  3. File LIVE_APPROVED.txt ada di folder skrip ini, berisi
     persetujuan pemilik (tanggal + kategori + nominal yang
     disetujui). File ini TIDAK BOLEH dibuat oleh skrip ini dan
     TIDAK ADA di paket ini — pemilik membuatnya sendiri hanya
     saat menyetujui.
  4. File params.json ada (salin dari params.example.json HANYA
     setelah parameter disetujui) dan lolos validasi: kategori
     dalam allowlist, chain polygon, kolateral USDC, modal > 0,
     0 < first_trade <= modal, SL 1-50%, TP 1-50%, kill-switch
     5-50%. TP < SL hanya peringatan, bukan penolakan.
  5. Geoblock: endpoint polymarket.com/api/geoblock dari mesin ini
     TIDAK menyatakan blocked. Bila blocked atau tidak dapat
     dipastikan, live DITOLAK. TIDAK ADA pengelakan: jangan pakai
     VPN/proxy untuk mengakali — pindahkan proses ke mesin yang
     diizinkan.
  6. Private key wallet live ada di environment mesin ini
     (POLY_PRIVATE_KEY, nama saja yang diperiksa, nilai tidak
     pernah dicetak). Kredensial CLOB TIDAK dibaca dari nilai
     POLY_API_KEY/POLY_SECRET/POLY_PASSPHRASE yang tersimpan —
     nilai-nilai itu, bila ada di environment, DIABAIKAN.
     Kredensial diturunkan ulang tiap kali bot jalan (runtime
     re-derivation) dari private key lewat SDK resmi, hanya di
     memori, tidak pernah dicetak, tidak pernah ditulis ke file.

Kredensial (L1 + L2, ringkas — detail di README):
  - L1: wallet menandatangani pesan EIP-712 ClobAuth, lalu SDK
    resmi menurunkan apiKey + secret + passphrase — SETIAP kali
    bot jalan, dari POLY_PRIVATE_KEY saja (runtime re-derivation).
    Hasil derive hanya hidup di memori proses ini dan tidak pernah
    dicetak, tidak pernah ditulis ke file/log, tidak pernah
    dikirim ke chat/repo.
  - L2: setiap request privat ditandatangani HMAC-SHA256; setiap
    order juga membawa tanda tangan wallet sendiri.
  - SDK resmi Python: paket pip `polymarket-client` (repo
    Polymarket/py-sdk), modul impornya `polymarket`, versi 0.15.0
    terpasang di host (log pip 2026-11-01). Entry point-nya
    `polymarket.SecureClient.create(private_key, wallet)` — di
    dalam create(), SDK menandatangani pesan L1 ClobAuth (EIP-712,
    chain 137) dan memanggil endpoint create/derive, lalu
    memvalidasi kredensial. JANGAN pakai py-clob-client (diarsipkan,
    order V1 ditolak sejak CLOB V2 live). Nama modul impor yang
    lama dan salah TIDAK ADA di SDK ini dan tidak boleh dipakai —
    itulah penyebab CHECK lama melaporkan SDK tidak terpasang
    padahal pip sudah memasang paketnya.
  - Satu-satunya rahasia yang dipegang mesin host adalah
    POLY_PRIVATE_KEY, diketik pemilik sendiri ke environment mesin
    itu. TIDAK PERNAH dari file di repo, chat, screenshot, atau
    output skrip ini.

Aturan besi yang dikodekan di sini (bukan sekadar janji):
  - Respons error order TIDAK MEMBUKTIKAN tidak terjadi fill.
    Setelah error apa pun, skrip TIDAK PERNAH me-retry otomatis:
    ia membaca ulang state (saldo/order) dan BERHENTI, menyerahkan
    verifikasi manual kepada pemilik.
  - Kill-switch menghentikan loop sepenuhnya.
  - Order minimum 5 lembar ditegakkan: ukuran di bawah itu
    DITOLAK, bukan dibulatkan ke atas secara diam-diam.
  - Binary/spot saja. Tanpa leverage, tanpa margin, tanpa
    futures, tanpa withdrawal (tidak ada pemanggilan withdraw
    dalam bentuk apa pun di paket ini).
  - Trigger jual diukur ask-ke-ask; hasil jual dihitung di bid
    (cermin modul paper). Prioritas: kill-switch > SL > TP2/TP20
    > TP1.

Kode keluar: 0 = selesai, 1 = gagal operasional (nol order baru),
2 = kredensial tidak lengkap (mode live), 3 = gerbang/params
ditolak (nol order).
"""

import argparse
import json
import os
import sys
import urllib.error
import urllib.request

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

# --- Konstanta publik (bukan rahasia) -------------------------------------
GEOBLOCK_URL = "https://polymarket.com/api/geoblock"
GAMMA_URL = "https://gamma-api.polymarket.com/markets"
CATEGORY_ALLOWLIST = ("updown", "weather", "soccer")
CHAIN = "polygon"
COLLATERAL = "USDC"
# Alamat-alamat publik akun utama di Polygon (bukan rahasia).
# Akun utama (perubahan rencana 2026-11-01: akun utama adalah wallet
# live; wallet bot Bitget diparkir dan TIDAK dipakai) berstruktur
# SIGNER + DEPOSIT: private key mengendalikan alamat SIGNER, dana
# berada di alamat PROFIL/deposit. Keduanya milik akun yang sama,
# tetapi HANYA alamat signer yang boleh menjadi identitas trading:
# pengecekan lokal + SecureClient.create() memakai signer.
# Memakai alamat profil sebagai wallet pernah menolak kunci yang
# benar (verifikasi 2026-11-02): alamat turunan kunci adalah signer,
# bukan profil.
LIVE_WALLET_ADDRESS = "0xc4bA60A94edBfeF6CD7177B6e6e02b1c2b17B4FB"
SIGNER_WALLET_ADDRESS = "0x911379D40dc42d8198baA4f1b7bB29b71A7d3d72"
MIN_ORDER_SIZE = 5
# Epsilon untuk perbandingan harga float (mis. 0.10 * 1.10 =
# 0.11000000000000001, bukan 0.11): tanpa ini, harga yang TEPAT di level
# TP/SL bisa lolos dari trigger.
EPS = 1e-9
TIMEOUT = 30
USER_AGENT = ("Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
              "(KHTML, like Gecko) Chrome/126.0 Safari/537.36")

# Nama environment SAJA. Nilai tidak pernah dibaca untuk dicetak,
# tidak pernah ditulis ke file, tidak pernah masuk log.
# SATU-SATUNYA rahasia yang dibaca bot: POLY_PRIVATE_KEY, untuk
# derive ulang kredensial tiap jalan (in-memory). Nama-nama lama
# POLY_API_KEY/POLY_SECRET/POLY_PASSPHRASE/POLY_ADDRESS TIDAK
# LAGI dibaca sebagai kredensial — bila ada di environment, nilainya
# diabaikan dan hanya kehadirannya yang dilaporkan satu baris.
ENV_PRIVATE_KEY = "POLY_PRIVATE_KEY"
IGNORED_OLD_CRED_NAMES = ("POLY_API_KEY", "POLY_SECRET",
                          "POLY_PASSPHRASE", "POLY_ADDRESS")

# Default risiko (cermin modul paper; CONTOH, bukan persetujuan live).
DEFAULTS = {
    "updown": {"tp_pct": 20.0, "tp_mode": "sell_all_rotate",
               "sl_pct": 5.0, "kill_switch_pct": 15.0},
    "weather": {"tp1_pct": 10.0, "tp2_pct": 15.0, "tp_mode": "ladder",
                "sl_pct": 5.0, "kill_switch_pct": 15.0},
    "soccer": {"tp1_pct": 10.0, "tp2_pct": 15.0, "tp_mode": "ladder",
               "sl_pct": 5.0, "kill_switch_pct": 15.0},
}


# --- Utilitas HTTP publik -------------------------------------------------
def http_get_json(url):
    """Satu GET publik, mengembalikan (status, payload). Tanpa kredensial."""
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT},
                                 method="GET")
    try:
        with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
            raw = resp.read().decode("utf-8", "replace")
            return resp.status, _try_json(raw)
    except urllib.error.HTTPError as e:
        return e.code, _try_json(e.read().decode("utf-8", "replace"))
    except Exception as e:  # transport gagal: laporkan, jangan traceback
        return 0, {"_transport_error": f"{type(e).__name__}: {e}"}


def _try_json(raw):
    try:
        return json.loads(raw)
    except ValueError:
        return {"_raw": raw[:300]}


def parse_geoblock(payload):
    """Tafsirkan respons geoblock menjadi: 'blocked' | 'allowed' | 'unknown'.

    Bentuk respons tidak diasumsikan kaku: kunci blocked/isBlocked/
    geoBlocked bernilai benar berarti blocked; nilai salah berarti
    allowed; sisanya (termasuk error transport) berarti unknown dan
    mode live WAJIB menolak (fail-closed).
    """
    if not isinstance(payload, dict) or payload.get("_transport_error"):
        return "unknown"
    for key in ("blocked", "isBlocked", "geoBlocked", "geo_blocked"):
        if key in payload:
            return "blocked" if payload[key] else "allowed"
    return "unknown"


# --- Environment: kehadiran saja, nilai tidak pernah dicetak ---------------
def sdk_available():
    """True hanya bila modul SDK resmi bisa diimpor di mesin ini.

    Nama modul impor SDK 0.15.0 adalah `polymarket` (nama paket
    pip-nya polymarket-client). Memeriksa nama modul lain akan
    selalu gagal meski paket sudah terpasang — itulah bug CHECK
    lama: pip memasang paketnya, CHECK tetap melaporkan SDK tidak
    terpasang.
    """
    import importlib.util
    return importlib.util.find_spec("polymarket") is not None


def env_presence():
    """{nama_env: True/False} untuk private key saja.

    Nilai TIDAK PERNAH dibaca untuk output. Nama kredensial lama
    (POLY_API_KEY dkk.) sengaja TIDAK masuk dict ini: bot tidak
    lagi membacanya sebagai kredensial.
    """
    return {ENV_PRIVATE_KEY: bool(os.environ.get(ENV_PRIVATE_KEY))}


def report_env_presence():
    print("Kredensial di environment (kehadiran saja, nilai tidak dicetak):")
    for name, present in env_presence().items():
        print(f"  {name}: {'ada' if present else 'TIDAK ADA'}")
    print(f"  SDK resmi (modul polymarket, paket polymarket-client): "
          f"{'terpasang' if sdk_available() else 'TIDAK TERPASANG'}")
    if any(os.environ.get(n) for n in IGNORED_OLD_CRED_NAMES):
        print("  Catatan: nama kredensial API tersimpan terdeteksi di")
        print("  environment, tetapi DIABAIKAN oleh bot — kredensial")
        print("  diturunkan ulang tiap jalan dari private key saja.")
    print("  Pola baru: bot derive ulang kredensial tiap jalan dari")
    print("  private key (in-memory, tidak dicetak, tidak disimpan).")
    print("  Private key diketik pemilik sendiri ke environment mesin")
    print("  host; tidak pernah ke chat, repo, atau screenshot.")


def local_wallet_address(private_key):
    """Alamat publik dari private key, dihitung lokal, tanpa jaringan.

    Mengembalikan (alamat_atau_None, status). Nilai private key tidak
    pernah dikembalikan/dicetak; hanya alamat publik (bila berhasil)
    dan kata status yang keluar dari fungsi ini.
    """
    if not private_key:
        return None, "skipped (private key absent)"
    try:
        from eth_account import Account
    except Exception:
        return None, "skipped (address library not installed)"
    try:
        return Account.from_key(private_key).address, "ok"
    except Exception:
        return None, "failed"


# --- Validasi params (murni, tanpa I/O — bisa dites offline) ---------------
def validate_params_data(p):
    """Mengembalikan (errors, warnings). errors kosong = lolos.

    Aturan: kategori dalam allowlist; chain polygon; kolateral USDC;
    modal > 0; 0 < first_trade <= modal; SL 1-50; TP 1-50;
    kill-switch 5-50; ukuran order minimum 5. TP < SL = peringatan.
    """
    errors = []
    warnings = []
    if not isinstance(p, dict):
        return ["params harus berupa objek JSON"], warnings
    if p.get("category") not in CATEGORY_ALLOWLIST:
        errors.append(f"category harus salah satu dari {CATEGORY_ALLOWLIST}")
    if p.get("chain") != CHAIN:
        errors.append(f"chain harus {CHAIN}")
    if p.get("collateral") != COLLATERAL:
        errors.append(f"collateral harus {COLLATERAL}")
    modal = p.get("modal_usd")
    if not isinstance(modal, (int, float)) or isinstance(modal, bool) \
            or modal <= 0:
        errors.append("modal_usd harus angka > 0")
    first = p.get("first_trade_usd")
    if not isinstance(first, (int, float)) or isinstance(first, bool) \
            or first <= 0:
        errors.append("first_trade_usd harus angka > 0")
    elif isinstance(modal, (int, float)) and first > modal:
        errors.append("first_trade_usd harus <= modal_usd")
    sl = p.get("sl_pct")
    if not isinstance(sl, (int, float)) or isinstance(sl, bool) \
            or not (1 <= sl <= 50):
        errors.append("sl_pct harus 1-50")
    tp = p.get("tp_pct")
    tp1 = p.get("tp1_pct")
    tp2 = p.get("tp2_pct")
    cat = p.get("category")
    if cat == "updown":
        if not isinstance(tp, (int, float)) or isinstance(tp, bool) \
                or not (1 <= tp <= 50):
            errors.append("updown: tp_pct harus 1-50")
        elif isinstance(sl, (int, float)) and tp < sl:
            warnings.append("PERINGATAN: TP < SL — risiko lebih besar "
                            "dari untung.")
    elif cat in ("weather", "soccer"):
        if not isinstance(tp1, (int, float)) or isinstance(tp1, bool) \
                or not (1 <= tp1 <= 50):
            errors.append("tp1_pct harus 1-50")
        if not isinstance(tp2, (int, float)) or isinstance(tp2, bool) \
                or not (1 <= tp2 <= 50):
            errors.append("tp2_pct harus 1-50")
        if isinstance(tp1, (int, float)) and isinstance(tp2, (int, float)) \
                and tp2 < tp1:
            errors.append("tp2_pct harus >= tp1_pct")
        elif isinstance(sl, (int, float)) and isinstance(tp1, (int, float)) \
                and tp1 < sl:
            warnings.append("PERINGATAN: TP1 < SL — risiko lebih besar "
                            "dari untung.")
    ks = p.get("kill_switch_pct")
    if not isinstance(ks, (int, float)) or isinstance(ks, bool) \
            or not (5 <= ks <= 50):
        errors.append("kill_switch_pct harus 5-50")
    min_size = p.get("min_order_size", MIN_ORDER_SIZE)
    if not isinstance(min_size, (int, float)) or min_size < MIN_ORDER_SIZE:
        errors.append(f"min_order_size minimal {MIN_ORDER_SIZE}")
    return errors, warnings


def load_params(path):
    """Baca params.json; mengembalikan (params, errors, warnings)."""
    try:
        with open(path) as f:
            p = json.load(f)
    except (OSError, ValueError) as e:
        return None, [f"params.json tidak bisa dibaca ({e})"], []
    errors, warnings = validate_params_data(p)
    return p, errors, warnings


# --- Gerbang live (diperiksa SEBELUM request order apa pun) ----------------
def check_gates(script_dir=SCRIPT_DIR):
    """Periksa semua gerbang live. Gagal -> SystemExit(3), nol order.

    Urutan: flag env -> file persetujuan -> params -> geoblock ->
    kredensial. TIDAK ADA request order sebelum fungsi ini kembali.
    """
    if os.environ.get("LIVE_TRADING") != "1":
        print("Gerbang live gagal: LIVE_TRADING=1 belum diset.")
        raise SystemExit(3)
    approved_path = os.path.join(script_dir, "LIVE_APPROVED.txt")
    if not os.path.isfile(approved_path):
        print("Gerbang live gagal: LIVE_APPROVED.txt tidak ditemukan.")
        print("File ini dibuat HANYA saat pemilik menyetujui parameter live.")
        raise SystemExit(3)
    with open(approved_path) as f:
        lines = f.read().strip().splitlines()
    print(f"Persetujuan tercatat: {lines[0] if lines else '(kosong)'}")
    params_path = os.path.join(script_dir, "params.json")
    if not os.path.isfile(params_path):
        print("Gerbang live gagal: params.json tidak ditemukan.")
        print("Salin params.example.json menjadi params.json HANYA setelah")
        print("parameter disetujui pemilik.")
        raise SystemExit(3)
    params, errors, warnings = load_params(params_path)
    if errors:
        print("params.json DITOLAK:")
        for e in errors:
            print(f"  - {e}")
        raise SystemExit(3)
    for w in warnings:
        print(w)
    status, payload = http_get_json(GEOBLOCK_URL)
    verdict = parse_geoblock(payload)
    print(f"Geoblock dari mesin ini: {verdict} (HTTP {status}).")
    if verdict != "allowed":
        print("Gerbang live gagal: mesin ini TIDAK dipastikan diizinkan.")
        print("JANGAN pakai VPN/proxy untuk mengakali — pindahkan proses")
        print("ke mesin yang diizinkan.")
        raise SystemExit(3)
    missing = [n for n, ok in env_presence().items() if not ok]
    if missing:
        print("Gerbang live gagal: private key belum ada di environment:")
        for n in missing:
            print(f"  - {n} TIDAK ADA")
        print("Pemilik mengetik POLY_PRIVATE_KEY sendiri ke environment")
        print("mesin host; bot derive ulang kredensial tiap jalan dari")
        print("kunci itu. Jangan tulis nilainya di file, chat, atau")
        print("screenshot. Kredensial API tersimpan (bila ada) sengaja")
        print("DIABAIKAN — bot tidak membacanya.")
        raise SystemExit(2)
    if not sdk_available():
        print("Gerbang live gagal: SDK resmi (modul polymarket) belum")
        print("terpasang di mesin ini. Host menginstal requirements.txt")
        print("dulu; nol order dibuat.")
        raise SystemExit(2)
    print("Semua gerbang live lolos.")
    return params


# --- Logika exit (murni, cermin modul paper) -------------------------------
def enforce_min_size(shares, min_size=MIN_ORDER_SIZE):
    """Order di bawah minimum DITOLAK (kembalikan 0), bukan dibulatkan."""
    if shares < min_size:
        return 0
    return shares


def decide_exit(entry_ask, ask, bid, remaining, tp1_done, total_value,
                start_value, category, sl_pct, tp_pct=None, tp1_pct=None,
                tp2_pct=None, kill_switch_pct=15.0):
    """Keputusan jual, cermin paper_exit.py + paper_categories.py.

    Trigger ask-ke-ask; hasil jual dihitung di bid oleh pemanggil.
    Prioritas: kill-switch > SL > TP2/TP20 > TP1.
    Mengembalikan (aksi, jumlah, alasan); aksi: HOLD, SELL_PARTIAL,
    SELL_ALL, BLOCKED_MIN_SIZE.
    """
    if total_value <= start_value * (1 - kill_switch_pct / 100) + EPS:
        qty = enforce_min_size(remaining)
        return ("SELL_ALL", qty, "KILL_SWITCH") if qty else \
            ("BLOCKED_MIN_SIZE", 0, "KILL_SWITCH_MIN_SIZE")
    if ask <= entry_ask * (1 - sl_pct / 100) + EPS:
        qty = enforce_min_size(remaining)
        return ("SELL_ALL", qty, "SL") if qty else \
            ("BLOCKED_MIN_SIZE", 0, "SL_MIN_SIZE")
    if category == "updown":
        if tp_pct is not None and \
                ask + EPS >= entry_ask * (1 + tp_pct / 100):
            qty = enforce_min_size(remaining)
            return ("SELL_ALL", qty, "TP20") if qty else \
                ("BLOCKED_MIN_SIZE", 0, "TP_MIN_SIZE")
    else:  # ladder: weather / soccer
        if tp2_pct is not None and tp1_done and \
                ask + EPS >= entry_ask * (1 + tp2_pct / 100):
            qty = enforce_min_size(remaining)
            return ("SELL_ALL", qty, "TP2") if qty else \
                ("BLOCKED_MIN_SIZE", 0, "TP_MIN_SIZE")
        if tp1_pct is not None and not tp1_done and \
                ask + EPS >= entry_ask * (1 + tp1_pct / 100):
            qty = remaining // 2
            qty = enforce_min_size(qty)
            return ("SELL_PARTIAL", qty, "TP1") if qty else \
                ("BLOCKED_MIN_SIZE", 0, "TP_MIN_SIZE")
    return ("HOLD", 0, "HOLD")


# --- Aturan pasca-error: TIDAK PERNAH retry otomatis -----------------------
def decide_after_order_error(verified_state):
    """Setelah respons error order apa pun: SELALU berhenti.

    verified_state hanya dipakai untuk laporan (apakah fill terverifikasi
    atau tidak); apa pun isinya, keputusannya sama: jangan retry.
    Respons error TIDAK MEMBUKTIKAN tidak terjadi fill — verifikasi
    manual oleh pemilik wajib sebelum tindakan apa pun berikutnya.
    """
    return ("ABORT_NO_RETRY", verified_state)


def should_retry_after_error():
    """Jawaban atas 'bolehkah retry otomatis setelah error order?'.

    Selalu False. Fungsi ini ada supaya aturan ini bisa dites.
    """
    return False


# --- Mode CHECK ------------------------------------------------------------
def mode_check():
    print("Mode: CHECK (hanya baca, tanpa order, tanpa request privat).")
    print(f"Wallet live profil/deposit (alamat publik): "
          f"{LIVE_WALLET_ADDRESS}")
    print(f"Wallet signer (alamat publik, identitas trading): "
          f"{SIGNER_WALLET_ADDRESS}")
    report_env_presence()
    status, payload = http_get_json(GEOBLOCK_URL)
    print(f"Geoblock dari mesin ini: {parse_geoblock(payload)} "
          f"(HTTP {status}).")
    if parse_geoblock(payload) == "blocked":
        print("PERINGATAN: mesin ini diblokir untuk order — mode live akan")
        print("ditolak di sini. Pindahkan proses ke mesin yang diizinkan,")
        print("bukan dengan VPN/proxy.")
    status, payload = http_get_json(GAMMA_URL + "?limit=1&active=true")
    if isinstance(payload, dict) and payload.get("_transport_error"):
        print(f"Baca pasar publik Gamma GAGAL: {payload['_transport_error']}")
    elif isinstance(payload, list):
        print(f"Baca pasar publik Gamma OK: {len(payload)} market (limit 1).")
    else:
        print(f"Baca pasar publik Gamma: HTTP {status}, bentuk tak dikenal.")
    params_path = os.path.join(SCRIPT_DIR, "params.json")
    if os.path.isfile(params_path):
        _, errors, warnings = load_params(params_path)
        if errors:
            print("params.json DITOLAK (cek saja, tanpa order):")
            for e in errors:
                print(f"  - {e}")
        else:
            print("params.json lolos validasi (cek saja, tanpa order).")
        for w in warnings:
            print(w)
    else:
        print("params.json belum ada — wajar untuk paket persiapan.")
        print("params.example.json adalah CONTOH, bukan persetujuan.")
    print("CHECK SELESAI. Nol order dibuat, nol kredensial diturunkan")
    print("(derive hanya terjadi di mode live setelah gerbang lolos),")
    print("nol request privat dikirim, nol nilai rahasia dicetak.")
    return 0


# --- Mode LIVE (hanya setelah semua gerbang lolos) -------------------------
def build_sdk_client():
    """Bangun klien SDK resmi via RUNTIME RE-DERIVATION.

    Pola: tiap kali bot jalan, kredensial diturunkan dari
    POLY_PRIVATE_KEY lewat entry point resmi SDK 0.15.0,
    `polymarket.SecureClient.create(private_key, wallet)` — di
    dalam create(), SDK menandatangani pesan L1 ClobAuth dan
    memanggil endpoint create/derive, lalu memvalidasi kredensial.
    Kredensial hidup hanya di memori proses ini: TIDAK PERNAH
    dicetak, ditulis ke file, atau disimpan di luar proses.
    Kredensial API yang tersimpan di environment (POLY_API_KEY
    dkk.) sengaja TIDAK dibaca — bila ada, nilainya diabaikan.

    Penjaga efek samping: verifikasi alamat lokal WAJIB lolos
    SEBELUM create() dipanggil. Alasannya: create() untuk tipe
    wallet non-EOA yang belum ter-deploy dapat men-deploy deposit
    wallet on-chain — efek samping yang tidak boleh terjadi dari
    langkah verifikasi. Akun ini berstruktur signer + deposit:
    kunci mengendalikan alamat SIGNER, sedangkan alamat profil
    adalah deposit tempat dana berada. Karena create() dipanggil
    dengan alamat signer (EOA yang dikendalikan kunci), create()
    tidak melakukan deploy apa pun. Bila alamat tidak bisa
    diverifikasi lokal, gagal aman.

    Mengembalikan klien SDK, atau None bila SDK tidak terpasang /
    tidak bisa diimpor, alamat tidak terverifikasi / tidak cocok,
    create() gagal, wallet klien tidak cocok, atau kredensial
    klien tidak lengkap — dalam semua kasus: nol order.
    """
    private_key = os.environ.get(ENV_PRIVATE_KEY)
    if not private_key:
        print("Private key tidak ada di environment — nol order dibuat.")
        return None
    if not sdk_available():
        print("SDK resmi (modul polymarket) belum terpasang di mesin ini.")
        print("Host menginstal requirements.txt dulu; nol order dibuat.")
        return None
    try:
        from polymarket import SecureClient
    except ImportError:
        print("SDK resmi (modul polymarket) tidak bisa diimpor di mesin")
        print("ini — nol order dibuat.")
        return None
    address, status = local_wallet_address(private_key)
    if address is None:
        print(f"Alamat tidak diverifikasi lokal ({status}) — "
              "nol order dibuat.")
        return None
    if address.lower() != SIGNER_WALLET_ADDRESS.lower():
        print("Private key TIDAK cocok dengan wallet signer yang")
        print("disetujui — nol order dibuat.")
        return None
    print("Alamat wallet signer terverifikasi lokal (nilai kunci tidak")
    print("dicetak).")
    try:
        client = SecureClient.create(private_key=private_key,
                                     wallet=SIGNER_WALLET_ADDRESS)
    except Exception as e:
        print(f"Klien SDK gagal dibangun ({type(e).__name__}) — "
              "nol order dibuat.")
        return None
    try:
        wallet = client.wallet
        creds = client.credentials
    except Exception:
        wallet, creds = None, None
    complete = bool(wallet) and \
        str(wallet).lower() == SIGNER_WALLET_ADDRESS.lower() and \
        creds is not None and bool(getattr(creds, "key", None)) and \
        bool(getattr(creds, "secret", None)) and \
        bool(getattr(creds, "passphrase", None))
    if not complete:
        print("Klien SDK tidak lengkap / wallet tidak cocok dengan")
        print("wallet signer — nol order dibuat.")
        try:
            client.close()
        except Exception:
            pass
        return None
    print("Klien SDK resmi berhasil dibangun (kredensial hanya di memori")
    print("proses ini, nilai tidak dicetak).")
    return client


def verify_state_via_sdk(client):
    """Baca ulang state (open orders) lewat SDK. Gagal -> dict error.

    Fungsi ini adalah satu-satunya dasar verifikasi setelah error:
    tidak ada asumsi, tidak ada retry buta. Hanya jumlah order
    terbuka yang dilaporkan — tidak ada nilai sensitif.
    """
    if client is None:
        return None
    try:
        reader = getattr(client, "list_open_orders", None)
        if reader is None:
            return {"orders": "unknown"}
        first = reader().first_page()
        items = getattr(first, "items", None)
        count = len(items) if items is not None else "unknown"
        return {"orders": count}
    except Exception as e:
        return {"error": f"{type(e).__name__}"}


def mode_live(params):
    """Satu siklus live: verifikasi dulu, order hanya lewat SDK resmi.

    Di paket persiapan ini, siklus berhenti pada verifikasi state dan
    TIDAK menempatkan order sampai antarmuka order SDK terverifikasi
    di mesin host. Itu disengaja: lebih baik nol order daripada order
    dari antarmuka yang belum terbukti.
    """
    print("Mode: LIVE — gerbang sudah lolos, verifikasi state dulu.")
    client = build_sdk_client()
    if client is None:
        return 1
    state = verify_state_via_sdk(client)
    print(f"State terverifikasi (ringkasan, tanpa nilai sensitif): "
          f"{list(state.keys()) if isinstance(state, dict) else 'gagal'}")
    if state is None or "error" in state:
        action, _ = decide_after_order_error(state)
        print(f"Verifikasi state gagal -> {action}. Nol order baru, "
              "tidak ada retry otomatis.")
        return 1
    print("Siklus live berhenti di sini pada paket persiapan ini: state")
    print("terbaca, tetapi order TIDAK ditempatkan sampai pemilik")
    print("memverifikasi antarmuka order SDK di mesin host dan menyetujui")
    print("parameter live secara eksplisit.")
    print("Nol order dibuat oleh run ini.")
    return 0


def main():
    ap = argparse.ArgumentParser(
        description="Polymarket LIVE bot — paket kode persiapan.")
    ap.add_argument("--live", action="store_true",
                    help="Aktifkan mode live (wajib lolos semua gerbang).")
    args = ap.parse_args()
    if args.live:
        params = check_gates()
        return mode_live(params)
    return mode_check()


if __name__ == "__main__":
    sys.exit(main())
