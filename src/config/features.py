"""
features.py
-----------
Machine-readable feature configuration for Phase 3 Data Preparation.

Defines feature taxonomies, target variables, leakage columns, identifiers, 
and analytics column specifications for food delivery analytics and ML.
"""

# Primary Target Variable for Binary Classification
PRIMARY_TARGET = "Is_Delayed_TARGET"

# Secondary Target Variables
SECONDARY_TARGETS = [
    "Delay_Minutes_TARGET",      # Regression target: max(0, duration - 45)
    "Duration_Bin_TARGET"        # Multi-class target: Fast / Normal / Slow
]

# All Target Columns
ALL_TARGET_COLUMNS = [PRIMARY_TARGET] + SECONDARY_TARGETS

# Safe Pre-Order Machine Learning Features (24 features)
ML_FEATURE_COLUMNS = [
    # Basket & Order Features
    "Quantity",
    "Total_Price",
    "Price_Per_Item",
    "Is_Large_Order",
    "Item_Name",
    "Payment_Method",

    # Geographic & Distance Features
    "City",
    "Delivery_Distance_km",
    "Driver_To_Restaurant_km",
    "Total_Trip_km",
    "Distance_Bin",
    "Order_Value_Tier",

    # Spatial Coordinates
    "Restaurant_Lat",
    "Restaurant_Lon",
    "Customer_Lat",
    "Customer_Lon",
    "Driver_Lat",
    "Driver_Lon",

    # Temporal Features
    "Order_Hour",
    "Order_DayOfWeek",
    "Is_Weekend",
    "Is_RushHour",
    "Time_Of_Day_Segment",

    # Mobility & Environment Features
    "Driver_Vehicle",
    "Traffic_Level",
    "Traffic_Level_Enc"
]

# Direct & Indirect Target Leakage Columns (Excluded from ML)
LEAKAGE_COLUMNS = [
    "Delivery_Time",
    "Delivery_Duration_Minutes",
    "Is_Delivered",
    "Is_Cancelled",
    "Is_InTransit",
    "Order_To_Delivery_Minutes_TARGET",
    "Delivery_Speed_kmh_ANALYTICAL",
    "Distance_Per_Minute_ANALYTICAL"
]

# Identifier Columns (Excluded from ML input matrices)
IDENTIFIER_COLUMNS = [
    "Order_ID",
    "User_ID",
    "Restaurant_ID",
    "Driver_ID"
]

# Analytics-Only & Contextual Columns
ANALYTICAL_ONLY_COLUMNS = [
    "Order_Status",         # Primary dataset row filter (Delivered)
    "Order_Time",           # Placement timestamp string
    "Order_Date",           # Date YYYY-MM-DD
    "Order_DayName",        # Day of week string
    "Order_DayOfMonth",     # Day of month (1-16)
    "Is_Weekday",           # Perfectly collinear with Is_Weekend (1 - Is_Weekend)
    "Driver_Availability",  # System extraction snapshot status
    "Driver_Online"         # Binary encoded extraction snapshot status
]

# Zero-Variance Columns Recommended for Removal
ZERO_VARIANCE_COLUMNS = [
    "Restaurant_Geo_Imputed",
    "Customer_Geo_Imputed",
    "Driver_Geo_Imputed",
    "Same_Location_Flag",
    "Order_Month"
]

# Complete Column List for Analytics Dataset (50 Columns)
ANALYTICS_DATASET_COLUMNS = [
    col for col in [
        # Identifiers
        "Order_ID", "User_ID", "Restaurant_ID", "Driver_ID",
        # Business & Order Specs
        "Item_Name", "Quantity", "Total_Price", "Price_Per_Item", "Order_Value_Tier", "Is_Large_Order", "Payment_Method",
        # Geography & Distance
        "City", "Delivery_Distance_km", "Driver_To_Restaurant_km", "Total_Trip_km", "Distance_Bin",
        "Restaurant_Lat", "Restaurant_Lon", "Customer_Lat", "Customer_Lon", "Driver_Lat", "Driver_Lon",
        # Fleet & Mobility
        "Driver_Vehicle", "Driver_Availability", "Driver_Online", "Traffic_Level", "Traffic_Level_Enc", "Is_High_Traffic",
        # Temporal Specs
        "Order_Time", "Delivery_Time", "Order_Date", "Order_DayName", "Order_Hour", "Order_DayOfWeek", "Order_DayOfMonth",
        "Time_Of_Day_Segment", "Is_Weekend", "Is_Weekday", "Is_RushHour",
        # Outcomes & Duration
        "Order_Status", "Is_Delivered", "Is_Cancelled", "Is_InTransit", "Delivery_Duration_Minutes",
        # Targets
        "Is_Delayed_TARGET", "Delay_Minutes_TARGET", "Duration_Bin_TARGET", "Order_To_Delivery_Minutes_TARGET",
        # Analytical Metrics
        "Delivery_Speed_kmh_ANALYTICAL", "Distance_Per_Minute_ANALYTICAL"
    ] if col not in ZERO_VARIANCE_COLUMNS
]

# Complete Column List for Machine Learning Dataset (ML Features + Target)
ML_DATASET_COLUMNS = ML_FEATURE_COLUMNS + [PRIMARY_TARGET]
