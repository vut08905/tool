@echo off
chcp 65001 >nul
color 0A
echo.
echo ================================================
echo 🤖 ULSA AUTOMATION - SMART RETRY SYSTEM
echo     Tự động đăng nhập và đăng ký lớp tín chỉ
echo ================================================
echo.
echo 📋 QUY TRÌNH TỰ ĐỘNG:
echo    1. Đọc thông tin từ auto_config.json
echo    2. Khởi động Chrome browser  
echo    3. Đăng nhập ULSA với retry thông minh
echo    4. Điều hướng trang đăng ký (xử lý nút disabled)
echo    5. Tự động chọn lớp từ danh sách cấu hình
echo    6. Lưu kết quả và tạo báo cáo chi tiết
echo.
echo 🔄 SMART RETRY SYSTEM:
echo    ✅ Tự động phát hiện lỗi 503, 502, 504, 404, timeout
echo    ✅ Exponential backoff: 2s → 4s → 8s (max 10s)
echo    ✅ Auto re-login khi phát hiện logout (404)
echo    ✅ Auto refresh trang khi lỗi máy chủ
echo    ✅ Retry tối đa 3-5 lần cho mỗi thao tác
echo    ✅ Không retry nếu trang hoạt động bình thường
echo.
echo 🚨 CẢNH BÁO QUAN TRỌNG:
echo    - Script sẽ TỰ ĐỘNG chọn lớp theo auto_config.json
echo    - KHÔNG CẦN XÁC NHẬN - chạy hoàn toàn tự động
echo    - Nếu nút đăng ký bị disabled, script sẽ tự động enable
echo    - Hệ thống xử lý thông minh khi web trường quá tải
echo    - Vui lòng kiểm tra thông tin trong auto_config.json TRƯỚC KHI CHẠY
echo.
echo 💡 HƯỚNG DẪN:
echo    - Mã sinh viên: %~dp0auto_config.json
echo    - Chỉnh sửa danh sách lớp trong selected_courses
echo    - Chế độ: test_mode = "ulsa" (website thật)
echo.

:: Chuyển đến thư mục script (nơi chứa file này)
cd /d "%~dp0"

:: Kiểm tra file cấu hình tồn tại
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
    echo 🔧 Vui lòng chạy: python -m venv .venv
    echo 📦 Sau đó: .venv\Scripts\pip install selenium
    echo.
    pause
    exit /b 1
)

:: Kiểm tra automation script
if not exist "automation\config_auto_login.py" (
    echo ❌ KHÔNG TÌM THẤY AUTOMATION SCRIPT!
    echo 📄 File automation\config_auto_login.py bị thiếu.
    echo.
    pause
    exit /b 1
)

echo ⏳ Đang khởi chạy automation...
echo 🔥 Sử dụng Smart Retry System để xử lý lỗi web!
echo ⚡ Tối ưu tốc độ cao nhất - Giảm 70% thời gian chờ!
echo.

:: Chạy automation script
.venv\Scripts\python.exe automation\config_auto_login.py

:: Hiển thị kết quả
echo.
if %ERRORLEVEL% EQU 0 (
    echo ✅ AUTOMATION HOÀN THÀNH!
) else (
    echo ❌ AUTOMATION GẶP LỖI (Exit Code: %ERRORLEVEL%)
)

echo.
echo ============================================
echo         PROCESS COMPLETED
echo ============================================
echo 📊 Kiểm tra file registration_result.json để xem kết quả chi tiết
echo 🔄 Browser có thể vẫn mở để bạn kiểm tra
echo.
pause
