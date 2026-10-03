"""
preprocess.py
=============
Food Delivery Analytics — Phase 1 Preprocessing Pipeline
Project : Food Delivery Analytics: Delivery Performance and Delay Prediction

Input  : data/raw/Order_delivery.csv
Output : data/processed/Order_delivery_cleaned.csv
Log    : logs/preprocessing_report.txt

Usage
-----
    # From project root:
    python src/preprocessing/preprocess.py

    # Or activate the project venv first:
    .venv\\Scripts\\activate          # Windows
    source .venv/bin/activate       # macOS/Linux
    python src/preprocessing/preprocess.py
"""

import os
import sys
import logging
from datetime import datetime

import numpy as np
import pandas as pd

# ---------------------------------------------------------------------------
# Paths  (resolved relative to project root, regardless of cwd)
# ---------------------------------------------------------------------------
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))

RAW_PATH     = os.path.join(PROJECT_ROOT, "data", "raw",       "Order_delivery.csv")
CLEANED_PATH = os.path.join(PROJECT_ROOT, "data", "processed", "Order_delivery_cleaned.csv")
LOG_PATH     = os.path.join(PROJECT_ROOT, "logs", "preprocessing_report.txt")

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
DT_FORMAT   = "%d-%m-%Y %H:%M"   # format in raw CSV
GEO_BOUNDS  = {"lat": (20.0, 33.0), "lon": (24.0, 38.0)}
DURATION_MIN, DURATION_MAX = 5, 240
TRAFFIC_ORDER      = {"Low": 0, "Medium": 1, "High": 2}
AVAILABILITY_BINARY = {"Online": 1, "Offline": 0}

EXPECTED_CATS = {
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

CANONICAL_MAPS = {
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

PLACEHOLDER_STRINGS = {
    "unknown", "n/a", "-", "none", "null", "", "0",
    "?", "na", "not available", "n.a.", "nan",
}

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------
os.makedirs(os.path.dirname(LOG_PATH), exist_ok=True)

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

SEP = "=" * 72
def section(t): log.info(f"\n{SEP}\n  {t}\n{SEP}")
def ok(m):      log.info(f"[OK]       {m}")
def note(m):    log.info(f"[DECISION] {m}")
def flag(m):    log.info(f"[FLAG]     {m}")

def _pct(mask, label):
    n = mask.sum()
    log.info(f"           {label}: {n:,}  ({n/len(mask)*100:.2f}%)")

# ---------------------------------------------------------------------------
# Step 1 — Load
# ---------------------------------------------------------------------------
def load_raw(path):
    section("STEP 1 - LOAD RAW DATASET")
    log.info(f"  Source : {path}")
    df = pd.read_csv(path)
    log.info(f"  Shape  : {df.shape[0]:,} rows x {df.shape[1]} columns")
    note("Raw file is loaded read-only into memory. It will NOT be modified.")
    return df

# ---------------------------------------------------------------------------
# Step 2 — Duplicates
# ---------------------------------------------------------------------------
def check_duplicates(df):
    section("STEP 2 - DUPLICATE CHECKS")
    full = df.duplicated()
    _pct(full, "Full-row duplicates")
    if full.sum():
        df = df[~full].reset_index(drop=True)
        flag(f"Dropped {full.sum():,} full-row duplicates.")
    else:
        ok("No full-row duplicates.")

    pk = df.duplicated(subset=["Order_ID"])
    _pct(pk, "Duplicate Order_ID")
    if pk.sum():
        before = len(df)
        df = df.drop_duplicates(subset=["Order_ID"], keep="first").reset_index(drop=True)
        flag(f"Dropped {before - len(df):,} duplicate Order_ID rows (kept first).")
    else:
        ok("Order_ID is unique.")
    return df

# ---------------------------------------------------------------------------
# Step 3 — Missing values
# ---------------------------------------------------------------------------
def handle_missing_values(df):
    section("STEP 3 - MISSING VALUE TREATMENT")
    total = df.isnull().sum().sum()
    if total == 0:
        ok("No missing values. No action needed.")
        note("Strategy documented: identifiers/datetimes/targets -> DROP; "
             "numerics -> DROP if <0.1%, median if 0.1-1%; "
             "categoricals -> mode if <0.5%; geo -> city-median imputation.")
        return df

    # Identifiers / datetimes / targets -> drop rows
    for grp, cols in [
        ("identifier", ["Order_ID", "User_ID", "Restaurant_ID", "Driver_ID"]),
        ("datetime",   ["Order_Time", "Delivery_Time"]),
        ("target",     ["Order_Status", "Delivery_Duration_Minutes"]),
    ]:
        mask = df[cols].isnull().any(axis=1)
        if mask.sum():
            flag(f"Dropping {mask.sum():,} rows with missing {grp} column(s).")
            df = df[~mask].reset_index(drop=True)

    # Numerics
    for col in ["Quantity", "Total_Price", "Delivery_Distance_km"]:
        m = df[col].isnull()
        if not m.any():
            continue
        pct = m.sum() / len(df) * 100
        if pct <= 0.1:
            df = df[~m].reset_index(drop=True)
            flag(f"Dropped {m.sum():,} rows with missing {col} (<=0.1%).")
        elif pct <= 1.0:
            med = df[col].median()
            df.loc[m, col] = med
            flag(f"Imputed {m.sum():,} missing {col} with median={med:.4f}.")
        else:
            flag(f"WARNING: {col} has {pct:.2f}% missing — MANUAL REVIEW REQUIRED.")

    # Geo columns -> city-median imputation + flag
    for lat, lon in [("Restaurant_Lat","Restaurant_Lon"),
                     ("Customer_Lat","Customer_Lon"),
                     ("Driver_Lat","Driver_Lon")]:
        prefix = lat.replace("_Lat","")
        flag_col = f"{prefix}_Geo_Imputed"
        imp_mask = df[[lat, lon]].isnull().any(axis=1)
        df[flag_col] = 0
        if imp_mask.sum():
            city_med = df.groupby("City")[[lat, lon]].transform("median")
            df.loc[imp_mask, lat] = city_med.loc[imp_mask, lat]
            df.loc[imp_mask, lon] = city_med.loc[imp_mask, lon]
            df.loc[imp_mask, flag_col] = 1
            flag(f"Imputed {imp_mask.sum():,} missing {lat}/{lon} with city median.")
        else:
            ok(f"No missing values in {lat}/{lon}.")

    # Categoricals -> mode
    for col in ["Item_Name","City","Payment_Method","Driver_Vehicle",
                "Traffic_Level","Driver_Availability"]:
        m = df[col].isnull()
        if not m.any():
            ok(f"No missing values in {col}.")
            continue
        pct = m.sum() / len(df) * 100
        if pct <= 0.5:
            mode_val = df[col].mode()[0]
            df.loc[m, col] = mode_val
            flag(f"Imputed {m.sum():,} missing {col} with mode='{mode_val}'.")
        else:
            before = len(df)
            df = df[~m].reset_index(drop=True)
            flag(f"Dropped {before-len(df):,} rows with missing {col} (>0.5%).")

    log.info(f"  Rows after missing-value treatment: {len(df):,}")
    return df

# ---------------------------------------------------------------------------
# Step 4 — Data types
# ---------------------------------------------------------------------------
def fix_dtypes(df):
    section("STEP 4 - DATA TYPE CORRECTIONS")

    # Datetimes
    for col in ["Order_Time", "Delivery_Time"]:
        before = df[col].isnull().sum()
        df[col] = pd.to_datetime(df[col], format=DT_FORMAT, errors="coerce")
        new_nat = df[col].isnull().sum() - before
        if new_nat:
            flag(f"{col}: {new_nat:,} values became NaT after parsing.")
        else:
            ok(f"{col} parsed -> datetime64")

    # Integer columns
    for col in ["Order_ID","Restaurant_ID","Driver_ID","Quantity",
                "Delivery_Duration_Minutes"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")
        bad = df[col].isnull()
        if bad.sum():
            flag(f"{col}: {bad.sum():,} coercion failures -> dropping rows.")
            df = df[~bad].reset_index(drop=True)
        df[col] = df[col].astype("Int64")
        ok(f"{col} -> Int64")

    # Float columns
    for col in ["Total_Price","Restaurant_Lat","Restaurant_Lon",
                "Customer_Lat","Customer_Lon","Driver_Lat","Driver_Lon",
                "Delivery_Distance_km"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")
        bad = df[col].isnull()
        if bad.sum():
            flag(f"{col}: {bad.sum():,} coercion failures -> dropping rows.")
            df = df[~bad].reset_index(drop=True)
        ok(f"{col} -> float64")

    # Strings
    for col in ["User_ID","Item_Name","City","Payment_Method","Order_Status",
                "Driver_Vehicle","Traffic_Level","Driver_Availability"]:
        df[col] = df[col].astype(str)
        ok(f"{col} -> str")

    log.info(f"  Rows after dtype coercion: {len(df):,}")
    return df

# ---------------------------------------------------------------------------
# Step 5 — Categorical standardisation
# ---------------------------------------------------------------------------
def standardise_categoricals(df):
    section("STEP 5 - CATEGORICAL STANDARDISATION")

    cat_cols = ["User_ID","Item_Name","City","Payment_Method","Order_Status",
                "Driver_Vehicle","Traffic_Level","Driver_Availability"]

    # Whitespace
    for col in cat_cols:
        before = df[col].nunique()
        df[col] = df[col].str.strip()
        after = df[col].nunique()
        if before != after:
            flag(f"{col}: whitespace stripping changed unique count {before} -> {after}.")
        else:
            ok(f"{col}: no whitespace issues.")

    # Canonical capitalisation (only fix non-canonical rows)
    for col, cmap in CANONICAL_MAPS.items():
        canonical_values = set(cmap.values())
        non_canonical = ~df[col].isin(canonical_values)
        lower = df[col].str.lower()
        fixable = non_canonical & lower.isin(cmap.keys())
        if fixable.sum():
            df.loc[fixable, col] = lower[fixable].map(cmap)
            flag(f"{col}: corrected {fixable.sum():,} capitalisation(s).")
        else:
            ok(f"{col}: all values already canonical.")

    # Validate expected sets
    for col, valid in EXPECTED_CATS.items():
        unexpected = df[~df[col].isin(valid)][col].unique()
        if len(unexpected):
            flag(f"{col}: {len(unexpected)} unexpected value(s): {list(unexpected)[:5]}. REVIEW REQUIRED.")
        else:
            ok(f"{col}: all values in expected set.")

    # User_ID format
    uid_ok = df["User_ID"].str.match(r"^U\d{4}$", na=False)
    if (~uid_ok).sum():
        flag(f"User_ID: {(~uid_ok).sum():,} values do not match U#### pattern.")
    else:
        ok("User_ID: all match U#### format.")

    return df

# ---------------------------------------------------------------------------
# Step 6 — Numerical validity
# ---------------------------------------------------------------------------
def validate_numerics(df):
    section("STEP 6 - NUMERICAL VALIDITY CHECKS")

    checks = {
        "Quantity"                 : (1,   5),
        "Total_Price"              : (0.01, None),
        "Delivery_Duration_Minutes": (DURATION_MIN, DURATION_MAX),
        "Delivery_Distance_km"     : (0.001, 100),
        "Restaurant_Lat"           : GEO_BOUNDS["lat"],
        "Restaurant_Lon"           : GEO_BOUNDS["lon"],
        "Customer_Lat"             : GEO_BOUNDS["lat"],
        "Customer_Lon"             : GEO_BOUNDS["lon"],
        "Driver_Lat"               : GEO_BOUNDS["lat"],
        "Driver_Lon"               : GEO_BOUNDS["lon"],
    }

    drop_mask = pd.Series(False, index=df.index)
    for col, (lo, hi) in checks.items():
        bad = pd.Series(False, index=df.index)
        if lo is not None: bad |= df[col].fillna(-np.inf) < lo
        if hi is not None: bad |= df[col].fillna(np.inf)  > hi
        if bad.sum():
            flag(f"{col}: {bad.sum():,} rows outside [{lo}, {hi}]. DROPPING.")
            drop_mask |= bad
        else:
            ok(f"{col}: all values in [{lo}, {hi}].")

    if drop_mask.sum():
        df = df[~drop_mask].reset_index(drop=True)
    log.info(f"  Rows after numerical validation: {len(df):,}")
    return df

# ---------------------------------------------------------------------------
# Step 7 — Datetime validation
# ---------------------------------------------------------------------------
def validate_datetimes(df):
    section("STEP 7 - DATETIME VALIDATION")

    nat = df["Order_Time"].isnull() | df["Delivery_Time"].isnull()
    if nat.sum():
        flag(f"Dropping {nat.sum():,} rows with NaT timestamps.")
        df = df[~nat].reset_index(drop=True)
    else:
        ok("No NaT timestamps.")

    chrono = df["Delivery_Time"] < df["Order_Time"]
    if chrono.sum():
        flag(f"Dropping {chrono.sum():,} rows where Delivery_Time < Order_Time.")
        df = df[~chrono].reset_index(drop=True)
    else:
        ok("All Delivery_Time >= Order_Time.")

    computed = (df["Delivery_Time"] - df["Order_Time"]).dt.total_seconds() / 60
    mismatch = (computed - df["Delivery_Duration_Minutes"].astype(float)).abs() > 1.0
    if mismatch.sum():
        flag(f"{mismatch.sum():,} duration mismatches -- overwriting with computed value.")
        df.loc[mismatch, "Delivery_Duration_Minutes"] = computed[mismatch].round().astype(int)
    else:
        ok("Duration perfectly consistent with computed difference.")

    log.info(f"  Rows after datetime validation: {len(df):,}")
    return df

# ---------------------------------------------------------------------------
# Step 8 — Placeholder scan
# ---------------------------------------------------------------------------
def scan_placeholders(df):
    section("STEP 8 - PLACEHOLDER AND SUSPICIOUS VALUE SCAN")

    cat_cols = ["User_ID","Item_Name","City","Payment_Method","Order_Status",
                "Driver_Vehicle","Traffic_Level","Driver_Availability"]
    total = 0
    for col in cat_cols:
        hits = df[col].str.strip().str.lower().isin(PLACEHOLDER_STRINGS)
        if hits.sum():
            df.loc[hits, col] = np.nan
            total += hits.sum()
            flag(f"{col}: {hits.sum():,} placeholder(s) -> NaN.")
    if total == 0:
        ok("No placeholder strings found.")

    for col, reason in [("Quantity","zero qty is invalid"), ("Total_Price","zero price is invalid")]:
        z = df[col] == 0
        if z.sum():
            df.loc[z, col] = np.nan
            flag(f"{col}: {z.sum():,} zeros -> NaN. ({reason})")
        else:
            ok(f"{col}: no zero values.")

    # Same-location flag
    same = (df["Restaurant_Lat"].round(6) == df["Customer_Lat"].round(6)) & \
           (df["Restaurant_Lon"].round(6) == df["Customer_Lon"].round(6))
    df["Same_Location_Flag"] = same.astype(int)
    if same.sum():
        flag(f"Same_Location_Flag: {same.sum():,} rows flagged (co-located coords).")
    else:
        ok("No co-located restaurant/customer coordinates.")

    return df

# ---------------------------------------------------------------------------
# Step 9 — Derived columns
# ---------------------------------------------------------------------------
def add_derived_columns(df):
    section("STEP 9 - DERIVED COLUMNS")

    df["Order_Hour"]       = df["Order_Time"].dt.hour
    df["Order_DayOfWeek"]  = df["Order_Time"].dt.dayofweek
    df["Order_DayOfMonth"] = df["Order_Time"].dt.day
    df["Is_Weekend"]       = df["Order_DayOfWeek"].isin([5,6]).astype(int)

    rush = set(range(7,10)) | set(range(18,22))
    df["Is_RushHour"]      = df["Order_Hour"].isin(rush).astype(int)
    df["Price_Per_Item"]   = (df["Total_Price"] / df["Quantity"]).round(4)
    df["Traffic_Level_Enc"]= df["Traffic_Level"].map(TRAFFIC_ORDER)
    df["Driver_Online"]    = df["Driver_Availability"].map(AVAILABILITY_BINARY)
    df["Is_Delivered"]     = (df["Order_Status"] == "Delivered").astype(int)
    df["Is_Cancelled"]     = (df["Order_Status"] == "Cancelled").astype(int)
    df["Is_InTransit"]     = (df["Order_Status"] == "In Transit").astype(int)

    # Geo imputation flags (if not already added in missing-value step)
    for prefix in ["Restaurant","Customer","Driver"]:
        col = f"{prefix}_Geo_Imputed"
        if col not in df.columns:
            df[col] = 0

    ok(f"Added 11 derived columns. Total columns: {df.shape[1]}")
    return df

# ---------------------------------------------------------------------------
# Step 10 — Final audit
# ---------------------------------------------------------------------------
def final_audit(raw, clean):
    section("STEP 10 - FINAL AUDIT")
    log.info(f"  Raw   : {raw.shape[0]:,} x {raw.shape[1]}")
    log.info(f"  Clean : {clean.shape[0]:,} x {clean.shape[1]}")
    log.info(f"  Rows removed : {raw.shape[0]-clean.shape[0]:,}")
    log.info(f"  Cols added   : {clean.shape[1]-raw.shape[1]:,}")

    null_total = clean.isnull().sum().sum()
    if null_total: flag(f"Still {null_total:,} null cells -- review above.")
    else: ok("Zero missing values in cleaned dataset.")

    if clean.duplicated().sum(): flag("Still has duplicate rows!")
    else: ok("Zero duplicate rows.")

    if clean["Order_ID"].duplicated().sum(): flag("Still has duplicate Order_IDs!")
    else: ok("Order_ID is unique.")

    chrono = (clean["Delivery_Time"] < clean["Order_Time"]).sum()
    if chrono: flag(f"{chrono:,} rows still have Delivery < Order time!")
    else: ok("All timestamps are chronologically consistent.")

# ---------------------------------------------------------------------------
# Step 11 — Save
# ---------------------------------------------------------------------------
def save_cleaned(df, path):
    section("STEP 11 - SAVE CLEANED DATASET")
    os.makedirs(os.path.dirname(path), exist_ok=True)

    df_save = df.copy()
    df_save["Order_Time"]    = df_save["Order_Time"].dt.strftime("%Y-%m-%d %H:%M")
    df_save["Delivery_Time"] = df_save["Delivery_Time"].dt.strftime("%Y-%m-%d %H:%M")
    for col in df_save.select_dtypes(include="Int64").columns:
        df_save[col] = df_save[col].astype(float).astype("Int64")

    df_save.to_csv(path, index=False, encoding="utf-8")
    size = os.path.getsize(path) / 1024
    ok(f"Saved: {path}  ({df_save.shape[0]:,} rows x {df_save.shape[1]} cols, {size:,.0f} KB)")
    note(f"Raw file '{RAW_PATH}' was NOT modified.")

# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    log.info(SEP)
    log.info("  Food Delivery Analytics -- Phase 1 Preprocessing Pipeline")
    log.info(f"  Run at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    log.info(SEP)

    raw  = load_raw(RAW_PATH)
    df   = raw.copy()

    df = check_duplicates(df)
    df = handle_missing_values(df)
    df = fix_dtypes(df)
    df = standardise_categoricals(df)
    df = validate_numerics(df)
    df = validate_datetimes(df)
    df = scan_placeholders(df)
    df = handle_missing_values(df)   # second pass after placeholder -> NaN
    df = add_derived_columns(df)

    final_audit(raw, df)
    save_cleaned(df, CLEANED_PATH)

    section("COMPLETE")
    log.info(f"  Cleaned dataset : {CLEANED_PATH}")
    log.info(f"  Log             : {LOG_PATH}")


if __name__ == "__main__":
    main()
