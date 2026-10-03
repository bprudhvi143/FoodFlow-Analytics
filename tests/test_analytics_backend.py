"""
Pytest suite for FoodFlow Analytics API Backend & Calculation Services.
"""

import pytest
from fastapi.testclient import TestClient
from src.backend.main import app
from src.backend.services.analytics import analytics_service

client = TestClient(app)


def test_health_endpoint():
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["dataset_loaded"] is True
    assert data["total_records"] == 10000


def test_overview_endpoint():
    response = client.get("/api/analytics/overview")
    assert response.status_code == 200
    data = response.json()
    assert data["total_orders"] == 10000
    assert data["delivered_orders"] == 8520
    assert data["cancelled_orders"] == 980
    assert data["in_transit_orders"] == 500
    assert data["delivery_completion_rate"] == 85.20
    assert data["cancellation_rate"] == 9.80
    assert data["in_transit_rate"] == 5.00
    assert data["delay_rate"] == 24.26
    assert data["average_delivery_duration"] == 37.50
    assert data["median_delivery_duration"] == 38.00
    assert data["average_order_value"] == 268.97


def test_city_analytics_endpoint():
    response = client.get("/api/analytics/city")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 7
    cities = {item["city"] for item in data}
    assert cities == {"Alexandria", "Assiut", "Cairo", "Giza", "Mansoura", "Tanta", "Zagazig"}


def test_traffic_analytics_endpoint():
    response = client.get("/api/analytics/traffic")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 3
    traffic_levels = [item["traffic_level"] for item in data]
    assert traffic_levels == ["Low", "Medium", "High"]


def test_status_analytics_endpoint():
    response = client.get("/api/analytics/status")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 3
    total_count = sum(item["count"] for item in data)
    assert total_count == 10000


def test_duration_distribution_endpoint():
    response = client.get("/api/analytics/duration-distribution")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    total_histogram_count = sum(item["count"] for item in data)
    assert total_histogram_count == 8520  # Delivered orders count


def test_time_of_day_endpoint():
    response = client.get("/api/analytics/time-of-day")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 6


def test_day_of_week_endpoint():
    response = client.get("/api/analytics/day-of-week")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 7
    days = [item["day_name"] for item in data]
    assert days == ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]


def test_vehicle_analytics_endpoint():
    response = client.get("/api/analytics/vehicle")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 3
    vehicles = {item["vehicle"] for item in data}
    assert vehicles == {"Bicycle", "Motorbike", "Car"}


def test_order_quantity_endpoint():
    response = client.get("/api/analytics/order-quantity")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 5
    quantities = [item["quantity"] for item in data]
    assert quantities == [1, 2, 3, 4, 5]


def test_order_value_endpoint():
    response = client.get("/api/analytics/order-value")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 4
    tiers = {item["order_value_tier"] for item in data}
    assert "Standard (100-300)" in tiers


def test_distance_analytics_endpoint():
    response = client.get("/api/analytics/distance")
    assert response.status_code == 200
    data = response.json()
    assert "correlation_distance_duration" in data
    assert "correlation_distance_delay" in data
    assert len(data["distance_bins"]) == 4
    assert pytest.approx(data["correlation_distance_duration"], abs=0.01) == -0.0119


def test_insights_endpoint():
    response = client.get("/api/analytics/insights")
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 5
    for insight in data:
        assert "causes" not in insight["description"].lower()


def test_filters_endpoint():
    response = client.get("/api/analytics/filters")
    assert response.status_code == 200
    data = response.json()
    assert len(data["cities"]) == 7
    assert len(data["vehicles"]) == 3


def test_query_filter_analytics():
    response = client.get("/api/analytics/overview?city=Cairo")
    assert response.status_code == 200
    data = response.json()
    assert data["total_orders"] == 1439
    assert data["delivered_orders"] == 1225


def test_explorer_summary_endpoint():
    response = client.get("/api/explorer/summary")
    assert response.status_code == 200
    data = response.json()
    assert data["total_rows"] == 10000
    assert data["total_columns"] == 55
    assert data["unique_users"] == 6048
    assert data["unique_restaurants"] == 1000
    assert data["unique_drivers"] == 500
    assert data["unique_cities"] == 7


def test_explorer_schema_endpoint():
    response = client.get("/api/explorer/schema")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 55
    col_names = [col["column_name"] for col in data]
    assert "Order_ID" in col_names
    assert "City" in col_names
    assert "Is_Delayed_TARGET" in col_names


def test_explorer_summary_stats_endpoint():
    response = client.get("/api/explorer/summary-stats")
    assert response.status_code == 200
    data = response.json()
    assert len(data["numerical_stats"]) > 0
    assert len(data["categorical_stats"]) > 0


def test_explorer_records_endpoint():
    response = client.get("/api/explorer/records?page=1&page_size=20&city=Cairo")
    assert response.status_code == 200
    data = response.json()
    assert data["page"] == 1
    assert data["page_size"] == 20
    assert data["total_records"] == 1439
    assert len(data["records"]) == 20
    for record in data["records"]:
        assert record["City"] == "Cairo"

