@echo off
echo === CHECKING PYTHON SETUP ===
cd /d "%~dp0automation"

echo.
echo 1. Python version:
python --version

echo.
echo 2. Pip version:
python -m pip --version

echo.
echo 3. Trying to install selenium with verbose output:
python -m pip install selenium --verbose

echo.
echo 4. Checking if selenium is installed:
python -c "import selenium; print('SUCCESS: Selenium version:', selenium.__version__)" 2>nul || echo "FAILED: Selenium not installed"

echo.
echo 5. List installed packages:
python -m pip list | findstr selenium

pause
