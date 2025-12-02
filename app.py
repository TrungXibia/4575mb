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
# HELPER FUNCTIONS (Advanced)
# =============================================================================

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
    """Get all numbers from a result item"""
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

def get_prize3_numbers(item):
    """Get all numbers from Prize 3 (G3)"""
    try:
        detail = json.loads(item['detail'])
        # G3 is index 4-9 (6 prizes)
        g3_numbers = []
        for i in range(4, 10):
            if i < len(detail):
                prizes = detail[i].split(",")
                for p in prizes:
                    p = p.strip()
                    if len(p) >= 2:
                        g3_numbers.append(p)
        return g3_numbers
    except:
        return []

def find_digit_positions_in_g3(g3_numbers, digit1, digit2, max_distance=2):
    """Find positions of 2 digits in G3 that are close to each other"""
    positions1 = []
    positions2 = []
    
    for idx, num in enumerate(g3_numbers):
        for pos, digit in enumerate(num):
            if digit == digit1:
                positions1.append((idx, pos, num))
            if digit == digit2:
                positions2.append((idx, pos, num))
    
    valid_pairs = []
    for p1 in positions1:
        for p2 in positions2:
            if p1[0] == p2[0]: # Same prize
                distance = abs(p1[1] - p2[1])
                if distance <= max_distance and distance > 0:
                    valid_pairs.append({
                        'prize_idx': p1[0],
                        'pos1': p1[1],
                        'pos2': p2[1],
                        'distance': distance
                    })
    return valid_pairs

def apply_pattern_to_current(current_g3, pattern):
    """Apply a pattern to current G3 to predict digits"""
    predicted = []
    if pattern['prize_idx'] < len(current_g3):
        current_num = current_g3[pattern['prize_idx']]
        p1, p2 = pattern['pos1'], pattern['pos2']
        if p1 < len(current_num) and p2 < len(current_num):
            predicted.append({
                'digit1': current_num[p1],
                'digit2': current_num[p2]
            })
    return predicted

def bridge_ab(l1, l2):
    """Create pairs from two lists"""
    s = set()
    for a in l1:
        for b in l2:
            s.add(a+b); s.add(b+a)
    return sorted(list(s))

def diff(src, target):
    """Remove items in target from src"""
    return sorted(list(set(src) - set(target)))

# =============================================================================
# TAB RENDER FUNCTIONS (Full Logic)
# =============================================================================

def render_tab1(data):
    st.subheader("Phân Tích List 0 & Cầu N1-N0 (Chi Tiết)")
    
    if len(data) < 10:
        st.warning("Cần ít nhất 10 kỳ dữ liệu để phân tích đầy đủ.")
        return

    # 1. Calculate List 0 for all periods
    processed = []
    for item in data:
        detail = json.loads(item['detail'])
        prizes_flat = []
        for field in detail: prizes_flat += field.split(",")
        
        # Default: Analyze G1 (index 1) and G2-1 (index 2)
        # In Tkinter app, user can select. Here we default to G1 & G2-1 for simplicity
        g_nums = []
        if len(prizes_flat) > 1: g_nums.extend([ch for ch in prizes_flat[1].strip() if ch.isdigit()]) # G1
        if len(prizes_flat) > 2: g_nums.extend([ch for ch in prizes_flat[2].strip() if ch.isdigit()]) # G2-1
        
        counter = Counter(g_nums)
        list0 = [str(i) for i in range(10) if counter[str(i)] == 0]
        
        current_los = []
        for lo in prizes_flat:
            lo = lo.strip()
            if len(lo)>=2 and lo[-2:].isdigit():
                current_los.append(lo[-2:])
        
        processed.append({"ky": item['turnNum'], "list0": list0, "res": current_los})

    # 2. Build Analysis Table
    rows = []
    for i in range(min(20, len(processed))):
        curr = processed[i]
        row = {
            "Kỳ": curr["ky"],
            "List 0 (Thiếu)": ",".join(curr["list0"])
        }
        
        # Prev List 0
        if i - 1 >= 0: row["Kỳ-1"] = ",".join(processed[i-1]["list0"])
        else: row["Kỳ-1"] = ""
            
        # Prev 2 List 0
        if i - 2 >= 0: row["Kỳ-2"] = ",".join(processed[i-2]["list0"])
        else: row["Kỳ-2"] = ""
        
        # Sót K0 (Bridge L0_curr + L0_next - Res_curr)
        # Note: In Tkinter logic, it uses i+1 (next in list, which is PREVIOUS in time if list is sorted desc?)
        # Usually data is sorted desc (latest first). So i+1 is previous period.
        # Let's assume data is sorted Latest -> Oldest.
        
        if i + 1 < len(processed):
            l0_curr = processed[i]["list0"]
            l0_prev = processed[i+1]["list0"] # Actually previous in time
            
            # Bridge logic: Combine L0 of this period and L0 of "next" period in list (previous time)
            k0_dan = bridge_ab(l0_curr, l0_prev)
            
            # Check against current result
            missed_k0 = diff(k0_dan, curr["res"])
            row["Sót K0"] = " ".join(missed_k0)
            
            # Check K1-K7 (Future checks? Or Past checks?)
            # Tkinter logic: target_idx = i - k. If i is current, i-k is FUTURE (newer).
            # So this analyzes: "If we used the bridge from (i, i+1), did it hit in (i-1), (i-2)...?"
            
            current_dan = k0_dan
            for k in range(1, 8):
                target_idx = i - k
                if target_idx >= 0:
                    res_target = processed[target_idx]["res"]
                    current_dan = diff(current_dan, res_target)
                    row[f"Sót K{k}"] = " ".join(current_dan)
                else:
                    row[f"Sót K{k}"] = ""
        else:
            row["Sót K0"] = ""
            for k in range(1, 8): row[f"Sót K{k}"] = ""
            
        rows.append(row)
        
    st.dataframe(pd.DataFrame(rows), use_container_width=True)

def render_tab2(data):
    st.subheader("So Sánh: Thiếu Đầu -> Chạm/Tổng")
    
    processed = []
    for item in data:
        detail = json.loads(item['detail'])
        prizes_flat = []
        for field in detail: prizes_flat += field.split(",")
        
        heads = []
        for p in prizes_flat:
            p = p.strip()
            if len(p) > 0: heads.append(p[0])
            
        counter = Counter(heads)
        missing_heads = [str(i) for i in range(10) if counter[str(i)] == 0]
        
        processed.append({
            "ky": item['turnNum'],
            "missing_heads": missing_heads,
            "full_prizes": prizes_flat
        })
        
    rows = []
    for i in range(min(20, len(processed))):
        curr = processed[i]
        dan_cham_tong = generate_cham_tong(curr["missing_heads"])
        
        row = {
            "Kỳ": curr["ky"],
            "Thiếu Đầu": ",".join(curr["missing_heads"]),
            "Dàn (Chạm+Tổng)": " ".join(dan_cham_tong)
        }
        
        # Check K1-K7
        for k in range(1, 8):
            target_idx = i - k
            if target_idx >= 0:
                target_data = processed[target_idx]
                # Target: Duoi DB (default)
                db = target_data["full_prizes"][0] if target_data["full_prizes"] else ""
                target_res = db[-2:] if len(db)>=2 else ""
                
                if target_res in dan_cham_tong:
                    row[f"K{k}"] = f"TRÚNG {target_res}"
                else:
                    row[f"K{k}"] = "-"
            else:
                row[f"K{k}"] = ""
        rows.append(row)
        
    st.dataframe(pd.DataFrame(rows), use_container_width=True)

def render_tab3(data, region):
    st.subheader("Phân Tích Lô Lạ (Pattern Đặc Biệt)")
    
    max_prize_index = 9 if "Bắc" in region else 13
    
    processed = []
    for item in data:
        detail = json.loads(item['detail'])
        prizes_flat = []
        for field in detail: prizes_flat += field.split(",")
        
        special_los = []
        day_digit_counts = Counter()
        
        for idx, prize in enumerate(prizes_flat):
            if idx > max_prize_index: break
            is_special, lo = detect_special_pattern(prize)
            if is_special and lo:
                prize_digits = set([d for d in prize if d.isdigit()])
                if prize_digits:
                    special_los.append("".join(sorted(list(prize_digits))))
                    for d in prize_digits: day_digit_counts[d] += 1
                    
        list0 = sorted(list(set(special_los)))
        
        # Generate Dan Nhi Hop
        selected_digits = []
        desired = 3 # Default max digits
        
        # Priority 1: High frequency in special prizes
        if day_digit_counts:
            sorted_digits = sorted(day_digit_counts.items(), key=lambda kv: (-kv[1], kv[0]))
            for d, _ in sorted_digits:
                if len(selected_digits) < desired: selected_digits.append(d)
        
        # Priority 2: Overall frequency
        if len(selected_digits) < desired:
            all_counts = Counter()
            for p in prizes_flat:
                for ch in p.strip():
                    if ch.isdigit(): all_counts[ch] += 1
            sorted_all = sorted(all_counts.items(), key=lambda kv: (-kv[1], kv[0]))
            for d, _ in sorted_all:
                if d not in selected_digits and len(selected_digits) < desired:
                    selected_digits.append(d)
                    
        dan_nhi_hop = generate_nhi_hop(sorted(selected_digits))
        
        current_los = []
        for lo in prizes_flat:
            lo = lo.strip()
            if len(lo)>=2 and lo[-2:].isdigit(): current_los.append(lo[-2:])
            
        processed.append({
            "ky": item['turnNum'],
            "list0": list0,
            "dan": dan_nhi_hop,
            "res": current_los
        })
        
    rows = []
    for i in range(min(20, len(processed))):
        curr = processed[i]
        row = {
            "Kỳ": curr["ky"],
            "Lô Lạ": ",".join(curr["list0"]),
            "Dàn Nhị Hợp": " ".join(curr["dan"])
        }
        
        # K1-K10
        current_dan = curr["dan"][:]
        for k in range(1, 11):
            target_idx = i - k
            if target_idx >= 0:
                res_target = processed[target_idx]["res"]
                current_dan = diff(current_dan, res_target)
                if current_dan:
                    row[f"K{k}"] = " ".join(current_dan)
                else:
                    row[f"K{k}"] = "-"
            else:
                row[f"K{k}"] = ""
        rows.append(row)
        
    st.dataframe(pd.DataFrame(rows), use_container_width=True)

def render_tab4_single(data):
    st.subheader("Dự Đoán Lô Nháy & Cặp (Miền Bắc)")
    
    if len(data) < 5:
        st.warning("Cần ít nhất 5 kỳ dữ liệu.")
        return
        
    col1, col2 = st.columns([1, 3])
    with col1:
        max_distance = st.number_input("Khoảng cách vị trí tối đa", min_value=1, max_value=10, value=2)
        num_digits = st.number_input("Số chữ số dự đoán", min_value=1, max_value=10, value=5)
        
    if st.button("Phân Tích Lô Nháy"):
        with st.spinner("Đang phân tích..."):
            # 1. Analyze Top Head/Tail
            dau_freq = Counter()
            duoi_freq = Counter()
            for item in data[:3]:
                nums = get_all_numbers(item)
                for n in nums:
                    if len(n)>=2:
                        dau_freq[n[-2]] += 1
                        duoi_freq[n[-1]] += 1
            top_dau = [d for d, c in dau_freq.most_common(5)]
            top_duoi = [d for d, c in duoi_freq.most_common(5)]
            
            # 2. Analyze Pattern (Lô Nháy)
            latest_item = data[0]
            prev_item = data[1]
            
            latest_g3 = get_prize3_numbers(latest_item)
            prev_g3 = get_prize3_numbers(prev_item)
            
            # Get pairs from latest result (simplified: all pairs)
            latest_nums = get_all_numbers(latest_item)
            pairs = set()
            for n in latest_nums:
                if len(n)>=2: pairs.add(n[-2:])
            
            pair_scores = {}
            for pair in pairs:
                d1, d2 = pair[0], pair[1]
                # Find in prev G3
                valid_positions = find_digit_positions_in_g3(prev_g3, d1, d2, max_distance)
                for pattern in valid_positions:
                    preds = apply_pattern_to_current(latest_g3, pattern)
                    for p in preds:
                        score = max_distance - pattern['distance'] + 1
                        pd1, pd2 = p['digit1'], p['digit2']
                        key = tuple(sorted((pd1, pd2)))
                        pair_scores[key] = pair_scores.get(key, 0) + score
            
            if pair_scores:
                # Calculate digit scores
                digit_scores = {}
                for (d1, d2), score in pair_scores.items():
                    digit_scores[d1] = digit_scores.get(d1, 0) + score
                    digit_scores[d2] = digit_scores.get(d2, 0) + score
                
                top_digits = [d for d, s in sorted(digit_scores.items(), key=lambda x: -x[1])[:num_digits]]
                top_digits = sorted(top_digits)
                
                # Display Results
                st.success(f"Chữ số dự đoán: {' - '.join(top_digits)}")
                
                c1, c2 = st.columns(2)
                with c1:
                    st.info(f"Top Đầu: {' - '.join(top_dau)}")
                    match_head = [d for d in top_digits if d in top_dau]
                    st.write(f"Trùng Đầu: {', '.join(match_head) if match_head else 'Không'}")
                with c2:
                    st.info(f"Top Đuôi: {' - '.join(top_duoi)}")
                    match_tail = [d for d in top_digits if d in top_duoi]
                    st.write(f"Trùng Đuôi: {', '.join(match_tail) if match_tail else 'Không'}")
            else:
                st.warning("Không tìm thấy mẫu phù hợp trong kỳ này.")

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
        try:
            default_day_idx = days_list.index(current_day)
        except:
            default_day_idx = 0
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

if __name__ == "__main__":
    main()
