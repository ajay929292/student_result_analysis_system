# Student Result Analysis System (SRAS)

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Flask 3.0.3](https://img.shields.io/badge/flask-3.0.3-green.svg)](https://palletsprojects.com/p/flask/)
[![SQLAlchemy](https://img.shields.io/badge/sqlalchemy-2.0+-red.svg)](https://www.sqlalchemy.org/)
[![Pandas](https://img.shields.io/badge/pandas-2.2.2-yellow.svg)](https://pandas.pydata.org/)
[![ReportLab](https://img.shields.io/badge/reportlab-5.0.1-orange.svg)](https://www.reportlab.com/)
[![OpenPyXL](https://img.shields.io/badge/openpyxl-3.1.5-brightgreen.svg)](https://openpyxl.readthedocs.io/)
[![Tests](https://img.shields.io/badge/tests-64%20passed-success.svg)]()

An institutional-grade, automated academic record management and analytical platform designed for universities and colleges. Built in full alignment with the **Indira Gandhi National Open University (IGNOU)** Major Project Guidelines (**BCSP-064 / MCSP-232**).

---

## 1. System Overview

The **Student Result Analysis System (SRAS)** transitions educational institutions from error-prone physical registers and fragmented spreadsheets into an integrated, secure, and data-driven digital ecosystem.

### Key Capabilities:
* **Academic Hierarchy Management:** Configure Academic Years, Semesters, Degree Classes, Master Course Registry, and Class-Subject credit/mark thresholds.
* **Role-Based Access Control (RBAC):** Distinct authentication and authorization tiers for **Administrators**, **Teachers/Evaluators**, and **Students**.
* **Dual Ingestion Engine:**
  * Interactive spreadsheet-like manual evaluation grid with real-time mark summation and IGNOU 10-point grade computation.
  * Atomic bulk ingestion supporting both `.csv` and `.xlsx` files with automatic header mapping, cell-level validation, and rollback on error.
* **Vectorized Statistical Analytics (Pandas & NumPy):**
  * Instant descriptive metrics (Mean, Median, Standard Deviation, Highest, Lowest).
  * Cohort pass/fail rates and grade frequency distribution (O, A+, A, B+, B, C, F).
  * Cross-subject benchmarking to highlight challenging courses.
  * At-risk student identification algorithm with recommended remedial interventions.
* **Document Generation & Export Services:**
  * **Individual Student Report Cards (PDF):** Institutional grade sheets generated using ReportLab Platypus with authentic university headers, subject marks breakdown, SGPA, and signature blocks.
  * **Master Tabulation Register (TR Sheet - Excel):** Comprehensive multi-column `.xlsx` registers generated via OpenPyXL with hierarchical headers, alternating zebra striping, and conditional formatting.
  * **Executive Class Performance Summary:** High-level printable briefings and landscape PDFs for Faculty Chairs and Heads of Department.

---

## 2. Quick Start (One-Command Execution)

The system includes automated setup and execution runner scripts that automatically verify Python, initialize the virtual environment, install dependencies, copy environment variables, seed default data, and start the web server:

### For Windows:
Double-click `start.bat` or execute in PowerShell / Command Prompt:
```cmd
start.bat
```

### For Linux / macOS:
Make executable and run in terminal:
```bash
chmod +x start.sh
./start.sh
```

The web application will be accessible at: **`http://127.0.0.1:5000`**

---

## 3. Manual Installation & Setup

If you prefer to configure and run the application manually, follow these steps:

### Prerequisites:
* Python **3.10+** (Python 3.11, 3.12, or 3.13 recommended)
* `pip` package manager
* Git

### Step 1: Clone Repository
```bash
git clone https://github.com/your-repo/IGNOU_project.git
cd IGNOU_project
```

### Step 2: Create and Activate Virtual Environment
```bash
# Windows
python -m venv venv
call venv\Scripts\activate

# Linux / macOS
python3 -m venv venv
source venv/bin/activate
```

### Step 3: Install Required Dependencies
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### Step 4: Configure Environment Variables
```bash
# Windows
copy .env.example .env

# Linux / macOS
cp .env.example .env
```

### Step 5: Initialize Schema & Seed Demo Records
```bash
python seed_db.py
```

### Step 6: Launch Development Server
```bash
python run.py
```
Open **`http://127.0.0.1:5000`** in your web browser.

---

## 4. Pre-Seeded Demonstration Accounts

The database comes pre-configured with three role-based user accounts for evaluation:

| Role | Username | Password | Access Privileges |
| :--- | :--- | :--- | :--- |
| **System Administrator** | `admin` | `Admin@12345` | Full system control: academic years, classes, course mappings, user accounts, exam term locking. |
| **Faculty / Evaluator** | `teacher1` | `Teacher@12345` | Student rosters, manual marks entry, CSV/Excel uploads, analytics dashboard, PDF marksheet generation, Excel TR export. |
| **Student / Viewer** | `student1` | `Student@12345` | Read-only access to enrolled term marks and personal performance history. |

---

## 5. Technology Stack & Rationale

| Layer | Technology | Rationale |
| :--- | :--- | :--- |
| **Backend Framework** | **Python (Flask 3.0.3)** | Lightweight, modular routing, clean Blueprint architecture, and native Python ecosystem integration. |
| **Database & ORM** | **SQLite / SQLAlchemy** | ACID compliant, strict foreign key constraints, parameterized queries preventing SQL injection. |
| **Security & Auth** | **Flask-Bcrypt** | Strong salted password hashing (Blowfish cipher) and secure HTTP session management. |
| **Data Analytics** | **Pandas & NumPy** | Vectorized statistical calculations for cohort metrics, grade distributions, and merit ranking. |
| **PDF Generation** | **ReportLab 5.0.1** | Pure-Python programmatic PDF generation (Platypus flowables) without requiring external binaries like `wkhtmltopdf`. |
| **Spreadsheet Engine** | **OpenPyXL 3.1.5** | Multi-column Excel register creation with styled headers, custom widths, and conditional formatting. |
| **Frontend UI** | **HTML5 & Vanilla CSS3** | Custom dark-obsidian design system with glassmorphism, responsive Flexbox/Grid, and zero framework bloat. |
| **Visual Charts** | **Chart.js (ES6)** | Dynamic, hardware-accelerated canvas charts (bar histograms, radar comparisons, doughnut charts). |
| **Automated Testing** | **PyTest 8.3.2** | Comprehensive test suite covering units, integration, routes, calculations, and security. |

---

## 6. Directory Structure

```text
IGNOU_project/
│
├── app/                              # Primary application package
│   ├── __init__.py                   # Application Factory pattern (create_app)
│   ├── config.py                     # Environment configurations (Dev, Test, Prod)
│   ├── models/                       # SQLAlchemy relational schema
│   │   ├── academic.py               # AcademicYear, Class, Subject, ClassSubject
│   │   ├── result.py                 # ExamTerm, GradingScale, GradeRule, Marks
│   │   ├── student.py                # Student profile model
│   │   └── user.py                   # User model with Bcrypt password hashing
│   ├── routes/                       # Modular Flask Blueprints
│   │   ├── academic_routes.py        # Curriculum and class management
│   │   ├── analytics_routes.py       # Visual dashboard & REST JSON APIs
│   │   ├── auth_routes.py            # Login, logout, profile management
│   │   ├── main_routes.py            # Landing and dashboard dispatch
│   │   ├── marks_routes.py           # Manual entry grid, bulk upload, term locking
│   │   ├── report_routes.py          # PDF marksheet, Excel TR, executive summary
│   │   └── student_routes.py         # Student directory, registration, bulk enroll
│   ├── services/                     # Business logic and computational engines
│   │   ├── analytics_service.py      # Pandas vector computations & at-risk algorithm
│   │   ├── grading_service.py        # Grade mapping & boundary evaluations
│   │   ├── ingestion_service.py      # CSV/Excel parsing, validation & atomic commit
│   │   └── report_service.py         # ReportLab PDF & OpenPyXL Excel generators
│   ├── static/                       # Client assets
│   │   ├── css/                      # Custom CSS design system (main.css, components.css)
│   │   └── js/                       # Vanilla JS helpers
│   ├── templates/                    # Jinja2 semantic HTML templates
│   │   ├── base.html                 # Core layout, sidebar navigation, dark mode
│   │   ├── academic/                 # Academic setup views
│   │   ├── analytics/                # Visual Chart.js dashboard
│   │   ├── auth/                     # Login and user profile forms
│   │   ├── marks/                    # Interactive entry grid & bulk upload
│   │   ├── reports/                  # Report cards, TR register, executive summary
│   │   └── students/                 # Student rosters and enrollment forms
│   └── utils/                        # Security decorators (login_required, teacher_required)
│
├── Docs/                             # Comprehensive project documentation
│   ├── academic_project_report.md    # IGNOU Project Report (SRS, DFD 0/1/2, ER diagram)
│   ├── architecture_plan.md          # 3-tier architectural blueprint
│   ├── implementationplan.md         # Detailed milestone completion tracker
│   ├── problemstatement.md           # Academic problem definition
│   └── user_manual.md                # Step-by-step user guide for faculty & admins
│
├── instance/                         # Local database storage (student_results.db)
├── tests/                            # Automated PyTest test suites
│   ├── test_academic.py              # Curriculum and academic model tests
│   ├── test_analytics.py             # Statistical computations and REST API tests
│   ├── test_auth.py                  # Authentication and RBAC tests
│   ├── test_factory.py               # Flask app factory and config tests
│   ├── test_marks.py                 # Evaluation engine and bulk upload tests
│   ├── test_models.py                # Database constraints and relations tests
│   ├── test_reports.py               # PDF and Excel generation tests
│   └── test_students.py              # Student management and roster tests
│
├── .env.example                      # Environment template
├── requirements.txt                  # Python package dependencies
├── run.py                            # Application entry point
├── seed_db.py                        # Database schema initialization & demo seed script
├── start.bat                         # Windows one-command startup script
└── start.sh                          # Linux/macOS one-command startup script
```

---

## 7. Running the Automated Test Suite

The test suite validates data models, grading logic, ingestion parsers, pandas statistical calculations, and document generation:

```bash
# Run all automated tests
pytest

# Run tests with verbose output
pytest -v

# Run specific test modules
pytest tests/test_reports.py -v
pytest tests/test_analytics.py -v
pytest tests/test_marks.py -v
```

All **64 automated tests** pass with 100% success rate.

---

## 8. Academic Project Guidelines Alignment

This application fulfills all specifications for the **IGNOU BCA (BCSP-064)** and **MCA (MCSP-232)** Project Guidelines:
* Detailed Data Flow Diagrams: **Context Level 0, Level 1, and Level 2** in [Docs/academic_project_report.md](file:///c:/Users/AJAY%20SHARMA/OneDrive/Desktop/AI_PROJECTS/IGNOU_project/Docs/academic_project_report.md).
* Complete Entity-Relationship (ER) Crow's Foot Diagram.
* Complete Relational Data Dictionary.
* Documented Test Cases and Boundary Value Analyses.

---

## 9. License

Developed for academic demonstration and research purposes under the **MIT License**.
