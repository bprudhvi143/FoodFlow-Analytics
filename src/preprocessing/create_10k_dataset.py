"""
create_10k_dataset.py
----------------------
Phase 2: Dataset Reduction to 10,000 Rows

Applies a reproducible, multi-feature stratified sampling strategy to reduce the 
100,002-row Phase 1 featured dataset to a representative 10,000-row sample.

Key Stratification Variables:
  - Order_Status (Delivered / Cancelled / In Transit)
  - Is_Delayed_TARGET (0: On-time / 1: Delayed)
  - City (7 Egyptian cities)

Output:
  - data/processed/food_delivery_10k.csv
  - Datasets/food_delivery_10k.csv
"""

import os
import sys
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split


def create_representative_10k_sample(
    input_path: str = "data/processed/Order_delivery_featured.csv",
    output_path: str = "data/processed/food_delivery_10k.csv",
    secondary_output_path: str = "Datasets/food_delivery_10k.csv",
    target_sample_size: int = 10000,
    random_state: int = 42
) -> pd.DataFrame:
    """
    Loads Phase 1 featured dataset, performs multi-feature stratified sampling,
    validates distribution preservation, and exports the 10,000-row dataset.
    """
    print(f"=== Starting Phase 2: Dataset Reduction to {target_sample_size:,} Rows ===")
    
    if not os.path.exists(input_path):
        # Fallback if running from a different relative root
        alt_path = os.path.join(os.path.dirname(__file__), "../../", input_path)
        if os.path.exists(alt_path):
            input_path = alt_path
        else:
            raise FileNotFoundError(f"Source file not found at {input_path}")
            
    print(f"Loading Phase 1 featured dataset from: {input_path}")
    df_orig = pd.read_csv(input_path)
    orig_rows, orig_cols = df_orig.shape
    print(f"Original dataset loaded: {orig_rows:,} rows, {orig_cols} columns.")
    
    # 1. Build composite stratification key
    print("Building composite stratification key (Order_Status x Is_Delayed_TARGET x City)...")
    df_orig['_stratify_key'] = (
        df_orig['Order_Status'].astype(str) + '_' +
        df_orig['Is_Delayed_TARGET'].astype(str) + '_' +
        df_orig['City'].astype(str)
    )
    
    num_strata = df_orig['_stratify_key'].nunique()
    print(f"Total active strata: {num_strata}")
    
    # 2. Perform stratified random sampling using fixed random seed
    print(f"Sampling exactly {target_sample_size:,} rows using train_test_split (random_state={random_state})...")
    df_10k, _ = train_test_split(
        df_orig,
        train_size=target_sample_size,
        stratify=df_orig['_stratify_key'],
        random_state=random_state
    )
    
    # Drop transient stratification column
    df_10k = df_10k.drop(columns=['_stratify_key'])
    df_orig = df_orig.drop(columns=['_stratify_key'])
    
    # Sort by Order_ID for clean order
    df_10k = df_10k.sort_values('Order_ID').reset_index(drop=True)
    
    # 3. Perform Validation & Quality Checks
    print("\n--- Validation & Quality Audit ---")
    sampled_rows, sampled_cols = df_10k.shape
    assert sampled_rows == target_sample_size, f"Expected {target_sample_size} rows, got {sampled_rows}"
    assert sampled_cols == orig_cols, f"Expected {orig_cols} columns, got {sampled_cols}"
    
    unique_ids = df_10k['Order_ID'].nunique()
    assert unique_ids == target_sample_size, f"Duplicate Order_IDs detected! {unique_ids} unique out of {target_sample_size}"
    
    total_nulls = df_10k.isnull().sum().sum()
    assert total_nulls == 0, f"Unexpected missing values detected: {total_nulls}"
    
    print(f"[OK] Row count check PASSED: {sampled_rows:,} rows")
    print(f"[OK] Column count check PASSED: {sampled_cols} columns preserved")
    print(f"[OK] Unique identifier check PASSED: {unique_ids:,} unique Order_IDs (0 duplicates)")
    print(f"[OK] Missing value check PASSED: 0 nulls")
    
    # 4. Compare categorical distributions
    print("\n--- Distribution Comparison (Original vs 10k Sample) ---")
    
    for col in ['Order_Status', 'Is_Delayed_TARGET', 'City', 'Driver_Vehicle', 'Payment_Method']:
        orig_pct = df_orig[col].value_counts(normalize=True) * 100
        samp_pct = df_10k[col].value_counts(normalize=True) * 100
        comp = pd.DataFrame({'Original %': orig_pct, 'Sampled 10k %': samp_pct, 'Max Diff %': (samp_pct - orig_pct).abs()})
        print(f"\nDistribution comparison for [{col}]:")
        print(comp.round(3).to_string())
        max_diff = comp['Max Diff %'].max()
        assert max_diff < 0.5, f"Distribution shift in {col} exceeded threshold: {max_diff:.3f}%"
    
    # 5. Compare numerical statistics
    print("\n--- Numerical Summary Statistics Comparison ---")
    num_vars = ['Delivery_Duration_Minutes', 'Total_Price', 'Delivery_Distance_km', 'Total_Trip_km']
    num_comp = []
    for var in num_vars:
        num_comp.append({
            'Variable': var,
            'Orig Mean': round(df_orig[var].mean(), 2),
            'Sampled Mean': round(df_10k[var].mean(), 2),
            'Orig Median': round(df_orig[var].median(), 2),
            'Sampled Median': round(df_10k[var].median(), 2),
            'Orig Std': round(df_orig[var].std(), 2),
            'Sampled Std': round(df_10k[var].std(), 2)
        })
    print(pd.DataFrame(num_comp).to_string(index=False))
    
    # 6. Export sampled dataset
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    df_10k.to_csv(output_path, index=False)
    print(f"\nSuccessfully exported 10k dataset to: {output_path}")
    
    if secondary_output_path:
        os.makedirs(os.path.dirname(secondary_output_path), exist_ok=True)
        df_10k.to_csv(secondary_output_path, index=False)
        print(f"Successfully exported secondary copy to: {secondary_output_path}")
        
    print("\n=== Phase 2 Dataset Reduction Successfully Completed ===")
    return df_10k


if __name__ == "__main__":
    create_representative_10k_sample()
