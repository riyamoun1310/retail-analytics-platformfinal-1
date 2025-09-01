@echo off
echo ========================================
echo   Retail Analytics Platform Setup
echo ========================================
echo.

echo 📋 Checking prerequisites...

REM Check Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python not found! Please install Python 3.8+ from https://python.org
    pause
    exit /b 1
)
echo ✅ Python found

REM Check Node.js
node --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Node.js not found! Please install Node.js from https://nodejs.org
    pause
    exit /b 1
)
echo ✅ Node.js found

REM Check PostgreSQL
pg_isready >nul 2>&1
if %errorlevel% neq 0 (
    echo ⚠️ PostgreSQL not running or not found
    echo   Please ensure PostgreSQL is installed and running
    echo   Download from: https://www.postgresql.org/download/windows/
)

echo.
echo 🔧 Setting up backend...
cd backend

REM Create virtual environment
if not exist "venv" (
    echo Creating Python virtual environment...
    python -m venv venv
)

REM Activate virtual environment
call venv\Scripts\activate.bat

REM Install Python dependencies
echo Installing Python dependencies...
pip install -r ..\requirements.txt

REM Create environment file
if not exist ".env" (
    echo Creating .env file...
    copy ..\.env.example .env
)

REM Create database
echo Creating database...
python create_db.py

echo.
echo 🎨 Setting up frontend...
cd ..\frontend

REM Install Node.js dependencies
echo Installing Node.js dependencies...
npm install

echo.
echo ✅ Setup complete!
echo.
echo 🚀 To start the application:
echo   Backend: cd backend && venv\Scripts\activate.bat && python -m uvicorn main:app --reload
echo   Frontend: cd frontend && npm run dev
echo.
echo 📖 Access points:
echo   Frontend: http://localhost:5173
echo   Backend API: http://localhost:8000
echo   API Docs: http://localhost:8000/docs
echo.
pause
