@echo off
echo Trying to install selenium with system Python...
cd /d "%~dp0automation"

echo Method 1: Try with system Python
python -m pip install --user selenium webdriver-manager

echo.
echo Method 2: Try with MSYS2 pacman
pacman -S --noconfirm mingw-w64-ucrt-x86_64-python-selenium

echo.
echo Starting ULSA Auto Login with system Python...
python auto_login_with_title_check.py
pause
