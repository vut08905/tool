@echo off
chcp 65001 >nul
echo ========================================
echo 🔨 BUILD FILE .EXE CHO ULSA AUTOMATION
echo ========================================
echo.

REM Kiểm tra Python có tồn tại không
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Không tìm thấy Python! Vui lòng cài đặt Python trước.
    echo 📥 Tải Python tại: https://www.python.org/downloads/
    pause
    exit /b 1
)

echo ✅ Đã tìm thấy Python
echo.

REM Kiểm tra/Tạo môi trường ảo
if not exist ".venv_build" (
    echo 📦 Tạo môi trường ảo mới...
    python -m venv .venv_build
) else (
    echo ✅ Môi trường ảo đã tồn tại
)

echo.
echo 🔧 Kích hoạt môi trường ảo...
call .venv_build\Scripts\activate.bat

echo.
echo 📥 Cài đặt dependencies...
python -m pip install --upgrade pip
pip install -r requirements_full.txt
pip install pyinstaller

echo.
echo 🏗️ Đang build file .exe...
echo Quá trình này có thể mất 2-5 phút...
echo.

pyinstaller --noconfirm --onefile --windowed ^
    --name "ULSA_DangKyTinChi" ^
    --icon=NONE ^
    --add-data "automation;automation" ^
    --add-data "b1.html;." ^
    --add-data "b11.html;." ^
    --add-data "b111.html;." ^
    --add-data "b2.html;." ^
    --add-data "b2_1.html;." ^
    --add-data "b22.html;." ^
    --add-data "b3.html;." ^
    --add-data "b33.html;." ^
    --hidden-import=pandas ^
    --hidden-import=fuzzywuzzy ^
    --hidden-import=selenium ^
    --hidden-import=webdriver_manager ^
    --collect-all selenium ^
    --collect-all webdriver_manager ^
    complete_gui.py

echo.
if exist "dist\ULSA_DangKyTinChi.exe" (
    echo ========================================
    echo ✅ BUILD THÀNH CÔNG!
    echo ========================================
    echo.
    echo 📁 File .exe được tạo tại:
    echo    %CD%\dist\ULSA_DangKyTinChi.exe
    echo.
    echo 📊 Kích thước file:
    dir "dist\ULSA_DangKyTinChi.exe" | find "ULSA_DangKyTinChi.exe"
    echo.
    echo 📤 Bạn có thể gửi file này cho người khác để chạy
    echo    mà không cần cài đặt Python!
    echo.
    echo 💡 Lưu ý:
    echo    - File .exe chỉ chạy được trên Windows
    echo    - Người dùng vẫn cần có Chrome đã cài đặt
    echo    - Chromedriver sẽ tự động tải về khi chạy lần đầu
    echo.
) else (
    echo ❌ BUILD THẤT BẠI! Vui lòng kiểm tra lỗi ở trên.
)

echo.
pause
