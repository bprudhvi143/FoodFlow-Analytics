"""
Analytics Router providing REST API endpoints for FoodFlow Analytics dashboard.
"""

from typing import List, Optional
from fastapi import APIRouter, Query, HTTPException
from src.backend.models.schemas import (
    OverviewAnalytics, CityAnalyticsItem, TrafficAnalyticsItem, StatusAnalyticsItem,
    DurationBinItem, TimeOfDayAnalyticsItem, DayOfWeekAnalyticsItem, VehicleAnalyticsItem,
    OrderQuantityAnalyticsItem, OrderValueAnalyticsItem, DistanceAnalyticsResponse,
    InsightItem, FiltersResponse
)
from src.backend.services.analytics import analytics_service

router = APIRouter(prefix="/analytics", tags=["Analytics"])


@router.get("/overview", response_model=OverviewAnalytics)
def get_overview(
    city: Optional[str] = Query(None, description="Filter by City"),
    traffic_level: Optional[str] = Query(None, description="Filter by Traffic Level"),
    time_of_day: Optional[str] = Query(None, description="Filter by Time of Day Segment"),
    day_of_week: Optional[str] = Query(None, description="Filter by Day of Week"),
    vehicle: Optional[str] = Query(None, description="Filter by Driver Vehicle"),
    payment_method: Optional[str] = Query(None, description="Filter by Payment Method"),
    distance_bin: Optional[str] = Query(None, description="Filter by Distance Category"),
    order_value_tier: Optional[str] = Query(None, description="Filter by Order Value Tier"),
    is_rush_hour: Optional[int] = Query(None, description="Filter by Rush Hour (0 or 1)")
):
    """GET /api/analytics/overview - Core executive KPIs."""
    try:
        filtered_df = analytics_service.filter_df(
            city=city, traffic_level=traffic_level, time_of_day=time_of_day,
            day_of_week=day_of_week, vehicle=vehicle, payment_method=payment_method,
            distance_bin=distance_bin, order_value_tier=order_value_tier, is_rush_hour=is_rush_hour
        )
        return analytics_service.get_overview(filtered_df)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to calculate overview analytics: {str(e)}")


@router.get("/city", response_model=List[CityAnalyticsItem])
def get_city_analytics(
    city: Optional[str] = Query(None),
    traffic_level: Optional[str] = Query(None),
    time_of_day: Optional[str] = Query(None),
    day_of_week: Optional[str] = Query(None),
    vehicle: Optional[str] = Query(None),
    payment_method: Optional[str] = Query(None),
    distance_bin: Optional[str] = Query(None),
    order_value_tier: Optional[str] = Query(None),
    is_rush_hour: Optional[int] = Query(None)
):
    """GET /api/analytics/city - Operational metrics by City."""
    try:
        filtered_df = analytics_service.filter_df(
            city=city, traffic_level=traffic_level, time_of_day=time_of_day,
            day_of_week=day_of_week, vehicle=vehicle, payment_method=payment_method,
            distance_bin=distance_bin, order_value_tier=order_value_tier, is_rush_hour=is_rush_hour
        )
        return analytics_service.get_city_analytics(filtered_df)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to calculate city analytics: {str(e)}")


@router.get("/traffic", response_model=List[TrafficAnalyticsItem])
def get_traffic_analytics(
    city: Optional[str] = Query(None),
    traffic_level: Optional[str] = Query(None),
    time_of_day: Optional[str] = Query(None),
    day_of_week: Optional[str] = Query(None),
    vehicle: Optional[str] = Query(None),
    payment_method: Optional[str] = Query(None),
    distance_bin: Optional[str] = Query(None),
    order_value_tier: Optional[str] = Query(None),
    is_rush_hour: Optional[int] = Query(None)
):
    """GET /api/analytics/traffic - Performance by Traffic Congestion Level."""
    try:
        filtered_df = analytics_service.filter_df(
            city=city, traffic_level=traffic_level, time_of_day=time_of_day,
            day_of_week=day_of_week, vehicle=vehicle, payment_method=payment_method,
            distance_bin=distance_bin, order_value_tier=order_value_tier, is_rush_hour=is_rush_hour
        )
        return analytics_service.get_traffic_analytics(filtered_df)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to calculate traffic analytics: {str(e)}")


@router.get("/status", response_model=List[StatusAnalyticsItem])
def get_status_analytics(
    city: Optional[str] = Query(None),
    traffic_level: Optional[str] = Query(None),
    time_of_day: Optional[str] = Query(None),
    day_of_week: Optional[str] = Query(None),
    vehicle: Optional[str] = Query(None),
    payment_method: Optional[str] = Query(None),
    distance_bin: Optional[str] = Query(None),
    order_value_tier: Optional[str] = Query(None),
    is_rush_hour: Optional[int] = Query(None)
):
    """GET /api/analytics/status - Order outcome status distribution."""
    try:
        filtered_df = analytics_service.filter_df(
            city=city, traffic_level=traffic_level, time_of_day=time_of_day,
            day_of_week=day_of_week, vehicle=vehicle, payment_method=payment_method,
            distance_bin=distance_bin, order_value_tier=order_value_tier, is_rush_hour=is_rush_hour
        )
        return analytics_service.get_status_analytics(filtered_df)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to calculate status analytics: {str(e)}")


@router.get("/duration-distribution", response_model=List[DurationBinItem])
def get_duration_distribution(
    city: Optional[str] = Query(None),
    traffic_level: Optional[str] = Query(None),
    time_of_day: Optional[str] = Query(None),
    day_of_week: Optional[str] = Query(None),
    vehicle: Optional[str] = Query(None),
    payment_method: Optional[str] = Query(None),
    distance_bin: Optional[str] = Query(None),
    order_value_tier: Optional[str] = Query(None),
    is_rush_hour: Optional[int] = Query(None)
):
    """GET /api/analytics/duration-distribution - Histogram duration bins and counts."""
    try:
        filtered_df = analytics_service.filter_df(
            city=city, traffic_level=traffic_level, time_of_day=time_of_day,
            day_of_week=day_of_week, vehicle=vehicle, payment_method=payment_method,
            distance_bin=distance_bin, order_value_tier=order_value_tier, is_rush_hour=is_rush_hour
        )
        return analytics_service.get_duration_distribution(filtered_df)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to calculate duration distribution: {str(e)}")


@router.get("/time-of-day", response_model=List[TimeOfDayAnalyticsItem])
def get_time_of_day_analytics(
    city: Optional[str] = Query(None),
    traffic_level: Optional[str] = Query(None),
    time_of_day: Optional[str] = Query(None),
    day_of_week: Optional[str] = Query(None),
    vehicle: Optional[str] = Query(None),
    payment_method: Optional[str] = Query(None),
    distance_bin: Optional[str] = Query(None),
    order_value_tier: Optional[str] = Query(None),
    is_rush_hour: Optional[int] = Query(None)
):
    """GET /api/analytics/time-of-day - Metrics grouped by 4-hour Time of Day segment."""
    try:
        filtered_df = analytics_service.filter_df(
            city=city, traffic_level=traffic_level, time_of_day=time_of_day,
            day_of_week=day_of_week, vehicle=vehicle, payment_method=payment_method,
            distance_bin=distance_bin, order_value_tier=order_value_tier, is_rush_hour=is_rush_hour
        )
        return analytics_service.get_time_of_day_analytics(filtered_df)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to calculate time-of-day analytics: {str(e)}")


@router.get("/day-of-week", response_model=List[DayOfWeekAnalyticsItem])
def get_day_of_week_analytics(
    city: Optional[str] = Query(None),
    traffic_level: Optional[str] = Query(None),
    time_of_day: Optional[str] = Query(None),
    day_of_week: Optional[str] = Query(None),
    vehicle: Optional[str] = Query(None),
    payment_method: Optional[str] = Query(None),
    distance_bin: Optional[str] = Query(None),
    order_value_tier: Optional[str] = Query(None),
    is_rush_hour: Optional[int] = Query(None)
):
    """GET /api/analytics/day-of-week - Metrics grouped by Day of Week."""
    try:
        filtered_df = analytics_service.filter_df(
            city=city, traffic_level=traffic_level, time_of_day=time_of_day,
            day_of_week=day_of_week, vehicle=vehicle, payment_method=payment_method,
            distance_bin=distance_bin, order_value_tier=order_value_tier, is_rush_hour=is_rush_hour
        )
        return analytics_service.get_day_of_week_analytics(filtered_df)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to calculate day-of-week analytics: {str(e)}")


@router.get("/vehicle", response_model=List[VehicleAnalyticsItem])
def get_vehicle_analytics(
    city: Optional[str] = Query(None),
    traffic_level: Optional[str] = Query(None),
    time_of_day: Optional[str] = Query(None),
    day_of_week: Optional[str] = Query(None),
    vehicle: Optional[str] = Query(None),
    payment_method: Optional[str] = Query(None),
    distance_bin: Optional[str] = Query(None),
    order_value_tier: Optional[str] = Query(None),
    is_rush_hour: Optional[int] = Query(None)
):
    """GET /api/analytics/vehicle - Metrics grouped by Courier Vehicle Type."""
    try:
        filtered_df = analytics_service.filter_df(
            city=city, traffic_level=traffic_level, time_of_day=time_of_day,
            day_of_week=day_of_week, vehicle=vehicle, payment_method=payment_method,
            distance_bin=distance_bin, order_value_tier=order_value_tier, is_rush_hour=is_rush_hour
        )
        return analytics_service.get_vehicle_analytics(filtered_df)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to calculate vehicle analytics: {str(e)}")


@router.get("/order-quantity", response_model=List[OrderQuantityAnalyticsItem])
def get_order_quantity_analytics(
    city: Optional[str] = Query(None),
    traffic_level: Optional[str] = Query(None),
    time_of_day: Optional[str] = Query(None),
    day_of_week: Optional[str] = Query(None),
    vehicle: Optional[str] = Query(None),
    payment_method: Optional[str] = Query(None),
    distance_bin: Optional[str] = Query(None),
    order_value_tier: Optional[str] = Query(None),
    is_rush_hour: Optional[int] = Query(None)
):
    """GET /api/analytics/order-quantity - Metrics grouped by Item Quantity (1-5)."""
    try:
        filtered_df = analytics_service.filter_df(
            city=city, traffic_level=traffic_level, time_of_day=time_of_day,
            day_of_week=day_of_week, vehicle=vehicle, payment_method=payment_method,
            distance_bin=distance_bin, order_value_tier=order_value_tier, is_rush_hour=is_rush_hour
        )
        return analytics_service.get_order_quantity_analytics(filtered_df)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to calculate order quantity analytics: {str(e)}")


@router.get("/order-value", response_model=List[OrderValueAnalyticsItem])
def get_order_value_analytics(
    city: Optional[str] = Query(None),
    traffic_level: Optional[str] = Query(None),
    time_of_day: Optional[str] = Query(None),
    day_of_week: Optional[str] = Query(None),
    vehicle: Optional[str] = Query(None),
    payment_method: Optional[str] = Query(None),
    distance_bin: Optional[str] = Query(None),
    order_value_tier: Optional[str] = Query(None),
    is_rush_hour: Optional[int] = Query(None)
):
    """GET /api/analytics/order-value - Metrics grouped by Order_Value_Tier."""
    try:
        filtered_df = analytics_service.filter_df(
            city=city, traffic_level=traffic_level, time_of_day=time_of_day,
            day_of_week=day_of_week, vehicle=vehicle, payment_method=payment_method,
            distance_bin=distance_bin, order_value_tier=order_value_tier, is_rush_hour=is_rush_hour
        )
        return analytics_service.get_order_value_analytics(filtered_df)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to calculate order value analytics: {str(e)}")


@router.get("/distance", response_model=DistanceAnalyticsResponse)
def get_distance_analytics(
    city: Optional[str] = Query(None),
    traffic_level: Optional[str] = Query(None),
    time_of_day: Optional[str] = Query(None),
    day_of_week: Optional[str] = Query(None),
    vehicle: Optional[str] = Query(None),
    payment_method: Optional[str] = Query(None),
    distance_bin: Optional[str] = Query(None),
    order_value_tier: Optional[str] = Query(None),
    is_rush_hour: Optional[int] = Query(None)
):
    """GET /api/analytics/distance - Distance correlation and distance bin analytics."""
    try:
        filtered_df = analytics_service.filter_df(
            city=city, traffic_level=traffic_level, time_of_day=time_of_day,
            day_of_week=day_of_week, vehicle=vehicle, payment_method=payment_method,
            distance_bin=distance_bin, order_value_tier=order_value_tier, is_rush_hour=is_rush_hour
        )
        return analytics_service.get_distance_analytics(filtered_df)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to calculate distance analytics: {str(e)}")


@router.get("/insights", response_model=List[InsightItem])
def get_insights(
    city: Optional[str] = Query(None),
    traffic_level: Optional[str] = Query(None),
    time_of_day: Optional[str] = Query(None),
    day_of_week: Optional[str] = Query(None),
    vehicle: Optional[str] = Query(None),
    payment_method: Optional[str] = Query(None),
    distance_bin: Optional[str] = Query(None),
    order_value_tier: Optional[str] = Query(None),
    is_rush_hour: Optional[int] = Query(None)
):
    """GET /api/analytics/insights - Descriptive analytical insights (strictly non-causal)."""
    try:
        filtered_df = analytics_service.filter_df(
            city=city, traffic_level=traffic_level, time_of_day=time_of_day,
            day_of_week=day_of_week, vehicle=vehicle, payment_method=payment_method,
            distance_bin=distance_bin, order_value_tier=order_value_tier, is_rush_hour=is_rush_hour
        )
        return analytics_service.get_insights(filtered_df)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve insights: {str(e)}")


@router.get("/filters", response_model=FiltersResponse)
def get_filters():
    """GET /api/analytics/filters - Dynamic dropdown filter options."""
    try:
        return analytics_service.get_filters()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve filter options: {str(e)}")
