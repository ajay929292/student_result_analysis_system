# STUDENT RESULT ANALYSIS SYSTEM (SRAS)
## Project File Manifest & Codebase Architecture Reference
### Master Documentation for BCA / MCA Major Project (BCSP-064 / MCSP-232)
**Indira Gandhi National Open University (IGNOU)**  
**School of Computer and Information Sciences (SOCIS)**  
**Academic Session:** 2025 – 2026

---

## 1. Executive Summary & Architectural Overview

The **Student Result Analysis System (SRAS)** is an institutional-grade, web-based academic record management and analytical platform. Designed according to the rigorous software engineering standards prescribed by **IGNOU SOCIS** for BCA and MCA Major Projects, the codebase adopts a clean, modular, and maintainable **Model-View-Controller (MVC)** architectural pattern augmented with a dedicated **Service Layer**.

### Core Engineering & Design Patterns Applied:
1. **Application Factory Pattern (`app/__init__.py:create_app`)**: Allows dynamic instantiation of the Flask application across distinct runtime environments (`development`, `testing`, `production`) with isolated configurations and database engines.
2. **Layered Separation of Concerns (SoC)**:
   - **Data Access Tier (`app/models/`)**: Relational entity definitions, constraints, indices, foreign keys, and cascading rules managed via SQLAlchemy ORM.
   - **Business Logic & Service Tier (`app/services/`)**: Encapsulates core domain computations—grading policy mapping, vectorized statistical analytics with Pandas/NumPy, batch spreadsheet ingestion with atomic rollback guarantees, and ReportLab/openpyxl document generation.
   - **Presentation & Routing Tier (`app/routes/` & `app/templates/`)**: URL endpoint routing, session-based Role-Based Access Control (RBAC), and server-side semantic HTML5/Jinja2 template rendering.
   - **Client Experience Tier (`app/static/`)**: Modern Vanilla CSS design system with CSS custom properties (variables), glassmorphic aesthetics, and interactive Chart.js visualizations.
3. **Role-Based Access Control (RBAC)**: Enforced via reusable Python decorators (`@login_required`, `@admin_required`, `@teacher_required`) preventing privilege escalation.
4. **Unit of Work & Atomic Transactions**: Batch data ingestion uses transactional commit and rollback mechanics ensuring that if any row fails validation, no partial or corrupt state is committed to the database.
5. **Two-Pass Dynamic PDF Pagination**: Custom canvas implementation (`NumberedCanvas`) dynamically measures total page count and stamps official institutional running footers and verification badges.

---

## 2. Complete Project Directory Tree

Below is the exhaustive, hierarchical layout of all tracked source code, templates, scripts, configurations, and documentation comprising the SRAS codebase:

```text
IGNOU_project/
├── .env.example                                  # Template for environment-specific secrets & configuration
├── .gitignore                                     # Git version control ignore rules
├── requirements.txt                              # Pinned Python package dependencies
├── run.py                                        # Application launch entry point
├── seed_db.py                                    # Idempotent database seeder with demo cohorts & scores
├── start.bat                                     # 1-Click automated execution script for Windows
├── start.sh                                      # 1-Click automated execution script for Linux / macOS
├── README.md                                     # Primary GitHub repository documentation & quick start
├── .vscode/
│   └── settings.json                             # Workspace IDE configuration for VS Code
├── Docs/
│   ├── academic_project_report.md                # Formal 700+ line academic project report for IGNOU
│   ├── architecture_plan.md                      # System architectural blueprint & design specifications
│   ├── implementationplan.md                     # Phased development milestone tracker & task logs
│   ├── problemstatement.md                       # Academic problem formulation & motivation
│   ├── project_files_description.md              # THIS FILE: Exhaustive codebase manifest & file reference
│   └── user_manual.md                            # Comprehensive operations manual for Admins, Teachers & Students
├── app/
│   ├── __init__.py                               # Flask Application Factory & extension initialization
│   ├── config.py                                 # Multi-environment configuration classes
│   ├── models/                                   # Relational Database Models (SQLAlchemy ORM)
│   │   ├── __init__.py                           # Models package export interface
│   │   ├── academic.py                           # AcademicYear, Class, Subject, ClassSubject entities
│   │   ├── result.py                             # ExamTerm, GradingScale, GradeRule, Marks entities
│   │   ├── student.py                            # Student entity & enrollment linkages
│   │   └── user.py                               # User entity, Bcrypt password hashing & RBAC roles
│   ├── routes/                                   # Controller Layer & HTTP Request Handlers (Flask Blueprints)
│   │   ├── __init__.py                           # Routes package initialization
│   │   ├── academic_routes.py                    # Academic years, class cohorts & curriculum mappings
│   │   ├── analytics_routes.py                   # Analytical web dashboard & REST API JSON endpoints
│   │   ├── auth_routes.py                        # Authentication, login, logout, profile & session status
│   │   ├── main_routes.py                        # Landing page, milestone status & system health check
│   │   ├── marks_routes.py                       # Manual grid evaluation & spreadsheet marks ingestion
│   │   ├── report_routes.py                      # PDF report card streaming & Excel TR Sheet downloads
│   │   └── student_routes.py                     # Student enrollment, search filter & batch roster import
│   ├── services/                                 # Business Logic, Calculations & Processing Layer
│   │   ├── __init__.py                           # Services package initialization
│   │   ├── analytics_service.py                  # Vectorized descriptive metrics, rankings & at-risk detection
│   │   ├── grading_service.py                    # IGNOU 10-point scale grade mapping & mark aggregations
│   │   ├── ingestion_service.py                  # High-speed CSV/Excel parsers & atomic rollback handler
│   │   └── report_service.py                     # ReportLab PDF generator & openpyxl Excel TR exporter
│   ├── static/                                   # Client-Side Assets
│   │   ├── css/
│   │   │   ├── components.css                    # UI components (cards, tables, badges, modals, forms)
│   │   │   └── main.css                          # Design tokens, CSS variables, typography & layout grid
│   │   └── js/
│   │       └── main.js                           # Chart.js initialization, live mark sum & AJAX utilities
│   ├── templates/                                # Server-Side Semantic HTML5 / Jinja2 Templates
│   │   ├── base.html                             # Master layout shell, navbar, flash alerts & footer
│   │   ├── index.html                            # Home dashboard landing page & milestones status
│   │   ├── academic/
│   │   │   ├── curriculum.html                   # Subject-to-class mapping & evaluation threshold setup
│   │   │   └── index.html                        # Academic configuration hub (years, classes, subjects)
│   │   ├── analytics/
│   │   │   └── dashboard.html                    # Visual analytics dashboard with charts & at-risk roster
│   │   ├── auth/
│   │   │   ├── login.html                        # Secure user authentication interface
│   │   │   └── profile.html                      # User account profile details & assigned permissions
│   │   ├── marks/
│   │   │   ├── bulk.html                         # Batch CSV/Excel marks upload with schema validation
│   │   │   ├── entry.html                        # Interactive spreadsheet-like manual evaluation grid
│   │   │   └── terms.html                        # Examination term management & term locking controls
│   │   ├── reports/
│   │   │   ├── class_summary.html                # Executive performance briefing & print-optimized report
│   │   │   ├── report_card_preview.html          # Individual student grade card preview & download triggers
│   │   │   ├── report_cards_index.html           # Student grade card directory & cohort selector
│   │   │   └── tabulation_register.html          # Master Tabulation Register (TR Sheet) preview & export
│   │   └── students/
│   │       ├── bulk.html                         # Bulk student registration via CSV/Excel template
│   │       ├── form.html                         # Individual student registration & profile editor
│   │       └── index.html                        # Student directory with real-time search & class filtering
│   └── utils/                                    # System Utilities & Helper Modules
│       ├── __init__.py                           # Utils package export interface
│       └── decorators.py                         # Route security decorators (@login_required, @role_required)
├── tests/                                        # Automated Pytest Quality Assurance Suite (64 Tests)
│   ├── __init__.py                               # Test suite package initializer
│   ├── test_academic.py                          # Tests for academic sessions, classes & curriculum mapping
│   ├── test_analytics.py                         # Tests for Pandas statistics, grade distributions & at-risk rules
│   ├── test_auth.py                              # Tests for Bcrypt authentication, sessions & RBAC enforcement
│   ├── test_factory.py                           # Tests for Flask application factory & health endpoints
│   ├── test_marks.py                             # Tests for mark calculations, batch ingestion & term locks
│   ├── test_models.py                            # Tests for SQLAlchemy relational models, constraints & cascades
│   ├── test_reports.py                           # Tests for PDF report card rendering & Excel TR sheet generation
│   └── test_students.py                          # Tests for student enrollment, validation & search filtering
└── uploads/
    └── .gitkeep                                  # Marker to maintain uploads directory in Git version control
```

---

## 3. Detailed Specifications of Every File

---

### 3.1 Root Configuration, Environment & Launcher Scripts

#### 1. `.env.example`
- **Path:** [`.env.example`](file:///.env.example)
- **Role:** Configuration Template / Security Baseline.
- **Description:** Acts as the template for environment variables required by the application. Developers copy this file to `.env` for local configuration.
- **Key Parameters Defined:**
  - `FLASK_ENV`: Selects the configuration profile (`development`, `testing`, `production`).
  - `SECRET_KEY`: Cryptographic salt for session signing and CSRF tokens.
  - `DEV_DATABASE_URL` / `DATABASE_URL`: Connection strings pointing to the SQLite database instance (`sqlite:///instance/dev.db`).
  - `PORT`: TCP port for the local WSGI server (defaults to 5000).
- **Academic Relevance:** Emphasizes the Twelve-Factor App methodology by separating configuration from code, preventing credential leakage in public repositories.

#### 2. `.gitignore`
- **Path:** [`.gitignore`](file:///.gitignore)
- **Role:** Version Control Exclusion Rules.
- **Description:** Instructs Git to ignore sensitive files, virtual environments, compiled bytecode, cache artifacts, and SQLite database binaries.
- **Patterns Excluded:** `__pycache__/`, `*.pyc`, `venv/`, `.env`, `instance/*.db`, `.pytest_cache/`, `*.egg-info/`, `.DS_Store`, and temporary upload spreadsheets.
- **Academic Relevance:** Ensures clean repository hygiene without bloating the repository with binary data or committing secrets.

#### 3. `.vscode/settings.json`
- **Path:** [`.vscode/settings.json`](file:///.vscode/settings.json)
- **Role:** Developer Environment Settings.
- **Description:** Configures Visual Studio Code to automatically recognize the local virtual environment interpreter (`venv/Scripts/python.exe`), format files using PEP 8 standards, and configure Pytest as the default test runner.

#### 4. `requirements.txt`
- **Path:** [`requirements.txt`](file:///.requirements.txt)
- **Role:** Dependency Specification.
- **Description:** Pinned list of all Python packages and libraries required to build, test, and run SRAS.
- **Key Dependencies:**
  - `Flask>=3.0.3`: Core WSGI web application framework.
  - `Flask-SQLAlchemy>=3.1.1`: Relational Object-Relational Mapping (ORM) toolkit.
  - `Flask-Bcrypt>=1.0.1`: Cryptographic password hashing wrapper around OpenSSL.
  - `python-dotenv>=1.0.1`: Environment variable loader.
  - `pandas>=2.2.2` & `numpy>=2.0.0`: Vectorized data analysis, aggregations, and statistics.
  - `openpyxl>=3.1.5` & `xlrd>=2.0.1`: Excel spreadsheet parsing, formatting, and styled workbook generation.
  - `reportlab>=4.2.5`: Institutional-grade PDF layout engine using Platypus flowables.
  - `pytest>=8.3.2`: Automated test framework.

#### 5. `run.py`
- **Path:** [`run.py`](file:///run.py)
- **Role:** WSGI Application Execution Entry Point.
- **Description:** The root executable file invoked to start the web application. Reads environment variables, calls `create_app(env_name)`, and starts the built-in development server on `http://127.0.0.1:5000`.
- **Key Code Logic:**
  ```python
  load_dotenv()
  env_name = os.environ.get('FLASK_ENV', 'development')
  app = create_app(env_name)
  if __name__ == '__main__':
      app.run(host='127.0.0.1', port=int(os.environ.get('PORT', 5000)), debug=app.config.get('DEBUG', True))
  ```

#### 6. `seed_db.py`
- **Path:** [`seed_db.py`](file:///seed_db.py)
- **Role:** Idempotent Database Initialization & Mock Data Seeder.
- **Description:** Populates a freshly initialized database with standard IGNOU curriculum data, user accounts, cohorts, subjects, and realistic student marks for demonstration and testing.
- **Seed Data Injected:**
  1. Default Users: `admin` (Administrator), `teacher` & `teacher1` (Evaluators), `student1` (Student).
  2. Grading Scale: "IGNOU Standard 10-Point" scale with all official grade brackets (`O`, `A+`, `A`, `B+`, `B`, `C`, `F`).
  3. Academic Sessions: `2024-2025` and `2025-2026` (Active).
  4. Course Registry: 8 BCA courses (`BCS-011`, `BCS-012`, `BCSL-013`, `MCS-011`, `MCS-012`, etc.) with credits and internal/external mark thresholds (30/70, pass 40).
  5. Exam Terms: "TEE December 2024" (Locked) and "TEE June 2025" (Open).
  6. Demo Cohorts: Over 30 student records across BCA Semester 1 (Sections A and B) with generated internal, external, and absentee marks.
- **Academic Relevance:** Enables immediate project demonstration during IGNOU viva voce examinations without requiring manual data setup.

#### 7. `start.bat`
- **Path:** [`start.bat`](file:///start.bat)
- **Role:** Windows 1-Click Startup Automation.
- **Description:** Automated batch runner for Windows operating systems. Checks for Python 3.10+ in `PATH`, verifies/creates the virtual environment (`venv`), installs all dependencies from `requirements.txt`, copies `.env.example` to `.env` if missing, seeds the database, and launches the browser to `http://127.0.0.1:5000`.

#### 8. `start.sh`
- **Path:** [`start.sh`](file:///start.sh)
- **Role:** Unix / Linux / macOS 1-Click Startup Automation.
- **Description:** Shell script equivalent of `start.bat` for POSIX systems. Automates environment creation, dependency resolution, database migration/seeding, and server execution.

---

### 3.2 Application Core & Utilities (`app/`)

#### 9. `app/__init__.py`
- **Path:** [`app/__init__.py`](file:///app/__init__.py)
- **Role:** Application Factory & Extension Hub.
- **Description:** Core factory module containing `create_app(config_name)`. Instantiates the Flask application, loads configuration classes, registers SQLAlchemy (`db`) and Bcrypt (`bcrypt`), configures SQLite foreign key enforcement via SQLite PRAGMA hooks, registers context processors for global Jinja variables, and registers all 7 architectural route Blueprints.
- **Key Code Symbols:**
  - `db = SQLAlchemy()`: Shared database engine.
  - `bcrypt = Bcrypt()`: Password encryption engine.
  - `set_sqlite_pragma()`: Ensures SQLite enforces `PRAGMA foreign_keys=ON` on every connection.
  - `create_app()`: Application factory method.
  - `@app.context_processor inject_global_vars()`: Injects `current_user`, `app_name`, and environment variables into all HTML templates.

#### 10. `app/config.py`
- **Path:** [`app/config.py`](file:///app/config.py)
- **Role:** Multi-Environment Configuration Dictionary.
- **Description:** Implements object-oriented configuration management using class inheritance:
  - `BaseConfig`: Default settings (`SECRET_KEY`, `MAX_CONTENT_LENGTH=16MB`, `ALLOWED_EXTENSIONS`, `UPLOAD_FOLDER`).
  - `DevelopmentConfig`: Enables debug mode, points to `instance/dev.db`.
  - `TestingConfig`: Disables CSRF, uses an isolated in-memory database (`sqlite:///:memory:`).
  - `ProductionConfig`: Disables debugging, utilizes production connection strings.
- **Dictionary Mapping:** `config = {'development': ..., 'testing': ..., 'production': ...}`.

#### 11. `app/utils/__init__.py`
- **Path:** [`app/utils/__init__.py`](file:///app/utils/__init__.py)
- **Role:** Package Export Interface.
- **Description:** Exports utility functions and authentication decorators for clean imports across blueprints.

#### 12. `app/utils/decorators.py`
- **Path:** [`app/utils/decorators.py`](file:///app/utils/decorators.py)
- **Role:** Security & Access Control Decorator Suite.
- **Description:** Contains higher-order function decorators wrapping Flask routes to implement security policies:
  - `@login_required`: Redirects unauthenticated requests to `/login` (or returns HTTP 401 for JSON API endpoints).
  - `@role_required(*allowed_roles)`: Inspects `session['user_role']`; rejects unauthorized requests with HTTP 403 or redirects with a flash notification.
  - `@admin_required`: Convenience decorator restricting access strictly to `ADMIN` accounts.
  - `@teacher_required`: Convenience decorator allowing both `ADMIN` and `TEACHER` accounts.

---

### 3.3 Relational Data Models & ORM Layer (`app/models/`)

#### 13. `app/models/__init__.py`
- **Path:** [`app/models/__init__.py`](file:///app/models/__init__.py)
- **Role:** Models Packaging Interface.
- **Description:** Exports all SQLAlchemy model classes (`User`, `AcademicYear`, `Class`, `Subject`, `ClassSubject`, `Student`, `ExamTerm`, `GradingScale`, `GradeRule`, `Marks`) to enable simple imports like `from app.models import Student, Marks`.

#### 14. `app/models/academic.py`
- **Path:** [`app/models/academic.py`](file:///app/models/academic.py)
- **Role:** Academic Hierarchy Data Models.
- **Entities Defined:**
  - `AcademicYear`: Academic session cycle (e.g., "2025-2026"). Tracks `is_active` status to indicate the current operating semester.
  - `Class`: Program cohort (e.g., "BCA Semester 1 - Section A"). Linked via foreign key to `AcademicYear`. Has unique constraint on `(class_name, section, year_id)`.
  - `Subject`: Master course catalog entity (e.g., "BCS-011 Computer Basics"). Stores unique `subject_code`, `subject_name`, and credit value.
  - `ClassSubject`: Associative curriculum mapping linking a `Class` and a `Subject`. Configures evaluation constraints: `max_internal_marks` (default 30.0), `max_external_marks` (default 70.0), and `pass_marks` (default 40.0).

#### 15. `app/models/result.py`
- **Path:** [`app/models/result.py`](file:///app/models/result.py)
- **Role:** Examination, Grading Policy & Marks Storage Models.
- **Entities Defined:**
  - `ExamTerm`: Examination cycle (e.g., "TEE June 2025"). Includes `is_locked` boolean flag preventing score tampering once results are finalized.
  - `GradingScale`: Container for institutional grading policies (e.g., "IGNOU Standard 10-Point").
  - `GradeRule`: Specific percentage boundaries, letter grades, and grade points (e.g., 85%–100% -> `O` / 10.0; 0%–39.99% -> `F` / 0.0).
  - `Marks`: Core evaluation record storing scores for a student in a specific subject and exam term. Contains `internal_marks`, `external_marks`, `total_marks`, `percentage`, `grade`, `grade_point`, `is_absent`, `is_passed`, and audit tracking (`updated_by`, `updated_at`). Enforces a composite unique constraint on `(student_id, class_subject_id, term_id)`.

#### 16. `app/models/student.py`
- **Path:** [`app/models/student.py`](file:///app/models/student.py)
- **Role:** Student Demographic & Enrollment Model.
- **Entity Defined:**
  - `Student`: Represents an enrolled student. Attributes include `student_id` (PK), `enrollment_no` (indexed unique string, e.g., "240100101"), `full_name`, `email`, and `class_id` (FK to `classes.class_id` with `RESTRICT` on delete to protect academic transcripts).

#### 17. `app/models/user.py`
- **Path:** [`app/models/user.py`](file:///app/models/user.py)
- **Role:** User Identity & RBAC Authentication Model.
- **Entity Defined:**
  - `User`: Manages user credentials and authorization roles.
  - **Roles Defined:** `ROLE_ADMIN = 'ADMIN'`, `ROLE_TEACHER = 'TEACHER'`, `ROLE_STUDENT = 'STUDENT'`.
  - **Methods:**
    - `set_password(password)`: Hashes plaintext passwords using Bcrypt with automatic salt generation.
    - `check_password(password)`: Validates input password against stored hash.
    - `is_admin`, `is_teacher`: Convenience properties for role verification.

---

### 3.4 Business Logic & Service Engines (`app/services/`)

#### 18. `app/services/__init__.py`
- **Path:** [`app/services/__init__.py`](file:///app/services/__init__.py)
- **Role:** Service Layer Packaging.
- **Description:** Exports service classes (`GradingService`, `MarksIngestionService`, `AnalyticsService`, `ReportService`).

#### 19. `app/services/grading_service.py`
- **Path:** [`app/services/grading_service.py`](file:///app/services/grading_service.py)
- **Role:** Automated Grade Computation & Evaluation Logic.
- **Description:** Implements the official IGNOU 10-point letter grading and evaluation rules.
- **Key Methods:**
  - `get_active_scale()`: Queries database for the active grading policy.
  - `get_grade_for_percentage(percentage, scale)`: Maps numerical percentage to letter grade (`O`, `A+`, `A`, `B+`, `B`, `C`, `F`), grade point (10.0 to 0.0), and qualitative description.
  - `evaluate(internal, external, max_in, max_ex, pass_marks, is_absent, scale)`: Aggregates internal and external marks, handles absent status, computes percentage, verifies aggregate pass thresholds, and determines grade letter and points.

#### 20. `app/services/ingestion_service.py`
- **Path:** [`app/services/ingestion_service.py`](file:///app/services/ingestion_service.py)
- **Role:** High-Throughput Spreadsheet Parsing & Atomic Ingestion.
- **Description:** Handles batch marks ingestion from `.csv` and `.xlsx` files with zero-tolerance validation.
- **Key Capabilities:**
  - `ingest_file(...)`: Reads spreadsheets into Pandas DataFrames, normalizes column headers, performs cell-level checks (e.g., negative scores, marks exceeding maximum thresholds, invalid enrollment IDs), and writes to the database in an atomic transaction. If even one record is invalid, the entire transaction is rolled back and detailed row error messages are returned.
  - `generate_template(class_id, subject_id, file_format)`: Generates pre-populated CSV or Excel evaluation templates pre-filled with enrolled student names and roll numbers for teachers.

#### 21. `app/services/analytics_service.py`
- **Path:** [`app/services/analytics_service.py`](file:///app/services/analytics_service.py)
- **Role:** Vectorized Statistical Analytics Engine.
- **Description:** Powers all descriptive metrics and performance indicators using Pandas and NumPy.
- **Key Capabilities:**
  - `get_class_term_dataframe(class_id, term_id)`: Extracts raw evaluation records into a structured Pandas DataFrame.
  - `compute_overview_metrics(...)`: Computes total enrolled, appeared, pass rate, class average, standard deviation, and count of at-risk students.
  - `compute_grade_distribution(...)`: Calculates frequency distribution across all IGNOU grade brackets (`O` through `F`).
  - `compute_subject_comparison(...)`: Computes cross-subject benchmarks (average score, pass percentage, failure count) to identify challenging courses.
  - `identify_at_risk_students(...)`: Filter query isolating students who have failed one or more courses or scored an aggregate percentage between 40% and 45% (the academic vulnerability boundary).
  - `compute_top_performers(...)`: Ranks top students by aggregate SGPA and overall percentage.

#### 22. `app/services/report_service.py`
- **Path:** [`app/services/report_service.py`](file:///app/services/report_service.py)
- **Role:** Document Generation & Export Services (PDF & Excel).
- **Description:** Produces print-ready, professional academic documents.
- **Key Components:**
  - `NumberedCanvas`: Dynamic two-pass canvas dynamically computing total pages (`Page X of Y`) and stamping institutional footers.
  - `generate_student_report_card_pdf(student_id, term_id)`: Generates a publication-quality PDF grade card with university headers, student biodata, tabular breakdown of internal/external marks, SGPA, grading key, and signature blocks.
  - `generate_tabulation_register_excel(class_id, term_id)`: Uses `openpyxl` to build comprehensive multi-column Tabulation Registers (TR Sheets) with hierarchical merged header rows, zebra striping, conditional color fills for failed subjects, and class summary formulas.
  - `generate_class_summary_pdf(class_id, term_id)`: Generates an executive landscape PDF report for Department Heads and Principals summarizing cohort performance.

---

### 3.5 Controller & HTTP Route Blueprints (`app/routes/`)

#### 23. `app/routes/__init__.py`
- **Path:** [`app/routes/__init__.py`](file:///app/routes/__init__.py)
- **Role:** Route Blueprint Packaging.
- **Description:** Initializes the routes package and coordinates blueprint registrations.

#### 24. `app/routes/main_routes.py`
- **Path:** [`app/routes/main_routes.py`](file:///app/routes/main_routes.py)
- **Role:** Landing Dashboard & System Health Controller.
- **Endpoints:**
  - `GET /`: Landing overview presenting high-level system metrics and project milestone status.
  - `GET /health`: JSON monitoring endpoint returning system status, application name, version, and active environment flags.

#### 25. `app/routes/auth_routes.py`
- **Path:** [`app/routes/auth_routes.py`](file:///app/routes/auth_routes.py)
- **Role:** Authentication & Session Controller.
- **Endpoints:**
  - `GET/POST /login`: Renders login form, authenticates user credentials via Bcrypt, guards against session fixation attacks, and redirects to target destination via `is_safe_url` verification.
  - `GET /logout`: Destroys the active session and redirects to login.
  - `GET /profile`: Displays account details and role permissions of the logged-in user.
  - `GET /api/session`: Lightweight JSON endpoint returning authentication status for frontend consumption.

#### 26. `app/routes/academic_routes.py`
- **Path:** [`app/routes/academic_routes.py`](file:///app/routes/academic_routes.py)
- **Role:** Academic Structure & Hierarchy Management.
- **Endpoints:**
  - `GET /academic/`: Unified management hub for academic years, class cohorts, and subjects.
  - `POST /academic/years`: Creates new academic sessions and toggles active status.
  - `POST /academic/classes`: Registers degree classes and sections.
  - `POST /academic/subjects`: Registers subjects in master course catalog.
  - `GET/POST /academic/curriculum/<class_id>`: Configures class-subject mappings and evaluation credit/mark boundaries.

#### 27. `app/routes/student_routes.py`
- **Path:** [`app/routes/student_routes.py`](file:///app/routes/student_routes.py)
- **Role:** Student Directory & Registration Controller.
- **Endpoints:**
  - `GET /students/`: Directory roster supporting multi-column search (name, enrollment number, email) and class filtering.
  - `GET/POST /students/new`: Enrolls individual student profiles with uniqueness validation.
  - `GET/POST /students/edit/<student_id>`: Edits existing student profiles.
  - `POST /students/delete/<student_id>`: Removes student profiles (enforcing relational integrity).
  - `GET/POST /students/bulk`: Batch student enrollment via CSV or Excel spreadsheets.
  - `GET /students/template`: Streams downloadable pre-formatted student enrollment templates.

#### 28. `app/routes/marks_routes.py`
- **Path:** [`app/routes/marks_routes.py`](file:///app/routes/marks_routes.py)
- **Role:** Marks Entry & Ingestion Controller.
- **Endpoints:**
  - `GET/POST /marks/entry`: Interactive grid interface for manual score entry and immediate grade evaluation.
  - `GET/POST /marks/bulk`: Batch spreadsheet upload endpoint delegating to `MarksIngestionService`.
  - `GET /marks/template`: Generates and streams pre-populated evaluation templates for teachers.
  - `GET /marks/terms` & `POST /marks/terms/<term_id>/lock`: Manages examination cycles and executes result locking/freezing to prevent post-publication modifications.

#### 29. `app/routes/analytics_routes.py`
- **Path:** [`app/routes/analytics_routes.py`](file:///app/routes/analytics_routes.py)
- **Role:** Analytical Dashboard & Data API Controller.
- **Endpoints:**
  - `GET /analytics`: Primary web dashboard displaying interactive Chart.js visualizations, subject benchmarks, and early warning at-risk student tables.
  - `GET /api/analytics/overview`: JSON API for class descriptive metrics.
  - `GET /api/analytics/grade-distribution`: JSON API for grade frequency distributions.
  - `GET /api/analytics/subject-comparison`: JSON API for cross-subject metrics.
  - `GET /api/analytics/at-risk`: JSON API listing vulnerable students requiring academic intervention.

#### 30. `app/routes/report_routes.py`
- **Path:** [`app/routes/report_routes.py`](file:///app/routes/report_routes.py)
- **Role:** Academic Reports & Document Export Controller.
- **Endpoints:**
  - `GET /reports/report-cards`: Student directory for selecting and generating individual grade cards.
  - `GET /reports/report-card/<student_id>`: Printable HTML preview of student marksheet.
  - `GET /reports/report-card/<student_id>/pdf`: Binary stream or download of official ReportLab PDF marksheet.
  - `GET /reports/tabulation-register`: Tabular preview of class TR sheet.
  - `GET /reports/tabulation-register/excel`: Generates and downloads styled `openpyxl` Excel Tabulation Register.
  - `GET /reports/class-summary`: HTML preview of Head of Department performance briefing.
  - `GET /reports/class-summary/pdf`: Streams downloadable landscape executive PDF report.

---

### 3.6 Frontend Presentation & Jinja2 Templates (`app/templates/`)

#### 31. `app/templates/base.html`
- **Path:** [`app/templates/base.html`](file:///app/templates/base.html)
- **Role:** Global Master Layout Shell.
- **Description:** Defines standard HTML5 skeleton, meta tags, Google Fonts typography (Inter / Outfit), global CSS imports, top navigation header with user profile badge, responsive mobile menu toggle, flash message toast alerts, and base footer. All other pages extend this layout via `{% extends "base.html" %}`.

#### 32. `app/templates/index.html`
- **Path:** [`app/templates/index.html`](file:///app/templates/index.html)
- **Role:** Landing Dashboard View.
- **Description:** Features hero banner, quick performance KPI summary cards (Total Students, Pass Rate, Class Average, At-Risk Count), quick navigation shortcuts for teachers/admins, and an interactive project milestone development roadmap.

#### 33. `app/templates/auth/login.html`
- **Path:** [`app/templates/auth/login.html`](file:///app/templates/auth/login.html)
- **Role:** Authentication Form.
- **Description:** Clean, centered glassmorphic login interface with username and password inputs, role-based demo credential quick-fill cards, and security warnings.

#### 34. `app/templates/auth/profile.html`
- **Path:** [`app/templates/auth/profile.html`](file:///app/templates/auth/profile.html)
- **Role:** User Profile View.
- **Description:** Displays the authenticated user's profile card, assigned RBAC role permissions, email, and session metadata.

#### 35. `app/templates/academic/index.html`
- **Path:** [`app/templates/academic/index.html`](file:///app/templates/academic/index.html)
- **Role:** Academic Hierarchy Management Interface.
- **Description:** Tabbed/multi-card administrative control center for configuring Academic Years, Class Sections, and Master Course Catalog items with inline creation modals and status toggles.

#### 36. `app/templates/academic/curriculum.html`
- **Path:** [`app/templates/academic/curriculum.html`](file:///app/templates/academic/curriculum.html)
- **Role:** Curriculum & Evaluation Mapping Interface.
- **Description:** Allows administrators and department chairs to map subjects to specific classes, assigning maximum internal marks, external marks, and passing thresholds.

#### 37. `app/templates/students/index.html`
- **Path:** [`app/templates/students/index.html`](file:///app/templates/students/index.html)
- **Role:** Student Directory Table View.
- **Description:** Interactive roster displaying enrolled students with live search by name or roll number, class filter dropdown, action links (edit, delete, view grade card), and pagination controls.

#### 38. `app/templates/students/form.html`
- **Path:** [`app/templates/students/form.html`](file:///app/templates/students/form.html)
- **Role:** Student Enrollment / Edit Form.
- **Description:** Form for inputting student enrollment number, full name, email, and cohort class assignment with validation feedback.

#### 39. `app/templates/students/bulk.html`
- **Path:** [`app/templates/students/bulk.html`](file:///app/templates/students/bulk.html)
- **Role:** Batch Student Enrollment Interface.
- **Description:** File drop zone for uploading CSV/Excel student rosters with instructions, column mapping guides, and sample template download triggers.

#### 40. `app/templates/marks/entry.html`
- **Path:** [`app/templates/marks/entry.html`](file:///app/templates/marks/entry.html)
- **Role:** Manual Marks Evaluation Grid.
- **Description:** Interactive spreadsheet grid for teachers. Allows cohort/subject/term selection and displays rows with student details, internal marks, external marks, absentee checkboxes, and real-time JavaScript total/grade calculation.

#### 41. `app/templates/marks/bulk.html`
- **Path:** [`app/templates/marks/bulk.html`](file:///app/templates/marks/bulk.html)
- **Role:** Batch Marks Upload Interface.
- **Description:** Ingestion interface for uploading course mark spreadsheets. Displays progress indicators, atomic rollback warnings, and error summary banners if errors are detected.

#### 42. `app/templates/marks/terms.html`
- **Path:** [`app/templates/marks/terms.html`](file:///app/templates/marks/terms.html)
- **Role:** Examination Term Administration.
- **Description:** Form for creating new examination terms (e.g., TEE June 2025) and toggling lock/unlock states to prevent unauthorized grade edits once results are finalized.

#### 43. `app/templates/analytics/dashboard.html`
- **Path:** [`app/templates/analytics/dashboard.html`](file:///app/templates/analytics/dashboard.html)
- **Role:** Visual Statistical Analytics Dashboard.
- **Description:** Rich visual analytics cockpit featuring:
  - KPI summary metric cards (Average, Median, Std Dev, Pass Rate).
  - Grade distribution bar chart (Chart.js) showing frequency of `O` through `F` grades.
  - Cross-subject performance comparison radar/bar chart.
  - Early warning table highlighting academically vulnerable students with recommended remedial actions.
  - Merit list highlighting top cohort performers.

#### 44. `app/templates/reports/report_cards_index.html`
- **Path:** [`app/templates/reports/report_cards_index.html`](file:///app/templates/reports/report_cards_index.html)
- **Role:** Report Card Directory.
- **Description:** Cohort selector listing all students in a class with individual links to preview or download their official PDF report card.

#### 45. `app/templates/reports/report_card_preview.html`
- **Path:** [`app/templates/reports/report_card_preview.html`](file:///app/templates/reports/report_card_preview.html)
- **Role:** Marksheet HTML Preview.
- **Description:** Faithful HTML representation of the official student grade sheet formatted with university styling, tabular marks, SGPA breakdown, and print/download triggers.

#### 46. `app/templates/reports/tabulation_register.html`
- **Path:** [`app/templates/reports/tabulation_register.html`](file:///app/templates/reports/tabulation_register.html)
- **Role:** Master Tabulation Register Preview.
- **Description:** Wide table preview of the master examination register showing all subjects side-by-side for every student in the cohort, with an instant trigger to download the styled `.xlsx` file.

#### 47. `app/templates/reports/class_summary.html`
- **Path:** [`app/templates/reports/class_summary.html`](file:///app/templates/reports/class_summary.html)
- **Role:** Executive Performance Summary Preview.
- **Description:** Clean, printable dashboard briefing for academic administrators presenting class distributions, pass percentages, subject difficulty rankings, and faculty signatures.

---

### 3.7 Frontend Design System & Client-Side Scripts (`app/static/`)

#### 48. `app/static/css/main.css`
- **Path:** [`app/static/css/main.css`](file:///app/static/css/main.css)
- **Role:** Core Design System & Global Styles.
- **Description:** Handcrafted Vanilla CSS design system. Establishes HSL color palettes, typography scales, light/dark surface layers, CSS grid and flexbox utility classes, smooth micro-transitions, responsive breakpoints, and glassmorphic card backdrops.

#### 49. `app/static/css/components.css`
- **Path:** [`app/static/css/components.css`](file:///app/static/css/components.css)
- **Role:** Reusable UI Component Styles.
- **Description:** Component-specific CSS rules covering data tables, zebra striping, status badges (pass green, fail red, absent yellow), modal dialogs, form inputs, button states, KPI stat cards, and print media queries.

#### 50. `app/static/js/main.js`
- **Path:** [`app/static/js/main.js`](file:///app/static/js/main.js)
- **Role:** Interactive Client-Side Behaviors.
- **Description:** Core JavaScript file implementing:
  - Interactive evaluation grid listeners that automatically compute total marks, percentage, and letter grade in real-time as teachers type.
  - Chart.js chart initializations and responsive data re-rendering for analytics dashboards.
  - Toast dismissal timers, modal openers, and client-side confirmation dialogs for destructive actions.

---

### 3.8 Automated Unit & Integration Testing Suite (`tests/`)

#### 51. `tests/__init__.py`
- **Path:** [`tests/__init__.py`](file:///tests/__init__.py)
- **Role:** Test Suite Package Initializer.
- **Description:** Enables Python module resolution across test cases.

#### 52. `tests/test_factory.py`
- **Path:** [`tests/test_factory.py`](file:///tests/test_factory.py)
- **Role:** Application Factory & Setup Tests.
- **Description:** Validates configuration loading (`TestingConfig`), in-memory SQLite isolation, context processor variables, and HTTP 200 response on `/health`.

#### 53. `tests/test_auth.py`
- **Path:** [`tests/test_auth.py`](file:///tests/test_auth.py)
- **Role:** Authentication & RBAC Security Tests.
- **Description:** Tests user authentication flows, Bcrypt hash validation, session creation, logout cleanup, role-based protection decorators, and safe URL redirect validation.

#### 54. `tests/test_models.py`
- **Path:** [`tests/test_models.py`](file:///tests/test_models.py)
- **Role:** Relational Schema & ORM Constraint Tests.
- **Description:** Tests database integrity: unique constraints on enrollment numbers, foreign key enforcement, cascading deletes, and model `to_dict()` serialization.

#### 55. `tests/test_academic.py`
- **Path:** [`tests/test_academic.py`](file:///tests/test_academic.py)
- **Role:** Academic Module Functional Tests.
- **Description:** Verifies creation and active toggling of academic sessions, degree classes, course catalog entries, and curriculum threshold mappings.

#### 56. `tests/test_students.py`
- **Path:** [`tests/test_students.py`](file:///tests/test_students.py)
- **Role:** Student Management Tests.
- **Description:** Verifies individual student registration, duplicate enrollment rejection, real-time search queries, and CSV bulk roster upload processing.

#### 57. `tests/test_marks.py`
- **Path:** [`tests/test_marks.py`](file:///tests/test_marks.py)
- **Role:** Grading & Ingestion Engine Tests.
- **Description:** Tests IGNOU 10-point scale grade bracket evaluations, absentee scoring, manual grid submission, atomic rollback on erroneous spreadsheet upload, and enforcement of exam term locks.

#### 58. `tests/test_analytics.py`
- **Path:** [`tests/test_analytics.py`](file:///tests/test_analytics.py)
- **Role:** Statistical Analytics Engine Tests.
- **Description:** Tests Pandas DataFrame generation, vector descriptive statistics (mean, median, standard deviation), grade frequency distributions, subject comparisons, and at-risk student identification logic.

#### 59. `tests/test_reports.py`
- **Path:** [`tests/test_reports.py`](file:///tests/test_reports.py)
- **Role:** Document Export Verification Tests.
- **Description:** Verifies data aggregation and successful generation of ReportLab PDF student report cards, openpyxl multi-column Excel Tabulation Registers, and Executive Class Summary documents.

---

### 3.9 Project Documentation, Manuals & Specifications (`Docs/` & Root)

#### 60. `Docs/academic_project_report.md`
- **Path:** [`Docs/academic_project_report.md`](file:///Docs/academic_project_report.md)
- **Role:** Official Academic Project Report (IGNOU BCSP-064 / MCSP-232).
- **Description:** Comprehensive 700+ line academic document following IGNOU project guidelines. Includes Executive Abstract, Problem Definition, Software Requirements Specification (SRS with Functional and Non-Functional requirements), DFD Level 0, 1, 2, Entity-Relationship (ER) diagram, complete Relational Data Dictionary, Security Implementation, Quality Assurance strategy, and references.

#### 61. `Docs/architecture_plan.md`
- **Path:** [`Docs/architecture_plan.md`](file:///Docs/architecture_plan.md)
- **Role:** Architectural Blueprint & Technical Specification.
- **Description:** Technical specification describing the 3-tier system design, database ER schema, service layer boundaries, data flow pipelines, and UI/UX responsive design tokens.

#### 62. `Docs/implementationplan.md`
- **Path:** [`Docs/implementationplan.md`](file:///Docs/implementationplan.md)
- **Role:** Engineering Milestone & Task Tracker.
- **Description:** Chronological breakdown of project engineering phases (Phases 0 through 6), recording completed milestones, implementation details, and verification steps.

#### 63. `Docs/problemstatement.md`
- **Path:** [`Docs/problemstatement.md`](file:///Docs/problemstatement.md)
- **Role:** Problem Definition & Background Motivation.
- **Description:** Formal explanation of challenges faced by traditional manual tabulation systems in universities and how SRAS addresses them through digital automation.

#### 64. `Docs/user_manual.md`
- **Path:** [`Docs/user_manual.md`](file:///Docs/user_manual.md)
- **Role:** Operations & User Guide.
- **Description:** Step-by-step user manual covering system requirements, installation, role-based user guides (for Administrators, Teachers, and Students), marks entry workflows, analytics interpretation, and troubleshooting.

#### 65. `Docs/project_files_description.md`
- **Path:** [`Docs/project_files_description.md`](file:///Docs/project_files_description.md)
- **Role:** Codebase Manifest & Architectural Dictionary (THIS FILE).
- **Description:** Comprehensive catalog detailing the purpose, symbols, dependencies, and academic relevance of every file in the SRAS repository.

#### 66. `README.md`
- **Path:** [`README.md`](file:///README.md)
- **Role:** Primary Repository Overview & Quick Start.
- **Description:** Showcase document featuring project status badges, capabilities summary, 1-command startup instructions, manual installation walkthrough, default credentials, API references, and project structure summary.

#### 67. `uploads/.gitkeep`
- **Path:** [`uploads/.gitkeep`](file:///uploads/.gitkeep)
- **Role:** Directory Preservation Marker.
- **Description:** Git ignores empty directories by default; `.gitkeep` ensures the `uploads/` directory exists in fresh clones so temporary file uploads can be stored safely.

---

## 4. Inter-Module Dependency & Data Flow Matrix

The table below illustrates how primary application components interact across layers:

| Layer | Component | Relies On (Inward Dependencies) | Consumed By (Outward Consumers) |
| :--- | :--- | :--- | :--- |
| **Configuration** | `app/config.py` | `os`, `pathlib.Path` | `app/__init__.py:create_app`, `run.py` |
| **Factory** | `app/__init__.py` | `Flask`, `SQLAlchemy`, `Bcrypt`, `config.py` | `run.py`, `seed_db.py`, `tests/test_factory.py` |
| **Security** | `app/utils/decorators.py` | `session`, `flask.request` | `app/routes/*.py` |
| **Data Models** | `app/models/*.py` | `app.db`, `Bcrypt` | `app/services/*.py`, `app/routes/*.py`, `seed_db.py` |
| **Grading Service** | `grading_service.py` | `GradingScale`, `GradeRule` models | `Marks` model, `ingestion_service.py`, `marks_routes.py` |
| **Ingestion Service** | `ingestion_service.py`| `pandas`, `GradingService`, `Marks`, `Class` | `marks_routes.py`, `student_routes.py` |
| **Analytics Service** | `analytics_service.py`| `pandas`, `numpy`, `Marks`, `Student` | `analytics_routes.py`, `report_service.py` |
| **Reporting Service** | `report_service.py` | `reportlab`, `openpyxl`, `AnalyticsService` | `report_routes.py`, `tests/test_reports.py` |
| **Controllers** | `app/routes/*.py` | Services, Models, Blueprints | `create_app()` Blueprint registry, Jinja2 Templates |
| **Presentation** | `app/templates/*.html` | `base.html`, Context processors, CSS/JS | Browser client / End users |

---

## 5. IGNOU Viva Voce & Defense Preparation Questions

When defending this project before an IGNOU external examiner or project guide, you may be asked specific architectural and implementation questions regarding the file structure:

### Q1: Why did you use the Application Factory Pattern (`app/__init__.py:create_app`) instead of a simple single-file Flask app?
> **Answer:** The Application Factory pattern decouples application instantiation from configuration. This enables SRAS to dynamically boot into distinct environments (`DevelopmentConfig` with SQLite file persistence, `TestingConfig` with an ultra-fast in-memory database and disabled CSRF, and `ProductionConfig`). It also eliminates circular import cycles between models, services, and route blueprints.

### Q2: What is the benefit of separating business logic into `app/services/` rather than placing it directly inside route functions in `app/routes/`?
> **Answer:** Placing computations like the IGNOU 10-point grade mapping, Pandas statistical aggregations, and ReportLab PDF document compilation inside a dedicated Service layer adheres strictly to the **Single Responsibility Principle (SRP)** and **Fat Models, Thin Controllers** philosophy. Routes only manage HTTP request parsing and response delivery, while service classes remain pure, reusable, and independently unit-testable without requiring a live web request context.

### Q3: How do you prevent out-of-range marks or corrupt records during batch Excel upload?
> **Answer:** In `app/services/ingestion_service.py:ingest_file`, the entire file is pre-validated in a Pandas DataFrame before any database write occurs. Furthermore, all writes are executed within a database transaction block:
> ```python
> try:
>     # Process all valid rows
>     db.session.commit()
> except Exception:
>     db.session.rollback()
> ```
> If even a single row has invalid marks or missing data, an atomic rollback is triggered and an exhaustive error log listing row numbers is returned to the teacher.

### Q4: Why is SQLite PRAGMA foreign keys explicitly enabled in `app/__init__.py`?
> **Answer:** By default, SQLite engine implementations do not enforce foreign key constraints unless explicitly activated on each database connection. In `app/__init__.py`, we hook into SQLAlchemy's engine connect event (`@event.listens_for(Engine, "connect")`) to issue `PRAGMA foreign_keys=ON`, guaranteeing referential integrity and cascading deletions.

---
*Document prepared for Indira Gandhi National Open University (IGNOU) Major Project Submission.*  
*Student Result Analysis System (SRAS) © 2026. All Rights Reserved.*
