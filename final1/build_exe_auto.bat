@echo off
chcp 65001 >nul
echo ========================================
echo 🔨 BUILD FILE .EXE - ULSA AUTOMATION
echo ========================================
echo.

REM Thử python từ PATH
python --version >nul 2>&1
if not errorlevel 1 (
    set PYTHON_EXE=python
    echo ✅ Tìm thấy Python trong PATH
    goto :found_python
)

REM Không tìm thấy Python
echo ❌ KHÔNG TÌM THẤY PYTHON!
echo.
echo 📥 Vui lòng:
echo   1. Cài Python: https://www.python.org/downloads/
echo   2. Tick vao "Add Python to PATH" khi cai.
echo.
pause
exit /b 1

:found_python
echo Khởi chạy bằng: %PYTHON_EXE%
echo.

echo 📦 Cài đặt/Nâng cấp thư viện cần thiết...
%PYTHON_EXE% -m pip install --upgrade pip pyinstaller requests qrcode pillow selenium --quiet

echo.
echo 🏗️ Đang tiến hành đóng gói file .EXE...
echo ⏳ Quá trình này mất 2-5 phút, có thể màn hình sẽ đứng yên, xin tuyệt đối kiên nhẫn...
echo.

%PYTHON_EXE% -m PyInstaller --clean -y dangkytinchiulsa.spec

echo.
if exist "dist\dangkytinchiulsa.exe" (
    echo ========================================
    echo ✅✅✅ ĐÓNG GÓI THÀNH CÔNG! ✅✅✅
    echo ========================================
    echo.
    echo 📁 File .exe của bạn được tạo tại:
    echo    %CD%\dist\dangkytinchiulsa.exe
    echo.
    echo 💡 BÂY GIỜ BẠN CÓ THỂ:
    echo    Đem file này đi chia sẻ hoặc update lên Link Gist Cloud.
    echo.
) else (
    echo ========================================
    echo ❌ ĐÓNG GÓI THẤT BẠI!
    echo ========================================
    echo.
    echo 🔍 Kiểm tra xem bạn có đang Bật/Mở file exe cũ không. Nếu có hãy tắt nó đi.
    echo.
)

pause

