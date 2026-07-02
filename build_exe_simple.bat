@echo off
chcp 65001 >nul
echo ========================================
echo 🚀 BUILD FILE .EXE - PHIÊN BẢN NHẸ
echo (Không bao gồm automation folder)
echo ========================================
echo.

REM Kiểm tra Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Không tìm thấy Python!
    pause
    exit /b 1
)

echo ✅ Đã tìm thấy Python
echo.

REM Tạo/Kích hoạt môi trường ảo
if not exist ".venv_build" (
    echo 📦 Tạo môi trường ảo...
    python -m venv .venv_build
)

call .venv_build\Scripts\activate.bat

echo 📥 Cài đặt dependencies...
pip install --upgrade pip >nul
pip install -r requirements_full.txt
pip install pyinstaller

echo.
echo 🏗️ Đang build file .exe (ONEFILE - dễ chia sẻ)...
echo.

pyinstaller --noconfirm --onefile --windowed ^
    --name "ULSA_DangKyTinChi_Simple" ^
    --hidden-import=pandas ^
    --hidden-import=fuzzywuzzy ^
    --hidden-import=selenium ^
    --hidden-import=webdriver_manager ^
    --collect-all selenium ^
    --collect-all webdriver_manager ^
    complete_gui.py

echo.
if exist "dist\ULSA_DangKyTinChi_Simple.exe" (
    echo ========================================
    echo ✅ BUILD THÀNH CÔNG!
    echo ========================================
    echo.
    echo 📁 File: dist\ULSA_DangKyTinChi_Simple.exe
    echo.
    echo 💡 Lưu ý:
    echo    - Lần chạy đầu tiên sẽ tạo folder "automation" tự động
    echo    - Người dùng cần nhập lại config
    echo.
) else (
    echo ❌ BUILD THẤT BẠI!
)

pause
