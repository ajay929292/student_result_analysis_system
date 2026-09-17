"""
Database Seeding Script for Student Result Analysis System.
Populates standard IGNOU 10-point grading scales, administrator/teacher accounts,
sample academic classes, master subject registry, and demo students.
"""

import os
import sys
from pathlib import Path

# Ensure project root is in sys.path
project_root = Path(__file__).resolve().parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from dotenv import load_dotenv

load_dotenv()

from app import create_app, db
from app.models import (
    User, AcademicYear, Class, Subject, ClassSubject,
    Student, ExamTerm, GradingScale, GradeRule, Marks)

app = create_app(os.environ.get('FLASK_ENV', 'development'))


def seed_database():
    with app.app_context():
        print("Initializing relational database schema...")
        db.create_all()

        # ----------------------------------------------------------------------
        # 1. Seed Default Users
        # ----------------------------------------------------------------------
        print("\n[1/6] Seeding User Accounts...")
        users_data = [
            {
                'username': 'admin',
                'password': 'Admin@12345',
                'role': User.ROLE_ADMIN,
                'full_name': 'System Administrator',
                'email': 'admin@ignou.ac.in'
            },
            {
                'username': 'teacher1',
                'password': 'Teacher@12345',
                'role': User.ROLE_TEACHER,
                'full_name': 'Prof. Rajesh Kumar',
                'email': 'rajesh.kumar@ignou.ac.in'
            },
            {
                'username': 'student1',
                'password': 'Student@12345',
                'role': User.ROLE_STUDENT,
                'full_name': 'Rahul Sharma',
                'email': 'rahul.sharma@ignou.ac.in'
            }
        ]

        seeded_users = {}
        for u in users_data:
            existing = User.query.filter_by(username=u['username']).first()
            if not existing:
                user = User(
                    username=u['username'],
                    role=u['role'],
                    full_name=u['full_name'],
                    email=u['email']
                )
                user.set_password(u['password'])
                db.session.add(user)
                seeded_users[u['username']] = user
                print(f"  + Created User: {u['username']} ({u['role']})")
            else:
                seeded_users[u['username']] = existing
                print(f"  * User exists: {u['username']}")

        db.session.commit()

        # ----------------------------------------------------------------------
        # 2. Seed IGNOU Standard 10-Point Grading Scale
        # ----------------------------------------------------------------------
        print("\n[2/6] Seeding IGNOU 10-Point Grading Scale...")
        scale = GradingScale.query.filter_by(scale_name="IGNOU Standard 10-Point").first()
        if not scale:
            scale = GradingScale(scale_name="IGNOU Standard 10-Point", is_active=True)
            db.session.add(scale)
            db.session.flush()

            rules_data = [
                {'min': 85.0, 'max': 100.0, 'grade': 'O',  'gp': 10.0, 'desc': 'Outstanding'},
                {'min': 75.0, 'max': 84.99, 'grade': 'A+', 'gp': 9.0,  'desc': 'Excellent'},
                {'min': 65.0, 'max': 74.99, 'grade': 'A',  'gp': 8.0,  'desc': 'Very Good'},
                {'min': 55.0, 'max': 64.99, 'grade': 'B+', 'gp': 7.0,  'desc': 'Good'},
                {'min': 50.0, 'max': 54.99, 'grade': 'B',  'gp': 6.0,  'desc': 'Above Average'},
                {'min': 40.0, 'max': 49.99, 'grade': 'C',  'gp': 5.0,  'desc': 'Average'},
                {'min': 0.0,  'max': 39.99, 'grade': 'F',  'gp': 0.0,  'desc': 'Fail'}
            ]

            for r in rules_data:
                rule = GradeRule(
                    scale_id=scale.scale_id,
                    min_percentage=r['min'],
                    max_percentage=r['max'],
                    grade_letter=r['grade'],
                    grade_point=r['gp'],
                    description=r['desc']
                )
                db.session.add(rule)
            print("  + Created IGNOU Standard 10-Point scale with 7 grade rules (O -> F).")
        else:
            print("  * IGNOU Grading Scale already seeded.")

        db.session.commit()

        # ----------------------------------------------------------------------
        # 3. Seed Academic Year & Classes
        # ----------------------------------------------------------------------
        print("\n[3/6] Seeding Academic Year and Classes...")
        ay = AcademicYear.query.filter_by(year_label="2025-2026").first()
        if not ay:
            ay = AcademicYear(year_label="2025-2026", is_active=True)
            db.session.add(ay)
            db.session.flush()
            print(f"  + Created Academic Year: {ay.year_label} (Active)")
        else:
            print(f"  * Academic Year {ay.year_label} exists.")

        classes_data = [
            {'name': 'BCA-Semester-1', 'section': 'A'},
            {'name': 'BCA-Semester-2', 'section': 'A'},
            {'name': 'MCA-Semester-1', 'section': 'A'}
        ]

        seeded_classes = {}
        for c in classes_data:
            existing_class = Class.query.filter_by(
                class_name=c['name'],
                section=c['section'],
                year_id=ay.year_id
            ).first()

            if not existing_class:
                new_class = Class(
                    class_name=c['name'],
                    section=c['section'],
                    year_id=ay.year_id
                )
                db.session.add(new_class)
                db.session.flush()
                seeded_classes[c['name']] = new_class
                print(f"  + Created Class: {new_class.display_name}")
            else:
                seeded_classes[c['name']] = existing_class
                print(f"  * Class exists: {existing_class.display_name}")

        db.session.commit()

        # ----------------------------------------------------------------------
        # 4. Seed Subjects & Class-Subject Mappings
        # ----------------------------------------------------------------------
        print("\n[4/6] Seeding Master Subject Registry & Curriculum...")
        subjects_data = [
            {'code': 'BCS-011',  'name': 'Computer Basics and PC Software', 'credits': 3},
            {'code': 'BCS-012',  'name': 'Mathematics',                      'credits': 4},
            {'code': 'BCSL-013', 'name': 'Computer Basics and Software Lab',  'credits': 2},
            {'code': 'MCS-211',  'name': 'Design and Analysis of Algorithms', 'credits': 4},
            {'code': 'MCS-212',  'name': 'Discrete Mathematics',              'credits': 4}
        ]

        seeded_subjects = {}
        for s in subjects_data:
            subj = Subject.query.filter_by(subject_code=s['code']).first()
            if not subj:
                subj = Subject(
                    subject_code=s['code'],
                    subject_name=s['name'],
                    credits=s['credits']
                )
                db.session.add(subj)
                db.session.flush()
                seeded_subjects[s['code']] = subj
                print(f"  + Created Subject: {subj.subject_code} - {subj.subject_name}")
            else:
                seeded_subjects[s['code']] = subj
                print(f"  * Subject exists: {subj.subject_code}")

        # Map BCA-Semester-1 subjects
        bca1 = seeded_classes.get('BCA-Semester-1')
        bca1_codes = ['BCS-011', 'BCS-012', 'BCSL-013']
        for code in bca1_codes:
            subj = seeded_subjects[code]
            mapping = ClassSubject.query.filter_by(class_id=bca1.class_id, subject_id=subj.subject_id).first()
            if not mapping:
                mapping = ClassSubject(
                    class_id=bca1.class_id,
                    subject_id=subj.subject_id,
                    max_internal_marks=30.0,
                    max_external_marks=70.0,
                    pass_marks=40.0
                )
                db.session.add(mapping)
                print(f"  + Mapped {code} to {bca1.class_name} (Max: 30/70, Pass: 40)")

        db.session.commit()

        # ----------------------------------------------------------------------
        # 5. Seed Exam Term & Sample Students
        # ----------------------------------------------------------------------
        print("\n[5/6] Seeding Exam Term & Students...")
        term = ExamTerm.query.filter_by(term_name="TEE June 2025", year_id=ay.year_id).first()
        if not term:
            term = ExamTerm(term_name="TEE June 2025", year_id=ay.year_id, is_locked=False)
            db.session.add(term)
            db.session.flush()
            print(f"  + Created Exam Term: {term.term_name}")
        else:
            print(f"  * Exam Term exists: {term.term_name}")

        students_data = [
            {'enr': '230100101', 'name': 'Rahul Sharma', 'email': 'rahul.sharma@ignou.ac.in'},
            {'enr': '230100102', 'name': 'Priya Patel',  'email': 'priya.patel@ignou.ac.in'},
            {'enr': '230100103', 'name': 'Amit Verma',   'email': 'amit.verma@ignou.ac.in'},
            {'enr': '230100104', 'name': 'Sneha Gupta',  'email': 'sneha.gupta@ignou.ac.in'},
            {'enr': '230100105', 'name': 'Rohan Mehra',  'email': 'rohan.mehra@ignou.ac.in'}
        ]

        seeded_students = []
        for st in students_data:
            student = Student.query.filter_by(enrollment_no=st['enr']).first()
            if not student:
                student = Student(
                    enrollment_no=st['enr'],
                    full_name=st['name'],
                    email=st['email'],
                    class_id=bca1.class_id
                )
                db.session.add(student)
                db.session.flush()
                seeded_students.append(student)
                print(f"  + Enrolled Student: {student.enrollment_no} ({student.full_name})")
            else:
                seeded_students.append(student)
                print(f"  * Student exists: {student.enrollment_no}")

        db.session.commit()

        # ----------------------------------------------------------------------
        # 6. Seed Sample Marks for Testing
        # ----------------------------------------------------------------------
        print("\n[6/6] Seeding Sample Marks Records...")
        bcs011_map = ClassSubject.query.filter_by(
            class_id=bca1.class_id,
            subject_id=seeded_subjects['BCS-011'].subject_id
        ).first()

        admin_user = seeded_users['admin']

        sample_scores = [
            {'idx': 0, 'int': 25.0, 'ext': 62.0, 'grade': 'O',  'gp': 10.0, 'absent': False},
            {'idx': 1, 'int': 22.0, 'ext': 56.0, 'grade': 'A+', 'gp': 9.0,  'absent': False},
            {'idx': 2, 'int': 16.0, 'ext': 36.0, 'grade': 'B',  'gp': 6.0,  'absent': False},
            {'idx': 3, 'int': 11.0, 'ext': 23.0, 'grade': 'F',  'gp': 0.0,  'absent': False},
            {'idx': 4, 'int': 0.0,  'ext': 0.0,  'grade': 'F',  'gp': 0.0,  'absent': True}
        ]

        for s in sample_scores:
            stu = seeded_students[s['idx']]
            existing_mark = Marks.query.filter_by(
                student_id=stu.student_id,
                class_subject_id=bcs011_map.class_subject_id,
                term_id=term.term_id
            ).first()

            if not existing_mark:
                mark = Marks(
                    student_id=stu.student_id,
                    class_subject_id=bcs011_map.class_subject_id,
                    term_id=term.term_id,
                    internal_marks=s['int'],
                    external_marks=s['ext'],
                    grade=s['grade'],
                    grade_point=s['gp'],
                    is_absent=s['absent'],
                    updated_by=admin_user.user_id
                )
                mark.calculate()
                db.session.add(mark)
                print(f"  + Added Score for {stu.full_name}: Total {mark.total_marks}, Grade {mark.grade}")

        db.session.commit()
        print("\n Database Seeding Complete! System ready for Phase 2 operations.\n")


if __name__ == '__main__':
    seed_database()
