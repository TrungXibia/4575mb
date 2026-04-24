# -*- coding: utf-8 -*-
"""Phân Tích Xổ Số - Streamlit v3 (clean light theme)"""

import streamlit as st
import requests, json, itertools
from collections import Counter
from datetime import datetime
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# ══════════════════════════════════════════════════
# CONFIG & LỊCH
# ══════════════════════════════════════════════════
HEADERS = {"User-Agent": "Mozilla/5.0", "Referer": "https://www.kqxs88.live/"}
_API_BASE = "https://www.kqxs88.live/api/front/open/lottery/history/list/game?limitNum=60&gameCode="
_GAME_CODES = {
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
DAI_API = {n: _API_BASE + c for n,c in _GAME_CODES.items()}
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
DAYS_VI = ["Thứ 2","Thứ 3","Thứ 4","Thứ 5","Thứ 6","Thứ 7","Chủ Nhật"]

# ══════════════════════════════════════════════════
# NETWORK
# ══════════════════════════════════════════════════
@st.cache_resource
def _sess():
    s = requests.Session()
    r = Retry(total=3, backoff_factor=0.5,
              status_forcelist=[429,500,502,503,504],
              allowed_methods=frozenset(["GET"]))
    s.mount("https://", HTTPAdapter(max_retries=r))
    return s

def load_data(station: str) -> list:
    key = station
    if "Miền Bắc" in station and "75s" not in station:
        key = "Miền Bắc"
    url = DAI_API.get(key, "")
    if not url:
        return []
    try:
        r = _sess().get(url, headers=HEADERS, timeout=15)
        r.raise_for_status()
        return r.json().get("t", {}).get("issueList", [])
    except Exception as e:
        st.error(f"Lỗi tải: {e}")
        return []

# ══════════════════════════════════════════════════
# DATA PARSING
# ══════════════════════════════════════════════════
def parse_detail(item: dict) -> list:
    raw = item.get("detail", None)
    if isinstance(raw, list):
        out = []
        for x in raw:
            out.append(",".join(str(v).strip() for v in x) if isinstance(x,(list,tuple)) else str(x).strip())
        return out
    if isinstance(raw, str) and raw.strip():
        try:
            p = json.loads(raw)
            if isinstance(p, list):
                out = []
                for x in p:
                    out.append(",".join(str(v).strip() for v in x) if isinstance(x,(list,tuple)) else str(x).strip())
                return out
        except Exception:
            pass
        if "|" in raw:
            return [x.strip() for x in raw.split("|") if x.strip()]
        return [raw.strip()]
    for key in ("openCode","prizeNum","number","code","prizes"):
        val = item.get(key,"")
        if val and str(val).strip():
            s = str(val).strip()
            if "|" in s: return [x.strip() for x in s.split("|") if x.strip()]
            return [s]
    return []

def pf(item): 
    return [p.strip() for f in parse_detail(item) for p in str(f).split(",") if p.strip()]

def td(prizes): 
    return [p[-2:] for p in prizes if len(p)>=2 and p[-2:].isdigit()]

def list0(prizes):
    cnt = Counter(c for p in prizes for c in p if c.isdigit())
    return [str(d) for d in range(10) if not cnt.get(str(d),0)]

def miss_heads(prizes):
    heads=[p[-2] if len(p)>=2 else "0" for p in prizes if p.strip()]
    cnt=Counter(heads)
    return [str(d) for d in range(10) if not cnt.get(str(d),0)]

def bridge(a,b): 
    return sorted({x+y for x in a for y in b}|{y+x for x in a for y in b})

_CH = {str(d):[f"{i:02d}" for i in range(100) if str(d) in f"{i:02d}"] for d in range(10)}
_TG = {str(d):[f"{i:02d}" for i in range(100) if (i//10+i%10)%10==d] for d in range(10)}

def cham_tong(miss):
    s=set()
    for d in miss: s.update(_CH.get(d,[])); s.update(_TG.get(d,[]))
    return sorted(s)

def ky(item):   return str(item.get("turnNum","") or item.get("issueNum","") or "")
def dt(item):   return str(item.get("openTime","") or "").split(" ")[0]
def stations(region,day):
    if region=="Miền Bắc": return [f"Miền Bắc ({LICH_BAC.get(day,'')})", "VN Miền Bắc 75s","Miền Bắc 75s"]
    if region=="Miền Nam":  return LICH_NAM.get(day,[])
    return LICH_TRUNG.get(day,[])

# ══════════════════════════════════════════════════
# HTML TABLE BUILDER
# ══════════════════════════════════════════════════
def html_table(headers, rows, col_styles=None):
    """
    headers: list of str
    rows: list of list of str/html
    col_styles: dict {col_index: "css"} or {col_name: "css"}
    """
    th_style = "background:#c0392b;color:#fff;padding:7px 10px;font-size:13px;white-space:nowrap;border:1px solid #e0e0e0"
    
    # Build header index map
    hi = {h:i for i,h in enumerate(headers)}
    
    def cs(ci):
        if col_styles is None: return "padding:6px 8px;font-size:13px;border:1px solid #e8e8e8;white-space:nowrap"
        style = col_styles.get(ci, col_styles.get(headers[ci] if ci<len(headers) else "", ""))
        base = "padding:6px 8px;font-size:13px;border:1px solid #e8e8e8;white-space:nowrap;"
        return base + style

    html = '<div style="overflow-x:auto;border-radius:8px;box-shadow:0 1px 4px #ccc">'
    html += '<table style="border-collapse:collapse;width:100%;background:#fff">'
    html += "<thead><tr>" + "".join(f'<th style="{th_style}">{h}</th>' for h in headers) + "</tr></thead>"
    html += "<tbody>"
    for ri, row in enumerate(rows):
        bg = "#f9f9f9" if ri%2 else "#fff"
        html += f'<tr style="background:{bg}">'
        for ci, cell in enumerate(row):
            html += f'<td style="{cs(ci)}">{cell if cell is not None else ""}</td>'
        html += "</tr>"
    html += "</tbody></table></div>"
    return html

# ══════════════════════════════════════════════════
# RESULT PANEL (right sidebar)
# ══════════════════════════════════════════════════
PRIZE_CONF = [
    ("ĐB","#c0392b",1),("G1","#e67e22",1),("G2","#f39c12",2),
    ("G3","#27ae60",6),("G4","#2980b9",4),("G5","#8e44ad",6),
    ("G6","#16a085",3),("G7","#95a5a6",4),
]

def result_panel(raw, show_g47):
    if not raw:
        st.info("Chưa có dữ liệu")
        return
    for item in raw[:2]:
        detail = parse_detail(item)
        html = f"""
        <div style="background:#fff;border:1px solid #ddd;border-radius:8px;
                    padding:10px;margin-bottom:10px;font-family:Consolas,monospace">
          <div style="color:#c0392b;font-weight:700;font-size:13px;margin-bottom:6px">
            🎯 Kỳ {ky(item)} &nbsp;<span style="color:#888;font-size:11px">{dt(item)}</span>
          </div>
        """
        idx = 0
        for label, color, cnt in PRIZE_CONF:
            if not show_g47 and label in ("G4","G5","G6","G7"):
                idx += cnt; continue
            vals = []
            for _ in range(cnt):
                if idx < len(detail):
                    vals.append(detail[idx].strip()); idx += 1
            val_str = " &nbsp; ".join(f"<b>{v}</b>" for v in vals if v)
            if val_str:
                html += (f'<div style="display:flex;align-items:center;gap:6px;margin:3px 0">'
                         f'<span style="background:{color};color:#fff;border-radius:4px;'
                         f'padding:1px 6px;font-size:11px;font-weight:700;min-width:28px;text-align:center">{label}</span>'
                         f'<span style="font-size:14px;color:#222;letter-spacing:1px">{val_str}</span>'
                         f'</div>')
        html += "</div>"
        st.markdown(html, unsafe_allow_html=True)

    # Đầu/đuôi
    prizes = pf(raw[0])
    nums = td(prizes)
    h2t = {str(i):[] for i in range(10)}
    t2h = {str(i):[] for i in range(10)}
    for n in nums:
        h2t[n[0]].append(n[1]); t2h[n[1]].append(n[0])

    rows = [[str(i),",".join(sorted(h2t[str(i)])),str(i),",".join(sorted(t2h[str(i)]))] for i in range(10)]
    tbl = html_table(
        ["Đầu","Đuôi ra","Đuôi","Đầu ra"], rows,
        {0:"color:#c0392b;font-weight:700;text-align:center",
         1:"color:#2471a3",
         2:"color:#c0392b;font-weight:700;text-align:center",
         3:"color:#2471a3"}
    )
    st.markdown(f"**📊 Đầu / Đuôi**")
    st.markdown(tbl, unsafe_allow_html=True)

# ══════════════════════════════════════════════════
# TAB 1 — CẦU LIST 0
# ══════════════════════════════════════════════════
def tab_list0(raw):
    if not raw:
        st.info("Chọn đài và nhấn **Tải Dữ Liệu**")
        return

    with st.expander("🔍 Debug API (click nếu bảng trống)"):
        item0 = raw[0]
        st.write("Fields:", list(item0.keys()))
        for k,v in item0.items():
            st.code(f"{k}: {str(v)[:200]}")
        p0 = pf(item0)
        st.write("prizes_flat:", p0[:10])
        st.write("list0:", list0(p0))

    proc = [{"ky":ky(i),"dt":dt(i),"l0":list0(pf(i)),"res":td(pf(i))} for i in raw]

    headers = ["Kỳ","Ngày","List 0","Sót K0"] + [f"K{k}" for k in range(1,8)]
    col_styles = {
        0:"color:#c0392b;font-weight:700;text-align:center",
        1:"color:#7f8c8d",
        2:"background:#fff8e1;color:#e67e22;font-weight:700",
        3:"background:#e8f4fd;color:#2471a3;font-weight:700",
        **{4+k: "background:#eafaf1;color:#1e8449" for k in range(7)},
    }

    rows = []
    for i, curr in enumerate(proc):
        dan = bridge(curr["l0"], proc[i+1]["l0"]) if i+1 < len(proc) else []
        row = [
            curr["ky"], curr["dt"],
            " ".join(curr["l0"]) if curr["l0"] else "<span style='color:#bbb'>—</span>",
            " ".join(dan) if dan else "<span style='color:#bbb'>—</span>",
        ]
        cur = dan[:]
        for k in range(1,8):
            t = i-k
            if t < 0:
                row.append("")
            else:
                cur = sorted(set(cur) - set(proc[t]["res"]))
                if cur:
                    row.append(" ".join(cur))
                else:
                    row.append("<span style='color:#27ae60;font-weight:700'>✅ Trúng</span>")
        rows.append(row)

    st.markdown(html_table(headers, rows, col_styles), unsafe_allow_html=True)

# ══════════════════════════════════════════════════
# TAB 2 — THIẾU ĐẦU
# ══════════════════════════════════════════════════
def tab_thieu_dau(raw):
    if not raw:
        st.info("Chọn đài và nhấn **Tải Dữ Liệu**")
        return

    c1,c2 = st.columns(2)
    duoi_db = c1.checkbox("✅ Đuôi ĐB", True,  key="t2a")
    dau_db  = c1.checkbox("✅ Đầu ĐB",  False, key="t2b")
    duoi_g1 = c2.checkbox("✅ Đuôi G1", False, key="t2c")
    dau_g1  = c2.checkbox("✅ Đầu G1",  False, key="t2d")

    def targets(prizes):
        t = set()
        if prizes and len(prizes[0])>=2:
            if duoi_db: t.add(prizes[0][-2:])
            if dau_db:  t.add(prizes[0][:2])
        if len(prizes)>1 and len(prizes[1])>=2:
            if duoi_g1: t.add(prizes[1][-2:])
            if dau_g1:  t.add(prizes[1][:2])
        return t

    proc = [{"ky":ky(i),"dt":dt(i),"mh":miss_heads(pf(i)),"pf":pf(i)} for i in raw]

    headers = ["Kỳ","Ngày","Thiếu Đầu","Dàn Chạm+Tổng"] + [f"K{k}" for k in range(1,8)]
    col_styles = {
        0:"color:#c0392b;font-weight:700;text-align:center",
        1:"color:#7f8c8d",
        2:"background:#fff8e1;color:#e67e22;font-weight:700",
        3:"background:#e8f4fd;color:#2471a3",
    }

    rows = []
    for i, curr in enumerate(proc):
        dan = cham_tong(curr["mh"])
        row = [
            curr["ky"], curr["dt"],
            " ".join(curr["mh"]) if curr["mh"] else "—",
            " ".join(dan),
        ]
        for k in range(1,8):
            t = i-k
            if t<0:
                row.append("")
            else:
                hits = set(dan) & targets(proc[t]["pf"])
                if hits:
                    row.append(f"<span style='color:#27ae60;font-weight:700'>✅ {','.join(sorted(hits))}</span>")
                else:
                    row.append("<span style='color:#bbb'>—</span>")
        rows.append(row)

    st.markdown(html_table(headers, rows, col_styles), unsafe_allow_html=True)

# ══════════════════════════════════════════════════
# TAB 3 — LÔ LẠ
# ══════════════════════════════════════════════════
def _detect(prize, use_s, use_l, use_g, use_c):
    s = prize.strip()
    if len(s) < 2: return False, None
    if use_c:
        for i in range(len(s)-2):
            if len(set(s[i:i+3]))==1: return True, s[-2:]
    if use_l:
        if any(c>=2 for c in Counter(d for d in s if d.isdigit()).values()): return True, s[-2:]
    if use_g:
        if s == s[::-1]: return True, s[-2:]
    if use_s:
        if len(set(d for d in s if d.isdigit()))<=3: return True, s[-2:]
    return False, None

def tab_lo_la(raw, region):
    if not raw:
        st.info("Chọn đài và nhấn **Tải Dữ Liệu**")
        return

    c1,c2,c3 = st.columns(3)
    use_s  = c1.checkbox("≤3 chữ số duy nhất", True,  key="t3s")
    use_l  = c1.checkbox("Lặp",                False, key="t3l")
    use_g  = c2.checkbox("Gánh/Đảo",           False, key="t3g")
    use_c  = c2.checkbox("Lặp liên tiếp ≥3",   False, key="t3c")
    dup    = c3.checkbox("Giữ số trùng",        False, key="t3d")
    mode   = c3.radio("Nhị hợp", ["Mặc định","Chỉ 1 giải","Cả hai"], index=2,
                      horizontal=True, key="t3m")
    mv = {"Mặc định":0,"Chỉ 1 giải":1,"Cả hai":2}[mode]
    mx = 9 if "Bắc" in region else 13

    proc = []
    for item in raw:
        p = pf(item)
        lo_set = []
        for ci, prize in enumerate(p):
            if ci>mx: break
            found, _ = _detect(prize, use_s, use_l, use_g, use_c)
            if found:
                digits = [d for d in prize if d.isdigit()]
                lo_set.append("".join(sorted(digits) if dup else sorted(set(digits))))
        l0 = sorted(lo_set) if dup else sorted(set(lo_set))
        all_d = sorted(set(c for s in l0 for c in s if c.isdigit()))
        n1,nm = len(l0)==1, len(l0)>1
        show = (mv==0 and nm) or (mv==1 and n1) or (mv==2 and (n1 or nm))
        dan = sorted({a+b for a in all_d for b in all_d}) if show and all_d else []
        proc.append({"ky":ky(item),"dt":dt(item),"l0":l0,"dan":dan,"res":td(p),"show":show})

    headers = ["Kỳ","Ngày","List 0 Lạ","Dàn Nhị Hợp"] + [f"K{k}" for k in range(1,11)]
    col_styles = {
        0:"color:#c0392b;font-weight:700;text-align:center",
        1:"color:#7f8c8d",
        2:"background:#fef9e7;color:#e67e22;font-weight:700",
        3:"background:#eaf2ff;color:#2471a3;font-size:12px",
    }

    rows = []
    for i, curr in enumerate(proc):
        dan_disp = (" ".join(curr["dan"][:25])+"..." if len(curr["dan"])>25 else " ".join(curr["dan"]))
        row = [
            curr["ky"], curr["dt"],
            ",".join(curr["l0"]) if curr["l0"] else "",
            dan_disp if curr["show"] else "",
        ]
        cur = curr["dan"][:]
        for k in range(1,11):
            t = i-k
            if t<0 or not curr["show"]:
                row.append("")
            else:
                cur = sorted(set(cur)-set(proc[t]["res"]))
                row.append(" ".join(cur) if cur else "<span style='color:#27ae60;font-weight:700'>✅</span>")
        rows.append(row)

    st.markdown(html_table(headers, rows, col_styles), unsafe_allow_html=True)

# ══════════════════════════════════════════════════
# TAB 4 — LÔ XIÊN
# ══════════════════════════════════════════════════
def tab_lo_xien():
    st.markdown("### 🔢 Ghép Xiên Tự Động")
    cols = st.columns(4)
    groups = []
    for i,col in enumerate(cols,1):
        with col:
            st.markdown(f"**Nhóm {i}**")
            txt = st.text_area("", height=100, key=f"xg{i}",
                               placeholder="Nhập số,\ncách bởi dấu cách/phẩy",
                               label_visibility="collapsed")
            groups.append(sorted(set(n.strip() for n in txt.replace(","," ").split() if n.strip().isdigit())))

    oc1,oc2,oc3,oc4 = st.columns([2,1,1,1])
    sep = oc1.selectbox("Ký tự nối",["&",",","-"," "],key="xsep")
    x2  = oc2.checkbox("Xiên 2",True, key="xx2")
    x3  = oc3.checkbox("Xiên 3",True, key="xx3")
    x4  = oc4.checkbox("Xiên 4",True, key="xx4")

    bc1,bc2 = st.columns(2)
    quay = bc1.button("🔄 Tạo Xiên Quay (Nhóm 1)", use_container_width=True)
    nhom = bc2.button("🔗 Tạo Xiên Nhóm",          use_container_width=True)

    if quay:
        if len(groups[0])<2: st.warning("Nhập ít nhất 2 số ở Nhóm 1!")
        else:
            rc = st.columns(3)
            for idx,(k,use) in enumerate([(2,x2),(3,x3),(4,x4)]):
                if use:
                    combos = list(itertools.combinations(groups[0],k))
                    rc[idx].text_area(f"Xiên {k} — {len(combos)} cặp",
                                      ";\n".join(sep.join(c) for c in combos),
                                      height=200, key=f"qr{k}")
    if nhom:
        rc = st.columns(3)
        for idx,(k,use) in enumerate([(2,x2),(3,x3),(4,x4)]):
            if use:
                src = groups[:k]
                if all(src):
                    res = list(itertools.product(*src))
                    rc[idx].text_area(f"Xiên {k} — {len(res)} cặp",
                                      ";\n".join(sep.join(c) for c in res),
                                      height=200, key=f"nr{k}")
                else:
                    st.warning(f"Cần nhập đủ {k} nhóm!")

# ══════════════════════════════════════════════════
# TAB 5 — TÀI / XỈU
# ══════════════════════════════════════════════════
def bead_road_html(seq):
    ROWS,CS,PAD = 6,32,6
    col,row,prev = 0,0,None
    cells=[]
    for d in seq:
        r = d["r"]
        if prev is not None and (r!=prev or row>=ROWS):
            col+=1; row=0
        cx = PAD+col*(CS+3)+CS//2
        cy = PAD+row*(CS+3)+CS//2
        cells.append((cx,cy,"#c0392b" if r=="T" else "#2471a3",r,d["total"]))
        prev=r; row+=1

    W = PAD+(col+1)*(CS+3)+PAD
    H = PAD+ROWS*(CS+3)+PAD
    svgs=""
    for cx,cy,color,lbl,tot in cells:
        svgs += (f'<circle cx="{cx}" cy="{cy}" r="{CS//2-1}" fill="{color}" stroke="white" stroke-width="1.5"/>'
                 f'<text x="{cx}" y="{cy+5}" text-anchor="middle" fill="white" '
                 f'font-size="13" font-weight="bold" font-family="Arial">{lbl}</text>'
                 f'<text x="{cx+CS//2-1}" y="{cy+CS//2-1}" text-anchor="end" '
                 f'fill="rgba(255,255,255,0.6)" font-size="7">{tot}</text>')
    return (f'<div style="overflow-x:auto;background:#1a2c3d;border-radius:10px;padding:4px">'
            f'<svg width="{W}" height="{H}" xmlns="http://www.w3.org/2000/svg">'
            f'<rect width="{W}" height="{H}" fill="#1a2c3d"/>{svgs}</svg></div>')

def tab_tai_xiu(raw):
    if not raw:
        st.info("Chọn đài và nhấn **Tải Dữ Liệu**")
        return

    seq = []
    for item in reversed(raw):
        p = pf(item)
        gdb = p[0].strip() if p else ""
        total = sum(int(c) for c in gdb if c.isdigit())
        seq.append({"turn":ky(item),"gdb":gdb,"total":total,"r":"T" if total>=23 else "X"})

    tot_t = sum(1 for d in seq if d["r"]=="T")
    tot_x = len(seq)-tot_t
    last  = seq[-1]["r"]
    streak=1
    for d in reversed(seq[:-1]):
        if d["r"]==last: streak+=1
        else: break

    m1,m2,m3,m4 = st.columns(4)
    m1.metric("Tổng kỳ",  len(seq))
    m2.metric("🔴 Tài",   f"{tot_t} ({tot_t/len(seq)*100:.0f}%)")
    m3.metric("🔵 Xỉu",   f"{tot_x} ({tot_x/len(seq)*100:.0f}%)")
    m4.metric("Chuỗi",    f"{streak} {'Tài 🔴' if last=='T' else 'Xỉu 🔵'}")

    l = seq[-1]
    tx = "**TÀI 🔴**" if l["r"]=="T" else "**XỈU 🔵**"
    st.info(f"Kỳ mới nhất: **{l['turn']}** &nbsp;·&nbsp; GĐB: **{l['gdb']}** &nbsp;·&nbsp; Tổng chữ số: **{l['total']}** &nbsp;→&nbsp; {tx}")

    st.markdown("#### 🎱 Bead Road")
    st.markdown(bead_road_html(seq), unsafe_allow_html=True)

    st.markdown("#### 📋 20 Kỳ Gần Nhất")
    recent = seq[-20:]
    table_rows = []
    for i,d in enumerate(recent):
        s=1
        for j in range(i-1,-1,-1):
            if recent[j]["r"]==d["r"]: s+=1
            else: break
        color = "#c0392b" if d["r"]=="T" else "#2471a3"
        bg    = "#fff0f0" if d["r"]=="T" else "#f0f5ff"
        table_rows.append([
            d["turn"], d["gdb"], str(d["total"]),
            f'<span style="color:{color};font-weight:700">{"TÀI 🔴" if d["r"]=="T" else "XỈU 🔵"}</span>',
            f"{s} {'Tài' if d['r']=='T' else 'Xỉu'} liên tiếp",
        ])
    st.markdown(
        html_table(["Kỳ","GĐB","Tổng","Kết quả","Chuỗi"], list(reversed(table_rows)),
                   {0:"font-weight:700;color:#555;text-align:center",
                    1:"font-family:Consolas;font-size:14px",
                    2:"text-align:center;font-weight:700"}),
        unsafe_allow_html=True
    )

# ══════════════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════════════
def main():
    st.set_page_config(page_title="Phân Tích Xổ Số", page_icon="🎲",
                       layout="wide", initial_sidebar_state="expanded")

    # Minimal CSS — chỉ fix những thứ cần thiết, không override màu chữ
    st.markdown("""
    <style>
    .block-container { padding-top: 0.5rem !important; max-width: 100% !important; }
    .stButton > button {
        background: #c0392b !important; color: #fff !important;
        font-weight: 700; border: none; border-radius: 6px;
        padding: 8px 20px; font-size: 14px;
    }
    .stButton > button:hover { background: #a93226 !important; }
    .stTabs [data-baseweb="tab-list"] { gap: 4px; }
    .stTabs [data-baseweb="tab"] {
        background: #f0f2f6; border-radius: 6px 6px 0 0;
        font-weight: 600; font-size: 13px; padding: 6px 14px;
    }
    .stTabs [aria-selected="true"] {
        background: #c0392b !important; color: #fff !important;
    }
    </style>
    """, unsafe_allow_html=True)

    # ── Sidebar ──
    with st.sidebar:
        st.header("⚙️ Cấu Hình")
        region  = st.selectbox("Khu vực", ["Miền Bắc","Miền Nam","Miền Trung"])
        today   = DAYS_VI[datetime.now().weekday()]
        day     = st.selectbox("Thứ", DAYS_VI, index=DAYS_VI.index(today))
        sl      = stations(region, day)
        station = st.selectbox("Đài", sl) if sl else None
        show_g47= st.checkbox("Hiện G4-G7 trong kết quả", False)
        st.divider()
        load    = st.button("📡 Tải Dữ Liệu", use_container_width=True)
        st.caption("Nguồn: kqxs88.live")

    if "raw"   not in st.session_state: st.session_state.raw = []
    if "name"  not in st.session_state: st.session_state.name = ""

    if load and station:
        with st.spinner(f"Đang tải {station}..."):
            data = load_data(station)
        st.session_state.raw  = data
        st.session_state.name = station
        if data: st.success(f"✅ Đã tải **{len(data)} kỳ** từ **{station}**")
        else:    st.error("Không tải được dữ liệu!")

    raw = st.session_state.raw
    left, right = st.columns([3,1])

    with right:
        st.markdown(f"### 📋 Kết Quả{' — ' + st.session_state.name if st.session_state.name else ''}")
        result_panel(raw, show_g47)

    with left:
        if raw:
            st.caption(f"📡 **{st.session_state.name}** · {len(raw)} kỳ")
        t1,t2,t3,t4,t5 = st.tabs([
            "📋 Cầu List 0",
            "📉 Thiếu Đầu & Chạm Tổng",
            "🔮 Lô Lạ (Pattern)",
            "🔢 Lô Xiên",
            "🎲 Tài / Xỉu",
        ])
        with t1: tab_list0(raw)
        with t2: tab_thieu_dau(raw)
        with t3: tab_lo_la(raw, region)
        with t4: tab_lo_xien()
        with t5: tab_tai_xiu(raw)

if __name__=="__main__":
    main()
