"""Analytics Blueprint: Web Dashboard and REST API endpoints for statistical result analysis."""

from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for
from app import db
from app.models.academic import Class, AcademicYear
from app.models.result import ExamTerm
from app.services.analytics_service import AnalyticsService
from app.utils.decorators import teacher_required, login_required

analytics_bp = Blueprint('analytics', __name__)


@analytics_bp.route('/analytics', methods=['GET'])
@teacher_required
def dashboard():
    """Render the primary visual analytics dashboard."""
    classes = Class.query.join(AcademicYear).filter(AcademicYear.is_active == True).order_by(Class.class_name).all()
    if not classes:
        classes = Class.query.order_by(Class.class_name).all()

    terms = ExamTerm.query.order_by(ExamTerm.term_id.desc()).all()

    class_id = request.args.get('class_id', type=int)
    term_id = request.args.get('term_id', type=int)

    # Defaults to first available class and term if none specified
    if not class_id and classes:
        class_id = classes[0].class_id
    if not term_id and terms:
        term_id = terms[0].term_id

    selected_class = db.session.get(Class, class_id) if class_id else None
    selected_term = db.session.get(ExamTerm, term_id) if term_id else None

    # Compute initial payload if selections are present
    overview = None
    grade_dist = None
    subj_comp = None
    at_risk = None
    top_performers = None

    if selected_class and selected_term:
        overview = AnalyticsService.compute_overview_metrics(class_id, term_id)
        grade_dist = AnalyticsService.compute_grade_distribution(class_id, term_id)
        subj_comp = AnalyticsService.compute_subject_comparison(class_id, term_id)
        at_risk = AnalyticsService.identify_at_risk_students(class_id, term_id)
        top_performers = AnalyticsService.compute_top_performers(class_id, term_id, limit=5)

    return render_template(
        'analytics/dashboard.html',
        classes=classes,
        terms=terms,
        selected_class=selected_class,
        selected_term=selected_term,
        overview=overview,
        grade_dist=grade_dist,
        subj_comp=subj_comp,
        at_risk=at_risk,
        top_performers=top_performers
    )


# ------------------------------------------------------------------------------
# REST API Endpoints (JSON)
# ------------------------------------------------------------------------------

@analytics_bp.route('/api/analytics/overview', methods=['GET'])
@teacher_required
def api_overview():
    """Return JSON overview descriptive & pass/fail metrics."""
    class_id = request.args.get('class_id', type=int)
    term_id = request.args.get('term_id', type=int)

    if not class_id or not term_id:
        return jsonify({'error': 'Missing required parameters: class_id and term_id', 'code': 'BAD_REQUEST'}), 400

    metrics = AnalyticsService.compute_overview_metrics(class_id, term_id)
    return jsonify(metrics), 200


@analytics_bp.route('/api/analytics/grade-distribution', methods=['GET'])
@teacher_required
def api_grade_distribution():
    """Return JSON frequency distribution for IGNOU 10-point grades."""
    class_id = request.args.get('class_id', type=int)
    term_id = request.args.get('term_id', type=int)

    if not class_id or not term_id:
        return jsonify({'error': 'Missing required parameters: class_id and term_id', 'code': 'BAD_REQUEST'}), 400

    distribution = AnalyticsService.compute_grade_distribution(class_id, term_id)
    return jsonify(distribution), 200


@analytics_bp.route('/api/analytics/subject-comparison', methods=['GET'])
@teacher_required
def api_subject_comparison():
    """Return JSON cross-subject benchmarking scores and pass percentages."""
    class_id = request.args.get('class_id', type=int)
    term_id = request.args.get('term_id', type=int)

    if not class_id or not term_id:
        return jsonify({'error': 'Missing required parameters: class_id and term_id', 'code': 'BAD_REQUEST'}), 400

    data = AnalyticsService.compute_subject_comparison(class_id, term_id)
    return jsonify(data), 200


@analytics_bp.route('/api/analytics/at-risk', methods=['GET'])
@teacher_required
def api_at_risk():
    """Return JSON list of academically vulnerable candidates with remediation actions."""
    class_id = request.args.get('class_id', type=int)
    term_id = request.args.get('term_id', type=int)

    if not class_id or not term_id:
        return jsonify({'error': 'Missing required parameters: class_id and term_id', 'code': 'BAD_REQUEST'}), 400

    at_risk_list = AnalyticsService.identify_at_risk_students(class_id, term_id)
    return jsonify({'at_risk_students': at_risk_list, 'count': len(at_risk_list)}), 200


@analytics_bp.route('/api/analytics/top-performers', methods=['GET'])
@teacher_required
def api_top_performers():
    """Return JSON list of top academic performers (class rankers)."""
    class_id = request.args.get('class_id', type=int)
    term_id = request.args.get('term_id', type=int)
    limit = request.args.get('limit', default=5, type=int)

    if not class_id or not term_id:
        return jsonify({'error': 'Missing required parameters: class_id and term_id', 'code': 'BAD_REQUEST'}), 400

    top_list = AnalyticsService.compute_top_performers(class_id, term_id, limit=limit)
    return jsonify({'top_performers': top_list, 'count': len(top_list)}), 200
