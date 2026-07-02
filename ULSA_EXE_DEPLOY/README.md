# 🎓 ULSA Đăng Ký Tín Chỉ Tự Động

Tool tự động hóa việc đăng ký học phần trên hệ thống ULSA, giúp sinh viên đăng ký nhanh chóng và không bị trễ.

## ⚡ Quick Start

### 1. Cài đặt Chrome
```bash
# Tải và cài Chrome (nếu chưa có)
https://www.google.com/chrome/
```

### 2. Tải ChromeDriver
```bash
# Double click file này để tự động tải ChromeDriver
DOWNLOAD_CHROMEDRIVER.bat
```

### 3. Cấu hình
Mở file `automation\auto_config.json` và điền thông tin:
```json
{
    "login": {
        "username": "MSSV_CUA_BAN",
        "password": "MATKHAU_CUA_BAN"
    },
    "registration": {
        "course_codes": ["DHMT13201", "CNXH03202"],
        "use_primary_schedule": true,
        "retry_count": 3,
        "delay_between_retries": 2
    }
}
```

### 4. Chạy Tool
```bash
# Double click file này
ULSA_DangKyTinChi.exe
```

## 📦 Nội Dung Package

```
ULSA_EXE_DEPLOY/
├── ULSA_DangKyTinChi.exe          ← File chính (46MB)
├── DOWNLOAD_CHROMEDRIVER.bat      ← Script tải ChromeDriver
├── download_chromedriver.ps1      ← Script PowerShell hỗ trợ
├── HUONG_DAN_SU_DUNG.txt          ← Hướng dẫn chi tiết (tiếng Việt)
├── README.md                      ← File này
├── automation/
│   ├── auto_config.json          ← File cấu hình
│   └── ...                       ← Scripts automation
├── drivers/
│   └── README.md                 ← Hướng dẫn ChromeDriver
└── *.html                        ← Files giao diện

```

## 🔧 Yêu Cầu Hệ Thống

- ✅ **Windows 10/11**
- ✅ **Google Chrome** (phiên bản mới nhất)
- ✅ **Kết nối Internet** ổn định

**KHÔNG CẦN:**
- ❌ Python
- ❌ Bất kỳ thư viện nào khác
- ❌ Kiến thức lập trình

## 🚀 Các Tính Năng

### ✨ Tự động đăng nhập
- Lưu thông tin đăng nhập an toàn
- Tự động điền form và login

### ✨ Đăng ký học phần
- Đăng ký nhiều môn cùng lúc
- Tự động retry nếu lỗi
- Xử lý trùng lịch thông minh

### ✨ Tra cứu thông tin
- Lịch học
- Học phí
- Điểm thi
- Thông tin sinh viên

### ✨ Giao diện thân thiện
- GUI dễ sử dụng
- Không cần viết code
- Hiển thị log chi tiết

## 💡 Ví Dụ Sử Dụng

### Đăng ký tự động khi mở đợt đăng ký

1. **Chuẩn bị trước:**
   - Cấu hình `auto_config.json` với các môn muốn đăng ký
   - Đảm bảo Chrome đã update

2. **Khi đến giờ mở đăng ký:**
   - Double click `ULSA_DangKyTinChi.exe`
   - Tool tự động login và đăng ký
   - Hoàn thành trong vài giây

3. **Kiểm tra kết quả:**
   - Xem file `registration_result.json`
   - Hoặc check trên web ULSA

## 🐛 Khắc Phục Sự Cố

### Lỗi: "Không tìm thấy ChromeDriver"
```bash
# Chạy lại script tải ChromeDriver
DOWNLOAD_CHROMEDRIVER.bat
```

### Lỗi: "Không kết nối được Chrome"
```bash
# 1. Update Chrome:
#    Menu → Help → About Google Chrome → Đợi update
# 2. Tải lại ChromeDriver:
DOWNLOAD_CHROMEDRIVER.bat
# 3. Khởi động lại máy
```

### Lỗi: "Windows Protected"
```
1. Click "More info"
2. Click "Run anyway"

HOẶC:

Chuột phải file .exe → Properties → Unblock → OK
```

### Lỗi: "Đăng nhập thất bại"
```
1. Kiểm tra username/password trong auto_config.json
2. Thử đăng nhập thủ công trên web ULSA
3. Đảm bảo Internet ổn định
```

## 📝 Cấu Hình Chi Tiết

### File: `automation/auto_config.json`

```jsonc
{
    "login": {
        "username": "2001234567",        // MSSV của bạn
        "password": "MatKhau@123"        // Mật khẩu ULSA
    },
    "registration": {
        "course_codes": [                // Danh sách mã học phần
            "DHMT13201",
            "CNXH03202",
            "KTTH01102"
        ],
        "use_primary_schedule": true,    // true = đăng ký lớp đầu tiên
        "retry_count": 3,                // Số lần thử lại nếu lỗi
        "delay_between_retries": 2       // Đợi 2 giây giữa các lần thử
    },
    "options": {
        "headless": false,               // true = chạy ngầm không hiện Chrome
        "screenshot_on_error": true,     // Chụp màn hình khi lỗi
        "log_level": "INFO"              // DEBUG, INFO, WARNING, ERROR
    }
}
```

## 🔒 Bảo Mật

- ⚠️ **QUAN TRỌNG:** File `auto_config.json` chứa mật khẩu của bạn
- 🔐 **Không chia sẻ** file này cho người khác
- 💾 **Lưu ý:** Mật khẩu được lưu dạng plain text (không mã hóa)
- 🔑 **Khuyến nghị:** Đổi mật khẩu định kỳ

## 📦 Cách Chia Sẻ Tool Cho Bạn Bè

### Gửi toàn bộ thư mục này

```
ULSA_EXE_DEPLOY/  ← Nén và gửi thư mục này
```

### Người nhận cần làm:

1. Giải nén thư mục
2. Cài Chrome (nếu chưa có)
3. Chạy `DOWNLOAD_CHROMEDRIVER.bat`
4. Cấu hình `automation\auto_config.json`
5. Chạy `ULSA_DangKyTinChi.exe`

## 🎯 Các File Quan Trọng

| File | Mục đích |
|------|----------|
| `ULSA_DangKyTinChi.exe` | File chính, chạy tool |
| `AUTO_CONFIG.json` | Cấu hình thông tin đăng ký |
| `DOWNLOAD_CHROMEDRIVER.bat` | Tải ChromeDriver tự động |
| `registration_result.json` | Kết quả đăng ký gần nhất |
| `HUONG_DAN_SU_DUNG.txt` | Hướng dẫn chi tiết tiếng Việt |

## ⚖️ Điều Khoản Sử Dụng

- ⚠️ Tool này **chỉ dành cho mục đích học tập** và hỗ trợ sinh viên
- ⚠️ **Không sử dụng** để spam hoặc gây hại hệ thống ULSA
- ⚠️ Người dùng **tự chịu trách nhiệm** về việc sử dụng tool
- ⚠️ **Không chia sẻ** thông tin đăng nhập cho người khác

## 📞 Hỗ Trợ

### Xem log chi tiết:
```bash
# Mở Command Prompt tại thư mục tool
# Gõ lệnh:
ULSA_DangKyTinChi.exe

# Log sẽ hiển thị chi tiết trên màn hình
```

### Các file log:
- `registration_result.json` - Kết quả đăng ký
- `screenshots/` - Ảnh chụp màn hình khi lỗi (nếu có)

## 🚀 Tips & Tricks

### 1. Đăng ký siêu nhanh
- Chuẩn bị `auto_config.json` trước
- Test thử trước 1 giờ
- Khi đến giờ: chạy .exe, tool tự động làm hết

### 2. Đăng ký nhiều môn
- Thêm tất cả mã môn vào `course_codes`
- Tool sẽ đăng ký tuần tự
- Tự động xử lý trùng lịch

### 3. Backup cấu hình
```bash
# Copy thư mục automation/ sang USB
# Khi cần: paste lại và dùng ngay
```

### 4. Chạy trên nhiều máy
- Copy toàn bộ thư mục `ULSA_EXE_DEPLOY/`
- Paste vào máy khác
- Chạy `DOWNLOAD_CHROMEDRIVER.bat` (chỉ lần đầu)
- Sẵn sàng sử dụng

## 🎓 Chúc Bạn Đăng Ký Thành Công!

Nếu tool hữu ích, hãy chia sẻ cho bạn bè cùng sử dụng! 🚀

---

**Version:** 1.0  
**Build date:** February 2026  
**Compatible:** Windows 10/11, Chrome 90+
