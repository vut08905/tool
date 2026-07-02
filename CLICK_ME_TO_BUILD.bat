@echo off
chcp 65001 >nul
echo.
echo =========================================================
echo.
echo    CLICK VAO DAY DE TU DONG BUILD FILE .EXE
echo.
echo    Script se tu dong:
echo    - Kiem tra Python
echo    - Tai va cai Python neu chua co
echo    - Cai dat tat ca dependencies  
echo    - Build file .exe
echo.
echo    Khong can lam gi ca, chi ngoi cho thoi!
echo.
echo =========================================================
echo.
echo [*] Dang khoi dong script tu dong...
echo.
timeout /t 2 /nobreak >nul

REM Chay PowerShell script moi (khong co Unicode)
powershell.exe -ExecutionPolicy Bypass -File "%~dp0auto_build.ps1"

echo.
echo [*] Xong! Co the dong cua so nay.
pause
