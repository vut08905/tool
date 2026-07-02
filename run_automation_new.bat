@echo off
echo ================================================
echo  ULSA AUTOMATION - CHAY TU DONG DANG KY MON HOC
echo ================================================
echo.

cd /d "%~dp0"
echo Current directory: %CD%
echo.

echo Checking virtual environment...
if exist .venv\Scripts\python.exe (
    echo ✅ Found virtual environment
    echo.
    echo Starting automation with NEW SUBJECTS:
    echo - VĩMO0523H_D20QL
    echo - KNGT0322H_D19TL
    echo.
    .venv\Scripts\python.exe automation\auto_login_with_title_check.py
) else (
    echo ❌ Virtual environment not found!
    echo Trying system Python...
    python automation\auto_login_with_title_check.py
)

echo.
echo ================================================
echo  AUTOMATION COMPLETED
echo ================================================
pause
