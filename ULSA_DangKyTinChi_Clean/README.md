# 🎓 ULSA - CÔNG CỤ ĐĂNG KÝ TÍN CHỈ TỰ ĐỘNG

## 📋 Giới Thiệu

Tool tự động đăng ký tín chỉ cho sinh viên ULSA với giao diện đồ họa thân thiện.

## 🚀 Hướng Dẫn Sử Dụng Nhanh

### ⚡ Bước 1: Cài Đặt Python & Dependencies

**Chạy file:**
```
SETUP_FIRST_TIME.bat
```

Script sẽ tự động:
- ✅ Kiểm tra Python
- ✅ Tạo virtual environment
- ✅ Cài đặt tất cả dependencies

### 🌐 Bước 2: Cài Đặt ChromeDriver

**Chạy file:**
```
DOWNLOAD_CHROMEDRIVER.bat
```

Script sẽ tự động tải ChromeDriver phù hợp với phiên bản Chrome của bạn.

### ▶️ Bước 3: Chạy Tool

**Chạy file:**
```
RUN_GUI.bat
```

## 📁 Cấu Trúc Thư Mục

```
ULSA_DangKyTinChi_Clean/
├── RUN_GUI.bat                    # ▶️ File chạy chính
├── complete_gui.py                # 💻 Code GUI
├── requirements_full.txt          # 📦 Danh sách dependencies
├── SETUP_FIRST_TIME.bat          # 🔧 Setup lần đầu
├── DOWNLOAD_CHROMEDRIVER.bat     # 📥 Tải ChromeDriver
├── download_chromedriver.ps1     # 📥 Script PowerShell
├── automation/                    # 🤖 Thư mục automation
│   ├── auto_config.json          # ⚙️ File config
│   ├── auto_login_with_title_check.py
│   ├── config_auto_login.py
│   └── ...
└── drivers/                       # 🚗 Thư mục ChromeDriver
    ├── chromedriver.exe          # ChromeDriver
    └── README.md                 # Hướng dẫn
```

## ⚙️ Cấu Hình

Chỉnh sửa file cấu hình tại:
```
automation/auto_config.json
```

**Cấu trúc config:**
```json
{
  "login_info": {
    "student_id": "SV123456",
    "password": "your_password"
  },
  "registration": {
    "subjects": [
      {
        "subject_code": "IT101",
        "class_code": "IT101_01"
      }
    ]
  }
}
```

## 🔧 Khắc Phục Lỗi

### ❌ Lỗi: Không tìm thấy Python
**Giải pháp:**
1. Tải Python tại: https://www.python.org/downloads/
2. Cài đặt và tick vào "Add Python to PATH"
3. Chạy lại `SETUP_FIRST_TIME.bat`

### ❌ Lỗi: ChromeDriver không tương thích
**Giải pháp:**
1. Chạy lại `DOWNLOAD_CHROMEDRIVER.bat`
2. Script sẽ tự động tải phiên bản đúng

### ❌ Lỗi: Chrome không mở được
**Giải pháp:**
1. Cập nhật Chrome lên phiên bản mới nhất
2. Chạy lại `DOWNLOAD_CHROMEDRIVER.bat`
3. Khởi động lại tool

## 💡 Tips & Tricks

### 🎯 Đăng ký nhiều môn cùng lúc
Thêm nhiều môn học vào `auto_config.json`:
```json
"subjects": [
  {"subject_code": "IT101", "class_code": "IT101_01"},
  {"subject_code": "IT102", "class_code": "IT102_01"},
  {"subject_code": "IT103", "class_code": "IT103_01"}
]
```

### 🔄 Chạy đồng thời nhiều tài khoản
1. Copy thư mục này với tên khác
2. Chỉnh sửa `auto_config.json` với thông tin khác
3. Chạy cả 2 folder cùng lúc

### 📸 Xem ảnh chụp màn hình
Screenshots tự động lưu tại:
```
automation/screenshots/
```

## 🆘 Hỗ Trợ

### Các file quan trọng:
- 📁 `automation/auto_config.json` - Cấu hình chính
- 📁 `automation/screenshots/` - Ảnh chụp màn hình
- 📁 `drivers/chromedriver.exe` - ChromeDriver

### Xóa và cài lại:
```batch
# Xóa virtual environment cũ
rmdir /s /q .venv

# Chạy lại setup
SETUP_FIRST_TIME.bat
```

## 📝 Ghi Chú

- ✅ Tool hoàn toàn portable, có thể copy sang máy khác
- ✅ Không cần cài đặt vào System
- ✅ Tất cả chạy trong thư mục riêng
- ✅ An toàn với dữ liệu cá nhân

## 🔒 Bảo Mật

- ⚠️ Không chia sẻ file `auto_config.json` (chứa mật khẩu)
- ⚠️ Mật khẩu lưu dạng plain text, hãy bảo vệ file config
- 💡 Khuyến nghị: Đổi mật khẩu định kỳ

## 📜 License

Tool này được tạo ra để hỗ trợ sinh viên ULSA. Sử dụng hợp lý và có trách nhiệm.

---

**Version:** 4.1  
**Last Updated:** February 2026  
**Author:** webtruong4.1 Team
