"""
create_phase3_datasets.py
-------------------------
Phase 3 Dataset Generator Script

Processes the Phase 2 10,000-row modeling dataset (data/processed/food_delivery_10k.csv)
and creates two logically separate datasets:

1. Analytics Dataset (data/processed/food_delivery_analytics_10k.csv):
   - 10,000 rows (all order statuses: Delivered, Cancelled, In Transit)
   - 50 columns (preserves operational, outcome, duration, and delay metrics)

2. Machine Learning Dataset (data/processed/food_delivery_ml_10k.csv):
   - 8,520 rows (filtered to Order_Status == 'Delivered' for completed delivery delay prediction)
   - 26 columns (25 safe pre-order features + 1 target Is_Delayed_TARGET)
   - 0 target leakage columns, 0 pure identifiers, 0 zero-variance columns
"""

import os
import sys
import pandas as pd
import numpy as np

# Ensure project root is in python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))

from src.config.features import (
    PRIMARY_TARGET,
    ML_FEATURE_COLUMNS,
    ANALYTICS_DATASET_COLUMNS,
    LEAKAGE_COLUMNS,
    IDENTIFIER_COLUMNS,
    ZERO_VARIANCE_COLUMNS
)


def build_phase3_datasets(
    input_path: str = "data/processed/food_delivery_10k.csv",
    analytics_output_path: str = "data/processed/food_delivery_analytics_10k.csv",
    ml_output_path: str = "data/processed/food_delivery_ml_10k.csv"
):
    print("=== Starting Phase 3 Dataset Generation ===")
    
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"Source dataset not found at {input_path}")
        
    print(f"Loading input modeling dataset from: {input_path}")
    df_10k = pd.read_csv(input_path)
    orig_rows, orig_cols = df_10k.shape
    print(f"Input dataset loaded: {orig_rows:,} rows, {orig_cols} columns.")
    
    # ---------------------------------------------------------
    # 1. BUILD ANALYTICS DATASET
    # ---------------------------------------------------------
    print("\n--- 1. Generating Analytics Dataset ---")
    # Retain all 10,000 rows across all order statuses
    # Remove only 5 zero-variance columns
    analytics_cols = [c for c in ANALYTICS_DATASET_COLUMNS if c in df_10k.columns]
    df_analytics = df_10k[analytics_cols].copy()
    
    analytics_rows, analytics_cols_cnt = df_analytics.shape
    print(f"Analytics Dataset Shape: {analytics_rows:,} rows, {analytics_cols_cnt} columns.")
    assert analytics_rows == 10000, f"Expected 10,000 rows, got {analytics_rows}"
    assert analytics_cols_cnt == 50, f"Expected 50 columns, got {analytics_cols_cnt}"
    assert df_analytics.isnull().sum().sum() == 0, "Unexpected nulls in Analytics Dataset"
    
    # Export Analytics Dataset
    os.makedirs(os.path.dirname(analytics_output_path), exist_ok=True)
    df_analytics.to_csv(analytics_output_path, index=False)
    print(f"[OK] Saved Analytics Dataset to: {analytics_output_path}")
    
    sec_analytics = "Datasets/food_delivery_analytics_10k.csv"
    os.makedirs(os.path.dirname(sec_analytics), exist_ok=True)
    df_analytics.to_csv(sec_analytics, index=False)
    print(f"[OK] Saved secondary copy to: {sec_analytics}")
    
    # ---------------------------------------------------------
    # 2. BUILD MACHINE LEARNING DATASET
    # ---------------------------------------------------------
    print("\n--- 2. Generating Machine Learning Dataset ---")
    # Filter 1: Row Filter to Completed Deliveries Only (Order_Status == 'Delivered')
    df_delivered = df_10k[df_10k['Order_Status'] == 'Delivered'].copy()
    delivered_rows = len(df_delivered)
    print(f"Filtered rows to completed deliveries (Order_Status == 'Delivered'): {delivered_rows:,} rows.")
    
    # Filter 2: Column Selection (25 ML Features + 1 Target)
    # Exclude leakage, identifiers, analytics-only, and zero-variance columns
    ml_cols = ML_FEATURE_COLUMNS + [PRIMARY_TARGET]
    # Remove duplicates if any
    ml_cols = list(dict.fromkeys(ml_cols))
    
    df_ml = df_delivered[ml_cols].copy()
    ml_rows, ml_cols_cnt = df_ml.shape
    
    print(f"ML Dataset Shape: {ml_rows:,} rows, {ml_cols_cnt} columns.")
    assert ml_rows == 8520, f"Expected 8,520 rows, got {ml_rows}"
    assert PRIMARY_TARGET in df_ml.columns, f"Target {PRIMARY_TARGET} missing from ML dataset!"
    assert df_ml.isnull().sum().sum() == 0, "Unexpected nulls in ML Dataset"
    
    # Verify zero leakage columns present in ML dataset
    found_leakage = [c for c in LEAKAGE_COLUMNS if c in df_ml.columns]
    assert len(found_leakage) == 0, f"CRITICAL: Leakage columns detected in ML dataset: {found_leakage}"
    
    # Verify zero identifiers present in ML dataset
    found_ids = [c for c in IDENTIFIER_COLUMNS if c in df_ml.columns]
    assert len(found_ids) == 0, f"CRITICAL: Identifier columns detected in ML dataset: {found_ids}"
    
    # Verify zero-variance columns removed
    found_zv = [c for c in ZERO_VARIANCE_COLUMNS if c in df_ml.columns]
    assert len(found_zv) == 0, f"CRITICAL: Zero-variance columns detected in ML dataset: {found_zv}"
    
    print("[OK] Zero leakage columns detected in ML dataset.")
    print("[OK] Zero identifier columns detected in ML dataset.")
    print("[OK] Zero null values detected.")
    
    # Export ML Dataset
    os.makedirs(os.path.dirname(ml_output_path), exist_ok=True)
    df_ml.to_csv(ml_output_path, index=False)
    print(f"[OK] Saved ML Dataset to: {ml_output_path}")
    
    sec_ml = "Datasets/food_delivery_ml_10k.csv"
    os.makedirs(os.path.dirname(sec_ml), exist_ok=True)
    df_ml.to_csv(sec_ml, index=False)
    print(f"[OK] Saved secondary copy to: {sec_ml}")
    
    print("\n=== Phase 3 Dataset Creation Successfully Completed ===")
    return df_analytics, df_ml


if __name__ == "__main__":
    build_phase3_datasets()
