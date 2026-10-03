"""
feature_engineering.py
=======================
Food Delivery Analytics — Phase 2: Feature Engineering
Project : Food Delivery Analytics: Delivery Performance and Delay Prediction
Input   : Datasets/Order_delivery_cleaned.csv   (output of preprocessing_pipeline.py)
Output  : Datasets/Order_delivery_featured.csv

Design principles
-----------------
1. Every feature is derived only from columns that EXIST in the cleaned dataset.
2. Features are classified by their TEMPORAL AVAILABILITY:
       - PRE_ORDER   : known when the order is placed (safe ML input features)
       - IN_DELIVERY : known only while the delivery is active (unsafe for prediction)
       - POST_DELIVERY: known only after the delivery completes (outcome / target variables)
3. Features in the IN_DELIVERY and POST_DELIVERY categories are documented and
   computed for analytics but must NOT be used as model input features.
   Using them would constitute target leakage.
4. No feature that is directly derived from Delivery_Duration_Minutes or
   Delivery_Time may appear as a model input feature.
5. Source column requirements are verified before each computation.
   A missing required column raises a ValueError with a clear message.

Run
---
    python feature_engineering.py

Dependencies: pandas >= 1.3, numpy
"""

import os
import sys
import logging
import numpy as np
import pandas as pd
from datetime import datetime

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

CLEANED_PATH  = os.path.join("Datasets", "Order_delivery_cleaned.csv")
FEATURED_PATH = os.path.join("Datasets", "Order_delivery_featured.csv")
LOG_PATH      = "feature_engineering_report.txt"

# Delay threshold: p75 of Delivery_Duration_Minutes on DELIVERED orders only.
# Rationale: The 75th-percentile is a standard "upper acceptable quartile"
# threshold in service-level agreement definitions. Orders above this are
# classified as delayed. The threshold is computed dynamically from the data
# rather than hard-coded, so it remains valid if the dataset changes.
# Value is confirmed at runtime and written to the log.
DELAY_THRESHOLD_PERCENTILE = 75   # used to derive the threshold dynamically

# Hour boundaries used for time-of-day segmentation
HOUR_SEGMENTS = {
    "Late Night" : (0,  5),   # 00:00–04:59
    "Early Morning": (5, 9),  # 05:00–08:59
    "Morning"    : (9, 12),   # 09:00–11:59
    "Afternoon"  : (12, 17),  # 12:00–16:59
    "Evening"    : (17, 21),  # 17:00–20:59
    "Night"      : (21, 24),  # 21:00–23:59
}

# Egypt approximate geographic centre — used only for orientation, not computation
EGYPT_LAT_CENTRE = 26.82
EGYPT_LON_CENTRE = 30.80

SEPARATOR = "=" * 72

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(LOG_PATH, mode="w", encoding="utf-8"),
    ],
)
log = logging.getLogger(__name__)


def section(title):
    log.info("")
    log.info(SEPARATOR)
    log.info(f"  {title}")
    log.info(SEPARATOR)


def ok(msg):    log.info(f"[OK]       {msg}")
def note(msg):  log.info(f"[FEATURE]  {msg}")
def warn(msg):  log.info(f"[WARN]     {msg}")
def leak(msg):  log.info(f"[LEAKAGE]  {msg}")


def require_cols(df, cols, feature_name):
    """Raise ValueError if any required column is absent."""
    missing = [c for c in cols if c not in df.columns]
    if missing:
        raise ValueError(
            f"Feature '{feature_name}' requires columns {cols} "
            f"but {missing} are absent from the dataset."
        )


def validate_range(series, lo, hi, label):
    """Log out-of-range count; return mask of invalid rows."""
    bad = pd.Series(False, index=series.index)
    if lo is not None:
        bad |= series < lo
    if hi is not None:
        bad |= series > hi
    n = bad.sum()
    if n > 0:
        warn(f"{label}: {n:,} values outside [{lo}, {hi}] — review these rows.")
    else:
        ok(f"{label}: all {len(series):,} values are within [{lo}, {hi}].")
    return bad

# ---------------------------------------------------------------------------
# Haversine distance helper
# ---------------------------------------------------------------------------

def haversine_km(lat1, lon1, lat2, lon2):
    """
    Compute great-circle distance (km) between two lat/lon coordinate arrays.
    Formula: Haversine, Earth radius = 6371 km.
    All inputs must be in decimal degrees.
    """
    R = 6371.0
    phi1 = np.radians(lat1)
    phi2 = np.radians(lat2)
    dphi = np.radians(lat2 - lat1)
    dlam = np.radians(lon2 - lon1)
    a = np.sin(dphi / 2) ** 2 + np.cos(phi1) * np.cos(phi2) * np.sin(dlam / 2) ** 2
    return 2 * R * np.arcsin(np.sqrt(a))

# ---------------------------------------------------------------------------
# Step 1 — Load and re-parse datetimes
# ---------------------------------------------------------------------------

def load_and_parse(path):
    section("STEP 1 - LOAD CLEANED DATASET")
    log.info(f"  Source: {path}")
    df = pd.read_csv(path)
    log.info(f"  Shape : {df.shape[0]:,} rows x {df.shape[1]} columns")

    # Re-parse datetime strings (saved as YYYY-MM-DD HH:MM by preprocessing pipeline)
    DT_FMT = "%Y-%m-%d %H:%M"
    for col in ["Order_Time", "Delivery_Time"]:
        df[col] = pd.to_datetime(df[col], format=DT_FMT, errors="coerce")
        nat = df[col].isna().sum()
        if nat > 0:
            warn(f"{col}: {nat:,} NaT values after parsing.")
        else:
            ok(f"{col} parsed -> datetime64[us]")

    ok(f"Dataset loaded. Columns available: {df.columns.tolist()}")
    return df

# ---------------------------------------------------------------------------
# Step 2 — PRE_ORDER temporal features
# (All known at the moment the customer places the order)
# ---------------------------------------------------------------------------

def add_preorder_temporal_features(df):
    """
    Source column: Order_Time (datetime)
    Availability : PRE_ORDER — the customer and system know all of these
                   at order-placement time.
    """
    section("STEP 2 - PRE-ORDER TEMPORAL FEATURES")
    require_cols(df, ["Order_Time"], "pre-order temporal features")

    # ---- 2.1 Order_Date --------------------------------------------------
    # Formula : Order_Time.date
    # Purpose : Group orders by calendar date for daily analytics.
    # Leakage : None — date is set when the order is placed.
    note("Order_Date = Order_Time.dt.date  [PRE_ORDER]")
    df["Order_Date"] = df["Order_Time"].dt.date
    ok(f"Order_Date range: {df['Order_Date'].min()} -> {df['Order_Date'].max()}")

    # ---- 2.2 Order_Month -------------------------------------------------
    # Formula : Order_Time.month  (1=Jan … 12=Dec)
    # Purpose : Seasonal analytics; feature for models with multi-month data.
    note("Order_Month = Order_Time.dt.month  [PRE_ORDER]")
    df["Order_Month"] = df["Order_Time"].dt.month
    ok(f"Order_Month unique values: {sorted(df['Order_Month'].unique())}")

    # ---- 2.3 Order_DayName -----------------------------------------------
    # Formula : Order_Time.day_name()  (Monday … Sunday)
    # Purpose : Human-readable complement to existing Order_DayOfWeek (0-6).
    # Note    : Order_DayOfWeek already exists from preprocessing; this adds
    #           the string label only. Not duplicating the integer column.
    note("Order_DayName = Order_Time.dt.day_name()  [PRE_ORDER]")
    df["Order_DayName"] = df["Order_Time"].dt.day_name()
    ok(f"Order_DayName values: {df['Order_DayName'].value_counts().to_dict()}")

    # ---- 2.4 Time_Of_Day_Segment -----------------------------------------
    # Formula : Segment hour into named periods:
    #           Late Night (0-4), Early Morning (5-8), Morning (9-11),
    #           Afternoon (12-16), Evening (17-20), Night (21-23)
    # Purpose : Non-linear time-of-day effect for tree-based models;
    #           interpretable for analytics dashboards.
    # Note    : Order_Hour already exists. This is a categorical grouping of it.
    note(
        "Time_Of_Day_Segment: categorise Order_Hour into 6 named time bands "
        "[PRE_ORDER]"
    )
    require_cols(df, ["Order_Hour"], "Time_Of_Day_Segment")

    def assign_segment(hour):
        for label, (lo, hi) in HOUR_SEGMENTS.items():
            if lo <= hour < hi:
                return label
        return "Night"  # fallback for hour=23

    df["Time_Of_Day_Segment"] = df["Order_Hour"].apply(assign_segment)
    ok(f"Time_Of_Day_Segment counts:\n{df['Time_Of_Day_Segment'].value_counts().to_string()}")

    # ---- 2.5 Is_Weekday --------------------------------------------------
    # Formula : 1 if Order_DayOfWeek in [0,1,2,3,4] else 0
    # Purpose : Complement to existing Is_Weekend flag; explicit for clarity.
    # Note    : Is_Weekend already exists. This is its logical inverse — kept
    #           for readability in feature importance plots.
    note("Is_Weekday = 1 - Is_Weekend  [PRE_ORDER]")
    require_cols(df, ["Is_Weekend"], "Is_Weekday")
    df["Is_Weekday"] = (1 - df["Is_Weekend"]).astype(int)
    ok(f"Is_Weekday: 1={df['Is_Weekday'].sum():,}  0={(df['Is_Weekday']==0).sum():,}")

    return df

# ---------------------------------------------------------------------------
# Step 3 — PRE_ORDER geographic / distance features
# ---------------------------------------------------------------------------

def add_preorder_geo_features(df):
    """
    Source columns: Restaurant_Lat/Lon, Customer_Lat/Lon,
                    Driver_Lat/Lon (driver's last-known position),
                    City, Delivery_Distance_km
    Availability  : PRE_ORDER — all coordinates are known when the order is
                    dispatched (they reflect the positions at order time).
    """
    section("STEP 3 - PRE-ORDER GEOGRAPHIC FEATURES")
    geo_cols = [
        "Restaurant_Lat", "Restaurant_Lon",
        "Customer_Lat",   "Customer_Lon",
        "Driver_Lat",     "Driver_Lon",
        "Delivery_Distance_km",
    ]
    require_cols(df, geo_cols, "geographic features")

    # ---- 3.1 Driver_To_Restaurant_km -------------------------------------
    # Formula : Haversine(Driver_Lat, Driver_Lon, Restaurant_Lat, Restaurant_Lon)
    # Purpose : Proxy for pickup wait time — how far the driver must travel
    #           to collect the order from the restaurant. This is known at
    #           dispatch time (Driver_Lat/Lon = position when order was placed).
    # Leakage : None — driver position at order placement is available before
    #           the delivery begins.
    note(
        "Driver_To_Restaurant_km = Haversine(Driver_Lat/Lon, Restaurant_Lat/Lon) "
        "[PRE_ORDER]"
    )
    df["Driver_To_Restaurant_km"] = haversine_km(
        df["Driver_Lat"],     df["Driver_Lon"],
        df["Restaurant_Lat"], df["Restaurant_Lon"],
    ).round(6)
    validate_range(df["Driver_To_Restaurant_km"], 0, 50, "Driver_To_Restaurant_km")
    ok(f"Driver_To_Restaurant_km stats:\n{df['Driver_To_Restaurant_km'].describe().round(4).to_string()}")

    # ---- 3.2 Total_Trip_km -----------------------------------------------
    # Formula : Driver_To_Restaurant_km + Delivery_Distance_km
    #           (full trip: driver -> restaurant -> customer)
    # Purpose : Better total-distance proxy than restaurant-to-customer alone.
    #           Captures both legs of the driver's journey.
    # Leakage : None — both components are known at order time.
    note(
        "Total_Trip_km = Driver_To_Restaurant_km + Delivery_Distance_km "
        "[PRE_ORDER]"
    )
    df["Total_Trip_km"] = (
        df["Driver_To_Restaurant_km"] + df["Delivery_Distance_km"]
    ).round(6)
    validate_range(df["Total_Trip_km"], 0, 100, "Total_Trip_km")
    ok(f"Total_Trip_km stats:\n{df['Total_Trip_km'].describe().round(4).to_string()}")

    # ---- 3.3 Distance_Bin ------------------------------------------------
    # Formula : Delivery_Distance_km bucketed into 4 ordinal bins:
    #           Short  : [0, 1) km
    #           Medium : [1, 3) km
    #           Long   : [3, 5) km
    #           Very Long: [5, inf) km
    # Purpose : Non-linear distance effect for tree models and visualisations.
    note("Distance_Bin: bucket Delivery_Distance_km into 4 bands  [PRE_ORDER]")
    bins   = [0, 1, 3, 5, np.inf]
    labels = ["Short (<1km)", "Medium (1-3km)", "Long (3-5km)", "Very Long (>5km)"]
    df["Distance_Bin"] = pd.cut(
        df["Delivery_Distance_km"], bins=bins, labels=labels, right=False
    )
    ok(f"Distance_Bin counts:\n{df['Distance_Bin'].value_counts().sort_index().to_string()}")

    return df

# ---------------------------------------------------------------------------
# Step 4 — PRE_ORDER order-complexity features
# ---------------------------------------------------------------------------

def add_preorder_order_features(df):
    """
    Source columns: Quantity, Total_Price, Price_Per_Item, Item_Name,
                    Payment_Method, Driver_Vehicle, Traffic_Level_Enc
    Availability  : PRE_ORDER
    """
    section("STEP 4 - PRE-ORDER ORDER FEATURES")
    require_cols(df, ["Quantity", "Total_Price", "Price_Per_Item",
                      "Traffic_Level_Enc"], "order complexity features")

    # ---- 4.1 Order_Value_Tier --------------------------------------------
    # Formula : Segment Total_Price into 4 tiers:
    #           Budget   : [0, 100) EGP
    #           Standard : [100, 300) EGP
    #           Premium  : [300, 500) EGP
    #           Luxury   : [500, inf) EGP
    # Purpose : Captures price-tier effect on delivery priority; useful for
    #           visualisation and tree models without raw price leaking ordinal
    #           bias into linear models.
    note("Order_Value_Tier: bucket Total_Price into 4 price tiers  [PRE_ORDER]")
    price_bins   = [0, 100, 300, 500, np.inf]
    price_labels = ["Budget (<100)", "Standard (100-300)",
                    "Premium (300-500)", "Luxury (>500)"]
    df["Order_Value_Tier"] = pd.cut(
        df["Total_Price"], bins=price_bins, labels=price_labels, right=False
    )
    ok(f"Order_Value_Tier counts:\n{df['Order_Value_Tier'].value_counts().sort_index().to_string()}")

    # ---- 4.2 Is_Large_Order ----------------------------------------------
    # Formula : 1 if Quantity >= 4 else 0
    # Reasoning: Quantity 4 or 5 represent the top 40% of orders by size.
    #            Large orders may take longer to prepare and package.
    # Leakage : None — Quantity is set at order placement.
    note("Is_Large_Order = 1 if Quantity >= 4 else 0  [PRE_ORDER]")
    df["Is_Large_Order"] = (df["Quantity"] >= 4).astype(int)
    ok(f"Is_Large_Order: 1={df['Is_Large_Order'].sum():,}  "
       f"0={(df['Is_Large_Order']==0).sum():,}")

    # ---- 4.3 Is_High_Traffic --------------------------------------------
    # Formula : 1 if Traffic_Level_Enc == 2 (High) else 0
    # Purpose : Binary flag for the most severe traffic condition; complementary
    #           to the ordinal encoding already in Traffic_Level_Enc.
    note("Is_High_Traffic = 1 if Traffic_Level == 'High' else 0  [PRE_ORDER]")
    require_cols(df, ["Traffic_Level_Enc"], "Is_High_Traffic")
    df["Is_High_Traffic"] = (df["Traffic_Level_Enc"] == 2).astype(int)
    ok(f"Is_High_Traffic: 1={df['Is_High_Traffic'].sum():,}  "
       f"0={(df['Is_High_Traffic']==0).sum():,}")

    return df

# ---------------------------------------------------------------------------
# Step 5 — POST_DELIVERY outcome features
# (Computed only AFTER delivery completes — must NOT be used as model inputs)
# ---------------------------------------------------------------------------

def add_postdelivery_outcome_features(df):
    """
    Source columns: Delivery_Duration_Minutes, Order_Status
    Availability  : POST_DELIVERY — these values are only known after the
                    delivery has concluded.

    *** TARGET LEAKAGE WARNING ***
    All features in this step are OUTCOME variables. They MUST NOT appear
    in the input feature set of any predictive model. They may only be used:
      - as the prediction TARGET itself, or
      - for performance analytics AFTER the fact.

    The script appends a '_TARGET' suffix to outcome columns and records
    their names in df.attrs['leakage_columns'] for downstream enforcement.
    """
    section("STEP 5 - POST-DELIVERY OUTCOME FEATURES  [TARGET / LEAKAGE ZONE]")
    leak(
        "All features derived in this step are POST_DELIVERY outcomes. "
        "They are labelled with suffix _TARGET and must NOT be used as "
        "model input features. Use them only as prediction targets or for "
        "retrospective analytics."
    )

    leakage_cols = df.attrs.get("leakage_columns", [])

    # ---- 5.1 Compute delay threshold dynamically -------------------------
    # Threshold is the p75 of Delivery_Duration_Minutes among DELIVERED orders.
    # Rationale: p75 = "top quartile worst performance" — a common SLA boundary.
    # Using only Delivered orders excludes Cancelled/In Transit duration noise.
    require_cols(df, ["Delivery_Duration_Minutes", "Order_Status"],
                 "delay threshold computation")
    delivered_mask = df["Order_Status"] == "Delivered"
    delay_threshold = df.loc[delivered_mask, "Delivery_Duration_Minutes"].quantile(
        DELAY_THRESHOLD_PERCENTILE / 100
    )
    log.info(f"  Delay threshold (p{DELAY_THRESHOLD_PERCENTILE} of Delivered orders): "
             f"{delay_threshold:.1f} minutes")
    df.attrs["delay_threshold_minutes"] = float(delay_threshold)

    # ---- 5.2 Is_Delayed_TARGET -------------------------------------------
    # Formula : 1 if Delivery_Duration_Minutes > delay_threshold else 0
    # Source  : Delivery_Duration_Minutes  (POST_DELIVERY)
    # Leakage : YES — duration is only known after delivery completes.
    # Role    : PRIMARY CLASSIFICATION TARGET for the delay prediction model.
    note(
        f"Is_Delayed_TARGET = 1 if Delivery_Duration_Minutes > {delay_threshold:.0f} min "
        f"(p{DELAY_THRESHOLD_PERCENTILE} of Delivered orders)  [POST_DELIVERY TARGET]"
    )
    df["Is_Delayed_TARGET"] = (
        df["Delivery_Duration_Minutes"] > delay_threshold
    ).astype(int)
    n_delayed = df.loc[delivered_mask, "Is_Delayed_TARGET"].sum()
    n_delivered = delivered_mask.sum()
    ok(
        f"Is_Delayed_TARGET (Delivered only): {n_delayed:,} delayed "
        f"({n_delayed/n_delivered*100:.1f}% of Delivered orders)"
    )
    validate_range(df["Is_Delayed_TARGET"], 0, 1, "Is_Delayed_TARGET")
    leakage_cols.append("Is_Delayed_TARGET")

    # ---- 5.3 Delay_Minutes_TARGET ----------------------------------------
    # Formula : max(0, Delivery_Duration_Minutes - delay_threshold)
    # Source  : Delivery_Duration_Minutes  (POST_DELIVERY)
    # Leakage : YES
    # Role    : REGRESSION TARGET — minutes beyond the threshold.
    #           Zero for on-time orders; positive for delayed orders.
    note(
        "Delay_Minutes_TARGET = max(0, Delivery_Duration_Minutes - threshold) "
        "[POST_DELIVERY TARGET]"
    )
    df["Delay_Minutes_TARGET"] = np.maximum(
        0, df["Delivery_Duration_Minutes"] - delay_threshold
    ).round(2)
    ok(
        f"Delay_Minutes_TARGET: mean={df.loc[delivered_mask,'Delay_Minutes_TARGET'].mean():.2f} "
        f"max={df.loc[delivered_mask,'Delay_Minutes_TARGET'].max():.1f} min"
    )
    leakage_cols.append("Delay_Minutes_TARGET")

    # ---- 5.4 Duration_Bin_TARGET -----------------------------------------
    # Formula : Bucket Delivery_Duration_Minutes:
    #           Fast    : [15, 30)
    #           Normal  : [30, 45)
    #           Slow    : [45, 60]
    # Source  : Delivery_Duration_Minutes  (POST_DELIVERY)
    # Leakage : YES
    # Role    : Multi-class classification target; interpretable performance tier.
    note(
        "Duration_Bin_TARGET: bucket Delivery_Duration_Minutes into "
        "Fast/Normal/Slow  [POST_DELIVERY TARGET]"
    )
    dur_bins   = [0, 30, 45, np.inf]
    dur_labels = ["Fast (<30min)", "Normal (30-45min)", "Slow (>45min)"]
    df["Duration_Bin_TARGET"] = pd.cut(
        df["Delivery_Duration_Minutes"],
        bins=dur_bins, labels=dur_labels, right=False
    )
    ok(f"Duration_Bin_TARGET counts:\n{df['Duration_Bin_TARGET'].value_counts().sort_index().to_string()}")
    leakage_cols.append("Duration_Bin_TARGET")

    # ---- 5.5 Order_To_Delivery_Minutes_TARGET ----------------------------
    # Formula : (Delivery_Time - Order_Time).total_seconds() / 60
    # Source  : Delivery_Time  (POST_DELIVERY) — redundant with stored column
    #           but provides an independently computed value.
    # Leakage : YES — Delivery_Time is the outcome timestamp.
    # Note    : This should equal Delivery_Duration_Minutes exactly (0 mismatch
    #           confirmed in preprocessing). Included as an explicit derived
    #           column for completeness; confirms the stored value.
    note(
        "Order_To_Delivery_Minutes_TARGET = (Delivery_Time - Order_Time) in minutes "
        "[POST_DELIVERY TARGET] -- redundant with Delivery_Duration_Minutes, "
        "included for explicit auditability"
    )
    require_cols(df, ["Order_Time", "Delivery_Time"],
                 "Order_To_Delivery_Minutes_TARGET")
    df["Order_To_Delivery_Minutes_TARGET"] = (
        (df["Delivery_Time"] - df["Order_Time"]).dt.total_seconds() / 60
    ).round(2)
    # Verify consistency with stored duration
    diff = (df["Order_To_Delivery_Minutes_TARGET"] -
            df["Delivery_Duration_Minutes"]).abs()
    mismatch = (diff > 1.0).sum()
    if mismatch > 0:
        warn(f"Order_To_Delivery_Minutes_TARGET: {mismatch:,} rows differ from "
             "Delivery_Duration_Minutes by >1 min.")
    else:
        ok("Order_To_Delivery_Minutes_TARGET matches Delivery_Duration_Minutes "
           "exactly for all rows.")
    leakage_cols.append("Order_To_Delivery_Minutes_TARGET")

    df.attrs["leakage_columns"] = leakage_cols
    log.info(f"  Leakage-flagged columns so far: {leakage_cols}")
    return df

# ---------------------------------------------------------------------------
# Step 6 — Analytical flags (cross-cutting, analytics-only)
# ---------------------------------------------------------------------------

def add_analytics_flags(df):
    """
    Flags derived for analytics dashboards and monitoring. These combine
    PRE_ORDER and POST_DELIVERY signals. Each is labelled with its availability.
    """
    section("STEP 6 - ANALYTICS FLAGS")

    leakage_cols = df.attrs.get("leakage_columns", [])

    # ---- 6.1 Is_Successful_Delivery --------------------------------------
    # Formula : 1 if Order_Status == 'Delivered' else 0
    # Source  : Order_Status (POST_DELIVERY — the terminal state is only
    #           known after the event concludes)
    # Leakage : YES — status is a post-event outcome.
    # Note    : Is_Delivered already exists from preprocessing. This is an
    #           explicit alias with leakage labelling for clarity.
    #           We reuse the existing column rather than creating a duplicate.
    leak(
        "Is_Delivered (from preprocessing) = POST_DELIVERY status outcome. "
        "Do not use as a model input feature. Already present in dataset."
    )
    leakage_cols.append("Is_Delivered")  # flag existing col as leakage

    # ---- 6.2 Delivery_Speed_kmh_ANALYTICAL -------------------------------
    # Formula : (Delivery_Distance_km / Delivery_Duration_Minutes) * 60
    #           = average speed in km/h during the customer-to-delivery leg.
    # Source  : Delivery_Duration_Minutes (POST_DELIVERY)
    # Leakage : YES — requires duration which is post-delivery.
    # Role    : Analytics metric only (driver performance, route efficiency).
    note(
        "Delivery_Speed_kmh_ANALYTICAL = "
        "(Delivery_Distance_km / Delivery_Duration_Minutes) * 60  "
        "[POST_DELIVERY - analytics only]"
    )
    require_cols(df, ["Delivery_Distance_km", "Delivery_Duration_Minutes"],
                 "Delivery_Speed_kmh_ANALYTICAL")

    # Guard: duration=0 would cause division by zero (none in dataset, but defensive)
    zero_dur = (df["Delivery_Duration_Minutes"] == 0).sum()
    if zero_dur > 0:
        warn(f"Delivery_Duration_Minutes has {zero_dur} zero values — "
             "speed will be inf for those rows.")

    df["Delivery_Speed_kmh_ANALYTICAL"] = (
        df["Delivery_Distance_km"] / df["Delivery_Duration_Minutes"].replace(0, np.nan) * 60
    ).round(4)
    validate_range(df["Delivery_Speed_kmh_ANALYTICAL"], 0, 200,
                   "Delivery_Speed_kmh_ANALYTICAL")
    ok(
        f"Delivery_Speed_kmh_ANALYTICAL stats:\n"
        f"{df['Delivery_Speed_kmh_ANALYTICAL'].describe().round(3).to_string()}"
    )
    leakage_cols.append("Delivery_Speed_kmh_ANALYTICAL")

    # ---- 6.3 Distance_Per_Minute_ANALYTICAL ------------------------------
    # Formula : Delivery_Distance_km / Delivery_Duration_Minutes
    #           = distance covered per minute (km/min).
    # Source  : Delivery_Duration_Minutes (POST_DELIVERY)
    # Leakage : YES
    # Role    : Analytics metric; more directly interpretable as efficiency ratio.
    note(
        "Distance_Per_Minute_ANALYTICAL = "
        "Delivery_Distance_km / Delivery_Duration_Minutes  "
        "[POST_DELIVERY - analytics only]"
    )
    df["Distance_Per_Minute_ANALYTICAL"] = (
        df["Delivery_Distance_km"] / df["Delivery_Duration_Minutes"].replace(0, np.nan)
    ).round(6)
    leakage_cols.append("Distance_Per_Minute_ANALYTICAL")
    ok(f"Distance_Per_Minute_ANALYTICAL: mean={df['Distance_Per_Minute_ANALYTICAL'].mean():.5f}")

    df.attrs["leakage_columns"] = leakage_cols
    return df

# ---------------------------------------------------------------------------
# Step 7 — Feature registry and leakage summary
# ---------------------------------------------------------------------------

def print_feature_registry(df):
    section("STEP 7 - FEATURE REGISTRY AND LEAKAGE SUMMARY")

    leakage_cols = set(df.attrs.get("leakage_columns", []))
    delay_thresh = df.attrs.get("delay_threshold_minutes", "N/A")
    log.info(f"  Delay threshold used: {delay_thresh} minutes")

    # Reconstruct lists
    original_raw_cols = [
        "Order_ID", "User_ID", "Restaurant_ID", "Driver_ID", "Item_Name",
        "Quantity", "Total_Price", "Order_Time", "Delivery_Time",
        "Delivery_Duration_Minutes", "City", "Payment_Method", "Order_Status",
        "Driver_Vehicle", "Restaurant_Lat", "Restaurant_Lon",
        "Customer_Lat", "Customer_Lon", "Driver_Lat", "Driver_Lon",
        "Delivery_Distance_km", "Traffic_Level", "Driver_Availability",
    ]
    preprocessing_cols = [
        "Restaurant_Geo_Imputed", "Customer_Geo_Imputed", "Driver_Geo_Imputed",
        "Same_Location_Flag", "Order_Hour", "Order_DayOfWeek", "Order_DayOfMonth",
        "Is_Weekend", "Is_RushHour", "Price_Per_Item", "Traffic_Level_Enc",
        "Driver_Online", "Is_Delivered", "Is_Cancelled", "Is_InTransit",
    ]
    new_feature_cols = [
        c for c in df.columns
        if c not in original_raw_cols and c not in preprocessing_cols
    ]

    log.info(f"\n  New features added in this script: {len(new_feature_cols)}")
    log.info(f"  {'Feature':<45} {'Availability':<20} {'Leakage?'}")
    log.info(f"  {'-'*45} {'-'*20} {'-'*8}")

    feature_meta = {
        # PRE_ORDER features
        "Order_Date"                      : ("PRE_ORDER",    False),
        "Order_Month"                     : ("PRE_ORDER",    False),
        "Order_DayName"                   : ("PRE_ORDER",    False),
        "Time_Of_Day_Segment"             : ("PRE_ORDER",    False),
        "Is_Weekday"                      : ("PRE_ORDER",    False),
        "Driver_To_Restaurant_km"         : ("PRE_ORDER",    False),
        "Total_Trip_km"                   : ("PRE_ORDER",    False),
        "Distance_Bin"                    : ("PRE_ORDER",    False),
        "Order_Value_Tier"                : ("PRE_ORDER",    False),
        "Is_Large_Order"                  : ("PRE_ORDER",    False),
        "Is_High_Traffic"                 : ("PRE_ORDER",    False),
        # POST_DELIVERY targets
        "Is_Delayed_TARGET"               : ("POST_DELIVERY", True),
        "Delay_Minutes_TARGET"            : ("POST_DELIVERY", True),
        "Duration_Bin_TARGET"             : ("POST_DELIVERY", True),
        "Order_To_Delivery_Minutes_TARGET": ("POST_DELIVERY", True),
        # Analytics-only (post-delivery)
        "Delivery_Speed_kmh_ANALYTICAL"   : ("POST_DELIVERY", True),
        "Distance_Per_Minute_ANALYTICAL"  : ("POST_DELIVERY", True),
    }

    for col in new_feature_cols:
        avail, is_leak = feature_meta.get(col, ("UNKNOWN", "?"))
        leak_str = "YES ***" if is_leak else "No"
        log.info(f"  {col:<45} {avail:<20} {leak_str}")

    log.info("")
    safe_features = [c for c in df.columns
                     if c not in leakage_cols
                     and c not in ["Order_Time", "Delivery_Time",
                                   "Delivery_Duration_Minutes", "Order_Status",
                                   "Order_Date"]  # dates / targets
                     and c not in original_raw_cols[:4]  # high-card IDs
                     ]
    log.info(f"  Safe ML input features (PRE_ORDER, no leakage): {len(safe_features)}")
    for f in safe_features:
        log.info(f"    - {f}")

# ---------------------------------------------------------------------------
# Step 8 — Validation
# ---------------------------------------------------------------------------

def validate_featured_dataset(df):
    section("STEP 8 - FINAL VALIDATION")

    ok(f"Shape: {df.shape[0]:,} rows x {df.shape[1]} columns")

    # No row should have been added or removed
    expected_rows = 100002
    if df.shape[0] != expected_rows:
        warn(f"Row count changed! Expected {expected_rows:,}, got {df.shape[0]:,}.")
    else:
        ok(f"Row count unchanged at {df.shape[0]:,}.")

    # Missing values
    null_counts = df.isnull().sum()
    # Categorical cuts (pd.Categorical) may produce NaN for out-of-bin values
    null_cols = null_counts[null_counts > 0]
    if len(null_cols) > 0:
        for col, n in null_cols.items():
            warn(f"Null values in {col}: {n:,}")
    else:
        ok("No null values in any column.")

    # Validate new binary flags are 0/1 only
    binary_cols = ["Is_Weekday", "Is_Large_Order", "Is_High_Traffic",
                   "Is_Delayed_TARGET"]
    for col in binary_cols:
        if col in df.columns:
            bad = ~df[col].isin([0, 1])
            if bad.sum() > 0:
                warn(f"{col}: {bad.sum():,} values outside {{0, 1}}.")
            else:
                ok(f"{col}: all values are 0 or 1.")

    # Validate haversine distance
    ok(f"Driver_To_Restaurant_km range: "
       f"[{df['Driver_To_Restaurant_km'].min():.4f}, "
       f"{df['Driver_To_Restaurant_km'].max():.4f}] km")

    # Validate delay flag vs threshold
    thresh = df.attrs.get("delay_threshold_minutes")
    if thresh:
        delivered = df["Order_Status"] == "Delivered"
        should_be_delayed = df.loc[delivered, "Delivery_Duration_Minutes"] > thresh
        is_flagged        = df.loc[delivered, "Is_Delayed_TARGET"] == 1
        mismatch = (should_be_delayed != is_flagged).sum()
        if mismatch > 0:
            warn(f"Is_Delayed_TARGET: {mismatch:,} rows mismatch the threshold logic.")
        else:
            ok(f"Is_Delayed_TARGET: flags are perfectly consistent with "
               f"threshold {thresh:.1f} min.")

    # Validate speed is non-negative
    if "Delivery_Speed_kmh_ANALYTICAL" in df.columns:
        neg_speed = (df["Delivery_Speed_kmh_ANALYTICAL"] < 0).sum()
        if neg_speed > 0:
            warn(f"Delivery_Speed_kmh_ANALYTICAL: {neg_speed:,} negative values.")
        else:
            ok("Delivery_Speed_kmh_ANALYTICAL: all values >= 0.")

    ok(f"Final column list ({df.shape[1]} total):\n  "
       + "\n  ".join(df.columns.tolist()))

# ---------------------------------------------------------------------------
# Step 9 — Save
# ---------------------------------------------------------------------------

def save_featured(df, path):
    section("STEP 9 - SAVE FEATURED DATASET")

    df_save = df.copy()

    # Serialise datetime back to string
    for col in ["Order_Time", "Delivery_Time"]:
        if pd.api.types.is_datetime64_any_dtype(df_save[col]):
            df_save[col] = df_save[col].dt.strftime("%Y-%m-%d %H:%M")

    # Serialise date column
    if "Order_Date" in df_save.columns:
        df_save["Order_Date"] = df_save["Order_Date"].astype(str)

    # Convert pd.Categorical to string for CSV portability
    for col in df_save.select_dtypes(include="category").columns:
        df_save[col] = df_save[col].astype(str)

    df_save.to_csv(path, index=False, encoding="utf-8")
    size_kb = os.path.getsize(path) / 1024
    ok(f"Saved: {path}  ({df_save.shape[0]:,} rows x {df_save.shape[1]} columns, {size_kb:,.0f} KB)")
    log.info(
        f"  Input (cleaned):  {CLEANED_PATH}\n"
        f"  Output (featured): {path}\n"
        f"  Feature report:    {LOG_PATH}"
    )

# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    log.info(SEPARATOR)
    log.info("  Food Delivery Analytics - Feature Engineering Pipeline")
    log.info(f"  Run at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    log.info(SEPARATOR)

    df = load_and_parse(CLEANED_PATH)
    df.attrs["leakage_columns"] = []

    df = add_preorder_temporal_features(df)
    df = add_preorder_geo_features(df)
    df = add_preorder_order_features(df)
    df = add_postdelivery_outcome_features(df)
    df = add_analytics_flags(df)

    print_feature_registry(df)
    validate_featured_dataset(df)
    save_featured(df, FEATURED_PATH)

    section("PIPELINE COMPLETE")
    log.info(f"  Input rows    : 100,002 (unchanged)")
    log.info(f"  Output columns: {df.shape[1]}")
    log.info(f"  Delay threshold: {df.attrs.get('delay_threshold_minutes')} min")
    log.info(f"  Leakage-flagged columns: {df.attrs.get('leakage_columns')}")
    log.info(f"  Featured dataset: {FEATURED_PATH}")
    log.info(f"  Feature report  : {LOG_PATH}")


if __name__ == "__main__":
    main()
