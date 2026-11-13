// office override 14 Nov 2026: live P/L, chatbot, debate, search, bots
/* Patch kantor 2026-11-14: P/L belum terealisasi, total harga sekarang, dst.
   Override fungsi render (definisi terakhir yang berlaku). */
(function () {
"use strict";
/* status.json mentah untuk analitik / debat / chatbot */
window.__liveRaw = window.__liveRaw || null;
if (typeof applyLive === "function" && !applyLive.__p14) {
    var _applyLive0 = applyLive;
    applyLive = function (d) { window.__liveRaw = d; return _applyLive0(d); };
    applyLive.__p14 = true;
}
function _anaTotals() {
    var sum = 0, sumPL = 0, sumUN = 0, plKnown = false, unKnown = false, n = 0;
    VENUE_ORDER.forEach(function (k) {
        var v = VENUES[k];
        if (!v) return;
        if (v.totalNum != null && !isNaN(v.totalNum)) { sum += v.totalNum; n++; }
        if (v.plNum != null && !isNaN(v.plNum)) { sumPL += v.plNum; plKnown = true; }
        if (v.unrealizedNum != null && !isNaN(v.unrealizedNum)) { sumUN += v.unrealizedNum; unKnown = true; }
    });
    return { sum: sum, pl: sumPL, realized: sumPL, plKnown: plKnown, unrealized: sumUN, unrealizedKnown: unKnown, count: n };
}
if (typeof anaTotals === "function") { anaTotals = _anaTotals; }
function _plFeed() {
    var t = _anaTotals();
    var rows = [];
    VENUE_ORDER.forEach(function (k) {
        var v = VENUES[k];
        if (!v) return;
        var hasR = (v.plNum != null && !isNaN(v.plNum));
        var hasU = (v.unrealizedNum != null && !isNaN(v.unrealizedNum));
        if (hasR || hasU) rows.push({ key: k, name: v.display, val: hasR ? v.plNum : 0, unreal: hasU ? v.unrealizedNum : null, hasReal: hasR });
    });
    rows.sort(function (a, b) { return Math.abs(b.val + (b.unreal || 0)) - Math.abs(a.val + (a.unreal || 0)); });
    return { total: t, rows: rows };
}
if (typeof plFeedItems === "function") { plFeedItems = _plFeed; }
function _plEmo(v) { return (v == null || v === 0) ? "" : (v > 0 ? "\uD83E\uDD11 " : "\uD83D\uDE2D "); }
function _renderPlTicker() {
    var list = $("#plTickList"), foot = $("#plTickFoot"), dot = $("#plTickDot");
    if (!list) return;
    var f = _plFeed();
    var html = "";
    if (f.total.plKnown) {
        html += '<button type="button" class="pl-tick-row is-total ' + plCls(f.total.pl) + '" data-pl-open="ana" title="Total P/L terealisasi ' + esc(fmtSigned(f.total.pl)) + ' — klik untuk buka Analitik"><span class="pl-tick-amt">' + _plEmo(f.total.pl) + esc(fmtCompactRp(f.total.pl)) + '</span><span class="pl-tick-name">TOTAL · Terealisasi</span></button>';
    }
    if (f.total.unrealizedKnown) {
        html += '<button type="button" class="pl-tick-row is-total ' + plCls(f.total.unrealized) + '" data-pl-open="ana" title="Total P/L belum terealisasi ' + esc(fmtSigned(f.total.unrealized)) + ' — klik untuk buka Analitik"><span class="pl-tick-amt">' + _plEmo(f.total.unrealized) + esc(fmtCompactRp(f.total.unrealized)) + '</span><span class="pl-tick-name">TOTAL · Belum terealisasi</span></button>';
    }
    html += f.rows.map(function (r) {
        var out = "";
        var rAmt = r.hasReal ? _plEmo(r.val) + esc(fmtCompactRp(r.val)) : "—";
        var rTitle = r.hasReal ? ("P/L terealisasi " + fmtSigned(r.val)) : "Terealisasi tidak tercatat di state";
        out += '<button type="button" class="pl-tick-row ' + plCls(r.hasReal ? r.val : 0) + '" data-pl-venue="' + r.key + '" title="' + esc(r.name) + ' · ' + esc(rTitle) + ' — klik untuk detail venue"><span class="pl-tick-amt">' + rAmt + '</span><span class="pl-tick-name">' + esc(r.name) + ' · Terealisasi</span></button>';
        var uAmt = (r.unreal != null) ? _plEmo(r.unreal) + esc(fmtCompactRp(r.unreal)) : "—";
        var uTitle = (r.unreal != null) ? ("P/L belum terealisasi " + fmtSigned(r.unreal)) : "Belum terealisasi belum tercatat (harga tidak tersedia)";
        out += '<button type="button" class="pl-tick-row ' + plCls(r.unreal || 0) + '" data-pl-venue="' + r.key + '" title="' + esc(r.name) + ' · ' + esc(uTitle) + ' — klik untuk detail venue"><span class="pl-tick-amt">' + uAmt + '</span><span class="pl-tick-name">' + esc(r.name) + ' · Belum terealisasi</span></button>';
        return out;
    }).join("");
    if (!html) html = '<div class="pl-tick-empty">P/L belum terbaca</div>';
    list.innerHTML = html;
    list.querySelectorAll("[data-pl-venue]").forEach(function (b) {
        b.addEventListener("click", function () { selectVenue(b.getAttribute("data-pl-venue")); });
    });
    list.querySelectorAll("[data-pl-open]").forEach(function (b) {
        b.addEventListener("click", function () { var ab = $("#anaBtn"); if (ab) ab.click(); });
    });
    if (dot) dot.className = "pl-tick-dot " + (!f.total.plKnown ? "is-unk" : plCls(f.total.pl));
    if (foot) { var _fr = live.ok; if (!_fr) { var _g2 = live.generatedAt || (window.__liveRaw && (window.__liveRaw.generatedAt || window.__liveRaw.generated_at)); if (_g2) { var _a2 = (Date.now() - new Date(_g2).getTime()) / 60000; if (_a2 >= 0 && _a2 < 10) _fr = true; } } if (!_fr && window.__liveRaw && window.__liveRaw.generated_at) { var _age = (Date.now() - new Date(window.__liveRaw.generated_at).getTime()) / 60000; _fr = _age >= 0 && _age < 10; } foot.textContent = (_fr ? "Live · " + fmtWIBShort(live.generatedAt || (window.__liveRaw && window.__liveRaw.generated_at)) : "Snapshot · live gagal") + " · Terealisasi tidak termasuk Indodax (tidak tercatat di state) · klik angka untuk detail"; }
}
if (typeof renderPlTicker === "function") { renderPlTicker = _renderPlTicker; }
function _anaFeed() {
    var f = _plFeed();
    var tot = "";
    if (f.total.plKnown) tot += '<div class="ana-feed-row is-total ' + plCls(f.total.pl) + '"><span class="ana-feed-amt">' + _plEmo(f.total.pl) + esc(fmtCompactRp(f.total.pl)) + '</span><span class="ana-feed-name">TOTAL · Terealisasi ' + esc(fmtSigned(f.total.pl)) + '</span></div>';
    if (f.total.unrealizedKnown) tot += '<div class="ana-feed-row is-total ' + plCls(f.total.unrealized) + '"><span class="ana-feed-amt">' + _plEmo(f.total.unrealized) + esc(fmtCompactRp(f.total.unrealized)) + '</span><span class="ana-feed-name">TOTAL · Belum terealisasi ' + esc(fmtSigned(f.total.unrealized)) + '</span></div>';
    var rows = f.rows.map(function (r) {
        var out = "";
        var rAmt = r.hasReal ? _plEmo(r.val) + esc(fmtCompactRp(r.val)) : "—";
        var rTxt = r.hasReal ? esc(fmtSigned(r.val)) : "tidak tercatat di state";
        out += '<div class="ana-feed-row ' + plCls(r.hasReal ? r.val : 0) + '"><span class="ana-feed-amt">' + rAmt + '</span><span class="ana-feed-name">' + esc(r.name) + ' · Terealisasi ' + rTxt + '</span></div>';
        var uAmt = (r.unreal != null) ? _plEmo(r.unreal) + esc(fmtCompactRp(r.unreal)) : "—";
        var uTxt = (r.unreal != null) ? esc(fmtSigned(r.unreal)) : "belum tercatat";
        out += '<div class="ana-feed-row ' + plCls(r.unreal || 0) + '"><span class="ana-feed-amt">' + uAmt + '</span><span class="ana-feed-name">' + esc(r.name) + ' · Belum terealisasi ' + uTxt + '</span></div>';
        return out;
    }).join("");
    return '<div class="ana-feed">' + tot + rows + '</div>';
}
if (typeof anaFeed === "function") { anaFeed = _anaFeed; }
function _anaBarRow(name, val, max, valTxt, emo) {
    var pct = max > 0 ? Math.min(100, Math.abs(val) / max * 100) : 0;
    return '<div class="ana-bar-row"><span class="ana-bar-name">' + esc(name) + '</span><div class="ana-bar" style="height:8px;background:rgba(255,255,255,.08);border-radius:4px;overflow:hidden"><div class="ana-bar-fill ' + (val < 0 ? "neg" : "pos") + '" style="width:' + pct.toFixed(1) + '%;height:100%"></div></div><span class="ana-bar-val">' + (emo ? _plEmo(val) : "") + esc(valTxt) + '</span></div>';
}
function _anaBars(kind) {
    var feed = _plFeed();
    var rows = feed.rows;
    if (!rows.length) return '<div class="ana-empty">P/L per venue belum terbaca.</div>';
    var max = 0;
    rows.forEach(function (r) {
        var vals = (kind === "pl") ? [r.val, (r.unreal != null ? r.unreal : 0)] : [(VENUES[r.key].totalNum || 0)];
        vals.forEach(function (x) { max = Math.max(max, Math.abs(x)); });
    });
    if (kind === "pl") {
        return rows.map(function (r) {
            var out = _anaBarRow(r.name + " · Terealisasi", r.hasReal ? r.val : 0, max, r.hasReal ? fmtSigned(r.val) : "—", true);
            out += (r.unreal != null) ? _anaBarRow(r.name + " · Belum terealisasi", r.unreal, max, fmtSigned(r.unreal), true) : '<div class="ana-bar-row"><span class="ana-bar-name">' + esc(r.name) + ' · Belum terealisasi</span><div class="ana-bar"></div><span class="ana-bar-val">—</span></div>';
            return out;
        }).join("");
    }
    return rows.map(function (r) {
        var v = VENUES[r.key];
        return _anaBarRow(r.name, v.totalNum || 0, max, fmtRp(v.totalNum || 0));
    }).join("");
}
if (typeof anaBars === "function") { anaBars = _anaBars; }
function _modalTotal() {
    var raw = window.__liveRaw, tot = 0, ok = false;
    if (raw && raw.venues) {
        Object.keys(raw.venues).forEach(function (k) {
            var r = raw.venues[k];
            var dep = (r && r.total_deposited_idr != null) ? r.total_deposited_idr : ((r && r.deposit_baseline_idr != null) ? r.deposit_baseline_idr : null);
            if (dep != null && !isNaN(dep)) { tot += dep; ok = true; }
        });
    }
    return ok ? tot : null;
}
function _overviewPost(h) {
    var t = _anaTotals();
    var cnt = (live.ok && live.totals && live.totals.count) ? live.totals.count : t.count;
    h = h.replace("total state 5 venue · live", "total state " + cnt + " venue · live");
    h = h.replace("total 5 venue", "total " + (t.count || 5) + " venue");
    var modal = _modalTotal();
    var sum = (live.ok && live.totals) ? live.totals.sum : t.sum;
    var col = (modal != null && sum != null && sum >= modal) ? "#2ea36b" : "#e0524d";
    var prev = window.__ovPrevSum;
    var deltaHtml = "";
    if (modal != null && sum != null) {
        if (prev != null && prev !== sum) {
            var d = sum - prev;
            deltaHtml = '<div class="side-line" style="margin-top:2px">Perubahan sejak update terakhir: <b style="color:' + (d > 0 ? "#2ea36b" : "#e0524d") + '">' + (d > 0 ? "▲ naik " : "▼ turun ") + _plEmo(d) + esc(fmtSigned(d)) + '</b> · ' + (sum >= modal ? "di atas modal (untung)" : "di bawah modal (rugi)") + '</div>';
        } else {
            deltaHtml = '<div class="side-line" style="margin-top:2px">Modal tercatat <b>' + esc(fmtRp(modal)) + '</b> · ' + (sum >= modal ? "di atas modal (untung)" : "di bawah modal (rugi)") + '</div>';
        }
    }
    window.__ovPrevSum = sum;
    h = h.replace(/<div class="side-big"><b>/, '<div class="side-big"><b style="color:' + col + '">' + (modal != null && sum != null ? _plEmo(sum - modal) : ""));
    h = h.replace(/(<div class="side-cap">[^<]*<\/div><\/div>)/, "$1" + deltaHtml);
    if (t.unrealizedKnown) {
        h = h.replace("· (Indodax belum termasuk)", '· belum terealisasi <b style="color:' + (t.unrealized < 0 ? "#e0524d" : "#2ea36b") + '">' + _plEmo(t.unrealized) + esc(fmtSigned(t.unrealized)) + '</b> · (Indodax belum termasuk di terealisasi)');
    }
    VENUE_ORDER.forEach(function (k) {
        var v = VENUES[k];
        if (!v || v.unrealizedNum == null) return;
        var pat = new RegExp('(data-venue="' + k + '"[^]*?style="color:[^"]*">[^<]*)(</span>)');
        h = h.replace(pat, "$1 · blm terealisasi " + _plEmo(v.unrealizedNum) + fmtSigned(v.unrealizedNum) + "$2");
    });
    var pl = VENUES.PLUANG;
    if (pl && pl.totalNum != null) {
        var pct = Math.max(0, Math.min(100, Math.round(pl.totalNum / 1500000 * 100)));
        h = h.replace(/<div class="progress" style="margin-top:9px"><i style="width:[^"]*"><\/i><\/div>/, '<div class="progress" style="margin-top:9px"><i style="width:' + pct + '%"></i></div>');
    }
    return h;
}
if (typeof overview === "function" && !overview.__p14) {
    var _overview0 = overview;
    overview = function () { var h = _overview0(); try { h = _overviewPost(h); } catch (e) {} return h; };
    overview.__p14 = true;
}
var _PERSONAS = [
    { id: "maus", name: "MausBot", color: "#14b8a6", angle: "data/harga", svg: '<svg viewBox="0 0 32 32" width="28" height="28"><circle cx="11" cy="9" r="5" fill="#14b8a6"/><circle cx="21" cy="9" r="5" fill="#14b8a6"/><circle cx="16" cy="18" r="10" fill="#0d9488"/><circle cx="13" cy="17" r="1.6" fill="#fff"/><circle cx="19" cy="17" r="1.6" fill="#fff"/></svg>' },
    { id: "dots", name: "Dots", color: "#a855f7", angle: "berita/sentimen", svg: '<svg viewBox="0 0 32 32" width="28" height="28"><circle cx="8" cy="16" r="5" fill="#a855f7"/><circle cx="16" cy="16" r="5" fill="#c084fc"/><circle cx="24" cy="16" r="5" fill="#7e22ce"/></svg>' },
    { id: "grok", name: "GrokBot", color: "#f59e0b", angle: "risiko", svg: '<svg viewBox="0 0 32 32" width="28" height="28"><rect x="6" y="6" width="20" height="20" rx="5" fill="#f59e0b"/><path d="M11 11l10 10M21 11L11 21" stroke="#451a03" stroke-width="2.6" stroke-linecap="round"/></svg>' },
    { id: "hermes", name: "Hermes", color: "#38bdf8", angle: "momentum", svg: '<svg viewBox="0 0 32 32" width="28" height="28"><path d="M16 4l9 6v9l-9 9-9-9v-9z" fill="#38bdf8"/><path d="M8 10l14-4M8 22l14 4" stroke="#075985" stroke-width="2" stroke-linecap="round"/></svg>' }
];
function _worstPos() {
    var raw = window.__liveRaw, worst = null;
    if (raw && raw.venues) {
        Object.keys(raw.venues).forEach(function (k) {
            (raw.venues[k].positions || []).forEach(function (p) {
                if (p.unrealized_pct != null && (!worst || p.unrealized_pct < worst.pct)) worst = { sym: String(p.symbol || p.pair_id || "?").toUpperCase(), venue: k, pct: p.unrealized_pct, idr: (p.unrealized_idr || 0) };
            });
        });
    }
    return worst;
}
function _discuss(topic) {
    var t = _anaTotals();
    var w = _worstPos();
    var news = (window.__liveRaw && window.__liveRaw.news) || [];
    var newsLine = "Tidak ada berita khusus di ticker hari ini.";
    if (w) {
        var hit = null;
        news.forEach(function (n) { if (!hit && (n.title || "").toLowerCase().indexOf(w.sym.toLowerCase().slice(0, 4)) >= 0) hit = n; });
        if (hit) newsLine = "Ticker: \u201c" + hit.title + "\u201d (" + hit.source + ").";
    }
    var worstTxt = w ? (w.sym + " " + fmtSigned(w.idr) + " (" + w.pct.toFixed(1) + "%)") : "tidak ada posisi terbuka yang rugi";
    var ops = {
        maus: "Data: total belum terealisasi " + fmtSigned(t.unrealized || 0) + "; rugi terbesar " + worstTxt + ".",
        dots: "Berita: " + newsLine,
        grok: "Risiko: " + ((w && w.sym === "FLOAT") ? "FLOAT di bawah min order MEXC $1 \u2014 tidak bisa dijual sampai harga \u2265 $0,008227; biarkan dulu." : (w ? w.sym + " masih " + Math.abs(w.pct).toFixed(0) + "% di bawah entry; jaga SL/KS, jangan tambah posisi." : "Tidak ada posisi berisiko saat ini.")),
        hermes: "Momentum: " + (w ? w.sym + " " + Math.abs(w.pct).toFixed(0) + "% di bawah entry \u2014 belum ada tanda balik dari data harga di kantor." : "Tidak ada posisi terbuka untuk dibaca momentumnya.")
    };
    var rows = _PERSONAS.map(function (p) {
        return '<div class="chat-disc-row" style="display:flex;gap:8px;align-items:flex-start;margin-top:6px"><span style="flex:0 0 auto">' + p.svg + '</span><div><b style="color:' + p.color + '">' + p.name + '</b> <span style="opacity:.65;font-size:11px">\u00b7 ' + p.angle + '</span><div>' + esc(ops[p.id]) + '</div></div></div>';
    }).join("");
    return '<div class="chat-discuss"><div style="font-weight:700">Diskusi agen \u2014 sebelum jawaban</div><div style="font-size:11px;opacity:.7">Persona di halaman ini berargumen dari data live kantor, bukan MausBot/Dots/Grok asli.</div>' + rows + '<div style="margin-top:8px;font-size:11px;opacity:.7">Konsensus di bawah ini dihitung dari angka yang sama.</div></div>';
}
function _cashLine() {
    var raw = window.__liveRaw, parts = [];
    if (raw && raw.venues) {
        Object.keys(raw.venues).forEach(function (k) {
            var r = raw.venues[k];
            if (r.cash_idr != null) parts.push((VENUES[k.toUpperCase()] ? VENUES[k.toUpperCase()].display : k) + " " + fmtRp(r.cash_idr));
        });
    }
    return parts.length ? parts.join(" · ") : "kas tidak tercatat di state";
}
function _targetLine() {
    var pl = VENUES.PLUANG;
    var kil = ["PUMPFUN", "FOURMEME", "CLANKER"].reduce(function (a, k) { return a + (VENUES[k].totalNum || 0); }, 0);
    var plPct = (pl && pl.totalNum != null) ? Math.round(pl.totalNum / 1500000 * 100) : null;
    var kilPct = Math.round((kil / 18200) / 30 * 100);
    return "Pluang " + (pl ? fmtRp(pl.totalNum || 0) : "—") + " dari target Rp1,5 jt (" + (plPct != null ? plPct : "?") + "%) · Kilat total " + fmtRp(kil) + " dari $30 (" + kilPct + "%) · deadline 1 Des 2026.";
}
function _reportLine() {
    var t = _anaTotals();
    var modal = _modalTotal();
    return "Total " + fmtRp(t.sum || 0) + (modal != null ? " vs modal " + fmtRp(modal) : "") + ". Terealisasi " + fmtSigned(t.realized || 0) + ", belum terealisasi " + fmtSigned(t.unrealized || 0) + ". " + _targetLine();
}
function _venuePl(key) {
    var v = VENUES[key];
    if (!v) return 0;
    return (v.plNum || 0) + (v.unrealizedNum || 0);
}
function _botShort(q) {
    var t = _anaTotals();
    var w = _worstPos();
    var venueKey = null;
    ["mexc", "indodax", "pluang", "pumpfun", "fourmeme", "clanker"].forEach(function (k) { if (q.indexOf(k) >= 0 || (k === "pumpfun" && q.indexOf("pump") >= 0) || (k === "fourmeme" && q.indexOf("four") >= 0)) venueKey = k; });
    if (/^(halo|hallo|hai|hi|hello|selamat pagi|selamat siang|selamat sore|selamat malam|pagi|siang|sore|malam|test|tes|cek)\b/.test(q)) return { topic: "sapa", discuss: false, text: "Halo bos! Ada yang bisa dibantu? Coba tanya 'laporan lengkap' atau 'kenapa aku rugi?'." };
    if (/terima kasih|makasih|thanks|thank you/.test(q)) return { topic: "thanks", discuss: false, text: "Sama-sama, bos. Ada lagi yang mau dicek?" };
    if (/sampai jumpa|dadah|bye|selamat tinggal/.test(q)) return { topic: "bye", discuss: false, text: "Sampai jumpa, bos. Semoga besok hijau!" };
    if (/apa kabar/.test(q)) return { topic: "kabar", discuss: true, text: "Kabar kantor: total " + fmtRp(t.sum || 0) + ", belum terealisasi " + fmtSigned(t.unrealized || 0) + ". " + (w ? ("Rugi terbesar " + w.sym + " " + w.pct.toFixed(1) + "%.") : "Tidak ada posisi rugi saat ini.") };
    if (/isi file|ringkas file|apa isi|baca file/.test(q)) {
        var files = window.__chatFiles || [];
        var txts = files.filter(function (f) { return f.text; });
        var imgs = files.filter(function (f) { return f.isImage; });
        if (!files.length) return { topic: "file", discuss: false, text: "Belum ada file yang dilampirkan, bos. Pakai tombol penjepit di samping mikrofon untuk kirim file." };
        if (imgs.length && !txts.length) return { topic: "file", discuss: false, text: "Gambarnya sudah tampil di chat, bos \u2014 chatbot lokal ini hanya bisa menampilkan gambar, belum bisa menganalisis isinya." };
        var f0 = txts[txts.length - 1];
        var one = f0.text.replace(/\s+/g, " ").slice(0, 400);
        return { topic: "file", discuss: false, text: "File " + f0.name + " (" + f0.text.split(/\n/).length + " baris): " + one + (f0.text.length > 400 ? "\u2026" : "") };
    }
    if (/^(terus|lanjut|yang mana|berapa|kenapa|gimana|detail|trus)\??$/.test(q)) {
        var last = window.__chatLastIntent || (typeof chat !== "undefined" && chat.mem && chat.mem.lastIntent);
        if (last === "rugi") return { topic: "rugi", discuss: true, text: "Yang paling rugi: " + (w ? (w.sym + " " + fmtSigned(w.idr) + " (" + w.pct.toFixed(1) + "%) di " + (VENUES[w.venue.toUpperCase()] ? VENUES[w.venue.toUpperCase()].display : w.venue) + ". ") : "tidak ada posisi rugi. ") + "Total belum terealisasi " + fmtSigned(t.unrealized || 0) + "." };
        if (last === "kas") return { topic: "kas", discuss: false, text: "Kas per venue: " + _cashLine() };
        if (last === "target") return { topic: "target", discuss: true, text: _targetLine() };
        if (last === "laporan") return { topic: "laporan", discuss: true, text: _reportLine() };
        return { topic: null, discuss: false, text: "Maksudmu yang mana, bos? Coba tanya soal laporan, rugi, kas, atau venue." };
    }
    if (/rugi|kenapa.*merah|kok (rugi|merah)|aku rugi|rugi terbesar|paling rugi|venue.*rugi/.test(q)) {
        var worstV = null, worstVal = 0;
        VENUE_ORDER.forEach(function (k) { var v = _venuePl(k); if (worstV === null || v < worstVal) { worstV = k; worstVal = v; } });
        return { topic: "rugi", discuss: true, text: "Total belum terealisasi " + fmtSigned(t.unrealized || 0) + "; terealisasi " + fmtSigned(t.realized || 0) + ". Rugi terbesar " + (w ? (w.sym + " " + w.pct.toFixed(1) + "% (" + fmtSigned(w.idr) + ")") : "tidak ada") + ". Venue paling rugi " + (worstV ? (VENUES[worstV].display + " " + fmtSigned(worstVal)) : "—") + "." };
    }
    if (/laporan|lapor|kasih laporan|gimana kabar uangku|status (uang|kantor)/.test(q)) return { topic: "laporan", discuss: true, text: _reportLine() };
    if (/bandingkan|venue.*(bagus|terbaik|paling bagus)|mana.*(bagus|untung|jelek)/.test(q)) {
        var best = null, bestVal = -Infinity, worst2 = null, worst2Val = Infinity;
        VENUE_ORDER.forEach(function (k) { var v = _venuePl(k); if (v > bestVal) { best = k; bestVal = v; } if (v < worst2Val) { worst2 = k; worst2Val = v; } });
        return { topic: "banding", discuss: true, text: "Paling bagus " + VENUES[best].display + " " + fmtSigned(bestVal) + "; paling rugi " + VENUES[worst2].display + " " + fmtSigned(worst2Val) + " (terealisasi + belum terealisasi)." };
    }
    if (/progres target|targetku|sudah sampai mana|progres misi|pencapaian target/.test(q)) return { topic: "target", discuss: true, text: _targetLine() };
    if (/berapa kas|kas |sisa uangku|saldo|uangku berapa|kasnya/.test(q)) {
        if (venueKey) { var raw = window.__liveRaw; var r = raw && raw.venues ? raw.venues[venueKey] : null; return { topic: "kas", discuss: false, text: "Kas " + VENUES[venueKey.toUpperCase()].display + ": " + ((r && r.cash_idr != null) ? fmtRp(r.cash_idr) : "tidak tercatat di state") + "." }; }
        return { topic: "kas", discuss: false, text: "Kas per venue: " + _cashLine() };
    }
    if (/posisi|berapa.*total|nilainya berapa/.test(q)) return { topic: "total", discuss: true, text: "Total " + fmtRp(t.sum || 0) + " dari " + t.count + " venue, " + (window.__liveRaw ? "posisi terbuka tercatat di state." : "state belum termuat.") + " Belum terealisasi " + fmtSigned(t.unrealized || 0) + "." };
    return null;
}
function _chatSpeak(text) {
    if (!text || window.__chatVoiceOn !== true) return;
    try {
        if (typeof speechSynthesis === "undefined") return;
        speechSynthesis.cancel();
        var clean = String(text).replace(/<[^>]*>/g, " ").replace(/\s+/g, " ").trim();
        if (!clean) return;
        var u = new SpeechSynthesisUtterance(clean);
        u.lang = "id-ID";
        var vs = speechSynthesis.getVoices ? speechSynthesis.getVoices() : [];
        var idv = null;
        vs.forEach(function (v) { if (!idv && v.lang && v.lang.toLowerCase().indexOf("id") === 0) idv = v; });
        if (idv) u.voice = idv;
        speechSynthesis.speak(u);
    } catch (e) {}
}
function _chatVoicePaint(btn) {
    var on = !!window.__chatVoiceOn;
    btn.setAttribute("aria-pressed", on ? "true" : "false");
    btn.style.opacity = on ? "1" : ".45";
    btn.style.color = on ? "#2ea36b" : "";
    btn.innerHTML = on
        ? '<svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polygon points="11 5 6 9 2 9 2 15 6 15 11 19 11 5" fill="currentColor" stroke="none"/><path d="M15.5 8.5a5 5 0 0 1 0 7"/><path d="M18.5 5.5a9 9 0 0 1 0 13"/></svg>'
        : '<svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polygon points="11 5 6 9 2 9 2 15 6 15 11 19 11 5" fill="currentColor" stroke="none"/><line x1="23" y1="9" x2="17" y2="15"/><line x1="17" y1="9" x2="23" y2="15"/></svg>';
}
function _chatInitVoice() {
    if (document.getElementById("chatVoiceBtn")) return;
    var input = document.getElementById("chatInput");
    if (!input) return;
    try { window.__chatVoiceOn = localStorage.getItem("chat-voice-v1") === "on"; } catch (e) { window.__chatVoiceOn = false; }
    var btn = document.createElement("button");
    btn.type = "button"; btn.id = "chatVoiceBtn"; btn.className = "chat-cbtn chat-voice-btn";
    btn.title = "Suara jawaban: klik untuk aktif/nonaktif";
    btn.setAttribute("aria-label", "Suara jawaban");
    _chatVoicePaint(btn);
    btn.addEventListener("click", function () {
        window.__chatVoiceOn = !window.__chatVoiceOn;
        try { localStorage.setItem("chat-voice-v1", window.__chatVoiceOn ? "on" : "off"); } catch (e) {}
        _chatVoicePaint(btn);
        if (window.__chatVoiceOn) _chatSpeak("Suara aktif, bos. Jawaban akan dibacakan.");
        else { try { speechSynthesis.cancel(); } catch (e) {} }
    });
    var panel = input.closest ? input.closest(".chat-panel, [id*='chat']") : null;
    var head = panel ? panel.querySelector(".chat-head, .chat-header, .chat-title, header") : null;
    if (head) head.appendChild(btn); else input.parentNode.insertBefore(btn, input);
}
window.__chatFiles = window.__chatFiles || [];
function _fmtSize(n) { if (n < 1024) return n + " B"; if (n < 1048576) return (n / 1024).toFixed(1) + " KB"; return (n / 1048576).toFixed(1) + " MB"; }
function _chatFiles(files) {
    files.forEach(function (f) {
        var rec = { name: f.name, size: f.size, type: f.type || "", text: null, isImage: (f.type || "").indexOf("image/") === 0 };
        window.__chatFiles.push(rec);
        var isText = /\.(txt|md|csv|json|log)$/i.test(f.name);
        var rd = new FileReader();
        rd.onload = function () {
            if (rec.isImage) {
                chatAddMsg("me", '<img src="' + rd.result + '" alt="' + esc(f.name) + '" style="max-width:220px;border-radius:8px"><div>\U0001F5BC ' + esc(f.name) + ' \u00b7 ' + _fmtSize(f.size) + '</div>', true);
            } else {
                if (isText) rec.text = String(rd.result || "");
                chatAddMsg("me", '<div>\U0001F4CE ' + esc(f.name) + ' \u00b7 ' + _fmtSize(f.size) + ' \u00b7 ' + esc(f.type || "file") + '</div>', true);
            }
        };
        if (rec.isImage) rd.readAsDataURL(f); else if (isText) rd.readAsText(f); else rd.readAsArrayBuffer(f);
    });
}
function _chatInitAttach() {
    var input = document.getElementById("chatInput");
    if (!input || document.getElementById("chatAttachBtn")) return;
    var btn = document.createElement("button");
    btn.type = "button"; btn.id = "chatAttachBtn"; btn.className = "chat-cbtn"; btn.title = "Lampirkan file";
    btn.setAttribute("aria-label", "Lampirkan file");
    btn.innerHTML = '<svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21.44 11.05l-9.19 9.19a6 6 0 0 1-8.49-8.49l9.19-9.19a4 4 0 0 1 5.66 5.66l-9.2 9.19a2 2 0 0 1-2.83-2.83l8.49-8.48"/></svg>';
    var fi = document.createElement("input");
    fi.type = "file"; fi.id = "chatFileInput"; fi.multiple = true; fi.style.display = "none";
    fi.accept = "image/*,.pdf,.txt,.md,.csv,.json,.log";
    input.parentNode.insertBefore(btn, input);
    input.parentNode.appendChild(fi);
    btn.addEventListener("click", function () { fi.click(); });
    fi.addEventListener("change", function () { _chatFiles(Array.prototype.slice.call(fi.files || [])); fi.value = ""; });
}
if (typeof botAnswer === "function" && !botAnswer.__p14) {
    var _botAnswer0 = botAnswer;
    botAnswer = function (rawQ) {
        var q = (rawQ || "").toLowerCase().trim();
        var cmd = null;
        try { cmd = (typeof runCommand === "function") ? runCommand(rawQ, q) : null; } catch (e) {}
        if (cmd != null) { _chatSpeak(cmd); return cmd; }
        var r = null;
        try { r = _botShort(q); } catch (e) {}
        if (r) {
            if (r.discuss) { try { chatAddMsg("bot", _discuss(r.topic), true); } catch (e) {} }
            try { if (chat && chat.mem) chat.mem.lastIntent = r.topic; } catch (e) {}
            window.__chatLastIntent = r.topic;
            _chatSpeak(r.text);
            return r.text;
        }
        var orig = null;
        try { orig = _botAnswer0(rawQ); } catch (e) {}
        if (orig && orig.indexOf("Yang itu di luar data") === 0) {
            var dflt = "Maksudmu yang mana, bos? Coba tanya soal laporan, rugi, kas, atau venue.";
            _chatSpeak(dflt);
            return dflt;
        }
        if (orig) _chatSpeak(orig);
        return orig;
    };
    botAnswer.__p14 = true;
}
_chatInitAttach();
_chatInitVoice();

function _searchInit() {
    var inp = document.getElementById("searchInput");
    if (!inp || inp.__p14) return;
    inp.__p14 = true;
    var box = document.createElement("div");
    box.id = "searchDrop";
    box.style.cssText = "position:absolute;z-index:60;background:#0f172a;border:1px solid rgba(255,255,255,.15);border-radius:10px;max-height:320px;overflow:auto;box-shadow:0 12px 32px rgba(0,0,0,.5);display:none;min-width:280px";
    (inp.parentNode || document.body).appendChild(box);
    function pos() { var r = inp.getBoundingClientRect(); box.style.left = (r.left + window.scrollX) + "px"; box.style.top = (r.bottom + window.scrollY + 4) + "px"; box.style.width = Math.max(r.width, 280) + "px"; }
    function results(q) {
        q = q.toLowerCase();
        var out = [];
        (C.agents || []).forEach(function (a) {
            var zn = (C.zones || []).filter(function (zz) { return zz.id === a.zone; })[0]; var hay = ((a.name || "") + " " + (a.role || "") + " " + (a.cat || a.category || "") + " " + (a.func || a.desc || a.tool || a.toolRaw || "") + " " + (zn ? (zn.title + " " + (zn.sub || "")) : "")).toLowerCase();
            if (hay.indexOf(q) >= 0) out.push({ kind: "agent", label: a.name, sub: (a.role || "") + " \u00b7 " + (a.cat || a.category || ""), ref: a });
        });
        VENUE_ORDER.forEach(function (k) {
            var v = VENUES[k];
            var hay = (v.display + " " + k + " " + (v.meta || "")).toLowerCase();
            if (hay.indexOf(q) >= 0) out.push({ kind: "venue", label: v.display, sub: "Venue \u00b7 " + (v.total || ""), ref: k });
        });
        (C.zones || []).forEach(function (z) {
            var hay = ((z.title || "") + " " + (z.sub || "")).toLowerCase();
            if (hay.indexOf(q) >= 0) out.push({ kind: "room", label: z.title, sub: "Ruangan \u00b7 " + (z.sub || ""), ref: z });
        });
        return out.slice(0, 12);
    }
    function openResult(r) {
        if (!r) return;
        box.style.display = "none";
        if (r.kind === "venue") { selectVenue(r.ref); return; }
        if (r.kind === "agent") {
            try { selectAgent(r.ref.id); return; } catch (e) {}
            var tags = document.querySelectorAll(".agent-tag");
            for (var i = 0; i < tags.length; i++) { if ((tags[i].textContent || "").trim().indexOf(r.ref.name) === 0) { tags[i].click(); return; } }
            return;
        }
        if (r.kind === "room") {
            var rows = document.querySelectorAll("[data-cat]");
            for (var j = 0; j < rows.length; j++) { if (rows[j].getAttribute("data-cat") === r.ref.id) { rows[j].click(); return; } }
        }
    }
    function render() {
        var q = inp.value.trim();
        if (!q) { box.style.display = "none"; return; }
        var res = results(q);
        pos();
        if (!res.length) { box.innerHTML = '<div style="padding:10px;opacity:.7">Tidak ada hasil untuk "' + esc(q) + '".</div>'; box.style.display = "block"; return; }
        box.innerHTML = res.map(function (r, i) {
            return '<button type="button" class="search-item" data-i="' + i + '" style="display:block;width:100%;text-align:left;padding:8px 10px;background:none;border:0;color:inherit;cursor:pointer"><b>' + esc(r.label) + '</b> <span style="opacity:.65;font-size:11px">' + esc(r.sub || "") + '</span></button>';
        }).join("");
        box.style.display = "block";
        box.querySelectorAll(".search-item").forEach(function (b) {
            b.addEventListener("click", function () { openResult(res[+b.getAttribute("data-i")]); });
        });
    }
    inp.addEventListener("input", render);
    inp.addEventListener("keydown", function (e) {
        if (e.key === "Enter") { var q = inp.value.trim(); if (!q) return; var res = results(q); if (res.length) openResult(res[0]); }
        if (e.key === "Escape") { inp.value = ""; box.style.display = "none"; inp.blur(); }
    });
    document.addEventListener("click", function (e) { if (!box.contains(e.target) && e.target !== inp) box.style.display = "none"; });
    var kbd = null;
    document.querySelectorAll("button, kbd, span").forEach(function (el) {
        if (!kbd && /^\s*\u2318\s*K\s*$/.test(el.textContent || "") && el.closest && el.closest(".topbar, header, .search, form, #topbar")) kbd = el;
    });
    if (!kbd) { document.querySelectorAll("kbd").forEach(function (el) { if (!kbd && (el.textContent || "").indexOf("\u2318") >= 0) kbd = el; }); }
    if (kbd) {
        kbd.style.cursor = "pointer"; kbd.setAttribute("role", "button"); kbd.setAttribute("tabindex", "0"); kbd.title = "Klik untuk membuka pencarian";
        kbd.addEventListener("click", function () { inp.focus(); inp.select(); if (inp.scrollIntoView) inp.scrollIntoView({ block: "nearest" }); });
        kbd.addEventListener("keydown", function (e) { if (e.key === "Enter" || e.key === " ") { e.preventDefault(); inp.focus(); } });
    }
    document.addEventListener("keydown", function (e) {
        if ((e.metaKey || e.ctrlKey) && (e.key === "k" || e.key === "K")) { e.preventDefault(); inp.focus(); inp.select(); }
    });
}


if (typeof zoomTo === "function" && !zoomTo.__p14) {
    var _zoomTo0 = zoomTo;
    zoomTo = function (z) {
        z = Math.max(0.4, Math.min(2.0, z));
        var from = (typeof cam !== "undefined" ? cam.zoom : 1), start = null;
        function step(ts) {
            if (start === null) start = ts;
            var p = Math.min(1, (ts - start) / 160);
            var v = from + (z - from) * (p * (2 - p));
            try { userCam = true; cam.zoom = v; applyCam(); } catch (e) {}
            if (p < 1) requestAnimationFrame(step);
        }
        requestAnimationFrame(step);
    };
    zoomTo.__p14 = true;
}
function _zoneForKeywords(kws) {
    var zones = C.zones || [];
    for (var i = 0; i < zones.length; i++) {
        var hay = ((zones[i].title || "") + " " + (zones[i].sub || "")).toLowerCase();
        for (var j = 0; j < kws.length; j++) if (hay.indexOf(kws[j]) >= 0) return zones[i];
    }
    return zones[0] || null;
}
function _roomMoveCheck() {
    try {
        var raw = window.__liveRaw; if (!raw || !raw.venues) return;
        var w = _worstPos(); if (!w) return;
        var focus = w.venue.toUpperCase();
        var tradeVenue = null;
        if (window.__prevTrades) {
            Object.keys(raw.venues).forEach(function (k) {
                var tc = raw.venues[k].trades_count;
                if (tc != null && window.__prevTrades[k] != null && tc > window.__prevTrades[k]) tradeVenue = k.toUpperCase();
            });
        }
        window.__prevTrades = {};
        Object.keys(raw.venues).forEach(function (k) { window.__prevTrades[k] = raw.venues[k].trades_count; });
        var target = tradeVenue || focus;
        if (window.__roomFocus && window.__roomFocus === target && !tradeVenue) return;
        // fix1: fokus baru diset sesudah pindah berhasil, bukan sebelumnya
        var zone = _zoneForKeywords((target === "MEXC" || target === "INDODAX") ? ["dex", "solana", "kripto", "crypto", "trading"] : (target === "PLUANG" ? ["saham", "forex", "makro"] : ["analis", "berita", "debat"]));
        if (!zone) { var _zid = (target === "PLUANG") ? "macro" : ((target === "MEXC" || target === "INDODAX") ? "market" : "ai"); var _zf = (C.zones || []).filter(function (z) { return z.id === _zid; })[0]; zone = _zf || (C.zones || [])[0] || null; } if (!zone) return;
        var kws = (target === "MEXC" || target === "INDODAX") ? ["crypto", "coin", "dex", "gecko", "terminal", "mexc", "indodax"] : (target === "PLUANG" ? ["saham", "stock", "pluang", "azn"] : ["analis", "berita", "news"]);
        var cands = (C.agents || []).filter(function (a) {
            var hay = ((a.name || "") + " " + (a.role || "") + " " + (a.cat || a.category || "") + " " + (a.func || a.desc || "")).toLowerCase();
            return a.zone !== zone.id && kws.some(function (k) { return hay.indexOf(k) >= 0; });
        }).sort(function (a, b) { return (a.name || "").localeCompare(b.name || ""); }).slice(0, 3);
        if (!cands.length) { cands = (C.agents || []).filter(function (a) { return a.zone !== zone.id; }).sort(function (a, b) { return (a.name || "").localeCompare(b.name || ""); }).slice(0, 3); } cands.forEach(function (a) { _moveAgent(a, zone, target); }); if (cands.length) { window.__roomFocus = target; try { _roomCountsSync(); } catch (e2) {} }
        if (cands.length) { try { window.dispatchEvent(new Event("resize")); } catch (e) {} }
    } catch (e) {}
}
function _moveReason(target) {
    var w = _worstPos();
    if (w && target === w.venue.toUpperCase()) return "posisi rugi terbesar " + w.sym + " " + w.pct.toFixed(1) + "%";
    return "trade baru di " + target;
}
function _moveAgent(a, zone, target) {
    var fromZone = (C.zones || []).filter(function (z) { return z.id === a.zone; })[0];
    var rec = { robot: a.name, from: fromZone ? fromZone.title : "\u2014", to: zone.title, time: new Date().toISOString(), reason: _moveReason(target) };
    a.zone = zone.id;
    window.__roomLog = window.__roomLog || [];
    window.__roomLog.unshift(rec);
    if (window.__roomLog.length > 50) window.__roomLog.length = 50;
    try { localStorage.setItem("room-moves-v1", JSON.stringify(window.__roomLog)); } catch (e) {}
    try { localStorage.setItem("room-zones-v1", JSON.stringify((C.agents || []).map(function (x) { return { n: x.name, z: x.zone }; }))); } catch (e) {}
    _roomLogRender();
    _animateAgent(a, zone);
}
function _animateAgent(a, zone) {
    var tag = null;
    document.querySelectorAll(".agent-tag").forEach(function (t) { if ((t.textContent || "").trim().indexOf(a.name) === 0) tag = t; });
    if (!tag) return;
    var cands = [];
    document.querySelectorAll(".agent-tag").forEach(function (t) {
        var nm = (t.textContent || "").trim();
        var ag = (C.agents || []).filter(function (x) { return x.name === nm; })[0];
        if (ag && ag.zone === zone.id && t !== tag) cands.push(t);
    });
    var pr = tag.parentElement.getBoundingClientRect();
    var r = tag.getBoundingClientRect();
    var cx = r.left - pr.left + r.width / 2, cy = r.top - pr.top + r.height / 2;
    var tx = cx, ty = cy;
    if (cands.length) {
        var sx = 0, sy = 0;
        cands.forEach(function (t) { var q = t.getBoundingClientRect(); sx += q.left - pr.left + q.width / 2; sy += q.top - pr.top + q.height / 2; });
        tx = sx / cands.length; ty = sy / cands.length;
    }
    tag.style.transition = "transform 1.4s ease";
    tag.style.transform = "translate(" + Math.round(tx - cx) + "px," + Math.round(ty - cy) + "px)";
}
function _roomLogRender() {
    var el = document.getElementById("roomLogPanel");
    if (!el) {
        var scene = document.querySelector(".scene") || document.body;
        el = document.createElement("div");
        el.id = "roomLogPanel";
        el.style.cssText = "position:absolute;left:452px;bottom:12px;z-index:40;width:280px;max-width:280px;max-height:56px;overflow:auto;background:rgba(15,23,42,.94);border:1px solid rgba(255,255,255,.15);border-radius:10px;padding:8px 10px;font-size:11px;color:#e2e8f0;box-shadow:0 12px 32px rgba(0,0,0,.45);cursor:pointer"; el.title = "Klik untuk memperbesar / mengecilkan log"; el.onclick = function () { el.style.maxHeight = (el.style.maxHeight === "260px") ? "56px" : "260px"; };
        scene.appendChild(el);
    }
    var log = window.__roomLog || [];
    el.innerHTML = '<div style="font-weight:700;margin-bottom:4px">Log perpindahan robot <span style="opacity:.6">(' + log.length + ')</span></div>' +
        (log.length ? log.slice(0, 5).map(function (m) {
            return '<div style="margin-top:4px;border-top:1px solid rgba(255,255,255,.08);padding-top:4px"><b>' + esc(m.robot) + '</b>: ' + esc(m.from) + ' \u2192 ' + esc(m.to) + '<br><span style="opacity:.7">' + esc(m.reason) + ' \u00b7 ' + esc(fmtWIBShort(m.time)) + '</span></div>';
        }).join("") : '<div style="opacity:.7">Belum ada perpindahan. Robot pindah saat ada venue yang butuh perhatian (rugi terbesar / trade baru).</div>');
}


function _brandDomain(a) {
    var name = (a.name || "").toLowerCase();
    var map = { "coingecko": "coingecko.com", "dexscreener": "dexscreener.com", "geckoterminal": "geckoterminal.com", "coinpaprika": "coinpaprika.com", "coinlore": "coinlore.com", "coinranking": "coinranking.com", "mexc": "mexc.com", "indodax": "indodax.com", "pluang": "pluang.com", "binance": "binance.com", "coinmarketcap": "coinmarketcap.com", "tradingview": "tradingview.com", "coindesk": "coindesk.com", "cointelegraph": "cointelegraph.com", "pump.fun": "pump.fun", "four.meme": "four.meme", "clanker": "clanker.world" };
    for (var k in map) { if (name.indexOf(k) >= 0) return map[k]; }
    var u = (a.url || a.link || a.tool || "");
    var m = String(u).match(/https?:\/\/([^\/]+)/);
    if (m) return m[1];
    return null;
}
function _brandImg(a, sz) {
    var d = _brandDomain(a);
    if (!d) return esc(a.emoji || "\uD83E\uDD16");
    return '<img src="https://www.google.com/s2/favicons?domain=' + encodeURIComponent(d) + '&sz=' + (sz || 64) + '" alt="' + esc(a.name) + '" style="width:22px;height:22px;object-fit:contain;vertical-align:middle" onerror="this.style.display=\'none\';if(this.nextElementSibling)this.nextElementSibling.style.display=\'inline\'"><span style="display:none">' + esc(a.emoji || "\uD83E\uDD16") + '</span>';
}
function _renderAgentBoard() {
    var q = (state.query || "").toLowerCase();
    var shown = C.agents.filter(function (a) {
        if (!q) return true;
        var zone = (C.zones || []).filter(function (z) { return z.id === a.zone; })[0];
        var hay = ((a.name || "") + " " + (a.role || "") + " " + (a.cat || a.category || "") + " " + (a.func || a.desc || a.tool || a.toolRaw || "") + " " + (zone ? (zone.title + " " + zone.sub) : "")).toLowerCase();
        return hay.indexOf(q) > -1;
    });
    $("#boardCount").textContent = shown.length;
    $("#board").innerHTML = C.zones.map(function (z) {
        var items = shown.filter(function (a) { return a.zone === z.id; });
        return '<section class="col" data-col="' + z.id + '">' +
            '<div class="col-head"><span class="col-dot" style="background:' + z.color + '"></span>' +
            '<span class="col-name">' + esc(z.title) + '</span><span class="col-count">' + items.length + '</span></div>' +
            '<div class="col-body">' + (items.map(function (a) {
                return '<article class="card agent-card" data-agent="' + a.id + '">' +
                    '<div class="ac-top"><span class="ac-av" style="background:' + a.color + '22;border:1px solid ' + a.color + '55">' + _brandImg(a) + '</span>' +
                    '<span><span class="ac-name">' + esc(a.name) + '</span><br><span class="ac-role">' + esc(a.role) + '</span></span></div>' +
                    '<div class="ac-meta"><span class="ac-badge' + (a.toolFinal === "TERBATAS" ? " off" : "") + '">' + (a.toolFinal === "TERBATAS" ? "TERBATAS" : "AKTIF") + (a.toolRaw ? " (" + a.toolRaw + ")" : "") + '</span>' +
                    '<span style="font-size:10.5px;opacity:.7">' + esc(a.status) + '</span></div></article>';
            }).join("") || '<div class="board-empty">Tidak ada robot yang cocok.</div>' + "</div></section>");
    }).join("");
    document.querySelectorAll(".agent-card[data-agent]").forEach(function (el) {
        el.addEventListener("click", function () { selectAgent(el.getAttribute("data-agent")); });
    });
}
if (typeof renderAgentBoard === "function") { renderAgentBoard = _renderAgentBoard; }
function _seedBoardTasks() {
    var cols = boardColumns();
    function colId(re) { var c = cols.filter(function (x) { return re.test((x.name || "") + " " + (x.id || "")); })[0]; return c ? c.id : null; }
    var inProg = colId(/progress|in progress|berjalan/i) || "inprogress";
    var todo = colId(/todo/i) || "todo";
    var backlog = colId(/backlog/i) || "backlog";
    var seeds = [
        { id: "task-pluang", title: "Misi scalping Pluang \u2014 target Rp1,5 jt bersih, 1 Des 2026", col: inProg, label: "Misi", comments: 0 },
        { id: "task-kilat", title: "Misi kilat \u2014 $30 bersih (3 wallet), 1 Des 2026", col: inProg, label: "Misi", comments: 0 },
        { id: "task-lpj", title: "LPJ trading 1 Des 2026 \u2014 6 venue", col: todo, label: "Laporan", comments: 0 },
        { id: "task-weekly", title: "Konfirmasi progres misi mingguan \u2014 sampai 1 Des 2026", col: todo, label: "Rutin", comments: 0 },
        { id: "task-vps", title: "Perpanjangan VPS Tencent \u2014 6 Des 2026", col: backlog, label: "VPS", comments: 0 }
    ];
    if (!C.workItems) C.workItems = [];
    seeds.forEach(function (s) { if (!C.workItems.some(function (w) { return w.id === s.id; })) C.workItems.push(s); });
    if (state.items) {
        seeds.forEach(function (s) { if (!state.items.some(function (w) { return w.id === s.id; })) state.items.push(JSON.parse(JSON.stringify(s))); });
    }
}


function _newsTickerRender() {
    var strip = document.querySelector(".dock-wrap") || document.querySelector(".tabstrip") || document.body;
    var bar = document.getElementById("newsTicker");
    if (!bar) {
        bar = document.createElement("div");
        bar.id = "newsTicker";
        bar.style.cssText = "display:flex;align-items:center;gap:10px;background:#0b1220;border-top:1px solid rgba(255,255,255,.12);color:#e2e8f0;font-size:12px;padding:6px 10px;overflow:hidden;white-space:nowrap;z-index:45";
        var host = strip.parentNode || document.body;
        host.insertBefore(bar, strip);
        bar.innerHTML = '<span id="newsClock" style="font-weight:700;color:#38bdf8;flex:0 0 auto">--:--:-- WIB</span>' +
            '<button id="newsPauseBtn" type="button" title="Jeda / lanjut ticker" style="flex:0 0 auto;background:none;border:1px solid rgba(255,255,255,.25);color:inherit;border-radius:6px;padding:2px 8px;cursor:pointer">\u23F8</button>' +
            '<button id="newsOpenBtn" type="button" title="Buka panel berita lengkap" style="flex:0 0 auto;background:none;border:1px solid rgba(255,255,255,.25);color:inherit;border-radius:6px;padding:2px 8px;cursor:pointer">\uD83D\uDCF0 Semua berita</button>' +
            '<div id="newsTrack" style="overflow:hidden;flex:1 1 auto"><div id="newsScroll" style="display:inline-block;white-space:nowrap;animation:newsScroll 90s linear infinite"></div></div>';
        var st = document.createElement("style");
        st.textContent = "@keyframes newsScroll{from{transform:translateX(0)}to{transform:translateX(-50%)}}";
        document.head.appendChild(st);
        document.getElementById("newsPauseBtn").addEventListener("click", function () {
            var sc = document.getElementById("newsScroll");
            var paused = sc.style.animationPlayState === "paused";
            sc.style.animationPlayState = paused ? "running" : "paused";
            this.textContent = paused ? "\u23F8" : "\u25B6";
        });
        bar.addEventListener("mouseenter", function () { var sc = document.getElementById("newsScroll"); if (sc) sc.style.animationPlayState = "paused"; });
        bar.addEventListener("mouseleave", function () { var sc = document.getElementById("newsScroll"); if (sc) sc.style.animationPlayState = "running"; });
        document.getElementById("newsOpenBtn").addEventListener("click", function () { _newsPanelOpen(); });
        setInterval(function () {
            var c = document.getElementById("newsClock");
            if (c) { try { c.textContent = new Date().toLocaleTimeString("id-ID", { timeZone: "Asia/Jakarta", hour: "2-digit", minute: "2-digit", second: "2-digit" }) + " WIB"; } catch (e) { c.textContent = new Date().toLocaleTimeString() + " WIB"; } }
        }, 1000);
    }
    var raw = window.__liveRaw;
    var items = (raw && raw.news) || [];
    var sc = document.getElementById("newsScroll");
    if (sc) {
        var at = (raw && raw.news_at) ? (" \u00b7 diperbarui " + fmtWIBShort(raw.news_at)) : "";
        var html = items.length ? items.map(function (n) {
            return '<a href="' + esc(n.url || "#") + '" target="_blank" rel="noopener" style="color:#e2e8f0;text-decoration:none;margin-right:36px"><b style="color:#38bdf8">' + esc(n.source || "") + '</b> \u00b7 ' + esc(n.title || "") + '</a>';
        }).join("") : '<span style="opacity:.7">Berita belum termuat \u2014 menunggu status live.</span>';
        sc.innerHTML = html + (items.length ? html : "") + '<span style="opacity:.6;font-size:11px">' + esc(at) + '</span>';
    }
}
function _newsPanelOpen() {
    var raw = window.__liveRaw;
    var items = (raw && raw.news) || [];
    var old = document.getElementById("newsPanel");
    if (old) { old.remove(); return; }
    var p = document.createElement("div");
    p.id = "newsPanel";
    p.style.cssText = "position:fixed;top:60px;right:12px;z-index:90;width:min(430px,92vw);max-height:70vh;overflow:auto;background:#0f172a;border:1px solid rgba(255,255,255,.15);border-radius:12px;padding:14px;color:#e2e8f0;box-shadow:0 16px 40px rgba(0,0,0,.5)";
    p.innerHTML = '<div style="display:flex;justify-content:space-between;align-items:center"><b>Berita pasar live</b><button id="newsPanelClose" type="button" style="background:none;border:0;color:inherit;font-size:18px;cursor:pointer">\u2715</button></div>' +
        '<div style="font-size:11px;opacity:.7;margin:4px 0 8px">' + (raw && raw.news_at ? ("Diperbarui " + esc(fmtWIBShort(raw.news_at)) + " \u00b7 sumber: CoinDesk / CoinTelegraph / Google News") : "Sumber: CoinDesk / CoinTelegraph / Google News") + '</div>' +
        (items.length ? items.map(function (n) {
            return '<a href="' + esc(n.url || "#") + '" target="_blank" rel="noopener" style="display:block;color:inherit;text-decoration:none;padding:8px 0;border-top:1px solid rgba(255,255,255,.08)"><b style="color:#38bdf8">' + esc(n.source || "") + '</b><div>' + esc(n.title || "") + '</div><span style="font-size:11px;opacity:.6">' + esc(n.time ? fmtWIBShort(n.time) : "") + '</span></a>';
        }).join("") : '<div style="opacity:.7">Belum ada berita \u2014 menunggu status live.</div>');
    document.body.appendChild(p);
    document.getElementById("newsPanelClose").addEventListener("click", function () { p.remove(); });
}


window.__repairs = window.__repairs || null;
function _repairsLoad() {
    if (window.__repairs) return;
    window.__repairs = { repairs: [
        { date: "12 Nov 2026", what: "Perbaikan Kurs", result: "Kurs USD/IDR selaras dengan sumber live" },
        { date: "13 Nov 2026", what: "Perbaikan kilat E1-E7", result: "7 loop kilat kembali jalan normal" },
        { date: "14 Nov 2026", what: "Tampilkan rugi/untung belum terealisasi", result: "Harga live MEXC/Indodax + unrealized tampil di ARUS P/L" }
    ], upcoming: [
        { date: "1 Des 2026", what: "LPJ trading 1 Desember 2026 - 6 venue" },
        { date: "6 Des 2026", what: "Perpanjangan VPS Tencent (H-3)" },
        { date: "Setelah limit lepas", what: "Login ulang Pluang - URL ronde 5" }
    ] };
    try {
        fetch("repairs.json").then(function (r) { return r.json(); }).then(function (d) { window.__repairs = d; }).catch(function () {});
    } catch (e) {}
}
function _repairsPanel() {
    var d = window.__repairs || { repairs: [], upcoming: [] };
    var inner = '<div style="margin-bottom:8px;font-size:12px;opacity:.8">Perbaikan live oleh robot/loop \u2014 kronologis.</div>' +
        '<div class="detail-block">' + d.repairs.map(function (r) {
            return '<div class="zone-item"><span class="zone-id">' + esc(r.date) + '</span><span class="zone-title">' + esc(r.what) + ' \u2014 ' + esc(r.result) + '</span></div>';
        }).join("") + '</div>' +
        '<div class="side-sec-title" style="margin-top:12px">Jadwal mendatang</div>' +
        '<div class="detail-block">' + d.upcoming.map(function (r) {
            return '<div class="zone-item"><span class="zone-id">' + esc(r.date) + '</span><span class="zone-title">' + esc(r.what) + '</span></div>';
        }).join("") + '</div>' +
        '<div style="margin-top:10px;font-size:11px;opacity:.6">Data dari office/repairs.json \u2014 perbaikan baru ditambahkan ke file itu.</div>';
    return panelShell("Riwayat Perbaiki", "Riwayat perbaikan, bukan jadwal.", inner);
}
if (typeof listPanel === "function" && !listPanel.__p14) {
    var _listPanel0 = listPanel;
    listPanel = function (id) { if (id === "scheduled") return _repairsPanel(); return _listPanel0(id); };
    listPanel.__p14 = true;
}
function _renameScheduledMenu() {
    document.querySelectorAll("span").forEach(function (el) {
        if (el.childNodes.length === 1 && el.childNodes[0].nodeType === 3 && (el.textContent || "").trim() === "Scheduled") el.textContent = "Riwayat Perbaiki";
    });
}
function _fmtLivePrice(price, k) {
    if (price == null) return "\u2014";
    if (k === "indodax") return fmtRp(price);
    if (Math.abs(price) >= 100) return "$" + Number(price).toLocaleString("en-US", { maximumFractionDigits: 2 });
    if (Math.abs(price) >= 1) return "$" + Number(price).toFixed(2);
    if (Math.abs(price) >= 0.01) return "$" + Number(price).toFixed(4);
    return "$" + Number(price).toFixed(6);
}
function _marketTableRender() {
    var scene = document.querySelector(".scene") || document.body;
    var panel = document.getElementById("marketTable");
    if (!panel) {
        panel = document.createElement("div");
        panel.id = "marketTable";
        panel.style.cssText = "position:absolute;left:12px;bottom:12px;z-index:35;width:min(360px,88vw);background:rgba(15,23,42,.94);border:1px solid rgba(255,255,255,.15);border-radius:12px;color:#e2e8f0;box-shadow:0 12px 32px rgba(0,0,0,.45)";
        scene.appendChild(panel);
        var open = true;
        try { open = localStorage.getItem("market-table-v1") !== "closed"; } catch (e) {}
        panel.dataset.open = open ? "1" : "0";
    }
    var raw = window.__liveRaw;
    var rows = [];
    if (raw && raw.venues) {
        Object.keys(raw.venues).forEach(function (k) {
            var v = raw.venues[k];
            var disp = (VENUES[k.toUpperCase()] ? VENUES[k.toUpperCase()].display : k);
            (v.positions || []).forEach(function (p) {
                rows.push({ sym: String(p.symbol || p.pair_id || "?").toUpperCase(), venue: disp, price: _fmtLivePrice(p.price, k), pct: (p.unrealized_pct != null ? p.unrealized_pct : null), note: null });
            });
            if (!(v.positions || []).length) {
                rows.push({ sym: disp, venue: "\u2014", price: "\u2014", pct: null, note: "tidak ada posisi terbuka \u00b7 total " + fmtRp((VENUES[k.toUpperCase()] && VENUES[k.toUpperCase()].totalNum) || 0) });
            }
        });
    }
    var isOpen = panel.dataset.open === "1";
    var body = "";
    if (isOpen) {
        body = '<table style="width:100%;border-collapse:collapse;font-size:12px"><thead><tr style="opacity:.7;text-align:left"><th style="padding:4px 8px">Aset</th><th style="padding:4px 8px">Venue</th><th style="padding:4px 8px;text-align:right">Harga sekarang</th><th style="padding:4px 8px;text-align:right">Perubahan dari entry</th></tr></thead><tbody>' +
            (rows.length ? rows.map(function (r) {
                var ch = (r.pct == null) ? '<span style="opacity:.6">\u2014</span>' : '<span style="color:' + (r.pct < 0 ? "#e0524d" : "#2ea36b") + '">' + (r.pct < 0 ? "\u25BC " : "\u25B2 ") + (r.pct > 0 ? "+" : "") + r.pct.toFixed(2) + "%</span>";
                return '<tr style="border-top:1px solid rgba(255,255,255,.08)"><td style="padding:5px 8px"><b>' + esc(r.sym) + '</b>' + (r.note ? '<div style="font-size:10.5px;opacity:.6">' + esc(r.note) + '</div>' : "") + '</td><td style="padding:5px 8px">' + esc(r.venue) + '</td><td style="padding:5px 8px;text-align:right">' + esc(r.price) + '</td><td style="padding:5px 8px;text-align:right">' + ch + '</td></tr>';
            }).join("") : '<tr><td colspan="4" style="padding:8px;opacity:.7">Menunggu status live\u2026</td></tr>') + '</tbody></table>' +
            '<div style="font-size:10.5px;opacity:.6;padding:6px 8px">Harga publik MEXC/Indodax/Pluang dari status.json \u00b7 bergerak tiap fetch (~30 dtk) \u00b7 perubahan = vs harga beli.</div>';
    }
    panel.innerHTML = '<div id="marketTableHead" style="display:flex;justify-content:space-between;align-items:center;padding:8px 10px;cursor:pointer"><b>\uD83D\uDCCA Pasar Live \u2014 6 venue</b><button id="marketTableToggle" type="button" style="background:none;border:1px solid rgba(255,255,255,.25);color:inherit;border-radius:6px;padding:2px 9px;cursor:pointer">' + (isOpen ? "\u25BE Tutup" : "\u25B8 Buka") + '</button></div>' + body;
    document.getElementById("marketTableToggle").addEventListener("click", function (e) {
        e.stopPropagation();
        panel.dataset.open = (panel.dataset.open === "1") ? "0" : "1";
        try { localStorage.setItem("market-table-v1", panel.dataset.open === "1" ? "open" : "closed"); } catch (e2) {}
        _marketTableRender();
    });
    document.getElementById("marketTableHead").addEventListener("click", function () { document.getElementById("marketTableToggle").click(); });
}
if (typeof applyLive === "function" && !applyLive.__p14b) {
    var _applyLiveB = applyLive;
    applyLive = function (d) {
        var r = _applyLiveB(d);
        try { _newsTickerRender(); _marketTableRender(); _roomMoveCheck(); } catch (e) {}
        return r;
    };
    applyLive.__p14b = true;
}


var _DEBATERS = [
    { id: "mod", name: "Moderator", color: "#64748b", role: "Memimpin debat" },
    { id: "berita", name: "Analis Berita", color: "#0ea5e9", role: "Berita & sentimen" },
    { id: "sosmed", name: "Pengamat Sosmed", color: "#a855f7", role: "Suara sosial" },
    { id: "peramal", name: "Peramal/Prediktor", color: "#f59e0b", role: "Prediksi harga" },
    { id: "jaringan", name: "Sinyal Jaringan", color: "#22c55e", role: "Data on-chain" },
    { id: "internet", name: "Pengamat Internet", color: "#ec4899", role: "Peristiwa dunia" }
];
function _debatePreds() { try { return JSON.parse(localStorage.getItem("debate-predictions-v1") || "[]"); } catch (e) { return []; } }
function _debateSavePreds(p) { try { localStorage.setItem("debate-predictions-v1", JSON.stringify(p)); } catch (e) {} }
function _debateEnsurePreds() {
    var preds = _debatePreds();
    var raw = window.__liveRaw; if (!raw || !raw.venues) return preds;
    var w = _worstPos(); if (!w) return preds;
    var today = new Date().toISOString().slice(0, 10);
    var exists = preds.some(function (p) { return p.day === today && p.sym === w.sym; });
    if (exists) return preds;
    var fromPrice = null;
    (raw.venues[w.venue.toLowerCase()].positions || []).forEach(function (p) { if (String(p.symbol || p.pair_id || "").toUpperCase() === w.sym) fromPrice = p.price; });
    if (fromPrice == null) return preds;
    preds.push({ id: "dp-" + Date.now(), day: today, debater: "Peramal/Prediktor", sym: w.sym, venue: w.venue, direction: "naik", target: fromPrice * 1.05, fromPrice: fromPrice, time: new Date().toISOString(), due: Date.now() + 24 * 3600 * 1000, args: "Harga " + w.pct.toFixed(1) + "% di bawah entry; momentum perlu balik 5% dalam 24 jam." });
    _debateSavePreds(preds);
    return preds;
}
function _debateScoreDue(preds) {
    var raw = window.__liveRaw; if (!raw || !raw.venues) return;
    var changed = false;
    preds.forEach(function (p) {
        if (p.result || Date.now() < p.due) return;
        var v = raw.venues[(p.venue || "").toLowerCase()]; if (!v) return;
        var f = (v.positions || []).filter(function (x) { return String(x.symbol || x.pair_id || "").toUpperCase() === p.sym; })[0];
        if (!f || f.price == null) return;
        p.actual = f.price; p.actualTime = new Date().toISOString();
        var diff = Math.abs(f.price - p.target) / p.target;
        if (diff <= 0.01) p.result = "impas";
        else if (p.direction === "naik") p.result = (f.price >= p.target) ? "menang" : "kalah";
        else p.result = (f.price <= p.target) ? "menang" : "kalah";
        changed = true;
    });
    if (changed) _debateSavePreds(preds);
}
function _debateScore(preds) {
    var out = {};
    _DEBATERS.forEach(function (d) { out[d.name] = { w: 0, l: 0, d: 0, open: 0, acc: null }; });
    preds.forEach(function (p) {
        var rec = out[p.debater] || (out[p.debater] = { w: 0, l: 0, d: 0, open: 0, acc: null });
        if (p.result) { if (p.result === "menang") rec.w++; else if (p.result === "kalah") rec.l++; else rec.d++; }
        else rec.open++;
    });
    Object.keys(out).forEach(function (k) { var r = out[k]; var tot = r.w + r.l + r.d; r.acc = tot ? Math.round((r.w + r.d * 0.5) / tot * 100) : null; });
    return out;
}
function _debateArgs() {
    var w = _worstPos();
    var raw = window.__liveRaw;
    var news = (raw && raw.news) || [];
    var newsLine = "Tidak ada berita khusus hari ini di ticker.";
    if (w) {
        var hit = null;
        news.forEach(function (n) { if (!hit && (n.title || "").toLowerCase().indexOf(w.sym.toLowerCase().slice(0, 4)) >= 0) hit = n; });
        newsLine = hit ? ("Ticker: \u201c" + hit.title + "\u201d (" + hit.source + ").") : ("Tidak ada berita khusus " + w.sym + " di ticker hari ini.");
    }
    return [
        { who: "Moderator", color: "#64748b", side: "topik", text: w ? ("Topik hari ini: " + w.sym + " " + w.pct.toFixed(1) + "% dari entry \u2014 apakah kembali atau lanjut turun?") : "Tidak ada posisi terbuka untuk diperdebatkan." },
        { who: "Analis Berita", color: "#0ea5e9", side: "berita", text: newsLine },
        { who: "Pengamat Sosmed", color: "#a855f7", side: "sentimen", text: "Tidak ada data sosial di kantor \u2014 argumen ini memakai harga, bukan sentimen sosmed." },
        { who: "Peramal/Prediktor", color: "#f59e0b", side: "prediksi", text: w ? ("Peramal: " + w.sym + " sekarang " + fmtSigned(w.idr) + " (" + w.pct.toFixed(1) + "%); butuh balik " + Math.abs(w.pct).toFixed(0) + "% untuk kembali ke entry.") : "Tidak ada posisi untuk diprediksi." },
        { who: "Sinyal Jaringan", color: "#22c55e", side: "data", text: w ? ("Sinyal: " + w.sym + " masih di bawah entry; trades MEXC tercatat 0 \u2014 belum ada aksi baru.") : "Tidak ada sinyal dari posisi terbuka." },
        { who: "Pengamat Internet", color: "#ec4899", side: "peristiwa", text: (news[0] ? ("Peristiwa dunia: " + news[0].title) : "Tidak ada peristiwa tercatat di ticker.") }
    ];
}


function _debateRender() {
    var scene = document.querySelector(".scene") || document.body;
    var el = document.getElementById("debateRoom");
    if (!el) {
        el = document.createElement("div");
        el.id = "debateRoom";
        el.style.cssText = "position:absolute;left:50%;top:46%;transform:translate(-50%,-50%);z-index:30;width:min(560px,92vw);max-height:80%;overflow:auto;background:rgba(15,23,42,.95);border:1px solid rgba(255,255,255,.15);border-radius:14px;padding:14px;color:#e2e8f0;box-shadow:0 16px 40px rgba(0,0,0,.5)";
        scene.appendChild(el);
    }
    var preds = _debateEnsurePreds();
    _debateScoreDue(preds);
    var score = _debateScore(preds);
    var w = _worstPos();
    var t = _anaTotals();
    var pl = VENUES.PLUANG;
    var plNeed = (pl && pl.totalNum) ? Math.round((1500000 - pl.totalNum) / pl.totalNum * 100) : null;
    var kil = ["PUMPFUN", "FOURMEME", "CLANKER"].reduce(function (a, k) { return a + (VENUES[k].totalNum || 0); }, 0);
    var kilUsd = kil / 18200;
    var kilNeed = kilUsd > 0 ? Math.round((30 - kilUsd) / kilUsd * 100) : null;
    var best = null, bestAcc = -1;
    Object.keys(score).forEach(function (k) { if (score[k].acc != null && score[k].acc > bestAcc) { bestAcc = score[k].acc; best = k; } });
    var args = _debateArgs();
    el.innerHTML = '<div style="display:flex;justify-content:space-between;align-items:center"><b>RUANG DEBAT</b><span style="display:flex;gap:6px"><button id="debateZoomBtn" type="button" style="background:none;border:1px solid rgba(255,255,255,.25);color:inherit;border-radius:6px;padding:2px 9px;cursor:pointer">\uD83D\uDD0D Zoom debat</button><button id="debateCloseBtn" type="button" style="background:none;border:0;color:inherit;font-size:18px;cursor:pointer">\u2715</button></span></div>' +
        '<div style="font-size:11px;opacity:.7;margin-top:2px">Debat dihitung dari data live kantor, bukan panggilan model berbayar. Prediksi disimpan di localStorage browser (bukan server).</div>' +
        '<div style="display:flex;gap:8px;flex-wrap:wrap;margin-top:10px">' + _DEBATERS.map(function (d) {
            return '<div style="flex:1 1 28%;min-width:140px;border:1px solid rgba(255,255,255,.12);border-radius:10px;padding:8px"><div style="display:flex;gap:6px;align-items:center"><span style="width:26px;height:26px;border-radius:50%;background:' + d.color + ';display:inline-flex;align-items:center;justify-content:center;font-weight:700;color:#fff">' + esc(d.name[0]) + '</span><b>' + esc(d.name) + '</b></div><div style="font-size:11px;opacity:.7">' + esc(d.role) + '</div></div>';
        }).join("") + '</div>' +
        '<div style="margin-top:10px"><b>Debat berjalan</b>' + args.map(function (a) {
            return '<div style="margin-top:6px;border-left:3px solid ' + a.color + ';padding:6px 8px;background:rgba(255,255,255,.04);border-radius:0 8px 8px 0"><b style="color:' + a.color + '">' + esc(a.who) + '</b> <span style="font-size:10.5px;opacity:.65">\u00b7 ' + esc(a.side) + '</span><div>' + esc(a.text) + '</div></div>';
        }).join("") + '</div>' +
        '<div style="margin-top:10px"><b>Prediksi menuju target</b><div style="font-size:12px;margin-top:4px">Pluang butuh ' + (plNeed != null ? ("+" + plNeed + "%") : "?") + ' dari total sekarang untuk mencapai Rp1,5 jt (1 Des 2026). Kilat butuh ' + (kilNeed != null ? ("+" + kilNeed + "%") : "?") + ' untuk mencapai $30. Prediksi debat: ' + (w ? (w.sym + " perlu balik mendekati entry sebelum target tercapai.") : "tidak ada posisi terbuka.") + '</div></div>' +
        '<div style="margin-top:10px"><b>Strategi terpilih saat ini</b><div style="font-size:12px;margin-top:4px">BreakoutTren (paper +759% vs Aturan A +605%, Hunter A \u221284% jangan dipakai \u2014 run #4, 11 Nov). Filter Fear &amp; Greed ditolak di paper (\u22121,39%/trade saat F&amp;G \u226425 \u2014 run #6, 13 Nov 08:01 WIB). Loop boleh berubah dari hasil latihan/debat (paper dulu, lalu live bila lolos) \u2014 spot saja, tanpa leverage, SL/KS tidak dilonggarkan, tanpa deposit baru tanpa persetujuan, tiap trade dilaporkan.</div></div>' +
        '<div style="margin-top:10px"><b>Hasil debat per robot</b> ' + (best ? '<span style="font-size:11px;color:#fbbf24">\uD83C\uDFC6 Paling Akurat: ' + esc(best) + ' (' + bestAcc + '%)</span>' : '<span style="font-size:11px;opacity:.7">Belum ada yang dinilai.</span>') +
        Object.keys(score).map(function (k) {
            var r = score[k];
            return '<button type="button" class="debate-res" data-debater="' + esc(k) + '" style="display:block;width:100%;text-align:left;background:none;border:0;border-top:1px solid rgba(255,255,255,.08);color:inherit;padding:6px 0;cursor:pointer"><b>' + esc(k) + '</b> \u00b7 Menang ' + r.w + ' \u00b7 Kalah ' + r.l + ' \u00b7 Impas ' + r.d + ' \u00b7 Prediksi terbuka ' + r.open + (r.acc != null ? ' \u00b7 Akurasi ' + r.acc + '%' : '') + '</button>';
        }).join("") + '<div id="debateDetail" style="margin-top:8px"></div></div>' +
        '<div style="margin-top:10px;font-size:11px;opacity:.7">Strategi aktif tiap loop \u2014 Indodax TP +15% / SL \u221230% \u00b7 MEXC TP +15% / SL \u221230% / KS 65% \u00b7 Kilat TP +150% / SL \u221235% / KS 65% \u00b7 Pluang AZN TP +12% / SL \u22125% (dari state/kantor; yang tidak tercatat ditandai).</div>';
    document.getElementById("debateCloseBtn").addEventListener("click", function () { el.style.display = "none"; });
    document.getElementById("debateZoomBtn").addEventListener("click", function () { _debateZoomOpen(); });
    el.querySelectorAll(".debate-res").forEach(function (b) {
        b.addEventListener("click", function () { _debateResultDetail(b.getAttribute("data-debater")); });
    });
}
function _debateResultDetail(name) {
    var box = document.getElementById("debateDetail");
    if (!box) return;
    var preds = _debatePreds().filter(function (p) { return p.debater === name; });
    var raw = window.__liveRaw;
    function curPrice(sym, venue) {
        if (!raw || !raw.venues) return null;
        var v = raw.venues[(venue || "").toLowerCase()]; if (!v) return null;
        var f = (v.positions || []).filter(function (p) { return String(p.symbol || p.pair_id || "").toUpperCase() === sym; })[0];
        return f ? f.price : null;
    }
    if (!preds.length) { box.innerHTML = '<div style="font-size:12px;opacity:.8">' + esc(name) + ' belum punya prediksi tercatat. Prediksi dibuat otomatis tiap hari dari posisi rugi terbesar.</div>'; return; }
    box.innerHTML = '<b>Kenapa ' + esc(name) + ' menang / kalah / impas \u2014 dari data tercatat</b>' + preds.map(function (p) {
        var cur = curPrice(p.sym, p.venue);
        var diff = (cur != null && p.fromPrice) ? ((cur - p.fromPrice) / p.fromPrice * 100) : null;
        var status = p.result ? (p.result === "menang" ? "Menang" : p.result === "kalah" ? "Kalah" : "Impas") : ("Menunggu hasil (jatuh tempo " + esc(fmtWIBShort(new Date(p.due).toISOString())) + ")");
        var why = p.result === "menang" ? "Harga mencapai target prediksi." : p.result === "kalah" ? "Harga tidak mencapai target sampai jatuh tempo." : p.result === "impas" ? "Harga akhir dalam \u00b11% dari target." : "Belum ada hasil \u2014 harga sekarang vs target masih berjalan.";
        return '<div style="margin-top:6px;border:1px solid rgba(255,255,255,.12);border-radius:8px;padding:8px;font-size:12px"><b>' + esc(p.sym) + '</b> \u00b7 ' + esc(p.direction) + ' \u00b7 ' + esc(status) + '<br>Prediksi ' + esc(p.direction === "naik" ? "naik ke " : "turun ke ") + esc(_fmtLivePrice(p.target, (p.venue || "").toLowerCase())) + ' dari ' + esc(_fmtLivePrice(p.fromPrice, (p.venue || "").toLowerCase())) + ' \u00b7 harga sekarang ' + esc(cur != null ? _fmtLivePrice(cur, (p.venue || "").toLowerCase()) : "\u2014") + (diff != null ? ' (' + (diff > 0 ? "+" : "") + diff.toFixed(2) + "% dari harga prediksi)" : "") + '<br><span style="opacity:.75">Argumen: ' + esc(p.args || "") + ' \u00b7 ' + esc(why) + '</span></div>';
    }).join("");
}


function _debateRobotSVG(x, y, color) {
    return '<g transform="translate(' + x + ',' + y + ')">' +
        '<ellipse cx="0" cy="96" rx="34" ry="7" fill="rgba(0,0,0,.12)"/>' +
        '<rect x="-26" y="34" width="52" height="58" rx="14" fill="#ffffff" stroke="' + color + '" stroke-width="2"/>' +
        '<circle cx="0" cy="8" r="22" fill="#ffffff" stroke="' + color + '" stroke-width="2"/>' +
        '<circle cx="-8" cy="6" r="3.5" fill="#0f172a"/><circle cx="8" cy="6" r="3.5" fill="#0f172a"/>' +
        '<rect x="-10" y="16" width="20" height="3" rx="1.5" fill="' + color + '"/>' +
        '<line x1="0" y1="-14" x2="0" y2="-22" stroke="' + color + '" stroke-width="2"/><circle cx="0" cy="-25" r="4" fill="' + color + '"/>' +
        '<rect x="-34" y="44" width="10" height="26" rx="5" fill="#ffffff" stroke="' + color + '" stroke-width="1.5"/>' +
        '<rect x="24" y="44" width="10" height="26" rx="5" fill="#ffffff" stroke="' + color + '" stroke-width="1.5"/>' +
        '<rect x="-16" y="52" width="32" height="16" rx="4" fill="' + color + '" opacity=".9"/></g>';
}
function _debateZoomOpen() {
    var old = document.getElementById("debateZoom");
    if (old) { old.remove(); return; }
    var w = _worstPos();
    var t = _anaTotals();
    var venueBars = VENUE_ORDER.map(function (k) { return { name: VENUES[k].display, val: (VENUES[k].totalNum || 0) }; });
    var max = 1;
    venueBars.forEach(function (b) { max = Math.max(max, Math.abs(b.val)); });
    var bars = venueBars.map(function (b, i) {
        var h = Math.max(4, Math.abs(b.val) / max * 62);
        var x = 312 + i * 52;
        var y = 168 - h;
        var col = (b.val >= 0) ? "#22c55e" : "#e0524d";
        return '<rect x="' + x + '" y="' + y + '" width="34" height="' + h + '" rx="3" fill="' + col + '"/>' +
            '<text x="' + (x + 17) + '" y="184" font-size="9" fill="#94a3b8" text-anchor="middle">' + esc(b.name.slice(0, 6)) + '</text>';
    }).join("");
    var ov = document.createElement("div");
    ov.id = "debateZoom";
    ov.style.cssText = "position:fixed;inset:0;z-index:95;background:rgba(15,23,42,.72);display:flex;align-items:center;justify-content:center;padding:16px";
    ov.innerHTML = '<div style="background:linear-gradient(180deg,#f8fafc,#e0e7ff);border-radius:16px;max-width:920px;width:100%;max-height:92vh;overflow:auto;padding:16px;color:#0f172a;box-shadow:0 24px 60px rgba(0,0,0,.5)">' +
        '<div style="display:flex;justify-content:space-between;align-items:center"><b style="font-size:16px">Ruang Debat \u2014 zoom in</b><button id="debateZoomClose" type="button" style="background:none;border:1px solid rgba(0,0,0,.2);border-radius:8px;padding:4px 10px;cursor:pointer;color:#0f172a">\u2715 Tutup</button></div>' +
        '<div style="font-size:11px;opacity:.7;margin-top:2px">Debat dihitung dari data live kantor, bukan panggilan model berbayar.</div>' +
        '<svg viewBox="0 0 900 420" style="width:100%;height:auto;display:block;margin-top:10px" role="img" aria-label="Robot pendebat berhadapan di depan layar data">' +
        '<defs><linearGradient id="dbg" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#f1f5f9"/><stop offset="1" stop-color="#dbeafe"/></linearGradient></defs>' +
        '<rect x="0" y="0" width="900" height="420" rx="12" fill="url(#dbg)"/>' +
        '<rect x="0" y="330" width="900" height="90" fill="#cbd5e1" opacity=".6"/>' +
        '<rect x="290" y="28" width="320" height="215" rx="12" fill="#0f172a"/>' +
        '<text x="450" y="52" font-size="13" fill="#e2e8f0" text-anchor="middle" font-weight="700">Layar data live</text>' +
        bars +
        '<text x="450" y="214" font-size="11" fill="#cbd5e1" text-anchor="middle">Total 6 venue per venue (Rp) \u00b7 ' + esc(fmtRp(t.sum || 0)) + ' \u00b7 belum terealisasi ' + esc(fmtSigned(t.unrealized || 0)) + '</text>' +
        '<text x="450" y="232" font-size="11" fill="#fbbf24" text-anchor="middle">' + (w ? esc("Posisi terdebat: " + w.sym + " " + fmtSigned(w.idr) + " (" + w.pct.toFixed(1) + "%)") : "Tidak ada posisi terbuka") + '</text>' +
        _debateRobotSVG(170, 180, "#22c55e") +
        _debateRobotSVG(700, 180, "#e0524d") +
        '<rect x="330" y="300" width="240" height="14" rx="7" fill="#94a3b8"/>' +
        '<rect x="360" y="314" width="12" height="30" fill="#64748b"/><rect x="528" y="314" width="12" height="30" fill="#64748b"/>' +
        '<text x="170" y="320" font-size="12" fill="#0f172a" text-anchor="middle" font-weight="700">PRO (bull)</text>' +
        '<text x="700" y="320" font-size="12" fill="#0f172a" text-anchor="middle" font-weight="700">KONTRA (bear)</text>' +
        '</svg>' +
        '<div style="display:grid;grid-template-columns:1fr 1fr;gap:8px;margin-top:10px">' +
        '<div style="background:#ecfdf5;border:1px solid #86efac;border-radius:10px;padding:10px"><b style="color:#15803d">PRO \u2014 Peramal</b><div style="font-size:12px;margin-top:4px">' + esc((w ? (w.sym + " bisa balik ke entry bila momentum membaik; jarak ke TP masih terbuka.") : "Tidak ada posisi untuk diperdebatkan.")) + '</div></div>' +
        '<div style="background:#fef2f2;border:1px solid #fca5a5;border-radius:10px;padding:10px"><b style="color:#b91c1c">KONTRA \u2014 Sinyal Jaringan</b><div style="font-size:12px;margin-top:4px">' + esc((w ? (w.sym + " " + Math.abs(w.pct).toFixed(0) + "% di bawah entry; risiko lanjut turun bila tidak ada katalis.") : "Tidak ada posisi untuk diperdebatkan.")) + '</div></div></div>' +
        '<div style="font-size:12px;margin-top:10px">Debat berjalan: ' + esc(_debateArgs()[0].text) + '</div></div>';
    document.body.appendChild(ov);
    document.getElementById("debateZoomClose").addEventListener("click", function () { ov.remove(); });
    ov.addEventListener("click", function (e) { if (e.target === ov) ov.remove(); });
}


function _sym(p) { var s = String(p.symbol || p.pair_id || "?").toUpperCase(); return s.replace(/USDT$/, "").replace(/IDR$/, ""); }
function _entryPrice(p, k) {
    if (p.entry_price != null) return p.entry_price;
    if (p.entry != null) return p.entry;
    if (p.entry_idr != null && p.qty) {
        var idr = p.entry_idr / p.qty;
        if (k === "indodax") return idr;
        var rate = (window.__liveRaw && window.__liveRaw.venues && window.__liveRaw.venues.pluang && window.__liveRaw.venues.pluang.usd_idr) || 18200;
        return idr / rate;
    }
    return null;
}
function _anaAdvice() {
    var raw = window.__liveRaw;
    var out = [];
    if (!raw || !raw.venues) return out;
    Object.keys(raw.venues).forEach(function (k) {
        var v = raw.venues[k];
        var disp = (VENUES[k.toUpperCase()] ? VENUES[k.toUpperCase()].display : k);
        var re = (v.realized_idr != null) ? v.realized_idr : null;
        var un = (v.unrealized_idr != null) ? v.unrealized_idr : 0;
        (v.positions || []).forEach(function (p) {
            var sym = _sym(p);
            var pct = (p.unrealized_pct != null) ? p.unrealized_pct : 0;
            var lines = [];
            if (sym === "FLOAT") lines.push("Saran: biarkan dulu (keputusan user 13 Nov). Risiko: di bawah min order MEXC $1 \u2014 tidak bisa dijual sampai harga \u2265 $0,008227 (1/121,55 koin).");
            else if (pct < -20) lines.push("Kritik: posisi turun " + Math.abs(pct).toFixed(0) + "% dari entry \u2014 cek SL/KS, jangan tambah posisi sebelum ada pembalikan.");
            else if (pct > 5) lines.push("Pendapat: posisi untung " + pct.toFixed(1) + "% \u2014 pertimbangkan ambil sebagian di TP bila tercapai.");
            else lines.push("Pendapat: posisi bergerak " + pct.toFixed(1) + "% dari entry \u2014 masih dalam jarak wajar; pantau TP/SL.");
            var tp = (k === "indodax" || k === "mexc") ? "+15%" : (k === "pluang" ? "+12%" : "+150%");
            var sl = (k === "indodax" || k === "mexc") ? "\u221230%" : (k === "pluang" ? "\u22125%" : "\u221235%");
            lines.push("Jarak ke target (bukan prediksi): TP " + tp + " / SL " + sl + " dari entry; harga sekarang " + _fmtLivePrice(p.price, k) + ".");
            out.push({ title: sym + " \u00b7 " + disp, lines: lines, src: "Harga: " + (k === "indodax" ? "Indodax" : k === "mexc" ? "MEXC" : k === "pluang" ? "Pluang" : "status.json") + " \u00b7 status: tools.json" });
        });
        if (!(v.positions || []).length) out.push({ title: disp, lines: ["Tidak ada posisi terbuka. Terealisasi " + (re != null ? fmtSigned(re) : "tidak tercatat") + "; belum terealisasi " + fmtSigned(un) + "."], src: "status.json" });
    });
    return out;
}
function _donutSVG(parts, title) {
    var total = 0;
    parts.forEach(function (p) { total += Math.abs(p.val); });
    if (total <= 0) return '<div style="font-size:12px;opacity:.7">' + esc(title) + ': tidak ada data.</div>';
    var r = 34, cx = 50, cy = 50, off = 0;
    var cols = ["#22c55e", "#e0524d", "#38bdf8", "#f59e0b", "#a855f7", "#ec4899"];
    var segs = [];
    parts.forEach(function (p, i) {
        var frac = Math.abs(p.val) / total;
        var a0 = off * 2 * Math.PI - Math.PI / 2, a1 = (off + frac) * 2 * Math.PI - Math.PI / 2;
        var large = frac > 0.5 ? 1 : 0;
        var x0 = cx + r * Math.cos(a0), y0 = cy + r * Math.sin(a0), x1 = cx + r * Math.cos(a1), y1 = cy + r * Math.sin(a1);
        segs.push('<path d="M ' + cx + ' ' + cy + ' L ' + x0.toFixed(1) + ' ' + y0.toFixed(1) + ' A ' + r + ' ' + r + ' 0 ' + large + ' 1 ' + x1.toFixed(1) + ' ' + y1.toFixed(1) + ' Z" fill="' + cols[i % cols.length] + '"/>');
        off += frac;
    });
    var legend = parts.map(function (p, i) {
        return '<div style="display:flex;justify-content:space-between;gap:8px;font-size:11.5px"><span><span style="display:inline-block;width:9px;height:9px;border-radius:2px;background:' + cols[i % cols.length] + ';margin-right:5px"></span>' + esc(p.label) + '</span><b>' + esc(p.txt) + '</b></div>';
    }).join("");
    return '<div><b style="font-size:12.5px">' + esc(title) + '</b><div style="display:flex;gap:10px;align-items:center;margin-top:6px"><svg viewBox="0 0 100 100" style="width:92px;height:92px;flex:0 0 auto">' + segs.join("") + '<circle cx="50" cy="50" r="20" fill="#0f172a"/></svg><div style="flex:1">' + legend + '</div></div></div>';
}
function _anaExtraHost() {
    var f = document.querySelector(".ana-feed");
    if (f) return f.closest("section") || f.parentElement;
    return document.querySelector("#analytics") || document.querySelector(".ana-panel");
}


function _analyticsExtras() {
    var host = _anaExtraHost();
    if (!host) return;
    var anchor = document.getElementById("anaExtras");
    if (!anchor || !host.contains(anchor)) {
        anchor = document.createElement("div");
        anchor.id = "anaExtras";
        host.appendChild(anchor);
    }
    var adv = _anaAdvice();
    var t = _anaTotals();
    var raw = window.__liveRaw;
    var modal = _modalTotal();
    var split = VENUE_ORDER.map(function (k) { return { label: VENUES[k].display, val: (VENUES[k].totalNum || 0), txt: fmtRp(VENUES[k].totalNum || 0) }; });
    var plParts = [];
    VENUE_ORDER.forEach(function (k) {
        var v = VENUES[k];
        var tot = (v.plNum || 0) + (v.unrealizedNum || 0);
        if (tot >= 0) plParts.push({ label: v.display + " (untung)", val: tot, txt: fmtSigned(tot) });
        else plParts.push({ label: v.display + " (rugi)", val: -tot, txt: fmtSigned(tot) });
    });
    var rows = [];
    if (raw && raw.venues) {
        Object.keys(raw.venues).forEach(function (k) {
            (raw.venues[k].positions || []).forEach(function (p) {
                rows.push({ sym: _sym(p), venue: (VENUES[k.toUpperCase()] ? VENUES[k.toUpperCase()].display : k), price: _fmtLivePrice(p.price, k), entry: _fmtLivePrice(_entryPrice(p, k), k), pct: p.unrealized_pct, k: k });
            });
        });
    }
    var trades = (raw && raw.venues) ? Object.keys(raw.venues).map(function (k) { return (VENUES[k.toUpperCase()] ? VENUES[k.toUpperCase()].display : k) + " " + (raw.venues[k].trades_count != null ? raw.venues[k].trades_count : "\u2014"); }).join(" \u00b7 ") : "\u2014";
    anchor.innerHTML = '<div style="border:1px solid rgba(255,255,255,.12);border-radius:12px;padding:12px;margin-top:6px"><b style="font-size:14px">Saran &amp; Analisis</b><div style="font-size:11px;opacity:.65;margin:2px 0 8px">Dihitung dari data live (harga sekarang vs entry, jarak ke TP/SL/KS, realized, kas). 170 alat adalah sumber data; analisis dihitung dari data mereka \u2014 bukan 170 opini AI terpisah.</div>' +
        adv.map(function (a) {
            return '<div style="margin-top:8px;border-top:1px solid rgba(255,255,255,.08);padding-top:8px"><b>' + esc(a.title) + '</b>' + a.lines.map(function (l) { return '<div style="font-size:12px;margin-top:3px">' + esc(l) + '</div>'; }).join("") + '<div style="font-size:10.5px;opacity:.55;margin-top:3px">Sumber: ' + esc(a.src) + '</div></div>';
        }).join("") + '</div>' +
        '<div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(240px,1fr));gap:12px;margin-top:12px">' +
        '<div style="border:1px solid rgba(255,255,255,.12);border-radius:12px;padding:12px">' + _donutSVG(split, "Pembagian aset per venue (harga sekarang)") + '</div>' +
        '<div style="border:1px solid rgba(255,255,255,.12);border-radius:12px;padding:12px">' + _donutSVG(plParts.filter(function (p) { return p.val > 0; }), "Untung vs rugi (realized + belum terealisasi)") + '</div>' +
        '<div style="border:1px solid rgba(255,255,255,.12);border-radius:12px;padding:12px"><b style="font-size:12.5px">Pembelian vs penjualan</b><div style="font-size:12px;margin-top:6px">Trades tercatat: ' + esc(trades) + '. Rincian beli/jual per trade tidak tersedia di state \u2014 ditampilkan apa adanya.</div><div style="font-size:12px;margin-top:6px">Modal vs nilai sekarang: modal ' + (modal != null ? fmtRp(modal) : "\u2014") + ' \u00b7 nilai sekarang ' + fmtRp(t.sum || 0) + ' \u00b7 selisih ' + fmtSigned((t.sum || 0) - (modal || 0)) + '.</div></div></div>' +
        '<div style="border:1px solid rgba(255,255,255,.12);border-radius:12px;padding:12px;margin-top:12px"><b style="font-size:13px">Per aset \u2014 harga, entry, jarak ke target</b><div style="font-size:11px;opacity:.65">Label "jarak ke target", bukan "prediksi" \u2014 halaman tidak meramal harga.</div><table style="width:100%;border-collapse:collapse;font-size:12px;margin-top:6px"><thead><tr style="opacity:.7;text-align:left"><th style="padding:4px 8px">Aset</th><th style="padding:4px 8px">Harga</th><th style="padding:4px 8px">Entry</th><th style="padding:4px 8px">Dari entry</th><th style="padding:4px 8px">Jarak ke target (TP/SL)</th></tr></thead><tbody>' +
        (rows.length ? rows.map(function (r) {
            var tp = (r.k === "indodax" || r.k === "mexc") ? "+15% / \u221230%" : (r.k === "pluang" ? "+12% / \u22125%" : "+150% / \u221235%");
            return '<tr style="border-top:1px solid rgba(255,255,255,.08)"><td style="padding:5px 8px"><b>' + esc(r.sym) + '</b><div style="font-size:10.5px;opacity:.6">' + esc(r.venue) + '</div></td><td style="padding:5px 8px">' + esc(r.price) + '</td><td style="padding:5px 8px">' + esc(r.entry) + '</td><td style="padding:5px 8px;color:' + ((r.pct || 0) < 0 ? "#e0524d" : "#2ea36b") + '">' + ((r.pct || 0) > 0 ? "+" : "") + (r.pct != null ? r.pct.toFixed(2) + "%" : "\u2014") + '</td><td style="padding:5px 8px">' + esc(tp) + '</td></tr>';
        }).join("") : '<tr><td colspan="5" style="padding:8px;opacity:.7">Tidak ada posisi terbuka.</td></tr>') + '</tbody></table></div>';
}
if (typeof renderAnalytics === "function" && !renderAnalytics.__p14) {
    var _renderAnalytics0 = renderAnalytics;
    renderAnalytics = function () {
        var r = _renderAnalytics0();
        try { _analyticsExtras(); } catch (e) {}
        return r;
    };
    renderAnalytics.__p14 = true;
}


var _p14css = document.createElement("style");
_p14css.textContent = [
    ".agent-tag .agent-tag-name{display:inline !important}",
    ".scene.is-zoomed .agent-tag .agent-tag-name{display:inline !important;font-size:9px !important}",
    ".agent-tags.is-dense .agent-tag .agent-tag-name{font-size:9px !important}",
    "body.is-fs .topbar,body.is-fs .tabstrip,body.is-fs .nav-rail,body.is-fs .dock-wrap,body.is-fs .chat-fab{display:flex !important;position:relative;z-index:60}",
    "body.is-fs #newsTicker{display:flex !important;position:relative;z-index:60}",
    ".agent-tag{transition:transform 1.4s ease,opacity .4s ease}"
].join("\n");
document.head.appendChild(_p14css);
function _deskRobotSVG(accent) {
    return '<svg viewBox="0 0 220 190" style="width:100%;max-width:220px;height:auto;display:block;margin:0 auto" role="img" aria-label="Robot putih di meja kerja">' +
        '<rect x="8" y="150" width="204" height="10" rx="5" fill="#94a3b8"/>' +
        '<rect x="26" y="160" width="10" height="26" fill="#64748b"/><rect x="184" y="160" width="10" height="26" fill="#64748b"/>' +
        '<rect x="120" y="96" width="72" height="52" rx="6" fill="#0f172a"/>' +
        '<rect x="126" y="102" width="60" height="34" rx="3" fill="#1e293b"/>' +
        '<polyline points="132,132 142,118 152,128 162,112 172,124 180,116" fill="none" stroke="#22c55e" stroke-width="2"/>' +
        '<rect x="132" y="140" width="48" height="5" rx="2" fill="#334155"/>' +
        '<rect x="58" y="104" width="46" height="46" rx="12" fill="#ffffff" stroke="' + accent + '" stroke-width="2.5"/>' +
        '<circle cx="81" cy="78" r="24" fill="#ffffff" stroke="' + accent + '" stroke-width="2.5"/>' +
        '<circle cx="73" cy="76" r="3.5" fill="#0f172a"/><circle cx="89" cy="76" r="3.5" fill="#0f172a"/>' +
        '<rect x="71" y="86" width="20" height="3" rx="1.5" fill="' + accent + '"/>' +
        '<line x1="81" y1="54" x2="81" y2="44" stroke="' + accent + '" stroke-width="2.5"/><circle cx="81" cy="41" r="4.5" fill="' + accent + '"/>' +
        '<rect x="46" y="112" width="10" height="24" rx="5" fill="#ffffff" stroke="' + accent + '" stroke-width="2"/>' +
        '<rect x="106" y="112" width="10" height="24" rx="5" fill="#ffffff" stroke="' + accent + '" stroke-width="2"/>' +
        '<text x="110" y="20" font-size="12" fill="#475569" text-anchor="middle">Meja kerja robot</text></svg>';
}
function _deskWork(a) {
    var raw = window.__liveRaw;
    var hay = ((a.name || "") + " " + (a.role || "") + " " + (a.cat || a.category || "")).toLowerCase();
    var out = [];
    if (/crypto|coin|dex|gecko|terminal|mexc|indodax|pump|four|clanker|pluang|binance|market/i.test(hay) && raw && raw.venues) {
        var w = _worstPos();
        if (w) out.push("Fokus: " + w.sym + " " + fmtSigned(w.idr) + " (" + w.pct.toFixed(1) + "% dari entry).");
        var t = _anaTotals();
        out.push("Total kantor: " + fmtRp(t.sum || 0) + " \u00b7 belum terealisasi " + fmtSigned(t.unrealized || 0) + ".");
    }
    if (/berita|news|sosmed|sentimen/i.test(hay)) {
        var news = (raw && raw.news) || [];
        out.push(news.length ? ("Berita terbaru: " + news[0].title) : "Belum ada berita di ticker.");
        if (news[1]) out.push("Juga: " + news[1].title);
    }
    var tasks = (state.items || []).filter(function (i) { return i.agent === a.id; });
    if (tasks.length) out.push("Tugas: " + tasks.map(function (i) { return i.title; }).join(" \u00b7 "));
    if (!out.length) out.push("Data yang sedang dikerjakan: " + (a.role || a.func || a.desc || a.tool || "\u2014") + ". Status alat: " + (a.toolFinal || "") + (a.toolRaw ? " (" + a.toolRaw + ")" : "") + ".");
    return out;
}
function _deskDetail(a) {
    if (!a) return;
    var old = document.getElementById("deskDetail");
    if (old) old.remove();
    var zone = (C.zones || []).filter(function (z) { return z.id === a.zone; })[0];
    var work = _deskWork(a);
    var el = document.createElement("div");
    el.id = "deskDetail";
    el.style.cssText = "position:fixed;inset:0;z-index:96;background:rgba(15,23,42,.55);display:flex;align-items:center;justify-content:center;padding:16px";
    el.innerHTML = '<div style="background:linear-gradient(180deg,#ffffff,#e0e7ff);border-radius:18px;max-width:560px;width:100%;max-height:92vh;overflow:auto;padding:18px;color:#0f172a;box-shadow:0 24px 60px rgba(0,0,0,.45)">' +
        '<div style="display:flex;justify-content:space-between;align-items:flex-start"><div><div style="font-size:11px;letter-spacing:.08em;color:#64748b">DETAIL ROBOT \u00b7 ZOOM IN</div><b style="font-size:19px">' + esc(a.name) + '</b><div style="font-size:12px;color:#475569">' + esc(a.role || "") + ' \u00b7 Ruangan: ' + esc(zone ? zone.title : "\u2014") + '</div></div><button id="deskClose" type="button" style="background:none;border:1px solid rgba(0,0,0,.2);border-radius:8px;padding:4px 10px;cursor:pointer;color:#0f172a">\u2715</button></div>' +
        '<div style="display:flex;gap:14px;align-items:center;margin-top:10px;flex-wrap:wrap"><div style="flex:0 0 220px">' + _deskRobotSVG(a.color || "#38bdf8") + '</div>' +
        '<div style="flex:1;min-width:200px"><div style="display:flex;gap:8px;align-items:center"><span style="display:inline-flex;width:34px;height:34px;border-radius:8px;background:#fff;border:1px solid #e2e8f0;align-items:center;justify-content:center;overflow:hidden">' + _brandImg(a, 64) + '</span><span style="font-size:12px;color:#475569">Logo merek alat (fallback avatar bila favicon tidak ada)</span></div>' +
        '<div style="margin-top:10px;font-size:12.5px"><b>Status live:</b> ' + esc(a.status || "") + ' \u00b7 ' + esc(a.toolFinal || "") + (a.toolRaw ? ' (' + esc(a.toolRaw) + ')' : '') + '</div>' +
        '<div style="margin-top:6px;font-size:12.5px"><b>Fungsi:</b> ' + esc(a.func || a.desc || a.role || "\u2014") + '</div></div></div>' +
        '<div style="margin-top:12px;background:#0f172a;border-radius:12px;padding:12px;color:#e2e8f0"><b style="font-size:12px;color:#38bdf8">LAYAR DATA \u2014 yang sedang dikerjakan</b>' + work.map(function (w2) { return '<div style="font-size:12.5px;margin-top:5px">\u00b7 ' + esc(w2) + '</div>'; }).join("") + '</div>' +
        '<div style="font-size:11px;opacity:.65;margin-top:8px">Detail tiap robot dihitung dari datanya sendiri (tools.json + status.json live).</div></div>';
    document.body.appendChild(el);
    document.getElementById("deskClose").addEventListener("click", function () { el.remove(); });
    el.addEventListener("click", function (e) { if (e.target === el) el.remove(); });
}


function _swapDetailAvatar(a) {
    try {
        var heads = document.querySelectorAll(".detail-name, .detail-title, h2, h3");
        var panel = null;
        heads.forEach(function (h) { if (!panel && (h.textContent || "").indexOf(a.name) >= 0) panel = h.closest("section") || h.parentElement; });
        if (!panel) return;
        var av = panel.querySelector("[class*='avatar'], [class*='ac-av'], [class*='robot-av'], [class*='detail-av']");
        if (!av) return;
        if (av.closest("#deskDetail") || av.closest(".chat-panel")) return;
        av.innerHTML = _brandImg(a, 64);
    } catch (e) {}
}
if (typeof selectAgent === "function" && !selectAgent.__p14) {
    var _selectAgent0 = selectAgent;
    selectAgent = function (id) {
        var r = _selectAgent0(id);
        try {
            var a = (C.agents || []).filter(function (x) { return String(x.id) === String(id); })[0];
            if (a) { _deskDetail(a); setTimeout(function () { _swapDetailAvatar(a); }, 150); }
        } catch (e) {}
        return r;
    };
    selectAgent.__p14 = true;
}
if (typeof zoomTo === "function" && !zoomTo.__p14desk) {
    var _zoomToDesk = zoomTo;
    zoomTo = function (z) {
        var r = _zoomToDesk(z);
        try {
            var target = Math.max(0.4, Math.min(2.0, z));
            if (target >= 1.5 && !document.getElementById("deskDetail")) {
                var scene = document.querySelector(".scene");
                if (scene) {
                    var sr = scene.getBoundingClientRect();
                    var cx = sr.left + sr.width / 2, cy = sr.top + sr.height / 2;
                    var best = null, bestD = 170;
                    document.querySelectorAll(".agent-tag").forEach(function (tg) {
                        var q = tg.getBoundingClientRect();
                        var d = Math.hypot(q.left + q.width / 2 - cx, q.top + q.height / 2 - cy);
                        if (d < bestD) { bestD = d; best = tg; }
                    });
                    if (best) {
                        var nm = (best.textContent || "").trim();
                        var a = (C.agents || []).filter(function (x) { return x.name === nm; })[0];
                        if (a) _deskDetail(a);
                    }
                }
            }
        } catch (e) {}
        return r;
    };
    zoomTo.__p14desk = true;
}
document.addEventListener("click", function (e) {
    var tg = e.target && e.target.closest ? e.target.closest(".agent-tag") : null;
    if (!tg) return;
    var nm = (tg.textContent || "").trim();
    var a = (C.agents || []).filter(function (x) { return x.name === nm; })[0];
    if (a) { try { selectAgent(a.id); } catch (err) {} }
});
function _fsChatSync() {
    if (!document.body.classList.contains("is-fs")) return;
    var p = document.querySelector(".chat-panel");
    if (!p) return;
    var open = (p.className || "").match(/open|show|active/i) || (p.style.display && p.style.display !== "none") || (document.body.className || "").match(/chat-open|chat-show/i);
    if (open) p.style.setProperty("display", "flex", "important");
    else p.style.removeProperty("display");
}
document.addEventListener("fullscreenchange", function () { setTimeout(_fsChatSync, 300); });
setInterval(_fsChatSync, 800);


// ---- 11c: bottom strip as index strip (item 30) ----
function _venueModal(k) {
  var raw = window.__liveRaw;
  if (!raw || !raw[k]) return null;
  var d = raw[k];
  if (d.total_deposited_idr != null && isFinite(d.total_deposited_idr)) return d.total_deposited_idr;
  if (d.deposit_baseline_idr != null && isFinite(d.deposit_baseline_idr)) return d.deposit_baseline_idr;
  return null;
}
function _dockRestyle() {
  var dockEl = $("#dock");
  if (!dockEl) return;
  var hasTotal = false;
  VENUE_ORDER.forEach(function(k){ var v = VENUES[k]; if (v && v.totalNum != null && isFinite(v.totalNum)) hasTotal = true; });
  if (!hasTotal) return;
  var nodes = [];
  Array.prototype.slice.call(dockEl.querySelectorAll(".chip, .board-empty")).forEach(function(n){ nodes.push(n); });
  var cards = [];
  VENUE_ORDER.forEach(function(k){
    var v = VENUES[k];
    if (!v) return;
    var pl = _venuePl(k);
    var modal = _venueModal(k);
    var base = modal;
    if (base == null || !(base > 0)) base = (v.totalNum || 0) - pl;
    var pct = (base > 0) ? (pl / base * 100) : null;
    cards.push({ k: k, name: v.display || k, total: v.totalNum || 0, pl: pl, pct: pct });
  });
  cards.sort(function(a, b){
    var pa = (a.pct == null ? -1e9 : a.pct), pb = (b.pct == null ? -1e9 : b.pct);
    return pb - pa;
  });
  var html = "<div class=\"dock-idx\" role=\"list\" aria-label=\"Indeks venue live, urut dari yang paling naik\">" + cards.map(function(c){
    var dir = (c.pct == null) ? "\u2014" : ((c.pct >= 0 ? "\u25B2 +" : "\u25BC \u2212") + Math.abs(c.pct).toFixed(2) + "%");
    var cls = (c.pct == null) ? "is-zero" : (c.pct >= 0 ? "is-pos" : "is-neg");
    return "<button type=\"button\" class=\"dock-idx-card\" data-venue=\"" + esc(c.k) + "\" role=\"listitem\" title=\"" + esc(c.name) + " \u2014 total vs modal\">" +
      "<span class=\"dock-idx-name\">" + esc(c.name) + "</span>" +
      "<span class=\"dock-idx-num\">" + esc(fmtRp(c.total)) + "</span>" +
      "<span class=\"dock-idx-chip " + cls + "\">" + esc(dir) + "</span></button>";
  }).join("") + "</div><div class=\"dock-div\" aria-hidden=\"true\"></div><div class=\"dock-chips\"></div>";
  dockEl.innerHTML = html;
  var chipsBox = dockEl.querySelector(".dock-chips");
  nodes.forEach(function(n){ chipsBox.appendChild(n); });
  $$(".dock-idx-card", dockEl).forEach(function(b){
    b.addEventListener("click", function(){ selectVenue(b.getAttribute("data-venue")); });
  });
}
var _p14cssDock = document.createElement("style");
_p14cssDock.textContent = "#dock{display:flex!important;align-items:stretch;gap:8px;}" +
".dock-idx{display:flex;gap:8px;overflow-x:auto;flex:0 1 auto;align-items:stretch;padding:2px;scrollbar-width:thin;}" +
".dock-div{width:1px;background:rgba(140,155,175,.45);margin:4px 2px;flex:0 0 auto;}" +
".dock-chips{display:flex;gap:6px;overflow-x:auto;flex:1 1 auto;align-items:center;padding:2px;min-width:0;}" +
".dock-idx-card{min-width:124px;flex:0 0 auto;display:flex;flex-direction:column;align-items:flex-start;gap:1px;background:#fff;border:1px solid rgba(226,229,235,.95);border-radius:10px;padding:6px 10px;cursor:pointer;text-align:left;box-shadow:0 2px 8px rgba(16,24,40,.08);}" +
".dock-idx-name{font-size:11px;font-weight:700;color:#374151;letter-spacing:.02em;}" +
".dock-idx-num{font-size:15px;font-weight:800;color:#111827;line-height:1.2;}" +
".dock-idx-chip{font-size:11px;font-weight:700;padding:1px 6px;border-radius:999px;}" +
".dock-idx-chip.is-pos{color:#15803d;background:#dcfce7;}" +
".dock-idx-chip.is-neg{color:#b91c1c;background:#fee2e2;}" +
".dock-idx-chip.is-zero{color:#6b7280;background:#f3f4f6;}" +
"@media (max-width:640px){.dock-idx-card{min-width:106px;padding:5px 8px;}.dock-idx-num{font-size:13px;}}";
document.head.appendChild(_p14cssDock);
if (typeof renderDock === "function" && !renderDock.__p14d) {
  var __rd = renderDock;
  renderDock = function(){ __rd(); _dockRestyle(); };
  renderDock.__p14d = true;
}

// ---- 11d: corner buttons in one neat row, tooltips above (item 31) ----
function _cornerRow() {
  var chat = $("#chatFab"), fs = $("#fsBtnStage"), zc = $("#zoomCtl");
  if (!chat || !fs) return;
  var dock = $("#cornerDock");
  if (!dock) {
    dock = document.createElement("div");
    dock.id = "cornerDock";
    (chat.parentNode || document.body).appendChild(dock);
  }
  if (chat.parentNode !== dock) dock.appendChild(chat);
  if (fs.parentNode !== dock) dock.appendChild(fs);
  [chat, fs].forEach(function(b){
    var t = b.getAttribute("title");
    if (t) { b.setAttribute("data-tip", t); b.removeAttribute("title"); }
  });
  Array.prototype.slice.call(chat.querySelectorAll("[title]")).forEach(function(l){
    l.setAttribute("data-tip", l.getAttribute("title"));
    l.removeAttribute("title");
  });
  if (zc) Array.prototype.slice.call(zc.querySelectorAll("[title]")).forEach(function(l){
    l.setAttribute("data-tip", l.getAttribute("title"));
    l.removeAttribute("title");
  });
  var strip = document.querySelector(".dock-wrap"), tick = $("#newsTicker");
  var base = 10;
  if (strip) base += (strip.getBoundingClientRect().height || 56);
  if (tick && tick.offsetParent !== null) base += (tick.getBoundingClientRect().height || 28);
  dock.style.bottom = base + "px";
  if (zc) {
    zc.style.position = "fixed";
    zc.style.right = "12px";
    var dh = dock.offsetHeight || 44;
    zc.style.bottom = (base + dh + 12) + "px";
  }
}
var _p14cssCorner = document.createElement("style");
_p14cssCorner.textContent = "#cornerDock{position:fixed;right:12px;z-index:90;display:flex;align-items:center;gap:10px;}" +
"#cornerDock .chat-fab,#cornerDock .yt-fs-btn{position:static!important;left:auto!important;right:auto!important;top:auto!important;bottom:auto!important;margin:0!important;flex:0 0 auto;}" +
"#cornerDock [data-tip]{position:relative;}" +
"#cornerDock [data-tip]::after{content:attr(data-tip);position:absolute;left:50%;bottom:calc(100% + 8px);transform:translateX(-50%);background:rgba(17,24,39,.95);color:#fff;font-size:11px;line-height:1.2;padding:6px 8px;border-radius:6px;white-space:nowrap;pointer-events:none;opacity:0;transition:opacity .15s;z-index:5;}" +
"#cornerDock [data-tip]:hover::after,#cornerDock [data-tip]:focus-visible::after{opacity:1;}" +
"#zoomCtl [data-tip]{position:relative;}" +
"#zoomCtl [data-tip]::after{content:attr(data-tip);position:absolute;right:calc(100% + 8px);top:50%;transform:translateY(-50%);background:rgba(17,24,39,.95);color:#fff;font-size:11px;line-height:1.2;padding:6px 8px;border-radius:6px;white-space:nowrap;pointer-events:none;opacity:0;transition:opacity .15s;z-index:5;}" +
"#zoomCtl [data-tip]:hover::after,#zoomCtl [data-tip]:focus-visible::after{opacity:1;}" +
"body.is-fs #cornerDock{display:flex!important;}" +
"@media (max-width:640px){#cornerDock{right:8px;gap:8px;}}";
document.head.appendChild(_p14cssCorner);
window.addEventListener("resize", _cornerRow);
document.addEventListener("fullscreenchange", function(){ setTimeout(_cornerRow, 300); });

// ---- 11e: Bengkel AI, Notifikasi robot, panel Update (items 32-34) ----
function _tpSlOf(k) {
  if (k === "pluang") return { tp: 12, sl: -5 };
  if (k === "pumpfun" || k === "fourmeme" || k === "clanker") return { tp: 150, sl: -35 };
  return { tp: 15, sl: -30 };
}
function _notifFeed() {
  var raw = window.__liveRaw;
  var out = [];
  if (!raw) return out;
  var worst = null, worstPct = 0;
  VENUE_ORDER.forEach(function(k){
    var v = raw[k];
    if (!v || !v.positions) return;
    v.positions.forEach(function(p){
      var sym = _sym(p);
      var up = (p.unrealized_pct != null) ? p.unrealized_pct : null;
      if (up != null && up < worstPct) { worstPct = up; worst = { sym: sym, venue: k, pct: up }; }
      if (up != null) {
        var ts = _tpSlOf(k);
        if (up >= ts.tp - 5) out.push({ t: "tp", urgent: true, title: sym + " mendekati TP (+" + ts.tp + "%)", detail: "Sekarang " + up.toFixed(1) + "% dari entry di " + (VENUES[k] ? VENUES[k].display : k) + " \u2014 TP +" + ts.tp + "%." });
        else if (up <= ts.sl + 5) out.push({ t: "sl", urgent: true, title: sym + " mendekati SL (" + ts.sl + "%)", detail: "Sekarang " + up.toFixed(1) + "% dari entry di " + (VENUES[k] ? VENUES[k].display : k) + " \u2014 SL " + ts.sl + "%; batas rugi tidak dilonggarkan." });
      }
      if (sym === "FLOAT" && p.price != null && p.price < 0.008227) out.push({ t: "loop", urgent: true, title: "FLOAT di bawah min order MEXC $1", detail: "Harga $" + p.price.toFixed(6) + " \u2014 tidak bisa dijual sampai harga \u2265 $0,008227 (keputusan user 13 Nov: biarkan dulu)." });
    });
    var tc = v.trades_count;
    var prev = (window.__prevTrades || {})[k];
    if (tc != null && prev != null && tc > prev) out.push({ t: "trade", urgent: false, title: "Trade baru di " + (VENUES[k] ? VENUES[k].display : k), detail: tc + " trade tercatat (sebelumnya " + prev + ")." });
  });
  if (!window.__prevTrades) window.__prevTrades = {};
  VENUE_ORDER.forEach(function(k){ var v = raw[k]; if (v && v.trades_count != null) window.__prevTrades[k] = v.trades_count; });
  if (worst) out.push({ t: "loop", urgent: false, title: "Posisi paling rugi: " + worst.sym + " " + worst.pct.toFixed(1) + "%", detail: "Di " + (VENUES[worst.venue] ? VENUES[worst.venue].display : worst.venue) + ". Lihat Saran & Analisis di Analitik." });
  var gen = raw.generated_at || raw.generatedAt || (raw.pluang && raw.pluang.updated);
  out.push({ t: "sync", urgent: false, title: "Status tersinkron dari VPS", detail: "status.json terakhir diperbarui " + (gen ? fmtWIBShort(gen) : "baru saja") + " WIB; harga MEXC/Indodax publik, cache 60 dtk." });
  return out;
}
function _p14overlay(id, title, bodyHtml) {
  var old = document.getElementById(id);
  if (old) { old.remove(); return null; }
  var ovl = document.createElement("div");
  ovl.className = "p14-ovl";
  ovl.id = id;
  ovl.innerHTML = "<div class=\"p14-ovl-card\"><div class=\"p14-ovl-head\"><b>" + esc(title) + "</b><button type=\"button\" class=\"p14-ovl-x\" aria-label=\"Tutup\">\u2715</button></div><div class=\"p14-ovl-body\">" + bodyHtml + "</div></div>";
  ovl.addEventListener("click", function(e){ if (e.target === ovl || e.target.className === "p14-ovl-x") ovl.remove(); });
  document.body.appendChild(ovl);
  return ovl;
}
function _notifPanel() {
  var feed = _notifFeed();
  var urg = feed.filter(function(n){ return n.urgent; }).length;
  var rows = feed.map(function(n){
    var ic = n.t === "trade" ? "\uD83D\uDCE5" : (n.t === "tp" ? "\uD83C\uDFAF" : (n.t === "sl" ? "\u26A0\uFE0F" : (n.t === "loop" ? "\uD83D\uDD27" : "\uD83D\uDD04")));
    return "<div class=\"zone-item\">" + ic + " <b>" + esc(n.title) + "</b>" + (n.urgent ? "<span class=\"p14-badge p14-badge-loop\">URGENT</span>" : "") + "<br><span style=\"color:#64748b\">" + esc(n.detail) + "</span></div>";
  }).join("");
  var note = "<div class=\"p14-note\">Notifikasi dihitung dari status.json live di halaman ini (trade, TP/SL, loop bermasalah, sinkron). Lonceng kantor membuka panel ini. Notifikasi Telegram dikirim cron tg_notify.py tiap 1 menit dari VPS \u2014 isinya tidak bisa dibaca halaman ini.</div>";
  _p14overlay("notifPanel", "Notifikasi \u2014 " + feed.length + " kabar (" + urg + " urgent)", note + rows);
}
function _bengkelDetail() {
  var reps = (window.__repairs && window.__repairs.repairs) || [];
  var rows = reps.slice(0, 10).map(function(r){
    return "<div class=\"zone-item\"><b>" + esc(r.date || "") + "</b> \u2014 " + esc(r.what || "") + "<br><span style=\"color:#64748b\">" + esc(r.result || "") + "</span></div>";
  }).join("") || "<div class=\"zone-item\">Log perbaikan belum termuat.</div>";
  var head = "<div class=\"p14-note\"><b>Bengkel AI</b> \u2014 robot engineering/perbaikan kantor. Tugasnya memperbaiki semuanya: status, harga, tampilan, dan loop. Log di bawah sama dengan panel Riwayat Perbaiki (data office/repairs.json).</div>";
  _p14overlay("bengkelDetail", "\uD83D\uDD27 Bengkel AI \u2014 log perbaikan", head + rows + "<div class=\"p14-note\">Lihat riwayat lengkap di menu kiri: Riwayat Perbaiki.</div>");
}
window.__updateFallback = [
  { date: "14 Nov 2026 02:25", type: "fitur baru", what: "Robot Bengkel AI + Robot Notifikasi + panel Update", detail: "Bengkel AI merawat kantor; Notifikasi robot memberi kabar trade/TP/SL; panel Update mencatat semua update." },
  { date: "14 Nov 2026 02:16", type: "perbaikan", what: "Tombol pojok tidak lagi bertumpuk", detail: "Chat + Layar penuh + zoom tersusun rapi berjajar; tooltip tampil di atas tombol." },
  { date: "14 Nov 2026 02:14", type: "fitur baru", what: "Strip bawah gaya indeks", detail: "Kartu venue dengan nilai + % chip, urut dari yang paling naik." },
  { date: "14 Nov 2026 01:36", type: "fitur baru", what: "Ruang Debat di tengah kantor", detail: "6 pendebat, skor akurasi, prediksi menuju target." },
  { date: "13 Nov 2026 08:01", type: "perubahan loop", what: "Latihan 20 jam: strategi terpilih BreakoutTren", detail: "Paper +759% vs Aturan A +605%, Hunter A \u221284% jangan dipakai; filter Fear & Greed ditolak." }
];
function _updatePanel() {
  if (window.__repairsLoad) { try { window.__repairsLoad(); } catch (e) {} }
  var ups = (window.__repairs && window.__repairs.updates && window.__repairs.updates.length) ? window.__repairs.updates : window.__updateFallback;
  var rows = ups.map(function(u){
    var bc = u.type === "perbaikan" ? "p14-badge-fix" : (u.type === "perubahan loop" ? "p14-badge-loop" : "p14-badge-feat");
    return "<div class=\"zone-item\"><b>" + esc(u.date || "") + "</b><span class=\"p14-badge " + bc + "\">" + esc(u.type || "update") + "</span><br><b>" + esc(u.what || "") + "</b><br><span style=\"color:#64748b\">" + esc(u.detail || "") + "</span></div>";
  }).join("");
  _p14overlay("updatePanel", "\uD83D\uDCE3 Update terbaru", "<div class=\"p14-note\">Semua perbaikan, fitur baru, dan perubahan loop tercatat di sini, dari file data office/repairs.json (bagian updates).</div>" + rows);
}
function _updateMenuItem() {
  if (document.querySelector("[data-update-menu]")) return;
  var spans = document.querySelectorAll("span");
  var rp = null;
  for (var i = 0; i < spans.length; i++) { if (spans[i].textContent.trim() === "Riwayat Perbaiki") { rp = spans[i]; break; } }
  if (!rp) return;
  var item = rp.closest("button, a, li, [role=menuitem]");
  if (!item || !item.parentNode) return;
  var clone = item.cloneNode(true);
  clone.removeAttribute("id");
  clone.removeAttribute("data-panel");
  clone.removeAttribute("data-id");
  clone.setAttribute("data-update-menu", "1");
  var sp = clone.querySelector("span");
  if (sp) sp.textContent = "Update";
  clone.addEventListener("click", function(e){ e.preventDefault(); e.stopPropagation(); _updatePanel(); });
  item.parentNode.insertBefore(clone, item.nextSibling);
}
function _specialBots() {
  var scene = document.querySelector(".scene");
  if (!scene) return;
  var box = document.getElementById("specialBots");
  if (box) { _specialBotsBadge(); return; }
  box = document.createElement("div");
  box.className = "special-bots";
  box.id = "specialBots";
  box.innerHTML = "<button type=\"button\" class=\"special-bot\" id=\"botBengkel\"><span class=\"special-bot-av\" style=\"background:#fef3c7\">\uD83D\uDD27</span><span><span class=\"special-bot-name\">Bengkel AI</span><br><span class=\"special-bot-sub\">Engineering \u00B7 perbaikan</span></span></button>" +
    "<button type=\"button\" class=\"special-bot\" id=\"botNotif\"><span class=\"special-bot-av\" style=\"background:#fee2e2\">\uD83D\uDD14</span><span><span class=\"special-bot-name\">Notifikasi</span><br><span class=\"special-bot-sub\">Trade \u00B7 TP/SL \u00B7 sinkron</span></span><span class=\"special-bot-badge\" id=\"notifBadge\">0</span></button>";
  scene.appendChild(box);
  document.getElementById("botBengkel").addEventListener("click", function(){ _bengkelDetail(); });
  document.getElementById("botNotif").addEventListener("click", function(){ _notifPanel(); });
  _specialBotsBadge();
}
function _specialBotsBadge() {
  var b = document.getElementById("notifBadge");
  if (!b) return;
  var feed = _notifFeed();
  var urg = feed.filter(function(n){ return n.urgent; }).length;
  b.textContent = urg;
  b.style.display = (urg > 0) ? "flex" : "none";
}
function _bindBell() {
  var els = document.querySelectorAll("button, [role=button]");
  for (var i = 0; i < els.length; i++) {
    var b = els[i];
    var s = (b.getAttribute("aria-label") || "") + " " + (b.title || "") + " " + (b.textContent || "");
    if (/lonceng|bell|notif|\uD83D\uDD14/i.test(s) && !b.__p14bell) { b.__p14bell = true; b.addEventListener("click", function(){ _notifPanel(); }); }
  }
}
var _p14cssSpecial = document.createElement("style");
_p14cssSpecial.textContent = ".p14-ovl{position:fixed;inset:0;background:rgba(15,23,42,.55);z-index:120;display:flex;align-items:center;justify-content:center;padding:16px;}" +
".p14-ovl-card{background:linear-gradient(180deg,#ffffff,#e0e7ff);color:#111827;border-radius:14px;max-width:560px;width:100%;max-height:86vh;overflow:auto;box-shadow:0 20px 60px rgba(0,0,0,.35);padding:16px 18px;}" +
".p14-ovl-head{display:flex;justify-content:space-between;align-items:center;font-size:16px;margin-bottom:6px;}" +
".p14-ovl-x{border:1px solid #cbd5e1;background:#fff;border-radius:8px;width:30px;height:30px;cursor:pointer;font-size:14px;}" +
".p14-ovl-body{font-size:13px;line-height:1.5;}" +
".p14-badge{display:inline-block;font-size:11px;font-weight:700;padding:1px 7px;border-radius:999px;margin-left:6px;}" +
".p14-badge-fix{background:#dcfce7;color:#15803d;}" +
".p14-badge-feat{background:#dbeafe;color:#1d4ed8;}" +
".p14-badge-loop{background:#fef3c7;color:#92400e;}" +
".p14-note{font-size:12px;color:#475569;background:#f1f5f9;border:1px solid #e2e8f0;border-radius:8px;padding:8px 10px;margin:8px 0;}" +
".special-bots{position:absolute;top:8px;right:8px;z-index:8;display:flex;gap:8px;}" +
".special-bot{display:flex;align-items:center;gap:8px;background:rgba(255,255,255,.94);border:1px solid rgba(226,229,235,.95);border-radius:12px;padding:6px 10px;cursor:pointer;box-shadow:0 4px 14px rgba(16,24,40,.12);font-size:12px;text-align:left;}" +
".special-bot-av{width:30px;height:30px;border-radius:50%;display:flex;align-items:center;justify-content:center;font-size:17px;flex:0 0 auto;}" +
".special-bot-name{font-weight:800;color:#111827;line-height:1.1;}" +
".special-bot-sub{font-size:11px;color:#6b7280;line-height:1.2;}" +
".special-bot-badge{background:#dc2626;color:#fff;font-size:10px;font-weight:800;border-radius:999px;min-width:18px;height:18px;display:flex;align-items:center;justify-content:center;padding:0 4px;}";
document.head.appendChild(_p14cssSpecial);

// ---- 11f: final init + live hook + close (items 30-34) ----
if (!applyLive.__p14c) {
  var __alC = applyLive;
  applyLive = function(d){ var r = __alC(d); try { if (document.querySelector("#debateRoom")) _debateRender(); } catch (e) {} try { _dockRestyle(); } catch (e) {} try { _cornerRow(); } catch (e) {} try { _specialBots(); } catch (e) {} return r; };
  applyLive.__p14c = true;
}
function _p14init() {
  if (window.__p14initDone) return;
  window.__p14initDone = true;
  try { _searchInit(); } catch (e) {}
  try { _repairsLoad(); } catch (e) {}
  try { _renameScheduledMenu(); } catch (e) {}
  try { _seedBoardTasks(); } catch (e) {}
  try {
    var z = JSON.parse(localStorage.getItem("room-zones-v1") || "null");
    if (z) C.agents.forEach(function(a){ if (z[a.id]) a.zone = z[a.id]; });
    var m = JSON.parse(localStorage.getItem("room-moves-v1") || "null");
    if (m) window.__roomLog = m;
  } catch (e) {}
  try { _roomLogRender(); } catch (e) {}
  try { _newsTickerRender(); } catch (e) {}
  try { _marketTableRender(); } catch (e) {}
  try { _dockRestyle(); } catch (e) {}
  try { _cornerRow(); } catch (e) {}
  try { _specialBots(); } catch (e) {}
  try { _updateMenuItem(); } catch (e) {}
  try { _bindBell(); } catch (e) {}
  setInterval(_roomMoveCheck, 60000);
  setTimeout(_roomMoveCheck, 8000);
  setTimeout(_debateRender, 2000);
  setTimeout(_cornerRow, 1200);
  setTimeout(_updateMenuItem, 1500);
}
if (document.readyState === "complete") setTimeout(_p14init, 600);
else {
  window.addEventListener("load", function(){ setTimeout(_p14init, 600); });
  setTimeout(_p14init, 2500);
}

  function _deskZoomHook(z) { try { var target = Math.max(0.4, Math.min(2.0, z)); if (target >= 1.5 && !document.getElementById("deskDetail")) { var sceneEl = document.querySelector(".scene"); if (sceneEl) { var sr = sceneEl.getBoundingClientRect(); var cx = sr.left + sr.width / 2, cy = sr.top + sr.height / 2; var best = null, bestD = 170; document.querySelectorAll(".agent-tag").forEach(function (tg) { var q = tg.getBoundingClientRect(); var d = Math.hypot(q.left + q.width / 2 - cx, q.top + q.height / 2 - cy); if (d < bestD) { bestD = d; best = tg; } }); if (best) { var nm = (best.textContent || "").trim(); var a = (C.agents || []).filter(function (x) { return x.name === nm; })[0]; if (a) _deskDetail(a); } } } } catch (e) {} }
  window.__onZoom = _deskZoomHook;

// FIX1 14 Nov 2026 - clean layout, bot realized total, crypto search, room moves, fullscreen
// FIX2 14 Nov 2026 - brand tabs, analitik counts, room count sync, footer live, ticker dock, dock empty
function _brandImgUrl(a) {
  var d = null;
  try { d = _brandDomain(a); } catch (e) {}
  if (!d) return null;
  return "https://www.google.com/s2/favicons?domain=" + encodeURIComponent(d) + "&sz=64";
}
function _swapDetailAvatarOnce(a) {
  try {
    var heads = document.querySelectorAll(".detail-name, .detail-title, h2, h3");
    var panel = null;
    heads.forEach(function (h) { if (!panel && (h.textContent || "").indexOf(a.name) >= 0) panel = h.closest("section") || h.parentElement; });
    if (!panel) return;
    var av = panel.querySelector("[class*=avatar], [class*=ac-av], [class*=robot-av], [class*=detail-av], [class*=agent-ico], [class*=ap-av]");
    if (!av) {
      var imgs = panel.querySelectorAll("img");
      for (var i = 0; i < imgs.length; i++) {
        var im = imgs[i];
        if (im.width <= 80 && im.src && im.src.indexOf("favicons") < 0) { av = im; break; }
      }
    }
    if (!av) return;
    if (av.closest("#deskDetail") || av.closest(".chat-panel")) return;
    if (av.tagName === "IMG") {
      var u = _brandImgUrl(a);
      if (u) av.src = u;
    } else {
      av.innerHTML = _brandImg(a, 64);
    }
  } catch (e) {}
}
function _swapDetailAvatar(a) {
  _swapDetailAvatarOnce(a);
  setTimeout(function () { _swapDetailAvatarOnce(a); }, 400);
  setTimeout(function () { _swapDetailAvatarOnce(a); }, 1000);
}
function _roomCountsSync() {
  try {
    var counts = {};
    (C.agents || []).forEach(function (a) {
      var z = (C.zones || []).filter(function (zz) { return zz.id === a.zone; })[0];
      var t = z ? z.title : "";
      counts[t] = (counts[t] || 0) + 1;
    });
    var btns = document.querySelectorAll("button");
    for (var i = 0; i < btns.length; i++) {
      var b = btns[i];
      var full = b.textContent || "";
      var keys = Object.keys(counts);
      for (var j = 0; j < keys.length; j++) {
        var t = keys[j];
        if (!t || full.indexOf(t) < 0) continue;
        var w = document.createTreeWalker(b, 4, null);
        var nodes = [];
        var tn;
        while ((tn = w.nextNode())) nodes.push(tn);
        for (var q = 0; q < nodes.length; q++) {
          var s = nodes[q].textContent;
          var ai = s.indexOf("alat");
          if (ai < 0) continue;
          var k = ai - 1;
          while (k >= 0 && (s[k] === " " || (s[k] >= "0" && s[k] <= "9"))) k--;
          var ns = k + 1;
          var numTxt = s.slice(ns, ai).trim();
          if (numTxt) {
            var pre = s.slice(0, ns);
            nodes[q].textContent = pre + (pre ? " " : "") + counts[t] + " " + s.slice(ai);
          } else if (q > 0) {
            var s2 = nodes[q - 1].textContent;
            var e2 = s2.length - 1;
            while (e2 >= 0 && s2[e2] === " ") e2--;
            var dEnd = e2;
            var dStart = dEnd;
            while (dStart >= 0 && s2[dStart] >= "0" && s2[dStart] <= "9") dStart--;
            dStart++;
            if (dEnd >= dStart) nodes[q - 1].textContent = s2.slice(0, dStart) + counts[t] + s2.slice(dEnd + 1);
          }
          break;
        }
      }
    }
  } catch (e) {}
}
function _p14layoutFix() {
  try {
    var st = document.getElementById("p14-fs-css");
    if (!st) {
      st = document.createElement("style");
      st.id = "p14-fs-css";
      st.textContent = "body.is-fs .topbar{display:flex !important}body.is-fs .tabstrip{display:flex !important}body.is-fs .nav-rail{display:flex !important}body.is-fs #sidebar,body.is-fs .sidebar{display:block !important}body.is-fs .dock-wrap{display:block !important}body.is-fs .chat-fab{display:flex !important}body.is-fs .chat-panel{display:block !important}body.is-fs #newsTicker{display:flex !important}body.is-fs .zoom-ctl{right:14px !important;bottom:84px !important}.zoom-ctl{right:170px !important;bottom:12px !important;z-index:60 !important}#newsTicker{position:relative !important;z-index:80 !important}#newsOpenBtn,#newsPauseBtn{position:relative !important;z-index:81 !important;pointer-events:auto !important}";
      document.head.appendChild(st);
    }
    var tk = document.getElementById("newsTicker");
    if (tk) { tk.style.position = "relative"; tk.style.zIndex = "80"; }
    var nb = document.getElementById("newsOpenBtn");
    if (nb) { nb.style.position = "relative"; nb.style.zIndex = "81"; }
    var pb = document.getElementById("newsPauseBtn");
    if (pb) { pb.style.position = "relative"; pb.style.zIndex = "81"; }
    var empties = document.querySelectorAll(".dock-wrap .board-empty");
    for (var i = 0; i < empties.length; i++) { empties[i].style.display = "none"; }
    var dw2 = document.querySelector(".dock-wrap");
    var tk2 = document.getElementById("newsTicker");
    if (dw2 && tk2 && tk2.parentNode !== dw2) { dw2.insertBefore(tk2, dw2.firstChild); tk2.style.position = "relative"; tk2.style.zIndex = "80"; tk2.style.width = "100%"; }
    var allEmpty = document.querySelectorAll(".board-empty");
    for (var q2 = 0; q2 < allEmpty.length; q2++) {
      var et = allEmpty[q2].textContent || "";
      if (et.indexOf("Tidak ada agent yang cocok") >= 0) allEmpty[q2].style.display = "none";
    }
    var si2 = document.getElementById("searchInput");
    if (si2 && !si2.value && state && state.query) { try { state.query = ""; si2.dispatchEvent(new Event("input", { bubbles: true })); } catch (e9) {} }
    var lg2 = document.getElementById("roomLogPanel");
    if (lg2) { lg2.style.zIndex = "55"; lg2.style.background = "#0b1220"; lg2.style.border = "1px solid rgba(255,255,255,.25)"; lg2.style.borderRadius = "8px"; }

    try { _roomCountsSync(); } catch (e) {}
  } catch (e2) {}
}
function _p14anaFix() {
  try {
    var raw = window.__liveRaw;
    if (!raw || !raw.venues) return;
    var pos = 0;
    var ven = 0;
    var keys = Object.keys(raw.venues);
    for (var i = 0; i < keys.length; i++) {
      var v = raw.venues[keys[i]];
      if (v) { if (v.positions) pos += v.positions.length; ven++; }
    }
    var dlg = null;
    var dlgs = document.querySelectorAll("[role=dialog]");
    for (var a = 0; a < dlgs.length; a++) {
      var lb = (dlgs[a].getAttribute("aria-label") || "") + " " + (dlgs[a].textContent || "");
      if (lb.indexOf("Dasbor analitik live") >= 0) { dlg = dlgs[a]; break; }
    }
    if (!dlg) return;
    var vals = dlg.querySelectorAll("div, span, p, b, strong, li, td");
    for (var b = 0; b < vals.length; b++) {
      var el = vals[b];
      if (el.children.length) continue;
      var t = el.textContent || "";
      if (t.indexOf("undefined") < 0) continue;
      var anc = el;
      var kind = "";
      while (anc && anc !== dlg) {
        var at = anc.textContent || "";
        if (at.indexOf("Posisi terbuka") >= 0) { kind = "pos"; break; }
        if (at.indexOf("Venue live") >= 0) { kind = "ven"; break; }
        anc = anc.parentNode;
      }
      if (kind === "pos") el.textContent = t.split("undefined").join(String(pos));
      else if (kind === "ven") el.textContent = t.split("undefined").join(String(ven)).split("/ 5").join("/ 6");
    }
  } catch (e) {}
}
function _p14brandFix() {
  try {
    var tbs = document.querySelectorAll("[role=tab]");
    for (var i = 0; i < tbs.length; i++) {
      try {
        var tb = tbs[i];
        if (tb.dataset.p14brand) continue;
        var nm = (tb.textContent || "").split("×").join("").trim();
        var ag = null;
        for (var j = 0; j < (C.agents || []).length; j++) {
          if (nm.indexOf(C.agents[j].name) >= 0) { ag = C.agents[j]; break; }
        }
        if (!ag) continue;
        var tn = null;
        var tw = document.createTreeWalker(tb, 4, null);
        var nd = null;
        while ((nd = tw.nextNode())) { if (nd.textContent.trim()) { tn = nd; break; } }
        if (!tn) continue;
        var holder = document.createElement("span");
        holder.innerHTML = _brandImg(ag, 18);
        tn.parentNode.insertBefore(holder, tn);
        var s = tn.textContent;
        var p = 0;
        while (p < s.length && s.charCodeAt(p) > 127) p++;
        tn.textContent = s.slice(p);
        tb.dataset.p14brand = "1";
      } catch (e2) {}
    }
  } catch (e) {}
}
setInterval(_p14layoutFix, 3000);
setInterval(_p14anaFix, 3000);
setInterval(_p14brandFix, 3000);
setTimeout(_p14layoutFix, 1200);
setTimeout(_p14anaFix, 1500);
setTimeout(_p14brandFix, 1500);
document.addEventListener("fullscreenchange", function () {
  setTimeout(_p14layoutFix, 250);
  setTimeout(function () { try { window.dispatchEvent(new Event("resize")); } catch (e) {} }, 700);
});
document.addEventListener("click", function (ev) {
  var t = ev.target;
  if (t && t.closest && t.closest(".p14-search")) {
    setTimeout(function () {
      var ip = document.getElementById("searchInput");
      if (ip) ip.value = "";
      try { state.query = ""; } catch (e2) {}
    }, 60);
  }
}, true);
})();
