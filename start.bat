@echo off
setlocal enabledelayedexpansion

title Student Result Analysis System - Startup Runner

echo ===============================================================================
echo                STUDENT RESULT ANALYSIS SYSTEM (IGNOU)
echo                Automated Deployment and Local Execution
echo ===============================================================================
echo.

:: 1. Check Python installation
where python >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Python was not found in your system PATH!
    echo Please install Python 3.10+ from https://www.python.org/ and check "Add Python to PATH".
    echo.
    pause
    exit /b 1
)

echo [1/5] Checking Python virtual environment...
if not exist "venv\Scripts\activate.bat" (
    echo  - Creating virtual environment 'venv'...
    python -m venv venv
    if %ERRORLEVEL% NEQ 0 (
        echo [ERROR] Failed to create virtual environment!
        pause
        exit /b 1
    )
    echo  - Virtual environment created successfully.
) else (
    echo  - Virtual environment 'venv' found.
)

:: 2. Activate Virtual Environment
echo [2/5] Activating virtual environment...
call venv\Scripts\activate.bat
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Failed to activate virtual environment!
    pause
    exit /b 1
)

:: 3. Install / Verify Dependencies
echo [3/5] Verifying and installing dependencies...
pip install -r requirements.txt --quiet
if %ERRORLEVEL% NEQ 0 (
    echo [WARNING] Dependency installation encountered issues. Attempting standard install...
    pip install -r requirements.txt
)
echo  - Dependencies verified.

:: 4. Environment Configuration
echo [4/5] Checking environment configuration (.env)...
if not exist ".env" (
    if exist ".env.example" (
        echo  - Creating default .env from .env.example...
        copy .env.example .env >nul
    ) else (
        echo  - Creating default .env file...
        echo FLASK_APP=run.py > .env
        echo FLASK_ENV=development >> .env
        echo FLASK_DEBUG=1 >> .env
        echo SECRET_KEY=student-result-analysis-secret-key-2025 >> .env
        echo DATABASE_URL=sqlite:///student_results.db >> .env
    )
)
echo  - Configuration ready.

:: 5. Initialize & Seed Relational Database
echo [5/5] Initializing database and verifying seed records...
python seed_db.py
if %ERRORLEVEL% NEQ 0 (
    echo [WARNING] Database seeding script reported an error. Continuing launch...
)

echo.
echo ===============================================================================
echo  Application is ready!
echo  Starting local development server...
echo  Access Web Application: http://127.0.0.1:5000
echo  Default Demo Accounts:
echo    - Administrator: admin    / Admin@12345
echo    - Evaluator:     teacher1 / Teacher@12345
echo    - Student:       student1 / Student@12345
echo ===============================================================================
echo.

python run.py

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo Server terminated with code %ERRORLEVEL%.
    pause
)
