# -*- coding: utf-8 -*-
import streamlit as st, requests, json, itertools
from collections import Counter
from datetime import datetime
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# ═══════════════════════════ DỮ LIỆU ═══════════════════════════
_BASE = "https://www.kqxs88.live/api/front/open/lottery/history/list/game?limitNum=60&gameCode="
CODES = {
    "Miền Bắc":"miba","VN Miền Bắc 75s":"vnmbmg","Miền Bắc 75s":"mbmg",
    "An Giang":"angi","Bạc Liêu":"bali","Bến Tre":"betr","Bình Dương":"bidu",
    "Bình Thuận":"bith","Bình Phước":"biph","Cà Mau":"cama","Cần Thơ":"cath",
    "Đà Lạt":"dalat","Đồng Nai":"dona","Đồng Tháp":"doth","Hậu Giang":"hagi",
    "Kiên Giang":"kigi","Long An":"loan","Sóc Trăng":"sotr","Tây Ninh":"tani",
    "Tiền Giang":"tigi","TP. Hồ Chí Minh":"tphc","Trà Vinh":"trvi",
    "Vĩnh Long":"vilo","Vũng Tàu":"vuta","Đà Nẵng":"dana","Bình Định":"bidi",
    "Đắk Lắk":"dalak","Đắk Nông":"dano","Gia Lai":"gila","Khánh Hòa":"khho",
    "Kon Tum":"kotu","Ninh Thuận":"nith","Phú Yên":"phye","Quảng Bình":"qubi",
    "Quảng Nam":"quna","Quảng Ngãi":"qung","Quảng Trị":"qutr","Thừa Thiên Huế":"thth",
}
API = {n: _BASE+c for n,c in CODES.items()}

LICH_NAM = {
    "Chủ Nhật":["Tiền Giang","Kiên Giang","Đà Lạt"],
    "Thứ 2":["TP. Hồ Chí Minh","Đồng Tháp","Cà Mau"],
    "Thứ 3":["Bến Tre","Vũng Tàu","Bạc Liêu"],
    "Thứ 4":["Đồng Nai","Cần Thơ","Sóc Trăng"],
    "Thứ 5":["Tây Ninh","An Giang","Bình Thuận"],
    "Thứ 6":["Vĩnh Long","Bình Dương","Trà Vinh"],
    "Thứ 7":["TP. Hồ Chí Minh","Long An","Bình Phước","Hậu Giang"],
}
LICH_TRUNG = {
    "Chủ Nhật":["Kon Tum","Khánh Hòa","Thừa Thiên Huế"],
    "Thứ 2":["Thừa Thiên Huế","Phú Yên"],
    "Thứ 3":["Đắk Lắk","Quảng Nam"],
    "Thứ 4":["Đà Nẵng","Khánh Hòa"],
    "Thứ 5":["Bình Định","Quảng Trị","Quảng Bình"],
    "Thứ 6":["Gia Lai","Ninh Thuận"],
    "Thứ 7":["Đà Nẵng","Quảng Ngãi","Đắk Nông"],
}
LICH_BAC = {
    "Chủ Nhật":"Thái Bình","Thứ 2":"Hà Nội","Thứ 3":"Quảng Ninh",
    "Thứ 4":"Bắc Ninh","Thứ 5":"Hà Nội","Thứ 6":"Hải Phòng","Thứ 7":"Nam Định",
}
DAYS = ["Thứ 2","Thứ 3","Thứ 4","Thứ 5","Thứ 6","Thứ 7","Chủ Nhật"]

PRIZE_CONF = [
    ("ĐB","#c0392b",1),("G1","#e67e22",1),("G2","#d4ac0d",2),
    ("G3","#1e8449",6),("G4","#2471a3",4),("G5","#6c3483",6),
    ("G6","#117a65",3),("G7","#7f8c8d",4),
]
GIAI_MB = [
    "ĐB","G1","G2-1","G2-2",
    "G3-1","G3-2","G3-3","G3-4","G3-5","G3-6",
    "G4-1","G4-2","G4-3","G4-4",
    "G5-1","G5-2","G5-3","G5-4","G5-5","G5-6",
    "G6-1","G6-2","G6-3","G7-1","G7-2","G7-3","G7-4",
]

def get_stations(region, day):
    if region == "Miền Bắc":
        t = LICH_BAC.get(day, "")
        return [f"Miền Bắc ({t})", "VN Miền Bắc 75s", "Miền Bắc 75s"]
    if region == "Miền Nam":  return LICH_NAM.get(day, [])
    return LICH_TRUNG.get(day, [])

# ═══════════════════════════ NETWORK ═══════════════════════════
HEADERS = {"User-Agent": "Mozilla/5.0", "Referer": "https://www.kqxs88.live/"}

@st.cache_resource
def _sess():
    s = requests.Session()
    s.mount("https://", HTTPAdapter(max_retries=Retry(
        total=3, backoff_factor=0.5,
        status_forcelist=[429,500,502,503,504],
        allowed_methods=frozenset(["GET"]))))
    return s

def load_raw(station: str) -> list:
    key = "Miền Bắc" if ("Miền Bắc" in station and "75s" not in station) else station
    url = API.get(key, "")
    if not url: return []
    try:
        r = _sess().get(url, headers=HEADERS, timeout=15)
        r.raise_for_status()
        return r.json().get("t", {}).get("issueList", [])
    except Exception as e:
        st.error(f"Lỗi tải: {e}")
        return []

# ═══════════════════════════ PARSE ═══════════════════════════
def parse_detail(item: dict) -> list:
    """Tự động nhận diện format API → trả về list các field giải thưởng."""
    raw = item.get("detail", None)

    def _coerce_list(lst):
        out = []
        for x in lst:
            if isinstance(x, (list, tuple)):
                out.append(",".join(str(v).strip() for v in x))
            else:
                out.append(str(x).strip())
        return out

    if isinstance(raw, list):
        return _coerce_list(raw)
    if isinstance(raw, str) and raw.strip():
        try:
            p = json.loads(raw)
            if isinstance(p, list):
                return _coerce_list(p)
        except Exception:
            pass
        if "|" in raw:
            return [x.strip() for x in raw.split("|") if x.strip()]
        return [raw.strip()]
    # fallback
    for k in ("openCode", "prizeNum", "number", "code"):
        v = str(item.get(k, "")).strip()
        if v:
            return [x.strip() for x in v.split("|")] if "|" in v else [v]
    return []

def get_prizes(item) -> list:
    """Tất cả số giải dạng string, split phẩy."""
    return [p.strip() for f in parse_detail(item)
            for p in str(f).split(",") if p.strip()]

def get_2d(prizes: list) -> list:
    """2 chữ số cuối của mỗi giải."""
    return [p[-2:] for p in prizes if len(p) >= 2 and p[-2:].isdigit()]

def miss_heads(prizes: list) -> list:
    h = [p[-2] if len(p) >= 2 else "0" for p in prizes if p.strip()]
    cnt = Counter(h)
    return [str(d) for d in range(10) if not cnt.get(str(d), 0)]

def get_list0(prizes: list, idxs=None) -> list:
    src = [prizes[i] for i in idxs if i < len(prizes)] if idxs else prizes
    cnt = Counter(c for p in src for c in p if c.isdigit())
    return [str(d) for d in range(10) if not cnt.get(str(d), 0)]

def bridge(a, b):
    return sorted({x+y for x in a for y in b} | {y+x for x in a for y in b})

_CH = {str(d): [f"{i:02d}" for i in range(100) if str(d) in f"{i:02d}"] for d in range(10)}
_TG = {str(d): [f"{i:02d}" for i in range(100) if (i//10+i%10) % 10 == d] for d in range(10)}

def cham_tong(miss: list) -> list:
    s = set()
    for d in miss:
        s.update(_CH.get(d, []))
        s.update(_TG.get(d, []))
    return sorted(s)

def ky(item):   return str(item.get("turnNum","") or item.get("issueNum","") or "")
def ngay(item): return str(item.get("openTime","") or "").split(" ")[0]

# ═══════════════════════════ HTML TABLE ═══════════════════════════
def htable(headers, rows, col_css=None, fs=13):
    TH = (f"background:#2c3e50;color:#fff;padding:8px 12px;"
          f"font-size:{fs}px;white-space:nowrap;border:1px solid #1a252f;")
    def td_s(ci, ri):
        bg = "#f5f7fa" if ri % 2 else "#ffffff"
        base = (f"padding:7px 11px;font-size:{fs}px;border:1px solid #e8ecf0;"
                f"white-space:nowrap;background:{bg};color:#2c3e50")
        ex = (col_css or {}).get(ci, (col_css or {}).get(
            headers[ci] if ci < len(headers) else "", ""))
        return base + (";" + ex if ex else "")
    ths = "".join(f'<th style="{TH}">{h}</th>' for h in headers)
    trs = ""
    for ri, row in enumerate(rows):
        cells = []
        for ci, c in enumerate(row):
            raw = str(c) if c is not None else ""
            # Strip HTML tags để làm title tooltip
            import re as _re
            plain = _re.sub(r'<[^>]+>', '', raw)
            cells.append(f'<td style="{td_s(ci,ri)}" title="{plain}">{raw}</td>')
        trs += f'<tr>{"".join(cells)}</tr>'
    return (f'<div style="overflow:auto;max-height:640px;border-radius:8px;'
            f'box-shadow:0 2px 8px rgba(0,0,0,.12);margin:6px 0">'
            f'<table style="border-collapse:collapse;width:100%;background:#fff">'
            f'<thead style="position:sticky;top:0;z-index:2"><tr>{ths}</tr></thead>'
            f'<tbody>{trs}</tbody></table></div>')

# ═══════════════════════════ KẾT QUẢ PANEL ═══════════════════════════
def panel_ket_qua(raw, show_g47):
    if not raw: return
    item   = raw[0]
    detail = parse_detail(item)

    # ── Kết quả giải ──
    html = (f'<div style="font-weight:700;color:#c0392b;font-size:13px;margin-bottom:6px">'
            f'🎯 {ky(item)} &nbsp;<span style="color:#888;font-weight:400;font-size:11px">{ngay(item)}</span></div>')
    idx = 0
    for label, color, cnt in PRIZE_CONF:
        if not show_g47 and label in ("G4","G5","G6","G7"):
            idx += cnt; continue
        vals = []
        for _ in range(cnt):
            if idx < len(detail): vals.append(detail[idx].strip()); idx += 1
        if not any(vals): continue
        nums = "&nbsp;".join(f'<b style="font-family:Consolas;font-size:14px;color:#1a1a2e">{v}</b>' for v in vals if v)
        html += (f'<div style="display:flex;align-items:center;gap:6px;padding:2px 0;border-bottom:1px solid #f0f0f0">'
                 f'<span style="background:{color};color:#fff;border-radius:3px;padding:1px 5px;'
                 f'font-size:10px;font-weight:700;min-width:26px;text-align:center;flex-shrink:0">{label}</span>'
                 f'{nums}</div>')
    st.markdown(f'<div style="background:#fff;border:1px solid #ddd;border-radius:8px;padding:10px;margin-bottom:8px">{html}</div>',
                unsafe_allow_html=True)

    # ── GĐB 5 kỳ ──
    gdbs = [get_prizes(it)[0].strip() for it in raw[:5] if get_prizes(it)]
    gdb_html = " &nbsp; ".join(f'<b style="font-family:Consolas;font-size:14px;color:#fff">{g}</b>' for g in gdbs)
    st.markdown(f'<div style="background:#2c3e50;border-radius:6px;padding:7px 10px;margin-bottom:8px">'
                f'<span style="color:#95a5a6;font-size:10px">GĐB 5 kỳ:&nbsp;</span>{gdb_html}</div>',
                unsafe_allow_html=True)

    # ── Bảng Đầu/Đuôi ──
    prizes = get_prizes(item)
    nums2d = get_2d(prizes)
    cnt_dau  = Counter(n[0] for n in nums2d)
    cnt_duoi = Counter(n[1] for n in nums2d)
    max_dau  = max(cnt_dau.values(),  default=1)
    max_duoi = max(cnt_duoi.values(), default=1)
    h2t = {str(i):[] for i in range(10)}
    t2h = {str(i):[] for i in range(10)}
    for n in nums2d:
        h2t[n[0]].append(n[1]); t2h[n[1]].append(n[0])

    dau_sorted  = sorted(range(10), key=lambda i: -cnt_dau.get(str(i),0))
    duoi_sorted = sorted(range(10), key=lambda i: -cnt_duoi.get(str(i),0))

    def mk_bar(cnt, max_c, color):
        w = int(cnt/max_c*40) if max_c else 0
        return (f'<div style="display:inline-block;width:{w}px;height:8px;'
                f'background:{color};border-radius:2px;margin-right:3px;vertical-align:middle"></div>')

    TH = "background:#2c3e50;color:#fff;padding:3px 6px;font-size:11px;text-align:center"
    TD = "padding:3px 6px;border:1px solid #eee;font-size:12px"

    rows_d, rows_t = "", ""
    for i in dau_sorted:
        d = str(i); c = cnt_dau.get(d,0); hot = c>=3
        bg = "background:#fff3e0;" if hot else ""
        rows_d += (f'<tr style="{bg}"><td style="{TD};font-weight:700;color:#c0392b;text-align:center;font-family:Consolas">{d}</td>'
                   f'<td style="{TD};white-space:nowrap">{mk_bar(c,max_dau,"#c0392b")}<b style="color:{"#c0392b" if hot else "#555"}">{c}</b></td>'
                   f'<td style="{TD};color:#1a5276;font-family:Consolas;font-size:11px">{",".join(sorted(h2t[d]))}</td></tr>')
    for i in duoi_sorted:
        d = str(i); c = cnt_duoi.get(d,0); hot = c>=3
        bg = "background:#e8f5e9;" if hot else ""
        rows_t += (f'<tr style="{bg}"><td style="{TD};font-weight:700;color:#1e8449;text-align:center;font-family:Consolas">{d}</td>'
                   f'<td style="{TD};white-space:nowrap">{mk_bar(c,max_duoi,"#1e8449")}<b style="color:{"#1e8449" if hot else "#555"}">{c}</b></td>'
                   f'<td style="{TD};color:#1a5276;font-family:Consolas;font-size:11px">{",".join(sorted(t2h[d]))}</td></tr>')

    tbl = (f'<div style="display:flex;gap:8px">'
           f'<div style="flex:1"><table style="border-collapse:collapse;width:100%">'
           f'<tr><th style="{TH}">Đầu</th><th style="{TH}">SL▼</th><th style="{TH}">Đuôi ra</th></tr>{rows_d}</table></div>'
           f'<div style="flex:1"><table style="border-collapse:collapse;width:100%">'
           f'<tr><th style="{TH}">Đuôi</th><th style="{TH}">SL▼</th><th style="{TH}">Đầu ra</th></tr>{rows_t}</table></div>'
           f'</div>')
    st.markdown(f'<div style="background:#fff;border:1px solid #ddd;border-radius:8px;padding:8px">{tbl}</div>',
                unsafe_allow_html=True)

# ═══════════════════════════ TAB THIẾU ĐẦU ═══════════════════════════
def tab_thieu_dau(raw):
    if not raw: st.info("👆 Chọn đài và nhấn **TẢI DỮ LIỆU**"); return

    c1, c2, c3, c4 = st.columns(4)
    duoi_db = c1.checkbox("Đuôi ĐB", True,  key="t2a")
    dau_db  = c2.checkbox("Đầu ĐB",  False, key="t2b")
    duoi_g1 = c3.checkbox("Đuôi G1", False, key="t2c")
    dau_g1  = c4.checkbox("Đầu G1",  False, key="t2d")

    def targets(prizes):
        t = set()
        if prizes and len(prizes[0]) >= 2:
            if duoi_db: t.add(prizes[0][-2:])
            if dau_db:  t.add(prizes[0][:2])
        if len(prizes) > 1 and len(prizes[1]) >= 2:
            if duoi_g1: t.add(prizes[1][-2:])
            if dau_g1:  t.add(prizes[1][:2])
        return t

    proc = [{"ky": ky(i), "ngay": ngay(i),
             "mh": miss_heads(get_prizes(i)),
             "pf": get_prizes(i)} for i in raw]

    # ── Bảng chính: Kỳ + Thiếu Đầu + Dàn ──
    headers_main = ["Kỳ","Ngày","Thiếu Đầu","Dàn Chạm+Tổng"]
    ccs_main = {
        0: "color:#c0392b;font-weight:700;text-align:center",
        1: "color:#7f8c8d;text-align:center",
        2: "background:#fff3cd;color:#7d4e00;font-weight:700;text-align:center",
        3: "background:#dbeafe;color:#1e40af;font-size:12px;font-family:Consolas",
    }
    headers_k = ["Kỳ","Ngày","K1","K2","K3","K4","K5","K6","K7"]
    ccs_k = {
        0: "color:#c0392b;font-weight:700;text-align:center",
        1: "color:#7f8c8d;text-align:center",
    }
    for k in range(2, 9): ccs_k[k] = "background:#ecfdf5;color:#065f46;font-size:12px;font-family:Consolas;max-width:30px;overflow:hidden;text-overflow:ellipsis;cursor:pointer"

    rows_main, rows_k = [], []
    for i, curr in enumerate(proc):
        dan = cham_tong(curr["mh"])
        rows_main.append([
            curr["ky"], curr["ngay"],
            " ".join(curr["mh"]) if curr["mh"] else "—",
            " ".join(dan) if dan else "—",
        ])
        row_k = [curr["ky"], curr["ngay"]]
        for k in range(1, 8):
            t = i - k
            if t < 0:
                row_k.append("")
            else:
                hits = set(dan) & targets(proc[t]["pf"])
                if hits:
                    row_k.append(f'<b style="color:#059669;font-size:13px">✅ {",".join(sorted(hits))}</b>')
                else:
                    row_k.append('<span style="color:#ccc">—</span>')
        rows_k.append(row_k)

    st.markdown(htable(headers_main, rows_main, ccs_main), unsafe_allow_html=True)
    with st.expander("📊 Xem K1 → K7 (kết quả trúng theo kỳ)"):
        st.markdown(htable(headers_k, rows_k, ccs_k), unsafe_allow_html=True)

# ═══════════════════════════ TAB CẦU LIST 0 ═══════════════════════════
def tab_list0(raw):
    if not raw: st.info("👆 Chọn đài và nhấn **TẢI DỮ LIỆU**"); return

    st.markdown("**Chọn giải tính List 0:**")
    defaults = {2, 3}
    selected = []
    cols = st.columns(9)
    for i, label in enumerate(GIAI_MB):
        if cols[i % 9].checkbox(label, value=(i in defaults), key=f"gl_{i}"):
            selected.append(i)

    def diff(s, t): return sorted(set(s) - set(t))

    proc = []
    for item in raw:
        p = get_prizes(item)
        proc.append({"ky": ky(item), "ngay": ngay(item),
                     "l0": get_list0(p, selected) if selected else get_list0(p),
                     "res": get_2d(p)})

    headers_main = ["Kỳ","Ngày","List 0 (Thiếu)","Kỳ-1","Kỳ-2","Sót K0"]
    ccs_main = {
        0: "color:#c0392b;font-weight:700;text-align:center",
        1: "color:#7f8c8d;text-align:center",
        2: "background:#fff3cd;color:#7d4e00;font-weight:700;text-align:center",
        3: "color:#856404;text-align:center",
        4: "color:#856404;text-align:center",
        5: "background:#dbeafe;color:#1e40af;font-weight:700;font-family:Consolas;font-size:12px",
    }
    headers_k = ["Kỳ","Ngày","K1","K2","K3","K4","K5","K6","K7"]
    ccs_k = {
        0: "color:#c0392b;font-weight:700;text-align:center",
        1: "color:#7f8c8d;text-align:center",
    }
    for k in range(2,9): ccs_k[k] = "background:#ecfdf5;color:#065f46;font-size:12px;font-family:Consolas;max-width:30px;overflow:hidden;text-overflow:ellipsis;cursor:pointer"

    rows_main, rows_k = [], []
    for i, curr in enumerate(proc):
        k0 = bridge(curr["l0"], proc[i+1]["l0"]) if i+1 < len(proc) else []
        k0 = diff(k0, curr["res"])
        rows_main.append([
            curr["ky"], curr["ngay"],
            " ".join(curr["l0"]) if curr["l0"] else "—",
            " ".join(proc[i-1]["l0"]) if i >= 1 else "",
            " ".join(proc[i-2]["l0"]) if i >= 2 else "",
            " ".join(k0) if k0 else "—",
        ])
        row_k = [curr["ky"], curr["ngay"]]
        cur = k0[:]
        for k in range(1, 8):
            t = i - k
            if t < 0: row_k.append("")
            else:
                cur = diff(cur, proc[t]["res"])
                row_k.append(" ".join(cur) if cur
                             else '<b style="color:#059669">✅</b>')
        rows_k.append(row_k)

    st.markdown(htable(headers_main, rows_main, ccs_main), unsafe_allow_html=True)
    with st.expander("📊 Xem K1 → K7 (sót qua từng kỳ)"):
        st.markdown(htable(headers_k, rows_k, ccs_k), unsafe_allow_html=True)

# ═══════════════════════════ TAB LÔ LẠ ═══════════════════════════
def _detect(prize, use_s, use_l, use_g, use_c):
    s = prize.strip()
    if len(s) < 2 or not all(c.isdigit() for c in s): return False
    if use_c:
        for i in range(len(s)-2):
            if len(set(s[i:i+3])) == 1: return True
    if use_l and any(c >= 2 for c in Counter(s).values()): return True
    if use_g and s == s[::-1]: return True
    if use_s and len(set(s)) <= 3: return True
    return False

def tab_lo_la(raw, region):
    if not raw: st.info("👆 Chọn đài và nhấn **TẢI DỮ LIỆU**"); return

    c1, c2, c3 = st.columns(3)
    use_s = c1.checkbox("≤3 chữ số duy nhất", True,  key="t3s")
    use_l = c1.checkbox("Lặp (≥2 giống nhau)", False, key="t3l")
    use_g = c2.checkbox("Gánh / Đảo",          False, key="t3g")
    use_c = c2.checkbox("Lặp liên tiếp ≥3",    False, key="t3c")
    dup   = c3.checkbox("Giữ số trùng",         False, key="t3d")
    mode  = c3.radio("Nhị hợp",
                     ["Mặc định (≥2 giải)", "Chỉ 1 giải", "Cả hai"],
                     index=2, horizontal=True, key="t3m")
    mv = {"Mặc định (≥2 giải)": 0, "Chỉ 1 giải": 1, "Cả hai": 2}[mode]
    mx = 9 if "Bắc" in region else 13

    def diff(s, t): return sorted(set(s) - set(t))

    proc = []
    for item in raw:
        p = get_prizes(item)
        td = get_2d(p)
        lo_list = []
        for ci, prize in enumerate(p):
            if ci > mx: break
            if _detect(prize, use_s, use_l, use_g, use_c):
                digs = [d for d in prize if d.isdigit()]
                lo_list.append("".join(sorted(digs) if dup else sorted(set(digs))))
        l0 = sorted(lo_list) if dup else sorted(set(lo_list))
        all_d = sorted({c for s in l0 for c in s if c.isdigit()})
        n1, nm = len(l0) == 1, len(l0) > 1
        show = (mv == 0 and nm) or (mv == 1 and n1) or (mv == 2 and (n1 or nm))
        dan = sorted({a+b for a in all_d for b in all_d}) if show and all_d else []
        proc.append({"ky": ky(item), "ngay": ngay(item),
                     "l0": l0, "dan": dan, "res": td, "show": show})

    headers_main = ["Kỳ","Ngày","List 0 Lạ","Dàn Nhị Hợp"]
    ccs_main = {
        0: "color:#c0392b;font-weight:700;text-align:center",
        1: "color:#7f8c8d;text-align:center",
        2: "background:#fff3cd;color:#7d4e00;font-weight:700;text-align:center",
        3: "background:#dbeafe;color:#1e40af;font-size:12px;font-family:Consolas",
    }
    headers_k = ["Kỳ","Ngày"] + [f"K{k}" for k in range(1,11)]
    ccs_k = {
        0: "color:#c0392b;font-weight:700;text-align:center",
        1: "color:#7f8c8d;text-align:center",
    }
    for k in range(2,12): ccs_k[k] = "background:#ecfdf5;color:#065f46;font-size:12px;font-family:Consolas;max-width:30px;overflow:hidden;text-overflow:ellipsis;cursor:pointer"

    rows_main, rows_k = [], []
    for i, curr in enumerate(proc):
        dan_disp = (" ".join(curr["dan"][:25]) + ("…" if len(curr["dan"]) > 25 else "")
                   if curr["show"] else "")
        rows_main.append([
            curr["ky"], curr["ngay"],
            ",".join(curr["l0"]) if curr["l0"] else "",
            dan_disp,
        ])
        row_k = [curr["ky"], curr["ngay"]]
        cur = curr["dan"][:]
        for k in range(1, 11):
            t = i - k
            if t < 0 or not curr["show"]: row_k.append("")
            else:
                cur = diff(cur, proc[t]["res"])
                row_k.append(" ".join(cur) if cur
                             else '<b style="color:#059669">✅</b>')
        rows_k.append(row_k)

    st.markdown(htable(headers_main, rows_main, ccs_main), unsafe_allow_html=True)
    with st.expander("📊 Xem K1 → K10 (sót qua từng kỳ)"):
        st.markdown(htable(headers_k, rows_k, ccs_k), unsafe_allow_html=True)

# ═══════════════════════════ TAB LÔ XIÊN ═══════════════════════════
def tab_lo_xien(raw):
    st.markdown("### 🔢 Ghép Xiên Tự Động")
    cols4 = st.columns(4)
    groups = []
    for i, col in enumerate(cols4, 1):
        with col:
            st.markdown(f"**Nhóm {i}**")
            txt = st.text_area("", height=90, key=f"xg{i}",
                               placeholder="Nhập số, cách bởi\ndấu cách hoặc phẩy",
                               label_visibility="collapsed")
            nums = sorted(set(
                n.strip() for n in txt.replace(",", " ").split()
                if n.strip().isdigit()))
            groups.append(nums)
            if nums: st.caption(f"{len(nums)} số: {' '.join(nums)}")

    c1, c2, c3, c4, c5 = st.columns([1.5, 1, 1, 1, 2])
    sep = c1.selectbox("Ký tự nối", ["&", ",", "-", " "], key="xsep")
    x2  = c2.checkbox("Xiên 2", True,  key="xx2")
    x3  = c3.checkbox("Xiên 3", True,  key="xx3")
    x4  = c4.checkbox("Xiên 4", True,  key="xx4")

    b1, b2 = c5.columns(2)
    quay = b1.button("🔄 Xiên Quay", use_container_width=True)
    nhom = b2.button("🔗 Xiên Nhóm", use_container_width=True)

    if quay:
        if len(groups[0]) < 2: st.warning("⚠️ Nhập ít nhất 2 số ở Nhóm 1!")
        else:
            rc = st.columns(3)
            for idx, (k, use) in enumerate([(2, x2), (3, x3), (4, x4)]):
                if use:
                    combos = list(itertools.combinations(groups[0], k))
                    rc[idx].text_area(f"Xiên {k} — {len(combos)} cặp",
                                      ";\n".join(sep.join(c) for c in combos),
                                      height=200, key=f"qr{k}")

    if nhom:
        rc = st.columns(3)
        for idx, (k, use) in enumerate([(2, x2), (3, x3), (4, x4)]):
            if use:
                src = groups[:k]
                if all(src):
                    res = list(itertools.product(*src))
                    rc[idx].text_area(f"Xiên {k} — {len(res)} cặp",
                                      ";\n".join(sep.join(c) for c in res),
                                      height=200, key=f"nr{k}")
                else:
                    st.warning(f"Cần nhập đủ {k} nhóm!")

    if raw and len(raw) >= 5:
        with st.expander("📜 Kiểm tra lịch sử 20 kỳ"):
            p0 = get_prizes(raw[0])
            pred_set = set(get_2d(p0)[:8])
            hist_rows = []
            for it in raw[:20]:
                actual = set(get_2d(get_prizes(it)))
                hits = sorted(pred_set & actual)
                hist_rows.append([
                    ky(it), ngay(it), " ".join(sorted(pred_set)),
                    f'<b style="color:{"#27ae60" if hits else "#bbb"}">'
                    f'{"✅ "+",".join(hits) if hits else "—"}</b>',
                    str(len(hits))])
            st.markdown(htable(
                ["Kỳ","Ngày","Bộ số","Trúng","Số trúng"], hist_rows,
                {0:"color:#c0392b;font-weight:700",
                 4:"text-align:center;font-weight:700"}),
                unsafe_allow_html=True)

# ═══════════════════════════ TAB TÀI XỈU ═══════════════════════════
def bead_svg(seq):
    ROWS, CS, PAD = 6, 34, 6
    col, row, prev = 0, 0, None
    cells = []
    for d in seq:
        r = d["r"]
        if prev is not None and (r != prev or row >= ROWS):
            col += 1; row = 0
        cx = PAD + col*(CS+4) + CS//2
        cy = PAD + row*(CS+4) + CS//2
        cells.append((cx, cy, "#c0392b" if r == "T" else "#2471a3", r, d["total"]))
        prev = r; row += 1
    W = PAD + (col+1)*(CS+4) + PAD
    H = PAD + ROWS*(CS+4) + PAD
    s = ""
    for cx, cy, color, lbl, tot in cells:
        s += (f'<circle cx="{cx}" cy="{cy}" r="{CS//2-1}" '
              f'fill="{color}" stroke="white" stroke-width="2"/>'
              f'<text x="{cx}" y="{cy+5}" text-anchor="middle" '
              f'fill="white" font-size="14" font-weight="bold" font-family="Arial">{lbl}</text>'
              f'<text x="{cx+CS//2-2}" y="{cy+CS//2-2}" text-anchor="end" '
              f'fill="rgba(255,255,255,0.5)" font-size="8">{tot}</text>')
    return (f'<div style="overflow-x:auto;background:#1a2c3d;'
            f'border-radius:10px;padding:6px;margin:6px 0">'
            f'<svg width="{W}" height="{H}" xmlns="http://www.w3.org/2000/svg">'
            f'<rect width="{W}" height="{H}" fill="#1a2c3d"/>{s}</svg></div>')

def tab_tai_xiu(raw):
    if not raw: st.info("👆 Chọn đài và nhấn **TẢI DỮ LIỆU**"); return

    seq = []
    for item in reversed(raw):
        p = get_prizes(item)
        gdb = p[0].strip() if p else ""
        total = sum(int(c) for c in gdb if c.isdigit())
        seq.append({"turn": ky(item), "gdb": gdb, "total": total,
                    "r": "T" if total >= 23 else "X"})

    tot_t = sum(1 for d in seq if d["r"] == "T")
    tot_x = len(seq) - tot_t
    last = seq[-1]["r"]
    streak = 1
    for d in reversed(seq[:-1]):
        if d["r"] == last: streak += 1
        else: break

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Tổng kỳ", len(seq))
    m2.metric("🔴 TÀI", f"{tot_t} ({tot_t/len(seq)*100:.0f}%)")
    m3.metric("🔵 XỈU", f"{tot_x} ({tot_x/len(seq)*100:.0f}%)")
    m4.metric("Chuỗi hiện tại",
              f'{streak} {"Tài 🔴" if last=="T" else "Xỉu 🔵"}')

    l = seq[-1]
    tx = "**TÀI 🔴**" if l["r"] == "T" else "**XỈU 🔵**"
    st.info(f"Kỳ mới: **{l['turn']}** · GĐB: **{l['gdb']}** · Tổng: **{l['total']}** → {tx}")

    st.markdown("#### 🎱 Bead Road")
    st.markdown(bead_svg(seq), unsafe_allow_html=True)

    recent = seq[-30:]
    tbl = []
    for i, d in enumerate(recent):
        s = 1
        for j in range(i-1, -1, -1):
            if recent[j]["r"] == d["r"]: s += 1
            else: break
        color = "#c0392b" if d["r"] == "T" else "#2471a3"
        bg = "#fff0f0" if d["r"] == "T" else "#f0f5ff"
        tbl.append([
            d["turn"], d["gdb"], str(d["total"]),
            f'<span style="color:{color};font-weight:700;background:{bg};'
            f'padding:2px 8px;border-radius:4px">'
            f'{"TÀI 🔴" if d["r"]=="T" else "XỈU 🔵"}</span>',
            f'{s} {"Tài" if d["r"]=="T" else "Xỉu"}',
        ])
    st.markdown("#### 📋 30 kỳ gần nhất")
    st.markdown(
        htable(["Kỳ","GĐB","Tổng","Kết quả","Chuỗi"],
               list(reversed(tbl)),
               {0: "font-weight:700;text-align:center",
                1: "font-family:Consolas;font-size:14px;letter-spacing:1px",
                2: "text-align:center;font-weight:700"}),
        unsafe_allow_html=True)

# ═══════════════════════════ DEBUG ═══════════════════════════
def tab_debug(raw):
    st.markdown("### 🔍 Debug cấu trúc API")
    if not raw:
        st.info("Tải dữ liệu trước")
        return
    item = raw[0]
    st.write("**Tất cả fields:**", list(item.keys()))
    for k, v in item.items():
        st.code(f"{k!r:20s}: {str(v)[:300]}", language="text")
    st.divider()
    p = get_prizes(item)
    st.write(f"**get_prizes() → {len(p)} phần tử:**", p[:15])
    st.write("**get_2d():**", get_2d(p)[:15])
    st.write("**get_list0():**", get_list0(p))
    st.write("**miss_heads():**", miss_heads(p))

# ═══════════════════════════ ÁNH XẠ GĐB ═══════════════════════════

def _get_top_heads_tails(item, top_n=2):
    """
    Top đầu/đuôi theo tần suất thực, sort cao→thấp.
    Lấy top_n, nếu có tie ở vị trí top_n thì lấy hết cùng mức.
    Không dùng ngưỡng cứng — nhất quán với bảng hiển thị panel.
    """
    prizes = get_prizes(item)
    heads, tails = [], []
    for p in prizes:
        if len(p) >= 2 and p[-2:].isdigit():
            heads.append(p[-2])
            tails.append(p[-1])

    def top_by_freq(lst, n):
        if not lst: return []
        cnt = Counter(lst)
        # Sort: tần suất cao → thấp, tie → chữ số nhỏ trước
        ranked = sorted(cnt.items(), key=lambda x: (-x[1], x[0]))
        if len(ranked) <= n:
            return [d for d,_ in ranked]
        # Lấy đúng top n, kèm tie-breaking tại vị trí n
        threshold = ranked[n-1][1]
        return [d for d,c in ranked if c >= threshold]

    return top_by_freq(heads, top_n), top_by_freq(tails, top_n)

def _position_map(curr_detail, prev_detail, target_digits):
    """
    Thuật toán ánh xạ vị trí:
    1. Tìm vị trí (g,n,c) trong prev_detail có chữ số ∈ target_digits
    2. Ánh xạ sang curr_detail cùng vị trí → thu thập chữ số
    3. Tần suất → top 5
    """
    if not target_digits: return [], {}
    matched = []
    for g_idx, field in enumerate(prev_detail):
        nums = [x.strip() for x in field.split(",")]
        for n_idx, num in enumerate(nums):
            for c_idx, ch in enumerate(num):
                if ch in target_digits:
                    matched.append((g_idx, n_idx, c_idx))
    collected = []
    for g_idx, n_idx, c_idx in matched:
        if g_idx < len(curr_detail):
            curr_nums = [x.strip() for x in curr_detail[g_idx].split(",")]
            if n_idx < len(curr_nums):
                num = curr_nums[n_idx]
                if c_idx < len(num) and num[c_idx].isdigit():
                    collected.append(num[c_idx])
    freq = Counter(collected)
    top5 = [d for d,_ in freq.most_common(5)]
    return top5, dict(freq)

def compute_anh_xa(curr_item, prev_item):
    """Tính ánh xạ GĐB + Đầu/Đuôi nhiều."""
    curr_d = parse_detail(curr_item)
    prev_d = parse_detail(prev_item)
    if not curr_d or not prev_d:
        return None

    # GĐB
    gdb = curr_d[0].split(",")[0].strip()
    gdb_digits = set(c for c in gdb if c.isdigit())
    top5_gdb, freq_gdb = _position_map(curr_d, prev_d, gdb_digits)

    # Đầu/Đuôi nhiều
    top_heads, top_tails = _get_top_heads_tails(curr_item)
    top5_head, freq_head = _position_map(curr_d, prev_d, set(top_heads))
    top5_tail, freq_tail = _position_map(curr_d, prev_d, set(top_tails))

    return {
        "gdb": gdb,
        "gdb_digits": "".join(sorted(gdb_digits)),
        "top5_gdb":  top5_gdb,
        "freq_gdb":  freq_gdb,
        "top_heads": top_heads,
        "top_tails": top_tails,
        "top5_head": top5_head,
        "freq_head": freq_head,
        "top5_tail": top5_tail,
        "freq_tail": freq_tail,
    }

def tab_anh_xa(raw):
    if not raw or len(raw) < 2:
        st.info("👆 Cần ít nhất 2 kỳ dữ liệu")
        return

    st.markdown("""
    **Thuật toán Ánh Xạ Vị Trí:**  
    Lấy chữ số GĐB (hoặc Đầu/Đuôi nhiều) kỳ hiện tại → tìm vị trí chứa chữ số đó trong kỳ trước → ánh xạ sang kỳ hiện tại → đếm tần suất → Top 5.
    """)

    n = min(15, len(raw) - 1)
    rows = []
    for i in range(n):
        curr, prev = raw[i], raw[i+1]
        r = compute_anh_xa(curr, prev)
        if not r: continue

        def fmt_top(top5, freq):
            return "  ".join(f'<b style="color:#c0392b">{d}</b>({freq.get(d,0)})' for d in top5) or "—"

        def fmt_freq(freq):
            s = sorted(freq.items(), key=lambda x:(-x[1],x[0]))
            return "  ".join(f"{d}:{c}" for d,c in s) if s else "—"

        rows.append([
            f'<b style="color:#c0392b">{ky(curr)}</b>',
            ngay(curr),
            f'<b style="font-family:Consolas;font-size:15px">{r["gdb"]}</b>',
            r["gdb_digits"],
            fmt_top(r["top5_gdb"],  r["freq_gdb"]),
            fmt_freq(r["freq_gdb"]),
            f'<span style="color:#e67e22;font-weight:700">{",".join(r["top_heads"])}</span>',
            fmt_top(r["top5_head"], r["freq_head"]),
            f'<span style="color:#1e8449;font-weight:700">{",".join(r["top_tails"])}</span>',
            fmt_top(r["top5_tail"], r["freq_tail"]),
        ])

    headers = [
        "Kỳ", "Ngày",
        "GĐB", "CS GĐB",
        "Top5 GĐB (freq)", "Toàn bộ GĐB",
        "Đầu nhiều", "Top5 Đầu",
        "Đuôi nhiều", "Top5 Đuôi",
    ]
    # Banner kỳ mới nhất — chỉ GĐB + Top5 ánh xạ
    if rows:
        kq_html = (
            f'<div style="background:#eff6ff;border:2px solid #3b82f6;border-radius:8px;'
            f'padding:12px;margin-bottom:12px">'
            f'<div style="font-weight:700;color:#1d4ed8;font-size:15px;margin-bottom:8px">'
            f'🔮 Kỳ mới nhất — Dự đoán từ ánh xạ</div>'
            f'<div style="display:flex;gap:20px;flex-wrap:wrap">'
            f'<div><span style="color:#6b7280;font-size:12px">GĐB</span><br>'
            f'<b style="color:#c0392b;font-family:Consolas;font-size:22px">{rows[0][2]}</b></div>'
            f'<div><span style="color:#6b7280;font-size:12px">Chữ số GĐB</span><br>'
            f'<b style="color:#d97706;font-size:18px">{rows[0][3]}</b></div>'
            f'<div><span style="color:#6b7280;font-size:12px">Top5 ánh xạ GĐB</span><br>'
            f'<b style="font-size:16px;color:#166534">{rows[0][4]}</b></div>'
            f'</div></div>')
        st.markdown(kq_html, unsafe_allow_html=True)

    # Bảng tóm tắt: bỏ Đầu nhiều/Đuôi nhiều, giữ Top5 ánh xạ
    headers_sum = ["Kỳ","Ngày","GĐB","CS GĐB","Top5 GĐB","Top5 Đầu (ánh xạ)","Top5 Đuôi (ánh xạ)"]
    ccs_sum = {
        0: "color:#dc2626;font-weight:700;text-align:center",
        1: "color:#6b7280;text-align:center",
        2: "background:#fff7ed;color:#c0392b;font-weight:700;font-family:Consolas;font-size:16px;text-align:center",
        3: "background:#fff7ed;color:#d97706;font-weight:700;text-align:center",
        4: "background:#f0fdf4;color:#166534;font-weight:700",
        5: "background:#fff7ed;color:#059669;font-weight:700",
        6: "background:#f5f3ff;color:#059669;font-weight:700",
    }
    rows_sum = [[r[0],r[1],r[2],r[3],r[4],r[7],r[9]] for r in rows]
    st.markdown(htable(headers_sum, rows_sum, ccs_sum), unsafe_allow_html=True)

    # Chi tiết đầy đủ
    with st.expander("📊 Xem chi tiết Top5 Đầu / Đuôi + Toàn bộ tần suất"):
        headers_full = ["Kỳ","GĐB","Toàn bộ GĐB","Top5 Đầu","Top5 Đuôi"]
        ccs_full = {
            0: "color:#dc2626;font-weight:700;text-align:center",
            1: "font-family:Consolas;font-size:15px;font-weight:700;color:#c0392b;text-align:center",
            2: "color:#374151;font-size:11px",
            3: "background:#fff7ed;color:#059669;font-weight:700",
            4: "background:#f5f3ff;color:#059669;font-weight:700",
        }
        rows_full = [[r[0],r[2],r[5],r[7],r[9]] for r in rows]
        st.markdown(htable(headers_full, rows_full, ccs_full), unsafe_allow_html=True)

# ═══════════════════════════ MAIN ═══════════════════════════
def main():
    st.set_page_config(
        page_title="XỔ SỐ PRO", page_icon="🎲",
        layout="wide", initial_sidebar_state="collapsed",
    )
    st.markdown("""
    <style>
    [data-testid="collapsedControl"]{display:none}
    .block-container{padding:0.4rem 0.8rem 1rem !important;max-width:100%!important}
    /* Tab */
    .stTabs [data-baseweb="tab-list"]{gap:2px;border-bottom:2px solid #c0392b;margin-bottom:6px}
    .stTabs [data-baseweb="tab"]{
        background:#f1f1f1;border-radius:4px 4px 0 0;
        font-weight:700;font-size:13px;padding:6px 14px;color:#333}
    .stTabs [aria-selected="true"]{background:#c0392b!important;color:#fff!important}
    /* Button */
    .stButton>button{
        background:#c0392b!important;color:#fff!important;
        font-weight:700;border:none;border-radius:5px;font-size:14px}
    .stButton>button:hover{background:#a93226!important}
    /* Label */
    label{font-size:13px!important;color:#222!important;font-weight:600!important}
    hr{margin:6px 0!important}
    div[data-testid="stSuccessMessage"]{padding:6px 12px!important}
    </style>
    """, unsafe_allow_html=True)

    # ── CONTROL BAR ──
    c0,c1,c2,c3,c4,c5 = st.columns([1.1, 0.8, 1.8, 0.7, 0.7, 1.1])
    region   = c0.selectbox("Khu vực",["Miền Bắc","Miền Nam","Miền Trung"],key="region")
    today    = DAYS[datetime.now().weekday()]
    day      = c1.selectbox("Thứ",DAYS,index=DAYS.index(today),key="day")
    sl       = get_stations(region,day)
    station  = c2.selectbox("Đài",sl if sl else ["—"],key="station")
    show_g47 = c3.checkbox("G4-G7",False,key="sg47")
    c4.write("")  # spacer align
    load     = c5.button("📡 TẢI DỮ LIỆU",use_container_width=True)
    st.divider()

    if "raw"  not in st.session_state: st.session_state.raw  = []
    if "name" not in st.session_state: st.session_state.name = ""

    if load and station and station != "—":
        with st.spinner(f"Đang tải {station}..."):
            data = load_raw(station)
        st.session_state.raw  = data
        st.session_state.name = station
        if data: st.success(f"✅ {len(data)} kỳ — {station}")
        else:    st.error("❌ Không tải được!")

    raw = st.session_state.raw

    # ── LAYOUT: trái kết quả | phải phân tích ──
    if raw:
        col_r, col_main = st.columns([1, 3])
        with col_r:
            panel_ket_qua(raw, show_g47)
        with col_main:
            t1,t2,t3,t4,t5,t6,t7 = st.tabs([
                "Thiếu Đầu","Cầu List 0","Lô Lạ","Lô Xiên","Tài/Xỉu","Ánh Xạ GĐB","Debug",
            ])
            with t1: tab_thieu_dau(raw)
            with t2: tab_list0(raw)
            with t3: tab_lo_la(raw, region)
            with t4: tab_lo_xien(raw)
            with t5: tab_tai_xiu(raw)
            with t6: tab_anh_xa(raw)
            with t7: tab_debug(raw)
    else:
        st.info("👆 Chọn khu vực → thứ → đài rồi nhấn **TẢI DỮ LIỆU**")

if __name__ == "__main__":
    main()
