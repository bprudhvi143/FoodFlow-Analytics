"""
feature_engineering.py
=======================
Food Delivery Analytics — Phase 2 Feature Engineering
Project : Food Delivery Analytics: Delivery Performance and Delay Prediction

Input  : data/processed/Order_delivery_cleaned.csv
Output : data/processed/Order_delivery_featured.csv
Log    : logs/feature_engineering_report.txt

Usage
-----
    python src/preprocessing/feature_engineering.py
"""

import os
import sys
import logging
from datetime import datetime

import numpy as np
import pandas as pd

PROJECT_ROOT  = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
CLEANED_PATH  = os.path.join(PROJECT_ROOT, "data", "processed", "Order_delivery_cleaned.csv")
FEATURED_PATH = os.path.join(PROJECT_ROOT, "data", "processed", "Order_delivery_featured.csv")
LOG_PATH      = os.path.join(PROJECT_ROOT, "logs", "feature_engineering_report.txt")

DELAY_THRESHOLD_PERCENTILE = 75
HOUR_SEGMENTS = {
    "Late Night"   : (0,  5),
    "Early Morning": (5,  9),
    "Morning"      : (9, 12),
    "Afternoon"    : (12, 17),
    "Evening"      : (17, 21),
    "Night"        : (21, 24),
}

os.makedirs(os.path.dirname(LOG_PATH), exist_ok=True)

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

logging.basicConfig(
    level=logging.INFO, format="%(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(LOG_PATH, mode="w", encoding="utf-8"),
    ],
)
log = logging.getLogger(__name__)

SEP = "=" * 72
def section(t): log.info(f"\n{SEP}\n  {t}\n{SEP}")
def ok(m):      log.info(f"[OK]      {m}")
def note(m):    log.info(f"[FEATURE] {m}")
def warn(m):    log.info(f"[WARN]    {m}")
def leak(m):    log.info(f"[LEAKAGE] {m}")


def haversine_km(lat1, lon1, lat2, lon2):
    R = 6371.0
    p1, p2 = np.radians(lat1), np.radians(lat2)
    dp = np.radians(lat2 - lat1)
    dl = np.radians(lon2 - lon1)
    a = np.sin(dp/2)**2 + np.cos(p1)*np.cos(p2)*np.sin(dl/2)**2
    return 2 * R * np.arcsin(np.sqrt(a))


def load(path):
    section("STEP 1 - LOAD CLEANED DATASET")
    df = pd.read_csv(path)
    df["Order_Time"]    = pd.to_datetime(df["Order_Time"],    format="%Y-%m-%d %H:%M", errors="coerce")
    df["Delivery_Time"] = pd.to_datetime(df["Delivery_Time"], format="%Y-%m-%d %H:%M", errors="coerce")
    ok(f"Loaded {df.shape[0]:,} rows x {df.shape[1]} columns from {path}")
    return df


def add_preorder_temporal(df):
    section("STEP 2 - PRE-ORDER TEMPORAL FEATURES")
    df["Order_Date"]     = df["Order_Time"].dt.date
    df["Order_Month"]    = df["Order_Time"].dt.month
    df["Order_DayName"]  = df["Order_Time"].dt.day_name()
    def seg(h):
        for label, (lo, hi) in HOUR_SEGMENTS.items():
            if lo <= h < hi: return label
        return "Night"
    df["Time_Of_Day_Segment"] = df["Order_Hour"].apply(seg)
    df["Is_Weekday"] = (1 - df["Is_Weekend"]).astype(int)
    ok("Added: Order_Date, Order_Month, Order_DayName, Time_Of_Day_Segment, Is_Weekday")
    return df


def add_preorder_geo(df):
    section("STEP 3 - PRE-ORDER GEOGRAPHIC FEATURES")
    df["Driver_To_Restaurant_km"] = haversine_km(
        df["Driver_Lat"], df["Driver_Lon"],
        df["Restaurant_Lat"], df["Restaurant_Lon"]
    ).round(6)
    df["Total_Trip_km"] = (df["Driver_To_Restaurant_km"] + df["Delivery_Distance_km"]).round(6)
    df["Distance_Bin"]  = pd.cut(
        df["Delivery_Distance_km"],
        bins=[0, 1, 3, 5, np.inf],
        labels=["Short (<1km)", "Medium (1-3km)", "Long (3-5km)", "Very Long (>5km)"],
        right=False
    )
    ok("Added: Driver_To_Restaurant_km, Total_Trip_km, Distance_Bin")
    return df


def add_preorder_order(df):
    section("STEP 4 - PRE-ORDER ORDER FEATURES")
    df["Order_Value_Tier"] = pd.cut(
        df["Total_Price"],
        bins=[0, 100, 300, 500, np.inf],
        labels=["Budget (<100)", "Standard (100-300)", "Premium (300-500)", "Luxury (>500)"],
        right=False
    )
    df["Is_Large_Order"]  = (df["Quantity"] >= 4).astype(int)
    df["Is_High_Traffic"] = (df["Traffic_Level_Enc"] == 2).astype(int)
    ok("Added: Order_Value_Tier, Is_Large_Order, Is_High_Traffic")
    return df


def add_postdelivery_targets(df):
    section("STEP 5 - POST-DELIVERY TARGET VARIABLES  [LEAKAGE ZONE]")
    leak("All features in this step are POST_DELIVERY. Never use as model inputs.")

    delivered = df["Order_Status"] == "Delivered"
    threshold = df.loc[delivered, "Delivery_Duration_Minutes"].quantile(
        DELAY_THRESHOLD_PERCENTILE / 100
    )
    df.attrs["delay_threshold"] = float(threshold)
    log.info(f"  Delay threshold (p{DELAY_THRESHOLD_PERCENTILE} of Delivered): {threshold:.1f} min")

    df["Is_Delayed_TARGET"]  = (df["Delivery_Duration_Minutes"] > threshold).astype(int)
    df["Delay_Minutes_TARGET"] = np.maximum(0, df["Delivery_Duration_Minutes"] - threshold).round(2)
    df["Duration_Bin_TARGET"]  = pd.cut(
        df["Delivery_Duration_Minutes"],
        bins=[0, 30, 45, np.inf],
        labels=["Fast (<30min)", "Normal (30-45min)", "Slow (>45min)"],
        right=False
    )
    df["Order_To_Delivery_Minutes_TARGET"] = (
        (df["Delivery_Time"] - df["Order_Time"]).dt.total_seconds() / 60
    ).round(2)
    ok(f"Targets created. Delayed (Delivered only): "
       f"{df.loc[delivered,'Is_Delayed_TARGET'].sum():,} / {delivered.sum():,} "
       f"({df.loc[delivered,'Is_Delayed_TARGET'].mean()*100:.1f}%)")
    return df


def add_analytics_metrics(df):
    section("STEP 6 - POST-DELIVERY ANALYTICS METRICS  [LEAKAGE ZONE]")
    df["Delivery_Speed_kmh_ANALYTICAL"] = (
        df["Delivery_Distance_km"] /
        df["Delivery_Duration_Minutes"].replace(0, np.nan) * 60
    ).round(4)
    df["Distance_Per_Minute_ANALYTICAL"] = (
        df["Delivery_Distance_km"] /
        df["Delivery_Duration_Minutes"].replace(0, np.nan)
    ).round(6)
    ok("Added: Delivery_Speed_kmh_ANALYTICAL, Distance_Per_Minute_ANALYTICAL")
    return df


def save(df, path):
    section("STEP 7 - SAVE FEATURED DATASET")
    df_save = df.copy()
    for col in ["Order_Time","Delivery_Time"]:
        if pd.api.types.is_datetime64_any_dtype(df_save[col]):
            df_save[col] = df_save[col].dt.strftime("%Y-%m-%d %H:%M")
    if "Order_Date" in df_save.columns:
        df_save["Order_Date"] = df_save["Order_Date"].astype(str)
    for col in df_save.select_dtypes(include="category").columns:
        df_save[col] = df_save[col].astype(str)
    df_save.to_csv(path, index=False, encoding="utf-8")
    size = os.path.getsize(path) / 1024
    ok(f"Saved: {path}  ({df_save.shape[0]:,} rows x {df_save.shape[1]} cols, {size:,.0f} KB)")


def main():
    log.info(SEP)
    log.info("  Food Delivery Analytics -- Feature Engineering Pipeline")
    log.info(f"  Run at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    log.info(SEP)

    df = load(CLEANED_PATH)
    df = add_preorder_temporal(df)
    df = add_preorder_geo(df)
    df = add_preorder_order(df)
    df = add_postdelivery_targets(df)
    df = add_analytics_metrics(df)
    save(df, FEATURED_PATH)

    section("COMPLETE")
    log.info(f"  Input  : {CLEANED_PATH}")
    log.info(f"  Output : {FEATURED_PATH}")
    log.info(f"  Delay threshold : {df.attrs.get('delay_threshold')} min")


if __name__ == "__main__":
    main()
