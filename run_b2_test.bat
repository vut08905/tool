@echo off
echo.
echo ===================================
echo    ULSA B2 AUTOMATION TEST
echo ===================================
echo.
echo Target: Click radio button for KTCT0722H_D19QL.03_LT
echo Expected: grd_ctl05_chk radio button
echo.
echo Changing to directory...
cd /d "%~dp0"
echo Current dir: %CD%
echo.
echo Checking Python...
if exist ".venv\Scripts\python.exe" (
    echo ✅ Python found: .venv\Scripts\python.exe
) else (
    echo ❌ Python not found!
    pause
    exit /b 1
)
echo.
echo Checking script...
if exist "automation\auto_login_with_title_check.py" (
    echo ✅ Script found: automation\auto_login_with_title_check.py
) else (
    echo ❌ Script not found!
    pause
    exit /b 1
)
echo.
echo ===================================
echo   STARTING AUTOMATION...
echo ===================================
echo.
.venv\Scripts\python.exe automation\auto_login_with_title_check.py
echo.
echo ===================================
echo Script finished with exit code: %ERRORLEVEL%
echo ===================================
echo.
if %ERRORLEVEL% EQU 0 (
    echo ✅ SUCCESS: Automation completed successfully!
) else (
    echo ❌ ERROR: Automation failed with code %ERRORLEVEL%
)
echo.
pause
