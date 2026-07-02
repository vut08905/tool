@echo off
echo Installing selenium with pre-built wheels...
cd /d "%~dp0automation"

echo Upgrading pip first...
.\venv\bin\python.exe -m pip install --upgrade pip

echo Installing selenium with --only-binary option...
.\venv\bin\python.exe -m pip install --only-binary=all selenium webdriver-manager

echo.
echo Installation complete! Starting ULSA Auto Login...
.\venv\bin\python.exe auto_login_with_title_check.py
pause
