from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from app import db
from app.models import AcademicYear, Class, Subject, ClassSubject
from app.utils.decorators import admin_required, teacher_required

academic_bp = Blueprint('academic', __name__, url_prefix='/academic')


@academic_bp.route('/')
@teacher_required
def index():
    """Unified Academic Management Hub."""
    years = AcademicYear.query.order_by(AcademicYear.year_label.desc()).all()
    classes = Class.query.order_by(Class.class_name, Class.section).all()
    subjects = Subject.query.order_by(Subject.subject_code).all()

    return render_template(
        'academic/index.html',
        years=years,
        classes=classes,
        subjects=subjects
    )


# --------------------------------------------------------------------------
# Academic Year Management
# --------------------------------------------------------------------------
@academic_bp.route('/years', methods=['POST'])
@admin_required
def create_year():
    """Create a new Academic Year."""
    year_label = request.form.get('year_label', '').strip()
    is_active = bool(request.form.get('is_active'))

    if not year_label:
        flash('Academic Year label is required (e.g., 2025-2026).', 'danger')
        return redirect(url_for('academic.index'))

    existing = AcademicYear.query.filter_by(year_label=year_label).first()
    if existing:
        flash(f'Academic Year "{year_label}" already exists.', 'warning')
        return redirect(url_for('academic.index'))

    # If setting as active, deactivate other years
    if is_active:
        AcademicYear.query.update({'is_active': False})

    new_year = AcademicYear(year_label=year_label, is_active=is_active)
    db.session.add(new_year)
    db.session.commit()

    flash(f'Academic Year "{year_label}" created successfully.', 'success')
    return redirect(url_for('academic.index'))


@academic_bp.route('/years/<int:year_id>/toggle-active', methods=['POST'])
@admin_required
def toggle_year_active(year_id):
    """Set an Academic Year as the primary active session."""
    year = AcademicYear.query.get_or_404(year_id)

    # Deactivate all and activate selected
    AcademicYear.query.update({'is_active': False})
    year.is_active = True
    db.session.commit()

    flash(f'Academic Year "{year.year_label}" is now set as the active session.', 'success')
    return redirect(url_for('academic.index'))


# --------------------------------------------------------------------------
# Class / Cohort Management
# --------------------------------------------------------------------------
@academic_bp.route('/classes', methods=['POST'])
@admin_required
def create_class():
    """Create a new program class / section."""
    class_name = request.form.get('class_name', '').strip()
    section = request.form.get('section', 'A').strip().upper()
    year_id = request.form.get('year_id', type=int)

    if not class_name or not year_id:
        flash('Class name and Academic Year are required.', 'danger')
        return redirect(url_for('academic.index'))

    existing = Class.query.filter_by(class_name=class_name, section=section, year_id=year_id).first()
    if existing:
        flash(f'Class "{class_name} - Section {section}" already exists for this session.', 'warning')
        return redirect(url_for('academic.index'))

    new_class = Class(class_name=class_name, section=section, year_id=year_id)
    db.session.add(new_class)
    db.session.commit()

    flash(f'Class "{new_class.display_name}" created successfully.', 'success')
    return redirect(url_for('academic.index'))


@academic_bp.route('/classes/<int:class_id>/delete', methods=['POST'])
@admin_required
def delete_class(class_id):
    """Delete class if no students are enrolled."""
    cls = Class.query.get_or_404(class_id)
    if cls.students and len(cls.students) > 0:
        flash(f'Cannot delete "{cls.display_name}": {len(cls.students)} student(s) are currently enrolled.', 'danger')
        return redirect(url_for('academic.index'))

    class_name = cls.display_name
    db.session.delete(cls)
    db.session.commit()

    flash(f'Class "{class_name}" deleted successfully.', 'info')
    return redirect(url_for('academic.index'))


# --------------------------------------------------------------------------
# Subject Registry
# --------------------------------------------------------------------------
@academic_bp.route('/subjects', methods=['POST'])
@admin_required
def create_subject():
    """Register a new subject in the master registry."""
    subject_code = request.form.get('subject_code', '').strip().upper()
    subject_name = request.form.get('subject_name', '').strip()
    credits = request.form.get('credits', 4, type=int)

    if not subject_code or not subject_name:
        flash('Subject code and title are required.', 'danger')
        return redirect(url_for('academic.index'))

    existing = Subject.query.filter_by(subject_code=subject_code).first()
    if existing:
        flash(f'Subject with code "{subject_code}" is already registered.', 'warning')
        return redirect(url_for('academic.index'))

    subject = Subject(subject_code=subject_code, subject_name=subject_name, credits=credits)
    db.session.add(subject)
    db.session.commit()

    flash(f'Subject "{subject.subject_code} - {subject.subject_name}" added to registry.', 'success')
    return redirect(url_for('academic.index'))


# --------------------------------------------------------------------------
# Curriculum / Class-Subject Mapping
# --------------------------------------------------------------------------
@academic_bp.route('/curriculum')
@teacher_required
def curriculum():
    """Curriculum mapping interface showing subject allocations across classes."""
    classes = Class.query.order_by(Class.class_name, Class.section).all()
    subjects = Subject.query.order_by(Subject.subject_code).all()
    mappings = ClassSubject.query.all()

    # Group mappings by class
    class_curriculum = {}
    for c in classes:
        class_curriculum[c.class_id] = [m for m in mappings if m.class_id == c.class_id]

    return render_template(
        'academic/curriculum.html',
        classes=classes,
        subjects=subjects,
        class_curriculum=class_curriculum,
        mappings=mappings
    )


@academic_bp.route('/curriculum', methods=['POST'])
@admin_required
def map_curriculum():
    """Map a subject to a class with evaluation mark thresholds."""
    class_id = request.form.get('class_id', type=int)
    subject_id = request.form.get('subject_id', type=int)
    max_internal = request.form.get('max_internal_marks', 30.0, type=float)
    max_external = request.form.get('max_external_marks', 70.0, type=float)
    pass_marks = request.form.get('pass_marks', 40.0, type=float)

    if not class_id or not subject_id:
        flash('Both Class and Subject must be selected.', 'danger')
        return redirect(url_for('academic.curriculum'))

    existing = ClassSubject.query.filter_by(class_id=class_id, subject_id=subject_id).first()
    if existing:
        flash('This subject is already mapped to the selected class.', 'warning')
        return redirect(url_for('academic.curriculum'))

    mapping = ClassSubject(
        class_id=class_id,
        subject_id=subject_id,
        max_internal_marks=max_internal,
        max_external_marks=max_external,
        pass_marks=pass_marks
    )
    db.session.add(mapping)
    db.session.commit()

    flash(f'Subject successfully mapped with evaluation scale ({max_internal} internal / {max_external} external).', 'success')
    return redirect(url_for('academic.curriculum'))


@academic_bp.route('/curriculum/<int:mapping_id>/delete', methods=['POST'])
@admin_required
def delete_curriculum_mapping(mapping_id):
    """Remove a subject association from a class."""
    mapping = ClassSubject.query.get_or_404(mapping_id)
    if mapping.marks_records and len(mapping.marks_records) > 0:
        flash(f'Cannot unmap: {len(mapping.marks_records)} examination score record(s) exist for this course mapping.', 'danger')
        return redirect(url_for('academic.curriculum'))

    db.session.delete(mapping)
    db.session.commit()

    flash('Curriculum course association removed.', 'info')
    return redirect(url_for('academic.curriculum'))
