# -*- coding: utf-8 -*-
"""
Ứng dụng Phân Tích Xổ Số - Streamlit Version
Chuyển đổi từ Tkinter sang Streamlit
"""

import streamlit as st
import requests
import json
import itertools
from collections import Counter
from datetime import datetime
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# ─────────────────────────────────────────────
# CẤU HÌNH & DỮ LIỆU
# ─────────────────────────────────────────────

HEADERS = {
    "User-Agent": "Mozilla/5.0",
    "Referer": "https://www.kqxs88.live/",
}

_API_BASE = "https://www.kqxs88.live/api/front/open/lottery/history/list/game?limitNum=60&gameCode="
_GAME_CODES = {
    "Miền Bắc": "miba", "VN Miền Bắc 75s": "vnmbmg", "Miền Bắc 75s": "mbmg",
    "An Giang": "angi", "Bạc Liêu": "bali", "Bến Tre": "betr",
    "Bình Dương": "bidu", "Bình Thuận": "bith", "Bình Phước": "biph",
    "Cà Mau": "cama", "Cần Thơ": "cath", "Đà Lạt": "dalat",
    "Đồng Nai": "dona", "Đồng Tháp": "doth", "Hậu Giang": "hagi",
    "Kiên Giang": "kigi", "Long An": "loan", "Sóc Trăng": "sotr",
    "Tây Ninh": "tani", "Tiền Giang": "tigi", "TP. Hồ Chí Minh": "tphc",
    "Trà Vinh": "trvi", "Vĩnh Long": "vilo", "Vũng Tàu": "vuta",
    "Đà Nẵng": "dana", "Bình Định": "bidi", "Đắk Lắk": "dalak",
    "Đắk Nông": "dano", "Gia Lai": "gila", "Khánh Hòa": "khho",
    "Kon Tum": "kotu", "Ninh Thuận": "nith", "Phú Yên": "phye",
    "Quảng Bình": "qubi", "Quảng Nam": "quna", "Quảng Ngãi": "qung",
    "Quảng Trị": "qutr", "Thừa Thiên Huế": "thth",
}
DAI_API = {name: _API_BASE + code for name, code in _GAME_CODES.items()}

LICH_QUAY_NAM = {
    "Chủ Nhật": ["Tiền Giang", "Kiên Giang", "Đà Lạt"],
    "Thứ 2": ["TP. Hồ Chí Minh", "Đồng Tháp", "Cà Mau"],
    "Thứ 3": ["Bến Tre", "Vũng Tàu", "Bạc Liêu"],
    "Thứ 4": ["Đồng Nai", "Cần Thơ", "Sóc Trăng"],
    "Thứ 5": ["Tây Ninh", "An Giang", "Bình Thuận"],
    "Thứ 6": ["Vĩnh Long", "Bình Dương", "Trà Vinh"],
    "Thứ 7": ["TP. Hồ Chí Minh", "Long An", "Bình Phước", "Hậu Giang"],
}
LICH_QUAY_TRUNG = {
    "Chủ Nhật": ["Kon Tum", "Khánh Hòa", "Thừa Thiên Huế"],
    "Thứ 2": ["Thừa Thiên Huế", "Phú Yên"],
    "Thứ 3": ["Đắk Lắk", "Quảng Nam"],
    "Thứ 4": ["Đà Nẵng", "Khánh Hòa"],
    "Thứ 5": ["Bình Định", "Quảng Trị", "Quảng Bình"],
    "Thứ 6": ["Gia Lai", "Ninh Thuận"],
    "Thứ 7": ["Đà Nẵng", "Quảng Ngãi", "Đắk Nông"],
}
LICH_QUAY_BAC = {
    "Chủ Nhật": "Thái Bình", "Thứ 2": "Hà Nội", "Thứ 3": "Quảng Ninh",
    "Thứ 4": "Bắc Ninh", "Thứ 5": "Hà Nội", "Thứ 6": "Hải Phòng", "Thứ 7": "Nam Định",
}

DAYS_VI = ["Thứ 2", "Thứ 3", "Thứ 4", "Thứ 5", "Thứ 6", "Thứ 7", "Chủ Nhật"]

# ─────────────────────────────────────────────
# NETWORK
# ─────────────────────────────────────────────

@st.cache_resource
def _get_session():
    s = requests.Session()
    retry = Retry(total=3, connect=3, read=3, backoff_factor=0.5,
                  status_forcelist=[429, 500, 502, 503, 504],
                  allowed_methods=frozenset(["GET"]))
    s.mount("https://", HTTPAdapter(max_retries=retry))
    s.mount("http://", HTTPAdapter(max_retries=retry))
    return s

def http_get_issue_list(url: str) -> list:
    try:
        s = _get_session()
        resp = s.get(url, headers=HEADERS, timeout=15)
        resp.raise_for_status()
        return resp.json().get("t", {}).get("issueList", [])
    except Exception as e:
        st.error(f"Lỗi tải dữ liệu: {e}")
        return []

# ─────────────────────────────────────────────
# DATA PARSING
# ─────────────────────────────────────────────

_detail_cache = {}

def parse_detail(item: dict) -> list:
    detail_str = item.get("detail", "")
    if detail_str not in _detail_cache:
        try:
            _detail_cache[detail_str] = json.loads(detail_str)
        except Exception:
            _detail_cache[detail_str] = []
        if len(_detail_cache) > 500:
            keys = list(_detail_cache.keys())
            for k in keys[:200]:
                del _detail_cache[k]
    return _detail_cache[detail_str]

def get_prizes_flat(item: dict) -> list:
    try:
        detail = parse_detail(item)
        prizes_flat = []
        for field in detail:
            prizes_flat += field.split(",")
        return prizes_flat
    except Exception:
        return []

def get_two_digit_numbers(prizes_flat: list) -> list:
    results = []
    for prize in prizes_flat:
        prize = prize.strip()
        if len(prize) >= 2 and prize[-2:].isdigit():
            results.append(prize[-2:])
    return results

def get_list0(prizes_flat: list) -> list:
    g_nums = []
    for prize in prizes_flat:
        g_nums.extend([ch for ch in prize.strip() if ch.isdigit()])
    counter = Counter(g_nums)
    counts = [counter.get(str(d), 0) for d in range(10)]
    return [str(i) for i, v in enumerate(counts) if v == 0]

def get_missing_heads(prizes_flat: list) -> list:
    heads = []
    for p in prizes_flat:
        p = p.strip()
        if len(p) >= 2:
            heads.append(p[-2])
        elif len(p) == 1:
            heads.append("0")
    counter = Counter(heads)
    counts = [counter.get(str(d), 0) for d in range(10)]
    return [str(i) for i, v in enumerate(counts) if v == 0]

def bridge_ab(list1, list2):
    result_set = {a + b for a in list1 for b in list2}
    result_set.update(b + a for a in list1 for b in list2)
    return sorted(result_set)

# Chạm + Tổng lookup
CHAM_LOOKUP = {}
TONG_LOOKUP = {}
all_nums = [f"{i:02d}" for i in range(100)]
for d in range(10):
    ds = str(d)
    CHAM_LOOKUP[ds] = [n for n in all_nums if ds in n]
for d in range(10):
    TONG_LOOKUP[str(d)] = [n for n in all_nums if (int(n[0]) + int(n[1])) % 10 == d]

def generate_cham_tong(list_missing: list) -> list:
    result_set = set()
    for d_str in list_missing:
        result_set.update(CHAM_LOOKUP.get(d_str, ()))
        result_set.update(TONG_LOOKUP.get(d_str, ()))
    return sorted(result_set)

# ─────────────────────────────────────────────
# PATTERN DETECTION
# ─────────────────────────────────────────────

def detect_special_pattern(prize_str):
    prize_str = prize_str.strip()
    if len(prize_str) < 2:
        return False, None
    digits = [ch for ch in prize_str if ch.isdigit()]
    unique_digits = set(digits)
    if len(unique_digits) <= 3:
        return True, prize_str[-2:]
    return False, None

def detect_consecutive_repeat(prize_str, min_count=3):
    prize_str = prize_str.strip()
    if len(prize_str) < min_count:
        return False, None
    for i in range(len(prize_str) - min_count + 1):
        first_digit = prize_str[i]
        count = 1
        for j in range(i + 1, len(prize_str)):
            if prize_str[j] == first_digit:
                count += 1
            else:
                break
        if count >= min_count:
            if len(prize_str) >= 2:
                return True, prize_str[-2:]
    return False, None

def detect_lap(prize_str):
    prize_str = prize_str.strip()
    if len(prize_str) < 2:
        return False, None
    digit_count = Counter(ch for ch in prize_str if ch.isdigit())
    if any(c >= 2 for c in digit_count.values()):
        return True, prize_str[-2:]
    return False, None

def detect_ganh(prize_str):
    prize_str = prize_str.strip()
    if len(prize_str) < 2:
        return False, None
    if prize_str == prize_str[::-1]:
        return True, prize_str[-2:]
    return False, None

# ─────────────────────────────────────────────
# TÀI XỈU
# ─────────────────────────────────────────────

def get_gdb_digit_sum(item: dict):
    prizes_flat = get_prizes_flat(item)
    gdb = prizes_flat[0].strip() if prizes_flat else ""
    total = sum(int(c) for c in gdb if c.isdigit())
    return item.get("turnNum", ""), gdb, total

def build_tx_sequence(raw_data: list) -> list:
    seq = []
    for item in reversed(raw_data):
        turn, gdb, total = get_gdb_digit_sum(item)
        result = "T" if total >= 23 else "X"
        seq.append({"turn": turn, "gdb": gdb, "total": total, "result": result})
    return seq

# ─────────────────────────────────────────────
# MAIN APP
# ─────────────────────────────────────────────

def get_current_day_vietnamese():
    return DAYS_VI[datetime.now().weekday()]

def get_station_list(region, day):
    if region == "Miền Bắc":
        tinh = LICH_QUAY_BAC.get(day, "")
        return [f"Miền Bắc ({tinh})", "VN Miền Bắc 75s", "Miền Bắc 75s"]
    elif region == "Miền Nam":
        return LICH_QUAY_NAM.get(day, [])
    elif region == "Miền Trung":
        return LICH_QUAY_TRUNG.get(day, [])
    return []

def fetch_data(station_display: str) -> list:
    api_key = station_display
    if "Miền Bắc" in station_display and "75s" not in station_display:
        api_key = "Miền Bắc"
    url = DAI_API.get(api_key)
    if not url:
        st.error(f"Không tìm thấy API cho: {station_display}")
        return []
    with st.spinner(f"Đang tải dữ liệu {station_display}..."):
        return http_get_issue_list(url)

# ─────────────────────────────────────────────
# TAB 1: CẦU LIST 0
# ─────────────────────────────────────────────

def render_tab1(raw_data):
    if not raw_data:
        st.info("Chưa có dữ liệu. Hãy chọn đài và tải dữ liệu.")
        return

    def diff(src, target):
        return sorted(list(set(src) - set(target)))

    processed = []
    for item in raw_data:
        prizes_flat = get_prizes_flat(item)
        two_digits = get_two_digit_numbers(prizes_flat)
        list0 = get_list0(prizes_flat)
        processed.append({
            "ky": item.get("turnNum", ""),
            "list0": list0,
            "res": two_digits,
        })

    rows = []
    for i in range(len(processed)):
        curr = processed[i]
        # Sót K0
        if i + 1 < len(processed):
            l0_curr = processed[i]["list0"]
            l0_next = processed[i + 1]["list0"]
            current_dan = bridge_ab(l0_curr, l0_next)
        else:
            current_dan = []

        row = {
            "Kỳ": curr["ky"],
            "List 0": " ".join(curr["list0"]),
            "Sót K0": " ".join(current_dan),
        }
        for k in range(1, 8):
            target_idx = i - k
            if target_idx < 0:
                row[f"K{k}"] = ""
            else:
                res_target = processed[target_idx]["res"]
                current_dan = diff(current_dan, res_target)
                row[f"K{k}"] = " ".join(current_dan)
        rows.append(row)

    import pandas as pd
    df = pd.DataFrame(rows)

    st.markdown("### 📊 Cầu List 0 (Truyền Thống)")

    def highlight_dan(val):
        if isinstance(val, str) and val and val != "":
            return "background-color: #e8f8f5; color: #16a085;"
        return ""

    def highlight_ky(val):
        return "background-color: #ffebee; color: #c0392b; font-weight: bold;"

    styled = df.style\
        .map(highlight_ky, subset=["Kỳ"])\
        .map(lambda v: "background-color: #fff8e1; color: #f57c00;", subset=["List 0"])\
        .map(lambda v: "background-color: #e1f5fe; color: #0277bd;", subset=["Sót K0"])

    st.dataframe(styled, use_container_width=True, height=600)

# ─────────────────────────────────────────────
# TAB 2: THIẾU ĐẦU & CHẠM TỔNG
# ─────────────────────────────────────────────

def render_tab2(raw_data):
    if not raw_data:
        st.info("Chưa có dữ liệu.")
        return

    st.markdown("### 📊 Cầu Thiếu Đầu & Chạm Tổng")

    col1, col2 = st.columns(2)
    with col1:
        use_duoi_db = st.checkbox("Đuôi ĐB", value=True, key="t2_duoi_db")
        use_dau_db = st.checkbox("Đầu ĐB", value=False, key="t2_dau_db")
    with col2:
        use_duoi_g1 = st.checkbox("Đuôi G1", value=False, key="t2_duoi_g1")
        use_dau_g1 = st.checkbox("Đầu G1", value=False, key="t2_dau_g1")

    processed_data = []
    for item in raw_data:
        prizes_flat = get_prizes_flat(item)
        missing_heads = get_missing_heads(prizes_flat)
        processed_data.append({
            "ky": item.get("turnNum", ""),
            "missing_heads": missing_heads,
            "full_prizes": prizes_flat,
        })

    def get_targets(prizes_flat):
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

    rows = []
    for i, curr in enumerate(processed_data):
        dan_ct = generate_cham_tong(curr["missing_heads"])
        row = {
            "Kỳ": curr["ky"],
            "Thiếu Đầu": ",".join(curr["missing_heads"]),
            "Dàn K0 (Chạm+Tổng)": " ".join(dan_ct),
        }
        for k in range(1, 8):
            target_idx = i - k
            if target_idx < 0:
                row[f"K{k}"] = ""
            else:
                td = processed_data[target_idx]
                targets = get_targets(td["full_prizes"])
                hits = set(dan_ct).intersection(targets)
                row[f"K{k}"] = f"✅ {','.join(sorted(hits))}" if hits else "-"
        rows.append(row)

    import pandas as pd
    df = pd.DataFrame(rows)

    def style_row(row):
        styles = [""] * len(row)
        for j, val in enumerate(row):
            if isinstance(val, str) and val.startswith("✅"):
                styles[j] = "background-color: #D4EDDA; color: #155724; font-weight: bold;"
        return styles

    styled = df.style.apply(style_row, axis=1)
    st.dataframe(styled, use_container_width=True, height=600)

# ─────────────────────────────────────────────
# TAB 3: LÔ LẠ
# ─────────────────────────────────────────────

def render_tab3(raw_data, region="Miền Bắc"):
    if not raw_data:
        st.info("Chưa có dữ liệu.")
        return

    st.markdown("### 📊 Lô Lạ - Pattern Đặc Biệt")

    col1, col2, col3 = st.columns(3)
    with col1:
        use_special = st.checkbox("Số có ≤3 chữ số duy nhất", value=True, key="t3_special")
        use_lap = st.checkbox("Lặp", value=False, key="t3_lap")
    with col2:
        use_ganh = st.checkbox("Gánh/Đảo", value=False, key="t3_ganh")
        use_consecutive = st.checkbox("Số lặp liên tiếp (≥3)", value=False, key="t3_consec")
    with col3:
        keep_dup = st.checkbox("Giữ số trùng", value=False, key="t3_dup")
        nhi_hop_mode = st.radio("Nhị hợp:", ["Mặc định", "Chỉ 1 giải", "Cả hai"],
                                 index=2, key="t3_nhihop", horizontal=True)

    nhi_hop_val = {"Mặc định": 0, "Chỉ 1 giải": 1, "Cả hai": 2}[nhi_hop_mode]
    max_prize_index = 9 if "Bắc" in region else 13

    def diff(src, target):
        return sorted(list(set(src) - set(target)))

    processed = []
    for item in raw_data:
        prizes_flat = get_prizes_flat(item)
        two_digits = get_two_digit_numbers(prizes_flat)
        special_los = []

        for idx, prize in enumerate(prizes_flat):
            if idx > max_prize_index:
                break
            prize = prize.strip()
            found, lo = False, None

            if use_consecutive:
                found, lo = detect_consecutive_repeat(prize, 3)
            if not found and use_lap:
                found, lo = detect_lap(prize)
            if not found and use_ganh:
                found, lo = detect_ganh(prize)
            if not found and use_special:
                found, lo = detect_special_pattern(prize)

            if found and lo:
                prize_digits = set(d for d in prize if d.isdigit())
                if prize_digits:
                    if keep_dup:
                        digits_str = "".join(sorted([d for d in prize if d.isdigit()]))
                    else:
                        digits_str = "".join(sorted(prize_digits))
                    special_los.append(digits_str)

        list0 = sorted(special_los) if keep_dup else sorted(set(special_los))

        # Build Nhị Hợp
        dan_nhi_hop = []
        if list0:
            all_digits = set()
            for s in list0:
                for ch in s:
                    if ch.isdigit():
                        all_digits.add(ch)
            if nhi_hop_val == 0 and len(list0) > 1:
                for d1 in sorted(all_digits):
                    for d2 in sorted(all_digits):
                        dan_nhi_hop.append(d1 + d2)
            elif nhi_hop_val == 1 and len(list0) == 1:
                for d1 in sorted(all_digits):
                    for d2 in sorted(all_digits):
                        dan_nhi_hop.append(d1 + d2)
            elif nhi_hop_val == 2:
                for d1 in sorted(all_digits):
                    for d2 in sorted(all_digits):
                        dan_nhi_hop.append(d1 + d2)

        dan_nhi_hop = sorted(set(dan_nhi_hop))
        processed.append({
            "ky": item.get("turnNum", ""),
            "list0": list0,
            "dan": dan_nhi_hop,
            "res": two_digits,
        })

    rows = []
    for i, curr in enumerate(processed):
        is_single = len(curr["list0"]) == 1
        is_multi = len(curr["list0"]) > 1
        show = (nhi_hop_val == 0 and is_multi) or \
               (nhi_hop_val == 1 and is_single) or \
               (nhi_hop_val == 2 and (is_single or is_multi))

        if not show:
            rows.append({
                "Kỳ": curr["ky"],
                "List 0 (Lô Lạ)": "",
                "Dàn Nhị Hợp": "",
                **{f"K{k}": "" for k in range(1, 11)},
            })
            continue

        current_dan = curr["dan"][:]
        row = {
            "Kỳ": curr["ky"],
            "List 0 (Lô Lạ)": ",".join(curr["list0"]),
            "Dàn Nhị Hợp": " ".join(current_dan[:20]) + ("..." if len(current_dan) > 20 else ""),
        }
        for k in range(1, 11):
            target_idx = i - k
            if target_idx < 0:
                row[f"K{k}"] = ""
            else:
                res_target = processed[target_idx]["res"]
                current_dan = diff(current_dan, res_target)
                row[f"K{k}"] = " ".join(current_dan) if current_dan else "-"
        rows.append(row)

    import pandas as pd
    df = pd.DataFrame(rows)
    st.dataframe(df, use_container_width=True, height=600)

# ─────────────────────────────────────────────
# TAB 4: LÔ XIÊN
# ─────────────────────────────────────────────

def render_tab5_loxien():
    st.markdown("### 🔢 Công Cụ Ghép Xiên Tự Động")
    st.caption("Xiên QUAY: Ghép quay vòng trong Nhóm 1 | Xiên NHÓM: Ghép giữa các nhóm")

    col1, col2, col3, col4 = st.columns(4)
    groups = []
    for i, col in enumerate([col1, col2, col3, col4], 1):
        with col:
            txt = st.text_area(f"Nhóm {i}", height=120, key=f"lx_grp{i}",
                               placeholder="Nhập các số, cách nhau bởi dấu cách hoặc phẩy")
            nums = sorted(set(n.strip() for n in txt.replace(",", " ").split() if n.strip().isdigit()))
            groups.append(nums)

    col_sep, col_x2, col_x3, col_x4 = st.columns([2, 1, 1, 1])
    with col_sep:
        sep = st.selectbox("Ký tự nối:", ["&", ",", "-", " "], key="lx_sep")
    with col_x2:
        use_x2 = st.checkbox("Xiên 2", value=True, key="lx_x2")
    with col_x3:
        use_x3 = st.checkbox("Xiên 3", value=True, key="lx_x3")
    with col_x4:
        use_x4 = st.checkbox("Xiên 4", value=True, key="lx_x4")

    btn_quay, btn_nhom, _ = st.columns([1, 1, 4])
    with btn_quay:
        do_quay = st.button("🔄 Tạo Xiên Quay", use_container_width=True)
    with btn_nhom:
        do_nhom = st.button("🔗 Tạo Xiên Nhóm", use_container_width=True)

    if do_quay:
        nums = groups[0]
        if len(nums) < 2:
            st.warning("Nhập ít nhất 2 số ở Nhóm 1!")
        else:
            cols = st.columns(3)
            for idx, (k, use) in enumerate([(2, use_x2), (3, use_x3), (4, use_x4)]):
                with cols[idx]:
                    if use:
                        combos = list(itertools.combinations(nums, k))
                        result = ";\n".join(sep.join(c) for c in combos)
                        st.text_area(f"Xiên {k} ({len(combos)} cặp)", value=result, height=200, key=f"lx_r_quay{k}")

    if do_nhom:
        cols = st.columns(3)
        for idx, (k, use) in enumerate([(2, use_x2), (3, use_x3), (4, use_x4)]):
            with cols[idx]:
                if use:
                    src = groups[:k]
                    if all(src):
                        res = list(itertools.product(*src))
                        result = ";\n".join(sep.join(c) for c in res)
                        st.text_area(f"Xiên {k} ({len(res)} cặp)", value=result, height=200, key=f"lx_r_nhom{k}")
                    else:
                        st.warning(f"Cần nhập đủ {k} nhóm!")

# ─────────────────────────────────────────────
# TAB 5: TÀI / XỈU
# ─────────────────────────────────────────────

def render_tab_taixiu(raw_data):
    if not raw_data:
        st.info("Chưa có dữ liệu.")
        return

    st.markdown("### 🎲 Phân Tích Tài / Xỉu")

    seq = build_tx_sequence(raw_data)
    if not seq:
        st.warning("Không đủ dữ liệu.")
        return

    # Stats
    total_t = sum(1 for d in seq if d["result"] == "T")
    total_x = len(seq) - total_t
    pct_t = total_t / len(seq) * 100

    last = seq[-1]["result"]
    streak = 1
    for d in reversed(seq[:-1]):
        if d["result"] == last:
            streak += 1
        else:
            break

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Tổng kỳ", len(seq))
    c2.metric("🔴 Tài", f"{total_t} ({pct_t:.0f}%)")
    c3.metric("🔵 Xỉu", f"{total_x} ({100 - pct_t:.0f}%)")
    streak_name = "Tài 🔴" if last == "T" else "Xỉu 🔵"
    c4.metric("Chuỗi hiện tại", f"{streak} {streak_name}")

    latest = seq[-1]
    st.info(f"**Kỳ mới nhất:** {latest['turn']}  |  **GĐB:** {latest['gdb']}  |  "
            f"**Tổng:** {latest['total']}  →  {'**TÀI 🔴**' if latest['result'] == 'T' else '**XỈU 🔵**'}")

    # Bead road
    st.markdown("#### Bản Đồ Cầu Tài/Xỉu (Bead Road)")
    bead_html = _build_bead_road_html(seq)
    st.components.v1.html(bead_html, height=250, scrolling=True)

    # Detail table
    st.markdown("#### 15 Kỳ Gần Nhất")
    import pandas as pd
    recent = seq[-15:]
    table_rows = []
    for i, d in enumerate(recent):
        s = 1
        for j in range(i - 1, -1, -1):
            if recent[j]["result"] == d["result"]:
                s += 1
            else:
                break
        table_rows.append({
            "Kỳ": d["turn"],
            "GĐB": d["gdb"],
            "Tổng": d["total"],
            "Kết quả": "TÀI 🔴" if d["result"] == "T" else "XỈU 🔵",
            "Chuỗi": f"{s} {'Tài' if d['result'] == 'T' else 'Xỉu'} liên tiếp",
        })
    df = pd.DataFrame(list(reversed(table_rows)))

    def color_result(val):
        if "TÀI" in str(val):
            return "background-color: #fdecea; color: #c0392b; font-weight:bold;"
        elif "XỈU" in str(val):
            return "background-color: #e8f4fd; color: #1565c0; font-weight:bold;"
        return ""

    styled = df.style.map(color_result, subset=["Kết quả"])
    st.dataframe(styled, use_container_width=True)

def _build_bead_road_html(seq):
    MAX_ROWS = 6
    CELL = 32
    PAD = 4
    TAI_COLOR = "#c0392b"
    XIU_COLOR = "#1a6494"

    col, row, prev_result = 0, 0, None
    cells = []
    for d in seq:
        r = d["result"]
        if prev_result is not None and (r != prev_result or row >= MAX_ROWS):
            col += 1
            row = 0
        color = TAI_COLOR if r == "T" else XIU_COLOR
        x = PAD + col * (CELL + 2)
        y = PAD + row * (CELL + 2)
        cells.append((x, y, color, r, d["total"]))
        prev_result = r
        row += 1

    total_cols = col + 1
    w = PAD + total_cols * (CELL + 2) + PAD
    h = PAD + MAX_ROWS * (CELL + 2) + PAD

    svg_items = []
    for (x, y, color, lbl, total) in cells:
        cx = x + CELL // 2
        cy = y + CELL // 2
        svg_items.append(
            f'<circle cx="{cx}" cy="{cy}" r="{CELL//2 - 2}" fill="{color}" stroke="white" stroke-width="1"/>'
            f'<text x="{cx}" y="{cy + 4}" text-anchor="middle" fill="white" font-size="12" font-weight="bold">{lbl}</text>'
            f'<text x="{cx + CELL//2 - 4}" y="{cy + CELL//2 - 2}" text-anchor="end" fill="#cccccc" font-size="8">{total}</text>'
        )

    svg_content = "\n".join(svg_items)
    return f"""
    <div style="overflow-x:auto; background:#0d2137; border-radius:8px; padding:4px;">
      <svg width="{w}" height="{h}" xmlns="http://www.w3.org/2000/svg">
        <rect width="{w}" height="{h}" fill="#0d2137"/>
        {svg_content}
      </svg>
    </div>
    """

# ─────────────────────────────────────────────
# KẾT QUẢ PANEL
# ─────────────────────────────────────────────

def render_result_panel(raw_data, show_g4g7=False):
    if not raw_data:
        return

    st.markdown("#### 📋 Kết Quả Mới Nhất")

    PRIZE_LABELS_MB = ["ĐB", "G1", "G2", "G2", "G3", "G3", "G3", "G3", "G3", "G3",
                       "G4", "G4", "G4", "G4", "G5", "G5", "G5", "G5", "G5", "G5",
                       "G6", "G6", "G6", "G7", "G7", "G7", "G7"]

    for period_idx in range(min(2, len(raw_data))):
        item = raw_data[period_idx]
        detail = parse_detail(item)
        turn = item.get("turnNum", "")
        open_time = item.get("openTime", "")
        st.markdown(f"**🎯 Kỳ {turn}** ({open_time})")

        for idx, content in enumerate(detail):
            if idx >= len(PRIZE_LABELS_MB):
                break
            label = PRIZE_LABELS_MB[idx] if idx < len(PRIZE_LABELS_MB) else f"G{idx}"
            if not show_g4g7 and label in ("G4", "G5", "G6", "G7"):
                continue
            if not content or content.strip() in ("", "-"):
                continue
            st.markdown(f"`{label}` &nbsp; **{content.strip()}**", unsafe_allow_html=True)

        if period_idx < min(2, len(raw_data)) - 1:
            st.divider()

    # Đầu/Đuôi stats
    st.markdown("#### 📊 Thống Kê Đầu/Đuôi")
    latest_item = raw_data[0]
    prizes_flat = get_prizes_flat(latest_item)
    all_numbers = [p.strip() for p in prizes_flat if len(p.strip()) >= 2]

    head_to_tails = {str(i): [] for i in range(10)}
    tail_to_heads = {str(i): [] for i in range(10)}
    for num in all_numbers:
        if len(num) >= 2:
            last2 = num[-2:]
            if last2.isdigit():
                h, t = last2[0], last2[1]
                head_to_tails[h].append(t)
                tail_to_heads[t].append(h)

    import pandas as pd
    rows = []
    for i in range(10):
        d = str(i)
        rows.append({
            "Đầu": d,
            "Đuôi ra": ",".join(sorted(head_to_tails[d])),
            " ": "",
            "Đuôi": d,
            "Đầu ra": ",".join(sorted(tail_to_heads[d])),
        })
    st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

# ─────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────

def main():
    st.set_page_config(
        page_title="Phân Tích Xổ Số",
        page_icon="🎲",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    st.markdown("""
    <style>
    .stApp { background-color: #f8f9fa; }
    .block-container { padding-top: 1rem; }
    .stTabs [data-baseweb="tab-list"] { gap: 8px; }
    .stTabs [data-baseweb="tab"] { 
        background: #eef0f3; border-radius: 6px 6px 0 0;
        padding: 8px 16px; font-weight: 600;
    }
    .stTabs [aria-selected="true"] { background: #ff4b4b; color: white; }
    </style>
    """, unsafe_allow_html=True)

    st.title("🎲 Phân Tích Xổ Số - Pro Version")

    # ── Sidebar Controls ──
    with st.sidebar:
        st.header("⚙️ Cấu Hình")
        region = st.selectbox("Khu vực", ["Miền Bắc", "Miền Nam", "Miền Trung"], key="region")
        today_day = get_current_day_vietnamese()
        day = st.selectbox("Thứ", DAYS_VI, index=DAYS_VI.index(today_day), key="day")

        stations = get_station_list(region, day)
        if stations:
            station = st.selectbox("Đài", stations, key="station")
        else:
            st.warning(f"Không có lịch quay {region} {day}")
            station = None

        show_g4g7 = st.checkbox("Hiện G4-G7 trong kết quả", value=False)
        load_btn = st.button("📡 Tải Dữ Liệu", type="primary", use_container_width=True)

        st.divider()
        st.caption("Nguồn dữ liệu: kqxs88.live")

    # ── State management ──
    if "raw_data" not in st.session_state:
        st.session_state.raw_data = []
    if "current_station" not in st.session_state:
        st.session_state.current_station = None

    if load_btn and station:
        data = fetch_data(station)
        st.session_state.raw_data = data
        st.session_state.current_station = station
        if data:
            st.success(f"✅ Đã tải {len(data)} kỳ từ **{station}**")
        else:
            st.error("Không tải được dữ liệu!")

    raw_data = st.session_state.raw_data

    # ── Layout: Left (tabs) + Right (results) ──
    main_col, result_col = st.columns([3, 1])

    with result_col:
        render_result_panel(raw_data, show_g4g7)

    with main_col:
        if raw_data:
            st.caption(f"📡 Đang xem: **{st.session_state.current_station}** — {len(raw_data)} kỳ")

        tab1, tab2, tab3, tab4, tab5 = st.tabs([
            "Cầu List 0",
            "Thiếu Đầu & Chạm Tổng",
            "Lô Lạ (Pattern)",
            "🔢 Lô Xiên",
            "🎲 Tài / Xỉu",
        ])

        with tab1:
            render_tab1(raw_data)

        with tab2:
            render_tab2(raw_data)

        with tab3:
            render_tab3(raw_data, region)

        with tab4:
            render_tab5_loxien()

        with tab5:
            render_tab_taixiu(raw_data)


if __name__ == "__main__":
    main()
