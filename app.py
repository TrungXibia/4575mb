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
import concurrent.futures

# =============================================================================
# CẤU HÌNH & DỮ LIỆU
# =============================================================================

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Referer": "https://www.kqxs88.live/",
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "vi-VN,vi;q=0.9,en-US;q=0.8,en;q=0.7",
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
        # Add cache busting
        ts = int(datetime.now().timestamp() * 1000)
        if "?" in url:
            final_url = f"{url}&_t={ts}"
        else:
            final_url = f"{url}?_t={ts}"
            
        resp = SESSION.get(final_url, headers=HEADERS, timeout=timeout)
        resp.raise_for_status()
        data = resp.json().get("t", {})
        issue_list = data.get("issueList", [])
        
        # Lấy thời gian từ kỳ mới nhất
        latest_time = ""
        if issue_list:
            latest_time = issue_list[0].get('openTime', '')
            
        return issue_list, latest_time
    except Exception as e:
        st.error(f"Lỗi tải dữ liệu: {str(e)}")
        print(f"Error fetching {url}: {e}")
        return [], ""

def get_current_day_vietnamese():
    return DAYS_OF_WEEK[datetime.now().weekday()]

def load_data(station_name, timeout=10):
    api_key = station_name
    if "Miền Bắc" in station_name and "45s" not in station_name and "75s" not in station_name:
        api_key = "Miền Bắc"
    
    url = DAI_API.get(api_key)
    if url:
        return http_get_issue_list(url, timeout=timeout)
    return [], ""

# =============================================================================
# LOGIC HELPER FUNCTIONS (FOR TAB 1-3)
# =============================================================================

class DataParser:
    """Utility class for parsing lottery data - eliminates duplicate code"""
    
    @staticmethod
    def get_prizes_flat(item: dict) -> list[str]:
        """Extract all prizes from item detail"""
        try:
            detail = json.loads(item['detail'])
            prizes_flat = []
            for field in detail:
                prizes_flat += field.split(",")
            return prizes_flat
        except (json.JSONDecodeError, KeyError, TypeError):
            return []
    
    @staticmethod
    def get_two_digit_numbers(prizes_flat: list[str]) -> list[str]:
        """Extract all 2-digit numbers from prizes"""
        try:
            results = []
            for prize in prizes_flat:
                prize = prize.strip()
                if len(prize) >= 2 and prize[-2:].isdigit():
                    results.append(prize[-2:])
            return results
        except Exception:
            return []
    
    @staticmethod
    def get_list0(prizes_flat: list[str]) -> list[str]:
        """Calculate List 0 (missing digits 0-9)"""
        try:
            g_nums = []
            for prize in prizes_flat:
                g_nums.extend([ch for ch in prize.strip() if ch.isdigit()])
            counter = Counter(g_nums)
            counts = [counter.get(str(d), 0) for d in range(10)]
            return [str(i) for i, v in enumerate(counts) if v == 0]
        except Exception:
            return []
    
    @staticmethod
    def get_missing_heads(prizes_flat: list[str]) -> list[str]:
        """Calculate missing head digits (first digit of prizes)"""
        try:
            heads = []
            for p in prizes_flat:
                p = p.strip()
                if len(p) >= 2:
                    heads.append(p[-2]) # Numerical head is tens digit
                elif len(p) == 1:
                    heads.append('0')
            
            counter = Counter(heads)
            counts = [counter.get(str(d), 0) for d in range(10)]
            return [str(i) for i, v in enumerate(counts) if v == 0]
        except Exception:
            return []
    
    @staticmethod
    def bridge_ab(list1: list[str], list2: list[str]) -> list[str]:
        """Create all combinations of two lists (AB and BA)"""
        try:
            result_set = set()
            for a in list1:
                for b in list2:
                    result_set.add(a + b)
                    result_set.add(b + a)
            return sorted(list(result_set))
        except Exception:
            return []

def generate_cham_tong(list_missing):
    """Tạo dàn Chạm + Tổng từ list số thiếu"""
    result_set = set()
    for d_str in list_missing:
        try:
            d = str(d_str)
            # Chạm
            for i in range(100):
                s = f"{i:02d}"
                if d in s:
                    result_set.add(s)
            # Tổng
            for i in range(100):
                s = f"{i:02d}"
                digit_sum = (int(s[0]) + int(s[1])) % 10
                if digit_sum == int(d):
                    result_set.add(s)
        except:
            continue
    return sorted(list(result_set))

def detect_consecutive_repeat(prize_str, min_count=3):
    """Kiểm tra số có chữ số lặp liên tiếp (≥3 số)"""
    prize_str = prize_str.strip()
    if len(prize_str) < min_count:
        return False, None
    for i in range(len(prize_str) - min_count + 1):
        first_digit = prize_str[i]
        count = 1
        for j in range(i + 1, len(prize_str)):
            if prize_str[j] == first_digit: count += 1
            else: break
        if count >= min_count:
            if len(prize_str) >= 2: return True, prize_str[-2:]
    return False, None

def detect_lap(prize_str):
    """Kiểm tra số có chữ số lặp lại (không cần liên tiếp)"""
    prize_str = prize_str.strip()
    if len(prize_str) < 2: return False, None
    digit_count = {}
    for digit in prize_str:
        if digit.isdigit():
            digit_count[digit] = digit_count.get(digit, 0) + 1
    for count in digit_count.values():
        if count >= 2:
            if len(prize_str) >= 2: return True, prize_str[-2:]
    return False, None

def detect_ganh(prize_str):
    """Kiểm tra số đối xứng (gánh/đảo)"""
    prize_str = prize_str.strip()
    if len(prize_str) < 2: return False, None
    if prize_str == prize_str[::-1]:
        if len(prize_str) >= 2: return True, prize_str[-2:]
    return False, None

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

def detect_special_pattern(prize_str):
    """Kiểm tra giải có <= 3 chữ số duy nhất"""
    prize_str = prize_str.strip()
    if not prize_str or not prize_str.isdigit():
        return False, None
    unique_digits = set(prize_str)
    num_unique = len(unique_digits)
    if num_unique <= 3:
        return True, prize_str[-2:]
    else:
        return False, None

def generate_nhi_hop(list_digits):
    """Tạo dàn nhị hợp từ danh sách các chữ số"""
    result_set = set()
    for d1 in list_digits:
        for d2 in list_digits:
            result_set.add(f"{d1}{d2}")
    return sorted(list(result_set))

def get_selected_pairs(current_numbers, use_nhay, use_cap, use_dau, use_duoi):
    """Lọc các cặp số dựa trên tùy chọn (Lô Nháy, Cặp, Đầu/Đuôi Nhiều)"""
    all_pairs = []
    for num in current_numbers:
        if len(num) >= 2:
            last2 = num[-2:]
            if last2.isdigit() and len(last2) == 2:
                all_pairs.append(last2)
    
    pair_counts = Counter(all_pairs)
    selected_pairs = set()
    if use_nhay:
        for pair, count in pair_counts.items():
            if count >= 2: selected_pairs.add(pair)
    if use_cap:
        for pair in pair_counts.keys():
            rev = pair[1] + pair[0]
            if rev in pair_counts and pair != rev: selected_pairs.add(pair)
    if use_dau:
        head_counts = Counter([p[0] for p in all_pairs])
        for head, count in head_counts.items():
            if count >= 3:
                for p in all_pairs:
                    if p[0] == head: selected_pairs.add(p)
    if use_duoi:
        tail_counts = Counter([p[1] for p in all_pairs])
        for tail, count in tail_counts.items():
            if count >= 3:
                for p in all_pairs:
                    if p[1] == tail: selected_pairs.add(p)
    return selected_pairs

# =============================================================================
# TAB 4 HELPER FUNCTIONS (NEWLY ADDED)
# =============================================================================

def get_all_numbers(item):
    """Lấy tất cả số từ một kỳ quay"""
    detail = json.loads(item['detail'])
    nums = []
    for field in detail:
        nums.extend([n.strip() for n in field.split(',') if n.strip()])
    return nums

def get_prize3_numbers(item):
    """Lấy các số giải 3"""
    detail = json.loads(item['detail'])
    prizes_flat = []
    for field in detail:
        prizes_flat.extend(field.split(','))
    # G3 indices: 4-9 (G3-1 through G3-6)
    g3_nums = []
    for idx in range(4, 10):
        if idx < len(prizes_flat):
            g3_nums.append(prizes_flat[idx].strip())
    return g3_nums

def find_digit_positions_in_g3(g3_nums, digit1, digit2, max_distance):
    """Tìm vị trí 2 chữ số trong G3"""
    results = []
    for num_str in g3_nums:
        num_str = num_str.strip()
        pos1 = [i for i, ch in enumerate(num_str) if ch == digit1]
        pos2 = [i for i, ch in enumerate(num_str) if ch == digit2]
        
        for p1 in pos1:
            for p2 in pos2:
                if p1 != p2:
                    dist = abs(p1 - p2)
                    if dist <= max_distance:
                        results.append({
                            'digit1': digit1,
                            'digit2': digit2,
                            'pos1': p1,
                            'pos2': p2,
                            'distance': dist
                        })
    return results

def apply_pattern_to_current(g3_nums, pattern):
    """Áp dụng pattern vào G3 hiện tại"""
    results = []
    for num_str in g3_nums:
        num_str = num_str.strip()
        if len(num_str) > max(pattern['pos1'], pattern['pos2']):
            d1 = num_str[pattern['pos1']]
            d2 = num_str[pattern['pos2']]
            if d1.isdigit() and d2.isdigit():
                results.append({'digit1': d1, 'digit2': d2})
    return results

def calculate_tab4_predictions(data):
    """Calculate Tab 4 style predictions for a single station"""
    if not data or len(data) < 2:
        return {
            "digits": "Không đủ dữ liệu",
            "top_dau": "",
            "top_duoi": "",
            "match_head": "",
            "match_tail": ""
        }
    
    predictions = {}
    
    # 1. Period indices (0=latest, 1=previous)
    period_data = []
    for i in range(min(2, len(data))):
        item = data[i]
        prizes_flat = DataParser.get_prizes_flat(item)
        period_data.append(prizes_flat)
    
    # Analyze all positions across 2 periods
    position_digits = {}  # position -> list of digits
    for period_idx, prizes in enumerate(period_data):
        for prize_idx, prize in enumerate(prizes):
            prize = prize.strip()
            for pos_idx, digit in enumerate(prize):
                if digit.isdigit():
                    key = (prize_idx, pos_idx)
                    if key not in position_digits:
                        position_digits[key] = []
                    position_digits[key].append(digit)
    
    # Find positions with same digit in both periods
    matching_digits = set()
    for key, digits_list in position_digits.items():
        if len(digits_list) >= 2:
            digit_counter = Counter(digits_list)
            for digit, count in digit_counter.items():
                if count >= 2:
                    matching_digits.add(digit)
    
    # If we found matching digits, use those. Otherwise, use most frequent
    if matching_digits:
        predicted_digits = sorted(list(matching_digits))[:5]
    else:
        all_digits = []
        for prizes in period_data:
            for prize in prizes:
                for ch in prize.strip():
                    if ch.isdigit():
                        all_digits.append(ch)
        digit_freq = Counter(all_digits)
        predicted_digits = [d for d, c in digit_freq.most_common(5)]
    
    predictions["digits"] = ",".join(predicted_digits)
    
    # 2. Calculate Top Đầu/Đuôi from last 3 periods
    dau_freq = Counter()
    duoi_freq = Counter()
    periods_for_top = min(len(data), 3)
    for item in data[:periods_for_top]:
        pf = DataParser.get_prizes_flat(item)
        for num in pf:
            num = num.strip()
            if len(num) >= 2 and num[-2:].isdigit():
                last2 = num[-2:]
                dau_freq[last2[0]] += 1
                duoi_freq[last2[1]] += 1
    
    top_dau_list = sorted(dau_freq.items(), key=lambda x: -x[1])[:5]
    top_duoi_list = sorted(duoi_freq.items(), key=lambda x: -x[1])[:5]
    
    predictions["top_dau"] = " - ".join([f"{d}" for d, c in top_dau_list])
    predictions["top_duoi"] = " - ".join([f"{d}" for d, c in top_duoi_list])
    
    # 3. Check matches
    top_dau_set = {d for d, c in top_dau_list}
    top_duoi_set = {d for d, c in top_duoi_list}
    match_head = [d for d in predicted_digits if d in top_dau_set]
    match_tail = [d for d in predicted_digits if d in top_duoi_set]
    
    predictions["match_head"] = ",".join(match_head) if match_head else "-"
    predictions["match_tail"] = ",".join(match_tail) if match_tail else "-"
    
    return predictions

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

# Tab 3 states
if "tab3_use_special" not in st.session_state: st.session_state.tab3_use_special = True
if "tab3_use_consecutive" not in st.session_state: st.session_state.tab3_use_consecutive = False
if "tab3_use_lap" not in st.session_state: st.session_state.tab3_use_lap = False
if "tab3_use_ganh" not in st.session_state: st.session_state.tab3_use_ganh = False
if "tab3_keep_dup" not in st.session_state: st.session_state.tab3_keep_dup = False
if "tab3_nhi_hop_mode" not in st.session_state: st.session_state.tab3_nhi_hop_mode = "Mặc định"
if "tab3_filter" not in st.session_state: st.session_state.tab3_filter = ""

# Tab 4 states
if "tab4_use_nhay" not in st.session_state: st.session_state.tab4_use_nhay = True
if "tab4_use_cap" not in st.session_state: st.session_state.tab4_use_cap = True
if "tab4_use_dau" not in st.session_state: st.session_state.tab4_use_dau = True
if "tab4_use_duoi" not in st.session_state: st.session_state.tab4_use_duoi = True

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
# TABS LOGIC (UPDATED TO 4 TABS)
# =============================================================================

tab1, tab2, tab3, tab4 = st.tabs(["📊 CẦU LIST 0", "🎯 THIẾU ĐẦU", "🔮 LÔ LẠ", "🎲 DỰ ĐOÁN"])

# -----------------------------------------------------------------------------
# TAB 1: CẦU LIST 0
# -----------------------------------------------------------------------------
with tab1:
    # 🔮 TOP PREDICTION BANNER (Sync with Tab 4)
    if st.session_state.raw_data:
        pred = calculate_tab4_predictions(st.session_state.raw_data)
        st.markdown(f"""
        <div style="background-color: #1e1e1e; border-left: 5px solid #ff4b4b; padding: 12px; border-radius: 5px; margin-bottom: 15px; border: 1px solid #333;">
            <p style="margin-bottom: 8px;"><b style="color: #ff4b4b; font-size: 16px;">🔮 TOP DỰ ĐOÁN (Đã đồng bộ)</b></p>
            <div style="display: flex; flex-wrap: wrap; gap: 25px;">
                <span><b style="color: #ccc;">Chữ số:</b> <span style="color: #ffffff; font-size: 15px; font-weight: bold;">{pred['digits'] or '...'}</span></span>
                <span><b style="color: #ff4b4b;">→ Trùng đầu:</b> <span style="color: #ffffff;">{pred['match_head']}</span></span>
                <span><b style="color: #ff4b4b;">| Trùng đuôi:</b> <span style="color: #ffffff;">{pred['match_tail']}</span></span>
                <span><b style="color: #ccc;">Top Đầu:</b> <span style="color: #ffc107;">{pred['top_dau']}</span></span>
                <span><b style="color: #ccc;">Top Đuôi:</b> <span style="color: #ffc107;">{pred['top_duoi']}</span></span>
            </div>
        </div>
        """, unsafe_allow_html=True)

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
                prizes_flat = DataParser.get_prizes_flat(item)
                row = [item['turnNum']]
                for idx in display_indices:
                    row.append(prizes_flat[idx] if idx < len(prizes_flat) else "")
                rows_res.append(row)
            
            df_res = pd.DataFrame(rows_res, columns=headers)
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
                prizes_flat = DataParser.get_prizes_flat(item)
                
                g_nums = []
                for idx in st.session_state.selected_giai:
                    if idx < len(prizes_flat):
                        g_nums.extend([ch for ch in prizes_flat[idx].strip() if ch.isdigit()])
                counter = Counter(g_nums)
                list0 = [str(i) for i, v in enumerate([counter.get(str(d), 0) for d in range(10)]) if v == 0]
                
                res_los = DataParser.get_two_digit_numbers(prizes_flat)
                processed.append({"ky": item['turnNum'], "list0": list0, "res": res_los})

            def diff(src, target): return sorted(list(set(src) - set(target)))

            rows_anal = []
            for i in range(len(processed)):
                curr = processed[i]
                row = [curr["ky"], ",".join(curr["list0"])]
                
                # K0 (N1-N0 bridge)
                if i+1 < len(processed):
                    dan = DataParser.bridge_ab(processed[i+1]["list0"], curr["list0"])
                    k0 = diff(dan, curr["res"])
                    row.append(" ".join(k0))
                else: row.append("")
                
                # K1-K7
                if i>0 and i+1 < len(processed):
                    dan = DataParser.bridge_ab(processed[i+1]["list0"], processed[i]["list0"])
                    for k in range(7):
                        t_idx = i - k
                        if t_idx < 0: row.append("")
                        else: row.append(" ".join(diff(dan, processed[t_idx]["res"])))
                else: row.extend([""]*7)
                rows_anal.append(row)
            
            df_anal = pd.DataFrame(rows_anal, columns=["Kỳ", "Thiếu", "Sót K0", "Sót K1"] + [f"Sót K{k}" for k in range(2, 8)])
            
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
                prizes_flat = DataParser.get_prizes_flat(item)
                db = prizes_flat[0] if len(prizes_flat)>0 else ""
                g1 = prizes_flat[1] if len(prizes_flat)>1 else ""
                rows_simple.append([item['turnNum'], db, g1])
            
            df_simple = pd.DataFrame(rows_simple, columns=["Kỳ", "ĐB", "G1"])
            
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
                prizes_flat = DataParser.get_prizes_flat(item)
                missing = DataParser.get_missing_heads(prizes_flat)
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
            
            t2_config = {
                "Kỳ": st.column_config.TextColumn("Kỳ", width=30),
                "Thiếu Đầu": st.column_config.TextColumn("Thiếu Đầu", width=40),
                "Dàn K0": st.column_config.TextColumn("Dàn K0", width="medium"),
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

# -----------------------------------------------------------------------------
# TAB 3: LÔ LẠ & PATTERN
# -----------------------------------------------------------------------------
with tab3:
    st.markdown("##### 🔮 PHÂN TÍCH LÔ LẠ (Tùy chọn đa dạng)")
    
    with st.expander("⚙️ CẤU HÌNH PHÂN TÍCH LÔ LẠ", expanded=True):
        c1, c2, c3, c4 = st.columns([2, 2, 3, 3])
        with c1:
            st.session_state.tab3_use_special = st.checkbox("≤3 CS duy nhất", st.session_state.tab3_use_special)
            st.session_state.tab3_use_consecutive = st.checkbox("Lặp l.tiếp (≥3)", st.session_state.tab3_use_consecutive)
        with c2:
            st.session_state.tab3_use_lap = st.checkbox("Lặp", st.session_state.tab3_use_lap)
            st.session_state.tab3_use_ganh = st.checkbox("Gánh/Đảo", st.session_state.tab3_use_ganh)
        with c3:
            st.session_state.tab3_keep_dup = st.checkbox("Giữ số trùng", st.session_state.tab3_keep_dup)
            st.session_state.tab3_nhi_hop_mode = st.radio("Chế độ Nhị hợp:", ["Mặc định", "Chỉ 1 giải", "Cả hai"], index=["Mặc định", "Chỉ 1 giải", "Cả hai"].index(st.session_state.tab3_nhi_hop_mode), horizontal=True)
        with c4:
            st.session_state.tab3_filter = st.text_input("Lọc số (vd: 01,02)", st.session_state.tab3_filter)
            filter_nums = [p.strip() for p in st.session_state.tab3_filter.replace(",", " ").split() if p.strip().isdigit() and len(p.strip())==2]

    if not st.session_state.raw_data:
        st.info("Chưa có dữ liệu.")
    else:
        t3_left, t3_right = st.columns([2, 7])

        with t3_left:
            rows_res = []
            for item in st.session_state.raw_data:
                prizes_flat = DataParser.get_prizes_flat(item)
                db = prizes_flat[0] if len(prizes_flat) > 0 else ""
                current_los = DataParser.get_two_digit_numbers(prizes_flat)
                lo_ra = " ".join(sorted(set(current_los)))
                rows_res.append([item['turnNum'], db, lo_ra])
            
            df_t3_res = pd.DataFrame(rows_res, columns=["Kỳ", "ĐB", "Lô Ra"])
            st.dataframe(
                df_t3_res,
                height=700,
                use_container_width=True,
                hide_index=True,
                column_config={
                    "Kỳ": st.column_config.TextColumn("Kỳ", width=30),
                    "ĐB": st.column_config.TextColumn("ĐB", width=30),
                    "Lô Ra": st.column_config.TextColumn("Lô Ra", width=50)
                }
            )

        with t3_right:
            max_prize_index = 9 if "Bắc" in region else 13
            nhi_hop_mode_val = {"Mặc định": 0, "Chỉ 1 giải": 1, "Cả hai": 2}[st.session_state.tab3_nhi_hop_mode]
            
            processed = []
            for item in st.session_state.raw_data:
                prizes_flat = DataParser.get_prizes_flat(item)
                special_los = []
                day_digit_counts = Counter()
                prize_occurrence_counts = Counter()
                
                for idx, prize in enumerate(prizes_flat):
                    if idx > max_prize_index: break
                    prize = prize.strip()
                    found = False
                    if st.session_state.tab3_use_consecutive:
                        ok, _ = detect_consecutive_repeat(prize)
                        if ok: found = True
                    if not found and st.session_state.tab3_use_lap:
                        ok, _ = detect_lap(prize)
                        if ok: found = True
                    if not found and st.session_state.tab3_use_ganh:
                        ok, _ = detect_ganh(prize)
                        if ok: found = True
                    if not found and st.session_state.tab3_use_special:
                        ok, _ = detect_special_pattern(prize)
                        if ok: found = True
                    
                    if found:
                        digits = [d for d in prize if d.isdigit()]
                        if st.session_state.tab3_keep_dup:
                            special_los.append("".join(sorted(digits)))
                        else:
                            special_los.append("".join(sorted(list(set(digits)))))
                        for d in set(digits): prize_occurrence_counts[d] += 1
                        for d in digits: day_digit_counts[d] += 1
                
                if st.session_state.tab3_keep_dup: list0 = sorted(special_los)
                else: list0 = sorted(list(set(special_los)))
                
                dan_nhi_hop = []
                top_str = ""
                if list0:
                    all_digits = set("".join(list0))
                    # Top logic
                    if nhi_hop_mode_val in (1, 2) and len(list0) == 1:
                        candidates = [d for d in all_digits if day_digit_counts[d] >= 1]
                    else:
                        candidates = [d for d in all_digits if day_digit_counts[d] >= 2]
                    
                    if candidates:
                        keyed = {d: (prize_occurrence_counts[d], day_digit_counts[d]) for d in candidates}
                        unique_levels = sorted(list(set(keyed.values())), reverse=True)
                        top_levels = unique_levels[:2]
                        final_top = [d for d in candidates if keyed[d] in top_levels]
                        final_top.sort(key=lambda d: (-keyed[d][0], -keyed[d][1], d))
                        top_str = " - ".join(final_top)
                        
                        # Generate dan nhi hop based on mode
                        sel_digits = []
                        if not st.session_state.tab3_use_consecutive and not st.session_state.tab3_use_lap and not st.session_state.tab3_use_ganh:
                            if len(list0) >= 2:
                                sel_digits = [d for d in all_digits if day_digit_counts[d] >= 2]
                            elif len(list0) == 1 and nhi_hop_mode_val in (1, 2):
                                sel_digits = sorted(list(all_digits))
                        else:
                            if st.session_state.tab3_use_lap and len(all_digits) > 3:
                                sel_digits = [d for d in all_digits if day_digit_counts[d] >= 2]
                            else:
                                sel_digits = sorted(list(all_digits))
                        
                        if sel_digits: dan_nhi_hop = generate_nhi_hop(sorted(sel_digits))

                current_los = DataParser.get_two_digit_numbers(prizes_flat)
                processed.append({"ky": item['turnNum'], "list0": list0, "dan": dan_nhi_hop, "top": top_str, "res": current_los})

            def diff(src, target): return sorted(list(set(src) - set(target)))

            rows_anal = []
            for i in range(len(processed)):
                curr = processed[i]
                is_multi = len(curr["list0"]) > 1
                is_single = len(curr["list0"]) == 1
                
                should_show = False
                if nhi_hop_mode_val == 1: should_show = is_single
                elif nhi_hop_mode_val == 2: should_show = is_single or is_multi
                else: should_show = is_multi
                
                if not should_show:
                    rows_anal.append([""] * 13)
                    continue

                row = [",".join(curr["list0"]), " ".join(curr["dan"][:15]) + ("..." if len(curr["dan"])>15 else ""), curr["top"]]
                
                if curr["dan"]:
                    current_dan = curr["dan"][:]
                    for k in range(1, 11):
                        target_idx = i - k
                        if target_idx < 0: row.append("")
                        else:
                            row.append(" ".join(diff(current_dan, processed[target_idx]["res"]) if diff(current_dan, processed[target_idx]["res"]) else "-"))
                            current_dan = diff(current_dan, processed[target_idx]["res"])
                else: row.extend([""] * 10)
                rows_anal.append(row)
            
            cols_anal = ["Lô Lạ", "Dàn Nhị Hợp", "Top"] + [f"K{k}" for k in range(1, 11)]
            df_anal = pd.DataFrame(rows_anal, columns=cols_anal)
            
            t3_config = {
                "Lô Lạ": st.column_config.TextColumn("Lô Lạ", width=50),
                "Dàn Nhị Hợp": st.column_config.TextColumn("Dàn Nhị Hợp", width="medium"),
                "Top": st.column_config.TextColumn("Top", width=50),
            }
            for k in range(1, 11): t3_config[f"K{k}"] = st.column_config.TextColumn(f"K{k}", width=40)

            k_colors = ["#F1F8E9", "#DCEDC8", "#C5E1A5", "#AED581", "#9CCC65", "#8BC34A", "#7CB342", "#689F38", "#558B2F", "#33691E"]

            def highlight_t3(s):
                styles = []
                for v in s:
                    if not v or v == "": styles.append('')
                    elif s.name == "Lô Lạ": styles.append('background-color: #ffebee; color: #c0392b')
                    elif s.name == "Dàn Nhị Hợp": styles.append('background-color: #e3f2fd; color: #1565c0')
                    elif s.name == "Top": styles.append('background-color: #fff3e0; color: #e65100')
                    elif s.name.startswith("K"):
                        try:
                            idx = int(s.name[1:]) - 1
                            if v and v.strip() not in ("", "-"): styles.append(f'background-color: {k_colors[idx]}; color: black')
                            else: styles.append('')
                        except: styles.append('')
                    else: styles.append('')
                    
                    # Filter highlighting
                    if filter_nums and styles[-1] != '' and any(n in str(v) for n in filter_nums):
                        styles[-1] = 'background-color: #FFF3CD; color: #000000; font-weight: bold'
                return styles

            st.dataframe(df_anal.style.apply(highlight_t3), height=700, use_container_width=True, hide_index=True, column_config=t3_config)

# -----------------------------------------------------------------------------
# TAB 4: DỰ ĐOÁN ĐA NĂNG (NEWLY ADDED)
# -----------------------------------------------------------------------------
with tab4:
    # Determine mode based on region
    is_multi_station_mode = (region == "Miền Nam" or region == "Miền Trung")
    
    if is_multi_station_mode:
        # Multi-station mode
        st.markdown(f"##### 📊 KẾT QUẢ TỔNG HỢP CÁC ĐÀI ({selected_day})")
        
        if st.button("🔄 Phân Tích Lại"):
            st.rerun()

        # AUTO ANALYSIS (No button required)
        with st.spinner(f"Đang tải dữ liệu {len(stations)} đài..."):
            # Sequential Fetching (More stable for Streamlit)
            multi_data = {}
            for stn in stations:
                try:
                    # Use shorter timeout (5s)
                    data, _ = load_data(stn, timeout=5)
                    if data:
                        multi_data[stn] = data
                except Exception as e:
                    st.error(f"Lỗi tải {stn}: {e}")
            
            # Calculate Predictions
            results = []
            for stn in stations:
                if stn in multi_data:
                    pred = calculate_tab4_predictions(multi_data[stn])
                    results.append({
                        "Đài": stn,
                        "Chữ số dự đoán": pred['digits'],
                        "Top Đầu": pred['top_dau'],
                        "Top Đuôi": pred['top_duoi'],
                        "Trùng Đầu": pred['match_head'],
                        "Trùng Đuôi": pred['match_tail']
                    })
                else:
                    results.append({"Đài": stn, "Chữ số dự đoán": "Lỗi/Không có DL"})
            
            # Display Transposed DataFrame (Stations as Columns)
            if results:
                df = pd.DataFrame(results).set_index("Đài").T
                st.dataframe(df, use_container_width=True)
    else:
        # Single station mode (Miền Bắc)
        st.markdown("##### 🎲 DỰ ĐOÁN LÔ NHÁY & CẶP (Miền Bắc)")
        
        if len(st.session_state.raw_data) < 5:
            st.warning("Cần ít nhất 5 kỳ dữ liệu.")
        else:
            with st.expander("⚙️ PHƯƠNG PHÁP LỌC & CẤU HÌNH", expanded=True):
                c1, c2, c3, c4, c5, c6 = st.columns([2, 1, 1, 1, 1, 1])
                with c1: max_distance = st.number_input("Vị trí tối đa", min_value=1, max_value=10, value=2)
                with c2: num_digits = st.number_input("Số CS dự đoán", min_value=1, max_value=10, value=5)
                with c3: st.session_state.tab4_use_nhay = st.checkbox("Lô Nháy", st.session_state.tab4_use_nhay)
                with c4: st.session_state.tab4_use_cap = st.checkbox("Lô Cặp", st.session_state.tab4_use_cap)
                with c5: st.session_state.tab4_use_dau = st.checkbox("Đầu Nhiều", st.session_state.tab4_use_dau)
                with c6: st.session_state.tab4_use_duoi = st.checkbox("Đuôi Nhiều", st.session_state.tab4_use_duoi)

            # Split layout: Left (Analysis) - Right (Results & Stats)
            t4_col_left, t4_col_right = st.columns([1.5, 1])
            
            # --- LEFT COLUMN: PREDICTION ---
            with t4_col_left:
                if st.button("🔄 Phân Tích Lại"):
                    st.rerun()

                # AUTO ANALYSIS (No button required)
                data = st.session_state.raw_data
                
                # 1. Analyze Top Head/Tail
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
                
                # 2. Analyze Pattern
                latest_item = data[0]
                prev_item = data[1]
                
                latest_g3 = get_prize3_numbers(latest_item)
                prev_g3 = get_prize3_numbers(prev_item)
                
                # Get selected pairs from latest result
                latest_nums = get_all_numbers(latest_item)
                pairs = get_selected_pairs(
                    latest_nums, 
                    st.session_state.tab4_use_nhay, 
                    st.session_state.tab4_use_cap,
                    st.session_state.tab4_use_dau,
                    st.session_state.tab4_use_duoi
                )
                
                pair_scores = {}
                for pair in pairs:
                    if len(pair) >= 2:
                        d1, d2 = pair[0], pair[1]
                        valid_positions = find_digit_positions_in_g3(prev_g3, d1, d2, max_distance)
                        for pattern in valid_positions:
                            preds = apply_pattern_to_current(latest_g3, pattern)
                            for p in preds:
                                score = max_distance - pattern['distance'] + 1
                                pd1, pd2 = p['digit1'], p['digit2']
                                key = tuple(sorted((pd1, pd2)))
                                pair_scores[key] = pair_scores.get(key, 0) + score
                
                if pair_scores:
                    digit_scores = {}
                    for (d1, d2), score in pair_scores.items():
                        digit_scores[d1] = digit_scores.get(d1, 0) + score
                        digit_scores[d2] = digit_scores.get(d2, 0) + score
                    
                    top_digits = [d for d, s in sorted(digit_scores.items(), key=lambda x: -x[1])[:num_digits]]
                    top_digits = sorted(top_digits)
                    
                    st.success(f"**Chữ số dự đoán:** {' - '.join(top_digits)}")
                    
                    # Detailed Prediction Info
                    st.markdown("###### CHI TIẾT DỰ ĐOÁN")
                    st.info(f"**Top Đầu (3 kỳ):** {' - '.join(top_dau)}")
                    st.info(f"**Top Đuôi (3 kỳ):** {' - '.join(top_duoi)}")
                    
                    match_head = [d for d in top_digits if d in top_dau]
                    match_tail = [d for d in top_digits if d in top_duoi]
                    
                    mc1, mc2 = st.columns(2)
                    with mc1:
                        if match_head: st.write(f"✅ **Trùng Đầu:** {', '.join(match_head)}")
                        else: st.write("❌ **Trùng Đầu:** Không")
                    with mc2:
                        if match_tail: st.write(f"✅ **Trùng Đuôi:** {', '.join(match_tail)}")
                        else: st.write("❌ **Trùng Đuôi:** Không")
                else:
                    st.warning("Không tìm thấy mẫu phù hợp trong kỳ này.")

            # --- RIGHT COLUMN: RESULTS & STATS ---
            with t4_col_right:
                st.markdown("##### 📋 KẾT QUẢ & THỐNG KÊ")
                
                def format_prizes(item):
                    prizes_flat = DataParser.get_prizes_flat(item)
                    if not prizes_flat: return "<div>Không có dữ liệu</div>"
                    
                    # Mapping for MB
                    labels = ["ĐB", "G1", "G2", "G3", "G4", "G5", "G6", "G7"]
                    # Indices for MB: ĐB(0), G1(1), G2(2-3), G3(4-9), G4(10-13), G5(14-19), G6(20-22), G7(23-26)
                    ranges = [(0,1), (1,2), (2,4), (4,10), (10,14), (14,20), (20,23), (23,27)]
                    
                    html = f"<div style='font-size:12px; border:1px solid #555; padding:8px; border-radius:5px; margin-bottom:8px; background-color: #1e1e1e;'>"
                    html += f"<div style='color:#ff4b4b; font-weight:bold; border-bottom:1px solid #444; margin-bottom:5px; padding-bottom:3px;'>📅 {item.get('openTime','')}</div>"
                    
                    for label, (start, end) in zip(labels, ranges):
                        if start < len(prizes_flat):
                            vals = prizes_flat[start:end]
                            vals_str = " - ".join([v.strip() for v in vals if v.strip()])
                            html += f"<div style='display:flex; justify-content:space-between; margin-bottom:2px;'><span style='color:#aaa'><b>{label}:</b></span> <span style='color:#ffffff; font-family: monospace;'>{vals_str}</span></div>"
                    html += "</div>"
                    return html

                # Latest Result
                if len(data) > 0:
                    st.markdown("**KỲ MỚI NHẤT:**")
                    st.markdown(format_prizes(data[0]), unsafe_allow_html=True)
                
                # Previous Result
                if len(data) > 1:
                    st.markdown("**KỲ TRƯỚC ĐÓ:**")
                    st.markdown(format_prizes(data[1]), unsafe_allow_html=True)
                
                # Stats Table (Head/Tail)
                st.markdown("**THỐNG KÊ ĐẦU/ĐUÔI (3 kỳ):**")
                stats_rows = []
                for d in range(10):
                    d_str = str(d)
                    stats_rows.append({
                        "Số": d_str,
                        "Đầu": dau_freq.get(d_str, 0),
                        "Đuôi": duoi_freq.get(d_str, 0)
                    })
                st.dataframe(pd.DataFrame(stats_rows).set_index("Số").T, use_container_width=True)
