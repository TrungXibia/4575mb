import streamlit as st
import requests
import json
from collections import Counter
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from datetime import datetime
import pandas as pd

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
    "Bến Tre": "https://www.kqxs88.live/api/front/open/lottery/history/list/game?limitNum=60&gameCode=betr",
    "Vũng Tàu": "https://www.kqxs88.live/api/front/open/lottery/history/list/game?limitNum=60&gameCode=vutu",
    "Bạc Liêu": "https://www.kqxs88.live/api/front/open/lottery/history/list/game?limitNum=60&gameCode=bali",
    "Cà Mau": "https://www.kqxs88.live/api/front/open/lottery/history/list/game?limitNum=60&gameCode=camu",
    "Cần Thơ": "https://www.kqxs88.live/api/front/open/lottery/history/list/game?limitNum=60&gameCode=cath",
    "TP. Hồ Chí Minh": "https://www.kqxs88.live/api/front/open/lottery/history/list/game?limitNum=60&gameCode=hochi",
    "Tiền Giang": "https://www.kqxs88.live/api/front/open/lottery/history/list/game?limitNum=60&gameCode=tigi",
    "Kiên Giang": "https://www.kqxs88.live/api/front/open/lottery/history/list/game?limitNum=60&gameCode=kigi",
    "Đà Lạt": "https://www.kqxs88.live/api/front/open/lottery/history/list/game?limitNum=60&gameCode=dalat",
    "Đồng Nai": "https://www.kqxs88.live/api/front/open/lottery/history/list/game?limitNum=60&gameCode=dona",
    "Đồng Tháp": "https://www.kqxs88.live/api/front/open/lottery/history/list/game?limitNum=60&gameCode=doth",
    "Hậu Giang": "https://www.kqxs88.live/api/front/open/lottery/history/list/game?limitNum=60&gameCode=hagi",
    "An Giang": "https://www.kqxs88.live/api/front/open/lottery/history/list/game?limitNum=60&gameCode=angi",
    "Long An": "https://www.kqxs88.live/api/front/open/lottery/history/list/game?limitNum=60&gameCode=loan",
    "Sóc Trăng": "https://www.kqxs88.live/api/front/open/lottery/history/list/game?limitNum=60&gameCode=sotr",
    "Tây Ninh": "https://www.kqxs88.live/api/front/open/lottery/history/list/game?limitNum=60&gameCode=tayni",
    "Trà Vinh": "https://www.kqxs88.live/api/front/open/lottery/history/list/game?limitNum=60&gameCode=trvi",
    "Vĩnh Long": "https://www.kqxs88.live/api/front/open/lottery/history/list/game?limitNum=60&gameCode=vilo",
    "Đà Nẵng": "https://www.kqxs88.live/api/front/open/lottery/history/list/game?limitNum=60&gameCode=dana",
    "Bình Định": "https://www.kqxs88.live/api/front/open/lottery/history/list/game?limitNum=60&gameCode=bidi",
    "Đắk Lắk": "https://www.kqxs88.live/api/front/open/lottery/history/list/game?limitNum=60&gameCode=dalak",
    "Đắk Nông": "https://www.kqxs88.live/api/front/open/lottery/history/list/game?limitNum=60&gameCode=dano",
    "Gia Lai": "https://www.kqxs88.live/api/front/open/lottery/history/list/game?limitNum=60&gameCode=gial",
    "Khánh Hòa": "https://www.kqxs88.live/api/front/open/lottery/history/list/game?limitNum=60&gameCode=khah",
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
    "Thứ 2":    ["TP. Hồ Chí Minh", "Đồng Tháp", "Cà Mau"],
    "Thứ 3":    ["Bến Tre", "Vũng Tàu", "Bạc Liêu"],
    "Thứ 4":    ["Đồng Nai", "Cần Thơ", "Sóc Trăng"],
    "Thứ 5":    ["An Giang", "Tây Ninh", "Bình Thuận"],
    "Thứ 6":    ["Vĩnh Long", "Bình Dương", "Trà Vinh"],
    "Thứ 7":    ["TP. Hồ Chí Minh", "Long An", "Hậu Giang"]
}

LICH_QUAY_TRUNG = {
    "Chủ Nhật": ["Quảng Trị"],
    "Thứ 2":    ["Thừa Thiên Huế", "Phú Yên"],
    "Thứ 3":    ["Đắk Lắk", "Quảng Nam"],
    "Thứ 4":    ["Đà Nẵng", "Khánh Hòa"],
    "Thứ 5":    ["Bình Định", "Quảng Trị", "Quảng Bình"],
    "Thứ 6":    ["Gia Lai", "Ninh Thuận"],
    "Thứ 7":    ["Đắk Nông", "Quảng Ngãi", "Đà Nẵng", "Kon Tum"]
}

GIAI_LABELS_MB = [
    "ĐB", "G1", "G2-1", "G2-2",
    "G3-1", "G3-2", "G3-3", "G3-4", "G3-5", "G3-6",
    "G4-1", "G4-2", "G4-3", "G4-4",
    "G5-1", "G5-2", "G5-3", "G5-4", "G5-5", "G5-6",
    "G6-1", "G6-2", "G6-3",
    "G7-1", "G7-2", "G7-3", "G7-4"
]

# =============================================================================
# NETWORK UTILS
# =============================================================================

@st.cache_resource
def _get_session():
    session = requests.Session()
    retries = Retry(total=3, backoff_factor=0.3, status_forcelist=[500, 502, 503, 504])
    adapter = HTTPAdapter(max_retries=retries)
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    return session

SESSION = _get_session()

def http_get_issue_list(url: str, timeout: int = 10):
    try:
        r = SESSION.get(url, headers=HEADERS, timeout=timeout)
        return r.json() if r.status_code == 200 else None
    except:
        return None

def get_current_day_vietnamese():
    day_map = ["Thứ 2", "Thứ 3", "Thứ 4", "Thứ 5", "Thứ 6", "Thứ 7", "Chủ Nhật"]
    return day_map[datetime.now().weekday()]

# =============================================================================
# STREAMLIT APP
# =============================================================================

def bridge_ab(l1, l2):
    s = set()
    for a in l1:
        for b in l2:
            s.add(a+b)
            s.add(b+a)
    return sorted(list(s))

def diff(src, target):
    return sorted(list(set(src) - set(target)))

def main():
    st.set_page_config(
        page_title="Phần Mềm Soi Cầu Đa Năng 3 Miền",
        page_icon="🎰",
        layout="wide"
    )
    
    st.title("🎰 Phần Mềm Soi Cầu Đa Năng 3 Miền - Pro Version")
    
    # Initialize session state
    if 'raw_data' not in st.session_state:
        st.session_state.raw_data = []
    
    # Sidebar controls
    with st.sidebar:
        st.header("⚙️ Cấu hình")
        
        region = st.selectbox("Khu vực", ["Miền Bắc", "Miền Nam", "Miền Trung"], index=0)
        
        # Filter stations by region
        if region == "Miền Bắc":
            stations = ["Miền Bắc", "Miền Bắc 75s"]
        elif region == "Miền Nam":
            stations = [k for k in DAI_API.keys() if k in LICH_QUAY_NAM.get(get_current_day_vietnamese(), [])]
            if not stations:
                stations = ["TP. Hồ Chí Minh", "Tiền Giang", "Bến Tre", "Vũng Tàu", "Cần Thơ", 
                           "Đồng Tháp", "Cà Mau", "Bạc Liêu", "Kiên Giang", "Đà Lạt", 
                           "Đồng Nai", "An Giang", "Tây Ninh", "Vĩnh Long", "Long An", 
                           "Hậu Giang", "Sóc Trăng", "Trà Vinh"]
        else:  # Miền Trung
            stations = [k for k in DAI_API.keys() if k in LICH_QUAY_TRUNG.get(get_current_day_vietnamese(), [])]
            if not stations:
                stations = ["Đà Nẵng", "Quảng Nam", "Quảng Ngãi", "Bình Định", "Phú Yên",
                           "Khánh Hòa", "Ninh Thuận", "Đắk Lắk", "Đắk Nông", "Gia Lai",
                           "Kon Tum", "Quảng Bình", "Quảng Trị", "Thừa Thiên Huế"]
        
        station = st.selectbox("Đài", stations)
        
        use_today = st.checkbox("Lịch hôm nay", value=True)
        
        if st.button("🔄 TẢI LẠI", use_container_width=True):
            if station in DAI_API:
                with st.spinner("Đang tải dữ liệu..."):
                    data = http_get_issue_list(DAI_API[station])
                    if data and data.get('data'):
                        st.session_state.raw_data = data['data'][:30]
                        st.success(f"✅ Đã tải {len(st.session_state.raw_data)} kỳ")
                    else:
                        st.error("❌ Không thể tải dữ liệu")
        
        st.divider()
        st.subheader("Chọn giải để phân tích")
        
        # Prize checkboxes
        if 'giai_selections' not in st.session_state:
            st.session_state.giai_selections = {label: True for label in GIAI_LABELS_MB}
        
        col1, col2 = st.columns(2)
        for i, label in enumerate(GIAI_LABELS_MB):
            if i % 2 == 0:
                with col1:
                    st.session_state.giai_selections[label] = st.checkbox(
                        label, 
                        value=st.session_state.giai_selections.get(label, True),
                        key=f"giai_{label}"
                    )
            else:
                with col2:
                    st.session_state.giai_selections[label] = st.checkbox(
                        label, 
                        value=st.session_state.giai_selections.get(label, True),
                        key=f"giai_{label}"
                    )
    
    # Main content
    if not st.session_state.raw_data:
        st.info("👈 Chọn đài và nhấn 'TẢI LẠI' để bắt đầu")
        return
    
    # Process data
    display_indices = [0]  # Always include ĐB
    headers = ["Kỳ", "ĐB"]
    
    for i, label in enumerate(GIAI_LABELS_MB):
        if i == 0:
            continue
        if st.session_state.giai_selections.get(label, False):
            display_indices.append(i)
            headers.append(label)
    
    # Build result table
    rows_res = []
    for item in st.session_state.raw_data:
        d = json.loads(item['detail'])
        prizes_flat = []
        for f in d:
            prizes_flat += f.split(',')
        
        row = {"Kỳ": item['turnNum']}
        for idx, header in zip(display_indices, headers[1:]):
            if idx < len(prizes_flat):
                row[header] = prizes_flat[idx]
            else:
                row[header] = ""
        rows_res.append(row)
    
    # Display result table
    st.subheader("📊 Bảng Kết Quả")
    df_result = pd.DataFrame(rows_res)
    st.dataframe(df_result, use_container_width=True, height=400)
    
    # Analysis
    st.subheader("🔍 Phân Tích & Cầu Số")
    
    processed = []
    for item in st.session_state.raw_data:
        detail = json.loads(item['detail'])
        counter = Counter()
        prizes_flat = []
        for field in detail:
            prizes_flat += field.split(",")
        
        g_nums = []
        for i, label in enumerate(GIAI_LABELS_MB):
            if st.session_state.giai_selections.get(label, False):
                if i < len(prizes_flat):
                    g_nums.extend([ch for ch in prizes_flat[i].strip() if ch.isdigit()])
        
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
    
    # Build analysis table
    rows_anal = []
    for i in range(len(processed)):
        curr = processed[i]
        row = {
            "Kỳ": curr["ky"],
            "List 0": ",".join(curr["list0"])
        }
        
        if i + 2 < len(processed):
            l0_prev1 = processed[i+1]["list0"]
            l0_prev2 = processed[i+2]["list0"]
            current_dan = bridge_ab(l0_prev2, l0_prev1)
            
            for k in range(7):
                target_idx = i - k
                if target_idx < 0:
                    row[f"Sót K{k+1}"] = ""
                else:
                    res_target = processed[target_idx]["res"]
                    current_dan = diff(current_dan, res_target)
                    row[f"Sót K{k+1}"] = " ".join(current_dan)
        else:
            for k in range(7):
                row[f"Sót K{k+1}"] = ""
        
        rows_anal.append(row)
    
    df_anal = pd.DataFrame(rows_anal)
    
    # Style the dataframe
    def highlight_cols(s):
        if s.name == "List 0":
            return ['background-color: #ffebee; color: #c0392b'] * len(s)
        elif s.name == "Sót K1":
            return ['background-color: #e8f8f5; color: #16a085'] * len(s)
        else:
            return [''] * len(s)
    
    st.dataframe(
        df_anal.style.apply(highlight_cols),
        use_container_width=True,
        height=400
    )
    
    # Legend
    st.caption("🔴 **List 0**: Các số không xuất hiện | 🟢 **Sót K1**: Cầu cho kỳ hiện tại")

if __name__ == "__main__":
    main()
