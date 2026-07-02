@echo off
chcp 65001 >nul
echo ========================================
echo 🔨 BUILD FILE .EXE - TỰ ĐỘNG TÌM PYTHON
echo ========================================
echo.

REM Tìm Python trong môi trường ảo hiện tại
set PYTHON_EXE=

if exist ".venv\Scripts\python.exe" (
    set PYTHON_EXE=.venv\Scripts\python.exe
    echo ✅ Tìm thấy Python trong .venv
    goto :found_python
)

if exist ".venv_build\Scripts\python.exe" (
    set PYTHON_EXE=.venv_build\Scripts\python.exe
    echo ✅ Tìm thấy Python trong .venv_build
    goto :found_python
)

REM Thử python từ PATH
python --version >nul 2>&1
if not errorlevel 1 (
    set PYTHON_EXE=python
    echo ✅ Tìm thấy Python trong PATH
    goto :found_python
)

REM Thử py launcher
py --version >nul 2>&1
if not errorlevel 1 (
    set PYTHON_EXE=py
    echo ✅ Tìm thấy Python launcher (py)
    goto :found_python
)

REM Không tìm thấy Python
echo ❌ KHÔNG TÌM THẤY PYTHON!
echo.
echo 📥 Vui lòng:
echo   1. Cài Python: https://www.python.org/downloads/
echo   2. Hoặc tạo venv: python -m venv .venv
echo.
pause
exit /b 1

:found_python
echo Python: %PYTHON_EXE%
echo.

REM Kiểm tra phiên bản
echo 🔍 Kiểm tra phiên bản Python...
%PYTHON_EXE% --version

echo.
echo 📦 Cài đặt/Nâng cấp pip...
%PYTHON_EXE% -m pip install --upgrade pip --quiet

echo.
echo 📥 Cài đặt PyInstaller và dependencies...
%PYTHON_EXE% -m pip install pyinstaller --quiet
%PYTHON_EXE% -m pip install -r requirements_full.txt --quiet

echo.
echo 🏗️ Đang build file .EXE...
echo ⏳ Quá trình này mất 2-5 phút, xin kiên nhẫn...
echo.

%PYTHON_EXE% -m PyInstaller --noconfirm --clean complete_gui.spec

echo.
if exist "dist\ULSA_DangKyTinChi.exe" (
    echo ========================================
    echo ✅✅✅ BUILD THÀNH CÔNG! ✅✅✅
    echo ========================================
    echo.
    echo 📁 File .exe được tạo tại:
    echo    %CD%\dist\ULSA_DangKyTinChi.exe
    echo.
    for %%F in ("dist\ULSA_DangKyTinChi.exe") do echo 📊 Kích thước: %%~zF bytes (~%%~zF:~0,-6% MB^)
    echo.
    echo 💡 BÂY GIỜ BẠN CÓ THỂ:
    echo    1. Copy file .exe ra Desktop để test
    echo    2. Gửi file này cho bạn bè
    echo    3. Người nhận chỉ cần click đúp là chạy!
    echo.
    echo ⚠️ LƯU Ý:
    echo    - Người dùng cần có Chrome đã cài
    echo    - Lần đầu chạy hơi lâu (10-30s) là bình thường
    echo    - Windows cảnh báo → Click "Run anyway"
    echo.
) else (
    echo ========================================
    echo ❌ BUILD THẤT BẠI!
    echo ========================================
    echo.
    echo 🔍 Kiểm tra lỗi ở trên và thử:
    echo    1. Xóa folder build/ và dist/
    echo    2. Chạy lại script này
    echo    3. Đọc HUONG_DAN_BUILD_EXE.md để biết chi tiết
    echo.
)

pause
