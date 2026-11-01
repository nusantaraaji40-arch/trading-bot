"""Sinyal GRATIS untuk gerbang beli live — RSS berita + Open-Meteo.

PERAN: Bro 4 SOCIAL (sentimen/berita). Modul ini BUKAN model LLM dan
tidak memakai key API apa pun. Semua sumber gratis, tanpa kunci:
- RSS berita: Google News RSS (pencarian per kata kunci), CoinDesk
  RSS, Cointelegraph RSS (kripto); BBC Sport Football RSS (bola).
- Prakiraan cuaca: Open-Meteo Geocoding + Forecast API (tanpa key).

ATURAN GERBANG (wajib, bukan skor tambahan):
- Up/Down + bola: TANPA berita relevan yang jelas -> JANGAN BELI.
  Berita di sini = KATALIS (ada kabar relevan), BUKAN prediksi arah:
  kata kunci membuktikan ada kabar tentang aset/tim itu, bukan
  bahwa harga akan naik/turun. Sisi yang dibeli tetap aturan value
  (sisi yang muat anggaran), bukan "diprediksi menang".
- Cuaca: prakiraan resmi mendukung sisi YES (selisih <= 2 C dari
  target) -> boleh beli YES; selain itu -> SKIP. Tidak ada pembelian
  sisi NO untuk cuaca di loop ini (hampir tidak pernah muat anggaran
  $1,00 dengan min 5 lembar di harga ~0,99).
- RSS gagal diakses SEMUA -> sinyal tidak tersedia -> SKIP.
  Bentuk RSS tak dikenal -> feed itu dianggap gagal, bukan crash.
- Bukti dicatat di log keputusan: judul + sumber berita yang cocok,
  atau kota + target + prakiraan untuk cuaca.

BATASAN JUJUR (baca sebelum percaya sinyal ini):
- Kata kunci bukan kepastian: judul yang mengandung "Bitcoin" bisa
  berupa kabar netral/negatif; modul ini TIDAK menilai sentimen arah.
- RSS gratis bisa lambat, dibatasi, atau mengubah format sewaktu-
  waktu; bila itu terjadi, loop SKIP (aman), bukan menebak.
- Prakiraan Open-Meteo adalah model cuaca, bukan hasil resmi;
  gerbang +-2 C hanyalah filter kewajaran, bukan ramalan akurat.
"""

import json
import re
import urllib.error
import urllib.request
import xml.etree.ElementTree as ET
from dataclasses import dataclass, field

USER_AGENT = "polymarket-live-loop/1.0 (free-signal-gate)"
TIMEOUT = 20

# --- Sumber RSS gratis (tanpa key) ----------------------------------------
# Google News RSS adalah endpoint publik (search?q=...&hl=en-US&
# gl=US&ceid=US:en). CoinDesk / Cointelegraph / BBC Sport adalah feed
# RSS publik masing-masing penerbit.
CRYPTO_FEEDS = [
    ("GoogleNews", "https://news.google.com/rss/search?q={q}"
                   "&hl=en-US&gl=US&ceid=US:en"),
    ("CoinDesk", "https://www.coindesk.com/arc/outboundfeeds/rss/"),
    ("Cointelegraph", "https://cointelegraph.com/rss"),
]
SOCCER_FEEDS = [
    ("GoogleNews", "https://news.google.com/rss/search?q={q}"
                   "&hl=en-US&gl=US&ceid=US:en"),
    ("BBCSportFootball", "http://feeds.bbci.co.uk/sport/football/rss.xml"),
]

GEOCODE_URL = ("https://geocoding-api.open-meteo.com/v1/search"
               "?name={name}&count=1&language=en&format=json")
FORECAST_URL = ("https://api.open-meteo.com/v1/forecast"
                "?latitude={lat}&longitude={lon}"
                "&daily=temperature_2m_max&timezone=auto"
                "&start_date={date}&end_date={date}")

WEATHER_TOLERANCE_C = 2.0

# Aset kripto yang dikenali dari pertanyaan Up/Down -> kata kunci.
ASSET_KEYWORDS = [
    ("bitcoin", ["bitcoin", "btc"]),
    ("ethereum", ["ethereum", "eth"]),
    ("solana", ["solana", "sol"]),
    ("xrp", ["xrp", "ripple"]),
    ("dogecoin", ["dogecoin", "doge"]),
    ("cardano", ["cardano", "ada"]),
]


@dataclass
class SignalResult:
    """Hasil gerbang sinyal. ok=True = gerbang lolos (boleh lanjut)."""
    ok: bool
    side: str | None = None  # "YES"/"NO" untuk cuaca; None = gerbang
    # katalis saja (Up/Down + bola: berita membuktikan katalis, bukan
    # arah — sisi beli ditentukan aturan value/budget, bukan sinyal).
    evidence: list = field(default_factory=list)
    reason: str = ""


def fetch_url(url, timeout=TIMEOUT):
    """GET publik. Mengembalikan teks; gagal -> exception (pemanggil
    yang memutuskan: gagal = sinyal tidak tersedia, bukan crash)."""
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return resp.read().decode("utf-8", "replace")


# --- RSS -------------------------------------------------------------------

def parse_rss_items(xml_text):
    """Parse RSS 2.0 (channel/item) atau Atom (feed/entry).

    Mengembalikan list {title, link, description}. Bentuk tak dikenal
    atau XML rusak -> [] (feed dianggap gagal, bukan crash).
    """
    try:
        root = ET.fromstring(xml_text)
    except Exception:
        return []
    items = []
    try:
        for el in root.iter():
            tag = el.tag.rsplit("}", 1)[-1]
            if tag not in ("item", "entry"):
                continue
            title = ""
            link = ""
            desc = ""
            for child in el:
                ctag = child.tag.rsplit("}", 1)[-1]
                text = (child.text or "").strip()
                if ctag == "title" and not title:
                    title = text
                elif ctag == "link":
                    if text and not link:
                        link = text
                    elif not link:
                        link = child.get("href", "")
                elif ctag in ("description", "summary") and not desc:
                    desc = text
            if title:
                items.append({"title": title, "link": link,
                              "description": desc})
    except Exception:
        return []
    return items


def _match_items(items, keywords):
    """Item yang judul/deskripsinya mengandung SALAH SATU kata kunci
    (case-insensitive). Mengembalikan list item yang cocok."""
    kws = [k.lower() for k in keywords if k]
    if not kws:
        return []
    matched = []
    for it in items:
        hay = (it.get("title", "") + " " +
               it.get("description", "")).lower()
        if any(k in hay for k in kws):
            matched.append(it)
    return matched


def news_gate(keywords, *, fetcher=fetch_url, feeds=None,
              max_evidence=3):
    """Gerbang berita: ada kabar relevan yang jelas?

    feeds: list (nama, url_template) dengan {q} = kata kunci pertama
    (untuk Google News). Bila feeds None, pemanggil wajib memberi
    daftar feed kategori (lihat news_gate_for_category).
    """
    if not keywords:
        return SignalResult(
            ok=False, side=None, evidence=[],
            reason="kata kunci tidak bisa diturunkan dari pertanyaan "
                   "pasar — sinyal tidak tersedia, SKIP")
    if not feeds:
        return SignalResult(
            ok=False, side=None, evidence=[],
            reason="daftar feed berita kosong — sinyal tidak tersedia, "
                   "SKIP")
    q = keywords[0]
    tried, ok_feeds, evidence = [], [], []
    for name, template in feeds:
        url = template.format(q=q) if "{q}" in template else template
        tried.append(name)
        try:
            items = parse_rss_items(fetcher(url))
        except Exception as e:
            continue
        if not items:
            continue
        ok_feeds.append(name)
        for it in _match_items(items, keywords)[:max_evidence]:
            evidence.append(f"{name}: {it['title'][:120]}")
        if evidence:
            break  # satu sumber yang membuktikan katalis sudah cukup
    if not ok_feeds:
        return SignalResult(
            ok=False, side=None, evidence=[],
            reason=f"sinyal tidak tersedia — semua RSS gagal "
                   f"({', '.join(tried)}), SKIP")
    if not evidence:
        return SignalResult(
            ok=False, side=None, evidence=[],
            reason=f"tidak ada berita relevan untuk kata kunci "
                   f"{keywords} di feed yang berhasil dibaca "
                   f"({', '.join(ok_feeds)}), SKIP")
    return SignalResult(ok=True, side=None, evidence=evidence,
                        reason=f"katalis berita ditemukan "
                               f"({len(evidence)} bukti)")


def news_gate_for_category(category, keywords, *, fetcher=fetch_url):
    """Gerbang berita per kategori (feed multi-sumber, gratis)."""
    feeds = CRYPTO_FEEDS if category == "updown" else SOCCER_FEEDS
    return news_gate(keywords, fetcher=fetcher, feeds=feeds)


# --- Kata kunci dari pertanyaan pasar --------------------------------------

def keywords_for_market(category, question):
    """Turunkan kata kunci dari pertanyaan pasar (murni, tanpa I/O).

    Up/Down: peta aset yang dikenal. Bola: nama tim dari pola
    "Will <TIM> win ...". Tidak ditemukan -> [] (gerbang gagal aman).
    """
    q = (question or "")
    ql = q.lower()
    if category == "updown":
        for asset, kws in ASSET_KEYWORDS:
            if asset in ql:
                return kws
        return []
    if category == "soccer":
        m = re.search(r"will\s+(.+?)\s+win\b", ql)
        if not m:
            return []
        team = m.group(1).strip()
        # "real madrid cf" -> ["real madrid cf", "real madrid", "madrid"]
        parts = team.split()
        kws = [team]
        if len(parts) >= 2:
            kws.append(" ".join(parts[:2]))
        if parts:
            kws.append(parts[-1])
        # Buang kata generik yang terlalu luas ("cf", "fc").
        kws = [k for k in dict.fromkeys(kws)
               if k not in ("cf", "fc", "club")]
        return kws
    return []


# --- Cuaca (Open-Meteo, tanpa key) ------------------------------------------

def parse_weather_question(question):
    """Parse pertanyaan cuaca -> (kota, target_C, tanggal_str) atau None.

    Format yang didukung (format Polymarket): "Will the highest
    temperature in <KOTA> be <X>°C on <BULAN> <TANGGAL>?" Tanggal
    tanpa tahun: pemanggil melengkapi tahun dari endDate pasar.
    """
    if not question:
        return None
    m = re.search(
        r"highest temperature in\s+(.+?)\s+be\s+(-?\d+(?:\.\d+)?)\s*°?C",
        question, re.IGNORECASE)
    if not m:
        return None
    city = m.group(1).strip()
    try:
        target = float(m.group(2))
    except ValueError:
        return None
    m2 = re.search(
        r"\bon\s+(January|February|March|April|May|June|July|August|"
        r"September|October|November|December)\s+(\d{1,2})\b",
        question)
    date_text = f"{m2.group(1)} {m2.group(2)}" if m2 else None
    return city, target, date_text


_MONTHS = {"January": 1, "February": 2, "March": 3, "April": 4,
           "May": 5, "June": 6, "July": 7, "August": 8, "September": 9,
           "October": 10, "November": 11, "December": 12}


def _date_iso(date_text, year):
    """'November 1' + tahun -> 'YYYY-11-01'. Gagal -> None."""
    if not date_text or not year:
        return None
    try:
        month_name, day = date_text.split()
        return f"{year:04d}-{_MONTHS[month_name]:02d}-{int(day):02d}"
    except Exception:
        return None


def weather_gate(question, end_date_iso=None, *, fetcher=fetch_url,
                 tolerance=WEATHER_TOLERANCE_C):
    """Gerbang prakiraan cuaca: dukung sisi YES bila prakiraan maks
    dalam +-tolerance dari target. Selain itu SKIP (bukan beli NO).

    end_date_iso (YYYY-MM-DD dari pasar) dipakai sebagai tahun +
    tanggal acuan bila pertanyaan tidak menyebut tahun.
    """
    parsed = parse_weather_question(question)
    if not parsed:
        return SignalResult(
            ok=False, side=None, evidence=[],
            reason="pertanyaan cuaca tidak bisa diparse (kota/target/"
                   "tanggal) — sinyal tidak tersedia, SKIP")
    city, target, date_text = parsed
    year = None
    date_iso = None
    if end_date_iso:
        try:
            year = int(end_date_iso[:4])
            date_iso = end_date_iso[:10]
        except Exception:
            year, date_iso = None, None
    if date_iso is None and date_text and year is None:
        # Tanpa endDate pasar, tahun tidak bisa dipastikan -> SKIP aman.
        return SignalResult(
            ok=False, side=None, evidence=[],
            reason="tanggal prakiraan tidak bisa dipastikan tanpa "
                   "endDate pasar — sinyal tidak tersedia, SKIP")
    if date_iso is None:
        date_iso = _date_iso(date_text, year)
    if not date_iso:
        return SignalResult(
            ok=False, side=None, evidence=[],
            reason="tanggal prakiraan tidak bisa diparse — sinyal "
                   "tidak tersedia, SKIP")
    try:
        geo = json.loads(fetcher(GEOCODE_URL.format(name=city)))
        results = geo.get("results") or []
        if not results:
            return SignalResult(
                ok=False, side=None, evidence=[],
                reason=f"kota '{city}' tidak ditemukan di geocoding "
                       "Open-Meteo — sinyal tidak tersedia, SKIP")
        lat, lon = results[0]["latitude"], results[0]["longitude"]
        fc = json.loads(fetcher(FORECAST_URL.format(
            lat=lat, lon=lon, date=date_iso)))
        daily = fc.get("daily") or {}
        temps = daily.get("temperature_2m_max") or []
        if not temps:
            return SignalResult(
                ok=False, side=None, evidence=[],
                reason="prakiraan Open-Meteo tidak mengembalikan suhu "
                       "maks — sinyal tidak tersedia, SKIP")
        forecast = float(temps[0])
    except Exception as e:
        return SignalResult(
            ok=False, side=None, evidence=[],
            reason=f"akses Open-Meteo gagal ({type(e).__name__}) — "
                   "sinyal tidak tersedia, SKIP")
    diff = abs(forecast - target)
    evidence = [f"Open-Meteo: kota {city}, target {target} C, "
                f"prakiraan maks {forecast} C pada {date_iso} "
                f"(selisih {diff:.1f} C)"]
    if diff <= tolerance:
        return SignalResult(ok=True, side="YES", evidence=evidence,
                            reason=f"prakiraan mendukung YES "
                                   f"(selisih {diff:.1f} C <= "
                                   f"{tolerance} C)")
    return SignalResult(
        ok=False, side=None, evidence=evidence,
        reason=f"prakiraan tidak mendukung YES (selisih {diff:.1f} C > "
               f"{tolerance} C) — SKIP")
