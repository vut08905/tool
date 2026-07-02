# 🚀 Hướng Dẫn Về ChromeDriver

## 📌 ChromeDriver là gì?

ChromeDriver là công cụ cần thiết để automation điều khiển Chrome. Nó phải tương thích với phiên bản Chrome trên máy bạn.

## 🎯 Cách Sử Dụng

### ✅ Tự động tải (Khuyến nghị)

Chạy file:
```
DOWNLOAD_CHROMEDRIVER.bat
```

Script sẽ:
1. ✅ Tự động phát hiện phiên bản Chrome
2. 📥 Tải ChromeDriver phù hợp
3. 📦 Cài đặt vào thư mục `drivers/`

### 🔧 Tải thủ công

Nếu tải tự động không được:

1. **Kiểm tra phiên bản Chrome:**
   - Mở Chrome → Menu (⋮) → Help → About Google Chrome
   - Ghi nhớ version (VD: `145.0.7632.117`)

2. **Tải ChromeDriver:**
   - Vào: https://googlechromelabs.github.io/chrome-for-testing/
   - Tìm phiên bản tương ứng
   - Tải file `chromedriver-win64.zip`

3. **Cài đặt:**
   - Giải nén file ZIP
   - Copy `chromedriver.exe` vào thư mục `drivers/` trong project
   - Kết quả: `webtruong4.1/drivers/chromedriver.exe`

## 📁 Vị trí ChromeDriver

App sẽ tìm ChromeDriver theo thứ tự:
1. `automation/drivers/chromedriver.exe`
2. `drivers/chromedriver.exe` (trong thư mục gốc)
3. `automation/chromedriver.exe`
4. Nếu không có → tự động tải về

## ❗ Khắc Phục Lỗi

### Lỗi: "WinError 193"
**Nguyên nhân:** ChromeDriver không tương thích với Chrome

**Giải pháp:**
```batch
# Chạy file này để tải lại ChromeDriver đúng phiên bản
DOWNLOAD_CHROMEDRIVER.bat
```

### Lỗi: "Chrome version must be..."
**Nguyên nhân:** Chrome đã update nhưng ChromeDriver còn cũ

**Giải pháp:**
1. Xóa thư mục `drivers/`
2. Chạy lại `DOWNLOAD_CHROMEDRIVER.bat`

### Lỗi: Cannot download
**Nguyên nhân:** Lỗi mạng hoặc phiên bản Chrome quá mới

**Giải pháp:**
1. Kiểm tra kết nối Internet
2. Update Chrome lên bản mới nhất
3. Thử tải thủ công từ: https://googlechromelabs.github.io/chrome-for-testing/

## 🔄 Khi nào cần tải lại ChromeDriver?

- ✅ Chrome vừa được update lên phiên bản mới
- ✅ Gặp lỗi "session not created"
- ✅ Gặp lỗi "WinError 193"
- ✅ App báo "ChromeDriver không tương thích"

## 💡 Tips

1. **Chrome tự động update:** Chrome thường tự update, nhưng ChromeDriver không. Nếu app đột nhiên báo lỗi, hãy chạy lại `DOWNLOAD_CHROMEDRIVER.bat`

2. **Giữ ChromeDriver cập nhật:** Nên tải lại ChromeDriver sau mỗi lần Chrome update

3. **Backup:** Có thể backup file `chromedriver.exe` để dùng lại khi cần

## 🔗 Links Hữu Ích

- Chrome for Testing: https://googlechromelabs.github.io/chrome-for-testing/
- ChromeDriver Documentation: https://chromedriver.chromium.org/
- Download Chrome: https://www.google.com/chrome/
