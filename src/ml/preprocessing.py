"""
preprocessing.py
----------------
Phase 3 Reproducible Machine Learning Preprocessing Pipeline

Handles dataset loading, feature-target separation, train/test splitting,
and ColumnTransformer pipeline construction. Ensures zero target leakage by fitting
preprocessors strictly on training data.
"""

import os
import sys
import pandas as pd
import numpy as np

from sklearn.model_selection import train_test_split
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder, OrdinalEncoder, StandardScaler
from sklearn.pipeline import Pipeline

# Ensure project root is in python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))

from src.config.features import (
    PRIMARY_TARGET,
    ML_FEATURE_COLUMNS,
    LEAKAGE_COLUMNS,
    IDENTIFIER_COLUMNS
)

# Feature Taxonomy Definition
NOMINAL_CATEGORICAL_FEATURES = [
    "City",
    "Item_Name",
    "Payment_Method",
    "Driver_Vehicle",
    "Traffic_Level"
]

ORDINAL_CATEGORICAL_FEATURES = [
    "Time_Of_Day_Segment",
    "Distance_Bin",
    "Order_Value_Tier"
]

# Specified categories for OrdinalEncoder (preserves natural domain ordering)
ORDINAL_CATEGORIES = [
    ["Late Night", "Early Morning", "Morning", "Afternoon", "Evening", "Night"],
    ["Short (<1km)", "Medium (1-3km)", "Long (3-5km)", "Very Long (>5km)"],
    ["Budget (<100)", "Standard (100-300)", "Premium (300-500)", "Luxury (>500)"]
]

NUMERICAL_FEATURES = [
    "Quantity",
    "Total_Price",
    "Price_Per_Item",
    "Delivery_Distance_km",
    "Driver_To_Restaurant_km",
    "Total_Trip_km",
    "Order_Hour",
    "Order_DayOfWeek",
    "Restaurant_Lat",
    "Restaurant_Lon",
    "Customer_Lat",
    "Customer_Lon",
    "Driver_Lat",
    "Driver_Lon",
    "Is_Weekend",
    "Is_RushHour",
    "Is_Large_Order",
    "Traffic_Level_Enc"
]


def load_and_split_ml_data(
    file_path: str = "data/processed/food_delivery_ml_10k.csv",
    test_size: float = 0.20,
    random_state: int = 42
):
    """
    Loads Phase 3 ML dataset, validates column contents, separates X and y,
    and performs a stratified train/test split.
    """
    if not os.path.exists(file_path):
        alt_path = os.path.join(os.path.dirname(__file__), "../../", file_path)
        if os.path.exists(alt_path):
            file_path = alt_path
        else:
            raise FileNotFoundError(f"ML dataset not found at {file_path}")

    df_ml = pd.read_csv(file_path)
    
    # Assert zero leakage and zero identifier columns present
    for leakage_col in LEAKAGE_COLUMNS:
        assert leakage_col not in df_ml.columns, f"CRITICAL LEAKAGE: {leakage_col} found in ML dataset!"
    for id_col in IDENTIFIER_COLUMNS:
        assert id_col not in df_ml.columns, f"CRITICAL IDENTIFIER: {id_col} found in ML dataset!"

    # Separate X and y
    y = df_ml[PRIMARY_TARGET].copy()
    X = df_ml[ML_FEATURE_COLUMNS].copy()

    # Stratified Train/Test Split
    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=test_size,
        random_state=random_state,
        stratify=y
    )

    return X_train, X_test, y_train, y_test


def create_preprocessor(scale_numerics: bool = False) -> ColumnTransformer:
    """
    Constructs an scikit-learn ColumnTransformer for categorical encoding 
    and optional numerical scaling.
    
    - OneHotEncoder for nominal categoricals
    - OrdinalEncoder for ordinal categoricals
    - StandardScaler or Passthrough for numerical features
    """
    nominal_transformer = OneHotEncoder(
        drop="first",
        sparse_output=False,
        handle_unknown="ignore"
    )

    ordinal_transformer = OrdinalEncoder(
        categories=ORDINAL_CATEGORIES,
        handle_unknown="use_encoded_value",
        unknown_value=-1
    )

    if scale_numerics:
        numerical_transformer = StandardScaler()
    else:
        numerical_transformer = "passthrough"

    preprocessor = ColumnTransformer(
        transformers=[
            ("num", numerical_transformer, NUMERICAL_FEATURES),
            ("nom", nominal_transformer, NOMINAL_CATEGORICAL_FEATURES),
            ("ord", ordinal_transformer, ORDINAL_CATEGORICAL_FEATURES)
        ],
        remainder="drop",
        verbose_feature_names_out=False
    )

    return preprocessor


def get_preprocessed_data(
    file_path: str = "data/processed/food_delivery_ml_10k.csv",
    scale_numerics: bool = False,
    test_size: float = 0.20,
    random_state: int = 42
):
    """
    Complete reproducible pipeline execution:
    1. Loads X, y and performs stratified train/test split.
    2. Fits preprocessor ONLY on X_train.
    3. Transforms X_train and X_test without data leakage.
    4. Returns transformed numpy arrays / dataframes and fitted preprocessor.
    """
    X_train, X_test, y_train, y_test = load_and_split_ml_data(
        file_path=file_path,
        test_size=test_size,
        random_state=random_state
    )

    preprocessor = create_preprocessor(scale_numerics=scale_numerics)
    
    # Fit ONLY on training data to prevent data leakage
    X_train_trans = preprocessor.fit_transform(X_train)
    # Transform test data using fitted preprocessor
    X_test_trans = preprocessor.transform(X_test)

    # Feature names
    try:
        feature_names = preprocessor.get_feature_names_out()
    except Exception:
        feature_names = None

    if feature_names is not None:
        X_train_df = pd.DataFrame(X_train_trans, columns=feature_names, index=X_train.index)
        X_test_df = pd.DataFrame(X_test_trans, columns=feature_names, index=X_test.index)
    else:
        X_train_df = pd.DataFrame(X_train_trans, index=X_train.index)
        X_test_df = pd.DataFrame(X_test_trans, index=X_test.index)

    return X_train_df, X_test_df, y_train, y_test, preprocessor


if __name__ == "__main__":
    print("=== Testing ML Preprocessing Pipeline ===")
    X_tr, X_te, y_tr, y_te, prep = get_preprocessed_data()
    print(f"X_train shape: {X_tr.shape}")
    print(f"X_test shape:  {X_te.shape}")
    print(f"y_train shape: {y_tr.shape} | Target mean: {y_tr.mean():.4f}")
    print(f"y_test shape:  {y_te.shape} | Target mean: {y_te.mean():.4f}")
    print(f"Transformed features ({len(X_tr.columns)}): {list(X_tr.columns[:10])}...")
    print("=== Preprocessing Pipeline Check Complete ===")
