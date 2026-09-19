# Student Result Analysis System (SRAS)
## Comprehensive User & Operations Manual

---

### Table of Contents
1. [System Overview & Architecture](#1-system-overview--architecture)
2. [Getting Started & Authentication](#2-getting-started--authentication)
3. [Administrator Guide](#3-administrator-guide)
   - [3.1 Academic Year Management](#31-academic-year-management)
   - [3.2 Class & Cohort Configuration](#32-class--cohort-configuration)
   - [3.3 Subject Catalog Registry](#33-subject-catalog-registry)
   - [3.4 Curriculum & Evaluation Scheme Mapping](#34-curriculum--evaluation-scheme-mapping)
   - [3.5 Exam Terms & Result Locking](#35-exam-terms--result-locking)
   - [3.6 Grading Scales & Rules](#36-grading-scales--rules)
   - [3.7 User Account Administration](#37-user-account-administration)
4. [Teacher & Faculty Guide](#4-teacher--faculty-guide)
   - [4.1 Student Roster & Enrollment](#41-student-roster--enrollment)
   - [4.2 Interactive Marks Entry](#42-interactive-marks-entry)
   - [4.3 Batch Spreadsheet Ingestion (CSV / Excel)](#43-batch-spreadsheet-ingestion-csv--excel)
5. [Statistical Analytics & Performance Dashboard](#5-statistical-analytics--performance-dashboard)
   - [5.1 Key Performance Indicators (KPIs)](#51-key-performance-indicators-kpis)
   - [5.2 Visual Analytics & Charts](#52-visual-analytics--charts)
   - [5.3 Early Warning System (At-Risk Students)](#53-early-warning-system-at-risk-students)
6. [Reporting & Document Generation](#6-reporting--document-generation)
   - [6.1 Individual Student Report Cards (PDF)](#61-individual-student-report-cards-pdf)
   - [6.2 Master Tabulation Register (Excel TR Sheet)](#62-master-tabulation-register-excel-tr-sheet)
   - [6.3 Executive Class Summary Report](#63-executive-class-summary-report)
7. [Troubleshooting & Frequently Asked Questions (FAQ)](#7-troubleshooting--frequently-asked-questions-faq)

---

## 1. System Overview & Architecture

The **Student Result Analysis System (SRAS)** is an institutional-grade academic assessment and result management platform. Developed for higher education institutions such as the Indira Gandhi National Open University (IGNOU) and affiliated colleges, SRAS replaces manual marks entry and fragmented spreadsheets with an automated, relational database platform.

### Key Capabilities:
* **Role-Based Access Control (RBAC):** Dedicated workflows for Administrators and Faculty Members.
* **Automated Grade Computation:** Real-time evaluation of Internal, External, Total marks, Percentages, Letter Grades, and Grade Points according to institutional standards.
* **High-Throughput Spreadsheet Ingestion:** Bulk upload of marks via `.xlsx` and `.csv` files with validation and atomic rollback.
* **Pandas-Powered Analytics:** Vectorized statistical analysis computing class averages, medians, standard deviations, and identifying at-risk learners.
* **Institutional Publishing:** Generation of university-standard PDF report cards, openpyxl-styled multi-column Excel Tabulation Registers, and Executive Summary reports.

---

## 2. Getting Started & Authentication

### 2.1 System Access
Open any modern web browser (Google Chrome, Mozilla Firefox, Microsoft Edge, Safari) and navigate to your institution's SRAS URL:
```text
http://127.0.0.1:5000/
```

### 2.2 Default Demo Credentials
The pre-seeded database provides access with two roles:

| Role | Username | Default Password | Privileges |
| :--- | :--- | :--- | :--- |
| **Administrator** | `admin` | `Admin@123` | Full access to academic configurations, grading scales, term locking, and user accounts. |
| **Faculty / Teacher** | `teacher` | `Teacher@123` | Student enrollment, manual and batch marks entry, class analytics, and report generation. |

### 2.3 Login Workflow
1. Access the **Login** screen at `/login`.
2. Enter your assigned **Username** and **Password**.
3. Click **Sign In**.
4. Upon successful authentication, administrators are redirected to the **Admin Dashboard**, and teachers are redirected to the **Faculty Operations Portal**.
5. To end your session, click your name in the top-right navigation bar and select **Logout**.

```
+-----------------------------------------------------------+
|                      SRAS Portal Login                    |
|                                                           |
|   Username: [ admin                                   ]   |
|   Password: [ ******************                      ]   |
|                                                           |
|                  [   Sign In   ]                          |
|                                                           |
|   (Demo: admin / Admin@123  or  teacher / Teacher@123)   |
+-----------------------------------------------------------+
```

---

## 3. Administrator Guide

Administrators configure the institution's curriculum hierarchy, academic calendar, grading standards, and faculty access.

### 3.1 Academic Year Management
*Path: Admin Menu -> Academic Setup -> Academic Years (`/academic/years`)*

Academic Years represent annual or bi-annual institutional sessions (e.g., `2025-2026`).
1. **Create Session:** Click **+ New Academic Year**, enter the label (e.g., `2025-2026`), and choose whether it is the active academic session.
2. **Active Status:** Exactly one academic year should be designated as active at any given time. This sets the default filter across student enrollment and grade entry screens.

### 3.2 Class & Cohort Configuration
*Path: Admin Menu -> Academic Setup -> Classes (`/academic/classes`)*

Classes represent specific degree cohorts, semesters, and sections (e.g., `BCA-Semester-1`, Section `A`).
1. **Add Class:** Click **+ Add Class**.
2. **Select Academic Year:** Select the associated academic session.
3. **Class Identifier:** Enter Class Name (e.g., `MCA-Semester-2`) and Section (e.g., `A`).
4. **Unique Constraint:** The system automatically prevents duplicate class and section pairings within the same academic year.

### 3.3 Subject Catalog Registry
*Path: Admin Menu -> Academic Setup -> Subjects (`/academic/subjects`)*

The central repository for all accredited courses and subjects offered by the university.
1. **Register Subject:** Click **+ Add Subject**.
2. **Subject Code:** Enter unique course alphanumeric code (e.g., `BCS-011`, `MCS-012`).
3. **Subject Title:** Enter full course title (e.g., `Computer Basics and PC Software`).
4. **Credits:** Assign credit weighting (e.g., `4` credits).

### 3.4 Curriculum & Evaluation Scheme Mapping
*Path: Admin Menu -> Academic Setup -> Class-Subject Mappings (`/academic/curriculum`)*

Defines which subjects are taught in which class, along with the specific marks breakdown.
1. Click **+ Map Subject to Class**.
2. Select target **Class** and **Subject**.
3. Set Evaluation Thresholds:
   - **Max Internal Marks:** Assessment/Assignment component (Default: `30.0`).
   - **Max External Marks:** Term-End Exam (TEE) component (Default: `70.0`).
   - **Pass Marks:** Minimum combined aggregate required to pass (Default: `40.0`).
4. Click **Save Mapping**.

### 3.5 Exam Terms & Result Locking
*Path: Admin Menu -> Examination -> Exam Terms (`/academic/terms`)*

Exam terms represent testing windows (e.g., `TEE June 2025`, `Mid-Term Examination`).
* **Creating Terms:** Specify term name and link it to the appropriate Academic Year.
* **Result Locking Mechanism:**
  - When marks entry and verification are complete, toggle **Lock Term Results**.
  - Once locked, teachers cannot alter scores or ingest new mark sheets for that term.
  - This preserves evaluation audit compliance and protects published records.

### 3.6 Grading Scales & Rules
*Path: Admin Menu -> Settings -> Grading Scales (`/academic/grading`)*

SRAS implements a model-driven grading engine supporting the standard IGNOU 10-point scale:

| Letter Grade | Description | Percentage Range | Grade Point |
| :---: | :---: | :---: | :---: |
| **O** | Outstanding | 85.0% - 100.0% | 10.0 |
| **A+** | Excellent | 75.0% - 84.99% | 9.0 |
| **A** | Very Good | 65.0% - 74.99% | 8.0 |
| **B+** | Good | 55.0% - 64.99% | 7.0 |
| **B** | Above Average | 50.0% - 54.99% | 6.0 |
| **C** | Average / Pass | 40.0% - 49.99% | 5.0 |
| **F** | Fail | Below 40.0% | 0.0 |

Administrators can adjust percentage thresholds or create alternate scales without modifying application code.

### 3.7 User Account Administration
*Path: Admin Menu -> Users (`/admin/users`)*
- Create user accounts for faculty members.
- Assign roles (`TEACHER` or `ADMIN`).
- Deactivate users or reset forgotten passwords.

---

## 4. Teacher & Faculty Guide

Faculty members manage student enrollment, enter marks, perform batch data uploads, review performance analytics, and export official reports.

### 4.1 Student Roster & Enrollment
*Path: Navigation -> Students -> Student Roster (`/students`)*

#### Individual Registration:
1. Click **+ Register Student**.
2. Provide **Enrollment Number** (e.g., `2101294819`), **Full Name**, **Email Address**, and select the assigned **Class & Section**.
3. Click **Enroll Student**.

#### Batch CSV Enrollment:
1. Click **Batch Upload Students**.
2. Prepare a `.csv` file with headers: `enrollment_no,full_name,email`.
3. Select target Class and upload the file.

---

### 4.2 Interactive Marks Entry
*Path: Navigation -> Marks -> Marks Entry (`/marks/entry`)*

Used for direct grading or making individual score adjustments.

```
+---------------------------------------------------------------------------------+
| Class: [ BCA-Semester-1 (A) v ]   Subject: [ BCS-011 v ]   Term: [ TEE June 2025 v ]
+---------------------------------------------------------------------------------+
| Enrollment No | Student Name   | Internal (30) | External (70) | Absent | Grade | Status |
|---------------|----------------|---------------|---------------|--------|-------|--------|
| 2101294810    | Aarav Sharma   | [ 24.0      ] | [ 58.0      ] | [  ]   |   A+  |  PASS  |
| 2101294811    | Priya Patel    | [ 28.0      ] | [ 65.0      ] | [  ]   |   O   |  PASS  |
| 2101294812    | Rohan Gupta    | [  0.0      ] | [  0.0      ] | [ X]   |   F   |  FAIL  |
+---------------------------------------------------------------------------------+
|                               [ Save Changes ]                                  |
+---------------------------------------------------------------------------------+
```

#### Step-by-Step Instructions:
1. **Select Context:** Choose **Class**, **Subject**, and **Exam Term**.
2. **Enter Marks:** 
   - Enter **Internal Marks** (must be within `0` and `max_internal`).
   - Enter **External Marks** (must be within `0` and `max_external`).
   - Instant client-side validation prevents negative scores or values exceeding maximum marks.
3. **Absentee Marking:** If a student was absent, check the **Absent** box. The system automatically sets scores to `0.0` and records `is_absent = True`.
4. **Commit:** Click **Save Marks**. Totals, percentages, and letter grades are recalculated atomically.

---

### 4.3 Batch Spreadsheet Ingestion (CSV / Excel)
*Path: Navigation -> Marks -> Batch Ingestion (`/marks/upload`)*

For high-speed upload of an entire class cohort's exam scores.

#### Workflow:
1. **Download Pre-Formatted Template:**
   - On the Upload page, select **Class**, **Subject**, and click **Download Template**.
   - The system generates an Excel file containing all enrolled students with pre-filled enrollment numbers and student names.
2. **Populate Marks in Excel:**
   - Open the spreadsheet in Excel, LibreOffice, or Google Sheets.
   - Enter marks in the `internal_marks` and `external_marks` columns.
   - For absent students, mark `TRUE` or `1` in the `is_absent` column.
3. **Upload File:**
   - Return to `/marks/upload`, select the **Exam Term**, select the file, and click **Validate & Ingest**.
4. **Validation & Atomic Rollback:**
   - The ingestion service verifies all columns, enrollment numbers, and mark limits before committing.
   - If any cell contains invalid data (e.g., negative mark, letters instead of numbers, mark > maximum), the entire upload is aborted and line-by-line errors are displayed.

---

## 5. Statistical Analytics & Performance Dashboard

*Path: Navigation -> Analytics -> Class Dashboard (`/analytics/dashboard`)*

The analytics dashboard provides real-time academic intelligence powered by Pandas.

### 5.1 Key Performance Indicators (KPIs)
* **Class Average (Mean Score):** Overall aggregate percentage across all students and subjects.
* **Pass Rate:** Percentage of students who successfully cleared all subjects.
* **Top Score:** Highest aggregate percentage achieved in the cohort.
* **At-Risk Count:** Number of students requiring remedial academic intervention.

### 5.2 Visual Analytics & Charts
* **Grade Distribution (Bar Chart):** Visualizes student counts across grade brackets (`O`, `A+`, `A`, `B+`, `B`, `C`, `F`).
* **Subject Performance Comparison (Horizontal Bar / Radar):** Compares average marks and pass rates across all subjects in the curriculum. Quickly highlights courses where students are struggling.
* **Overall Pass vs. Fail (Doughnut Chart):** Cohort clearance breakdown.
* **Rankings Table:** Displays Top 5 academic rankers with total scores and percentages.

### 5.3 Early Warning System (At-Risk Students)
*Path: Navigation -> Analytics -> At-Risk Students (`/analytics/at-risk`)*

SRAS identifies vulnerable students before semester end:
* **Failing Learners:** Students who have failed in one or more subjects.
* **Borderline Performers:** Students scoring between `40.0%` and `45.0%` aggregate.
* **Actionable Support:** Faculty can download the At-Risk roster to schedule targeted tutorials and parent-teacher conferences.

---

## 6. Reporting & Document Generation

*Path: Navigation -> Reports (`/reports`)*

SRAS produces formal institutional reports ready for distribution and archiving.

### 6.1 Individual Student Report Cards (PDF)
*Path: Reports -> Report Cards (`/reports/report-cards`)*
1. Select **Class** and **Exam Term**.
2. Click **View** beside any student to preview their report card.
3. Click **Download Official PDF**.
4. **Report Card Features:**
   - University/Institution Header and crest placeholder.
   - Student metadata: Enrollment Number, Name, Class, Term.
   - Tabular subject breakdown: Subject Code, Title, Max Marks, Internal, External, Total, Grade, Status.
   - Aggregate summary: Grand Total, Percentage, Overall CGPA, Final Result.
   - Controller of Examinations and Faculty signature placeholders.

### 6.2 Master Tabulation Register (Excel TR Sheet)
*Path: Reports -> Tabulation Register (`/reports/tabulation-register`)*
1. Select **Class** and **Exam Term**.
2. View the interactive online register.
3. Click **Export Master TR (Excel)**.
4. An `.xlsx` workbook is generated with:
   - Nested column headers for each subject: `Int`, `Ext`, `Tot`, `Grd`.
   - Grand Total, Percentage, and Pass/Fail status.
   - Professional openpyxl formatting: styled header banners, borders, and alternating zebra rows.

### 6.3 Executive Class Summary Report
*Path: Reports -> Class Performance Summary (`/reports/class-summary`)*
1. Select **Class** and **Exam Term**.
2. Click **Generate Executive Summary**.
3. View executive-level metrics, subject-by-subject clearance tables, and grade frequency distribution.
4. Click **Print Summary** for faculty council and Head of Department meetings.

---

## 7. Troubleshooting & Frequently Asked Questions (FAQ)

### Q1: The system indicates "Exam Term is Locked" when trying to save marks.
**Answer:** The administrator has locked this exam term to prevent unauthorized alterations. Contact the exam coordinator or administrator to unlock the term if legitimate corrections are required.

### Q2: Batch Excel upload failed with error "Row 14: Mark 78.0 exceeds maximum external mark 70.0".
**Answer:** Each subject has a configured maximum mark threshold in curriculum mapping. Correct the score in your spreadsheet to be within the permissible bounds and re-upload. The system uses atomic transactions, so no corrupt data was saved.

### Q3: How do I mark a student who was absent from the exam?
**Answer:** 
- In manual entry: check the **Absent** checkbox.
- In Excel upload: set the `is_absent` column to `TRUE` or `1`. Absent students are awarded `0` marks and flagged as absent.

### Q4: How do I reset the system database or reload sample demo data?
**Answer:** In the project root terminal, run:
```powershell
.\venv\Scripts\python seed_db.py
```
This safely updates and ensures all demo users, sample classes, subjects, and test marks are present.

---
*End of User & Operations Manual — Student Result Analysis System (SRAS)*
