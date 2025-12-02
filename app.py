import streamlit as st
import requests
import json
import pandas as pd
from collections import Counter
from datetime import datetime, timedelta
import concurrent.futures
import time

# =============================================================================
# CONFIG & CONSTANTS
# =============================================================================

st.set_page_config(
    page_title="Soi Cầu Đa Năng 3 Miền - Pro Version",
    page_icon="🎲",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 24px;
        font-weight: bold;
        color: #ff4b4b;
        margin-bottom: 20px;
    }
    .prediction-card {
        background-color: #f0f2f6;
        padding: 15px;
        border-radius: 10px;
        margin-bottom: 10px;
    }
    .highlight-digit {
        color: #ff4b4b;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

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
    "TP. Hồ Chí Minh": "https://www.kqxs88.live/api/front/open/lottery/history/list/game?limitNum=60&gameCode=hochiminh",
    "Trà Vinh": "https://www.kqxs88.live/api/front/open/lottery/history/list/game?limitNum=60&gameCode=trvi",
    "Vĩnh Long": "https://www.kqxs88.live/api/front/open/lottery/history/list/game?limitNum=60&gameCode=vilo",
    "Vũng Tàu": "https://www.kqxs88.live/api/front/open/lottery/history/list/game?limitNum=60&gameCode=vuta",
    "Đà Nẵng": "https://www.kqxs88.live/api/front/open/lottery/history/list/game?limitNum=60&gameCode=dana",
    "Bình Định": "https://www.kqxs88.live/api/front/open/lottery/history/list/game?limitNum=60&gameCode=bidi",
    "Đắk Lắk": "https://www.kqxs88.live/api/front/open/lottery/history/list/game?limitNum=60&gameCode=dala",
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
    "Thứ 2":    ["TP. Hồ Chí Minh", "Đồng Tháp", "Cà Mau"],
    "Thứ 3":    ["Bến Tre", "Vũng Tàu", "Bạc Liêu"],
    "Thứ 4":    ["Đồng Nai", "Cần Thơ", "Sóc Trăng"],
    "Thứ 5":    ["Tây Ninh", "An Giang", "Bình Thuận"],
    "Thứ 6":    ["Vĩnh Long", "Bình Dương", "Trà Vinh"],
    "Thứ 7":    ["TP. Hồ Chí Minh", "Long An", "Bình Phước", "Hậu Giang"]
}

LICH_QUAY_TRUNG = {
    "Chủ Nhật": ["Kon Tum", "Khánh Hòa", "Thừa Thiên Huế"],
    "Thứ 2":    ["Thừa Thiên Huế", "Phú Yên"],
    "Thứ 3":    ["Đắk Lắk", "Quảng Nam"],
    "Thứ 4":    ["Đà Nẵng", "Khánh Hòa"],
    "Thứ 5":    ["Bình Định", "Quảng Trị", "Quảng Bình"],
    "Thứ 6":    ["Gia Lai", "Ninh Thuận"],
    "Thứ 7":    ["Đà Nẵng", "Quảng Ngãi", "Đắk Nông"]
}

LICH_QUAY_BAC = {
    "Thứ 2": "Hà Nội", "Thứ 3": "Quảng Ninh", "Thứ 4": "Bắc Ninh",
    "Thứ 5": "Hà Nội", "Thứ 6": "Hải Phòng", "Thứ 7": "Nam Định", "Chủ Nhật": "Thái Bình"
}

# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

@st.cache_data(ttl=60)
def http_get_issue_list(url):
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            data = response.json()
            if data.get("success"):
                return data.get("t", {}).get("issueList", [])
    except Exception as e:
        st.error(f"Lỗi kết nối: {e}")
    return []

def get_current_day_vietnamese():
    days = {0: "Thứ 2", 1: "Thứ 3", 2: "Thứ 4", 3: "Thứ 5", 4: "Thứ 6", 5: "Thứ 7", 6: "Chủ Nhật"}
    return days[datetime.now().weekday()]

def generate_cham_tong(list_missing):
    result_set = set()
    for d_str in list_missing:
        try:
            d = int(d_str)
        except: continue
        # Chạm
        for i in range(100):
            s = f"{i:02d}"
            if str(d) in s: result_set.add(s)
        # Tổng
        for i in range(100):
            s = f"{i:02d}"
            digit_sum = (int(s[0]) + int(s[1])) % 10
            if digit_sum == d: result_set.add(s)
    return sorted(list(result_set))

def generate_nhi_hop(list_digits):
    result_set = set()
    for d1 in list_digits:
        for d2 in list_digits:
            result_set.add(f"{d1}{d2}")
    return sorted(list(result_set))

def detect_special_pattern(prize_str):
    prize_str = prize_str.strip()
    if not prize_str or not prize_str.isdigit(): return False, None
    unique_digits = set(prize_str)
    if len(unique_digits) <= 3:
        return True, prize_str[-2:]
    return False, None

def get_all_numbers(item):
    try:
        detail = json.loads(item['detail'])
        all_numbers = []
        for field in detail:
            prizes = field.split(",")
            for p in prizes:
                p = p.strip()
                if len(p) >= 2:
                    all_numbers.append(p)
        return all_numbers
    except:
        return []

# =============================================================================
# MAIN APP
# =============================================================================

def main():
    st.markdown('<div class="main-header">🎲 PHẦN MỀM SOI CẦU ĐA NĂNG 3 MIỀN (STREAMLIT VERSION)</div>', unsafe_allow_html=True)

    # --- SIDEBAR ---
    with st.sidebar:
        st.header("Cấu Hình")
        
        # Region Selection
        region = st.selectbox("Chọn Miền", ["Miền Bắc", "Miền Nam", "Miền Trung"])
        
        # Day Selection
        current_day = get_current_day_vietnamese()
        days_list = ["Thứ 2", "Thứ 3", "Thứ 4", "Thứ 5", "Thứ 6", "Thứ 7", "Chủ Nhật"]
        default_day_idx = days_list.index(current_day)
        selected_day = st.selectbox("Chọn Thứ", days_list, index=default_day_idx)
        
        # Station Selection logic
        stations = []
        if region == "Miền Bắc":
            lbl_tinh = LICH_QUAY_BAC.get(selected_day, "")
            stations = [f"Miền Bắc ({lbl_tinh})", "Miền Bắc 75s", "Miền Bắc 45s"]
        elif region == "Miền Nam":
            stations = LICH_QUAY_NAM.get(selected_day, [])
        elif region == "Miền Trung":
            stations = LICH_QUAY_TRUNG.get(selected_day, [])
            
        if not stations:
            st.warning(f"Không có lịch quay {region} {selected_day}")
            return

        # Multi-station mode detection
        is_multi_station_mode = region in ["Miền Nam", "Miền Trung"]
        
        # Station Selectbox
        # If multi-station mode, we still allow selecting a specific station for Tabs 1-3
        # But Tab 4 will use all stations.
        selected_station = st.selectbox("Chọn Đài (cho Tab 1-3)", stations)
        
        # Auto-reload option
        auto_reload = st.checkbox("Tự động làm mới (30s)", value=False)
        if auto_reload:
            time.sleep(1)
            st.rerun()

    # --- DATA FETCHING (Single Station) ---
    api_key = selected_station
    if "Miền Bắc" in selected_station and "45s" not in selected_station and "75s" not in selected_station:
        api_key = "Miền Bắc"
    
    url = DAI_API.get(api_key)
    if not url:
        # Fallback search
        for k, v in DAI_API.items():
            if k == api_key:
                url = v
                break
    
    if url:
        data = http_get_issue_list(url)
    else:
        st.error("Không tìm thấy URL cho đài này.")
        data = []

    if not data:
        st.warning("Chưa có dữ liệu hoặc lỗi tải.")
        return

    # --- TABS ---
    tab1, tab2, tab3, tab4 = st.tabs([
        "Tab 1: List 0 & Cầu", 
        "Tab 2: So Sánh Kết Quả", 
        "Tab 3: Phân Tích Chu Kỳ", 
        "Tab 4: Dự Đoán Đa Năng"
    ])

    # --- TAB 1: LIST 0 & CẦU ---
    with tab1:
        render_tab1(data)

    # --- TAB 2: SO SÁNH ---
    with tab2:
        render_tab2(data)

    # --- TAB 3: CHU KỲ ---
    with tab3:
        render_tab3(data, region)

    # --- TAB 4: MULTI-STATION / PREDICTION ---
    with tab4:
        if is_multi_station_mode:
            render_tab4_multi(selected_day, stations)
        else:
            render_tab4_single(data)

# =============================================================================
# TAB RENDER FUNCTIONS
# =============================================================================

def render_tab1(data):
    st.subheader("Phân Tích List 0 & Cầu N1-N0")
    
    if len(data) < 2:
        st.warning("Cần ít nhất 2 kỳ dữ liệu.")
        return

    # Process data for table
    rows = []
    for i in range(min(15, len(data) - 1)):
        current = data[i]
        prev = data[i+1]
        
        turn_num = current.get('turnNum')
        
        # Get Special Prize (ĐB)
        try:
            detail = json.loads(current['detail'])
            db = detail[0].split(',')[0]
            db_last2 = db[-2:] if len(db) >= 2 else ""
        except: db_last2 = ""
        
        # Calculate List 0 (Missing digits in GĐB)
        missing = []
        if db:
            for d in "0123456789":
                if d not in db: missing.append(d)
        list0_str = "".join(missing)
        
        # Calculate Bridge (N1-N0) logic (simplified for demo)
        # Real logic from Tkinter app:
        # 1. Get List 0 from Prev period
        # 2. Generate Pairs (N-1)(N-2)
        # 3. Check if current DB matches
        
        rows.append({
            "Kỳ": turn_num,
            "ĐB": db_last2,
            "List 0 (Thiếu ĐB)": list0_str,
            "Tổng List 0": len(missing)
        })
        
    st.dataframe(pd.DataFrame(rows), use_container_width=True)

def render_tab2(data):
    st.subheader("So Sánh Kết Quả & Thống Kê")
    # Placeholder for complex comparison logic
    st.info("Chức năng so sánh chi tiết đang được cập nhật...")
    
    # Simple display of recent results
    st.write("Kết quả gần đây:")
    recent_data = []
    for item in data[:5]:
        detail = json.loads(item['detail'])
        recent_data.append({
            "Kỳ": item['turnNum'],
            "ĐB": detail[0],
            "G1": detail[1]
        })
    st.table(pd.DataFrame(recent_data))

def render_tab3(data, region):
    st.subheader("Phân Tích Chu Kỳ (List 0, Nhị Hợp, K1-K10)")
    
    # Determine prize range
    max_prize_index = 9 if "Bắc" in region else 13
    
    rows = []
    for item in data[:10]:
        detail = json.loads(item['detail'])
        prizes_flat = []
        for field in detail: prizes_flat += field.split(",")
        
        # Analyze prizes
        day_digit_counts = Counter()
        # Logic simplified: count digits in relevant prizes
        for i, prize in enumerate(prizes_flat):
            if i <= max_prize_index:
                prize = prize.strip()
                if len(prize) >= 2:
                    for digit in prize: day_digit_counts[digit] += 1
        
        # List 0 (Digits appearing 0 times in the analyzed range)
        list0 = [d for d in "0123456789" if day_digit_counts[d] == 0]
        
        rows.append({
            "Kỳ": item['turnNum'],
            "List 0 (Chu Kỳ)": "".join(list0),
            "Số lượng": len(list0)
        })
        
    st.dataframe(pd.DataFrame(rows), use_container_width=True)

def render_tab4_single(data):
    st.subheader("Dự Đoán Lô Nháy & Cặp (Miền Bắc)")
    
    if len(data) < 2:
        st.warning("Không đủ dữ liệu.")
        return
        
    # Reuse logic from TabMode4.calculate_tab4_predictions
    # For now, simplified display
    st.info("Đang hiển thị chế độ Đơn Đài (Miền Bắc)")
    
    # Example prediction logic
    current_nums = get_all_numbers(data[0])
    prev_nums = get_all_numbers(data[1])
    
    # Find common digits/pairs (simplified)
    common = set(current_nums).intersection(set(prev_nums))
    st.write(f"Số lô trùng với kỳ trước: {len(common)}")
    st.write(f"Các số trùng: {', '.join(list(common)[:10])}...")

def render_tab4_multi(weekday, stations):
    st.subheader(f"📊 KẾT QUẢ TỔNG HỢP CÁC ĐÀI ({weekday})")
    
    if st.button("Phân Tích Tất Cả Đài"):
        with st.spinner(f"Đang tải dữ liệu {len(stations)} đài..."):
            # Parallel Fetching
            multi_data = {}
            with concurrent.futures.ThreadPoolExecutor() as executor:
                future_to_station = {executor.submit(http_get_issue_list, DAI_API.get(s)): s for s in stations}
                for future in concurrent.futures.as_completed(future_to_station):
                    station = future_to_station[future]
                    try:
                        data = future.result()
                        if data: multi_data[station] = data
                    except Exception as e:
                        st.error(f"Lỗi tải {station}: {e}")
            
            # Calculate Predictions
            results = []
            for station in stations:
                if station in multi_data:
                    pred = calculate_tab4_predictions(multi_data[station])
                    results.append({
                        "Đài": station,
                        "Chữ số dự đoán": pred['digits'],
                        "Top Đầu": pred['top_dau'],
                        "Top Đuôi": pred['top_duoi'],
                        "Trùng Đầu": pred['match_head'],
                        "Trùng Đuôi": pred['match_tail']
                    })
                else:
                    results.append({"Đài": station, "Chữ số dự đoán": "Lỗi/Không có DL"})
            
            # Display Transposed DataFrame (Stations as Columns)
            df = pd.DataFrame(results).set_index("Đài").T
            st.dataframe(df, use_container_width=True)

def calculate_tab4_predictions(data):
    """Logic from TabMode4"""
    if not data or len(data) < 2:
        return {"digits": "", "top_dau": "", "top_duoi": "", "match_head": "", "match_tail": ""}
    
    # 1. Predicted Digits (Simplified logic: Most frequent in last 2 periods)
    all_digits = []
    for item in data[:2]:
        nums = get_all_numbers(item)
        for n in nums:
            for d in n: all_digits.append(d)
    
    freq = Counter(all_digits)
    top_5_digits = [d for d, c in freq.most_common(5)]
    predicted_digits = sorted(top_5_digits)
    
    # 2. Top Head/Tail (Last 3 periods)
    dau_freq = Counter()
    duoi_freq = Counter()
    for item in data[:3]:
        nums = get_all_numbers(item)
        for n in nums:
            if len(n) >= 2:
                dau_freq[n[-2]] += 1
                duoi_freq[n[-1]] += 1
                
    top_dau = [d for d, c in dau_freq.most_common(5)]
    top_duoi = [d for d, c in duoi_freq.most_common(5)]
    
    # 3. Matches
    match_head = [d for d in predicted_digits if d in top_dau]
    match_tail = [d for d in predicted_digits if d in top_duoi]
    
    return {
        "digits": ",".join(predicted_digits),
        "top_dau": "-".join(top_dau),
        "top_duoi": "-".join(top_duoi),
        "match_head": ",".join(match_head) if match_head else "-",
        "match_tail": ",".join(match_tail) if match_tail else "-"
    }

if __name__ == "__main__":
    main()
