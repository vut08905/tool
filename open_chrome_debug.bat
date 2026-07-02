@echo off
chcp 65001 >nul
echo ========================================
echo 🌐 Mở Chrome với Debugging Mode
echo ========================================
echo.
echo 📌 Cổng debug: 9222
echo 🔧 Chrome sẽ mở và cho phép script kết nối vào
echo.

REM Đóng tất cả Chrome đang chạy
echo 🔄 Đang đóng Chrome cũ...
taskkill /F /IM chrome.exe >nul 2>&1
timeout /t 2 /nobreak >nul

REM Mở Chrome với debugging port
echo ✅ Đang khởi động Chrome với debugging mode...
start "" "C:\Program Files\Google\Chrome\Application\chrome.exe" --remote-debugging-port=9222 --user-data-dir="%TEMP%\chrome_debug_profile" "http://sinhvien.ulsa.edu.vn/Login.aspx"

echo.
echo ========================================
echo ✅ Chrome đã được mở với debugging mode!
echo 📍 Đã mở trang: http://sinhvien.ulsa.edu.vn/Login.aspx
echo.
echo 👉 HƯỚNG DẪN TIẾP THEO:
echo    1. Đăng nhập vào trang web trên Chrome
echo    2. Mở GUI: python complete_gui.py
echo    3. Nhấn nút "Bắt đầu Automation"
echo    4. Script sẽ TỰ ĐỘNG kết nối vào Chrome này
echo       (KHÔNG mở Chrome mới nữa!)
echo ========================================
echo.
pause
