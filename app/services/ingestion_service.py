"""High-speed CSV / Excel Batch Marks Ingestion Service with Atomic Transactions."""

import io
import csv
from typing import Dict, Any, Tuple
import pandas as pd
from app import db
from app.models.academic import Class, Subject, ClassSubject
from app.models.student import Student
from app.models.result import ExamTerm, Marks, GradingScale
from app.services.grading_service import GradingService


class MarksIngestionService:
    """Service handling high-throughput spreadsheet ingestion for student marks."""

    @classmethod
    def ingest_file(
        cls,
        file_obj,
        filename: str,
        class_id: int,
        subject_id: int,
        term_id: int,
        user_id: int
    ) -> Dict[str, Any]:
        """
        Parse and validate an uploaded CSV or Excel spreadsheet.
        Guarantees atomic rollback: if ANY row fails validation, 0 database writes occur.
        """
        # 1. Validation of Context Entities
        term = db.session.get(ExamTerm, term_id)
        if not term:
            return {'success': False, 'errors': ['Specified Exam Term does not exist.']}
        if term.is_locked:
            return {'success': False, 'errors': [f'Exam Term "{term.term_name}" is locked. Marks cannot be modified.']}

        target_class = db.session.get(Class, class_id)
        if not target_class:
            return {'success': False, 'errors': ['Selected Class does not exist.']}

        mapping = ClassSubject.query.filter_by(class_id=class_id, subject_id=subject_id).first()
        if not mapping:
            return {'success': False, 'errors': ['Selected subject is not mapped to this class in the curriculum.']}

        # 2. Read spreadsheet into Pandas DataFrame
        filename_lower = filename.lower()
        try:
            if filename_lower.endswith('.csv'):
                # Read as UTF-8 with fallback
                try:
                    df = pd.read_csv(file_obj, encoding='utf-8')
                except UnicodeDecodeError:
                    file_obj.seek(0)
                    df = pd.read_csv(file_obj, encoding='latin1')
            elif filename_lower.endswith(('.xlsx', '.xls')):
                df = pd.read_excel(file_obj)
            else:
                return {'success': False, 'errors': ['Unsupported file format. Please upload a .csv or .xlsx file.']}
        except Exception as e:
            return {'success': False, 'errors': [f'Failed to parse spreadsheet file: {str(e)}']}

        if df.empty:
            return {'success': False, 'errors': ['The uploaded file contains no data rows.']}

        # 3. Clean and normalize column headers
        df.columns = [str(c).strip().lower() for c in df.columns]

        # Alias resolution
        header_map = {}
        for col in df.columns:
            if 'enroll' in col or 'roll' in col:
                header_map['enrollment_no'] = col
            elif 'internal' in col:
                header_map['internal_marks'] = col
            elif 'external' in col or 'tee' in col or 'exam' in col:
                header_map['external_marks'] = col
            elif 'absent' in col:
                header_map['is_absent'] = col

        if 'enrollment_no' not in header_map or 'internal_marks' not in header_map or 'external_marks' not in header_map:
            missing = []
            if 'enrollment_no' not in header_map:
                missing.append('enrollment_no')
            if 'internal_marks' not in header_map:
                missing.append('internal_marks')
            if 'external_marks' not in header_map:
                missing.append('external_marks')
            return {
                'success': False,
                'errors': [f'Missing required column(s): {", ".join(missing)}. File must include enrollment_no, internal_marks, and external_marks.']
            }

        enr_col = header_map['enrollment_no']
        int_col = header_map['internal_marks']
        ext_col = header_map['external_marks']
        abs_col = header_map.get('is_absent')

        # 4. Fetch enrolled students mapping
        enrolled_students = {s.enrollment_no: s.student_id for s in target_class.students}

        errors = []
        parsed_rows = []
        seen_in_file = set()

        max_in = mapping.max_internal_marks
        max_ex = mapping.max_external_marks
        pass_cutoff = mapping.pass_marks

        active_scale = GradingService.get_active_scale()

        # 5. Row-by-Row Strict Validation
        for idx, row in df.iterrows():
            row_num = idx + 2  # Excel/CSV line number (1-based + 1 for header)
            raw_enr = row.get(enr_col)

            if pd.isna(raw_enr) or not str(raw_enr).strip():
                errors.append(f'Row {row_num}: Enrollment number is missing.')
                continue

            enr_str = str(raw_enr).strip()
            # If pandas read enrollment as float (e.g. 240100101.0), convert safely
            if enr_str.endswith('.0') and enr_str[:-2].isdigit():
                enr_str = enr_str[:-2]

            if enr_str in seen_in_file:
                errors.append(f'Row {row_num}: Duplicate enrollment "{enr_str}" in uploaded file.')
                continue
            seen_in_file.add(enr_str)

            if enr_str not in enrolled_students:
                errors.append(f'Row {row_num}: Student "{enr_str}" is not enrolled in {target_class.display_name}.')
                continue

            student_id = enrolled_students[enr_str]

            # Parse absent flag
            is_absent = False
            if abs_col and not pd.isna(row.get(abs_col)):
                raw_abs = row.get(abs_col)
                if isinstance(raw_abs, bool):
                    is_absent = raw_abs
                elif isinstance(raw_abs, (int, float)):
                    is_absent = bool(int(raw_abs) == 1)
                else:
                    abs_val = str(raw_abs).strip().lower()
                    if abs_val in ['1', '1.0', 'true', 'yes', 'y', 'absent', 'ab']:
                        is_absent = True

            # Parse numerical marks
            if is_absent:
                in_marks = 0.0
                ex_marks = 0.0
            else:
                raw_in = row.get(int_col)
                raw_ex = row.get(ext_col)

                try:
                    in_marks = float(raw_in) if not pd.isna(raw_in) else 0.0
                except (ValueError, TypeError):
                    errors.append(f'Row {row_num}: Internal marks "{raw_in}" is not a valid number.')
                    continue

                try:
                    ex_marks = float(raw_ex) if not pd.isna(raw_ex) else 0.0
                except (ValueError, TypeError):
                    errors.append(f'Row {row_num}: External marks "{raw_ex}" is not a valid number.')
                    continue

                if in_marks < 0.0 or in_marks > max_in:
                    errors.append(f'Row {row_num}: Internal marks ({in_marks}) must be between 0 and maximum ({max_in}).')
                    continue

                if ex_marks < 0.0 or ex_marks > max_ex:
                    errors.append(f'Row {row_num}: External marks ({ex_marks}) must be between 0 and maximum ({max_ex}).')
                    continue

            parsed_rows.append({
                'student_id': student_id,
                'enrollment_no': enr_str,
                'internal_marks': in_marks,
                'external_marks': ex_marks,
                'is_absent': is_absent
            })

        # Atomic rule: If ANY error occurred, rollback and return error list
        if errors:
            return {
                'success': False,
                'errors': errors,
                'total_rows': len(df)
            }

        if not parsed_rows:
            return {'success': False, 'errors': ['No valid marks records found in the spreadsheet to import.']}

        # 6. Apply database writes within atomic transaction
        try:
            passed_count = 0
            failed_count = 0
            absent_count = 0

            for entry in parsed_rows:
                # Calculate evaluation
                eval_res = GradingService.evaluate(
                    internal_marks=entry['internal_marks'],
                    external_marks=entry['external_marks'],
                    max_internal=max_in,
                    max_external=max_ex,
                    pass_marks=pass_cutoff,
                    is_absent=entry['is_absent'],
                    scale=active_scale
                )

                if eval_res['is_absent']:
                    absent_count += 1
                elif eval_res['is_passed']:
                    passed_count += 1
                else:
                    failed_count += 1

                # Check existing mark record
                mark = Marks.query.filter_by(
                    student_id=entry['student_id'],
                    class_subject_id=mapping.class_subject_id,
                    term_id=term_id
                ).first()

                if mark:
                    mark.internal_marks = eval_res['internal_marks']
                    mark.external_marks = eval_res['external_marks']
                    mark.total_marks = eval_res['total_marks']
                    mark.percentage = eval_res['percentage']
                    mark.grade = eval_res['grade']
                    mark.grade_point = eval_res['grade_point']
                    mark.is_absent = eval_res['is_absent']
                    mark.is_passed = eval_res['is_passed']
                    mark.updated_by = user_id
                else:
                    mark = Marks(
                        student_id=entry['student_id'],
                        class_subject_id=mapping.class_subject_id,
                        term_id=term_id,
                        internal_marks=eval_res['internal_marks'],
                        external_marks=eval_res['external_marks'],
                        total_marks=eval_res['total_marks'],
                        percentage=eval_res['percentage'],
                        grade=eval_res['grade'],
                        grade_point=eval_res['grade_point'],
                        is_absent=eval_res['is_absent'],
                        is_passed=eval_res['is_passed'],
                        updated_by=user_id
                    )
                    db.session.add(mark)

            db.session.commit()

            return {
                'success': True,
                'total_processed': len(parsed_rows),
                'passed': passed_count,
                'failed': failed_count,
                'absent': absent_count,
                'class_name': target_class.display_name,
                'subject_code': mapping.subject.subject_code if mapping.subject else None
            }

        except Exception as e:
            db.session.rollback()
            return {'success': False, 'errors': [f'Database transaction error: {str(e)}']}

    @classmethod
    def generate_template(
        cls,
        class_id: int,
        subject_id: int,
        file_format: str = 'csv'
    ) -> Tuple[bytes, str, str]:
        """
        Generate a pre-populated evaluation spreadsheet pre-filled with enrolled students.
        Returns: (file_bytes, mimetype, filename)
        """
        target_class = db.session.get(Class, class_id)
        subject = db.session.get(Subject, subject_id)
        mapping = ClassSubject.query.filter_by(class_id=class_id, subject_id=subject_id).first()

        max_in = mapping.max_internal_marks if mapping else 30.0
        max_ex = mapping.max_external_marks if mapping else 70.0
        sub_code = subject.subject_code if subject else 'SUBJECT'

        # Rows data
        rows = []
        students = sorted(target_class.students, key=lambda s: s.enrollment_no) if target_class else []
        for s in students:
            rows.append({
                'enrollment_no': s.enrollment_no,
                'student_name': s.full_name,
                f'internal_marks (max: {max_in})': '',
                f'external_marks (max: {max_ex})': '',
                'is_absent': '0'
            })

        if not rows:
            # Provide sample placeholders if class has no students yet
            rows = [
                {
                    'enrollment_no': '240100101',
                    'student_name': 'Sample Student',
                    f'internal_marks (max: {max_in})': '',
                    f'external_marks (max: {max_ex})': '',
                    'is_absent': '0'
                }
            ]

        df = pd.DataFrame(rows)

        clean_class = (target_class.display_name if target_class else 'Class').replace(' ', '_').replace('/', '-')
        filename_base = f"{clean_class}_{sub_code}_marks_template"

        if file_format.lower() in ['excel', 'xlsx']:
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                df.to_excel(writer, index=False, sheet_name='MarksEntry')
            return output.getvalue(), 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', f"{filename_base}.xlsx"
        else:
            output = io.StringIO()
            # Standard simplified column names for CSV
            csv_df = pd.DataFrame([
                {
                    'enrollment_no': r['enrollment_no'],
                    'student_name': r['student_name'],
                    'internal_marks': '',
                    'external_marks': '',
                    'is_absent': r['is_absent']
                } for r in rows
            ])
            csv_df.to_csv(output, index=False)
            return output.getvalue().encode('utf-8'), 'text/csv', f"{filename_base}.csv"
