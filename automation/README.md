# ULSA University Login Automation

## Mô tả
Công cụ tự động hóa đăng nhập hệ thống sinh viên ULSA University.

## Yêu cầu hệ thống
- Windows 10/11
- Python 3.7+
- Google Chrome Browser
- Kết nối Internet

## Cài đặt

### Bước 1: Cài đặt Python
1. Tải Python từ: https://python.org/downloads/
2. Chọn "Add Python to PATH" khi cài đặt

### Bước 2: Cài đặt môi trường
1. Mở Command Prompt với quyền Administrator
2. Chạy file `setup.bat`:
```
setup.bat
```

### Bước 3: Chạy chương trình
```
run.bat
```

## Sử dụng

### 🚀 Phương pháp 1: Đăng nhập tự động (có thể bị chặn)
```
run.bat
```
- Chọn "1" để đăng nhập tự động
- Nhập tài khoản và mật khẩu
- Chờ kết quả

### 🖱️ Phương pháp 2: Hỗ trợ nhập thủ công (khuyến nghị)
```
run_simple.bat
```
- Nhập mã sinh viên và mật khẩu trong terminal
- Script sẽ mở trình duyệt đến trang đăng nhập
- Bạn tự nhập thông tin vào form trên web
- Phù hợp với các trang có chống automation

### 🔧 Phương pháp 3: Bypass anti-automation
```
python manual_input_login.py
```
- Script thông minh với khả năng bypass
- Nhiều phương pháp submit form
- Gõ phím giống như con người

## Tính năng

### ✅ Đã hoàn thành
- [x] Tự động khởi động ChromeDriver
- [x] Truy cập trang đăng nhập ULSA
- [x] Phân tích form đăng nhập
- [x] Đăng nhập tự động
- [x] Chụp ảnh màn hình
- [x] Xử lý lỗi chi tiết

### 🚧 Đang phát triển
- [ ] Lưu thông tin đăng nhập (mã hóa)
- [ ] Tự động điền thông tin từ lần trước
- [ ] Báo cáo chi tiết
- [ ] Giao diện đồ họa

## Cấu trúc thư mục
```
automation/
├── ulsa_auto_login.py          # Script chính (tự động)
├── manual_input_login.py       # Script bypass anti-automation
├── simple_login_helper.py      # Script hỗ trợ nhập thủ công
├── login_automation.py         # Script cơ bản
├── config.json                # Cấu hình
├── requirements.txt           # Thư viện Python
├── setup.bat                 # Cài đặt tự động
├── run.bat                   # Chạy script chính
├── run_simple.bat            # Chạy script đơn giản
├── run.ps1                   # Chạy bằng PowerShell
├── screenshots/              # Ảnh chụp màn hình
└── README.md                 # Hướng dẫn này
```

## Khắc phục sự cố

### Lỗi "ChromeDriver not found"
```bash
pip install webdriver-manager
```

### Lỗi "Permission denied"
- Chạy Command Prompt với quyền Administrator
- Tắt antivirus tạm thời

### Lỗi "Timeout"
- Kiểm tra kết nối internet
- Kiểm tra URL có chính xác không
- Tăng thời gian chờ trong script

### Lỗi "Module not found"
```bash
pip install -r requirements.txt
```

## Liên hệ hỗ trợ
- Email: support@example.com
- GitHub: https://github.com/username/ulsa-automation

## Bản quyền
© 2025 ULSA Automation Tool. All rights reserved.

## Cảnh báo
- Chỉ sử dụng với tài khoản hợp lệ của bạn
- Không chia sẻ thông tin đăng nhập
- Tuân thủ quy định của trường học
