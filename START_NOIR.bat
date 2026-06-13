@echo off
title NOIR SOVEREIGN LAUNCHER v2.0
color 0A
echo.
echo  ████████████████████████████████████████████████████
echo   NOIR SOVEREIGN COMMAND CENTER - STARTING UP...
echo  ████████████████████████████████████████████████████
echo.

cd /d "%~dp0"

:: Hentikan proses lama
echo [1/4] Stopping old processes...
taskkill /F /IM python.exe /T 2>nul
timeout /t 2 /nobreak >nul

:: Cari Python
set PYTHON=C:\Users\ASUS\AppData\Local\Programs\Python\Python311\python.exe
if not exist "%PYTHON%" set PYTHON=C:\Users\ASUS\AppData\Local\Programs\Python\Python312\python.exe
if not exist "%PYTHON%" set PYTHON=C:\Users\ASUS\AppData\Local\Programs\Python\Python313\python.exe
if not exist "%PYTHON%" (
    echo [ERROR] Python tidak ditemukan!
    pause
    exit /b 1
)
echo [OK] Python: %PYTHON%

:: Instal websockets jika belum ada
echo [2/4] Checking dependencies...
"%PYTHON%" -c "import websockets" 2>nul || "%PYTHON%" -m pip install websockets -q

:: Start Backend Server
echo [3/4] Starting Backend Server (port 8000)...
start "NOIR-Backend" cmd /k "%PYTHON% noir-ui\web_server.py --port 8000"
timeout /t 4 /nobreak >nul

:: Start PC WebSocket Client
echo [4/4] Starting PC Agent (WebSocket Client)...
start "NOIR-PC-Agent" cmd /k "%PYTHON% noir-vps\pc_ws_client.py"
timeout /t 2 /nobreak >nul

:: Start Frontend
echo [5/4] Starting Frontend Dashboard...
if exist "C:\Program Files\nodejs\npm.cmd" (
    start "NOIR-Frontend" cmd /k "cd /d %~dp0noir_dashboard && C:\Program Files\nodejs\npm.cmd run dev"
) else if exist "C:\Program Files\nodejs\npm" (
    start "NOIR-Frontend" cmd /k "cd /d %~dp0noir_dashboard && npm run dev"
) else (
    echo [WARN] Node.js tidak ditemukan, skip frontend.
)

echo.
echo  ██████████████████████████████████████████████████████
echo   NOIR SOVEREIGN IS RUNNING!
echo  ██████████████████████████████████████████████████████
echo.
echo   Backend API  : http://localhost:8000
echo   API Docs     : http://localhost:8000/docs
echo   Dashboard    : http://localhost:5173
echo   Health Check : http://localhost:8000/health
echo.
echo   3 jendela terminal terbuka:
echo    [1] NOIR-Backend    (Web Server)
echo    [2] NOIR-PC-Agent   (WebSocket Client - tools executor)
echo    [3] NOIR-Frontend   (React Dashboard)
echo.
echo   Buka browser: http://localhost:5173
echo.
pause
