@echo off
chcp 65001 >nul
echo ============================================================
echo  TỰ ĐỘNG TẢI CHROMEDRIVER PHÙ HỢP VỚI CHROME
echo ============================================================
echo.
echo Script này sẽ:
echo  1. Kiểm tra phiên bản Chrome trên máy
echo  2. Tự động tải ChromeDriver tương ứng
echo  3. Cài đặt vào thư mục drivers/
echo.
pause
echo.

powershell -ExecutionPolicy Bypass -File download_chromedriver.ps1

echo.
echo ============================================================
pause
