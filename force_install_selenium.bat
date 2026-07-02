@echo off
echo === ALTERNATIVE SELENIUM INSTALLATION ===
cd /d "%~dp0automation"

echo.
echo Method 1: Install with --user flag (user-specific installation)
python -m pip install --user selenium webdriver-manager

echo.
echo Method 2: Install with --break-system-packages (override protection)
python -m pip install --break-system-packages selenium webdriver-manager

echo.
echo Method 3: Install specific version known to work
python -m pip install --user selenium==4.15.0 webdriver-manager==4.0.1

echo.
echo Testing selenium import:
python -c "import selenium; print('SUCCESS! Selenium version:', selenium.__version__)"

echo.
echo Starting ULSA Auto Login...
python auto_login_with_title_check.py

pause
