@echo off
echo ========================================
echo   Starting Retail Analytics Platform
echo ========================================
echo.

REM Start backend
echo 🚀 Starting backend server...
start cmd /k "cd backend && venv\Scripts\activate.bat && python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000"

REM Wait a moment
timeout /t 3 /nobreak >nul

REM Start frontend
echo 🎨 Starting frontend server...
start cmd /k "cd frontend && npm run dev"

echo.
echo ✅ Both servers are starting up!
echo.
echo 📖 Access points:
echo   Frontend: http://localhost:5173
echo   Backend API: http://localhost:8000
echo   API Docs: http://localhost:8000/docs
echo.
echo ⏹️ Press any key to close this window (servers will keep running)
pause >nul
