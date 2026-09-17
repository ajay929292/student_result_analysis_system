from flask import Blueprint, render_template, jsonify, current_app

main_bp = Blueprint('main', __name__)


@main_bp.route('/')
def index():
    """System overview and dashboard landing page."""
    # System metadata and statistics preview
    system_stats = {
        'enrolled_students': 148,
        'pass_rate': 87.5,
        'class_average': 68.4,
        'at_risk_count': 6,
        'total_classes': 6,
        'active_terms': 2,
    }

    # Roadmap milestones status
    milestones = [
        {
            'phase': 'Phase 0 / Phase 1',
            'title': 'Foundation, Scaffold & Design System',
            'status': 'completed',
            'desc': 'App factory, modular configs, responsive layout, modern Vanilla CSS tokens.'
        },
        {
            'phase': 'Phase 2',
            'title': 'Data Modeling & RBAC Authentication',
            'status': 'completed',
            'desc': 'SQLAlchemy models, Bcrypt passwords, session RBAC, database seeding.'
        },
        {
            'phase': 'Phase 3',
            'title': 'Academic Setup & Student Management',
            'status': 'pending',
            'desc': 'Academic years, subjects, class mappings, student registration rosters.'
        },
        {
            'phase': 'Phase 4',
            'title': 'Marks Ingestion & Automated Grading',
            'status': 'pending',
            'desc': 'Interactive grid entry, CSV/Excel batch ingestion, 10-point scale grading engine.'
        },
        {
            'phase': 'Phase 5',
            'title': 'Statistical Analytics & Dashboards',
            'status': 'pending',
            'desc': 'Pandas aggregations, descriptive metrics, at-risk filters, Chart.js visuals.'
        },
        {
            'phase': 'Phase 6',
            'title': 'Institutional Reports & Exports',
            'status': 'pending',
            'desc': 'PDF Report Cards (ReportLab), Tabulation Register (Excel) exporter.'
        }
    ]

    return render_template('index.html', stats=system_stats, milestones=milestones)


@main_bp.route('/health')
def health_check():
    """Health check endpoint for monitoring."""
    return jsonify({
        'status': 'ok',
        'app': current_app.config.get('APP_NAME', 'Student Result Analysis System'),
        'version': current_app.config.get('APP_VERSION', '1.0.0'),
        'debug': current_app.config.get('DEBUG', False),
        'testing': current_app.config.get('TESTING', False)
    }), 200
