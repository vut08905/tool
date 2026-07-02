@echo off
chcp 65001 >nul
echo =========================================================
echo  CHAY GUI TU SOURCE (KHONG CAN BUILD .EXE)
echo =========================================================
echo.

REM Tim Python
set PYTHON_EXE=

REM Thu tim trong .venv
if exist ".venv\Scripts\python.exe" (
    set PYTHON_EXE=.venv\Scripts\python.exe
    echo [OK] Su dung Python trong .venv
    goto :run
)

REM Thu Python trong system
python --version >nul 2>&1
if not errorlevel 1 (
    set PYTHON_EXE=python
    echo [OK] Su dung Python trong PATH
    goto :run
)

REM Thu Python launcher
py --version >nul 2>&1
if not errorlevel 1 (
    set PYTHON_EXE=py
    echo [OK] Su dung Python launcher
    goto :run
)

REM Thu Python 3.11 trong LocalAppData
set "PYTHON_PATH=%LOCALAPPDATA%\Programs\Python\Python311\python.exe"
if exist "%PYTHON_PATH%" (
    set PYTHON_EXE=%PYTHON_PATH%
    echo [OK] Su dung Python 3.11
    goto :run
)

REM Không tìm thấy Python nào
echo.
echo ========================================================
echo  ⚠️  CHUA TIM THAY PYTHON!
echo ========================================================
echo.
echo 💡 BAN CAN:
echo.
echo    1. Chay file: SETUP_FIRST_TIME.bat
echo       (Setup se tu dong tao .venv va cai Python)
echo.
echo    HOAC
echo.
echo    2. Cai Python vao he thong:
echo       https://www.python.org/downloads/
echo       Nho tick "Add Python to PATH"
echo.
echo ========================================================
echo.
echo 📖 Xem huong dan chi tiet trong: QUICK_START.txt
echo.
pause
exit /b 1

:run
echo.
echo [*] Dang khoi dong GUI...
echo.
"%PYTHON_EXE%" complete_gui.py

if errorlevel 1 (
    echo.
    echo [ERROR] Co loi khi chay!
    echo.
    pause
)
