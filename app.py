# -*- coding: utf-8 -*-
import streamlit as st
import streamlit.components.v1 as components
import requests
import json
from collections import Counter
import pandas as pd
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from datetime import datetime

# =============================================================================
# CẤU HÌNH & DỮ LIỆU
# =============================================================================

HEADERS = {
    "User-Agent": "Mozilla/5.0",
    "Referer": "https://www.kqxs88.live/",
}

DAI_API = {
    "Miền Bắc": "https://www.kqxs88.live/api/front/open/lottery/history/list/game?limitNum=60&gameCode=miba",
    "Miền Bắc 75s": "https://www.kqxs88.live/api/front/open/lottery/history/list/game?limitNum=60&gameCode=vnmbmg",
    "Miền Bắc 45s": "https://www.kqxs88.live/api/front/open/lottery/history/list/game?limitNum=60&gameCode=miba45",
    "An Giang": "https://www.kqxs88.live/api/front/open/lottery/history/list/game?limitNum=60&gameCode=angi",
    "Bạc Liêu": "https://www.kqxs88.live/api/front/open/lottery/history/list/game?limitNum=60&gameCode=bali",
    "Bến Tre": "https://www.kqxs88.live/api/front/open/lottery/history/list/game?limitNum=60&gameCode=betr",
    "Bình Dương": "https://www.kqxs88.live/api/front/open/lottery/history/list/game?limitNum=60&gameCode=bidu",
    "Bình Thuận": "https://www.kqxs88.live/api/front/open/lottery/history/list/game?limitNum=60&gameCode=bith",
    "Bình Phước": "https://www.kqxs88.live/api/front/open/lottery/history/list/game?limitNum=60&gameCode=biph",
    "Cà Mau": "https://www.kqxs88.live/api/front/open/lottery/history/list/game?limitNum=60&gameCode=cama",
    "Cần Thơ": "https://www.kqxs88.live/api/front/open/lottery/history/list/game?limitNum=60&gameCode=cath",
    "Đà Lạt": "https://www.kqxs88.live/api/front/open/lottery/history/list/game?limitNum=60&gameCode=dalat",
    "Đồng Nai": "https://www.kqxs88.live/api/front/open/lottery/history/list/game?limitNum=60&gameCode=dona",
    "Đồng Tháp": "https://www.kqxs88.live/api/front/open/lottery/history/list/game?limitNum=60&gameCode=doth",
    "Hậu Giang": "https://www.kqxs88.live/api/front/open/lottery/history/list/game?limitNum=60&gameCode=hagi",
    "Kiên Giang": "https://www.kqxs88.live/api/front/open/lottery/history/list/game?limitNum=60&gameCode=kigi",
    "Long An": "https://www.kqxs88.live/api/front/open/lottery/history/list/game?limitNum=60&gameCode=loan",
    "Sóc Trăng": "https://www.kqxs88.live/api/front/open/lottery/history/list/game?limitNum=60&gameCode=sotr",
    "Tây Ninh": "https://www.kqxs88.live/api/front/open/lottery/history/list/game?limitNum=60&gameCode=tani",
    "Tiền Giang": "https://www.kqxs88.live/api/front/open/lottery/history/list/game?limitNum=60&gameCode=tigi",
    "TP. Hồ Chí Minh": "https://www.kqxs88.live/api/front/open/lottery/history/list/game?limitNum=60&gameCode=tphc",
    "Trà Vinh": "https://www.kqxs88.live/api/front/open/lottery/history/list/game?limitNum=60&gameCode=trvi",
    "Vĩnh Long": "https://www.kqxs88.live/api/front/open/lottery/history/list/game?limitNum=60&gameCode=vilo",
    "Vũng Tàu": "https://www.kqxs88.live/api/front/open/lottery/history/list/game?limitNum=60&gameCode=vuta",
    "Đà Nẵng": "https://www.kqxs88.live/api/front/open/lottery/history/list/game?limitNum=60&gameCode=dana",
    "Bình Định": "https://www.kqxs88.live/api/front/open/lottery/history/list/game?limitNum=60&gameCode=bidi",
    "Đắk Lắk": "https://www.kqxs88.live/api/front/open/lottery/history/list/game?limitNum=60&gameCode=dalak",
    "Đắk Nông": "https://www.kqxs88.live/api/front/open/lottery/history/list/game?limitNum=60&gameCode=dano",
    "Gia Lai": "https://www.kqxs88.live/api/front/open/lottery/history/list/game?limitNum=60&gameCode=gila",
    "Khánh Hòa": "https://www.kqxs88.live/api/front/open/lottery/history/list/game?limitNum=60&gameCode=khho",
    "Kon Tum": "https://www.kqxs88.live/api/front/open/lottery/history/list/game?limitNum=60&gameCode=kotu",
    "Ninh Thuận": "https://www.kqxs88.live/api/front/open/lottery/history/list/game?limitNum=60&gameCode=nith",
    "Phú Yên": "https://www.kqxs88.live/api/front/open/lottery/history/list/game?limitNum=60&gameCode=phye",
    "Quảng Bình": "https://www.kqxs88.live/api/front/open/lottery/history/list/game?limitNum=60&gameCode=qubi",
    "Quảng Nam": "https://www.kqxs88.live/api/front/open/lottery/history/list/game?limitNum=60&gameCode=quna",
    "Quảng Ngãi": "https://www.kqxs88.live/api/front/open/lottery/history/list/game?limitNum=60&gameCode=qung",
    "Quảng Trị": "https://www.kqxs88.live/api/front/open/lottery/history/list/game?limitNum=60&gameCode=qutr",
    "Thừa Thiên Huế": "https://www.kqxs88.live/api/front/open/lottery/history/list/game?limitNum=60&gameCode=thth"
}

LICH_QUAY_NAM = {
    "Chủ Nhật": ["Tiền Giang", "Kiên Giang", "Đà Lạt"],
    "Thứ 2": ["TP. Hồ Chí Minh", "Đồng Tháp", "Cà Mau"],
    "Thứ 3": ["Bến Tre", "Vũng Tàu", "Bạc Liêu"],
    "Thứ 4": ["Đồng Nai", "Cần Thơ", "Sóc Trăng"],
    "Thứ 5": ["Tây Ninh", "An Giang", "Bình Thuận"],
    "Thứ 6": ["Vĩnh Long", "Bình Dương", "Trà Vinh"],
    "Thứ 7": ["TP. Hồ Chí Minh", "Long An", "Bình Phước", "Hậu Giang"]
}

LICH_QUAY_TRUNG = {
    "Chủ Nhật": ["Kon Tum", "Khánh Hòa", "Thừa Thiên Huế"],
    "Thứ 2": ["Thừa Thiên Huế", "Phú Yên"],
    "Thứ 3": ["Đắk Lắk", "Quảng Nam"],
    "Thứ 4": ["Đà Nẵng", "Khánh Hòa"],
    "Thứ 5": ["Bình Định", "Quảng Trị", "Quảng Bình"],
    "Thứ 6": ["Gia Lai", "Ninh Thuận"],
    "Thứ 7": ["Đà Nẵng", "Quảng Ngãi", "Đắk Nông"]
}

LICH_QUAY_BAC = {
    "Chủ Nhật": "Thái Bình",
    "Thứ 2": "Hà Nội",
    "Thứ 3": "Quảng Ninh",
    "Thứ 4": "Bắc Ninh",
    "Thứ 5": "Hà Nội",
    "Thứ 6": "Hải Phòng",
    "Thứ 7": "Nam Định"
}

GIAI_LABELS_MB = [
    "ĐB", "G1", "G2-1", "G2-2",
    "G3-1", "G3-2", "G3-3", "G3-4", "G3-5", "G3-6",
    "G4-1", "G4-2", "G4-3", "G4-4",
    "G5-1", "G5-2", "G5-3", "G5-4", "G5-5", "G5-6",
    "G6-1", "G6-2", "G6-3",
    "G7-1", "G7-2", "G7-3", "G7-4"
]

DAYS_OF_WEEK = ["Thứ 2", "Thứ 3", "Thứ 4", "Thứ 5", "Thứ 6", "Thứ 7", "Chủ Nhật"]

# =============================================================================
# NETWORK UTILS
# =============================================================================

@st.cache_resource
def _get_session():
    s = requests.Session()
    retry = Retry(
        total=3, connect=3, read=3, backoff_factor=0.5,
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=frozenset(["GET"]),
    )
    s.mount("https://", HTTPAdapter(max_retries=retry))
    s.mount("http://", HTTPAdapter(max_retries=retry))
    return s

SESSION = _get_session()

def http_get_issue_list(url: str, timeout: int = 10):
    try:
        resp = SESSION.get(url, headers=HEADERS, timeout=timeout)
        resp.raise_for_status()
        data = resp.json().get("t", {})
        issue_list = data.get("issueList", [])
        
        # Lấy thời gian từ kỳ mới nhất
        latest_time = ""
        if issue_list:
            latest_time = issue_list[0].get('openTime', '')
            
        return issue_list, latest_time
    except Exception:
        return [], ""

def get_current_day_vietnamese():
    return DAYS_OF_WEEK[datetime.now().weekday()]

def load_data(station_name):
    api_key = station_name
    if "Miền Bắc" in station_name and "45s" not in station_name and "75s" not in station_name:
        api_key = "Miền Bắc"
    
    url = DAI_API.get(api_key)
    if url:
        return http_get_issue_list(url)
    return [], ""

# =============================================================================
# LOGIC HELPER FUNCTIONS
# =============================================================================

def generate_cham_tong(list_missing):
    """Tạo dàn Chạm + Tổng từ list số thiếu"""
    result_set = set()
    for d_str in list_missing:
        try:
            d = int(d_str)
        except:
            continue
        # Chạm
        for i in range(100):
            s = f"{i:02d}"
            if str(d) in s:
                result_set.add(s)
        # Tổng
        for i in range(100):
            s = f"{i:02d}"
            digit_sum = (int(s[0]) + int(s[1])) % 10
            if digit_sum == d:
                result_set.add(s)
    return sorted(list(result_set))

def get_target_results(prizes_flat, use_duoi_db, use_dau_db, use_duoi_g1, use_dau_g1):
    """Lấy tập hợp kết quả để so sánh (Đuôi/Đầu ĐB/G1)"""
    targets = set()
    if len(prizes_flat) > 0:
        db = prizes_flat[0].strip()
        if len(db) >= 2:
            if use_duoi_db: targets.add(db[-2:])
            if use_dau_db: targets.add(db[:2])
    if len(prizes_flat) > 1:
        g1 = prizes_flat[1].strip()
        if len(g1) >= 2:
            if use_duoi_g1: targets.add(g1[-2:])
            if use_dau_g1: targets.add(g1[:2])
    return targets

# =============================================================================
# STREAMLIT APP
# =============================================================================

st.set_page_config(page_title="Phần Mềm Soi Cầu 3 Miền", layout="wide")

# CSS for Compact UI
st.markdown("""
<style>
    .block-container {
        padding-top: 0.5rem !important;
        padding-bottom: 0rem !important;
        padding-left: 1rem !important;
        padding-right: 1rem !important;
        max-width: 100% !important;
    }
    html, body, [class*="css"] {
        font-size: 13px;
    }
    div[data-testid="stVerticalBlock"] > div {
        gap: 0.2rem !important;
    }
    .stDataFrame {
        font-size: 12px !important;
    }
    h1, h2, h3, h4, h5 {
        margin-bottom: 0.2rem !important;
        padding-top: 0 !important;
        color: #ff4b4b !important;
    }
    /* Tabs */
    button[data-baseweb="tab"] {
        font-size: 14px !important;
        font-weight: bold !important;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'raw_data' not in st.session_state:
    st.session_state.raw_data = []
    st.session_state.last_open_time = ""
    st.session_state.current_station = ""
    data, time = load_data("Miền Bắc")
    st.session_state.raw_data = data
    st.session_state.last_open_time = time
    st.session_state.current_station = "Miền Bắc"

if 'selected_giai' not in st.session_state:
    st.session_state.selected_giai = [2, 3]

# Tab 2 states
if 'tab2_duoi_db' not in st.session_state: st.session_state.tab2_duoi_db = True
if 'tab2_dau_db' not in st.session_state: st.session_state.tab2_dau_db = False
if 'tab2_duoi_g1' not in st.session_state: st.session_state.tab2_duoi_g1 = False
if 'tab2_dau_g1' not in st.session_state: st.session_state.tab2_dau_g1 = False

# =============================================================================
# TOP CONTROLS
# =============================================================================

st.markdown("#### 🛠️ CẤU HÌNH & DỮ LIỆU")
col1, col2, col3, col4 = st.columns([1.5, 1.5, 3, 3])

with col1:
    region = st.selectbox("Khu vực", ["Miền Bắc", "Miền Nam", "Miền Trung"], index=0, label_visibility="collapsed")
with col2:
    current_day = get_current_day_vietnamese()
    try: default_day_idx = DAYS_OF_WEEK.index(current_day)
    except: default_day_idx = 0
    selected_day = st.selectbox("Thứ", DAYS_OF_WEEK, index=default_day_idx, label_visibility="collapsed")
with col3:
    stations = []
    if region == "Miền Bắc":
        lbl_tinh = LICH_QUAY_BAC.get(selected_day, "")
        stations = [f"Miền Bắc ({lbl_tinh})", "Miền Bắc 75s", "Miền Bắc 45s"]
    elif region == "Miền Nam": stations = LICH_QUAY_NAM.get(selected_day, [])
    elif region == "Miền Trung": stations = LICH_QUAY_TRUNG.get(selected_day, [])
    
    if stations: station = st.selectbox("Đài", stations, index=0, label_visibility="collapsed")
    else: station = st.selectbox("Đài", ["Không có lịch quay"], disabled=True, label_visibility="collapsed")

with col4:
    # Auto load logic: Check if station changed
    if station and station != "Không có lịch quay":
        if station != st.session_state.get('current_station'):
            with st.spinner(f"Đang tải {station}..."):
                data, time = load_data(station)
                st.session_state.raw_data = data
                st.session_state.last_open_time = time
                st.session_state.current_station = station
                st.rerun()

    # NOTE: The button is critical for the JavaScript to click. 
    # Do NOT remove type="primary" or the logic below will break.
    if st.button("🔄 TẢI LẠI", type="primary", use_container_width=True):
        if station and station != "Không có lịch quay":
            with st.spinner(f"Đang tải {station}..."):
                data, time = load_data(station)
                st.session_state.raw_data = data
                st.session_state.last_open_time = time
                st.session_state.current_station = station
                st.rerun()

    # Clock Logic
    interval_seconds = 0
    draw_time_config = ""
    if "75s" in station: interval_seconds = 75
    elif "45s" in station: interval_seconds = 45
    else:
        if region == "Miền Bắc": draw_time_config = "18:15"
        elif region == "Miền Nam": draw_time_config = "16:15"
        elif region == "Miền Trung": draw_time_config = "17:15"

    # -----------------------------------------------------------------------------------------
    # JAVASCRIPT AUTO RELOAD LOGIC:
    # When diff <= 0, wait 4 seconds (buffer), then find the Primary Button and Click it.
    # -----------------------------------------------------------------------------------------
    clock_html = f"""
    <style>
        body {{ margin: 0; padding: 0; font-family: "Source Sans Pro", sans-serif; font-size: 13px; background-color: transparent; color: #31333F; }}
        .container {{ display: flex; align-items: center; justify-content: space-between; padding-top: 8px; }}
        .highlight {{ color: #ff4b4b; font-weight: bold; font-size: 14px; }}
        .countdown {{ color: #28a745; font-weight: bold; font-size: 14px; margin-left: 10px; }}
        .label {{ font-weight: 600; margin-right: 4px; }}
    </style>
    <div class="container">
        <div><span class="label">📅 Kỳ:</span><span class="highlight">{st.session_state.last_open_time}</span></div>
        <div><span class="label">⏳ Sắp quay:</span><span id="countdown" class="countdown">--:--</span></div>
    </div>
    <script>
        var interval = {interval_seconds};
        var lastTimeStr = "{st.session_state.last_open_time}"; 
        var drawTimeConfig = "{draw_time_config}";
        var reloadScheduled = false;

        function parseDate(str) {{ var t = str.split(/[- :]/); return new Date(t[0], t[1]-1, t[2], t[3], t[4], t[5]); }}
        
        function triggerReload() {{
            if (!reloadScheduled) {{
                reloadScheduled = true;
                setTimeout(function() {{
                    var buttons = window.parent.document.querySelectorAll('button[kind="primary"]');
                    if (buttons.length > 0) {{
                        buttons[0].click();
                    }} else {{
                        var buttons2 = window.parent.document.querySelectorAll('button[data-testid="baseButton-primary"]');
                        if (buttons2.length > 0) buttons2[0].click();
                    }}
                }}, 4000); 
            }}
        }}

        function updateClock() {{
            var now = new Date();
            var targetDate = null;
            var diff = 0;
            
            if (interval > 0) {{
                var lastDate = parseDate(lastTimeStr);
                targetDate = new Date(lastDate.getTime() + interval * 1000);
                diff = targetDate - now;
            }} else if (drawTimeConfig) {{
                var parts = drawTimeConfig.split(":");
                targetDate = new Date(now.getFullYear(), now.getMonth(), now.getDate(), parts[0], parts[1], 0);
                if (now > targetDate) {{ targetDate.setDate(targetDate.getDate() + 1); }}
                diff = targetDate - now;
            }}
            
            var cdEl = document.getElementById('countdown');
            
            if (diff > 0) {{
                var hours = Math.floor(diff / (1000 * 60 * 60));
                var minutes = Math.floor((diff % (1000 * 60 * 60)) / (1000 * 60));
                var seconds = Math.floor((diff % (1000 * 60)) / 1000);
                cdEl.innerText = (hours>0?hours.toString().padStart(2,'0')+':':'') + minutes.toString().padStart(2,'0') + ':' + seconds.toString().padStart(2,'0');
                cdEl.style.color = "#28a745";
                reloadScheduled = false;
            }} else {{
                cdEl.innerText = "Đang quay..."; 
                cdEl.style.color = "#dc3545";
                if (interval > 0 || Math.abs(diff) < 60000) {{ 
                    triggerReload();
                }}
            }}
        }}
        setInterval(updateClock, 1000); 
        updateClock();
    </script>
    """
    components.html(clock_html, height=40)

st.markdown("---")

# =============================================================================
# TABS LOGIC
# =============================================================================

tab1, tab2 = st.tabs(["📊 CẦU LIST 0 (TRUYỀN THỐNG)", "🎯 CẦU THIẾU ĐẦU & KIỂM TRA TRÚNG"])

# -----------------------------------------------------------------------------
# TAB 1: CẦU LIST 0
# -----------------------------------------------------------------------------
with tab1:
    with st.expander("⚙️ CẤU HÌNH GIẢI PHÂN TÍCH", expanded=False):
        c1, c2, c3 = st.columns([1, 1, 8])
        with c1:
            if st.button("Chọn hết", key="btn_all"):
                st.session_state.selected_giai = list(range(1, len(GIAI_LABELS_MB)))
                st.rerun()
        with c2:
            if st.button("Bỏ chọn", key="btn_none"):
                st.session_state.selected_giai = []
                st.rerun()
        
        num_cols = 9
        giai_selected = []
        cols = st.columns(num_cols)
        for i, label in enumerate(GIAI_LABELS_MB):
            if i == 0: continue
            col_idx = (i-1) % num_cols
            with cols[col_idx]:
                default_val = i in st.session_state.selected_giai
                if st.checkbox(label, value=default_val, key=f"giai_{i}"):
                    giai_selected.append(i)
        st.session_state.selected_giai = giai_selected

    if not st.session_state.raw_data:
        st.info("Chưa có dữ liệu.")
    else:
        col_left, col_right = st.columns([2.5, 5.5])
        
        with col_left:
            st.markdown("##### KẾT QUẢ")
            display_indices = [0] + st.session_state.selected_giai
            headers = ["Kỳ", "ĐB"] + [GIAI_LABELS_MB[i] for i in st.session_state.selected_giai]
            
            rows_res = []
            for item in st.session_state.raw_data:
                d = json.loads(item['detail'])
                prizes_flat = []
                for f in d: prizes_flat += f.split(',')
                row = [item['turnNum']]
                for idx in display_indices:
                    row.append(prizes_flat[idx] if idx < len(prizes_flat) else "")
                rows_res.append(row)
            
            df_res = pd.DataFrame(rows_res, columns=headers)
            
            # CONFIG: Fixed width 30px for result columns
            column_config = {
                "Kỳ": st.column_config.TextColumn("Kỳ", width=30),
                "ĐB": st.column_config.TextColumn("ĐB", width=30),
            }
            for h in headers[2:]: 
                column_config[h] = st.column_config.TextColumn(h, width=30)

            st.dataframe(df_res, height=700, use_container_width=True, hide_index=True, column_config=column_config)
        
        with col_right:
            st.markdown("##### PHÂN TÍCH LIST 0 & SÓT")
            processed = []
            for item in st.session_state.raw_data:
                d = json.loads(item['detail'])
                prizes_flat = []
                for f in d: prizes_flat += f.split(',')
                g_nums = []
                for idx in st.session_state.selected_giai:
                    if idx < len(prizes_flat):
                        g_nums.extend([ch for ch in prizes_flat[idx].strip() if ch.isdigit()])
                counter = Counter(g_nums)
                list0 = [str(i) for i, v in enumerate([counter.get(str(d), 0) for d in range(10)]) if v == 0]
                res_los = [lo[-2:] for lo in prizes_flat if len(lo)>=2 and lo[-2:].isdigit()]
                processed.append({"ky": item['turnNum'], "list0": list0, "res": res_los})

            def bridge_ab(l1, l2):
                s = set()
                for a in l1:
                    for b in l2: s.add(a+b); s.add(b+a)
                return sorted(list(s))
            def diff(src, target): return sorted(list(set(src) - set(target)))

            rows_anal = []
            for i in range(len(processed)):
                curr = processed[i]
                row = [curr["ky"], ",".join(curr["list0"])]
                
                # K0
                if i+1 < len(processed):
                    k0 = diff(bridge_ab(processed[i+1]["list0"], curr["list0"]), curr["res"])
                    row.append(" ".join(k0))
                else: row.append("")
                
                # K1-K7
                if i>0 and i+1 < len(processed):
                    dan = bridge_ab(processed[i+1]["list0"], processed[i]["list0"])
                    for k in range(7):
                        t_idx = i - k
                        if t_idx < 0: row.append("")
                        else: row.append(" ".join(diff(dan, processed[t_idx]["res"])))
                else: row.extend([""]*7)
                rows_anal.append(row)
            
            df_anal = pd.DataFrame(rows_anal, columns=["Kỳ", "Thiếu", "Sót K0", "Sót K1"] + [f"Sót K{k}" for k in range(2, 8)])
            
            # CONFIG: Fixed width 60px for Sót columns
            anal_config = {
                "Kỳ": st.column_config.TextColumn("Kỳ", width=30),
                "Thiếu": st.column_config.TextColumn("Thiếu", width=50),
                "Sót K0": st.column_config.TextColumn("Sót K0", width=60),
                "Sót K1": st.column_config.TextColumn("Sót K1", width=60)
            }
            for k in range(2, 8):
                anal_config[f"Sót K{k}"] = st.column_config.TextColumn(f"Sót K{k}", width=60)

            def highlight_t1(s):
                styles = []
                for v in s:
                    if s.name == "Thiếu": styles.append('background-color: #ffebee; color: #c0392b')
                    elif s.name == "Sót K1": styles.append('background-color: #e8f8f5; color: #16a085' if v else '')
                    else: styles.append('')
                return styles
            
            st.dataframe(df_anal.style.apply(highlight_t1), height=700, use_container_width=True, hide_index=True, column_config=anal_config)

# -----------------------------------------------------------------------------
# TAB 2: CẦU THIẾU ĐẦU & TRÚNG
# -----------------------------------------------------------------------------
with tab2:
    st.markdown("##### ⚙️ MỤC TIÊU SO SÁNH (Check để tính Trúng/Trượt)")
    chk_c1, chk_c2, chk_c3, chk_c4, _ = st.columns([1,1,1,1,4])
    with chk_c1: st.session_state.tab2_duoi_db = st.checkbox("Đuôi ĐB", st.session_state.tab2_duoi_db)
    with chk_c2: st.session_state.tab2_dau_db = st.checkbox("Đầu ĐB", st.session_state.tab2_dau_db)
    with chk_c3: st.session_state.tab2_duoi_g1 = st.checkbox("Đuôi G1", st.session_state.tab2_duoi_g1)
    with chk_c4: st.session_state.tab2_dau_g1 = st.checkbox("Đầu G1", st.session_state.tab2_dau_g1)

    if not st.session_state.raw_data:
        st.info("Chưa có dữ liệu.")
    else:
        t2_left, t2_right = st.columns([2, 6])
        
        with t2_left:
            # Simple result table
            rows_simple = []
            for item in st.session_state.raw_data:
                d = json.loads(item['detail'])
                prizes_flat = []
                for f in d: prizes_flat += f.split(',')
                db = prizes_flat[0] if len(prizes_flat)>0 else ""
                g1 = prizes_flat[1] if len(prizes_flat)>1 else ""
                rows_simple.append([item['turnNum'], db, g1])
            
            df_simple = pd.DataFrame(rows_simple, columns=["Kỳ", "ĐB", "G1"])
            
            # CONFIG: Fixed width 30px for result columns
            simple_config = {
                "Kỳ": st.column_config.TextColumn("Kỳ", width=30),
                "ĐB": st.column_config.TextColumn("ĐB", width=30),
                "G1": st.column_config.TextColumn("G1", width=30),
            }

            st.dataframe(df_simple, height=700, use_container_width=True, hide_index=True, column_config=simple_config)
            
        with t2_right:
            # Analysis Logic
            processed_data = []
            for item in st.session_state.raw_data:
                d = json.loads(item['detail'])
                prizes_flat = []
                for f in d: prizes_flat += f.split(',')
                heads = [p[0] for p in prizes_flat if p.strip()]
                counter = Counter(heads)
                missing = [str(i) for i, v in enumerate([counter.get(str(d),0) for d in range(10)]) if v==0]
                processed_data.append({"ky": item['turnNum'], "missing": missing, "full": prizes_flat})
            
            rows_t2 = []
            for i in range(len(processed_data)):
                curr = processed_data[i]
                dan = generate_cham_tong(curr["missing"])
                row = [curr["ky"], ",".join(curr["missing"]), " ".join(dan)]
                
                # Check hits K1-K7
                for k in range(1, 8):
                    target_idx = i - k
                    if target_idx < 0:
                        row.append("")
                    else:
                        target_data = processed_data[target_idx]
                        targets = get_target_results(
                            target_data["full"], 
                            st.session_state.tab2_duoi_db, st.session_state.tab2_dau_db,
                            st.session_state.tab2_duoi_g1, st.session_state.tab2_dau_g1
                        )
                        hits = set(dan).intersection(targets)
                        if hits: row.append(f"TRÚNG {','.join(sorted(list(hits)))}")
                        else: row.append("-")
                rows_t2.append(row)
            
            cols_t2 = ["Kỳ", "Thiếu Đầu", "Dàn K0", "K1", "K2", "K3", "K4", "K5", "K6", "K7"]
            df_t2 = pd.DataFrame(rows_t2, columns=cols_t2)
            
            # CONFIG: Fixed width 60px for K1-K7 (Sót equivalent)
            t2_config = {
                "Kỳ": st.column_config.TextColumn("Kỳ", width=30),
                "Thiếu Đầu": st.column_config.TextColumn("Thiếu Đầu", width=40),
                "Dàn K0": st.column_config.TextColumn("Dàn K0", width="medium"), # Dàn is long
            }
            for k in range(1, 8):
                t2_config[f"K{k}"] = st.column_config.TextColumn(f"K{k}", width=60)

            def highlight_t2(s):
                styles = []
                for v in s:
                    if s.name == "Dàn K0": styles.append('background-color: #e3f2fd; color: #1565c0')
                    elif str(v).startswith("TRÚNG"): styles.append('background-color: #c8e6c9; color: #2e7d32; font-weight: bold')
                    else: styles.append('')
                return styles
                
            st.dataframe(
                df_t2.style.apply(highlight_t2), 
                height=700, 
                use_container_width=True, 
                hide_index=True,
                column_config=t2_config
            )
