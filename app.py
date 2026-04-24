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
    TH = (f"background:#34495e;color:#fff;padding:8px 12px;"
          f"font-size:{fs}px;white-space:nowrap;border:1px solid #2c3e50;"
          f"position:sticky;top:0")
    def td_s(ci):
        base = f"padding:6px 10px;font-size:{fs}px;border:1px solid #ecf0f1;white-space:nowrap"
        ex = (col_css or {}).get(ci, (col_css or {}).get(
            headers[ci] if ci < len(headers) else "", ""))
        return base + (";" + ex if ex else "")
    ths = "".join(f'<th style="{TH}">{h}</th>' for h in headers)
    trs = ""
    for ri, row in enumerate(rows):
        bg = "#f8f9fa" if ri % 2 else "#ffffff"
        tds = "".join(f'<td style="{td_s(ci)}">{c if c is not None else ""}</td>'
                      for ci, c in enumerate(row))
        trs += f'<tr style="background:{bg}">{tds}</tr>'
    return (f'<div style="overflow:auto;max-height:620px;border-radius:8px;'
            f'box-shadow:0 2px 8px rgba(0,0,0,.12);margin:6px 0">'
            f'<table style="border-collapse:collapse;width:100%;background:#fff">'
            f'<thead style="position:sticky;top:0;z-index:1"><tr>{ths}</tr></thead>'
            f'<tbody>{trs}</tbody></table></div>')

# ═══════════════════════════ KẾT QUẢ PANEL ═══════════════════════════
def panel_ket_qua(raw, show_g47):
    """Hiển thị kết quả xổ số + thống kê Đầu/Đuôi nhiều + GĐB nhiều."""
    if not raw: return
    item = raw[0]
    detail = parse_detail(item)

    # ── Kết quả giải ──
    html_prizes = ""
    idx = 0
    for label, color, cnt in PRIZE_CONF:
        if not show_g47 and label in ("G4","G5","G6","G7"):
            idx += cnt; continue
        vals = []
        for _ in range(cnt):
            if idx < len(detail): vals.append(detail[idx].strip()); idx += 1
        if not any(vals): continue
        nums_html = "&nbsp;&nbsp;".join(
            f'<b style="font-size:15px;font-family:Consolas;letter-spacing:2px;color:#1a1a2e">{v}</b>'
            for v in vals if v)
        html_prizes += (
            f'<div style="display:flex;align-items:center;gap:8px;'
            f'padding:4px 0;border-bottom:1px solid #f0f0f0">'
            f'<span style="background:{color};color:#fff;border-radius:4px;'
            f'padding:2px 8px;font-size:11px;font-weight:700;min-width:32px;'
            f'text-align:center;flex-shrink:0">{label}</span>'
            f'{nums_html}</div>')

    # ── Thống kê đầu/đuôi từ NHIỀU kỳ ──
    prizes_all = get_prizes(item)
    nums2d = get_2d(prizes_all)

    # Đầu nhiều / Đuôi nhiều (kỳ hiện tại)
    cnt_dau  = Counter(n[0] for n in nums2d)
    cnt_duoi = Counter(n[1] for n in nums2d)

    # GĐB nhiều (5 kỳ gần nhất)
    gdb_digits = []
    for it in raw[:5]:
        p = get_prizes(it)
        if p: gdb_digits.append(p[0].strip())

    # Đầu ra / Đuôi ra (từ các lô 2 số)
    h2t = {str(i): [] for i in range(10)}
    t2h = {str(i): [] for i in range(10)}
    for n in nums2d:
        h2t[n[0]].append(n[1])
        t2h[n[1]].append(n[0])

    def badge(digit, count, max_count):
        """Tạo badge màu theo tần suất."""
        ratio = count / max_count if max_count else 0
        if ratio >= 0.8:   bg, fg = "#c0392b", "#fff"
        elif ratio >= 0.5: bg, fg = "#e67e22", "#fff"
        elif ratio >= 0.3: bg, fg = "#f39c12", "#000"
        else:              bg, fg = "#ecf0f1", "#555"
        return (f'<span style="background:{bg};color:{fg};border-radius:4px;'
                f'padding:1px 6px;font-size:12px;font-weight:700;margin:1px;'
                f'display:inline-block">{digit}({count})</span>')

    max_dau  = max(cnt_dau.values(),  default=1)
    max_duoi = max(cnt_duoi.values(), default=1)

    # Bảng Đầu/Đuôi 10 hàng
    dt_rows = ""
    for i in range(10):
        d = str(i)
        cnt_d = cnt_dau.get(d, 0)
        cnt_t = cnt_duoi.get(d, 0)
        duoi_ra = ",".join(sorted(h2t.get(d, [])))
        dau_ra  = ",".join(sorted(t2h.get(d, [])))
        # màu hàng nếu nhiều
        bg = "#fff3e0" if cnt_d >= 3 else ("#e8f5e9" if cnt_t >= 3 else "")
        bg_style = f"background:{bg};" if bg else ""
        dt_rows += (
            f'<tr style="{bg_style}">'
            f'<td style="text-align:center;font-weight:700;color:#c0392b;'
            f'font-family:Consolas;padding:3px 6px;border:1px solid #ecf0f1">{d}</td>'
            f'<td style="font-weight:700;color:{"#c0392b" if cnt_d>=3 else "#555"};'
            f'text-align:center;padding:3px 6px;border:1px solid #ecf0f1">{cnt_d}</td>'
            f'<td style="color:#2471a3;font-family:Consolas;padding:3px 8px;'
            f'border:1px solid #ecf0f1">{duoi_ra}</td>'
            f'<td style="width:8px;border:none"></td>'
            f'<td style="text-align:center;font-weight:700;color:#c0392b;'
            f'font-family:Consolas;padding:3px 6px;border:1px solid #ecf0f1">{d}</td>'
            f'<td style="font-weight:700;color:{"#1e8449" if cnt_t>=3 else "#555"};'
            f'text-align:center;padding:3px 6px;border:1px solid #ecf0f1">{cnt_t}</td>'
            f'<td style="color:#2471a3;font-family:Consolas;padding:3px 8px;'
            f'border:1px solid #ecf0f1">{dau_ra}</td>'
            f'</tr>')

    dau_nhieu  = sorted([d for d,c in cnt_dau.items()  if c >= 3], key=lambda x: -cnt_dau[x])
    duoi_nhieu = sorted([d for d,c in cnt_duoi.items() if c >= 3], key=lambda x: -cnt_duoi[x])
    dau_badges  = "".join(badge(d, cnt_dau[d],  max_dau)  for d in dau_nhieu)  or '<span style="color:#aaa">—</span>'
    duoi_badges = "".join(badge(d, cnt_duoi[d], max_duoi) for d in duoi_nhieu) or '<span style="color:#aaa">—</span>'

    # GĐB 5 kỳ
    gdb_html = "".join(
        f'<span style="background:#34495e;color:#fff;border-radius:4px;'
        f'padding:2px 8px;margin:2px;font-family:Consolas;font-weight:700;'
        f'font-size:14px">{g}</span>'
        for g in gdb_digits)

    col1, col2 = st.columns([2, 3])
    with col1:
        st.markdown(
            f'<div style="background:#fff;border:2px solid #dee2e6;border-radius:10px;'
            f'padding:12px;font-family:Consolas">'
            f'<div style="color:#c0392b;font-weight:700;font-size:14px;margin-bottom:8px">'
            f'🎯 KỲ {ky(item)} &nbsp;·&nbsp;'
            f'<span style="color:#7f8c8d;font-size:12px">{ngay(item)}</span></div>'
            f'{html_prizes}</div>',
            unsafe_allow_html=True)

        # GĐB 5 kỳ gần nhất
        st.markdown(
            f'<div style="background:#2c3e50;border-radius:8px;padding:10px;margin-top:8px">'
            f'<div style="color:#95a5a6;font-size:11px;margin-bottom:6px">🎰 GĐB 5 KỲ GẦN NHẤT</div>'
            f'{gdb_html}</div>',
            unsafe_allow_html=True)

    with col2:
        st.markdown(
            f'<div style="background:#fff;border:2px solid #dee2e6;border-radius:10px;padding:10px">'
            # Đầu nhiều / Đuôi nhiều banner
            f'<div style="display:flex;gap:12px;margin-bottom:8px;flex-wrap:wrap">'
            f'<div style="flex:1;background:#fff3e0;border-radius:6px;padding:6px 10px">'
            f'<div style="font-size:11px;font-weight:700;color:#e67e22;margin-bottom:4px">🔴 ĐẦU NHIỀU (≥3)</div>'
            f'{dau_badges}</div>'
            f'<div style="flex:1;background:#e8f5e9;border-radius:6px;padding:6px 10px">'
            f'<div style="font-size:11px;font-weight:700;color:#1e8449;margin-bottom:4px">🟢 ĐUÔI NHIỀU (≥3)</div>'
            f'{duoi_badges}</div>'
            f'</div>'
            # Bảng đầu/đuôi
            f'<table style="border-collapse:collapse;width:100%;font-size:12px">'
            f'<tr>'
            f'<th style="background:#34495e;color:#fff;padding:4px 6px;text-align:center">Đầu</th>'
            f'<th style="background:#34495e;color:#fff;padding:4px 6px;text-align:center">SL</th>'
            f'<th style="background:#34495e;color:#fff;padding:4px 6px">Đuôi ra</th>'
            f'<th style="width:8px;background:transparent"></th>'
            f'<th style="background:#34495e;color:#fff;padding:4px 6px;text-align:center">Đuôi</th>'
            f'<th style="background:#34495e;color:#fff;padding:4px 6px;text-align:center">SL</th>'
            f'<th style="background:#34495e;color:#fff;padding:4px 6px">Đầu ra</th>'
            f'</tr>'
            f'{dt_rows}'
            f'</table></div>',
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

    headers = ["Kỳ","Ngày","Thiếu Đầu","Dàn Chạm+Tổng",
               "K1","K2","K3","K4","K5","K6","K7"]
    ccs = {
        0: "color:#c0392b;font-weight:700;text-align:center",
        1: "color:#7f8c8d;text-align:center",
        2: "background:#fff8e1;color:#d35400;font-weight:700;text-align:center",
        3: "background:#eaf2ff;color:#1a5276;font-size:12px",
    }
    for k in range(4, 11): ccs[k] = "background:#eafaf1;color:#1e8449;font-size:12px"

    rows = []
    for i, curr in enumerate(proc):
        dan = cham_tong(curr["mh"])
        row = [curr["ky"], curr["ngay"],
               " ".join(curr["mh"]) if curr["mh"] else "—",
               " ".join(dan) if dan else "—"]
        for k in range(1, 8):
            t = i - k
            if t < 0:
                row.append("")
            else:
                hits = set(dan) & targets(proc[t]["pf"])
                if hits:
                    row.append(f'<b style="color:#27ae60">✅ {",".join(sorted(hits))}</b>')
                else:
                    row.append('<span style="color:#bbb">—</span>')
        rows.append(row)

    st.markdown(htable(headers, rows, ccs), unsafe_allow_html=True)

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

    headers = ["Kỳ","Ngày","List 0","Kỳ-1","Kỳ-2",
               "Sót K0","K1","K2","K3","K4","K5","K6","K7"]
    ccs = {
        0: "color:#c0392b;font-weight:700;text-align:center",
        1: "color:#7f8c8d;text-align:center",
        2: "background:#fff8e1;color:#d35400;font-weight:700;text-align:center",
        3: "color:#b7950b;text-align:center",
        4: "color:#b7950b;text-align:center",
        5: "background:#eaf2ff;color:#1a5276;font-weight:700",
    }
    for k in range(6, 13): ccs[k] = "background:#eafaf1;color:#1e8449;font-size:12px"

    rows = []
    for i, curr in enumerate(proc):
        k0 = bridge(curr["l0"], proc[i+1]["l0"]) if i+1 < len(proc) else []
        k0 = diff(k0, curr["res"])
        row = [
            curr["ky"], curr["ngay"],
            " ".join(curr["l0"]) if curr["l0"] else "—",
            " ".join(proc[i-1]["l0"]) if i >= 1 else "",
            " ".join(proc[i-2]["l0"]) if i >= 2 else "",
            " ".join(k0) if k0 else "—",
        ]
        cur = k0[:]
        for k in range(1, 8):
            t = i - k
            if t < 0: row.append("")
            else:
                cur = diff(cur, proc[t]["res"])
                row.append(" ".join(cur) if cur
                           else '<b style="color:#27ae60">✅</b>')
        rows.append(row)

    st.markdown(htable(headers, rows, ccs), unsafe_allow_html=True)

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

    headers = ["Kỳ","Ngày","List 0 Lạ","Dàn Nhị Hợp",
               "K1","K2","K3","K4","K5","K6","K7","K8","K9","K10"]
    ccs = {
        0: "color:#c0392b;font-weight:700;text-align:center",
        1: "color:#7f8c8d;text-align:center",
        2: "background:#fef9e7;color:#d35400;font-weight:700;text-align:center",
        3: "background:#eaf2ff;color:#1a5276;font-size:12px",
    }
    for k in range(4, 14): ccs[k] = "background:#eafaf1;color:#1e8449;font-size:12px"

    rows = []
    for i, curr in enumerate(proc):
        dan_disp = (" ".join(curr["dan"][:25]) + ("…" if len(curr["dan"]) > 25 else "")
                   if curr["show"] else "")
        row = [curr["ky"], curr["ngay"],
               ",".join(curr["l0"]) if curr["l0"] else "",
               dan_disp]
        cur = curr["dan"][:]
        for k in range(1, 11):
            t = i - k
            if t < 0 or not curr["show"]: row.append("")
            else:
                cur = diff(cur, proc[t]["res"])
                row.append(" ".join(cur) if cur
                           else '<b style="color:#27ae60">✅</b>')
        rows.append(row)

    st.markdown(htable(headers, rows, ccs), unsafe_allow_html=True)

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

# ═══════════════════════════ MAIN ═══════════════════════════
def main():
    st.set_page_config(
        page_title="Phân Tích Xổ Số Pro",
        page_icon="🎲",
        layout="wide",
        initial_sidebar_state="collapsed",
    )

    # CSS tối giản — không override màu chữ
    st.markdown("""
    <style>
    [data-testid="collapsedControl"] { display: none }
    .block-container { padding: 0.5rem 1rem 1rem !important; max-width: 100% !important }
    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 3px; border-bottom: 3px solid #2c3e50; margin-bottom: 8px
    }
    .stTabs [data-baseweb="tab"] {
        background: #ecf0f1; border-radius: 6px 6px 0 0;
        font-weight: 700; font-size: 13px; padding: 8px 18px;
        color: #2c3e50; border: 1px solid #bdc3c7
    }
    .stTabs [aria-selected="true"] {
        background: #c0392b !important; color: #fff !important;
        border-color: #c0392b
    }
    /* Buttons */
    .stButton > button {
        background: #2c3e50 !important; color: #fff !important;
        font-weight: 700; border: none; border-radius: 6px;
        padding: 8px 20px; font-size: 14px; width: 100%
    }
    .stButton > button:hover { background: #c0392b !important }
    /* Selectbox & checkbox label rõ ràng */
    label { font-size: 13px !important; color: #2c3e50 !important; font-weight: 600 !important }
    .stSelectbox > label { font-size: 13px !important }
    /* Divider */
    hr { margin: 8px 0 !important }
    </style>
    """, unsafe_allow_html=True)

    # ── HEADER ──
    today_str = datetime.now().strftime("%H:%M  %d/%m/%Y")
    st.markdown(
        f'<div style="background:#2c3e50;color:#fff;padding:10px 16px;'
        f'border-radius:8px;margin-bottom:10px;display:flex;'
        f'align-items:center;justify-content:space-between">'
        f'<span style="font-size:20px;font-weight:800">🎲 PHÂN TÍCH XỔ SỐ PRO</span>'
        f'<span style="font-size:12px;color:#95a5a6">{today_str}</span>'
        f'</div>',
        unsafe_allow_html=True)

    # ── CONTROL BAR ──
    cc = st.columns([1.2, 0.9, 2, 0.9, 1.2])

    region = cc[0].selectbox(
        "Khu vực", ["Miền Bắc", "Miền Nam", "Miền Trung"], key="region")
    today  = DAYS[datetime.now().weekday()]
    day    = cc[1].selectbox("Thứ", DAYS, index=DAYS.index(today), key="day")
    sl     = get_stations(region, day)
    station = cc[2].selectbox("Đài xổ số", sl if sl else ["—"], key="station")
    show_g47 = cc[3].checkbox("Hiện G4–G7", False, key="sg47")
    load   = cc[4].button("📡 TẢI DỮ LIỆU")

    st.divider()

    # ── STATE ──
    if "raw"  not in st.session_state: st.session_state.raw  = []
    if "name" not in st.session_state: st.session_state.name = ""

    if load and station and station != "—":
        with st.spinner(f"Đang tải {station}..."):
            data = load_raw(station)
        st.session_state.raw  = data
        st.session_state.name = station
        if data: st.success(f"✅ Đã tải **{len(data)} kỳ** từ **{station}**")
        else:    st.error("❌ Không tải được dữ liệu!")

    raw = st.session_state.raw

    # ── KẾT QUẢ + THỐNG KÊ ──
    if raw:
        panel_ket_qua(raw, show_g47)
        st.divider()

    # ── TABS ──
    t1, t2, t3, t4, t5, t6 = st.tabs([
        "📉 Thiếu Đầu & Chạm Tổng",
        "📋 Cầu List 0",
        "🔮 Lô Lạ",
        "🔢 Lô Xiên",
        "🎲 Tài / Xỉu",
        "🔧 Debug API",
    ])
    with t1: tab_thieu_dau(raw)
    with t2: tab_list0(raw)
    with t3: tab_lo_la(raw, region)
    with t4: tab_lo_xien(raw)
    with t5: tab_tai_xiu(raw)
    with t6: tab_debug(raw)

if __name__ == "__main__":
    main()
