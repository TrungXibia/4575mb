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
# STREAMLIT APP
# =============================================================================

st.set_page_config(page_title="Phần Mềm Soi Cầu 3 Miền", layout="wide")

# CSS for Compact UI
st.markdown("""
<style>
    /* Compact Layout */
    .block-container {
        padding-top: 0.5rem !important;
        padding-bottom: 0rem !important;
        padding-left: 1rem !important;
        padding-right: 1rem !important;
        max-width: 100% !important;
    }
    
    /* Reduce font sizes */
    html, body, [class*="css"] {
        font-size: 12px;
    }
    p, .stMarkdown, .stText {
        font-size: 13px !important;
        margin-bottom: 0px !important;
    }
    
    /* Compact Controls */
    div[data-testid="stVerticalBlock"] > div {
        gap: 0.2rem !important;
    }
    
    /* Compact Dataframe */
    .stDataFrame {
        font-size: 11px !important;
    }
    
    /* Headers */
    h1, h2, h3, h4, h5 {
        margin-bottom: 0.2rem !important;
        padding-top: 0 !important;
        color: #ff4b4b !important;
    }
    
    /* Expander */
    .streamlit-expanderHeader {
        font-size: 13px !important;
        padding: 0.2rem 0.5rem !important;
        background-color: #f8f9fa !important;
        border: 1px solid #dee2e6 !important;
        color: #31333F !important;
    }
    
    /* Buttons */
    button {
        height: auto !important;
        padding-top: 0.2rem !important;
        padding-bottom: 0.2rem !important;
    }
    
    /* Checkboxes */
    div[data-testid="stCheckbox"] {
        min-height: 1rem !important;
        margin-top: -8px !important;
        margin-bottom: -8px !important;
    }
    div[data-testid="stCheckbox"] label {
        font-size: 11px !important;
        padding-left: 0.2rem !important;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'raw_data' not in st.session_state:
    st.session_state.raw_data = []
    st.session_state.last_open_time = ""
    st.session_state.current_station = ""
    # Auto load Miền Bắc on first run
    data, time = load_data("Miền Bắc")
    st.session_state.raw_data = data
    st.session_state.last_open_time = time
    st.session_state.current_station = "Miền Bắc"

if 'selected_giai' not in st.session_state:
    st.session_state.selected_giai = [2, 3]  # Default: G2-1, G2-2

# =============================================================================
# TOP CONTROLS
# =============================================================================

st.markdown("#### 🛠️ CẤU HÌNH & DỮ LIỆU")

col1, col2, col3, col4 = st.columns([1.5, 1.5, 3, 3])

with col1:
    region = st.selectbox("Khu vực", ["Miền Bắc", "Miền Nam", "Miền Trung"], index=0, label_visibility="collapsed")

with col2:
    # Default to current day
    current_day = get_current_day_vietnamese()
    try:
        default_day_idx = DAYS_OF_WEEK.index(current_day)
    except:
        default_day_idx = 0
    selected_day = st.selectbox("Thứ", DAYS_OF_WEEK, index=default_day_idx, label_visibility="collapsed")

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
        station = st.selectbox("Đài", stations, index=0, label_visibility="collapsed")
    else:
        station = st.selectbox("Đài", ["Không có lịch quay"], disabled=True, label_visibility="collapsed")

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

    # Manual Reload Button
    if st.button("🔄 TẢI LẠI", type="primary", use_container_width=True):
        if station and station != "Không có lịch quay":
            with st.spinner(f"Đang tải {station}..."):
                data, time = load_data(station)
                st.session_state.raw_data = data
                st.session_state.last_open_time = time
                st.session_state.current_station = station
                st.rerun()

    # Determine Interval and Next Draw Time Logic
    interval_seconds = 0
    draw_time_config = "" # For traditional lotteries (HH:mm)
    
    if "75s" in station:
        interval_seconds = 75
    elif "45s" in station:
        interval_seconds = 45
    else:
        # Traditional Lottery Schedules
        if region == "Miền Bắc":
            draw_time_config = "18:15"
        elif region == "Miền Nam":
            draw_time_config = "16:15"
        elif region == "Miền Trung":
            draw_time_config = "17:15"

    # Display Time & Countdown (Real-time Clock)
    clock_html = f"""
    <style>
        body {{
            margin: 0;
            padding: 0;
            font-family: "Source Sans Pro", sans-serif;
            font-size: 13px;
            background-color: transparent;
            color: #31333F;
        }}
        .container {{
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding-top: 8px;
        }}
        .highlight {{
            color: #ff4b4b;
            font-weight: bold;
            font-size: 14px;
        }}
        .clock {{
            color: #0068c9;
            font-weight: bold;
            font-size: 14px;
        }}
        .countdown {{
            color: #28a745; /* Green */
            font-weight: bold;
            font-size: 14px;
            margin-left: 10px;
        }}
        .label {{
            font-weight: 600;
            margin-right: 4px;
        }}
    </style>
    <div class="container">
        <div>
            <span class="label">📅 Kỳ:</span>
            <span class="highlight">{st.session_state.last_open_time}</span>
        </div>
        <div>
            <span class="label">⏳ Sắp quay:</span>
            <span id="countdown" class="countdown">--:--</span>
        </div>
        <div>
            <span class="label">🕒</span>
            <span id="clock" class="clock">Loading...</span>
        </div>
    </div>
    <script>
        var interval = {interval_seconds};
        var lastTimeStr = "{st.session_state.last_open_time}"; // Format: YYYY-MM-DD HH:mm:ss
        var drawTimeConfig = "{draw_time_config}"; // Format: HH:mm
        
        function parseDate(str) {{
            // Handle format YYYY-MM-DD HH:mm:ss for Safari/Firefox compatibility
            var t = str.split(/[- :]/);
            return new Date(t[0], t[1]-1, t[2], t[3], t[4], t[5]);
        }}

        function updateClock() {{
            var now = new Date();
            
            // 1. Update System Clock
            var timeStr = now.toLocaleTimeString('vi-VN', {{hour12: false}});
            var dateStr = now.toLocaleDateString('vi-VN');
            document.getElementById('clock').innerText = timeStr;

            // 2. Update Countdown
            var targetDate = null;
            var diff = 0;

            if (interval > 0) {{
                // Logic for 75s/45s
                var lastDate = parseDate(lastTimeStr);
                targetDate = new Date(lastDate.getTime() + interval * 1000);
                
                // If target is in the past (data outdated), keep adding interval to find next theoretical draw
                // or just show "Waiting..." if we strictly follow the last loaded data.
                // Here we strictly follow last loaded data + interval to prompt user to reload.
                diff = targetDate - now;
            }} else if (drawTimeConfig) {{
                // Logic for Traditional
                var parts = drawTimeConfig.split(":");
                targetDate = new Date(now.getFullYear(), now.getMonth(), now.getDate(), parts[0], parts[1], 0);
                if (now > targetDate) {{
                    // If passed today's draw time, target tomorrow
                    targetDate.setDate(targetDate.getDate() + 1);
                }}
                diff = targetDate - now;
            }}

            var cdEl = document.getElementById('countdown');
            
            if (diff > 0) {{
                var hours = Math.floor(diff / (1000 * 60 * 60));
                var minutes = Math.floor((diff % (1000 * 60 * 60)) / (1000 * 60));
                var seconds = Math.floor((diff % (1000 * 60)) / 1000);
                
                var hStr = hours > 0 ? hours.toString().padStart(2, '0') + ':' : '';
                var mStr = minutes.toString().padStart(2, '0');
                var sStr = seconds.toString().padStart(2, '0');
                
                cdEl.innerText = hStr + mStr + ':' + sStr;
                cdEl.style.color = "#28a745"; // Green
            }} else {{
                if (interval > 0) {{
                     cdEl.innerText = "Đang quay...";
                     cdEl.style.color = "#dc3545"; // Red
                }} else {{
                     cdEl.innerText = "Đang quay...";
                     cdEl.style.color = "#dc3545";
                }}
            }}
        }}
        setInterval(updateClock, 1000);
        updateClock();
    </script>
    """
    components.html(clock_html, height=40)

# Prize Selection
with st.expander("🎯 CHỌN GIẢI ĐỂ PHÂN TÍCH", expanded=True):
    # Control buttons
    c1, c2, c3 = st.columns([1, 1, 8])
    with c1:
        if st.button("Chọn hết"):
            st.session_state.selected_giai = list(range(1, len(GIAI_LABELS_MB)))
            st.rerun()
    with c2:
        if st.button("Bỏ chọn"):
            st.session_state.selected_giai = []
            st.rerun()
            
    # Create checkboxes in columns (9 columns)
    num_cols = 9
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
    st.info("Chưa có dữ liệu.")
else:
    # Create two columns (Adjust ratio to make left side smaller)
    col_left, col_right = st.columns([2.5, 5.5])
    
    with col_left:
        st.markdown("##### 📊 KẾT QUẢ")
        
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
        
        # Configure columns for compactness (Force pixel width)
        column_config = {
            "Kỳ": st.column_config.TextColumn("Kỳ", width=70),
            "ĐB": st.column_config.TextColumn("ĐB", width=50),
        }
        for h in headers[2:]:
             column_config[h] = st.column_config.TextColumn(h, width=50)

        st.dataframe(
            df_res, 
            height=700, 
            use_container_width=True, 
            hide_index=True,
            column_config=column_config
        )
    
    with col_right:
        st.markdown("##### 📈 PHÂN TÍCH LIST 0 & SÓT K1-K7")
        
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
            
            # Sót K0 (N1-N0): Bridge current row's List 0 with next row's List 0
            if i + 1 < len(processed):
                l0_current = curr["list0"]
                l0_next = processed[i + 1]["list0"]
                bridge_k0 = bridge_ab(l0_next, l0_current)
                # Subtract current draw's results
                bridge_k0 = diff(bridge_k0, curr["res"])
                row.append(" ".join(bridge_k0))
            else:
                row.append("")
            
            # Sót K1-K7: Display data from previous row (shifted down)
            # Row i shows K1-K7 calculated for row i-1
            if i > 0 and i + 1 < len(processed):
                # Use data from previous row (i-1)
                l0_prev1 = processed[i]["list0"]      # N1 for row i-1
                l0_prev2 = processed[i + 1]["list0"]  # N2 for row i-1
                current_dan = bridge_ab(l0_prev2, l0_prev1)
                
                for k in range(7):
                    # K1 uses i, K2 uses i-1, K3 uses i-2, etc.
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
        
        cols_anal = ["Kỳ", "List 0 (Thiếu)", "Sót K0 (N1-N0)", "Sót K1 (Nay)", "Sót K2", "Sót K3", "Sót K4", "Sót K5", "Sót K6", "Sót K7"]
        df_anal = pd.DataFrame(rows_anal, columns=cols_anal)
        
        # Apply styling
        def highlight_cols(s):
            styles = []
            for val in s:
                if s.name == "List 0 (Thiếu)":
                    styles.append('background-color: #ffebee; color: #c0392b')
                elif s.name == "Sót K0 (N1-N0)":
                    # Only highlight if cell has value
                    if val and str(val).strip():
                        styles.append('background-color: #fff3e0; color: #e67e22')  # Orange
                    else:
                        styles.append('')
                elif s.name == "Sót K1 (Nay)":
                    # Only highlight if cell has value
                    if val and str(val).strip():
                        styles.append('background-color: #e8f8f5; color: #16a085')  # Green
                    else:
                        styles.append('')
                else:
                    styles.append('')
            return styles
        
        styled_df = df_anal.style.apply(highlight_cols)
        
        # Configure columns for compactness (Force pixel width)
        anal_config = {
            "Kỳ": st.column_config.TextColumn("Kỳ", width=70),
            "List 0 (Thiếu)": st.column_config.TextColumn("List 0 (Thiếu)", width=80),
            "Sót K0 (N1-N0)": st.column_config.TextColumn("Sót K0 (N1-N0)", width=85),
            "Sót K1 (Nay)": st.column_config.TextColumn("Sót K1 (Nay)", width=70),
        }
        for k in range(2, 8):
             anal_config[f"Sót K{k}"] = st.column_config.TextColumn(f"Sót K{k}", width=70)

        st.dataframe(
            styled_df, 
            height=700, 
            use_container_width=True, 
            hide_index=True,
            column_config=anal_config
        )

