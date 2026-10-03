"""
validate_preprocessing.py
-------------------------
Phase 3 Machine Learning Preprocessing Validation Suite

Runs 8 automated verification checks to validate pipeline execution, 
target distribution preservation, zero leakage, and proper train/test fitting isolation.
"""

import os
import sys
import pandas as pd
import numpy as np

# Ensure project root is in python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))

from src.ml.preprocessing import (
    load_and_split_ml_data,
    create_preprocessor,
    get_preprocessed_data,
    NUMERICAL_FEATURES,
    NOMINAL_CATEGORICAL_FEATURES,
    ORDINAL_CATEGORICAL_FEATURES
)
from src.config.features import LEAKAGE_COLUMNS, IDENTIFIER_COLUMNS, PRIMARY_TARGET


def run_pipeline_validation():
    print("=== Phase 3 ML Preprocessing Pipeline Validation Suite ===")
    
    # Check 1: Data Loading & Splitting
    X_train, X_test, y_train, y_test = load_and_split_ml_data(
        file_path="data/processed/food_delivery_ml_10k.csv",
        test_size=0.20,
        random_state=42
    )
    
    total_samples = len(X_train) + len(X_test)
    assert total_samples == 8520, f"Expected 8,520 total rows, got {total_samples}"
    assert len(X_train) == 6816, f"Expected 6,816 train rows, got {len(X_train)}"
    assert len(X_test) == 1704, f"Expected 1,704 test rows, got {len(X_test)}"
    print(f"[OK] Check 1 Passed: Train/Test Split dimensions ({len(X_train)} train, {len(X_test)} test, total {total_samples})")
    
    # Check 2: Target Distribution & Stratification
    train_delay_rate = y_train.mean() * 100
    test_delay_rate = y_test.mean() * 100
    overall_delay_rate = (y_train.sum() + y_test.sum()) / total_samples * 100
    
    assert abs(train_delay_rate - test_delay_rate) < 0.1, "Stratification discrepancy in target between train and test!"
    print(f"[OK] Check 2 Passed: Target Distribution Stratified (Train Delay: {train_delay_rate:.2f}%, Test Delay: {test_delay_rate:.2f}%, Overall: {overall_delay_rate:.2f}%)")
    
    # Check 3: Numerical & Categorical Feature Taxonomy
    assert len(NUMERICAL_FEATURES) == 18, f"Expected 18 numerical features, got {len(NUMERICAL_FEATURES)}"
    assert len(NOMINAL_CATEGORICAL_FEATURES) == 5, f"Expected 5 nominal categoricals, got {len(NOMINAL_CATEGORICAL_FEATURES)}"
    assert len(ORDINAL_CATEGORICAL_FEATURES) == 3, f"Expected 3 ordinal categoricals, got {len(ORDINAL_CATEGORICAL_FEATURES)}"
    print(f"[OK] Check 3 Passed: Feature Taxonomies (18 Numerical, 5 Nominal, 3 Ordinal = 26 total features)")
    
    # Check 4: Target Leakage Verification
    for leakage_col in LEAKAGE_COLUMNS:
        assert leakage_col not in X_train.columns, f"CRITICAL: Leakage column {leakage_col} in X_train!"
        assert leakage_col not in X_test.columns, f"CRITICAL: Leakage column {leakage_col} in X_test!"
    print("[OK] Check 4 Passed: 0 Target Leakage columns present in X_train or X_test")
    
    # Check 5: Identifier Verification
    for id_col in IDENTIFIER_COLUMNS:
        assert id_col not in X_train.columns, f"CRITICAL: Identifier {id_col} in X_train!"
        assert id_col not in X_test.columns, f"CRITICAL: Identifier {id_col} in X_test!"
    print("[OK] Check 5 Passed: 0 Identifier columns present in X_train or X_test")
    
    # Check 6: Pipeline Fitting Isolation (No Fitting on Full Dataset)
    preprocessor = create_preprocessor(scale_numerics=True)
    # Ensure preprocessor is unfitted initially
    assert not hasattr(preprocessor, "transformers_"), "Preprocessor should be unfitted prior to training!"
    
    # Fit ONLY on training data
    X_train_trans = preprocessor.fit_transform(X_train)
    assert hasattr(preprocessor, "transformers_"), "Preprocessor should be fitted after fit_transform on X_train!"
    
    # Transform test data using fitted preprocessor
    X_test_trans = preprocessor.transform(X_test)
    print("[OK] Check 6 Passed: Preprocessor fitted ONLY on X_train; X_test transformed cleanly without data leakage")
    
    # Check 7: Feature Names & Dimensionality
    feature_names = preprocessor.get_feature_names_out()
    expected_dim = X_train_trans.shape[1]
    assert len(feature_names) == expected_dim, f"Feature name count mismatch: {len(feature_names)} vs {expected_dim}"
    print(f"[OK] Check 7 Passed: Feature name output preserved ({expected_dim} encoded features)")
    
    # Check 8: Complete End-to-End Execution & Reproducibility
    X_tr1, X_te1, y_tr1, y_te1, prep1 = get_preprocessed_data(random_state=42)
    X_tr2, X_te2, y_tr2, y_te2, prep2 = get_preprocessed_data(random_state=42)
    
    pd.testing.assert_frame_equal(X_tr1, X_tr2)
    pd.testing.assert_frame_equal(X_te1, X_te2)
    pd.testing.assert_series_equal(y_tr1, y_tr2)
    pd.testing.assert_series_equal(y_te1, y_te2)
    print("[OK] Check 8 Passed: End-to-end preprocessing execution is 100% reproducible (random_state=42)")
    
    print("\n=== ALL 8 PREPROCESSING VALIDATION CHECKS PASSED SUCCESSFULLY ===")


if __name__ == "__main__":
    run_pipeline_validation()
