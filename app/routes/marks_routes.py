from flask import Blueprint, render_template, request, redirect, url_for, flash, session, Response
from app import db
from app.models.academic import Class, Subject, ClassSubject, AcademicYear
from app.models.student import Student
from app.models.result import ExamTerm, Marks
from app.services.grading_service import GradingService
from app.services.ingestion_service import MarksIngestionService
from app.utils.decorators import teacher_required, admin_required

marks_bp = Blueprint('marks', __name__, url_prefix='/marks')


@marks_bp.route('/')
@teacher_required
def index():
    """Redirect marks root to interactive marks entry."""
    return redirect(url_for('marks.entry'))


# --------------------------------------------------------------------------
# Milestone 4.1: Manual Interactive Marks Entry
# --------------------------------------------------------------------------
@marks_bp.route('/entry', methods=['GET', 'POST'])
@teacher_required
def entry():
    """Interactive spreadsheet grid for manual marks evaluation."""
    classes = Class.query.order_by(Class.class_name, Class.section).all()
    subjects = Subject.query.order_by(Subject.subject_code).all()
    terms = ExamTerm.query.order_by(ExamTerm.term_name.desc()).all()

    class_id = request.args.get('class_id', type=int)
    subject_id = request.args.get('subject_id', type=int)
    term_id = request.args.get('term_id', type=int)

    selected_class = db.session.get(Class, class_id) if class_id else None
    selected_subject = db.session.get(Subject, subject_id) if subject_id else None
    selected_term = db.session.get(ExamTerm, term_id) if term_id else None

    mapping = None
    student_rows = []

    if selected_class and selected_subject and selected_term:
        mapping = ClassSubject.query.filter_by(class_id=class_id, subject_id=subject_id).first()
        if mapping:
            students = sorted(selected_class.students, key=lambda s: s.enrollment_no)
            existing_marks = {
                m.student_id: m for m in Marks.query.filter_by(
                    class_subject_id=mapping.class_subject_id,
                    term_id=term_id
                ).all()
            }

            for st in students:
                student_rows.append({
                    'student': st,
                    'mark': existing_marks.get(st.student_id)
                })

    if request.method == 'POST':
        p_class_id = request.form.get('class_id', type=int)
        p_subject_id = request.form.get('subject_id', type=int)
        p_term_id = request.form.get('term_id', type=int)

        term = db.session.get(ExamTerm, p_term_id)
        if not term:
            flash('Invalid examination term specified.', 'danger')
            return redirect(url_for('marks.entry'))

        if term.is_locked:
            flash(f'Exam Term "{term.term_name}" is locked. Modification is forbidden.', 'danger')
            return redirect(url_for('marks.entry', class_id=p_class_id, subject_id=p_subject_id, term_id=p_term_id))

        cur_mapping = ClassSubject.query.filter_by(class_id=p_class_id, subject_id=p_subject_id).first()
        if not cur_mapping:
            flash('Selected subject is not mapped to this class.', 'danger')
            return redirect(url_for('marks.entry'))

        student_ids = request.form.getlist('student_ids', type=int)
        user_id = session.get('user_id')
        active_scale = GradingService.get_active_scale()
        saved_count = 0

        for st_id in student_ids:
            is_absent = bool(request.form.get(f'absent_{st_id}'))
            in_val = request.form.get(f'internal_{st_id}', 0.0, type=float)
            ex_val = request.form.get(f'external_{st_id}', 0.0, type=float)

            eval_res = GradingService.evaluate(
                internal_marks=in_val,
                external_marks=ex_val,
                max_internal=cur_mapping.max_internal_marks,
                max_external=cur_mapping.max_external_marks,
                pass_marks=cur_mapping.pass_marks,
                is_absent=is_absent,
                scale=active_scale
            )

            mark = Marks.query.filter_by(
                student_id=st_id,
                class_subject_id=cur_mapping.class_subject_id,
                term_id=p_term_id
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
                    student_id=st_id,
                    class_subject_id=cur_mapping.class_subject_id,
                    term_id=p_term_id,
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

            saved_count += 1

        db.session.commit()
        flash(f'Successfully evaluated and recorded marks for {saved_count} student(s).', 'success')
        return redirect(url_for('marks.entry', class_id=p_class_id, subject_id=p_subject_id, term_id=p_term_id))

    return render_template(
        'marks/entry.html',
        classes=classes,
        subjects=subjects,
        terms=terms,
        selected_class=selected_class,
        selected_subject=selected_subject,
        selected_term=selected_term,
        mapping=mapping,
        student_rows=student_rows
    )


# --------------------------------------------------------------------------
# Milestone 4.2: Bulk File Ingestion Engine (CSV / Excel)
# --------------------------------------------------------------------------
@marks_bp.route('/bulk-upload', methods=['GET', 'POST'])
@teacher_required
def bulk_upload():
    """Bulk file ingestion engine supporting .csv, .xlsx, and .xls spreadsheets."""
    classes = Class.query.order_by(Class.class_name, Class.section).all()
    subjects = Subject.query.order_by(Subject.subject_code).all()
    terms = ExamTerm.query.order_by(ExamTerm.term_name.desc()).all()

    if request.method == 'POST':
        class_id = request.form.get('class_id', type=int)
        subject_id = request.form.get('subject_id', type=int)
        term_id = request.form.get('term_id', type=int)
        file = request.files.get('file')

        if not class_id or not subject_id or not term_id:
            flash('Class, Subject, and Exam Term must all be selected.', 'danger')
            return render_template('marks/bulk.html', classes=classes, subjects=subjects, terms=terms)

        if not file or not file.filename:
            flash('Please choose a valid spreadsheet file (.csv or .xlsx).', 'warning')
            return render_template('marks/bulk.html', classes=classes, subjects=subjects, terms=terms)

        user_id = session.get('user_id')
        result = MarksIngestionService.ingest_file(
            file_obj=file.stream,
            filename=file.filename,
            class_id=class_id,
            subject_id=subject_id,
            term_id=term_id,
            user_id=user_id
        )

        if result['success']:
            flash(
                f"Successfully ingested {result['total_processed']} student marks for "
                f"{result['class_name']} ({result['subject_code']})! "
                f"Passed: {result['passed']}, Failed: {result['failed']}, Absent: {result['absent']}.",
                'success'
            )
            return redirect(url_for('marks.entry', class_id=class_id, subject_id=subject_id, term_id=term_id))
        else:
            return render_template(
                'marks/bulk.html',
                classes=classes,
                subjects=subjects,
                terms=terms,
                selected_class_id=class_id,
                selected_subject_id=subject_id,
                selected_term_id=term_id,
                validation_errors=result.get('errors', []),
                total_rows=result.get('total_rows', 0)
            )

    return render_template('marks/bulk.html', classes=classes, subjects=subjects, terms=terms)


@marks_bp.route('/template')
@teacher_required
def download_template():
    """Download pre-populated CSV or Excel evaluation spreadsheet."""
    class_id = request.args.get('class_id', type=int)
    subject_id = request.args.get('subject_id', type=int)
    fmt = request.args.get('format', 'csv').lower()

    if not class_id or not subject_id:
        flash('Please select both a class and subject to generate a template.', 'warning')
        return redirect(url_for('marks.bulk_upload'))

    file_bytes, mimetype, filename = MarksIngestionService.generate_template(
        class_id=class_id,
        subject_id=subject_id,
        file_format=fmt
    )

    return Response(
        file_bytes,
        mimetype=mimetype,
        headers={'Content-Disposition': f'attachment; filename={filename}'}
    )


# --------------------------------------------------------------------------
# Milestone 4.4: Exam Term Locking & Audit Management
# --------------------------------------------------------------------------
@marks_bp.route('/terms')
@teacher_required
def terms():
    """Exam terms listing and lock status management."""
    terms_list = ExamTerm.query.order_by(ExamTerm.term_name.desc()).all()
    years = AcademicYear.query.order_by(AcademicYear.year_label.desc()).all()
    return render_template('marks/terms.html', terms=terms_list, years=years)


@marks_bp.route('/terms/create', methods=['POST'])
@admin_required
def create_term():
    """Create a new exam evaluation cycle term."""
    term_name = request.form.get('term_name', '').strip()
    year_id = request.form.get('year_id', type=int)

    if not term_name or not year_id:
        flash('Term name and Academic Year are required.', 'danger')
        return redirect(url_for('marks.terms'))

    new_term = ExamTerm(term_name=term_name, year_id=year_id, is_locked=False)
    db.session.add(new_term)
    db.session.commit()

    flash(f'Examination Term "{term_name}" created.', 'success')
    return redirect(url_for('marks.terms'))


@marks_bp.route('/terms/<int:term_id>/toggle-lock', methods=['POST'])
@admin_required
def toggle_term_lock(term_id):
    """Toggle lock status on an exam term."""
    term = db.session.get(ExamTerm, term_id)
    if not term:
        flash('Exam term not found.', 'danger')
        return redirect(url_for('marks.terms'))

    term.is_locked = not term.is_locked
    db.session.commit()

    state_str = "LOCKED (Read-Only)" if term.is_locked else "UNLOCKED (Editable)"
    flash(f'Examination Term "{term.term_name}" is now {state_str}.', 'info' if term.is_locked else 'success')
    return redirect(url_for('marks.terms'))
