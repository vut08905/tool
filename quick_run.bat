@echo off
cd /d "%~dp0automation"
echo Starting ULSA Auto Login...
.\venv\bin\python.exe auto_login_with_title_check.py
pause
