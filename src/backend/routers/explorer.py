"""
Explorer Router providing REST API endpoints for Data Explorer page.
"""

from typing import List, Optional
from fastapi import APIRouter, Query, HTTPException
from src.backend.models.schemas import (
    ExplorerSummary, ColumnSchemaItem, ExplorerSummaryStats, ExplorerRecordsResponse
)
from src.backend.services.explorer import explorer_service

router = APIRouter(prefix="/explorer", tags=["Data Explorer"])


@router.get("/summary", response_model=ExplorerSummary)
def get_explorer_summary():
    """GET /api/explorer/summary - High-level dataset summary metrics."""
    try:
        return explorer_service.get_summary()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve explorer summary: {str(e)}")


@router.get("/schema", response_model=List[ColumnSchemaItem])
def get_explorer_schema():
    """GET /api/explorer/schema - Metadata for all columns."""
    try:
        return explorer_service.get_schema()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve explorer schema: {str(e)}")


@router.get("/summary-stats", response_model=ExplorerSummaryStats)
def get_explorer_summary_stats():
    """GET /api/explorer/summary-stats - Numerical and categorical summary distributions."""
    try:
        return explorer_service.get_summary_stats()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve explorer summary stats: {str(e)}")


@router.get("/records", response_model=ExplorerRecordsResponse)
def get_explorer_records(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Page size (max 100)"),
    search: Optional[str] = Query(None, description="Global text search query"),
    city: Optional[str] = Query(None, description="Filter by City"),
    traffic_level: Optional[str] = Query(None, description="Filter by Traffic Level"),
    vehicle: Optional[str] = Query(None, description="Filter by Vehicle"),
    order_status: Optional[str] = Query(None, description="Filter by Order Status"),
    sort_by: Optional[str] = Query(None, description="Column to sort by"),
    sort_order: Optional[str] = Query('asc', description="Sort order: asc or desc")
):
    """GET /api/explorer/records - Paginated & searchable table preview of dataset orders."""
    try:
        return explorer_service.get_records(
            page=page, page_size=page_size, search=search,
            city=city, traffic_level=traffic_level, vehicle=vehicle,
            order_status=order_status, sort_by=sort_by, sort_order=sort_order
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve explorer records: {str(e)}")
