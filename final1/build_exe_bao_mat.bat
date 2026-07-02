@echo off
setlocal enabledelayedexpansion
echo ========================================
echo BUILD FILE .EXE MA HOA BAO MAT
echo ========================================
echo.

REM Kiem tra python tu PATH
python --version >nul 2>&1
if not errorlevel 1 (
    set "PYTHON_EXE=python"
    echo [OK] Tim thay Python trong PATH.
    goto :found_python
)

REM Khong tim thay Python
echo [ERROR] KHONG TIM THAY PYTHON!
pause
exit /b 1

:found_python
echo Khoi chay bang: %PYTHON_EXE%
echo.

echo [INFO] Cai dat cac thu vien can thiet...
%PYTHON_EXE% -m pip install --upgrade pip pyinstaller requests qrcode pillow selenium webdriver_manager --quiet

echo.
echo [INFO] Dang tien hanh dong goi va bien dich ra Bytecode Python 3.11...
echo Code cua thu muc automation se duoc an va chuyen sang dang bytecode (Khong doc duoc ma nguon)
echo Vui long cho tu 2-5 phut...
echo.

%PYTHON_EXE% -m PyInstaller --clean --onefile --noconsole --name "dangkytinchi_baomat" --add-data "automation\*.json;automation" --add-data "automation\*.bat;automation" --hidden-import "automation.auto_login_with_title_check" --hidden-import "automation.auto_with_save" --hidden-import "automation.config_auto_login" --hidden-import "automation.enhanced_two_step_registration" --hidden-import "automation.handle_schedule_conflict" --hidden-import "automation.real_website_automation" --hidden-import "automation.two_step_registration" --hidden-import selenium --hidden-import PIL --hidden-import qrcode --hidden-import requests --collect-all selenium --collect-all webdriver_manager -y complete_gui.py

echo.
if exist "dist\dangkytinchi_baomat.exe" (
    echo ========================================
    echo [OK] DA DONG GOI VA BIEN DICH THANH CONG!
    echo ========================================
    echo File bao mat nam tai: %CD%\dist\dangkytinchi_baomat.exe
    echo Code duoc dich sang pyc 3.11 khong the dich nguoc nguon thong thuong.
) else (
    echo ========================================
    echo [ERROR] DONG GOI THAT BAI!
    echo ========================================
)

pause
