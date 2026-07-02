@echo off
echo Installing selenium...
cd /d "%~dp0automation"
.\venv\bin\python.exe -m pip install selenium webdriver-manager
echo.
echo Installation complete! Starting ULSA Auto Login...
.\venv\bin\python.exe auto_login_with_title_check.py
pause
