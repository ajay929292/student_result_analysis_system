import io
import csv
from flask import Blueprint, render_template, request, redirect, url_for, flash, Response
from app import db
from app.models import Student, Class
from app.utils.decorators import teacher_required, admin_required

student_bp = Blueprint('student', __name__, url_prefix='/students')


@student_bp.route('/')
@teacher_required
def index():
    """Student directory roster with search and class filtering."""
    class_id = request.args.get('class_id', type=int)
    search_query = request.args.get('q', '').strip()

    query = Student.query.join(Class)

    if class_id:
        query = query.filter(Student.class_id == class_id)

    if search_query:
        search_term = f"%{search_query}%"
        query = query.filter(
            db.or_(
                Student.enrollment_no.ilike(search_term),
                Student.full_name.ilike(search_term),
                Student.email.ilike(search_term)
            )
        )

    students = query.order_by(Student.enrollment_no.asc()).all()
    classes = Class.query.order_by(Class.class_name, Class.section).all()

    return render_template(
        'students/index.html',
        students=students,
        classes=classes,
        selected_class_id=class_id,
        search_query=search_query,
        total_count=len(students)
    )


@student_bp.route('/new', methods=['GET', 'POST'])
@teacher_required
def create_student():
    """Register an individual student profile."""
    classes = Class.query.order_by(Class.class_name, Class.section).all()

    if request.method == 'POST':
        enrollment_no = request.form.get('enrollment_no', '').strip()
        full_name = request.form.get('full_name', '').strip()
        email = request.form.get('email', '').strip() or None
        class_id = request.form.get('class_id', type=int)

        if not enrollment_no or not full_name or not class_id:
            flash('Enrollment Number, Full Name, and Class assignment are required.', 'danger')
            return render_template('students/form.html', classes=classes, student=None, form_data=request.form)

        # Check unique constraint on enrollment_no
        existing = Student.query.filter_by(enrollment_no=enrollment_no).first()
        if existing:
            flash(f'A student with Enrollment No "{enrollment_no}" is already registered ({existing.full_name}).', 'danger')
            return render_template('students/form.html', classes=classes, student=None, form_data=request.form)

        target_class = db.session.get(Class, class_id)
        if not target_class:
            flash('Selected Class does not exist.', 'danger')
            return render_template('students/form.html', classes=classes, student=None, form_data=request.form)

        student = Student(
            enrollment_no=enrollment_no,
            full_name=full_name,
            email=email,
            class_id=class_id
        )
        db.session.add(student)
        db.session.commit()

        flash(f'Student "{full_name}" ({enrollment_no}) successfully enrolled in {target_class.display_name}.', 'success')
        return redirect(url_for('student.index', class_id=class_id))

    return render_template('students/form.html', classes=classes, student=None, form_data={})


@student_bp.route('/edit/<int:student_id>', methods=['GET', 'POST'])
@teacher_required
def edit_student(student_id):
    """Edit student profile details."""
    student = Student.query.get_or_404(student_id)
    classes = Class.query.order_by(Class.class_name, Class.section).all()

    if request.method == 'POST':
        full_name = request.form.get('full_name', '').strip()
        email = request.form.get('email', '').strip() or None
        class_id = request.form.get('class_id', type=int)

        if not full_name or not class_id:
            flash('Full Name and Class assignment are required.', 'danger')
            return render_template('students/form.html', classes=classes, student=student)

        student.full_name = full_name
        student.email = email
        student.class_id = class_id
        db.session.commit()

        flash(f'Student profile for {student.enrollment_no} updated.', 'success')
        return redirect(url_for('student.index', class_id=class_id))

    return render_template('students/form.html', classes=classes, student=student)


@student_bp.route('/delete/<int:student_id>', methods=['POST'])
@admin_required
def delete_student(student_id):
    """Remove student profile (admin only)."""
    student = Student.query.get_or_404(student_id)
    enr = student.enrollment_no
    name = student.full_name

    db.session.delete(student)
    db.session.commit()

    flash(f'Student {name} ({enr}) removed from system records.', 'info')
    return redirect(url_for('student.index'))


# --------------------------------------------------------------------------
# Bulk CSV Ingestion Engine
# --------------------------------------------------------------------------
@student_bp.route('/bulk-upload', methods=['GET', 'POST'])
@teacher_required
def bulk_upload():
    """Batch enroll students via CSV spreadsheet upload with atomic validation."""
    classes = Class.query.order_by(Class.class_name, Class.section).all()

    if request.method == 'POST':
        class_id = request.form.get('class_id', type=int)
        file = request.files.get('file')

        if not class_id:
            flash('Please select an academic class for enrollment.', 'danger')
            return render_template('students/bulk.html', classes=classes)

        target_class = db.session.get(Class, class_id)
        if not target_class:
            flash('Selected Class does not exist.', 'danger')
            return render_template('students/bulk.html', classes=classes)

        if not file or not file.filename:
            flash('Please choose a CSV file to upload.', 'warning')
            return render_template('students/bulk.html', classes=classes)

        if not file.filename.lower().endswith('.csv'):
            flash('Invalid file format. Please upload a .csv file.', 'danger')
            return render_template('students/bulk.html', classes=classes)

        try:
            # Read and decode CSV content
            stream = io.StringIO(file.stream.read().decode('utf-8-sig', errors='replace'))
            reader = csv.DictReader(stream)

            # Normalize headers
            if not reader.fieldnames:
                flash('The uploaded CSV file is empty.', 'danger')
                return render_template('students/bulk.html', classes=classes)

            headers = [h.strip().lower() for h in reader.fieldnames if h]
            if 'enrollment_no' not in headers or 'full_name' not in headers:
                flash('Missing required headers. CSV must contain: "enrollment_no" and "full_name".', 'danger')
                return render_template('students/bulk.html', classes=classes)

            errors = []
            new_students = []
            seen_in_file = set()

            for line_no, row in enumerate(reader, start=2):
                # Clean row keys and values
                clean_row = {k.strip().lower(): (v.strip() if v else '') for k, v in row.items() if k}
                enr = clean_row.get('enrollment_no', '')
                name = clean_row.get('full_name', '')
                email = clean_row.get('email', '') or None

                if not enr:
                    errors.append(f'Row {line_no}: Enrollment number is missing.')
                    continue
                if not name:
                    errors.append(f'Row {line_no}: Full name is missing for enrollment "{enr}".')
                    continue

                if enr in seen_in_file:
                    errors.append(f'Row {line_no}: Duplicate enrollment "{enr}" found within the CSV file.')
                    continue
                seen_in_file.add(enr)

                # Check database duplicate
                existing = Student.query.filter_by(enrollment_no=enr).first()
                if existing:
                    errors.append(f'Row {line_no}: Enrollment "{enr}" is already registered in the system ({existing.full_name}).')
                    continue

                new_students.append(
                    Student(
                        enrollment_no=enr,
                        full_name=name,
                        email=email,
                        class_id=class_id
                    )
                )

            # Atomic Transaction: If ANY row failed, reject entire file
            if errors:
                return render_template(
                    'students/bulk.html',
                    classes=classes,
                    validation_errors=errors,
                    total_rows=len(new_students) + len(errors)
                )

            if not new_students:
                flash('No student records found in file to enroll.', 'warning')
                return render_template('students/bulk.html', classes=classes)

            # Commit all valid students
            db.session.add_all(new_students)
            db.session.commit()

            flash(f'Successfully enrolled {len(new_students)} students into {target_class.display_name}!', 'success')
            return redirect(url_for('student.index', class_id=class_id))

        except Exception as e:
            db.session.rollback()
            flash(f'Error reading CSV file: {str(e)}', 'danger')
            return render_template('students/bulk.html', classes=classes)

    return render_template('students/bulk.html', classes=classes)


@student_bp.route('/template.csv')
@teacher_required
def download_template():
    """Provide downloadable pre-formatted student enrollment CSV template."""
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['enrollment_no', 'full_name', 'email'])
    writer.writerow(['240100201', 'Aarav Sharma', 'aarav.sharma@ignou.ac.in'])
    writer.writerow(['240100202', 'Diya Patel', 'diya.patel@ignou.ac.in'])
    writer.writerow(['240100203', 'Kabir Verma', 'kabir.verma@ignou.ac.in'])

    return Response(
        output.getvalue(),
        mimetype='text/csv',
        headers={'Content-Disposition': 'attachment; filename=student_enrollment_template.csv'}
    )
