"""Wiring order Polymarket — antarmuka order SDK resmi, tanpa tebakan.

Sumber kebenaran antarmuka: wheel publik polymarket-client==0.15.0
(modul impor `polymarket`, dibaca langsung 2026-11-02). JANGAN pakai
nama lama (polymarket_client, ClobClient, createOrDeriveApiKey) —
terbukti tidak ada di 0.15.0.

Antarmuka yang DIPAKAI (semua di `polymarket.SecureClient`):
- create_limit_order(*, token_id, price, size, side, post_only=False,
  expiration=None) -> SignedOrder
  "Create and sign a limit order without posting it."
- create_market_order(*, token_id, side, amount=None, shares=None,
  max_spend=None, max_price=None, min_price=None, order_type="FAK")
  -> SignedOrder
  BUY memakai `amount` (USDC yang dibelanjakan); SELL memakai
  `shares` (lembar yang dijual); max_price/min_price membatasi
  harga eksekusi. "Create and sign a market order without posting."
- place_limit_order(...) / place_market_order(...) -> OrderResponse
  (create + sign + post sekaligus, dengan allowance recovery).
- post_order(signed_order) -> OrderResponse
  (mengirim SignedOrder yang sudah dibuat + ditandatangani).
- post_orders(signed_orders) -> tuple[OrderResponse, ...]
- cancel_order(*, order_id) / cancel_orders / cancel_all
- list_open_orders(*, token_id=None) -> Paginator[OpenOrder]
  (v4 terverifikasi di host: .first_page().items)
- get_order(*, order_id) -> OpenOrder
- SignedOrder (dataclass): builder, expiration, maker, maker_amount,
  metadata, order_type, salt, side, signature, signature_type,
  signer, taker_amount, timestamp, token_id, post_only.
- OrderResponse sukses: order_id, status ("live"/"matched"/
  "delayed"), making_amount, taking_amount, trade_ids.

ATURAN KEAMANAN modul ini:
- TIDAK ADA order nyata yang dibuat modul ini sendiri: fungsi
  build_* hanya membangun + menandatangani (tanpa POST).
  POST hanya terjadi lewat fungsi post_*/place_* yang eksplisit,
  dan loop memanggilnya HANYA di mode live (bukan DRY-RUN).
- TIDAK ADA nilai sensitif yang dicetak/dikembalikan: ringkasan
  order SENGAJA menghilangkan `signature` (dan `salt`).
- Alamat yang muncul di file ini hanya alamat PUBLIK (signer +
  profil/deposit akun utama). Private key dibaca dari environment
  saat jalan, tidak pernah dari file ini.
- Impor SDK dilakukan LAZAT di dalam fungsi (bukan di atas modul)
  supaya modul ini bisa dites tanpa SDK terpasang, dengan klien
  palsu yang disuntikkan lewat parameter `client`.
"""

import importlib.util
import os

# Alamat publik akun utama (bukan rahasia). Struktur SIGNER + DEPOSIT:
# private key mengendalikan SIGNER (identitas trading); dana berada
# di PROFIL/deposit (referensi saja).
SIGNER_WALLET_ADDRESS = "0x911379D40dc42d8198baA4f1b7bB29b71A7d3d72"
PROFILE_WALLET_ADDRESS = "0xc4bA60A94edBfeF6CD7177B6e6e02b1c2b17B4FB"

ENV_PRIVATE_KEY = "POLY_PRIVATE_KEY"

ORDER_SIDES = ("BUY", "SELL")
MARKET_ORDER_TYPES = ("FAK", "FOK")


# --- Ketersediaan SDK + alamat lokal (cermin paket v4) --------------------

def sdk_available():
    """True hanya bila modul resmi `polymarket` bisa diimpor."""
    return importlib.util.find_spec("polymarket") is not None


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


def _get_secure_client_class():
    """Kelas SecureClient resmi, atau None bila SDK tidak terpasang."""
    try:
        from polymarket import SecureClient
        return SecureClient
    except Exception:
        return None


def build_sdk_client(private_key):
    """Bangun klien SDK resmi dengan penjaga alamat signer.

    Mengembalikan klien, atau None bila: kunci tidak ada, SDK tidak
    terpasang, alamat turunan tidak bisa diverifikasi, alamat turunan
    BUKAN signer yang disetujui, atau create() gagal. Dalam semua
    kasus gagal: nol order. Alamat profil/deposit TIDAK PERNAH dipakai
    sebagai wallet create() — kunci tidak mengendalikannya, dan
    create() untuk wallet non-EOA yang belum ter-deploy bisa
    men-deploy deposit wallet on-chain (efek samping yang dilarang
    untuk langkah verifikasi).
    """
    if not private_key:
        print("Private key tidak ada di environment — nol order dibuat.")
        return None
    if not sdk_available():
        print("SDK resmi (modul polymarket) belum terpasang di mesin ini.")
        return None
    secure_cls = _get_secure_client_class()
    if secure_cls is None:
        print("SDK resmi (modul polymarket) tidak bisa diimpor — "
              "nol order dibuat.")
        return None
    address, status = local_wallet_address(private_key)
    if address is None:
        print(f"Alamat tidak diverifikasi lokal ({status}) — "
              "nol order dibuat.")
        return None
    if address.lower() != SIGNER_WALLET_ADDRESS.lower():
        print("Private key TIDAK cocok dengan wallet signer yang "
              "disetujui — nol order dibuat.")
        return None
    print("Alamat wallet signer terverifikasi lokal (nilai kunci tidak "
          "dicetak).")
    try:
        client = secure_cls.create(private_key=private_key,
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
        print("Klien SDK tidak lengkap / wallet tidak cocok dengan "
              "wallet signer — nol order dibuat.")
        try:
            client.close()
        except Exception:
            pass
        return None
    print("Klien SDK resmi berhasil dibangun (kredensial hanya di memori "
          "proses ini, nilai tidak dicetak).")
    return client


# --- Validasi argumen order (murni, tanpa I/O) -----------------------------

def _is_number(x):
    return isinstance(x, (int, float)) and not isinstance(x, bool)


def validate_limit_args(token_id, price, size, side):
    """Mengembalikan list error (kosong = lolos). Tidak menyentuh klien."""
    errors = []
    if not isinstance(token_id, str) or not token_id.strip() \
            or not token_id.strip().isdigit():
        errors.append("token_id harus string digit CLOB yang tidak kosong")
    if not _is_number(price) or not (0 < price < 1):
        errors.append("price limit harus angka 0 < price < 1 (harga biner)")
    if not _is_number(size) or size <= 0:
        errors.append("size harus angka > 0")
    if side not in ORDER_SIDES:
        errors.append(f"side harus salah satu dari {ORDER_SIDES}")
    return errors


def validate_market_args(side, amount, shares, order_type="FAK"):
    """Mengembalikan list error (kosong = lolos). Tidak menyentuh klien."""
    errors = []
    if side not in ORDER_SIDES:
        errors.append(f"side harus salah satu dari {ORDER_SIDES}")
        return errors
    if order_type not in MARKET_ORDER_TYPES:
        errors.append(f"order_type harus salah satu dari "
                      f"{MARKET_ORDER_TYPES}")
    if side == "BUY":
        if not _is_number(amount) or amount <= 0:
            errors.append("market BUY butuh amount (USDC) > 0")
        if shares is not None:
            errors.append("market BUY tidak memakai shares")
    else:
        if not _is_number(shares) or shares <= 0:
            errors.append("market SELL butuh shares > 0")
        if amount is not None:
            errors.append("market SELL tidak memakai amount")
    return errors


# --- Bangun + tanda tangani (TANPA POST) ----------------------------------

def build_limit_order(client, *, token_id, price, size, side,
                      post_only=False, expiration=None):
    """Bangun + tanda tangani limit order. TIDAK POST.

    Validasi jalan DULU: argumen tidak valid -> ValueError SEBELUM
    klien disentuh (dibuktikan tes: klien palsu mencatat nol panggilan).
    """
    errors = validate_limit_args(token_id, price, size, side)
    if errors:
        raise ValueError("argumen limit order tidak valid: " +
                         "; ".join(errors))
    kwargs = {"token_id": token_id, "price": price, "size": size,
              "side": side, "post_only": bool(post_only)}
    if expiration is not None:
        kwargs["expiration"] = expiration
    return client.create_limit_order(**kwargs)


def build_market_order(client, *, token_id, side, amount=None, shares=None,
                       max_price=None, min_price=None, order_type="FAK"):
    """Bangun + tanda tangani market order. TIDAK POST.

    BUY: amount = USDC yang dibelanjakan (boleh dibatasi max_price /
    max_spend). SELL: shares = lembar yang dijual (boleh dibatasi
    min_price). order_type default "FAK" (fill-or-kill sebagian:
    terisi sebagian atau dibatalkan sisanya).
    """
    errors = validate_market_args(side, amount, shares, order_type)
    if errors:
        raise ValueError("argumen market order tidak valid: " +
                         "; ".join(errors))
    if not isinstance(token_id, str) or not token_id.strip() \
            or not token_id.strip().isdigit():
        raise ValueError("token_id harus string digit CLOB yang tidak "
                         "kosong")
    kwargs = {"token_id": token_id, "side": side,
              "order_type": order_type}
    if side == "BUY":
        kwargs["amount"] = amount
        if max_price is not None:
            kwargs["max_price"] = max_price
    else:
        kwargs["shares"] = shares
        if min_price is not None:
            kwargs["min_price"] = min_price
    return client.create_market_order(**kwargs)


def summarize_signed(signed):
    """Ringkasan SignedOrder yang AMAN dicetak/dilog.

    SENGAJA menghilangkan `signature` dan `salt`: keduanya adalah
    artefak kriptografis dari kunci dan tidak pernah perlu muncul di
    log. Alamat maker/signer adalah publik.
    """
    get = lambda name, default=None: getattr(signed, name, default)
    return {
        "side": get("side"),
        "token_id": get("token_id"),
        "order_type": get("order_type"),
        "maker": get("maker"),
        "signer": get("signer"),
        "maker_amount": get("maker_amount"),
        "taker_amount": get("taker_amount"),
        "expiration": get("expiration"),
        "post_only": get("post_only", False),
    }


def dry_run_limit_order(client, *, token_id, price, size, side,
                        post_only=False, expiration=None):
    """DRY-RUN: bangun + tanda tangani, JANGAN POST, kembalikan ringkasan.

    Ini mode verifikasi pertama di host: membuktikan build + sign
    bekerja dengan kunci asli TANPA menempatkan order apa pun. Fungsi
    ini TIDAK PERNAH memanggil post_order / place_* — dibuktikan tes
    (klien palsu yang post-nya melempar bila dipanggil).
    """
    signed = build_limit_order(client, token_id=token_id, price=price,
                               size=size, side=side, post_only=post_only,
                               expiration=expiration)
    summary = summarize_signed(signed)
    summary["posted"] = False
    summary["mode"] = "DRY-RUN"
    return summary


def dry_run_market_order(client, *, token_id, side, amount=None,
                         shares=None, max_price=None, min_price=None,
                         order_type="FAK"):
    """DRY-RUN market order: bangun + tanda tangani, JANGAN POST."""
    signed = build_market_order(client, token_id=token_id, side=side,
                                amount=amount, shares=shares,
                                max_price=max_price, min_price=min_price,
                                order_type=order_type)
    summary = summarize_signed(signed)
    summary["posted"] = False
    summary["mode"] = "DRY-RUN"
    return summary


# --- POST (hanya dipanggil loop di mode live) ------------------------------

def summarize_response(resp):
    """Ringkasan OrderResponse yang aman dicetak/dilog."""
    get = lambda name, default=None: getattr(resp, name, default)
    trades = get("trade_ids") or ()
    try:
        trade_count = len(trades)
    except TypeError:
        trade_count = 0
    ok = get("ok")
    if ok is None:
        ok = bool(get("success"))
    return {
        "order_id": get("order_id"),
        "status": get("status"),
        "ok": bool(ok),
        "making_amount": str(get("making_amount")),
        "taking_amount": str(get("taking_amount")),
        "trade_count": trade_count,
    }


def post_signed_order(client, signed):
    """Kirim SignedOrder yang sudah dibuat. Mengembalikan ringkasan."""
    resp = client.post_order(signed)
    return summarize_response(resp)


def place_limit_order_live(client, *, token_id, price, size, side,
                           post_only=False, expiration=None):
    """Create + sign + post limit order sekaligus (mode live saja)."""
    errors = validate_limit_args(token_id, price, size, side)
    if errors:
        raise ValueError("argumen limit order tidak valid: " +
                         "; ".join(errors))
    kwargs = {"token_id": token_id, "price": price, "size": size,
              "side": side, "post_only": bool(post_only)}
    if expiration is not None:
        kwargs["expiration"] = expiration
    return summarize_response(client.place_limit_order(**kwargs))


def place_market_order_live(client, *, token_id, side, amount=None,
                            shares=None, max_price=None, min_price=None,
                            order_type="FAK"):
    """Create + sign + post market order sekaligus (mode live saja)."""
    errors = validate_market_args(side, amount, shares, order_type)
    if errors:
        raise ValueError("argumen market order tidak valid: " +
                         "; ".join(errors))
    if not isinstance(token_id, str) or not token_id.strip() \
            or not token_id.strip().isdigit():
        raise ValueError("token_id harus string digit CLOB yang tidak "
                         "kosong")
    kwargs = {"token_id": token_id, "side": side, "order_type": order_type}
    if side == "BUY":
        kwargs["amount"] = amount
        if max_price is not None:
            kwargs["max_price"] = max_price
    else:
        kwargs["shares"] = shares
        if min_price is not None:
            kwargs["min_price"] = min_price
    return summarize_response(client.place_market_order(**kwargs))


def cancel_open_order(client, order_id):
    """Batalkan satu open order. Mengembalikan (ok_bool, catatan)."""
    if not order_id:
        return False, "order_id kosong — tidak ada yang dibatalkan"
    try:
        client.cancel_order(order_id=order_id)
        return True, f"cancel diminta untuk order {order_id}"
    except Exception as e:
        return False, f"cancel gagal ({type(e).__name__})"


# --- Verifikasi isi (pelajaran Indodax: jangan percaya respons mentah) -----

def position_size_for_token(client, token_id):
    """Ukuran posisi berjalan untuk satu token, best-effort.

    Membaca list_positions() (Data API, wallet terautentikasi) halaman
    pertama dan mencocokkan asset_id. Mengembalikan (size, read_ok):
    - read_ok True + size float = ukuran posisi terbaca (0.0 bila
      tidak ada baris posisi = tidak ada posisi terbuka).
    - read_ok True + size None = tidak ada baris posisi (diperlakukan
      sebagai 0.0 oleh pemanggil untuk jual, sebagai "tidak terisi"
      untuk beli).
    - read_ok False = baca gagal / bentuk tak dikenal -> TIDAK ADA
      bukti (pemanggil TIDAK BOLEH menyimpulkan nol).
    (Catatan: posisi Data API berjangkar pada proxy wallet; bila
    kueri wallet signer mengembalikan kosong padahal posisi ada,
    fungsi ini mengembalikan (None, True) dan verifikasi jatuh ke
    bukti respons + open orders — didokumentasikan di README.)
    """
    try:
        page = client.list_positions().first_page()
        items = page.items
    except Exception:
        try:
            items = []
            for page in client.list_positions():
                items.extend(page.items)
        except Exception:
            return None, False
    try:
        for p in items:
            asset = getattr(p, "asset_id", None)
            if asset is None:
                asset = getattr(p, "token_id", None)
            if str(asset) == str(token_id):
                size = getattr(p, "current_size", None)
                return (float(size) if size is not None else None), True
    except Exception:
        return None, False
    return None, True


def adopt_posted_order(client, token_id, side, price, size):
    """Cari order di book yang cocok dengan order yang baru dipost.

    Dipakai saat respons POST error (pelajaran Indodax: error belum
    tentu tidak terpasang). Cocok bila: sisi sama, harga dalam
    toleransi 0,002, dan ukuran sama (toleransi float 1e-9).
    Mengembalikan order_id atau None (tidak ditemukan = tidak ada
    bukti terpasang).
    """
    orders = list_open_orders_for_token(client, token_id)
    if not orders:
        return None
    for o in orders:
        if o.get("side") != side:
            continue
        try:
            o_price = float(o.get("price"))
            o_size = float(o.get("original_size"))
        except (TypeError, ValueError):
            continue
        if abs(o_price - float(price)) <= 0.002 and \
                abs(o_size - float(size)) <= 1e-9:
            return o.get("order_id")
    return None


def list_open_orders_for_token(client, token_id):
    """Open order untuk satu token. Mengembalikan list dict ringkas.

    Mengembalikan [] bila tidak ada / bila baca gagal (kegagalan baca
    dilaporkan lewat reason terpisah oleh pemanggil, bukan disamarkan
    sebagai "tidak ada order").
    """
    try:
        page = client.list_open_orders(token_id=token_id).first_page()
        items = page.items
    except Exception:
        try:
            items = []
            for page in client.list_open_orders(token_id=token_id):
                items.extend(page.items)
        except Exception:
            return None  # baca gagal — BUKAN bukti "tidak ada order"
    out = []
    for o in items:
        get = lambda name, default=None: getattr(o, name, default)
        out.append({
            "order_id": get("id"),
            "side": get("side"),
            "price": float(get("price")) if get("price") is not None
            else None,
            "original_size": str(get("original_size")),
            "size_matched": str(get("size_matched")),
            "status": get("status"),
        })
    return out


def verify_post(client, *, token_id, order_id, response_summary,
                expect="filled"):
    """Verifikasi posting order lewat open orders (bukan respons mentah).

    expect="filled" (market order): terverifikasi bila respons
    menunjukkan match (status matched / trade_count > 0) DAN order
    sudah tidak ada di open orders.
    expect="resting-or-filled" (limit order): terverifikasi bila
    respons ok DAN (order masih terbuka dengan sisi yang sama ATAU
    order sudah tidak terbuka tapi ada trade — terisi).
    Mengembalikan dict bukti: {verified, reason, open_orders}.
    Bila baca open orders GAGAL -> verified=False, reason menjelaskan
    (jangan pernah menyimpulkan "terisi" dari kegagalan baca).
    """
    open_orders = list_open_orders_for_token(client, token_id)
    if open_orders is None:
        return {"verified": False,
                "reason": "baca open orders gagal — isi belum "
                          "terverifikasi, jangan simpulkan terisi",
                "open_orders": None}
    still_open = [o for o in open_orders if o["order_id"] == order_id]
    resp_ok = bool(response_summary.get("ok"))
    status = response_summary.get("status")
    trades = response_summary.get("trade_count", 0)
    if expect == "filled":
        if not resp_ok:
            return {"verified": False,
                    "reason": "respons posting tidak ok — order "
                              "dianggap belum terisi",
                    "open_orders": open_orders}
        if still_open:
            return {"verified": False,
                    "reason": "order masih terbuka padahal market order "
                              "seharusnya langsung terisi — tunggu "
                              "verifikasi ulang",
                    "open_orders": open_orders}
        if status == "matched" or trades > 0:
            return {"verified": True,
                    "reason": "market order terverifikasi terisi "
                              "(respons matched/trade + order tidak "
                              "terbuka)",
                    "open_orders": open_orders}
        return {"verified": False,
                "reason": "order tidak terbuka tapi tidak ada bukti "
                          "trade — isi belum terverifikasi",
                "open_orders": open_orders}
    # resting-or-filled (limit)
    if not resp_ok:
        return {"verified": False,
                "reason": "respons posting tidak ok — order dianggap "
                          "belum terpasang",
                "open_orders": open_orders}
    if still_open:
        return {"verified": True,
                "reason": "limit order terverifikasi terpasang "
                          "(masih terbuka di book)",
                "open_orders": open_orders}
    if status == "matched" or trades > 0:
        return {"verified": True,
                "reason": "limit order terverifikasi terisi (respons "
                          "matched/trade + order tidak terbuka)",
                "open_orders": open_orders}
    return {"verified": False,
            "reason": "order tidak terbuka tanpa bukti trade — isi "
                      "belum terverifikasi",
            "open_orders": open_orders}
