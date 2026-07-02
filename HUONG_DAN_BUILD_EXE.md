# 🚀 HƯỚNG DẪN BUILD FILE .EXE - ULSA AUTOMATION

## 📋 MỤC ĐÍCH
Đóng gói tool đăng ký tín chỉ thành file .exe để:
- ✅ Không cần cài đặt Python
- ✅ Không cần cài đặt dependencies
- ✅ Chỉ cần click đúp là chạy
- ✅ Dễ chia sẻ cho bạn bè

---

## 🔧 CHUẨN BỊ (Chỉ cần làm 1 lần)

### 1. Cài đặt Python (nếu chưa có)
- Tải Python 3.8 - 3.11 tại: https://www.python.org/downloads/
- ⚠️ Quan trọng: Tick vào ô "Add Python to PATH" khi cài

### 2. Kiểm tra Python
Mở PowerShell và gõ:
```powershell
python --version
```
Phải hiện: `Python 3.x.x`

---

## 🏗️ CÁCH BUILD FILE .EXE

### Phương án 1: BUILD ĐẦY ĐỦ (Khuyến nghị)
```batch
# Click đúp vào file:
build_exe.bat
```

**Ưu điểm:**
- Bao gồm tất cả HTML templates
- Bao gồm folder automation với config
- File .exe to hơn (~200-300MB) nhưng đầy đủ chức năng

**Kết quả:**
- File: `dist\ULSA_DangKyTinChi.exe`

---

### Phương án 2: BUILD NHẸ
```batch
# Click đúp vào file:
build_exe_simple.bat
```

**Ưu điểm:**
- File .exe nhỏ hơn (~150-200MB)
- Tự tạo folder automation khi chạy lần đầu

**Nhược điểm:**
- Người dùng phải cấu hình lại từ đầu

---

### Phương án 3: BUILD TỰ DO (Advanced)
```powershell
# Kích hoạt môi trường ảo
.\.venv_build\Scripts\activate

# Cài PyInstaller
pip install pyinstaller

# Build bằng file .spec
pyinstaller complete_gui.spec
```

---

## 📦 SAU KHI BUILD XONG

### Kiểm tra file
```
webtruong4.1/
├── dist/
│   └── ULSA_DangKyTinChi.exe  ← File này gửi cho mọi người
├── build/                      ← Tạm thời, có thể xóa
└── complete_gui.spec           ← Config PyInstaller
```

### Test file .exe
1. Copy file `ULSA_DangKyTinChi.exe` ra Desktop
2. Click đúp để chạy
3. Kiểm tra các chức năng:
   - Nhập tài khoản
   - Chọn lớp
   - Đăng ký tín chỉ

---

## 📤 CHIA SẺ CHO NGƯỜI KHÁC

### Cách 1: Gửi file .exe đơn lẻ (Phương án 2)
- Chỉ cần gửi file `.exe`
- Người nhận click đúp là chạy
- Tự động tạo folder cấu hình

### Cách 2: Gửi kèm config (Phương án 1)
Nén các file sau thành .zip:
```
ULSA_Tool.zip
├── ULSA_DangKyTinChi.exe
└── automation/
    └── auto_config.json  (nếu muốn chia sẻ config)
```

---

## ⚠️ LƯU Ý QUAN TRỌNG

### Yêu cầu trên máy người dùng:
1. ✅ Windows 7/8/10/11 (64-bit)
2. ✅ Google Chrome đã cài đặt
3. ❌ KHÔNG cần Python
4. ❌ KHÔNG cần cài dependencies

### Kích thước file:
- File .exe: 150-300MB (tùy phương án)
- Nguyên nhân: Đóng gói Python runtime + tất cả thư viện

### Lần chạy đầu tiên:
- Có thể mất 10-30 giây để khởi động
- Windows Defender có thể cảnh báo (bình thường với .exe tự build)
- ChromeDriver tự động tải về

### Antivirus cảnh báo:
- File .exe tự build thường bị cảnh báo
- Giải pháp:
  1. Click "More info" → "Run anyway"
  2. Thêm vào whitelist
  3. Hoặc code sign (mất phí)

---

## 🐛 XỬ LÝ LỖI

### Lỗi: "Python not found"
```batch
# Cài Python và thêm vào PATH
# Rồi chạy lại build_exe.bat
```

### Lỗi: "Module not found"
```batch
# Cài đầy đủ dependencies
pip install -r requirements_full.txt
pip install pyinstaller

# Rồi chạy lại
```

### File .exe quá to (>500MB)
```python
# Edit file complete_gui.spec
# Thêm vào excludes:
excludes=[
    'matplotlib',
    'numpy',
    'scipy',
    'IPython',
    'PIL',
    'pytest',
],
```

### File .exe chạy chậm
- Lần đầu chậm là bình thường (giải nén runtime)
- Lần sau sẽ nhanh hơn
- Hoặc build dạng `--onedir` thay vì `--onefile`

---

## 🎯 BUILD NÂNG CAO

### Thêm icon cho .exe
1. Tạo/tải file `icon.ico`
2. Edit `build_exe.bat`, thay `--icon=NONE` thành:
   ```
   --icon=icon.ico
   ```

### Giảm kích thước
```batch
# Thêm UPX compression
pyinstaller complete_gui.spec --upx-dir=C:\upx
```

### Build dạng folder (nhanh hơn)
```batch
# Thay --onefile thành --onedir
# Kết quả: folder dist/ chứa nhiều file
```

---

## 📞 HỖ TRỢ

### Build thành công nhưng .exe không chạy?
1. Kiểm tra console error:
   ```batch
   # Build với console mode
   pyinstaller --onefile --console complete_gui.py
   ```
2. Xem lỗi trong cửa sổ console

### Thiếu file HTML/config?
- Kiểm tra lại phần `datas` trong `complete_gui.spec`
- Đảm bảo đường dẫn đúng

### Muốn test trước khi build?
```powershell
# Chạy trực tiếp bằng Python
python complete_gui.py
```

---

## ✅ CHECKLIST TRƯỚC KHI CHIA SẺ

- [ ] File .exe đã test trên máy mình
- [ ] File .exe đã test trên máy khác (không có Python)
- [ ] Đã test tất cả chức năng (login, chọn lớp, đăng ký)
- [ ] Đã kiểm tra ChromeDriver tự động tải
- [ ] Đã viết hướng dẫn sử dụng cho người nhận
- [ ] Đã nén .zip nếu cần gửi nhiều file

---

## 🎊 HOÀN THÀNH!

Giờ bạn có thể gửi file `.exe` cho bạn bè mà không lo về Python hay dependencies!

**Chúc bạn đăng ký tín chỉ thành công! 🎓**
