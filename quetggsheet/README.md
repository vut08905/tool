# Hướng dẫn Quét Google Sheet bị khóa

## 🎯 3 Phương pháp chính

### 1️⃣ Google Apps Script (DỄ NHẤT - KHUYẾN NGHỊ)
**Ưu điểm:** Không cần cài đặt gì, chạy trực tiếp trong Google Sheets

**Cách làm:**
1. Mở Google Sheet cần quét
2. Vào **Extensions** → **Apps Script**
3. Paste code từ file `google_apps_script.gs`
4. Nhấn **Run** và cho phép quyền truy cập
5. Dữ liệu sẽ được export vào Google Drive hoặc gửi email

**Lưu ý:** Phương pháp này chỉ hoạt động nếu bạn có quyền xem Sheet

---

### 2️⃣ Selenium (Scraping Web)
**Ưu điểm:** Hoạt động ngay cả khi không có API access, giống như người dùng thật

**Cách làm:**
```powershell
# Cài đặt
pip install -r requirements.txt

# Chạy
python scrape_google_sheet.py
```

**Các bước:**
1. Script sẽ mở Chrome tự động
2. Đăng nhập Google khi được yêu cầu
3. Mở Sheet và nhấn Enter trong terminal
4. Script sẽ scrape tất cả dữ liệu hiển thị

**Lưu ý:** 
- Cần đăng nhập thủ công lần đầu
- Có thể bị giới hạn nếu Sheet quá lớn
- Tốc độ phụ thuộc vào kết nối mạng

---

### 3️⃣ Google Sheets API (CHÍNH THỨC)
**Ưu điểm:** Nhanh, chính xác, có thể tự động hóa

**Cách làm:**
```powershell
pip install -r requirements.txt
python scrape_gsheet_api.py
```

**Setup Google Cloud:**
1. Vào [Google Cloud Console](https://console.cloud.google.com/)
2. Tạo project mới
3. Enable **Google Sheets API**
4. Tạo **OAuth 2.0 credentials**
5. Download file `credentials.json` và để cùng folder
6. Chạy script, đăng nhập khi được yêu cầu

**Lấy Spreadsheet ID:**
```
URL: https://docs.google.com/spreadsheets/d/SPREADSHEET_ID/edit
                                              ^^^^^^^^^^^^^^
```

---

## ⚠️ Lưu ý quan trọng

### Quyền truy cập:
- ✅ Bạn PHẢI có quyền **Viewer** trở lên
- ❌ Nếu Sheet ở chế độ "Anyone with the link" → OK
- ❌ Nếu Sheet chỉ cho phép specific emails → Email bạn phải được add

### Giới hạn:
- **Apps Script:** Giới hạn 6 phút chạy mỗi lần
- **Selenium:** Phụ thuộc vào tốc độ render của browser
- **API:** Quota 500 requests/100 seconds/user

### Pháp lý:
- ⚖️ Chỉ scrape Sheet mà bạn có quyền truy cập hợp pháp
- ⚖️ Tôn trọng quyền riêng tư và bản quyền dữ liệu
- ⚖️ Không sử dụng cho mục đích xấu

---

## 🚀 Quick Start

```powershell
# Clone/Download project
cd d:\quetggsheet

# Cài đặt dependencies
pip install -r requirements.txt

# Chọn 1 trong 3 phương pháp:

# Phương pháp 1: Apps Script
# → Mở Google Sheet → Extensions → Apps Script → Paste code

# Phương pháp 2: Selenium
python scrape_google_sheet.py

# Phương pháp 3: API
python scrape_gsheet_api.py
```

---

## 🔧 Troubleshooting

### "Access Denied"
→ Bạn không có quyền xem Sheet. Yêu cầu owner cấp quyền.

### "Selenium không tìm thấy elements"
→ Google Sheets thay đổi HTML structure. Cần update selector.

### "API quota exceeded"
→ Đợi 1 phút hoặc dùng API key khác.

### Sheet quá lớn, scrape lâu
→ Chia nhỏ range: `Sheet1!A1:Z1000` thay vì toàn bộ.

---

## 📊 Export formats

Dữ liệu được lưu dưới dạng:
- **JSON:** `sheet_data.json` (mặc định)
- **CSV:** Dùng `pandas.to_csv()`
- **Excel:** Dùng `pandas.to_excel()`

```python
import pandas as pd
import json

# Đọc JSON
with open('sheet_data.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# Chuyển sang DataFrame
df = pd.DataFrame(data[1:], columns=data[0])

# Export
df.to_csv('output.csv', index=False, encoding='utf-8-sig')
df.to_excel('output.xlsx', index=False)
```

---

## 💡 Tips

1. **Dùng Apps Script nếu có thể** - Đơn giản nhất
2. **Selenium cho Sheet phức tạp** - Khi API không hoạt động
3. **Cache credentials** - Lưu token để không phải đăng nhập lại
4. **Batch processing** - Nếu có nhiều sheets
5. **Error handling** - Luôn có backup plan

---

## 📞 Support

Nếu gặp vấn đề, check:
- File `credentials.json` đã đúng chưa
- Chrome driver version có khớp với Chrome không
- Network connection ổn định không
- Sheet ID có chính xác không

Good luck! 🎉
