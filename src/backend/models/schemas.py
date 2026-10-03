"""
Pydantic Schemas for FoodFlow Analytics API Request/Response Payloads.
"""

from typing import List, Optional
from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    status: str = Field(..., examples=["healthy"])
    dataset_loaded: bool = Field(..., examples=[True])
    total_records: int = Field(..., examples=[10000])
    dataset_path: str = Field(..., examples=["data/processed/food_delivery_10k.csv"])


class OverviewAnalytics(BaseModel):
    total_orders: int = Field(..., examples=[10000])
    delivered_orders: int = Field(..., examples=[8520])
    cancelled_orders: int = Field(..., examples=[980])
    in_transit_orders: int = Field(..., examples=[500])
    delivery_completion_rate: float = Field(..., examples=[85.20])
    cancellation_rate: float = Field(..., examples=[9.80])
    in_transit_rate: float = Field(..., examples=[5.00])
    delay_rate: float = Field(..., examples=[24.26])
    overall_delay_rate: float = Field(..., examples=[24.17])
    average_delivery_duration: float = Field(..., examples=[37.50])
    median_delivery_duration: float = Field(..., examples=[38.00])
    average_delay_among_delayed_orders: float = Field(..., examples=[5.65])
    average_order_value: float = Field(..., examples=[268.97])
    average_delivery_distance: float = Field(..., examples=[2.15])
    average_quantity: float = Field(..., examples=[3.00])


class CityAnalyticsItem(BaseModel):
    city: str
    order_count: int
    delivered_orders: int
    average_delivery_duration: float
    delay_rate: float
    average_delay: float
    average_order_value: float


class TrafficAnalyticsItem(BaseModel):
    traffic_level: str
    order_count: int
    delivered_orders: int
    delay_rate: float
    average_delivery_duration: float


class StatusAnalyticsItem(BaseModel):
    status: str
    count: int
    percentage: float


class DurationBinItem(BaseModel):
    bin_start: int
    bin_end: int
    bin_label: str
    count: int
    percentage: float


class TimeOfDayAnalyticsItem(BaseModel):
    segment: str
    order_count: int
    delivered_orders: int
    delay_rate: float
    average_duration: float


class DayOfWeekAnalyticsItem(BaseModel):
    day_name: str
    day_of_week_index: int
    order_count: int
    delivered_orders: int
    delay_rate: float
    average_duration: float


class VehicleAnalyticsItem(BaseModel):
    vehicle: str
    order_count: int
    delivered_orders: int
    delay_rate: float
    average_duration: float
    average_speed_kmh: float


class OrderQuantityAnalyticsItem(BaseModel):
    quantity: int
    order_count: int
    delivered_orders: int
    delay_rate: float
    average_duration: float
    average_order_value: float


class OrderValueAnalyticsItem(BaseModel):
    order_value_tier: str
    order_count: int
    delivered_orders: int
    delay_rate: float
    average_order_value: float
    average_duration: float


class DistanceBinItem(BaseModel):
    distance_bin: str
    order_count: int
    delivered_orders: int
    delay_rate: float
    average_duration: float
    average_distance_km: float


class DistanceAnalyticsResponse(BaseModel):
    correlation_distance_duration: float
    correlation_distance_delay: float
    distance_bins: List[DistanceBinItem]


class InsightItem(BaseModel):
    id: str
    category: str
    title: str
    description: str
    metric: str
    direction: str
    sample_size: int
    supporting_metric: Optional[str] = None


class FiltersResponse(BaseModel):
    cities: List[str]
    traffic_levels: List[str]
    vehicles: List[str]
    payment_methods: List[str]
    distance_bins: List[str]
    order_value_tiers: List[str]
    time_segments: List[str]
    days_of_week: List[str]


class AnalyticsFilterQuery(BaseModel):
    city: Optional[str] = None
    traffic_level: Optional[str] = None
    time_of_day: Optional[str] = None
    day_of_week: Optional[str] = None
    vehicle: Optional[str] = None
    payment_method: Optional[str] = None
    distance_bin: Optional[str] = None
    order_value_tier: Optional[str] = None
    is_rush_hour: Optional[int] = None


from typing import Dict, Any


class ExplorerSummary(BaseModel):
    total_rows: int
    total_columns: int
    unique_users: int
    unique_restaurants: int
    unique_drivers: int
    unique_cities: int
    file_size_kb: float


class ColumnSchemaItem(BaseModel):
    column_name: str
    data_type: str
    unique_count: int
    missing_count: int
    missing_percentage: float
    sample_values: List[str]


class NumericalStatItem(BaseModel):
    column_name: str
    count: int
    mean: float
    std: float
    min: float
    p25: float
    median: float
    p75: float
    max: float


class CategoricalStatItem(BaseModel):
    column_name: str
    unique_count: int
    top_value: str
    top_count: int
    value_counts: Dict[str, int]


class ExplorerSummaryStats(BaseModel):
    numerical_stats: List[NumericalStatItem]
    categorical_stats: List[CategoricalStatItem]


class ExplorerRecordsResponse(BaseModel):
    page: int
    page_size: int
    total_records: int
    total_pages: int
    records: List[Dict[str, Any]]


class ExecutiveSummaryData(BaseModel):
    total_orders: int
    completion_rate: float
    cancellation_rate: float
    delay_rate: float
    avg_delivery_duration: float
    median_delivery_duration: float
    avg_delay_among_delayed: float
    total_revenue_egp: float
    avg_order_value_egp: float


class KeyObservationItem(BaseModel):
    id: str
    category: str
    finding: str
    supporting_metric: str
    type: str  # 'descriptive' or 'correlation'


class ReportSummaryResponse(BaseModel):
    title: str
    dataset_name: str
    disclaimer: str
    executive_summary: ExecutiveSummaryData
    key_observations: List[KeyObservationItem]
    data_limitations: List[str]



