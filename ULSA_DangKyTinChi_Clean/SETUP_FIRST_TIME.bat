@echo off
chcp 65001 >nul
echo ============================================================
echo  🔧 SETUP LẦN ĐẦU - ULSA ĐĂNG KÝ TÍN CHỈ
echo ============================================================
echo.
echo Script này sẽ:
echo  1. Kiểm tra Python đã cài chưa
echo  2. Tạo virtual environment (.venv)
echo  3. Cài đặt tất cả dependencies cần thiết
echo.
echo ⏳ Quá trình có thể mất 2-5 phút...
echo.
pause
echo.

REM Kiểm tra Python
echo [BƯỚC 1/3] Kiểm tra Python...
echo.

py --version >nul 2>&1
if errorlevel 1 (
    python --version >nul 2>&1
    if errorlevel 1 (
        echo ❌ KHÔNG TÌM THẤY PYTHON!
        echo.
        echo 📥 Vui lòng tải và cài đặt Python tại:
        echo    https://www.python.org/downloads/
        echo.
        echo 💡 Lưu ý: Khi cài hãy tick vào "Add Python to PATH"
        echo.
        pause
        exit /b 1
    ) else (
        set PYTHON_CMD=python
    )
) else (
    set PYTHON_CMD=py
)

echo ✅ Đã tìm thấy Python!
%PYTHON_CMD% --version
echo.

REM Xóa .venv cũ nếu có
if exist ".venv" (
    echo [CẢNH BÁO] Phát hiện .venv cũ
    echo.
    choice /C YN /M "Bạn có muốn xóa và tạo lại không? (Y/N)"
    if errorlevel 2 (
        echo.
        echo ⏭️  Giữ .venv cũ, bỏ qua bước tạo mới
        goto :install_deps
    )
    echo.
    echo 🗑️  Đang xóa .venv cũ...
    rmdir /s /q .venv
    echo ✅ Đã xóa .venv cũ
    echo.
)

REM Tạo virtual environment
echo [BƯỚC 2/3] Tạo virtual environment...
echo.
%PYTHON_CMD% -m venv .venv
if errorlevel 1 (
    echo ❌ Lỗi tạo virtual environment!
    echo.
    echo 💡 Thử cài venv:
    echo    %PYTHON_CMD% -m pip install virtualenv
    echo.
    pause
    exit /b 1
)
echo ✅ Đã tạo .venv thành công!
echo.

:install_deps
REM Cài đặt dependencies
echo [BƯỚC 3/3] Cài đặt dependencies...
echo.
echo ⏳ Đang cài đặt... (có thể mất vài phút)
echo.

.venv\Scripts\python.exe -m pip install --upgrade pip >nul 2>&1
.venv\Scripts\python.exe -m pip install -r requirements_full.txt

if errorlevel 1 (
    echo.
    echo ❌ Lỗi cài đặt dependencies!
    echo.
    echo 💡 Thử chạy thủ công:
    echo    .venv\Scripts\python.exe -m pip install -r requirements_full.txt
    echo.
    pause
    exit /b 1
)

echo.
echo ============================================================
echo  ✅ HOÀN TẤT SETUP!
echo ============================================================
echo.
echo 🎉 Tool đã sẵn sàng sử dụng!
echo.
echo 📌 BƯỚC TIẾP THEO:
echo    1. Chạy DOWNLOAD_CHROMEDRIVER.bat để tải ChromeDriver
echo    2. Chỉnh sửa automation\auto_config.json với thông tin của bạn
echo    3. Chạy RUN_GUI.bat để bắt đầu
echo.
echo ============================================================
pause
