@echo off
echo ========================================
echo   ST Mobile ^& Designing — POS v19
echo   Flask + SQLite Web Server
echo ========================================
echo.

REM Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python install නෑ!
    echo Download: https://python.org/downloads
    pause
    exit /b 1
)

REM Install Flask if needed
pip install flask -q

echo Starting server...
echo.
echo Open browser: http://localhost:5000
echo.
echo Server stop කරන්න: Ctrl+C press කරන්න
echo ========================================
echo.

python app.py
pause
