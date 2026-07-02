@echo off
chcp 65001 >nul
color 0C
echo.
echo ════════════════════════════════════════════════════════════════════
echo.
echo    ⚠️  CẢNH BÁO: BẠN CHƯA CHẠY SETUP!
echo.
echo ════════════════════════════════════════════════════════════════════
echo.
echo 📌 LÝ DO BẠN ĐANG THẤY THÔNG BÁO NÀY:
echo.
echo    Tool phát hiện bạn chưa chạy setup lần đầu tiên
echo.
echo ════════════════════════════════════════════════════════════════════
echo.
echo ✅ HÃY LÀM THEO CÁC BƯỚC SAU:
echo.
echo    BƯỚC 1: Chạy setup (CHỈ LÀM 1 LẦN)
echo    -----------------------------------
echo.
echo       👉 Click vào file: SETUP_FIRST_TIME.bat
echo.
echo       ⏳ Chờ ~2-5 phút để cài đặt
echo.
echo.
echo    BƯỚC 2: Tải ChromeDriver (CHỈ LÀM 1 LẦN)
echo    -----------------------------------------
echo.
echo       👉 Click vào file: DOWNLOAD_CHROMEDRIVER.bat
echo.
echo       ⏳ Chờ tải xong
echo.
echo.
echo    BƯỚC 3: Chạy tool
echo    -----------------
echo.
echo       👉 Click vào file: RUN_GUI.bat
echo.
echo       🎉 Tool sẽ hoạt động!
echo.
echo ════════════════════════════════════════════════════════════════════
echo.
echo 💡 CHỈ CẦN SETUP 1 LẦN DUY NHẤT
echo.
echo    • Các lần sau chỉ cần chạy RUN_GUI.bat
echo    • Không cần setup lại trừ khi:
echo      - Xóa thư mục .venv
echo      - Copy sang máy mới
echo.
echo ════════════════════════════════════════════════════════════════════
echo.
pause
exit /b 0
