@echo off
chcp 65001 >nul
echo =========================================================
echo  REINSTALL PYTHON WITH TKINTER SUPPORT
echo =========================================================
echo.
echo [*] Starting reinstall process...
echo.

powershell.exe -ExecutionPolicy Bypass -File "%~dp0reinstall_python_with_tkinter.ps1"

echo.
echo [*] Done! You can close this window.
pause
