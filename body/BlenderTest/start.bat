@echo off
chcp 65001 >nul
echo.
echo  ┌──────────────────────────────────────────────┐
echo  │         BodyForge - Blender MPFB Web         │
echo  └──────────────────────────────────────────────┘
echo.

:: Kiểm tra Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python chưa được cài đặt!
    echo   → Tải tại: https://python.org
    pause
    exit /b 1
)

:: Tạo thư mục output
if not exist "output" mkdir output
if not exist "assets\clothing" mkdir assets\clothing

:: Cài đặt dependencies nếu chưa có
if not exist "backend\venv" (
    echo [SETUP] Tạo virtual environment...
    python -m venv backend\venv
    echo [SETUP] Cài đặt packages...
    backend\venv\Scripts\pip install -r backend\requirements.txt -q
    echo [OK] Đã cài đặt xong!
    echo.
)

:: Kiểm tra Blender
echo [CHECK] Kiểm tra Blender...
set BLENDER_DEFAULT="C:\Program Files\Blender Foundation\Blender 4.2\blender.exe"
if exist %BLENDER_DEFAULT% (
    echo [OK] Blender 4.2 tìm thấy
) else (
    echo [WARN] Blender không tìm thấy tại đường dẫn mặc định
    echo   → Chỉnh BLENDER_PATH trong backend\main.py
    echo   → Hoặc set biến môi trường: set BLENDER_PATH=C:\path\to\blender.exe
)
echo.

:: Khởi động server
echo [START] Khởi động FastAPI server...
echo   → Web App:  http://localhost:8000/app
echo   → API Docs: http://localhost:8000/docs
echo.

:: Mở browser tự động sau 2 giây
start "" timeout /t 2 >nul
start "" "http://localhost:8000/app"

:: Chạy server
backend\venv\Scripts\python backend\main.py
