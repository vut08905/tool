# 🎓 ULSA Schedule Crawler

Tool Python để crawl lịch học từ trang web ULSA (http://sinhvien.ulsa.edu.vn/TraCuuLichHocSinhVien.aspx)

## 🚀 Tính năng

- ✅ **Enhanced Python Version**: Phiên bản mạnh mẽ với auto-detect và màu sắc
- ✅ **Simple Python Version**: Phiên bản đơn giản cho người mới bắt đầu
- ✅ **Class Manager**: Tool quản lý lịch học đã crawl
- ✅ **Tự động phân trang**: Crawl tất cả các trang
- ✅ **Xuất Excel**: Định dạng đẹp với styling
- ✅ **Xuất JSON**: Backup dữ liệu
- ✅ **Giao diện thân thiện**: Hướng dẫn từng bước
- ✅ **Xử lý lỗi**: Robust error handling

## 📋 Yêu cầu hệ thống

### Python + Dependencies
```bash
pip install selenium pandas openpyxl
```

### Chrome/Chromium
- Cần có Chrome browser đã cài đặt
- ChromeDriver sẽ được tự động tải bởi Selenium

## 🎯 Cách sử dụng

### Cách 1: Sử dụng Batch Script (Windows)
```bash
# Double-click file run_crawler.bat
# Hoặc chạy từ command line:
run_crawler.bat
```

### Cách 2: Chạy trực tiếp

#### Enhanced Python Version (Khuyên dùng)
```bash
python enhanced_crawler.py
```

#### Simple Python Version
```bash
python simple_crawler.py
```

## 📖 Hướng dẫn sử dụng

1. **Khởi động tool** bằng một trong các cách trên
2. **Chọn tùy chọn** (headless mode, v.v.)
3. **Browser sẽ mở** trang ULSA
4. **Đăng nhập thủ công** vào hệ thống ULSA
5. **Chọn học kỳ** muốn crawl
6. **Nhấn "Tra cứu"** để hiển thị bảng lịch học
7. **Quay lại terminal** và nhấn Enter
8. **Tool sẽ tự động**:
   - Phát hiện bảng lịch học
   - Crawl tất cả các trang
   - Xuất ra file Excel/JSON
   - Hiển thị thống kê

## 📁 Cấu trúc file output

### Excel File
```
lich_hoc_ulsa_enhanced_YYYYMMDD_HHMMSS.xlsx
├── Sheet: "Lịch học"
└── Columns:
    ├── STT
    ├── Mã học phần  
    ├── Tên học phần
    ├── Số tín chỉ
    ├── Tên lớp tín chỉ
    ├── Ca học
    ├── Lịch học
    ├── Giảng viên
    ├── Phòng học
    ├── Còn trống
    ├── Ghi chú
    └── Ngày crawl
```

## 📊 Class Manager

Tool quản lý lịch học đã crawl:
- Xem danh sách môn học
- Thêm/sửa/xóa môn học
- Xuất ra Excel
- Import từ file Excel
- Thống kê tín chỉ

### Mở Class Manager:
```bash
# Từ batch menu
run_crawler.bat -> Option 3

# Hoặc trực tiếp
start class_manager.html
```

## 📖 Hướng dẫn sử dụng

1. **Khởi động tool** bằng một trong các cách trên
2. **Chọn tùy chọn** (headless mode, export JSON, v.v.)
3. **Browser sẽ mở** trang ULSA
4. **Đăng nhập thủ công** vào hệ thống ULSA
5. **Chọn học kỳ** muốn crawl
6. **Nhấn "Tra cứu"** để hiển thị bảng lịch học
7. **Quay lại terminal** và nhấn Enter
8. **Tool sẽ tự động**:
   - Phát hiện bảng lịch học
   - Crawl tất cả các trang
   - Xuất ra file Excel/JSON
   - Hiển thị thống kê

## 📁 Cấu trúc file output

### Excel File
```
lich_hoc_ulsa_YYYYMMDD_HHMMSS.xlsx
├── Sheet: "Lịch học"
└── Columns:
    ├── STT
    ├── Mã học phần  
    ├── Tên học phần
    ├── Số tín chỉ
    ├── Tên lớp tín chỉ
    ├── Ca học
    ├── Lịch học
    ├── Giảng viên
    ├── Phòng học
    ├── Còn trống
    ├── Ghi chú
    └── Ngày crawl
```

### JSON File
```json
[
  {
    "stt": 1,
    "maHocPhan": "ANHM1223L",
    "tenHocPhan": "An toàn và bảo mật hệ thống thông tin",
    "soTinChi": "3",
    "tenLop": "ANHM1223L_D18HQ.01_LT",
    "caHoc": "Sáng",
    "lichHoc": "Thứ 6(T1-5)",
    "giangVien": "Nguyễn Văn A",
    "phongHoc": "101",
    "conTrong": "17",
    "ghiChu": "",
    "ngayCrawl": "2025-07-12 18:30:45"
  }
]
```

## ⚙️ Tùy chọn nâng cao

### Python Version
```python
# Chạy headless (ẩn browser)
crawler = ULSAScheduleCrawler(headless=True)

# Chỉ định học kỳ cụ thể
crawler.run(semester="Đợt 1 Học kỳ 1 Năm học 2024-2025")

# Lưu cả Excel và JSON
crawler.run(save_excel=True, save_json=True)
```

### Node.js Version
```javascript
// Khởi tạo với options
const crawler = new ULSAScheduleCrawler({
    headless: true,
    timeout: 60000
});

// Chạy với options
await crawler.run({
    semester: "Đợt 1 Học kỳ 1 Năm học 2024-2025",
    saveExcel: true,
    saveJson: true
});
```

## 🐛 Troubleshooting

### Lỗi thường gặp

#### 1. Không tìm thấy bảng lịch học
```
❌ Không tìm thấy bảng lịch học
```
**Giải pháp:**
- Đảm bảo đã đăng nhập thành công
- Đã chọn học kỳ
- Đã nhấn nút "Tra cứu"
- Bảng đã hiển thị trên trang

#### 2. Browser đã bị đóng
```
NoSuchWindowException: target window already closed
```
**Giải pháp:**
- KHÔNG đóng browser khi tool đang chạy
- Chỉ thao tác trên trang web, không đóng tab/window

#### 3. Timeout
```
TimeoutException: Timeout waiting for element
```
**Giải pháp:**
- Kiểm tra kết nối internet
- Thử lại sau khi trang web ổn định
- Sử dụng enhanced version với timeout dài hơn

#### 4. Lỗi dependencies
```
ModuleNotFoundError: No module named 'selenium'
```
**Giải pháp:**
```bash
pip install selenium pandas openpyxl
```

### Kiểm tra phiên bản
```bash
python --version
pip list | findstr selenium
```

## 🔧 Files trong project

```
d:\lichhoc\
├── enhanced_crawler.py      # Phiên bản mạnh mẽ nhất (Khuyên dùng)
├── simple_crawler.py        # Phiên bản đơn giản
├── class_manager.html       # Tool quản lý lịch học
├── run_crawler.bat         # Menu launcher cho Windows
├── chromedriver.exe        # Chrome driver
├── README.md              # Hướng dẫn này
├── LICENSE.chromedriver   # License ChromeDriver
└── THIRD_PARTY_NOTICES.chromedriver
```

## 📝 Changelog

### v2.0.0 (2025-07-12)
- ✅ Cleaned up project structure
- ✅ Removed Node.js dependencies
- ✅ Enhanced Python version with colors and smart detection
- ✅ Updated batch launcher
- ✅ Improved error handling

### v1.0.0 (2025-07-12)
- ✅ Phiên bản đầu tiên
- ✅ Hỗ trợ Python và Node.js
- ✅ Auto pagination
- ✅ Excel/JSON export

## 🔧 Customization

### Thay đổi cấu trúc dữ liệu
Sửa function `extract_table_data()` để thay đổi:
- Tên cột
- Thứ tự cột  
- Xử lý dữ liệu

### Thêm selector mới
Thêm vào list `possible_table_ids` hoặc `possibleSelectors`:
```python
possible_table_ids = ["gvDSLopMo", "grd", "YOUR_NEW_ID"]
```

### Thay đổi format output
Sửa function `save_to_excel()` để:
- Thay đổi style
- Thêm chart
- Multiple sheets

## 📝 Changelog

### v1.0.0 (2025-07-12)
- ✅ Phiên bản đầu tiên
- ✅ Hỗ trợ Python và Node.js
- ✅ Auto pagination
- ✅ Excel/JSON export
- ✅ Error handling

## 📄 License

MIT License - Free to use and modify

## 👨‍💻 Author

Created by ULSA Student for ULSA Community

---

## 🆘 Hỗ trợ

Nếu gặp vấn đề, hãy:
1. Đọc kỹ hướng dẫn troubleshooting
2. Kiểm tra log errors
3. Thử chạy lại với browser visible (headless=false)
4. Liên hệ để được hỗ trợ

**Happy Crawling! 🚀**
