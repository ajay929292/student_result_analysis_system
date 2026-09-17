"""Automated Grading and Evaluation Service for IGNOU 10-Point Scale."""

from typing import Optional, Tuple, Dict, Any
from app import db
from app.models.result import GradingScale, GradeRule


DEFAULT_IGNOU_RULES = [
    (85.0, 100.0, 'O', 10.0, 'Outstanding'),
    (75.0, 84.99, 'A+', 9.0, 'Excellent'),
    (65.0, 74.99, 'A', 8.0, 'Very Good'),
    (55.0, 64.99, 'B+', 7.0, 'Good'),
    (50.0, 54.99, 'B', 6.0, 'Above Average'),
    (40.0, 49.99, 'C', 5.0, 'Average'),
    (0.0, 39.99, 'F', 0.0, 'Fail'),
]


class GradingService:
    """Service handling grade computation, percentage scaling, and pass/fail determination."""

    @classmethod
    def get_active_scale(cls) -> Optional[GradingScale]:
        """Fetch current active grading scale with its rules from the database."""
        try:
            return GradingScale.query.filter_by(is_active=True).first()
        except Exception:
            return None

    @classmethod
    def get_grade_for_percentage(cls, percentage: float, scale: Optional[GradingScale] = None) -> Tuple[str, float, str]:
        """
        Map a percentage score (0-100) to letter grade, grade points, and descriptor.
        Uses active database scale if available; otherwise falls back to standard IGNOU 10-point scale.
        """
        clamped_pct = max(0.0, min(100.0, round(float(percentage), 2)))

        target_scale = scale or cls.get_active_scale()
        if target_scale and target_scale.rules:
            for rule in target_scale.rules:
                if rule.min_percentage <= clamped_pct <= rule.max_percentage:
                    return rule.grade_letter, rule.grade_point, rule.description

        # Fallback to standard IGNOU 10-point scale
        for min_pct, max_pct, letter, points, desc in DEFAULT_IGNOU_RULES:
            if min_pct <= clamped_pct <= max_pct:
                return letter, points, desc

        return 'F', 0.0, 'Fail'

    @classmethod
    def evaluate(
        cls,
        internal_marks: float,
        external_marks: float,
        max_internal: float,
        max_external: float,
        pass_marks: float,
        is_absent: bool = False,
        scale: Optional[GradingScale] = None
    ) -> Dict[str, Any]:
        """
        Compute total, percentage, pass/fail status, letter grade, and grade points.
        """
        if is_absent:
            return {
                'internal_marks': 0.0,
                'external_marks': 0.0,
                'total_marks': 0.0,
                'percentage': 0.0,
                'is_absent': True,
                'is_passed': False,
                'grade': 'F',
                'grade_point': 0.0,
                'description': 'Absent'
            }

        safe_internal = max(0.0, min(max_internal, float(internal_marks)))
        safe_external = max(0.0, min(max_external, float(external_marks)))
        total_marks = round(safe_internal + safe_external, 2)
        max_total = max_internal + max_external

        if max_total > 0:
            percentage = round((total_marks / max_total) * 100, 2)
        else:
            percentage = 0.0

        # Meeting aggregate pass marks requirement
        is_passed = bool(total_marks >= pass_marks)

        if is_passed:
            grade, grade_point, desc = cls.get_grade_for_percentage(percentage, scale)
        else:
            grade, grade_point, desc = 'F', 0.0, 'Fail'

        return {
            'internal_marks': safe_internal,
            'external_marks': safe_external,
            'total_marks': total_marks,
            'percentage': percentage,
            'is_absent': False,
            'is_passed': is_passed,
            'grade': grade,
            'grade_point': grade_point,
            'description': desc
        }
