# -*- coding: utf-8 -*-
import streamlit as st, requests, json, itertools
from collections import Counter
from datetime import datetime
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# ════════════════════════════════════════════════════
# DỮ LIỆU
# ════════════════════════════════════════════════════
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

GIAI_MB = ["ĐB","G1","G2-1","G2-2",
           "G3-1","G3-2","G3-3","G3-4","G3-5","G3-6",
           "G4-1","G4-2","G4-3","G4-4",
           "G5-1","G5-2","G5-3","G5-4","G5-5","G5-6",
           "G6-1","G6-2","G6-3","G7-1","G7-2","G7-3","G7-4"]

PRIZE_CONF = [
    ("ĐB","#c0392b",1),("G1","#e67e22",1),("G2","#d4ac0d",2),
    ("G3","#1e8449",6),("G4","#2471a3",4),("G5","#6c3483",6),
    ("G6","#117a65",3),("G7","#717d7e",4),
]

def get_stations(region, day):
    if region=="Miền Bắc":
        t = LICH_BAC.get(day,"")
        return [f"Miền Bắc ({t})","VN Miền Bắc 75s","Miền Bắc 75s"]
    if region=="Miền Nam": return LICH_NAM.get(day,[])
    return LICH_TRUNG.get(day,[])

# ════════════════════════════════════════════════════
# NETWORK
# ════════════════════════════════════════════════════
HEADERS = {"User-Agent":"Mozilla/5.0","Referer":"https://www.kqxs88.live/"}

@st.cache_resource
def _sess():
    s = requests.Session()
    s.mount("https://", HTTPAdapter(max_retries=Retry(
        total=3, backoff_factor=0.5,
        status_forcelist=[429,500,502,503,504],
        allowed_methods=frozenset(["GET"]))))
    return s

def load_raw(station:str) -> list:
    key = "Miền Bắc" if ("Miền Bắc" in station and "75s" not in station) else station
    url = API.get(key,"")
    if not url: return []
    try:
        r = _sess().get(url, headers=HEADERS, timeout=15)
        r.raise_for_status()
        return r.json().get("t",{}).get("issueList",[])
    except Exception as e:
        st.error(f"Lỗi: {e}"); return []

# ════════════════════════════════════════════════════
# PARSE
# ════════════════════════════════════════════════════
def parse_detail(item:dict) -> list:
    raw = item.get("detail", None)
    def _from_list(lst):
        return [",".join(str(v).strip() for v in x) if isinstance(x,(list,tuple))
                else str(x).strip() for x in lst]
    if isinstance(raw, list): return _from_list(raw)
    if isinstance(raw, str) and raw.strip():
        try:
            p = json.loads(raw)
            if isinstance(p, list): return _from_list(p)
        except: pass
        if "|" in raw: return [x.strip() for x in raw.split("|") if x.strip()]
        return [raw.strip()]
    for k in ("openCode","prizeNum","number"):
        v = str(item.get(k,"")).strip()
        if v: return [x.strip() for x in v.split("|")] if "|" in v else [v]
    return []

def get_prizes(item):
    return [p.strip() for f in parse_detail(item) for p in str(f).split(",") if p.strip()]

def get_2d(prizes):
    return [p[-2:] for p in prizes if len(p)>=2 and p[-2:].isdigit()]

def get_list0(prizes, idxs=None):
    """Chữ số không xuất hiện. idxs=None → toàn bộ giải"""
    src = [prizes[i] for i in idxs if i<len(prizes)] if idxs else prizes
    cnt = Counter(c for p in src for c in p if c.isdigit())
    return [str(d) for d in range(10) if not cnt.get(str(d),0)]

def miss_heads(prizes):
    h = [p[-2] if len(p)>=2 else "0" for p in prizes if p.strip()]
    cnt = Counter(h)
    return [str(d) for d in range(10) if not cnt.get(str(d),0)]

def bridge(a,b):
    return sorted({x+y for x in a for y in b}|{y+x for x in a for y in b})

_CH = {str(d):[f"{i:02d}" for i in range(100) if str(d) in f"{i:02d}"] for d in range(10)}
_TG = {str(d):[f"{i:02d}" for i in range(100) if (i//10+i%10)%10==d] for d in range(10)}

def cham_tong(miss):
    s=set()
    for d in miss: s.update(_CH.get(d,[])); s.update(_TG.get(d,[]))
    return sorted(s)

def ky(item):  return str(item.get("turnNum","") or item.get("issueNum","") or "")
def ngay(item): return str(item.get("openTime","") or "").split(" ")[0]

# ════════════════════════════════════════════════════
# HTML TABLE (dùng khắp nơi)
# ════════════════════════════════════════════════════
def htable(headers, rows, col_css=None, font_size=13):
    TH = (f"background:#2c3e50;color:#fff;padding:8px 10px;"
          f"font-size:{font_size}px;white-space:nowrap;"
          f"border:1px solid #bdc3c7;text-align:center")
    def td_css(ci):
        base = (f"padding:6px 9px;font-size:{font_size}px;"
                f"border:1px solid #e0e0e0;white-space:nowrap")
        extra = (col_css or {}).get(ci, (col_css or {}).get(
            headers[ci] if ci<len(headers) else "", ""))
        return base + (";" + extra if extra else "")

    ths = "".join(f'<th style="{TH}">{h}</th>' for h in headers)
    trs = ""
    for ri, row in enumerate(rows):
        bg = "#f9f9f9" if ri%2 else "#ffffff"
        tds = "".join(f'<td style="{td_css(ci)}">{c or ""}</td>'
                      for ci,c in enumerate(row))
        trs += f'<tr style="background:{bg}">{tds}</tr>'
    return (f'<div style="overflow-x:auto;border-radius:8px;'
            f'box-shadow:0 1px 6px #ccc;margin:8px 0">'
            f'<table style="border-collapse:collapse;width:100%;background:#fff">'
            f'<thead><tr>{ths}</tr></thead><tbody>{trs}</tbody></table></div>')

# ════════════════════════════════════════════════════
# KẾT QUẢ + ĐẦU ĐUÔI
# ════════════════════════════════════════════════════
def show_result_header(raw, show_g47):
    if not raw: return
    item = raw[0]
    detail = parse_detail(item)
    k0 = ky(item); d0 = ngay(item)

    cards = ""
    idx = 0
    for label, color, cnt in PRIZE_CONF:
        if not show_g47 and label in ("G4","G5","G6","G7"):
            idx += cnt; continue
        vals = []
        for _ in range(cnt):
            if idx < len(detail): vals.append(detail[idx].strip()); idx+=1
        if not vals: continue
        nums_html = "&nbsp;&nbsp;".join(
            f'<span style="font-size:16px;font-weight:700;color:#222;'
            f'font-family:Consolas,monospace;letter-spacing:2px">{v}</span>'
            for v in vals if v)
        if nums_html:
            cards += (f'<div style="display:flex;align-items:center;gap:8px;'
                      f'padding:4px 0;border-bottom:1px solid #f0f0f0">'
                      f'<span style="background:{color};color:#fff;border-radius:4px;'
                      f'padding:2px 8px;font-size:12px;font-weight:700;min-width:32px;'
                      f'text-align:center">{label}</span>{nums_html}</div>')

    # Đầu/Đuôi
    prizes = get_prizes(item)
    nums2d = get_2d(prizes)
    h2t = {str(i):[] for i in range(10)}
    t2h = {str(i):[] for i in range(10)}
    for n in nums2d:
        h2t[n[0]].append(n[1]); t2h[n[1]].append(n[0])
    dt_rows = "".join(
        f'<tr><td style="color:#c0392b;font-weight:700;text-align:center;'
        f'padding:3px 6px;font-family:Consolas">{i}</td>'
        f'<td style="color:#2471a3;padding:3px 6px;font-family:Consolas">'
        f'{",".join(sorted(h2t[str(i)]))}</td>'
        f'<td style="padding:3px 6px"></td>'
        f'<td style="color:#c0392b;font-weight:700;text-align:center;'
        f'padding:3px 6px;font-family:Consolas">{i}</td>'
        f'<td style="color:#2471a3;padding:3px 6px;font-family:Consolas">'
        f'{",".join(sorted(t2h[str(i)]))}</td></tr>'
        for i in range(10))
    dt_table = (f'<table style="border-collapse:collapse;font-size:12px;width:100%">'
                f'<tr><th style="background:#eee;padding:4px 6px">Đầu</th>'
                f'<th style="background:#eee;padding:4px 6px">Đuôi ra</th>'
                f'<th style="width:10px"></th>'
                f'<th style="background:#eee;padding:4px 6px">Đuôi</th>'
                f'<th style="background:#eee;padding:4px 6px">Đầu ra</th></tr>'
                f'{dt_rows}</table>')

    col_r, col_dt = st.columns([3,2])
    with col_r:
        st.markdown(
            f'<div style="background:#fff;border:2px solid #e0e0e0;border-radius:10px;'
            f'padding:12px;font-family:Consolas">'
            f'<div style="color:#c0392b;font-weight:700;font-size:14px;margin-bottom:8px">'
            f'🎯 KỲ {k0} &nbsp;·&nbsp; <span style="color:#888;font-size:12px">{d0}</span>'
            f'</div>{cards}</div>',
            unsafe_allow_html=True)
    with col_dt:
        st.markdown(
            f'<div style="background:#fff;border:2px solid #e0e0e0;border-radius:10px;'
            f'padding:12px">'
            f'<div style="font-weight:700;font-size:13px;color:#2c3e50;margin-bottom:8px">'
            f'📊 THỐNG KÊ ĐẦU / ĐUÔI — Kỳ {k0}</div>'
            f'{dt_table}</div>',
            unsafe_allow_html=True)

# ════════════════════════════════════════════════════
# TAB 1 — THIẾU ĐẦU & CHẠM TỔNG
# ════════════════════════════════════════════════════
def tab_thieu_dau(raw):
    if not raw: st.info("Chọn đài → Tải dữ liệu"); return

    c1,c2,c3,c4 = st.columns(4)
    duoi_db = c1.checkbox("Đuôi ĐB", True,  key="t2a")
    dau_db  = c2.checkbox("Đầu ĐB",  False, key="t2b")
    duoi_g1 = c3.checkbox("Đuôi G1", False, key="t2c")
    dau_g1  = c4.checkbox("Đầu G1",  False, key="t2d")

    def targets(prizes):
        t = set()
        if prizes:
            db = prizes[0].strip()
            if len(db)>=2:
                if duoi_db: t.add(db[-2:])
                if dau_db:  t.add(db[:2])
        if len(prizes)>1:
            g1 = prizes[1].strip()
            if len(g1)>=2:
                if duoi_g1: t.add(g1[-2:])
                if dau_g1:  t.add(g1[:2])
        return t

    proc = []
    for item in raw:
        p = get_prizes(item)
        proc.append({"ky":ky(item),"ngay":ngay(item),
                     "mh":miss_heads(p),"pf":p,"2d":get_2d(p)})

    headers = ["Kỳ","Ngày","Thiếu Đầu","Dàn Chạm+Tổng",
               "K1","K2","K3","K4","K5","K6","K7"]
    col_css = {
        0:"color:#c0392b;font-weight:700;text-align:center",
        1:"color:#7f8c8d;text-align:center",
        2:"background:#fff8e1;color:#e67e22;font-weight:700;text-align:center",
        3:"background:#eaf2ff;color:#1a5276;font-size:12px",
    }
    for k in range(4,11):
        col_css[k]="background:#eafaf1;color:#1e8449;font-size:12px"

    rows=[]
    for i, curr in enumerate(proc):
        dan = cham_tong(curr["mh"])
        row=[curr["ky"], curr["ngay"],
             " ".join(curr["mh"]) if curr["mh"] else "—",
             " ".join(dan) if dan else "—"]
        for k in range(1,8):
            t=i-k
            if t<0: row.append("")
            else:
                hits = set(dan) & targets(proc[t]["pf"])
                if hits:
                    row.append(f'<span style="color:#27ae60;font-weight:700">'
                               f'✅ {",".join(sorted(hits))}</span>')
                else:
                    row.append('<span style="color:#bbb">—</span>')
        rows.append(row)

    st.markdown(htable(headers, rows, col_css), unsafe_allow_html=True)

# ════════════════════════════════════════════════════
# TAB 2 — CẦU LIST 0 (TRUYỀN THỐNG)
# ════════════════════════════════════════════════════
def tab_list0(raw):
    if not raw: st.info("Chọn đài → Tải dữ liệu"); return

    st.markdown("**Chọn giải để tính List 0:**")
    # Checkbox chọn giải — 3 hàng
    selected = []
    cols_ck = st.columns(9)
    defaults = {2,3}  # G1, G2-1 mặc định
    for i, label in enumerate(GIAI_MB):
        col = cols_ck[i % 9]
        val = col.checkbox(label, value=(i in defaults), key=f"gl0_{i}")
        if val:
            selected.append(i)

    proc=[]
    for item in raw:
        p = get_prizes(item)
        l0 = get_list0(p, selected) if selected else get_list0(p)
        proc.append({"ky":ky(item),"ngay":ngay(item),"l0":l0,"res":get_2d(p),"pf":p})

    headers = ["Kỳ","Ngày","List 0","Kỳ-1 List0","Kỳ-2 List0",
               "Sót K0","K1","K2","K3","K4","K5","K6","K7"]
    col_css = {
        0:"color:#c0392b;font-weight:700;text-align:center",
        1:"color:#7f8c8d;text-align:center",
        2:"background:#fff8e1;color:#e67e22;font-weight:700;text-align:center",
        3:"background:#fef9e7;color:#b7950b;text-align:center",
        4:"background:#fef9e7;color:#b7950b;text-align:center",
        5:"background:#eaf2ff;color:#1a5276;font-weight:700",
    }
    for k in range(6,13):
        col_css[k]="background:#eafaf1;color:#1e8449;font-size:12px"

    def diff(s,t): return sorted(set(s)-set(t))
    rows=[]
    for i, curr in enumerate(proc):
        # Sót K0: bridge(list0_i, list0_i+1)
        if i+1<len(proc):
            k0 = bridge(curr["l0"], proc[i+1]["l0"])
            k0 = diff(k0, curr["res"])
        else:
            k0=[]
        row=[
            curr["ky"], curr["ngay"],
            " ".join(curr["l0"]) if curr["l0"] else "—",
            " ".join(proc[i-1]["l0"]) if i>=1 else "",
            " ".join(proc[i-2]["l0"]) if i>=2 else "",
            " ".join(k0) if k0 else "—",
        ]
        cur=k0[:]
        for k in range(1,8):
            t=i-k
            if t<0: row.append("")
            else:
                cur=diff(cur, proc[t]["res"])
                if cur: row.append(" ".join(cur))
                else:   row.append('<span style="color:#27ae60;font-weight:700">✅</span>')
        rows.append(row)

    st.markdown(htable(headers, rows, col_css), unsafe_allow_html=True)

# ════════════════════════════════════════════════════
# TAB 3 — LÔ LẠ (PATTERN ĐẶC BIỆT)
# ════════════════════════════════════════════════════
def _detect(prize, use_s, use_l, use_g, use_c):
    s=prize.strip()
    if len(s)<2 or not all(c.isdigit() for c in s): return False
    if use_c:
        for i in range(len(s)-2):
            if len(set(s[i:i+3]))==1: return True
    if use_l and any(c>=2 for c in Counter(s).values()): return True
    if use_g and s==s[::-1]: return True
    if use_s and len(set(s))<=3: return True
    return False

def tab_lo_la(raw, region):
    if not raw: st.info("Chọn đài → Tải dữ liệu"); return

    c1,c2,c3 = st.columns(3)
    use_s = c1.checkbox("≤3 chữ số duy nhất",True,key="t3s")
    use_l = c1.checkbox("Lặp (≥2 chữ số giống nhau)",False,key="t3l")
    use_g = c2.checkbox("Gánh / Đảo",False,key="t3g")
    use_c = c2.checkbox("Lặp liên tiếp ≥3",False,key="t3c")
    dup   = c3.checkbox("Giữ số trùng",False,key="t3d")
    mode  = c3.radio("Nhị hợp",["Mặc định (≥2 giải)","Chỉ 1 giải","Cả hai"],
                     index=2,horizontal=True,key="t3m")
    mv    = {"Mặc định (≥2 giải)":0,"Chỉ 1 giải":1,"Cả hai":2}[mode]
    mx    = 9 if "Bắc" in region else 13

    def diff(s,t): return sorted(set(s)-set(t))
    proc=[]
    for item in raw:
        p=get_prizes(item); td=get_2d(p)
        lo_list=[]
        for ci,prize in enumerate(p):
            if ci>mx: break
            if _detect(prize,use_s,use_l,use_g,use_c):
                digs=[d for d in prize if d.isdigit()]
                s="".join(sorted(digs) if dup else sorted(set(digs)))
                lo_list.append(s)
        l0=sorted(lo_list) if dup else sorted(set(lo_list))
        all_d=sorted({c for s in l0 for c in s if c.isdigit()})
        n1,nm=len(l0)==1,len(l0)>1
        show=(mv==0 and nm)or(mv==1 and n1)or(mv==2 and(n1 or nm))
        dan=sorted({a+b for a in all_d for b in all_d}) if show and all_d else []
        proc.append({"ky":ky(item),"ngay":ngay(item),
                     "l0":l0,"dan":dan,"res":td,"show":show})

    headers=["Kỳ","Ngày","List 0 Lạ","Dàn Nhị Hợp",
             "K1","K2","K3","K4","K5","K6","K7","K8","K9","K10"]
    col_css={
        0:"color:#c0392b;font-weight:700;text-align:center",
        1:"color:#7f8c8d;text-align:center",
        2:"background:#fef9e7;color:#e67e22;font-weight:700;text-align:center",
        3:"background:#eaf2ff;color:#1a5276;font-size:12px",
    }
    for k in range(4,14):
        col_css[k]="background:#eafaf1;color:#1e8449;font-size:12px"

    rows=[]
    for i,curr in enumerate(proc):
        dan_disp=(" ".join(curr["dan"][:25])+("…" if len(curr["dan"])>25 else "")
                  if curr["show"] else "")
        row=[curr["ky"],curr["ngay"],
             ",".join(curr["l0"]) if curr["l0"] else "",
             dan_disp]
        cur=curr["dan"][:]
        for k in range(1,11):
            t=i-k
            if t<0 or not curr["show"]: row.append("")
            else:
                cur=diff(cur,proc[t]["res"])
                if cur: row.append(" ".join(cur))
                else:   row.append('<span style="color:#27ae60;font-weight:700">✅</span>')
        rows.append(row)

    st.markdown(htable(headers,rows,col_css),unsafe_allow_html=True)

# ════════════════════════════════════════════════════
# TAB 4 — LÔ XIÊN
# ════════════════════════════════════════════════════
def tab_lo_xien(raw):
    st.markdown("### 🔢 Ghép Xiên Tự Động")
    st.caption("Nhóm 1 dùng cho Xiên Quay. Xiên Nhóm ghép giữa 2–4 nhóm với nhau.")

    cols4 = st.columns(4)
    groups=[]
    for i,col in enumerate(cols4,1):
        with col:
            st.markdown(f"**📌 Nhóm {i}**")
            txt=st.text_area("",height=100,key=f"xg{i}",
                             placeholder="Nhập các số,\ncách nhau bởi khoảng trắng hoặc phẩy",
                             label_visibility="collapsed")
            nums=sorted(set(n.strip() for n in txt.replace(","," ").split()
                            if n.strip().isdigit()))
            groups.append(nums)
            if nums:
                st.caption(f"{len(nums)} số: {' '.join(nums)}")

    st.divider()
    oc1,oc2,oc3,oc4,oc5 = st.columns([2,1,1,1,3])
    sep  = oc1.selectbox("Ký tự nối",["&",",","-"," "],key="xsep")
    x2   = oc2.checkbox("Xiên 2",True, key="xx2")
    x3   = oc3.checkbox("Xiên 3",True, key="xx3")
    x4   = oc4.checkbox("Xiên 4",True, key="xx4")

    # Dự đoán tự động từ dữ liệu
    if raw and oc5.button("🔮 Tự động điền Nhóm 1 từ dữ liệu",use_container_width=True):
        p0 = get_prizes(raw[0])
        td0= get_2d(p0)
        cnt= Counter(td0)
        top8=[n for n,_ in cnt.most_common(8)]
        st.info(f"Top 8 lô nháy gần nhất: **{' '.join(top8)}**")

    bc1,bc2,bc3=st.columns([1,1,2])
    quay = bc1.button("🔄 Tạo Xiên Quay",use_container_width=True)
    nhom = bc2.button("🔗 Tạo Xiên Nhóm",use_container_width=True)

    if quay:
        if len(groups[0])<2:
            st.warning("⚠️ Nhập ít nhất 2 số ở Nhóm 1!")
        else:
            rc=st.columns(3)
            for idx,(k,use) in enumerate([(2,x2),(3,x3),(4,x4)]):
                if use:
                    combos=list(itertools.combinations(groups[0],k))
                    rc[idx].text_area(
                        f"**Xiên {k}** — {len(combos)} cặp",
                        ";\n".join(sep.join(c) for c in combos),
                        height=220, key=f"qr{k}")

    if nhom:
        rc=st.columns(3)
        for idx,(k,use) in enumerate([(2,x2),(3,x3),(4,x4)]):
            if use:
                src=groups[:k]
                if all(src):
                    res=list(itertools.product(*src))
                    rc[idx].text_area(
                        f"**Xiên {k}** — {len(res)} cặp",
                        ";\n".join(sep.join(c) for c in res),
                        height=220, key=f"nr{k}")
                else:
                    st.warning(f"Cần nhập đủ {k} nhóm!")

    # Kiểm tra lịch sử lô xiên
    if raw and len(raw)>=5:
        with st.expander("📜 Kiểm tra lịch sử (20 kỳ gần nhất)"):
            p0=get_prizes(raw[0]); td0=get_2d(p0)
            cnt=Counter(td0)
            pred=[n for n,_ in cnt.most_common(8)]
            pred_set=set(pred)
            hist_rows=[]
            for item in raw[:20]:
                p=get_prizes(item); actual=set(get_2d(p))
                hits=sorted(pred_set & actual)
                hist_rows.append([ky(item), ngay(item),
                                  " ".join(pred),
                                  f'<span style="color:{"#27ae60" if hits else "#bbb"};font-weight:700">'
                                  f'{"✅ "+",".join(hits) if hits else "—"}</span>',
                                  str(len(hits))])
            st.markdown(htable(
                ["Kỳ","Ngày","Bộ số dự đoán","Kết quả trúng","Số trúng"],
                hist_rows,
                {0:"color:#c0392b;font-weight:700",
                 4:"text-align:center;font-weight:700"}),
                unsafe_allow_html=True)

# ════════════════════════════════════════════════════
# TAB 5 — TÀI / XỈU
# ════════════════════════════════════════════════════
def bead_svg(seq):
    ROWS,CS,PAD=6,34,6
    col,row,prev=0,0,None
    cells=[]
    for d in seq:
        r=d["r"]
        if prev is not None and(r!=prev or row>=ROWS):
            col+=1; row=0
        cx=PAD+col*(CS+4)+CS//2
        cy=PAD+row*(CS+4)+CS//2
        cells.append((cx,cy,"#c0392b" if r=="T" else "#2471a3",r,d["total"]))
        prev=r; row+=1
    W=PAD+(col+1)*(CS+4)+PAD
    H=PAD+ROWS*(CS+4)+PAD
    s=""
    for cx,cy,color,lbl,tot in cells:
        s+=(f'<circle cx="{cx}" cy="{cy}" r="{CS//2-1}" fill="{color}" '
            f'stroke="white" stroke-width="2"/>'
            f'<text x="{cx}" y="{cy+5}" text-anchor="middle" fill="white" '
            f'font-size="14" font-weight="bold" font-family="Arial">{lbl}</text>'
            f'<text x="{cx+CS//2-1}" y="{cy+CS//2-1}" text-anchor="end" '
            f'fill="rgba(255,255,255,0.5)" font-size="8">{tot}</text>')
    return (f'<div style="overflow-x:auto;background:#1a2c3d;'
            f'border-radius:10px;padding:6px">'
            f'<svg width="{W}" height="{H}" xmlns="http://www.w3.org/2000/svg">'
            f'<rect width="{W}" height="{H}" fill="#1a2c3d"/>{s}</svg></div>')

def tab_tai_xiu(raw):
    if not raw: st.info("Chọn đài → Tải dữ liệu"); return

    seq=[]
    for item in reversed(raw):
        p=get_prizes(item)
        gdb=p[0].strip() if p else ""
        total=sum(int(c) for c in gdb if c.isdigit())
        seq.append({"turn":ky(item),"gdb":gdb,"total":total,
                    "r":"T" if total>=23 else "X"})

    tot_t=sum(1 for d in seq if d["r"]=="T")
    tot_x=len(seq)-tot_t
    last=seq[-1]["r"]
    streak=1
    for d in reversed(seq[:-1]):
        if d["r"]==last: streak+=1
        else: break

    m1,m2,m3,m4=st.columns(4)
    m1.metric("Tổng kỳ phân tích",len(seq))
    m2.metric("🔴 TÀI",f"{tot_t} kỳ ({tot_t/len(seq)*100:.0f}%)")
    m3.metric("🔵 XỈU",f"{tot_x} kỳ ({tot_x/len(seq)*100:.0f}%)")
    m4.metric("Chuỗi hiện tại",
              f'{streak} {"Tài 🔴" if last=="T" else "Xỉu 🔵"} liên tiếp')

    l=seq[-1]
    tx="**TÀI 🔴**" if l["r"]=="T" else "**XỈU 🔵**"
    st.info(f"Kỳ mới nhất: **{l['turn']}** &nbsp;·&nbsp; "
            f"GĐB: **{l['gdb']}** &nbsp;·&nbsp; "
            f"Tổng chữ số: **{l['total']}** &nbsp;→&nbsp; {tx}")

    st.markdown("#### 🎱 Bead Road Tài / Xỉu")
    st.markdown(bead_svg(seq), unsafe_allow_html=True)

    st.markdown("#### 📋 Lịch sử 30 kỳ gần nhất")
    recent=seq[-30:]
    tbl=[]
    for i,d in enumerate(recent):
        s=1
        for j in range(i-1,-1,-1):
            if recent[j]["r"]==d["r"]: s+=1
            else: break
        color="#c0392b" if d["r"]=="T" else "#2471a3"
        bg_kq="#fff0f0" if d["r"]=="T" else "#f0f5ff"
        tbl.append([
            d["turn"], d["gdb"], str(d["total"]),
            f'<span style="color:{color};font-weight:700;background:{bg_kq};'
            f'padding:2px 8px;border-radius:4px">'
            f'{"TÀI 🔴" if d["r"]=="T" else "XỈU 🔵"}</span>',
            f'{s} {"Tài" if d["r"]=="T" else "Xỉu"}',
        ])
    st.markdown(
        htable(["Kỳ","GĐB","Tổng","Kết quả","Chuỗi"],
               list(reversed(tbl)),
               {0:"font-weight:700;color:#555;text-align:center",
                1:"font-family:Consolas;font-size:14px;letter-spacing:1px",
                2:"text-align:center;font-weight:700",
                4:"color:#7f8c8d"}),
        unsafe_allow_html=True)

# ════════════════════════════════════════════════════
# MAIN
# ════════════════════════════════════════════════════
def main():
    st.set_page_config(
        page_title="Phân Tích Xổ Số Pro",
        page_icon="🎲",
        layout="wide",
        initial_sidebar_state="collapsed",
    )

    st.markdown("""
    <style>
    /* Ẩn sidebar toggle, thu gọn padding */
    [data-testid="collapsedControl"] { display:none }
    .block-container { padding: 0.6rem 1.2rem 1rem 1.2rem !important; max-width:100% !important }
    /* Tab styling */
    .stTabs [data-baseweb="tab-list"] { gap:3px; border-bottom:2px solid #2c3e50 }
    .stTabs [data-baseweb="tab"] {
        background:#ecf0f1; border-radius:6px 6px 0 0;
        font-weight:600; font-size:13px; padding:7px 16px;
        color:#2c3e50 !important; border:1px solid #bdc3c7
    }
    .stTabs [aria-selected="true"] {
        background:#c0392b !important; color:#fff !important; border-color:#c0392b
    }
    /* Button */
    .stButton>button {
        background:#c0392b !important; color:#fff !important;
        font-weight:700; border:none; border-radius:6px;
        padding:7px 18px; font-size:14px
    }
    .stButton>button:hover { background:#a93226 !important }
    /* Checkbox label luôn hiện */
    .stCheckbox label { font-size:13px !important; color:#2c3e50 !important }
    /* Metric */
    [data-testid="metric-container"] {
        background:#f8f9fa; border:1px solid #dee2e6;
        border-radius:8px; padding:10px
    }
    /* Selectbox */
    .stSelectbox label { font-size:13px !important; font-weight:600 !important }
    </style>
    """, unsafe_allow_html=True)

    # ── HEADER BAR ──
    st.markdown(
        '<div style="background:#2c3e50;color:#fff;padding:10px 16px;'
        'border-radius:8px;margin-bottom:12px;display:flex;align-items:center;gap:10px">'
        '<span style="font-size:22px">🎲</span>'
        '<span style="font-size:18px;font-weight:700">PHÂN TÍCH XỔ SỐ PRO</span>'
        '<span style="margin-left:auto;font-size:12px;color:#95a5a6">'
        f'Cập nhật: {datetime.now().strftime("%H:%M — %d/%m/%Y")}</span>'
        '</div>',
        unsafe_allow_html=True)

    # ── CONTROL BAR ──
    cc = st.columns([1.4, 1, 2, 1, 1.5])
    region  = cc[0].selectbox("🗺️ Khu vực", ["Miền Bắc","Miền Nam","Miền Trung"],
                               key="region", label_visibility="visible")
    today   = DAYS[datetime.now().weekday()]
    day     = cc[1].selectbox("📅 Thứ", DAYS, index=DAYS.index(today),
                               key="day", label_visibility="visible")
    sl      = get_stations(region, day)
    station = cc[2].selectbox("🏠 Đài", sl if sl else ["—"],
                               key="station", label_visibility="visible")
    show_g47= cc[3].checkbox("Hiện G4–G7", False, key="sg47")
    load    = cc[4].button("📡 Tải Dữ Liệu", use_container_width=True)

    st.divider()

    # ── STATE ──
    if "raw"  not in st.session_state: st.session_state.raw  = []
    if "name" not in st.session_state: st.session_state.name = ""

    if load and station and station != "—":
        with st.spinner(f"Đang tải dữ liệu {station}..."):
            data = load_raw(station)
        st.session_state.raw  = data
        st.session_state.name = station
        if data: st.success(f"✅ Đã tải **{len(data)} kỳ** từ **{station}**")
        else:    st.error("❌ Không tải được dữ liệu!")

    raw  = st.session_state.raw
    name = st.session_state.name

    # ── KẾT QUẢ + ĐẦU ĐUÔI ──
    if raw:
        show_result_header(raw, show_g47)
        st.divider()

    # ── TABS ──
    t1,t2,t3,t4,t5 = st.tabs([
        "📉 Thiếu Đầu & Chạm Tổng",
        "📋 Cầu List 0 (Truyền Thống)",
        "🔮 Lô Lạ (Pattern Đặc Biệt)",
        "🔢 Lô Xiên (Ghép Cặp)",
        "🎲 Tài / Xỉu",
    ])
    with t1: tab_thieu_dau(raw)
    with t2: tab_list0(raw)
    with t3: tab_lo_la(raw, region)
    with t4: tab_lo_xien(raw)
    with t5: tab_tai_xiu(raw)

if __name__=="__main__":
    main()
