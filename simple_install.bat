@echo off
cd /d "%~dp0"
echo ================================================
echo     🚀 ULSA AUTO REGISTRATION - QUICK START 🚀
echo ================================================
echo.
echo [INFO] Dang chay tool dang ky tin chi ULSA...
echo [INFO] Su dung strategy RELOAD PAGE moi
echo [INFO] Khong submit form ma chi reload lien tuc
echo.

if exist "%~dp0.venv\Scripts\python.exe" (
    echo [OK] Su dung Python tu virtual environment
    "%~dp0.venv\Scripts\python.exe" automation\auto_login_with_title_check.py
) else (
    echo [WARNING] Khong tim thay virtual environment
    echo [INFO] Thu cai dat dependencies...
    pip install selenium webdriver-manager
    python automation\auto_login_with_title_check.py
)

echo.
echo ============================================
echo         🎉 TOOL COMPLETED 🎉
echo ============================================
pause
