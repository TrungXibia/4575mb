# -*- coding: utf-8 -*-
import tkinter as tk
from tkinter import ttk, messagebox
import requests
import json
from collections import Counter
import tksheet
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

COLOR_BG = "#ffffff"       
COLOR_PANEL_BG = "#f8f9fa" 
COLOR_HEADER_BG = "#eef0f3" 
COLOR_ACCENT = "#ff4b4b"
COLOR_BORDER = "#dee2e6"

FONT_MAIN = ("Segoe UI", 9, "normal")
FONT_BOLD = ("Segoe UI", 9, "bold")
FONT_LARGE = ("Segoe UI", 11, "bold")

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

# =============================================================================
# NETWORK UTILS
# =============================================================================

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
    days = ["Thứ 2", "Thứ 3", "Thứ 4", "Thứ 5", "Thứ 6", "Thứ 7", "Chủ Nhật"]
    return days[datetime.now().weekday()]

# =============================================================================
# MAIN APP CLASS
# =============================================================================

class LotteryApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Phần Mềm Soi Cầu Đa Năng 3 Miền - Pro Version (Auto Load)")
        self.geometry("1600x900")
        self.configure(bg=COLOR_BG)
        
        # Style
        style = ttk.Style(self)
        style.theme_use('clam')
        style.configure("TFrame", background=COLOR_BG)
        style.configure("Panel.TFrame", background=COLOR_PANEL_BG)
        style.configure("TLabel", background=COLOR_PANEL_BG, foreground="#333", font=FONT_MAIN)
        style.configure("Header.TLabel", background=COLOR_PANEL_BG, foreground="#333", font=FONT_BOLD)
        style.configure("TButton", font=FONT_BOLD, background=COLOR_ACCENT, foreground="white", borderwidth=0)
        style.map("TButton", background=[("active", "#ff6b6b")])
        style.configure("TCheckbutton", background=COLOR_PANEL_BG, font=("Segoe UI", 9))
        
        self.setup_ui()
        self.cb_region.current(0) 
        self.on_region_change()   

    def setup_ui(self):
        top_frame = ttk.Frame(self, style="Panel.TFrame")
        top_frame.pack(side="top", fill="x", pady=(0, 1))

        # --- Khu vực & Đài ---
        fr_source = ttk.Frame(top_frame, style="Panel.TFrame")
        fr_source.pack(side="left", padx=15, pady=10)
        
        ttk.Label(fr_source, text="KHU VỰC & ĐÀI", style="Header.TLabel").pack(anchor="w")
        
        self.cb_region = ttk.Combobox(fr_source, values=["Miền Bắc", "Miền Nam", "Miền Trung"], width=12, state="readonly", font=FONT_MAIN)
        self.cb_region.pack(side="left", pady=5)
        self.cb_region.bind('<<ComboboxSelected>>', self.on_region_change)
        
        self.cb_station = ttk.Combobox(fr_source, width=25, state="readonly", font=FONT_MAIN)
        self.cb_station.pack(side="left", padx=5, pady=5)
        self.cb_station.bind('<<ComboboxSelected>>', lambda e: self.update_data())
        
        self.var_today = tk.BooleanVar(value=True)
        self.chk_today = ttk.Checkbutton(fr_source, text="Lịch hôm nay", variable=self.var_today, command=self.on_region_change)
        self.chk_today.pack(side="left", padx=5)
        
        btn_load = ttk.Button(fr_source, text="TẢI LẠI", command=self.update_data, width=12)
        btn_load.pack(side="left", padx=10)

        # Separator
        ttk.Frame(top_frame, width=1, style="Panel.TFrame").pack(side="left", fill="y", padx=10)

        # --- Cấu hình List 0 ---
        fr_config = ttk.Frame(top_frame, style="Panel.TFrame")
        fr_config.pack(side="left", fill="y", padx=10, pady=10)
        
        ttk.Label(fr_config, text="CHỌN GIẢI ĐỂ PHÂN TÍCH (Và hiển thị cột)", style="Header.TLabel", foreground=COLOR_ACCENT).pack(anchor="w", pady=(0,5))
        
        self.fr_checkboxes = ttk.Frame(fr_config, style="Panel.TFrame")
        self.fr_checkboxes.pack(side="left", padx=0)
        
        self.giai_vars = []
        default_checks = [2, 3]
        for i, label in enumerate(GIAI_LABELS_MB):
            var = tk.BooleanVar(value=(i in default_checks))
            var.trace_add("write", lambda *a: self.refresh_ui())
            chk = ttk.Checkbutton(self.fr_checkboxes, text=label, variable=var)
            chk.grid(row=i//9, column=i%9, sticky="w", padx=2)
            self.giai_vars.append(var)

        # --- Info ---
        fr_info = ttk.Frame(top_frame, style="Panel.TFrame")
        fr_info.pack(side="right", padx=20, fill="y")
        self.lbl_info = tk.Label(fr_info, text="Sẵn sàng", font=FONT_LARGE, fg=COLOR_ACCENT, bg=COLOR_PANEL_BG)
        self.lbl_info.pack(pady=15)

        # MAIN LAYOUT
        main_body = ttk.Frame(self)
        main_body.pack(fill="both", expand=True, padx=5, pady=5)

        # LEFT
        frame_left = ttk.Frame(main_body)
        frame_left.pack(side="left", fill="y")
        
        self.sheet_res = tksheet.Sheet(frame_left, headers=["Kỳ"], width=400, font=FONT_MAIN, header_font=FONT_BOLD)
        self.sheet_res.pack(fill="both", expand=True)
        self.sheet_res.enable_bindings()

        # RIGHT
        frame_right = ttk.Frame(main_body)
        frame_right.pack(side="left", fill="both", expand=True, padx=(5, 0))
        
        cols_anal = ["Kỳ", "List 0 (Thiếu)", "Sót K1 (Nay)", "Sót K2", "Sót K3", "Sót K4", "Sót K5", "Sót K6", "Sót K7"]
        self.sheet_anal = tksheet.Sheet(frame_right, headers=cols_anal, font=FONT_MAIN, header_font=FONT_BOLD)
        self.sheet_anal.pack(fill="both", expand=True)
        self.sheet_anal.enable_bindings()
        
    def on_region_change(self, event=None):
        region = self.cb_region.get()
        today_str = get_current_day_vietnamese()
        is_today_filter = self.var_today.get()
        
        stations = []
        if region == "Miền Bắc":
            lbl_tinh = LICH_QUAY_BAC.get(today_str, "")
            stations = [f"Miền Bắc ({lbl_tinh})", "Miền Bắc 75s", "Miền Bắc 45s"]
        elif region == "Miền Nam":
            if is_today_filter:
                stations = LICH_QUAY_NAM.get(today_str, [])
            else:
                s = set()
                for lst in LICH_QUAY_NAM.values(): s.update(lst)
                stations = sorted(list(s))
        elif region == "Miền Trung":
            if is_today_filter:
                stations = LICH_QUAY_TRUNG.get(today_str, [])
            else:
                s = set()
                for lst in LICH_QUAY_TRUNG.values(): s.update(lst)
                stations = sorted(list(s))

        self.cb_station['values'] = stations
        if stations:
            self.cb_station.current(0)
            self.update_data()
        else:
            self.cb_station.set("")
            self.lbl_info.config(text=f"Không có lịch quay {region} hôm nay")

    def update_data(self):
        station_display = self.cb_station.get()
        if not station_display: return
        
        api_key = station_display
        if "Miền Bắc" in station_display and "45s" not in station_display and "75s" not in station_display:
            api_key = "Miền Bắc"
        
        url = DAI_API.get(api_key)
        if not url:
            for k, v in DAI_API.items():
                if k == api_key:
                    url = v
                    break
        if not url: return
            
        self.lbl_info.config(text=f"Đang tải: {station_display}...")
        self.update() 
        
        self.raw_data = http_get_issue_list(url)
        
        if not self.raw_data:
            self.lbl_info.config(text="Lỗi tải dữ liệu!")
            return

        self.refresh_ui()
        self.lbl_info.config(text=f"Đã tải: {station_display} ({len(self.raw_data)} kỳ)")

    def refresh_ui(self):
        if not hasattr(self, 'raw_data') or not self.raw_data:
            return
        self.render_result_table()
        self.recalc_analysis()

    def render_result_table(self):
        """Vẽ bảng kết quả: Cố định ĐB, các giải khác theo checkbox"""
        
        # 1. Xác định cột hiển thị
        # Mặc định luôn có ĐB (Index 0)
        display_indices = [0] 
        headers = ["Kỳ", "ĐB"]
        
        # Duyệt qua các checkbox để thêm cột
        for i, var in enumerate(self.giai_vars):
            if i == 0: continue # Bỏ qua checkbox ĐB vì đã thêm thủ công ở trên
            
            if var.get():
                display_indices.append(i)
                headers.append(GIAI_LABELS_MB[i])
        
        # 2. Xây dựng dữ liệu dòng
        rows_res = []
        for item in self.raw_data:
            d = json.loads(item['detail'])
            prizes_flat = []
            for f in d: prizes_flat += f.split(',')
            
            row = [item['turnNum']]
            
            # Lấy dữ liệu theo index hiển thị
            for idx in display_indices:
                if idx < len(prizes_flat):
                    row.append(prizes_flat[idx])
                else:
                    row.append("")
            
            rows_res.append(row)
            
        # 3. Cập nhật bảng
        self.sheet_res.headers(headers)
        self.sheet_res.set_sheet_data(rows_res)
        self.sheet_res.set_all_cell_sizes_to_text(redraw=False)
        self.sheet_res.column_width(0, 80)
        self.sheet_res.column_width(1, 60) # Fix size cột ĐB cho đẹp
        self.sheet_res.redraw()

    def recalc_analysis(self):
        """Tính toán (vẫn dùng Checkbox ĐB nếu được tích)"""
        processed = []

        for item in self.raw_data:
            detail = json.loads(item['detail'])
            counter = Counter()
            prizes_flat = []
            for field in detail: prizes_flat += field.split(",")

            g_nums = []
            idxs = [i for i, v in enumerate(self.giai_vars) if v.get()]
            for idx in idxs:
                if idx < len(prizes_flat):
                    g_nums.extend([ch for ch in prizes_flat[idx].strip() if ch.isdigit()])
            counter = Counter(g_nums)
            
            counts = [counter.get(str(d), 0) for d in range(10)]
            list0 = [str(i) for i, v in enumerate(counts) if v == 0]
            
            current_los = []
            for lo in prizes_flat:
                lo = lo.strip()
                if len(lo)>=2 and lo[-2:].isdigit():
                    current_los.append(lo[-2:])

            processed.append({
                "ky": item['turnNum'],
                "list0": list0,
                "res": current_los
            })

        # Logic Cầu
        def bridge_ab(l1, l2):
            s = set()
            for a in l1:
                for b in l2:
                    s.add(a+b)
                    s.add(b+a)
            return sorted(list(s))

        def diff(src, target):
            return sorted(list(set(src) - set(target)))

        rows_anal = []
        for i in range(len(processed)):
            curr = processed[i]
            row = [curr["ky"], ",".join(curr["list0"])]
            
            if i + 2 < len(processed):
                l0_prev1 = processed[i+1]["list0"]
                l0_prev2 = processed[i+2]["list0"]
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

        self.sheet_anal.set_sheet_data(rows_anal)
        self.sheet_anal.column_width(0, 80)
        self.sheet_anal.column_width(1, 80)
        for c in range(2, 9): self.sheet_anal.column_width(c, 130)
        self.sheet_anal.highlight_columns([1], bg="#ffebee", fg="#c0392b")
        self.sheet_anal.highlight_columns([2], bg="#e8f8f5", fg="#16a085")
        self.sheet_anal.redraw()

if __name__ == "__main__":
    app = LotteryApp()
    app.mainloop()
