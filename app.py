# -*- coding: utf-8 -*-
import streamlit as st
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
        return resp.json().get("t", {}).get("issueList", [])
    except Exception:
        return []

def get_current_day_vietnamese():
    return DAYS_OF_WEEK[datetime.now().weekday()]

def load_data(station_name):
    api_key = station_name
    if "Miền Bắc" in station_name and "45s" not in station_name and "75s" not in station_name:
        api_key = "Miền Bắc"
    
    url = DAI_API.get(api_key)
    if url:
        return http_get_issue_list(url)
    return []

# =============================================================================
# STREAMLIT APP
# =============================================================================

st.set_page_config(page_title="Phần Mềm Soi Cầu 3 Miền", layout="wide")

st.markdown("""
<style>
    .main > div {
        padding-top: 1rem;
    }
    .stDataFrame {
        font-size: 12px;
    }
    h1, h2, h3 {
        color: #ff4b4b;
    }
    .block-container {
        padding-top: 1rem;
        padding-bottom: 1rem;
    }
    /* Compact header */
    div[data-testid="stVerticalBlock"] > div:has(div[data-testid="stHorizontalBlock"]) {
        background-color: #262730;
        padding: 15px;
        border-radius: 10px;
        border: 1px solid #464b5c;
    }
    /* Checkbox spacing */
    div[data-testid="stCheckbox"] {
        margin-bottom: 5px;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'raw_data' not in st.session_state:
    st.session_state.raw_data = []
    # Auto load Miền Bắc on first run
    st.session_state.raw_data = load_data("Miền Bắc")

if 'selected_giai' not in st.session_state:
    st.session_state.selected_giai = [2, 3]  # Default: G2-1, G2-2

# =============================================================================
# TOP CONTROLS
# =============================================================================

st.subheader("🛠️ CẤU HÌNH & DỮ LIỆU")

col1, col2, col3, col4 = st.columns([1.5, 1.5, 3, 1.5])

with col1:
    region = st.selectbox("Khu vực", ["Miền Bắc", "Miền Nam", "Miền Trung"], index=0)

with col2:
    # Default to current day
    current_day = get_current_day_vietnamese()
    try:
        default_day_idx = DAYS_OF_WEEK.index(current_day)
    except:
        default_day_idx = 0
    selected_day = st.selectbox("Thứ", DAYS_OF_WEEK, index=default_day_idx)

with col3:
    # Get stations based on region and selected day
    stations = []
    if region == "Miền Bắc":
        lbl_tinh = LICH_QUAY_BAC.get(selected_day, "")
        stations = [f"Miền Bắc ({lbl_tinh})", "Miền Bắc 75s", "Miền Bắc 45s"]
    elif region == "Miền Nam":
        stations = LICH_QUAY_NAM.get(selected_day, [])
    elif region == "Miền Trung":
        stations = LICH_QUAY_TRUNG.get(selected_day, [])
    
    if stations:
        station = st.selectbox("Đài", stations, index=0)
    else:
        station = st.selectbox("Đài", ["Không có lịch quay"], disabled=True)

with col4:
    st.write("") # Spacer
    st.write("") # Spacer
    if st.button("🔄 TẢI LẠI", type="primary", use_container_width=True):
        if station and station != "Không có lịch quay":
            with st.spinner(f"Đang tải: {station}..."):
                data = load_data(station)
                if data:
                    st.session_state.raw_data = data
                    st.success(f"Đã tải {len(data)} kỳ")
                else:
                    st.error("Lỗi tải dữ liệu!")

# Prize Selection
with st.expander("🎯 CHỌN GIẢI ĐỂ PHÂN TÍCH (Và hiển thị cột)", expanded=True):
    # Control buttons
    c1, c2, c3 = st.columns([1, 1, 6])
    with c1:
        if st.button("Chọn tất cả"):
            st.session_state.selected_giai = list(range(1, len(GIAI_LABELS_MB)))
            st.rerun()
    with c2:
        if st.button("Bỏ chọn"):
            st.session_state.selected_giai = []
            st.rerun()
            
    st.write("")
    
    # Create checkboxes in columns (Reduced to 6 columns for better visibility)
    num_cols = 6
    giai_selected = []
    cols = st.columns(num_cols)
    
    for i, label in enumerate(GIAI_LABELS_MB):
        if i == 0: continue # Skip ĐB
        
        col_idx = (i-1) % num_cols
        with cols[col_idx]:
            default_val = i in st.session_state.selected_giai
            if st.checkbox(label, value=default_val, key=f"giai_{i}"):
                giai_selected.append(i)
    
    st.session_state.selected_giai = giai_selected

st.markdown("---")

# =============================================================================
# MAIN CONTENT
# =============================================================================

if not st.session_state.raw_data:
    st.info("Không có dữ liệu. Vui lòng kiểm tra kết nối hoặc chọn đài khác.")
else:
    # Create two columns
    col_left, col_right = st.columns([1, 2])
    
    with col_left:
        st.markdown("### 📊 KẾT QUẢ")
        
        # Build result table
        display_indices = [0]  # Always include ĐB
        headers = ["Kỳ", "ĐB"]
        
        for i in st.session_state.selected_giai:
            display_indices.append(i)
            headers.append(GIAI_LABELS_MB[i])
        
        rows_res = []
        for item in st.session_state.raw_data:
            d = json.loads(item['detail'])
            prizes_flat = []
            for f in d:
                prizes_flat += f.split(',')
            
            row = [item['turnNum']]
            for idx in display_indices:
                if idx < len(prizes_flat):
                    row.append(prizes_flat[idx])
                else:
                    row.append("")
            rows_res.append(row)
        
        df_res = pd.DataFrame(rows_res, columns=headers)
        st.dataframe(df_res, height=600, use_container_width=True, hide_index=True)
    
    with col_right:
        st.markdown("### 📈 PHÂN TÍCH LIST 0 & SÓT K1-K7")
        
        # Process data for analysis
        processed = []
        for item in st.session_state.raw_data:
            detail = json.loads(item['detail'])
            prizes_flat = []
            for field in detail:
                prizes_flat += field.split(",")
            
            g_nums = []
            for idx in st.session_state.selected_giai:
                if idx < len(prizes_flat):
                    g_nums.extend([ch for ch in prizes_flat[idx].strip() if ch.isdigit()])
            
            counter = Counter(g_nums)
            counts = [counter.get(str(d), 0) for d in range(10)]
            list0 = [str(i) for i, v in enumerate(counts) if v == 0]
            
            current_los = []
            for lo in prizes_flat:
                lo = lo.strip()
                if len(lo) >= 2 and lo[-2:].isdigit():
                    current_los.append(lo[-2:])
            
            processed.append({
                "ky": item['turnNum'],
                "list0": list0,
                "res": current_los
            })
        
        # Bridge logic
        def bridge_ab(l1, l2):
            s = set()
            for a in l1:
                for b in l2:
                    s.add(a + b)
                    s.add(b + a)
            return sorted(list(s))
        
        def diff(src, target):
            return sorted(list(set(src) - set(target)))
        
        # Build analysis table
        rows_anal = []
        for i in range(len(processed)):
            curr = processed[i]
            row = [curr["ky"], ",".join(curr["list0"])]
            
            if i + 2 < len(processed):
                l0_prev1 = processed[i + 1]["list0"]
                l0_prev2 = processed[i + 2]["list0"]
                current_dan = bridge_ab(l0_prev2, l0_prev1)
                
                for k in range(7):
                    target_idx = i - k
                    if target_idx < 0:
                        row.append("")
                    else:
                        res_target = processed[target_idx]["res"]
                        current_dan = diff(current_dan, res_target)
                        row.append(" ".join(current_dan))
            else:
                row.extend([""] * 7)
            
            rows_anal.append(row)
        
        cols_anal = ["Kỳ", "List 0 (Thiếu)", "Sót K1 (Nay)", "Sót K2", "Sót K3", "Sót K4", "Sót K5", "Sót K6", "Sót K7"]
        df_anal = pd.DataFrame(rows_anal, columns=cols_anal)
        
        # Apply styling
        def highlight_cols(s):
            if s.name == "List 0 (Thiếu)":
                return ['background-color: #ffebee; color: #c0392b'] * len(s)
            elif s.name == "Sót K1 (Nay)":
                return ['background-color: #e8f8f5; color: #16a085'] * len(s)
            else:
                return [''] * len(s)
        
        styled_df = df_anal.style.apply(highlight_cols)
        st.dataframe(styled_df, height=600, use_container_width=True, hide_index=True)
