# 🎲 Phần Mềm Phân Tích Xổ Số - Streamlit Version

Chuyển đổi từ ứng dụng Tkinter sang Streamlit web app, dễ dàng deploy lên Streamlit Cloud.

## ✨ Tính Năng

| Tab | Mô tả |
|-----|-------|
| **Cầu List 0** | Phân tích List 0 truyền thống, K1-K7 |
| **Thiếu Đầu & Chạm Tổng** | Dàn chạm tổng từ đầu thiếu |
| **Lô Lạ (Pattern)** | Phát hiện lô đặc biệt: lặp, gánh, tam hoa... |
| **Lô Xiên** | Ghép xiên 2/3/4 tự động theo nhóm |
| **Tài / Xỉu** | Bead road + thống kê chuỗi Tài/Xỉu |

## 🚀 Cách Chạy Local

```bash
pip install -r requirements.txt
streamlit run app.py
```

## ☁️ Deploy lên Streamlit Cloud

1. Push code lên GitHub:
```bash
git init
git add app.py requirements.txt README.md
git commit -m "Initial commit: Lottery Analysis App"
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO.git
git push -u origin main
```

2. Vào [share.streamlit.io](https://share.streamlit.io)
3. Kết nối GitHub → chọn repo → chọn `app.py` → **Deploy**

## 📁 Cấu Trúc

```
.
├── app.py            # Ứng dụng chính
├── requirements.txt  # Dependencies
└── README.md         # Hướng dẫn
```

## 📊 Nguồn Dữ Liệu

API từ `kqxs88.live` — hỗ trợ Miền Bắc, Miền Nam, Miền Trung.
