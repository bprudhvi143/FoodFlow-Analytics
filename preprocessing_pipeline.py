"""
preprocessing_pipeline.py
==========================
Food Delivery Analytics — Phase 1: Preprocessing Pipeline
Project : Food Delivery Analytics: Delivery Performance and Delay Prediction
Dataset : Datasets/Order_delivery.csv  (100,002 rows × 23 columns)

Purpose
-------
Produce a cleaned, type-correct, enriched copy of the raw dataset.
The raw file is NEVER modified.  Every decision is documented inline.

Output
------
Datasets/Order_delivery_cleaned.csv   — cleaned dataset (same row count unless
                                        genuine hard errors are found)
preprocessing_report.txt             — machine-readable audit log

Run
---
    python preprocessing_pipeline.py

Dependencies: pandas >= 1.3, numpy
"""

import os
import sys
import logging
import textwrap
from datetime import datetime

import numpy as np
import pandas as pd

# ---------------------------------------------------------------------------
# 0 · Configuration
# ---------------------------------------------------------------------------

RAW_PATH     = os.path.join("Datasets", "Order_delivery.csv")
CLEANED_PATH = os.path.join("Datasets", "Order_delivery_cleaned.csv")
LOG_PATH     = "preprocessing_report.txt"

# Datetime string format used in the raw CSV
DT_FORMAT = "%d-%m-%Y %H:%M"

# Egypt geographic bounds (generous; used only for impossible-value detection)
GEO_BOUNDS = {
    "lat": (20.0, 33.0),   # Egypt spans roughly 22°N to 31.8°N
    "lon": (24.0, 38.0),   # Egypt spans roughly 25°E to 37°E
}

# Delivery duration hard limits (minutes) – based on profiling
DURATION_MIN =  5    # below 5 min is physically impossible for any Egyptian city
DURATION_MAX = 240   # above 4 h is effectively impossible for in-city food delivery

# Traffic level ordinal mapping  (Low < Medium < High)
TRAFFIC_ORDER = {"Low": 0, "Medium": 1, "High": 2}

# Driver availability binary mapping
AVAILABILITY_BINARY = {"Online": 1, "Offline": 0}

# ---------------------------------------------------------------------------
# 1 · Logging setup  (writes to both stdout and a log file)
# ---------------------------------------------------------------------------

# Force stdout to UTF-8 on Windows (avoids cp1252 UnicodeEncodeError)
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

SEPARATOR = "=" * 72


def section(title: str) -> None:
    log.info("")
    log.info(SEPARATOR)
    log.info(f"  {title}")
    log.info(SEPARATOR)


def note(msg: str) -> None:
    """Log a decision note (prefixed so it is easy to grep)."""
    log.info(f"[DECISION] {msg}")


def flag(msg: str) -> None:
    """Log a flagged anomaly (not necessarily an error)."""
    log.info(f"[FLAG]     {msg}")


def ok(msg: str) -> None:
    log.info(f"[OK]       {msg}")


# ---------------------------------------------------------------------------
# 2 · Helper utilities
# ---------------------------------------------------------------------------

def _count_pct(mask: pd.Series, label: str) -> None:
    n = mask.sum()
    pct = n / len(mask) * 100
    log.info(f"           {label}: {n:,}  ({pct:.2f}%)")


# ---------------------------------------------------------------------------
# 3 · Load raw data
# ---------------------------------------------------------------------------

def load_raw(path: str) -> pd.DataFrame:
    section("STEP 1 · LOAD RAW DATASET")
    log.info(f"  Source : {path}")

    df = pd.read_csv(path)

    log.info(f"  Shape  : {df.shape[0]:,} rows × {df.shape[1]} columns")
    log.info(f"  Columns: {df.columns.tolist()}")
    note("Raw file is loaded into memory only.  It will NOT be written back.")
    return df


# ---------------------------------------------------------------------------
# 4 · Duplicate checks
# ---------------------------------------------------------------------------

def check_duplicates(df: pd.DataFrame) -> pd.DataFrame:
    section("STEP 2 · DUPLICATE CHECKS")

    # 4a — full-row duplicates
    full_dups = df.duplicated()
    _count_pct(full_dups, "Full-row duplicates")
    if full_dups.sum() > 0:
        note(
            "Dropping full-row duplicates.  A row that is identical in every "
            "field across all 23 columns carries no additional information and "
            "is treated as a data-entry error."
        )
        df = df[~full_dups].reset_index(drop=True)
        flag(f"Dropped {full_dups.sum():,} full-row duplicate(s).")
    else:
        ok("No full-row duplicates found.")

    # 4b — duplicate Order_ID (primary key)
    pk_dups = df.duplicated(subset=["Order_ID"])
    _count_pct(pk_dups, "Duplicate Order_ID values")
    if pk_dups.sum() > 0:
        # Keep first occurrence — later occurrences are assumed re-submissions
        note(
            "Keeping the first occurrence of each Order_ID and dropping "
            "subsequent duplicates.  Order_ID is the primary key; a second "
            "row with the same ID is a re-submission or system duplication, "
            "not an independent event."
        )
        before = len(df)
        df = df.drop_duplicates(subset=["Order_ID"], keep="first").reset_index(drop=True)
        flag(f"Dropped {before - len(df):,} rows with duplicate Order_ID.")
    else:
        ok("Order_ID is unique — no primary-key violations.")

    return df


# ---------------------------------------------------------------------------
# 5 · Missing-value audit and treatment
# ---------------------------------------------------------------------------

def handle_missing_values(df: pd.DataFrame) -> pd.DataFrame:
    """
    Treatment strategy by column semantic type:

    IDENTIFIER columns (Order_ID, User_ID, Restaurant_ID, Driver_ID):
        A missing identifier means the row cannot be linked to any entity.
        These rows are dropped.  Filling with a placeholder ID would create
        false groupings.

    DATETIME columns (Order_Time, Delivery_Time):
        Temporal analysis is the core of this project.  A row without a
        valid timestamp cannot be placed in time and cannot contribute to
        duration calculations.  These rows are dropped.

    NUMERICAL columns with a natural substitute (Quantity, Total_Price,
    Delivery_Duration_Minutes, Delivery_Distance_km):
        There is no safe imputation strategy for these key metrics without
        introducing bias.  Rows are flagged; if counts are very small
        (< 0.1% of total), they are dropped.  If counts are large, a
        median/model-based strategy would be applied instead (documented
        below per column).

    CATEGORICAL columns (City, Payment_Method, Order_Status, Driver_Vehicle,
    Traffic_Level, Driver_Availability, Item_Name):
        A single missing value in a low-cardinality column is imputed with
        the mode only if the column is not the target variable.
        Order_Status is the secondary classification target and must NOT be
        imputed — those rows are dropped.
        Traffic_Level has natural ordinal order; mode imputation is acceptable
        as a last resort because it introduces minimal directional bias.

    GEO columns (lat/lon × 3 pairs):
        A missing coordinate cannot be reconstructed without city-level
        coordinates (which are available via City).  However, since we are
        NOT dropping any useful column yet, we impute with the city-level
        median coordinate as a reasonable spatial approximation and add a
        boolean flag column to mark the imputed rows.
    """
    section("STEP 3 · MISSING VALUE AUDIT AND TREATMENT")

    missing = df.isnull().sum()
    total_missing = missing.sum()

    if total_missing == 0:
        ok("No missing values detected in any column.  No imputation required.")
        note(
            "Missing value treatment strategy is documented here for "
            "reproducibility.  If missing values appear in future data "
            "refreshes, the logic below will apply automatically."
        )
    else:
        flag(f"Total missing cells: {total_missing:,}")
        log.info(missing[missing > 0].to_string())

    # --- IDENTIFIER COLUMNS ---
    id_cols = ["Order_ID", "User_ID", "Restaurant_ID", "Driver_ID"]
    note(
        "IDENTIFIER columns (Order_ID, User_ID, Restaurant_ID, Driver_ID): "
        "rows with a missing identifier are DROPPED.  Imputing an identifier "
        "with a placeholder creates false entity groupings and corrupts any "
        "aggregation performed at the customer, restaurant, or driver level."
    )
    id_missing_mask = df[id_cols].isnull().any(axis=1)
    if id_missing_mask.sum() > 0:
        flag(f"Dropping {id_missing_mask.sum():,} rows with missing identifier(s).")
        df = df[~id_missing_mask].reset_index(drop=True)
    else:
        ok("No missing values in identifier columns.")

    # --- DATETIME COLUMNS ---
    dt_cols = ["Order_Time", "Delivery_Time"]
    note(
        "DATETIME columns (Order_Time, Delivery_Time): rows with a missing "
        "timestamp are DROPPED.  Delivery duration cannot be computed, and "
        "time-of-day / day-of-week features cannot be extracted.  These rows "
        "would need to be excluded from every time-sensitive analysis anyway."
    )
    dt_missing_mask = df[dt_cols].isnull().any(axis=1)
    if dt_missing_mask.sum() > 0:
        flag(f"Dropping {dt_missing_mask.sum():,} rows with missing datetime(s).")
        df = df[~dt_missing_mask].reset_index(drop=True)
    else:
        ok("No missing values in datetime columns.")

    # --- ORDER_STATUS (classification target) ---
    note(
        "Order_Status (classification target): rows with a missing status are "
        "DROPPED.  Imputing the target variable would introduce label noise "
        "that directly corrupts model training.  Status is also a required "
        "filter for the delay prediction task."
    )
    status_missing = df["Order_Status"].isnull()
    if status_missing.sum() > 0:
        flag(f"Dropping {status_missing.sum():,} rows with missing Order_Status.")
        df = df[~status_missing].reset_index(drop=True)
    else:
        ok("No missing values in Order_Status.")

    # --- DELIVERY_DURATION_MINUTES ---
    note(
        "Delivery_Duration_Minutes (primary regression target): rows with a "
        "missing duration are DROPPED if count < 0.1% of total.  There is no "
        "valid way to impute the label of a supervised regression target "
        "without introducing circularity or heavy bias.  If count exceeds "
        "0.1%, a note is raised for manual review."
    )
    dur_missing = df["Delivery_Duration_Minutes"].isnull()
    _count_pct(dur_missing, "Missing Delivery_Duration_Minutes")
    if dur_missing.sum() > 0:
        pct = dur_missing.sum() / len(df) * 100
        if pct <= 0.1:
            df = df[~dur_missing].reset_index(drop=True)
            flag(f"Dropped {dur_missing.sum():,} rows with missing duration (≤ 0.1% — safe to drop).")
        else:
            flag(
                f"WARNING: {dur_missing.sum():,} rows ({pct:.2f}%) have missing "
                "Delivery_Duration_Minutes.  This exceeds the 0.1% threshold. "
                "MANUAL REVIEW REQUIRED before deciding on imputation strategy."
            )
    else:
        ok("No missing values in Delivery_Duration_Minutes.")

    # --- OTHER NUMERICAL COLUMNS ---
    other_num = ["Quantity", "Total_Price", "Delivery_Distance_km"]
    note(
        "Other numerical columns (Quantity, Total_Price, Delivery_Distance_km): "
        "rows with missing values are DROPPED if count < 0.1% of total.  "
        "Median imputation is used if count is between 0.1% and 1%, because "
        "these features are not direct targets.  Above 1%, a flag is raised "
        "for manual review."
    )
    for col in other_num:
        mask = df[col].isnull()
        if mask.sum() == 0:
            ok(f"No missing values in {col}.")
            continue
        pct = mask.sum() / len(df) * 100
        _count_pct(mask, f"Missing {col}")
        if pct <= 0.1:
            df = df[~mask].reset_index(drop=True)
            flag(f"Dropped {mask.sum():,} rows with missing {col} (≤ 0.1%).")
        elif pct <= 1.0:
            median_val = df[col].median()
            df.loc[mask, col] = median_val
            flag(f"Imputed {mask.sum():,} missing {col} values with median={median_val:.4f}.")
            note(f"Median imputation for {col}: robust to skew, does not extend range.")
        else:
            flag(f"WARNING: {col} has {pct:.2f}% missing — MANUAL REVIEW REQUIRED.")

    # --- GEO COLUMNS ---
    geo_pairs = [
        ("Restaurant_Lat", "Restaurant_Lon"),
        ("Customer_Lat",   "Customer_Lon"),
        ("Driver_Lat",     "Driver_Lon"),
    ]
    note(
        "Geo coordinate columns: if a latitude/longitude pair is partially "
        "or fully missing, it is imputed with the city-level median coordinate "
        "of the same City.  A boolean flag column (e.g. Restaurant_Geo_Imputed) "
        "is added to identify imputed rows.  The city-level median is accurate "
        "to within ~0.04 degrees (~4 km), which is acceptable for city-level "
        "analytics.  Rows where City is also missing would be dropped, but "
        "City has no missing values (confirmed in profiling)."
    )
    for lat_col, lon_col in geo_pairs:
        prefix = lat_col.replace("_Lat", "")
        flag_col = f"{prefix}_Geo_Imputed"
        imputed_mask = df[[lat_col, lon_col]].isnull().any(axis=1)
        df[flag_col] = 0  # initialise; 1 = imputed
        if imputed_mask.sum() > 0:
            city_medians = df.groupby("City")[[lat_col, lon_col]].transform("median")
            df.loc[imputed_mask, lat_col] = city_medians.loc[imputed_mask, lat_col]
            df.loc[imputed_mask, lon_col] = city_medians.loc[imputed_mask, lon_col]
            df.loc[imputed_mask, flag_col] = 1
            flag(f"Imputed {imputed_mask.sum():,} missing {lat_col}/{lon_col} with city median.")
        else:
            ok(f"No missing values in {lat_col} / {lon_col}.")

    # --- CATEGORICAL COLUMNS (remaining) ---
    cat_cols = ["Item_Name", "City", "Payment_Method",
                "Driver_Vehicle", "Traffic_Level", "Driver_Availability"]
    note(
        "Remaining categorical columns: mode imputation is applied if count "
        "< 0.5% of total.  Mode is chosen over a placeholder ('Unknown') "
        "because these columns have 2–9 balanced categories; a dedicated "
        "'Unknown' category would appear in only a handful of rows and would "
        "create a near-zero-frequency category that degrades model performance.  "
        "Above 0.5%, rows are dropped."
    )
    for col in cat_cols:
        mask = df[col].isnull()
        if mask.sum() == 0:
            ok(f"No missing values in {col}.")
            continue
        pct = mask.sum() / len(df) * 100
        _count_pct(mask, f"Missing {col}")
        if pct <= 0.5:
            mode_val = df[col].mode()[0]
            df.loc[mask, col] = mode_val
            flag(f"Imputed {mask.sum():,} missing {col} values with mode='{mode_val}'.")
        else:
            before = len(df)
            df = df[~mask].reset_index(drop=True)
            flag(f"Dropped {before - len(df):,} rows with missing {col} (> 0.5%).")

    log.info(f"  Rows after missing-value treatment: {len(df):,}")
    return df


# ---------------------------------------------------------------------------
# 6 · Data-type coercions
# ---------------------------------------------------------------------------

def fix_dtypes(df: pd.DataFrame) -> pd.DataFrame:
    section("STEP 4 · DATA TYPE CORRECTIONS")

    # 6a — Parse datetime strings
    note(
        "Order_Time and Delivery_Time are stored as plain strings in the raw "
        "CSV (format DD-MM-YYYY HH:MM).  They are converted to datetime64[ns] "
        "using pd.to_datetime with the exact format to avoid ambiguous parsing.  "
        "errors='coerce' turns any unparseable string into NaT so it can be "
        "caught in the next validation step rather than raising an exception."
    )
    for col in ["Order_Time", "Delivery_Time"]:
        before_nulls = df[col].isnull().sum()
        df[col] = pd.to_datetime(df[col], format=DT_FORMAT, errors="coerce")
        new_nat = df[col].isnull().sum() - before_nulls
        if new_nat > 0:
            flag(f"{col}: {new_nat:,} values could not be parsed (became NaT).")
        else:
            ok(f"{col} parsed successfully -> dtype={df[col].dtype}")

    # 6b — Numeric columns: coerce to proper types
    note(
        "Numerical columns are re-coerced with pd.to_numeric(errors='coerce') "
        "to catch any values that slipped through as object dtype due to mixed "
        "types or stray non-numeric characters in the raw CSV.  NaN values "
        "produced by coercion are then handled by the missing-value logic."
    )
    int_cols   = ["Order_ID", "Restaurant_ID", "Driver_ID",
                  "Quantity", "Delivery_Duration_Minutes"]
    float_cols = ["Total_Price", "Restaurant_Lat", "Restaurant_Lon",
                  "Customer_Lat", "Customer_Lon",
                  "Driver_Lat",   "Driver_Lon",
                  "Delivery_Distance_km"]

    for col in int_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce")
        # Drop rows that became NaN after coercion (coercion produced NaN from
        # a value that was already valid or already handled above)
        bad = df[col].isnull()
        if bad.sum() > 0:
            flag(f"{col}: {bad.sum():,} values failed numeric coercion — dropping rows.")
            df = df[~bad].reset_index(drop=True)
        # Downcast to integer after NaN check (pandas nullable int)
        df[col] = df[col].astype("Int64")
        ok(f"{col} -> dtype={df[col].dtype}")

    for col in float_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce")
        bad = df[col].isnull()
        if bad.sum() > 0:
            flag(f"{col}: {bad.sum():,} values failed numeric coercion -- dropping rows.")
            df = df[~bad].reset_index(drop=True)
        ok(f"{col} -> dtype={df[col].dtype}")

    # 6c — String columns: ensure they are proper Python str (not object with mixed types)
    str_cols = ["User_ID", "Item_Name", "City", "Payment_Method",
                "Order_Status", "Driver_Vehicle", "Traffic_Level", "Driver_Availability"]
    for col in str_cols:
        df[col] = df[col].astype(str)
        ok(f"{col} -> dtype=str")

    log.info(f"  Rows after dtype coercion: {len(df):,}")
    return df


# ---------------------------------------------------------------------------
# 7 · Categorical standardisation
# ---------------------------------------------------------------------------

def standardise_categoricals(df: pd.DataFrame) -> pd.DataFrame:
    section("STEP 5 · CATEGORICAL STANDARDISATION")

    cat_cols = ["User_ID", "Item_Name", "City", "Payment_Method",
                "Order_Status", "Driver_Vehicle", "Traffic_Level", "Driver_Availability"]

    # 7a — Strip leading/trailing whitespace
    note(
        "Leading and trailing whitespace is stripped from all string columns.  "
        "Trailing spaces are invisible in CSV viewers but cause category splits "
        "('Delivered ' != 'Delivered') that inflate unique-value counts and "
        "break joins and groupby operations."
    )
    for col in cat_cols:
        before_uniq = df[col].nunique()
        df[col] = df[col].str.strip()
        after_uniq = df[col].nunique()
        if before_uniq != after_uniq:
            flag(f"{col}: whitespace stripping changed unique count {before_uniq} → {after_uniq}.")
        else:
            ok(f"{col}: no whitespace issues found.")

    # 7b — Normalise capitalisation
    note(
        "Known fixed-vocabulary columns are normalised to their canonical "
        "capitalisation using a lookup map.  This corrects accidental "
        "all-lowercase or all-uppercase variants (e.g. 'high' -> 'High', "
        "'BICYCLE' -> 'Bicycle') without altering meaningful case distinctions "
        "like 'U3522' for User_ID."
    )
    canonical_maps = {
        "Order_Status"       : {"delivered": "Delivered", "cancelled": "Cancelled",
                                "in transit": "In Transit", "in_transit": "In Transit"},
        "Driver_Vehicle"     : {"bicycle": "Bicycle", "car": "Car", "motorbike": "Motorbike"},
        "Traffic_Level"      : {"low": "Low", "medium": "Medium", "high": "High"},
        "Driver_Availability": {"online": "Online", "offline": "Offline"},
        "Payment_Method"     : {"cash": "Cash", "wallet": "Wallet",
                                "credit card": "Credit Card", "creditcard": "Credit Card"},
        "City"               : {"cairo": "Cairo", "giza": "Giza", "alexandria": "Alexandria",
                                "tanta": "Tanta", "mansoura": "Mansoura",
                                "zagazig": "Zagazig", "assiut": "Assiut"},
        "Item_Name"          : {"burger": "Burger", "pizza": "Pizza", "salad": "Salad",
                                "sushi": "Sushi", "pasta": "Pasta", "koshary": "Koshary",
                                "shawarma": "Shawarma", "sandwich": "Sandwich",
                                "fried chicken": "Fried Chicken"},
    }
    for col, cmap in canonical_maps.items():
        # Only rows whose current value is NOT already in the valid canonical set
        valid_set = set(canonical_maps[col].values()) if col in canonical_maps else set()
        # Build the full expected canonical set for this column from the expected dict
        # (populated later, but we can derive it from the map values)
        canonical_values = set(cmap.values())
        non_canonical_mask = ~df[col].isin(canonical_values)
        lower_series = df[col].str.lower()
        # Among non-canonical rows, check if the lowercased value is in the correction map
        fixable_mask = non_canonical_mask & lower_series.isin(cmap.keys())
        n_fixed = fixable_mask.sum()
        if n_fixed > 0:
            df.loc[fixable_mask, col] = lower_series[fixable_mask].map(cmap)
            flag(f"{col}: corrected {n_fixed:,} non-canonical capitalisation(s).")
        else:
            ok(f"{col}: all values already in canonical form.")

    # 7c — Validate that only expected categories remain
    note(
        "After standardisation, each fixed-vocabulary column is checked "
        "against its expected value set.  Any unexpected value is flagged.  "
        "Unexpected values are NOT silently dropped — they require human "
        "decision before any action (might represent a new valid category)."
    )
    expected = {
        "Order_Status"       : {"Delivered", "Cancelled", "In Transit"},
        "Driver_Vehicle"     : {"Bicycle", "Car", "Motorbike"},
        "Traffic_Level"      : {"Low", "Medium", "High"},
        "Driver_Availability": {"Online", "Offline"},
        "Payment_Method"     : {"Cash", "Wallet", "Credit Card"},
        "City"               : {"Cairo", "Giza", "Alexandria", "Tanta",
                                "Mansoura", "Zagazig", "Assiut"},
        "Item_Name"          : {"Burger", "Pizza", "Salad", "Sushi", "Pasta",
                                "Koshary", "Shawarma", "Sandwich", "Fried Chicken"},
    }
    for col, valid_set in expected.items():
        unexpected = df[~df[col].isin(valid_set)][col].unique()
        if len(unexpected) > 0:
            flag(
                f"{col}: {len(unexpected)} unexpected value(s) found: "
                f"{list(unexpected)}.  MANUAL REVIEW REQUIRED."
            )
        else:
            ok(f"{col}: all values are within the expected category set {sorted(valid_set)}.")

    # 7d — User_ID format validation (must match U followed by exactly 4 digits)
    note(
        "User_ID format is validated against the pattern U#### (U followed by "
        "exactly 4 digits).  Non-conforming IDs are flagged.  They are NOT "
        "automatically dropped because the ID might still be valid for the "
        "business; however, they should not be used as a join key without review."
    )
    uid_valid = df["User_ID"].str.match(r"^U\d{4}$", na=False)
    invalid_uids = (~uid_valid).sum()
    if invalid_uids > 0:
        flag(f"User_ID: {invalid_uids:,} values do not match U#### format.")
        log.info(df[~uid_valid]["User_ID"].value_counts().head(10).to_string())
    else:
        ok("User_ID: all values match U#### format.")

    log.info(f"  Rows after categorical standardisation: {len(df):,}")
    return df


# ---------------------------------------------------------------------------
# 8 · Numerical validity checks
# ---------------------------------------------------------------------------

def validate_numerics(df: pd.DataFrame) -> pd.DataFrame:
    section("STEP 6 · NUMERICAL VALIDITY CHECKS")

    note(
        "Numerical impossibility checks use domain knowledge to define hard "
        "lower and upper limits.  Values outside these limits are physically "
        "or operationally impossible (e.g. a negative price, a zero quantity, "
        "a delivery that takes 0 seconds).  Statistical outliers within the "
        "valid range are NOT removed here — that is a modelling decision "
        "made in Phase 2 based on the chosen algorithm."
    )

    checks = {
        # column        : (lower_incl, upper_incl, description)
        "Quantity"                 : (1,   5,    "Items per order: must be 1–5 (per dataset domain)"),
        "Total_Price"              : (0.01, None, "Price must be positive (> 0 EGP)"),
        "Delivery_Duration_Minutes": (DURATION_MIN, DURATION_MAX,
                                      f"Duration must be {DURATION_MIN}–{DURATION_MAX} min"),
        "Delivery_Distance_km"     : (0.001, 100, "Distance must be > 1 m and < 100 km"),
        "Restaurant_Lat"           : (GEO_BOUNDS["lat"][0], GEO_BOUNDS["lat"][1],
                                      "Restaurant latitude must be within Egypt"),
        "Restaurant_Lon"           : (GEO_BOUNDS["lon"][0], GEO_BOUNDS["lon"][1],
                                      "Restaurant longitude must be within Egypt"),
        "Customer_Lat"             : (GEO_BOUNDS["lat"][0], GEO_BOUNDS["lat"][1],
                                      "Customer latitude must be within Egypt"),
        "Customer_Lon"             : (GEO_BOUNDS["lon"][0], GEO_BOUNDS["lon"][1],
                                      "Customer longitude must be within Egypt"),
        "Driver_Lat"               : (GEO_BOUNDS["lat"][0], GEO_BOUNDS["lat"][1],
                                      "Driver latitude must be within Egypt"),
        "Driver_Lon"               : (GEO_BOUNDS["lon"][0], GEO_BOUNDS["lon"][1],
                                      "Driver longitude must be within Egypt"),
    }

    drop_mask = pd.Series(False, index=df.index)

    for col, (lo, hi, desc) in checks.items():
        col_mask = pd.Series(False, index=df.index)
        if lo is not None:
            col_mask |= df[col].fillna(-np.inf) < lo
        if hi is not None:
            col_mask |= df[col].fillna(np.inf) > hi

        n_bad = col_mask.sum()
        if n_bad > 0:
            flag(
                f"{col}: {n_bad:,} rows violate constraint [{lo}, {hi}].  "
                f"Reason: {desc}.  Sample values: "
                f"{df.loc[col_mask, col].head(5).tolist()}"
            )
            note(
                f"Rows where {col} is outside [{lo}, {hi}] are marked for "
                "removal.  These values are impossible by definition and cannot "
                "be imputed without fabricating data."
            )
            drop_mask |= col_mask
        else:
            ok(f"{col}: all values are within valid range [{lo}, {hi}].  {desc}.")

    if drop_mask.sum() > 0:
        flag(f"Total rows with at least one impossible numerical value: {drop_mask.sum():,}")
        df = df[~drop_mask].reset_index(drop=True)
    else:
        ok("No rows with impossible numerical values found.")

    log.info(f"  Rows after numerical validation: {len(df):,}")
    return df


# ---------------------------------------------------------------------------
# 9 · Datetime validation
# ---------------------------------------------------------------------------

def validate_datetimes(df: pd.DataFrame) -> pd.DataFrame:
    section("STEP 7 · DATETIME VALIDATION")

    # 9a — Drop rows where parsing produced NaT (caught from fix_dtypes step)
    nat_mask = df["Order_Time"].isnull() | df["Delivery_Time"].isnull()
    if nat_mask.sum() > 0:
        flag(
            f"{nat_mask.sum():,} rows have NaT in Order_Time or Delivery_Time "
            "after parsing (unparseable strings).  Dropping these rows because "
            "no temporal feature or duration consistency check is possible "
            "without valid timestamps."
        )
        df = df[~nat_mask].reset_index(drop=True)
    else:
        ok("No NaT values in Order_Time or Delivery_Time after parsing.")

    # 9b — Check for Delivery_Time BEFORE Order_Time (chronologically impossible)
    note(
        "A delivery cannot be completed before the order was placed.  Any row "
        "where Delivery_Time < Order_Time is a data error (likely a year/month "
        "swap or timezone corruption) and is dropped.  A row where "
        "Delivery_Time == Order_Time would mean 0-minute delivery, which is "
        "also impossible and is caught by the duration check below."
    )
    chrono_bad = df["Delivery_Time"] < df["Order_Time"]
    _count_pct(chrono_bad, "Delivery before Order (impossible)")
    if chrono_bad.sum() > 0:
        flag(
            f"Dropping {chrono_bad.sum():,} rows where Delivery_Time < Order_Time."
        )
        df = df[~chrono_bad].reset_index(drop=True)
    else:
        ok("All Delivery_Time values are at or after Order_Time.")

    # 9c — Verify stored duration matches computed duration
    note(
        "Delivery_Duration_Minutes is independently stored in the CSV.  It is "
        "cross-checked against the computed value "
        "(Delivery_Time - Order_Time in minutes).  A mismatch > 1 minute "
        "indicates that either the timestamps or the stored duration field was "
        "incorrectly recorded.  When there is a mismatch, the COMPUTED value "
        "is trusted (derived from two independent timestamp fields) and the "
        "stored duration is overwritten.  This ensures downstream calculations "
        "use a consistent duration regardless of which field was wrong."
    )
    computed_dur = (df["Delivery_Time"] - df["Order_Time"]).dt.total_seconds() / 60
    duration_diff = (computed_dur - df["Delivery_Duration_Minutes"].astype(float)).abs()
    mismatched = duration_diff > 1.0

    if mismatched.sum() > 0:
        flag(
            f"{mismatched.sum():,} rows have Delivery_Duration_Minutes inconsistent "
            "with (Delivery_Time − Order_Time) by more than 1 minute.  "
            "Overwriting stored duration with the computed value."
        )
        df.loc[mismatched, "Delivery_Duration_Minutes"] = (
            computed_dur[mismatched].round().astype(int)
        )
    else:
        ok("Delivery_Duration_Minutes is perfectly consistent with the computed difference.")

    # 9d — Check date range plausibility (dataset should span Jun 2025 only)
    note(
        "Order dates are validated against the expected dataset window "
        "(Jun 2025).  Dates outside this window may indicate format "
        "misparses (e.g. DD-MM ambiguity) and are flagged for review.  "
        "They are NOT automatically dropped — a date just outside the window "
        "could be a legitimate edge-case order."
    )
    min_date = pd.Timestamp("2025-01-01")
    max_date = pd.Timestamp("2025-12-31")
    out_of_window = (df["Order_Time"] < min_date) | (df["Order_Time"] > max_date)
    if out_of_window.sum() > 0:
        flag(
            f"{out_of_window.sum():,} orders fall outside 2025.  "
            "Review: " + str(df.loc[out_of_window, "Order_Time"].unique()[:5].tolist())
        )
    else:
        ok("All Order_Time values fall within the 2025 calendar year.")

    log.info(f"  Rows after datetime validation: {len(df):,}")
    return df


# ---------------------------------------------------------------------------
# 10 · Placeholder / suspicious value scan
# ---------------------------------------------------------------------------

def scan_placeholders(df: pd.DataFrame) -> pd.DataFrame:
    section("STEP 8 · PLACEHOLDER AND SUSPICIOUS VALUE SCAN")

    # 10a — String placeholder scan
    note(
        "Placeholder strings are a common data-entry error in which an "
        "operator enters a dummy value instead of a real one.  The following "
        "patterns are checked (case-insensitive after strip): "
        "'unknown', 'n/a', '-', 'none', 'null', '', '0', '?', 'na', "
        "'not available', 'n.a.'.  Any matched cell is converted to NaN "
        "so that the missing-value logic (Step 3) handles it consistently."
    )
    PLACEHOLDERS = {
        "unknown", "n/a", "-", "none", "null", "", "0",
        "?", "na", "not available", "n.a.", "nan",
    }
    str_cols = ["User_ID", "Item_Name", "City", "Payment_Method",
                "Order_Status", "Driver_Vehicle", "Traffic_Level", "Driver_Availability"]
    total_placeholder_cells = 0
    for col in str_cols:
        hits = df[col].str.strip().str.lower().isin(PLACEHOLDERS)
        if hits.sum() > 0:
            df.loc[hits, col] = np.nan
            total_placeholder_cells += hits.sum()
            flag(
                f"{col}: {hits.sum():,} placeholder value(s) converted to NaN "
                "for missing-value treatment."
            )
    if total_placeholder_cells == 0:
        ok("No placeholder strings found in any categorical column.")

    # 10b — Suspicious zero values in numerical columns where zero is invalid
    note(
        "Zero values are checked in columns where zero has no valid real-world "
        "meaning: Quantity (you cannot order 0 items), Total_Price (an order "
        "with zero cost is likely a test record).  Zeros in Delivery_Distance_km "
        "are physically impossible (restaurant and customer cannot be at the "
        "same GPS coordinate).  These are converted to NaN for re-handling."
    )
    zero_checks = {
        "Quantity"    : "An order of 0 items is a test/error record.",
        "Total_Price" : "An order with 0 EGP price is a test/error record.",
    }
    for col, reason in zero_checks.items():
        zeros = df[col] == 0
        if zeros.sum() > 0:
            df.loc[zeros, col] = np.nan
            flag(f"{col}: {zeros.sum():,} zero value(s) converted to NaN. Reason: {reason}")
        else:
            ok(f"{col}: no zero values found.")

    # 10c — Exact-duplicate coordinate pairs (restaurant == customer: distance ≈ 0)
    note(
        "Rows where Restaurant_Lat equals Customer_Lat AND Restaurant_Lon "
        "equals Customer_Lon to 6 decimal places are flagged.  These represent "
        "a delivery distance of exactly 0 metres, which is a data-generation "
        "anomaly.  They are NOT dropped — a delivery to the same address as "
        "the restaurant is uncommon but not impossible (e.g. an office in the "
        "same building).  They are flagged with a boolean column "
        "'Same_Location_Flag' for downstream awareness."
    )
    same_loc = (
        (df["Restaurant_Lat"].round(6) == df["Customer_Lat"].round(6)) &
        (df["Restaurant_Lon"].round(6) == df["Customer_Lon"].round(6))
    )
    df["Same_Location_Flag"] = same_loc.astype(int)
    if same_loc.sum() > 0:
        flag(
            f"{same_loc.sum():,} rows have identical restaurant and customer "
            "coordinates (distance ≈ 0 m).  Flagged in Same_Location_Flag=1."
        )
    else:
        ok("No rows with identical restaurant and customer coordinates.")

    log.info(f"  Rows after placeholder scan: {len(df):,}")
    return df


# ---------------------------------------------------------------------------
# 11 · Derived / engineered columns
# ---------------------------------------------------------------------------

def add_derived_columns(df: pd.DataFrame) -> pd.DataFrame:
    section("STEP 9 · DERIVED COLUMNS AND ENCODINGS")

    # 11a — Time-based features
    note(
        "Time-based features are derived from Order_Time (now datetime64).  "
        "These features are essential for analytics and are used as ML "
        "features in Phase 2/4.  They do not modify Order_Time or "
        "Delivery_Time — they are additive new columns."
    )
    df["Order_Hour"]        = df["Order_Time"].dt.hour
    df["Order_DayOfWeek"]   = df["Order_Time"].dt.dayofweek   # 0=Mon … 6=Sun
    df["Order_DayOfMonth"]  = df["Order_Time"].dt.day
    df["Is_Weekend"]        = df["Order_DayOfWeek"].isin([5, 6]).astype(int)

    # Rush hour: morning commute (07:00–09:59) and evening commute (18:00–21:59)
    rush_hours = set(range(7, 10)) | set(range(18, 22))
    df["Is_RushHour"]       = df["Order_Hour"].isin(rush_hours).astype(int)

    ok("Added: Order_Hour, Order_DayOfWeek, Order_DayOfMonth, Is_Weekend, Is_RushHour")

    # 11b — Price per item
    note(
        "Price_Per_Item = Total_Price / Quantity.  This captures the per-unit "
        "item tier (cheap vs expensive items) independently of order size.  "
        "Useful for analytics and as a feature that decouples price from "
        "quantity effects."
    )
    df["Price_Per_Item"] = (df["Total_Price"] / df["Quantity"]).round(4)
    ok("Added: Price_Per_Item")

    # 11c — Ordinal encoding of Traffic_Level
    note(
        "Traffic_Level has a natural order (Low < Medium < High) and is "
        "ordinal-encoded as integers 0/1/2.  This allows the ordering to be "
        "preserved in distance-based and linear models.  The original string "
        "column is retained for interpretability."
    )
    df["Traffic_Level_Enc"] = df["Traffic_Level"].map(TRAFFIC_ORDER)
    unmapped = df["Traffic_Level_Enc"].isnull().sum()
    if unmapped > 0:
        flag(f"Traffic_Level_Enc: {unmapped:,} values could not be mapped (unexpected category).")
    else:
        ok("Added: Traffic_Level_Enc (Low=0, Medium=1, High=2)")

    # 11d — Binary encoding of Driver_Availability
    note(
        "Driver_Availability is binary (Online / Offline) and is encoded as "
        "a single integer (1 / 0).  The original string column is retained."
    )
    df["Driver_Online"] = df["Driver_Availability"].map(AVAILABILITY_BINARY)
    unmapped = df["Driver_Online"].isnull().sum()
    if unmapped > 0:
        flag(f"Driver_Online: {unmapped:,} values could not be mapped.")
    else:
        ok("Added: Driver_Online (Online=1, Offline=0)")

    # 11e — Order status flags
    note(
        "Boolean flag columns for order status are added to simplify "
        "downstream filtering.  Models predicting delivery delay should "
        "operate only on Is_Delivered=1 rows.  Cancelled and In Transit rows "
        "are preserved for separate analyses."
    )
    df["Is_Delivered"]  = (df["Order_Status"] == "Delivered").astype(int)
    df["Is_Cancelled"]  = (df["Order_Status"] == "Cancelled").astype(int)
    df["Is_InTransit"]  = (df["Order_Status"] == "In Transit").astype(int)
    ok("Added: Is_Delivered, Is_Cancelled, Is_InTransit")

    log.info(f"  Columns after derived additions: {df.shape[1]}")
    return df


# ---------------------------------------------------------------------------
# 12 · Post-processing audit
# ---------------------------------------------------------------------------

def final_audit(df_raw: pd.DataFrame, df_clean: pd.DataFrame) -> None:
    section("STEP 10 · FINAL AUDIT")

    log.info(f"  Raw dataset shape  : {df_raw.shape[0]:,} rows × {df_raw.shape[1]} columns")
    log.info(f"  Clean dataset shape: {df_clean.shape[0]:,} rows × {df_clean.shape[1]} columns")

    rows_removed = df_raw.shape[0] - df_clean.shape[0]
    cols_added   = df_clean.shape[1] - df_raw.shape[1]
    log.info(f"  Rows removed       : {rows_removed:,}")
    log.info(f"  Columns added      : {cols_added}")

    # Missing value check on cleaned dataset
    remaining_missing = df_clean.isnull().sum().sum()
    if remaining_missing > 0:
        flag(f"Cleaned dataset still has {remaining_missing:,} missing cells — review above flags.")
    else:
        ok("Cleaned dataset has zero missing values.")

    # Duplicate check on cleaned dataset
    remaining_dups = df_clean.duplicated().sum()
    if remaining_dups > 0:
        flag(f"Cleaned dataset still has {remaining_dups:,} duplicate rows.")
    else:
        ok("Cleaned dataset has zero duplicate rows.")

    # Duplicate Order_ID check
    remaining_pk = df_clean["Order_ID"].duplicated().sum()
    if remaining_pk > 0:
        flag(f"Cleaned dataset still has {remaining_pk:,} duplicate Order_IDs.")
    else:
        ok("Order_ID is unique in the cleaned dataset.")

    # Datetime type check
    for col in ["Order_Time", "Delivery_Time"]:
        ok(f"{col} dtype: {df_clean[col].dtype}")

    # Numerical range spot-checks
    spot_checks = {
        "Delivery_Duration_Minutes": (DURATION_MIN, DURATION_MAX),
        "Delivery_Distance_km"     : (0.001, 100),
        "Quantity"                 : (1, 5),
        "Total_Price"              : (0.01, None),
    }
    for col, (lo, hi) in spot_checks.items():
        bad = pd.Series(False, index=df_clean.index)
        if lo is not None:
            bad |= df_clean[col].fillna(-np.inf) < lo
        if hi is not None:
            bad |= df_clean[col].fillna(np.inf) > hi
        if bad.sum() > 0:
            flag(f"AUDIT FAILED: {col} still has {bad.sum():,} out-of-range values!")
        else:
            ok(f"AUDIT PASSED: {col} is within valid range.")

    # Chronological check
    chrono_bad = df_clean["Delivery_Time"] < df_clean["Order_Time"]
    if chrono_bad.sum() > 0:
        flag(f"AUDIT FAILED: {chrono_bad.sum():,} rows still have Delivery before Order.")
    else:
        ok("AUDIT PASSED: all Delivery_Time >= Order_Time.")

    # New columns present
    expected_new = [
        "Order_Hour", "Order_DayOfWeek", "Order_DayOfMonth", "Is_Weekend",
        "Is_RushHour", "Price_Per_Item", "Traffic_Level_Enc", "Driver_Online",
        "Is_Delivered", "Is_Cancelled", "Is_InTransit", "Same_Location_Flag",
        "Restaurant_Geo_Imputed", "Customer_Geo_Imputed", "Driver_Geo_Imputed",
    ]
    for col in expected_new:
        if col in df_clean.columns:
            ok(f"New column present: {col}")
        else:
            flag(f"Expected new column NOT found: {col}")


# ---------------------------------------------------------------------------
# 13 · Save cleaned dataset
# ---------------------------------------------------------------------------

def save_cleaned(df: pd.DataFrame, path: str) -> None:
    section("STEP 11 · SAVE CLEANED DATASET")

    # Serialise datetime columns back to ISO format strings for wide compatibility
    df_save = df.copy()
    df_save["Order_Time"]    = df_save["Order_Time"].dt.strftime("%Y-%m-%d %H:%M")
    df_save["Delivery_Time"] = df_save["Delivery_Time"].dt.strftime("%Y-%m-%d %H:%M")

    # Convert pandas nullable Int64 back to standard int for CSV compatibility
    for col in df_save.select_dtypes(include="Int64").columns:
        df_save[col] = df_save[col].astype(float).astype("Int64")

    df_save.to_csv(path, index=False, encoding="utf-8")
    size_kb = os.path.getsize(path) / 1024
    log.info(f"  Saved : {path}")
    log.info(f"  Shape : {df_save.shape[0]:,} rows × {df_save.shape[1]} columns")
    log.info(f"  Size  : {size_kb:,.1f} KB")
    note(
        f"The raw file '{RAW_PATH}' was NOT modified.  "
        f"The cleaned file '{path}' is a separate, independent copy."
    )


# ---------------------------------------------------------------------------
# 14 · Main
# ---------------------------------------------------------------------------

def main() -> None:
    log.info(SEPARATOR)
    log.info("  Food Delivery Analytics — Phase 1 Preprocessing Pipeline")
    log.info(f"  Run at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    log.info(SEPARATOR)

    # Load raw  (never written back)
    df_raw   = load_raw(RAW_PATH)
    df_clean = df_raw.copy()

    # Pipeline steps
    df_clean = check_duplicates(df_clean)
    df_clean = handle_missing_values(df_clean)
    df_clean = fix_dtypes(df_clean)
    df_clean = standardise_categoricals(df_clean)
    df_clean = validate_numerics(df_clean)
    df_clean = validate_datetimes(df_clean)
    df_clean = scan_placeholders(df_clean)

    # Repeat missing-value pass after placeholder → NaN conversion
    section("STEP 8b · SECOND MISSING-VALUE PASS (post-placeholder scan)")
    note(
        "Placeholder values converted to NaN in Step 8 are handled here "
        "using the same strategy as Step 3."
    )
    df_clean = handle_missing_values(df_clean)

    df_clean = add_derived_columns(df_clean)

    # Audit
    final_audit(df_raw, df_clean)

    # Save
    save_cleaned(df_clean, CLEANED_PATH)

    # Summary
    section("PIPELINE COMPLETE")
    log.info(f"  Raw dataset       : {RAW_PATH}  ({df_raw.shape[0]:,} rows, UNCHANGED)")
    log.info(f"  Cleaned dataset   : {CLEANED_PATH}  ({df_clean.shape[0]:,} rows)")
    log.info(f"  Preprocessing log : {LOG_PATH}")


if __name__ == "__main__":
    main()
