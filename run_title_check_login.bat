@echo off
chcp 65001 >nul
color 0B
echo.
echo ================================================================
echo 🤖 ULSA AUTO LOGIN WITH TITLE CHECK
echo     Tự động reload trang → kiểm tra title → đăng nhập
echo ================================================================
echo.
echo 📋 QUY TRÌNH HOẠT ĐỘNG:
echo    1. Truy cập trang sinhvien.ulsa.edu.vn/Login.aspx
echo    2. Kiểm tra title của trang
echo    3. Nếu title = "sinhvien.ulsa.edu.vn" → RELOAD trang
echo    4. Nếu title = "Phần mềm quản lý đào tạo tín chỉ UniSoft - Thiên An" → DỪNG reload
echo    5. Tự động đăng nhập với thông tin từ auto_config.json
echo    6. RETRY SUBMIT form cho đến khi URL = http://sinhvien.ulsa.edu.vn/SinhVien.aspx?Chuyen_nganh=1
echo.
echo 🔄 TÍNH NĂNG RETRY SUBMIT + F5 THÔNG MINH (CẬP NHẬT MỚI):
echo    ✅ Tự động submit lại form khi chưa đăng nhập thành công
echo    ✅ Kiểm tra URL mục tiêu: SinhVien.aspx?Chuyen_nganh=1
echo    ✅ KHÔNG GIỚI HẠN số lần submit - chạy đến khi thành công
echo    ✅ Chờ trang load hoàn toàn (document.readyState = 'complete')
echo    ✅ SỬ DỤNG F5 REFRESH khi URL chưa đổi
echo    ✅ XỬ LÝ THÔNG BÁO BROWSER "Bạn có muốn tiếp tục không?"
echo    ✅ TỰ ĐỘNG CHUYỂN đến trang chọn lớp sau khi thành công
echo    ✅ Thời gian chờ cố định 3s sau mỗi submit
echo.
echo 🚨 THÔNG TIN QUAN TRỌNG:
echo    - Script sẽ sử dụng thông tin từ auto_config.json
echo    - Mã sinh viên: %~dp0auto_config.json
echo    - Tự động điền form và submit khi title đã đúng
echo    - Chụp ảnh màn hình để theo dõi quá trình
echo.

:: Chuyển đến thư mục script
cd /d "%~dp0"

:: Kiểm tra file cấu hình
if not exist "auto_config.json" (
    echo ❌ KHÔNG TÌM THẤY FILE auto_config.json!
    echo 📄 Vui lòng tạo file cấu hình với thông tin đăng nhập.
    echo.
    pause
    exit /b 1
)

:: Kiểm tra virtual environment
if not exist ".venv\Scripts\python.exe" (
    echo ❌ KHÔNG TÌM THẤY VIRTUAL ENVIRONMENT!
    echo 🔧 Đang tạo virtual environment...
    python -m venv .venv
    echo 📦 Đang cài đặt selenium...
    .venv\Scripts\pip install selenium webdriver-manager
)

:: Kiểm tra script
if not exist "automation\auto_login_with_title_check.py" (
    echo ❌ KHÔNG TÌM THẤY SCRIPT auto_login_with_title_check.py!
    echo 📄 File automation\auto_login_with_title_check.py bị thiếu.
    echo.
    pause
    exit /b 1
)

echo ⏳ Đang khởi chạy auto login with title check...
echo 🔄 Sẽ reload trang cho đến khi title đúng!
echo.

:: Chạy script
.venv\Scripts\python.exe automation\auto_login_with_title_check.py

:: Hiển thị kết quả
echo.
if %ERRORLEVEL% EQU 0 (
    echo ✅ AUTO LOGIN HOÀN THÀNH!
) else (
    echo ❌ AUTO LOGIN GẶP LỖI (Exit Code: %ERRORLEVEL%)
)

echo.
echo ================================================================
echo                    PROCESS COMPLETED
echo ================================================================
echo 📷 Kiểm tra thư mục screenshots/ để xem các ảnh chụp màn hình
echo 🌐 Browser có thể vẫn mở để bạn kiểm tra kết quả
echo.
pause
