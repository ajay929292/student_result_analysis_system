"""Services package."""

from app.services.grading_service import GradingService
from app.services.ingestion_service import MarksIngestionService

__all__ = ['GradingService', 'MarksIngestionService']
