"""Reporting Blueprint: Routes for Student Report Cards, Tabulation Registers & Executive Summaries."""

from flask import Blueprint, render_template, request, Response, flash, redirect, url_for
from app import db
from app.models.academic import Class, AcademicYear
from app.models.student import Student
from app.models.result import ExamTerm
from app.services.report_service import ReportService
from app.utils.decorators import teacher_required

reports_bp = Blueprint('reports', __name__, url_prefix='/reports')


# ------------------------------------------------------------------------------
# Milestone 6.1: Student Report Cards
# ------------------------------------------------------------------------------

@reports_bp.route('/report-cards', methods=['GET'])
@teacher_required
def report_cards():
    """Roster view for selecting cohort and generating individual student report cards."""
    classes = Class.query.join(AcademicYear).filter(AcademicYear.is_active == True).order_by(Class.class_name, Class.section).all()
    if not classes:
        classes = Class.query.order_by(Class.class_name, Class.section).all()

    terms = ExamTerm.query.order_by(ExamTerm.term_id.desc()).all()

    class_id = request.args.get('class_id', type=int)
    term_id = request.args.get('term_id', type=int)

    if not class_id and classes:
        class_id = classes[0].class_id
    if not term_id and terms:
        term_id = terms[0].term_id

    selected_class = db.session.get(Class, class_id) if class_id else None
    selected_term = db.session.get(ExamTerm, term_id) if term_id else None

    students_data = []
    if selected_class and selected_term:
        tr_data = ReportService.get_class_tr_data(class_id, term_id)
        if tr_data:
            students_data = tr_data.get('students', [])

    return render_template(
        'reports/report_cards_index.html',
        classes=classes,
        terms=terms,
        selected_class=selected_class,
        selected_term=selected_term,
        students_data=students_data
    )


@reports_bp.route('/report-card/<int:student_id>', methods=['GET'])
@teacher_required
def report_card_preview(student_id):
    """Render printable HTML preview of official student grade card / marksheet."""
    student = db.session.get(Student, student_id)
    if not student:
        flash('Student profile not found.', 'danger')
        return redirect(url_for('reports.report_cards'))

    terms = ExamTerm.query.order_by(ExamTerm.term_id.desc()).all()
    term_id = request.args.get('term_id', type=int)
    if not term_id and terms:
        term_id = terms[0].term_id

    data = ReportService.get_student_report_card_data(student_id, term_id)
    if not data:
        flash('Unable to compile report card data for selected term.', 'warning')
        return redirect(url_for('reports.report_cards', class_id=student.class_id, term_id=term_id))

    return render_template(
        'reports/report_card_preview.html',
        data=data,
        terms=terms,
        selected_term_id=term_id
    )


@reports_bp.route('/report-card/<int:student_id>/pdf', methods=['GET'])
@teacher_required
def download_report_card_pdf(student_id):
    """Stream or download official institutional ReportLab PDF marksheet."""
    terms = ExamTerm.query.order_by(ExamTerm.term_id.desc()).all()
    term_id = request.args.get('term_id', type=int)
    if not term_id and terms:
        term_id = terms[0].term_id

    pdf_bytes = ReportService.generate_student_report_card_pdf(student_id, term_id)
    if not pdf_bytes:
        flash('Unable to generate PDF report card.', 'danger')
        return redirect(url_for('reports.report_cards'))

    student = db.session.get(Student, student_id)
    enr_safe = student.enrollment_no.replace('/', '_') if student else str(student_id)
    filename = f"ReportCard_{enr_safe}_Term{term_id}.pdf"
    as_attachment = request.args.get('download', '0') == '1'
    disposition = 'attachment' if as_attachment else 'inline'

    return Response(
        pdf_bytes,
        mimetype='application/pdf',
        headers={'Content-Disposition': f'{disposition}; filename={filename}'}
    )


# ------------------------------------------------------------------------------
# Milestone 6.2: Master Tabulation Register (TR Sheet)
# ------------------------------------------------------------------------------

@reports_bp.route('/tabulation-register', methods=['GET'])
@teacher_required
def tabulation_register():
    """Web preview of Master Tabulation Register (TR Sheet) with Excel export."""
    classes = Class.query.join(AcademicYear).filter(AcademicYear.is_active == True).order_by(Class.class_name, Class.section).all()
    if not classes:
        classes = Class.query.order_by(Class.class_name, Class.section).all()

    terms = ExamTerm.query.order_by(ExamTerm.term_id.desc()).all()

    class_id = request.args.get('class_id', type=int)
    term_id = request.args.get('term_id', type=int)

    if not class_id and classes:
        class_id = classes[0].class_id
    if not term_id and terms:
        term_id = terms[0].term_id

    selected_class = db.session.get(Class, class_id) if class_id else None
    selected_term = db.session.get(ExamTerm, term_id) if term_id else None

    tr_data = None
    if selected_class and selected_term:
        tr_data = ReportService.get_class_tr_data(class_id, term_id)

    return render_template(
        'reports/tabulation_register.html',
        classes=classes,
        terms=terms,
        selected_class=selected_class,
        selected_term=selected_term,
        tr_data=tr_data
    )


@reports_bp.route('/tabulation-register/export', methods=['GET'])
@teacher_required
def export_tabulation_register():
    """Download multi-column Master Tabulation Register as styled Excel (.xlsx)."""
    class_id = request.args.get('class_id', type=int)
    term_id = request.args.get('term_id', type=int)

    if not class_id or not term_id:
        flash('Please select both a class and an examination term.', 'warning')
        return redirect(url_for('reports.tabulation_register'))

    excel_bytes = ReportService.generate_class_tr_sheet_excel(class_id, term_id)
    if not excel_bytes:
        flash('Failed to generate Tabulation Register spreadsheet.', 'danger')
        return redirect(url_for('reports.tabulation_register', class_id=class_id, term_id=term_id))

    target_class = db.session.get(Class, class_id)
    class_label = target_class.class_name.replace(' ', '_') if target_class else f"Class_{class_id}"
    filename = f"TR_Sheet_{class_label}_Term{term_id}.xlsx"

    return Response(
        excel_bytes,
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        headers={'Content-Disposition': f'attachment; filename={filename}'}
    )


# ------------------------------------------------------------------------------
# Milestone 6.3: Executive Class Performance Summary
# ------------------------------------------------------------------------------

@reports_bp.route('/class-summary', methods=['GET'])
@teacher_required
def class_summary():
    """Executive class performance and statistical summary web view."""
    classes = Class.query.join(AcademicYear).filter(AcademicYear.is_active == True).order_by(Class.class_name, Class.section).all()
    if not classes:
        classes = Class.query.order_by(Class.class_name, Class.section).all()

    terms = ExamTerm.query.order_by(ExamTerm.term_id.desc()).all()

    class_id = request.args.get('class_id', type=int)
    term_id = request.args.get('term_id', type=int)

    if not class_id and classes:
        class_id = classes[0].class_id
    if not term_id and terms:
        term_id = terms[0].term_id

    selected_class = db.session.get(Class, class_id) if class_id else None
    selected_term = db.session.get(ExamTerm, term_id) if term_id else None

    summary_data = None
    if selected_class and selected_term:
        summary_data = ReportService.get_class_summary_data(class_id, term_id)

    return render_template(
        'reports/class_summary.html',
        classes=classes,
        terms=terms,
        selected_class=selected_class,
        selected_term=selected_term,
        summary_data=summary_data
    )


@reports_bp.route('/class-summary/pdf', methods=['GET'])
@teacher_required
def download_class_summary_pdf():
    """Download executive performance summary as printable landscape PDF."""
    class_id = request.args.get('class_id', type=int)
    term_id = request.args.get('term_id', type=int)

    if not class_id or not term_id:
        flash('Please select both a class and an examination term.', 'warning')
        return redirect(url_for('reports.class_summary'))

    pdf_bytes = ReportService.generate_class_summary_pdf(class_id, term_id)
    if not pdf_bytes:
        flash('Failed to generate Executive Summary PDF.', 'danger')
        return redirect(url_for('reports.class_summary', class_id=class_id, term_id=term_id))

    target_class = db.session.get(Class, class_id)
    class_label = target_class.class_name.replace(' ', '_') if target_class else f"Class_{class_id}"
    filename = f"Executive_Summary_{class_label}_Term{term_id}.pdf"
    as_attachment = request.args.get('download', '0') == '1'
    disposition = 'attachment' if as_attachment else 'inline'

    return Response(
        pdf_bytes,
        mimetype='application/pdf',
        headers={'Content-Disposition': f'{disposition}; filename={filename}'}
    )
