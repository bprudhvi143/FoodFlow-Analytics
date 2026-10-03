"""
Health Check Router.
"""

from fastapi import APIRouter
from src.backend.models.schemas import HealthResponse
from src.backend.services.analytics import analytics_service

router = APIRouter(tags=["Health"])


@router.get("/health", response_model=HealthResponse)
def health_check():
    dataset_loaded = analytics_service.df is not None and len(analytics_service.df) > 0
    return HealthResponse(
        status="healthy",
        dataset_loaded=dataset_loaded,
        total_records=len(analytics_service.df) if dataset_loaded else 0,
        dataset_path=analytics_service.csv_path
    )
