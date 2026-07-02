@echo off
color 0A
echo ================================================
echo     ULSA AUTO LOGIN + SMART RETRY SYSTEM
echo     Tu dong dang nhap va retry thong minh
echo ================================================
echo.

cd /d "%~dp0"

echo [INFO] Script se tu dong:
echo [INFO] 1. Doc va kiem tra thong tin tu auto_config.json
echo [INFO] 2. Dien thong tin dang nhap va XAC NHAN dang nhap thanh cong
echo [INFO] 3. CHI TIEP TUC khi dang nhap THANH CONG
echo [INFO] 4. Tu dong vao trang dang ky lop tin chi
echo [INFO] 5. Tu dong chon cac lop theo danh sach trong config
echo [INFO] 6. Tu dong click "Luu ket qua dang ky"
echo [INFO] 7. Tao bao cao chi tiet ket qua
echo [INFO] 8. GIU trinh duyet mo de ban kiem tra
echo.
echo [NEW] SMART RETRY SYSTEM:
echo [NEW] - Tu dong phat hien loi 503, 404, timeout
echo [NEW] - Retry thong minh khi web qua tai
echo [NEW] - Dang nhap lai neu gap loi 404
echo [NEW] - Exponential backoff cho server error
echo [NEW] - Khong retry neu trang hoat dong binh thuong
echo.
echo [CANH BAO] Script se DUNG LAI neu:
echo [CANH BAO] - Thong tin dang nhap SAI
echo [CANH BAO] - Mat khau chua duoc thay doi
echo [CANH BAO] - Dang nhap THAT BAI sau nhieu lan retry
echo.
echo [NOTICE] Hay dam bao da sua DUNG thong tin trong auto_config.json!
echo.

REM Tim Python
if exist "..^\.venv\Scripts\python.exe" (
    set PYTHON_EXE=..^\.venv\Scripts\python.exe
) else if exist ".venv\Scripts\python.exe" (
    set PYTHON_EXE=.venv\Scripts\python.exe
) else (
    set PYTHON_EXE=python
)

"%PYTHON_EXE%" config_auto_login.py

echo.
echo ============================================
echo         PROCESS COMPLETED
echo ============================================
pause
