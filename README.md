# Phần Mềm Soi Cầu Đa Năng 3 Miền

Ứng dụng Streamlit phân tích và dự đoán kết quả xổ số 3 miền (Bắc, Nam, Trung).

## Tính năng

- 🎯 Hỗ trợ 3 miền: Miền Bắc, Miền Nam, Miền Trung
- 📊 Hiển thị bảng kết quả chi tiết
- 🔍 Phân tích "List 0" (số không xuất hiện)
- 🎲 Tính toán "Sót K1-K7" (dự đoán cho các kỳ tiếp theo)
- 🔄 Lấy dữ liệu trực tiếp từ API
- ⚙️ Tùy chọn giải để phân tích

## Cài đặt

1. Clone repository:
```bash
git clone <repository-url>
cd 75smb
```

2. Cài đặt thư viện:
```bash
pip install -r requirements.txt
```

3. Chạy ứng dụng:
```bash
streamlit run app.py
```

## Triển khai lên Streamlit Cloud

1. Đẩy code lên GitHub repository
2. Truy cập [share.streamlit.io](https://share.streamlit.io/)
3. Kết nối với GitHub repository
4. Chọn branch `main` và file `app.py`
5. Nhấn Deploy

## Hướng dẫn sử dụng

1. **Chọn khu vực**: Miền Bắc / Miền Nam / Miền Trung
2. **Chọn đài**: Danh sách đài sẽ được lọc theo khu vực
3. **Chọn giải**: Tích chọn các giải muốn phân tích (sidebar)
4. **Tải dữ liệu**: Nhấn nút "🔄 TẢI LẠI" để lấy dữ liệu mới nhất
5. **Xem kết quả**: 
   - Bảng kết quả hiển thị chi tiết các giải
   - Bảng phân tích hiển thị "List 0" và "Sót K1-K7"

## Giải thích thuật ngữ

- **List 0**: Các số từ 0-9 không xuất hiện trong kỳ
- **Sót K1**: Dự đoán cho kỳ hiện tại (dựa trên bridge của 2 kỳ trước)
- **Sót K2-K7**: Dự đoán cho các kỳ tiếp theo (loại bỏ dần các số đã trúng)

## Công nghệ sử dụng

- **Streamlit**: Framework web app
- **Pandas**: Xử lý dữ liệu dạng bảng
- **Requests**: Gọi API lấy dữ liệu
- **urllib3**: Hỗ trợ retry khi gọi API

## Nguồn dữ liệu

Dữ liệu được lấy từ API: `https://www.kqxs88.live/`

## License

MIT License
