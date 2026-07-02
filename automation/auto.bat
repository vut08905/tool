@echo off
color 0A
echo ============================================
echo    ULSA FULL AUTO LOGIN SYSTEM
echo    Tu dong dien va dang nhap hoan toan
echo ============================================
echo.

cd /d "%~dp0"

echo [INFO] Khoi dong automation...
echo [INFO] Se tu dong dien ma sinh vien va mat khau
echo [INFO] Roi bam nut dang nhap
echo.

REM Tim Python
if exist "..\.venv\Scripts\python.exe" (
    set PYTHON_EXE=..^\.venv\Scripts\python.exe
) else if exist ".venv\Scripts\python.exe" (
    set PYTHON_EXE=.venv\Scripts\python.exe
) else (
    set PYTHON_EXE=python
)

"%PYTHON_EXE%" full_auto_login.py

echo.
echo ============================================
echo         AUTOMATION COMPLETED
echo ============================================
pause
