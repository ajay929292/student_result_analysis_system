#!/usr/bin/env bash
# ==============================================================================
# Student Result Analysis System (IGNOU)
# Automated Unix / macOS / Linux Startup Runner
# ==============================================================================

set -e

echo "==============================================================================="
echo "               STUDENT RESULT ANALYSIS SYSTEM (IGNOU)"
echo "               Automated Deployment and Local Execution"
echo "==============================================================================="
echo ""

# 1. Determine Python command
if command -v python3 &> /dev/null; then
    PY_BIN="python3"
elif command -v python &> /dev/null; then
    PY_BIN="python"
else
    echo "[ERROR] Python is not installed or not in your PATH!"
    echo "Please install Python 3.10+ and re-run this script."
    exit 1
fi

# 2. Check virtual environment
echo "[1/5] Checking Python virtual environment..."
if [ ! -d "venv" ]; then
    echo " - Creating virtual environment 'venv'..."
    $PY_BIN -m venv venv
    echo " - Virtual environment created successfully."
else
    echo " - Virtual environment 'venv' found."
fi

# 3. Activate virtual environment
echo "[2/5] Activating virtual environment..."
# shellcheck source=/dev/null
source venv/bin/activate

# 4. Install / Verify Dependencies
echo "[3/5] Verifying and installing dependencies..."
pip install --upgrade pip --quiet
pip install -r requirements.txt --quiet
echo " - Dependencies verified."

# 5. Environment configuration
echo "[4/5] Checking environment configuration (.env)..."
if [ ! -f ".env" ]; then
    if [ -f ".env.example" ]; then
        echo " - Creating .env from .env.example..."
        cp .env.example .env
    else
        echo " - Generating default .env..."
        cat <<EOF > .env
FLASK_APP=run.py
FLASK_ENV=development
FLASK_DEBUG=1
SECRET_KEY=student-result-analysis-secret-key-2025
DATABASE_URL=sqlite:///student_results.db
EOF
    fi
fi
echo " - Configuration ready."

# 6. Initialize & Seed Relational Database
echo "[5/5] Initializing database schema and seed records..."
python seed_db.py

echo ""
echo "==============================================================================="
echo " Application is ready!"
echo " Starting local development server..."
echo " Access Web Application: http://127.0.0.1:5000"
echo " Default Demo Accounts:"
echo "   - Administrator: admin    / Admin@12345"
echo "   - Evaluator:     teacher1 / Teacher@12345"
echo "   - Student:       student1 / Student@12345"
echo "==============================================================================="
echo ""

python run.py
