"""Statistical Analytics Service for Student Result Analysis System.

Vectorized calculations using Pandas for descriptive metrics, grade distributions,
cross-subject benchmarking, at-risk student identification, and merit rankings.
"""

from typing import Dict, Any, List, Optional
import numpy as np
import pandas as pd
from sqlalchemy.orm import joinedload
from app import db
from app.models.academic import Class, ClassSubject, Subject
from app.models.student import Student
from app.models.result import Marks, ExamTerm
from app.services.grading_service import GradingService


class AnalyticsService:
    """Core analytics engine leveraging Pandas for vector statistical computations."""

    IGNOU_GRADES = ['O', 'A+', 'A', 'B+', 'B', 'C', 'F']

    @classmethod
    def get_class_term_dataframe(cls, class_id: int, term_id: int) -> pd.DataFrame:
        """
        Query and convert raw marks data for a cohort and term into a typed Pandas DataFrame.
        """
        marks_query = (
            db.session.query(Marks)
            .join(Student, Marks.student_id == Student.student_id)
            .join(ClassSubject, Marks.class_subject_id == ClassSubject.class_subject_id)
            .join(Subject, ClassSubject.subject_id == Subject.subject_id)
            .filter(
                Student.class_id == class_id,
                Marks.term_id == term_id
            )
            .options(
                joinedload(Marks.student),
                joinedload(Marks.class_subject).joinedload(ClassSubject.subject_ref)
            )
            .all()
        )

        if not marks_query:
            return pd.DataFrame(columns=[
                'mark_id', 'student_id', 'enrollment_no', 'student_name',
                'subject_id', 'subject_code', 'subject_name',
                'max_internal', 'max_external', 'max_total', 'pass_marks',
                'internal_marks', 'external_marks', 'total_marks',
                'percentage', 'grade', 'grade_point', 'is_absent', 'is_passed'
            ])

        records = []
        for m in marks_query:
            cs = m.class_subject
            sub = cs.subject_ref if cs else None
            st = m.student
            records.append({
                'mark_id': m.mark_id,
                'student_id': m.student_id,
                'enrollment_no': st.enrollment_no if st else '',
                'student_name': st.full_name if st else '',
                'subject_id': sub.subject_id if sub else cs.subject_id,
                'subject_code': sub.subject_code if sub else '',
                'subject_name': sub.subject_name if sub else '',
                'max_internal': cs.max_internal_marks if cs else 30.0,
                'max_external': cs.max_external_marks if cs else 70.0,
                'max_total': cs.max_total_marks if cs else 100.0,
                'pass_marks': cs.pass_marks if cs else 40.0,
                'internal_marks': float(m.internal_marks or 0.0),
                'external_marks': float(m.external_marks or 0.0),
                'total_marks': float(m.total_marks or 0.0),
                'percentage': float(m.percentage or 0.0),
                'grade': m.grade or 'F',
                'grade_point': float(m.grade_point or 0.0),
                'is_absent': bool(m.is_absent),
                'is_passed': bool(m.is_passed)
            })

        return pd.DataFrame(records)

    @classmethod
    def compute_overview_metrics(cls, class_id: int, term_id: int) -> Dict[str, Any]:
        """
        Compute high-level descriptive and performance statistics for a class and term.
        """
        target_class = db.session.get(Class, class_id)
        target_term = db.session.get(ExamTerm, term_id)
        total_enrolled = Student.query.filter_by(class_id=class_id).count() if target_class else 0

        df = cls.get_class_term_dataframe(class_id, term_id)

        if df.empty:
            return {
                'class_id': class_id,
                'class_name': target_class.display_name if target_class else '',
                'term_id': term_id,
                'term_name': target_term.term_name if target_term else '',
                'total_enrolled': total_enrolled,
                'total_appeared': 0,
                'total_passed': 0,
                'total_failed': 0,
                'pass_percentage': 0.0,
                'class_average': 0.0,
                'median_score': 0.0,
                'standard_deviation': 0.0,
                'highest_score': 0.0,
                'lowest_score': 0.0,
                'top_student': None,
                'has_data': False
            }

        # Students who appeared in at least one examination
        appeared_student_ids = df[~df['is_absent']]['student_id'].unique().tolist()
        total_appeared = len(appeared_student_ids)

        if total_appeared == 0:
            return {
                'class_id': class_id,
                'class_name': target_class.display_name if target_class else '',
                'term_id': term_id,
                'term_name': target_term.term_name if target_term else '',
                'total_enrolled': total_enrolled,
                'total_appeared': 0,
                'total_passed': 0,
                'total_failed': 0,
                'pass_percentage': 0.0,
                'class_average': 0.0,
                'median_score': 0.0,
                'standard_deviation': 0.0,
                'highest_score': 0.0,
                'lowest_score': 0.0,
                'top_student': None,
                'has_data': True
            }

        # Student-level aggregates
        student_group = df.groupby(['student_id', 'enrollment_no', 'student_name'])
        student_stats = student_group.agg(
            total_obtained=('total_marks', 'sum'),
            max_possible=('max_total', 'sum'),
            avg_pct=('percentage', lambda p: p[~df.loc[p.index, 'is_absent']].mean() if not p[~df.loc[p.index, 'is_absent']].empty else 0.0),
            fail_count=('is_passed', lambda p: (p == False).sum()),
            absent_count=('is_absent', lambda a: (a == True).sum()),
            total_subs=('subject_id', 'count')
        ).reset_index()

        # Passed: student appeared in at least 1 subject and failed in 0 subjects
        student_stats['is_overall_passed'] = (student_stats['fail_count'] == 0) & (student_stats['absent_count'] < student_stats['total_subs'])
        total_passed = int(student_stats['is_overall_passed'].sum())
        total_failed = int(total_appeared - total_passed)
        pass_percentage = round((total_passed / total_appeared) * 100.0, 2) if total_appeared > 0 else 0.0

        # Descriptive metrics based on student average percentages
        student_pcts = student_stats[student_stats['absent_count'] < student_stats['total_subs']]['avg_pct']
        class_average = round(float(student_pcts.mean()), 2) if not student_pcts.empty else 0.0
        median_score = round(float(student_pcts.median()), 2) if not student_pcts.empty else 0.0
        std_dev = round(float(student_pcts.std(ddof=0)), 2) if len(student_pcts) > 0 else 0.0
        highest_score = round(float(student_pcts.max()), 2) if not student_pcts.empty else 0.0
        lowest_score = round(float(student_pcts.min()), 2) if not student_pcts.empty else 0.0

        # Top student identification
        top_student = None
        if not student_pcts.empty:
            top_row = student_stats.sort_values(by=['avg_pct', 'total_obtained'], ascending=False).iloc[0]
            top_grade, _, _ = GradingService.get_grade_for_percentage(float(top_row['avg_pct']))
            top_student = {
                'student_id': int(top_row['student_id']),
                'enrollment_no': str(top_row['enrollment_no']),
                'student_name': str(top_row['student_name']),
                'percentage': round(float(top_row['avg_pct']), 2),
                'total_obtained': round(float(top_row['total_obtained']), 2),
                'grade': top_grade
            }

        return {
            'class_id': class_id,
            'class_name': target_class.display_name if target_class else '',
            'term_id': term_id,
            'term_name': target_term.term_name if target_term else '',
            'total_enrolled': total_enrolled,
            'total_appeared': total_appeared,
            'total_passed': total_passed,
            'total_failed': total_failed,
            'pass_percentage': pass_percentage,
            'class_average': class_average,
            'median_score': median_score,
            'standard_deviation': std_dev,
            'highest_score': highest_score,
            'lowest_score': lowest_score,
            'top_student': top_student,
            'has_data': True
        }

    @classmethod
    def compute_grade_distribution(cls, class_id: int, term_id: int) -> Dict[str, Any]:
        """
        Compute frequency count and percentage across IGNOU 10-point grade brackets.
        """
        df = cls.get_class_term_dataframe(class_id, term_id)
        
        # Initialize default zero counts for all IGNOU grades
        counts = {g: 0 for g in cls.IGNOU_GRADES}
        percentages = {g: 0.0 for g in cls.IGNOU_GRADES}

        if df.empty:
            return {
                'labels': cls.IGNOU_GRADES,
                'counts': [0] * len(cls.IGNOU_GRADES),
                'percentages': [0.0] * len(cls.IGNOU_GRADES),
                'total_evaluations': 0
            }

        # Compute grade frequencies across all valid subject entries
        grade_series = df['grade'].value_counts()
        total_evaluations = len(df)

        for grade, count in grade_series.items():
            if grade in counts:
                counts[grade] = int(count)

        if total_evaluations > 0:
            for g in cls.IGNOU_GRADES:
                percentages[g] = round((counts[g] / total_evaluations) * 100.0, 2)

        return {
            'labels': cls.IGNOU_GRADES,
            'counts': [counts[g] for g in cls.IGNOU_GRADES],
            'percentages': [percentages[g] for g in cls.IGNOU_GRADES],
            'total_evaluations': total_evaluations
        }

    @classmethod
    def compute_subject_comparison(cls, class_id: int, term_id: int) -> Dict[str, Any]:
        """
        Compare average scores and pass rates per subject within the cohort to identify challenging subjects.
        """
        df = cls.get_class_term_dataframe(class_id, term_id)

        if df.empty:
            return {
                'subjects': [],
                'labels': [],
                'averages': [],
                'pass_rates': [],
                'most_challenging': None,
                'top_performing': None
            }

        results = []
        grouped = df.groupby(['subject_id', 'subject_code', 'subject_name'])

        for (sub_id, sub_code, sub_name), group in grouped:
            total_students = len(group)
            valid_group = group[~group['is_absent']]
            appeared = len(valid_group)
            absent = total_students - appeared
            passed = int((group['is_passed'] == True).sum())
            failed = int((group['is_passed'] == False).sum())

            avg_total = round(float(valid_group['total_marks'].mean()), 2) if appeared > 0 else 0.0
            avg_pct = round(float(valid_group['percentage'].mean()), 2) if appeared > 0 else 0.0
            pass_rate = round((passed / appeared) * 100.0, 2) if appeared > 0 else 0.0
            highest = round(float(valid_group['total_marks'].max()), 2) if appeared > 0 else 0.0
            lowest = round(float(valid_group['total_marks'].min()), 2) if appeared > 0 else 0.0

            results.append({
                'subject_id': int(sub_id),
                'subject_code': str(sub_code),
                'subject_name': str(sub_name),
                'total_candidates': total_students,
                'appeared': appeared,
                'absent': absent,
                'passed': passed,
                'failed': failed,
                'pass_rate': pass_rate,
                'average_marks': avg_total,
                'average_percentage': avg_pct,
                'highest_marks': highest,
                'lowest_marks': lowest
            })

        # Sort by pass_rate ascending to identify the most challenging course
        sorted_by_difficulty = sorted(results, key=lambda x: (x['pass_rate'], x['average_percentage']))
        most_challenging = sorted_by_difficulty[0] if sorted_by_difficulty else None
        top_performing = sorted_by_difficulty[-1] if sorted_by_difficulty else None

        return {
            'subjects': results,
            'labels': [s['subject_code'] for s in results],
            'averages': [s['average_percentage'] for s in results],
            'pass_rates': [s['pass_rate'] for s in results],
            'most_challenging': most_challenging,
            'top_performing': top_performing
        }

    @classmethod
    def identify_at_risk_students(cls, class_id: int, term_id: int) -> List[Dict[str, Any]]:
        """
        Detect academically vulnerable students requiring remedial attention based on:
        1. Subjects failed
        2. Borderline aggregate percentage (40% - 45%)
        3. Trend score drops compared to previous terms
        """
        df = cls.get_class_term_dataframe(class_id, term_id)

        if df.empty:
            return []

        # Find previous term for trend drop analysis
        current_term = db.session.get(ExamTerm, term_id)
        prev_term = None
        if current_term and current_term.year_id:
            prev_term = (
                ExamTerm.query.filter(
                    ExamTerm.year_id == current_term.year_id,
                    ExamTerm.term_id < current_term.term_id
                )
                .order_by(ExamTerm.term_id.desc())
                .first()
            )

        prev_student_avgs = {}
        if prev_term:
            prev_df = cls.get_class_term_dataframe(class_id, prev_term.term_id)
            if not prev_df.empty:
                prev_valid = prev_df[~prev_df['is_absent']]
                if not prev_valid.empty:
                    prev_avgs = prev_valid.groupby('student_id')['percentage'].mean().to_dict()
                    prev_student_avgs = {int(k): float(v) for k, v in prev_avgs.items()}

        at_risk_list = []
        student_groups = df.groupby(['student_id', 'enrollment_no', 'student_name'])

        for (s_id, enr, name), group in student_groups:
            valid_marks = group[~group['is_absent']]
            total_subjects = len(group)
            appeared_subs = len(valid_marks)
            failed_subs = group[(group['is_passed'] == False) & (~group['is_absent'])]
            absent_subs = group[group['is_absent'] == True]
            failed_count = len(failed_subs)
            absent_count = len(absent_subs)
            failed_sub_codes = failed_subs['subject_code'].tolist()
            absent_sub_codes = absent_subs['subject_code'].tolist()

            avg_pct = round(float(valid_marks['percentage'].mean()), 2) if appeared_subs > 0 else 0.0
            prev_avg = prev_student_avgs.get(int(s_id))
            score_drop = round(prev_avg - avg_pct, 2) if prev_avg is not None else 0.0

            # Determine risk factors
            is_at_risk = False
            risk_level = 'LOW'
            reasons = []
            recommendation = ''

            # Factor 1: Failing in subjects
            if failed_count >= 2:
                is_at_risk = True
                risk_level = 'HIGH'
                reasons.append(f"Failed in {failed_count} subjects: {', '.join(failed_sub_codes)}")
                recommendation = "Intensive Remedial Coaching & Academic Advisor Counseling"
            elif failed_count == 1:
                is_at_risk = True
                risk_level = 'MEDIUM'
                reasons.append(f"Failed in {failed_sub_codes[0]}")
                recommendation = f"Subject Tutorial Support in {failed_sub_codes[0]}"

            # Factor 2: Borderline Aggregate (40% - 45%)
            if 40.0 <= avg_pct <= 45.0 and appeared_subs > 0:
                is_at_risk = True
                if risk_level != 'HIGH':
                    risk_level = 'MEDIUM'
                reasons.append(f"Borderline score ({avg_pct}%) near failure threshold")
                if not recommendation:
                    recommendation = "Targeted Academic Reinforcement Sessions"

            # Factor 3: Significant Score Drop (> 10% decline)
            if score_drop >= 10.0:
                is_at_risk = True
                reasons.append(f"Sharp performance drop of {score_drop}% from previous term")
                if risk_level == 'LOW':
                    risk_level = 'MEDIUM'
                if not recommendation:
                    recommendation = "Mentor Review & Attendance Investigation"

            # Factor 4: Complete Absence
            if appeared_subs == 0 and total_subjects > 0:
                is_at_risk = True
                risk_level = 'HIGH'
                reasons.append("Absent in all examination papers")
                recommendation = "Contact Candidate Regarding Examination Non-Attendance"

            if is_at_risk:
                grade_letter, _, _ = GradingService.get_grade_for_percentage(avg_pct)
                at_risk_list.append({
                    'student_id': int(s_id),
                    'enrollment_no': str(enr),
                    'student_name': str(name),
                    'average_percentage': avg_pct,
                    'failed_count': failed_count,
                    'failed_subjects': failed_sub_codes,
                    'risk_level': risk_level,
                    'reasons': reasons,
                    'recommendation': recommendation,
                    'grade': grade_letter,
                    'score_drop': score_drop if score_drop > 0 else 0.0
                })

        # Order by risk severity (HIGH -> MEDIUM -> LOW), then lowest percentage
        priority_map = {'HIGH': 0, 'MEDIUM': 1, 'LOW': 2}
        at_risk_list.sort(key=lambda x: (priority_map.get(x['risk_level'], 3), x['average_percentage']))
        return at_risk_list

    @classmethod
    def compute_top_performers(cls, class_id: int, term_id: int, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Rank top academic performers by aggregate percentage and marks.
        """
        df = cls.get_class_term_dataframe(class_id, term_id)
        if df.empty:
            return []

        # Only evaluate students who appeared in subjects
        student_group = df.groupby(['student_id', 'enrollment_no', 'student_name'])
        records = []

        for (s_id, enr, name), group in student_group:
            valid_marks = group[~group['is_absent']]
            if valid_marks.empty:
                continue

            total_obtained = round(float(valid_marks['total_marks'].sum()), 2)
            max_possible = round(float(group['max_total'].sum()), 2)
            avg_pct = round(float(valid_marks['percentage'].mean()), 2)
            has_failed = bool((group['is_passed'] == False).any())
            is_absent_any = bool((group['is_absent'] == True).any())

            grade_letter, grade_point, desc = GradingService.get_grade_for_percentage(avg_pct)

            records.append({
                'student_id': int(s_id),
                'enrollment_no': str(enr),
                'student_name': str(name),
                'total_obtained': total_obtained,
                'max_possible': max_possible,
                'percentage': avg_pct,
                'grade': grade_letter,
                'grade_point': grade_point,
                'grade_desc': desc,
                'has_failed': has_failed,
                'is_absent_any': is_absent_any
            })

        # Sort: first students who passed everything, ordered by percentage desc, total_obtained desc
        records.sort(key=lambda x: (not x['has_failed'] and not x['is_absent_any'], x['percentage'], x['total_obtained']), reverse=True)

        top_list = []
        for rank, r in enumerate(records[:limit], start=1):
            r['rank'] = rank
            top_list.append(r)

        return top_list
