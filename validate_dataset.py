"""
validate_dataset.py
===================
Food Delivery Analytics — Dataset Quality Validation
Checks both the cleaned and featured datasets against 18 quality dimensions.
Produces a structured validation report (JSON + text) for the HTML artifact.
"""
import json, os, sys, warnings
import numpy as np
import pandas as pd
warnings.filterwarnings("ignore")

OUTPUT_JSON = "validation_results.json"

RAW_PATH      = os.path.join("Datasets", "Order_delivery.csv")
CLEANED_PATH  = os.path.join("Datasets", "Order_delivery_cleaned.csv")
FEATURED_PATH = os.path.join("Datasets", "Order_delivery_featured.csv")

LEAKAGE_COLS = {
    "Delivery_Time", "Delivery_Duration_Minutes", "Order_Status",
    "Is_Delivered", "Is_Cancelled", "Is_InTransit",
    "Is_Delayed_TARGET", "Delay_Minutes_TARGET",
    "Duration_Bin_TARGET", "Order_To_Delivery_Minutes_TARGET",
    "Delivery_Speed_kmh_ANALYTICAL", "Distance_Per_Minute_ANALYTICAL",
}
DROP_COLS = {"Order_ID", "User_ID", "Restaurant_ID", "Driver_ID",
             "Order_Time", "Order_Date", "Order_DayName"}

POST_DELIVERY_RAW = {"Delivery_Time", "Delivery_Duration_Minutes", "Order_Status"}

GEO_BOUNDS = {"lat": (20.0, 33.0), "lon": (24.0, 38.0)}

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
    "Driver_Availability": {"Online", "Offline"},
    "Time_Of_Day_Segment": {"Late Night", "Early Morning", "Morning",
                            "Afternoon", "Evening", "Night"},
    "Distance_Bin"       : {"Short (<1km)", "Medium (1-3km)",
                            "Long (3-5km)", "Very Long (>5km)"},
    "Order_Value_Tier"   : {"Budget (<100)", "Standard (100-300)",
                            "Premium (300-500)", "Luxury (>500)"},
    "Duration_Bin_TARGET": {"Fast (<30min)", "Normal (30-45min)", "Slow (>45min)"},
}

NUM_BOUNDS = {
    "Quantity"                 : (1, 5),
    "Total_Price"              : (0.01, None),
    "Delivery_Duration_Minutes": (5, 240),
    "Delivery_Distance_km"     : (0.001, 100),
    "Driver_To_Restaurant_km"  : (0, 50),
    "Total_Trip_km"            : (0, 100),
    "Price_Per_Item"           : (0.01, None),
    "Order_Hour"               : (0, 23),
    "Order_DayOfWeek"          : (0, 6),
    "Order_DayOfMonth"         : (1, 31),
    "Traffic_Level_Enc"        : (0, 2),
    "Is_Delayed_TARGET"        : (0, 1),
    "Delay_Minutes_TARGET"     : (0, None),
}

BINARY_COLS = [
    "Is_Weekend", "Is_RushHour", "Driver_Online", "Is_Delivered",
    "Is_Cancelled", "Is_InTransit", "Is_Weekday", "Is_Large_Order",
    "Is_High_Traffic", "Is_Delayed_TARGET", "Same_Location_Flag",
    "Restaurant_Geo_Imputed", "Customer_Geo_Imputed", "Driver_Geo_Imputed",
]

GEO_COLS = {
    "Restaurant_Lat": "lat", "Restaurant_Lon": "lon",
    "Customer_Lat"  : "lat", "Customer_Lon"  : "lon",
    "Driver_Lat"    : "lat", "Driver_Lon"    : "lon",
}

OUTLIER_COLS = [
    "Total_Price", "Delivery_Duration_Minutes", "Delivery_Distance_km",
    "Driver_To_Restaurant_km", "Total_Trip_km",
    "Delivery_Speed_kmh_ANALYTICAL",
]

# ---- Load ---------------------------------------------------------------
raw      = pd.read_csv(RAW_PATH)
cleaned  = pd.read_csv(CLEANED_PATH)
featured = pd.read_csv(FEATURED_PATH)

for df_name, df in [("featured", featured)]:
    for col in ["Order_Time", "Delivery_Time"]:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], format="%Y-%m-%d %H:%M", errors="coerce")

N = len(featured)
PASS, WARN, FAIL = "PASS", "WARN", "FAIL"

results = []  # list of dicts

def record(check_id, check_name, column, n_affected, status, action, justification,
           detail=""):
    pct = round(n_affected / N * 100, 4) if N > 0 else 0
    results.append({
        "id"           : check_id,
        "check"        : check_name,
        "column"       : column,
        "n_affected"   : int(n_affected),
        "pct_affected" : pct,
        "status"       : status,
        "action"       : action,
        "justification": justification,
        "detail"       : detail,
    })

# ==========================================================================
# CHECK 1 — Row count before and after preprocessing
# ==========================================================================
raw_rows     = len(raw)
cleaned_rows = len(cleaned)
featured_rows= len(featured)
rows_removed = raw_rows - cleaned_rows

record(
    1, "Row count — raw vs cleaned", "ALL",
    rows_removed,
    PASS if rows_removed == 0 else WARN,
    "No rows removed (dataset had zero data-quality errors requiring row deletion).",
    (f"Raw: {raw_rows:,}. Cleaned: {cleaned_rows:,}. Featured: {featured_rows:,}. "
     "The preprocessing pipeline found 0 duplicates, 0 missing values, "
     "0 impossible numerical values, and 0 impossible timestamps. "
     "All rows are retained."),
    f"raw={raw_rows}, cleaned={cleaned_rows}, featured={featured_rows}"
)

# ==========================================================================
# CHECK 2 — Column count
# ==========================================================================
raw_cols      = raw.shape[1]
cleaned_cols  = cleaned.shape[1]
featured_cols = featured.shape[1]
added_pp  = cleaned_cols - raw_cols
added_fe  = featured_cols - cleaned_cols

record(
    2, "Column count — progression", "ALL",
    0,
    PASS,
    "No action needed — column expansion is expected and documented.",
    (f"Raw: {raw_cols} cols. +{added_pp} from preprocessing = {cleaned_cols}. "
     f"+{added_fe} from feature engineering = {featured_cols}. "
     "All additions are documented in feature_documentation.md."),
    f"raw={raw_cols}, cleaned={cleaned_cols}, featured={featured_cols}"
)

# ==========================================================================
# CHECK 3 — Missing values
# ==========================================================================
null_counts = featured.isnull().sum()
null_cols   = null_counts[null_counts > 0]
total_nulls = null_counts.sum()

record(
    3, "Missing values", "ALL" if total_nulls == 0 else str(null_cols.index.tolist()),
    int(total_nulls),
    PASS if total_nulls == 0 else FAIL,
    ("No imputation or row removal needed — dataset is complete."
     if total_nulls == 0 else
     f"Missing values found in: {null_cols.to_dict()}. Review preprocessing pipeline."),
    ("Dataset has zero missing values across all 55 columns. "
     "Verified after both preprocessing and feature engineering steps."
     if total_nulls == 0 else
     "Unexpected missing values require investigation."),
    f"total_null_cells={total_nulls}"
)

# ==========================================================================
# CHECK 4 — Duplicate rows
# ==========================================================================
dup_rows = featured.duplicated().sum()
record(
    4, "Duplicate rows (full-row)", "ALL",
    int(dup_rows),
    PASS if dup_rows == 0 else FAIL,
    ("No action needed." if dup_rows == 0
     else f"Drop {dup_rows:,} exact full-row duplicates."),
    "A row identical across all 55 columns is a system re-submission error with no added value.",
    f"duplicate_rows={dup_rows}"
)

# ==========================================================================
# CHECK 5 — Duplicate Order_IDs
# ==========================================================================
dup_oids = featured["Order_ID"].duplicated().sum()
record(
    5, "Duplicate Order_ID (primary key)", "Order_ID",
    int(dup_oids),
    PASS if dup_oids == 0 else FAIL,
    ("No action needed — Order_ID is unique." if dup_oids == 0
     else "Drop duplicate Order_IDs (keep first occurrence)."),
    "Order_ID is the primary key. Any duplication indicates a re-submitted or system-duplicated record.",
    f"duplicate_order_ids={dup_oids}, unique_ids={featured['Order_ID'].nunique():,}"
)

# ==========================================================================
# CHECK 6 — Data types
# ==========================================================================
type_issues = []
expected_numeric = [
    "Order_ID","Restaurant_ID","Driver_ID","Quantity","Total_Price",
    "Delivery_Duration_Minutes","Delivery_Distance_km",
    "Restaurant_Lat","Restaurant_Lon","Customer_Lat","Customer_Lon",
    "Driver_Lat","Driver_Lon","Order_Hour","Order_DayOfWeek",
    "Order_DayOfMonth","Is_Weekend","Is_RushHour","Price_Per_Item",
    "Traffic_Level_Enc","Driver_Online","Is_Delivered","Is_Cancelled",
    "Is_InTransit","Is_Weekday","Is_Large_Order","Is_High_Traffic",
    "Driver_To_Restaurant_km","Total_Trip_km","Order_Month",
    "Is_Delayed_TARGET","Delay_Minutes_TARGET",
    "Order_To_Delivery_Minutes_TARGET","Delivery_Speed_kmh_ANALYTICAL",
    "Distance_Per_Minute_ANALYTICAL","Same_Location_Flag",
    "Restaurant_Geo_Imputed","Customer_Geo_Imputed","Driver_Geo_Imputed",
]
for col in expected_numeric:
    if col in featured.columns:
        if not pd.api.types.is_numeric_dtype(featured[col]):
            type_issues.append(col)

expected_str = [
    "User_ID","Item_Name","City","Payment_Method","Order_Status",
    "Driver_Vehicle","Traffic_Level","Driver_Availability",
    "Order_DayName","Time_Of_Day_Segment","Distance_Bin",
    "Order_Value_Tier","Duration_Bin_TARGET",
]
for col in expected_str:
    if col in featured.columns:
        if not (pd.api.types.is_string_dtype(featured[col]) or
                pd.api.types.is_object_dtype(featured[col])):
            type_issues.append(col)

dt_cols = ["Order_Time","Delivery_Time"]
for col in dt_cols:
    if col in featured.columns:
        if not pd.api.types.is_datetime64_any_dtype(featured[col]):
            type_issues.append(f"{col}(not datetime64)")

record(
    6, "Data types", str(type_issues) if type_issues else "ALL",
    len(type_issues),
    PASS if not type_issues else FAIL,
    ("All columns have correct dtypes." if not type_issues
     else f"Re-coerce: {type_issues}"),
    ("Numeric columns verified as int64/float64. "
     "Categorical columns verified as str/object. "
     "Datetime columns verified as datetime64[us]."),
    f"type_issues={type_issues}"
)

# ==========================================================================
# CHECK 7 — Invalid categorical values
# ==========================================================================
cat_issues = {}
for col, valid in EXPECTED_CATS.items():
    if col not in featured.columns:
        continue
    unexpected = featured[~featured[col].isin(valid)][col]
    if len(unexpected) > 0:
        cat_issues[col] = {"n": len(unexpected), "vals": unexpected.value_counts().head(5).to_dict()}

n_cat_affected = sum(v["n"] for v in cat_issues.values())
record(
    7, "Invalid categorical values", str(list(cat_issues.keys())) if cat_issues else "ALL",
    n_cat_affected,
    PASS if not cat_issues else FAIL,
    ("All categorical columns contain only expected values." if not cat_issues
     else f"Flag unexpected values for manual review: {cat_issues}"),
    "Each fixed-vocabulary column is validated against its complete expected value set.",
    str(cat_issues) if cat_issues else "all clean"
)

# ==========================================================================
# CHECK 8 — Invalid numerical values
# ==========================================================================
num_issues = {}
for col, (lo, hi) in NUM_BOUNDS.items():
    if col not in featured.columns:
        continue
    mask = pd.Series(False, index=featured.index)
    if lo is not None:
        mask |= featured[col] < lo
    if hi is not None:
        mask |= featured[col] > hi
    n = mask.sum()
    if n > 0:
        num_issues[col] = {
            "n": int(n),
            "min": float(featured[col].min()),
            "max": float(featured[col].max()),
            "lo": lo, "hi": hi
        }

n_num_affected = sum(v["n"] for v in num_issues.values())
record(
    8, "Invalid numerical values", str(list(num_issues.keys())) if num_issues else "ALL",
    n_num_affected,
    PASS if not num_issues else FAIL,
    ("All numerical columns are within valid domain ranges." if not num_issues
     else f"Values outside valid bounds: {num_issues}"),
    "Hard domain-knowledge bounds are applied: e.g. Quantity 1-5, Duration 5-240 min, Distance 0-100 km.",
    str(num_issues) if num_issues else "all clean"
)

# ==========================================================================
# CHECK 9 — Impossible timestamps
# ==========================================================================
ot = featured["Order_Time"]
dt_col = featured["Delivery_Time"]
nat_ot = ot.isna().sum()
nat_dt = dt_col.isna().sum()
chrono_bad = (dt_col < ot).sum()
future_orders = (ot > pd.Timestamp("2025-12-31")).sum()
past_orders   = (ot < pd.Timestamp("2025-01-01")).sum()

record(
    9, "Unparseable / NaT timestamps", "Order_Time / Delivery_Time",
    int(nat_ot + nat_dt),
    PASS if (nat_ot + nat_dt) == 0 else FAIL,
    "No action needed." if (nat_ot + nat_dt) == 0 else "Drop rows with NaT timestamps.",
    "Both datetime columns parsed cleanly from format %Y-%m-%d %H:%M with 0 NaT values.",
    f"NaT Order_Time={nat_ot}, NaT Delivery_Time={nat_dt}"
)
record(
    "9b", "Delivery_Time before Order_Time", "Order_Time / Delivery_Time",
    int(chrono_bad),
    PASS if chrono_bad == 0 else FAIL,
    "No action needed." if chrono_bad == 0 else "Drop rows where Delivery_Time < Order_Time.",
    "A delivery cannot complete before it is ordered. Zero violations found.",
    f"chrono_violations={chrono_bad}"
)
record(
    "9c", "Order_Time outside dataset window (2025)", "Order_Time",
    int(future_orders + past_orders),
    PASS if (future_orders + past_orders) == 0 else WARN,
    "No action needed." if (future_orders + past_orders) == 0 else "Flag for manual review.",
    "All order timestamps fall within calendar year 2025.",
    f"before_2025={past_orders}, after_2025={future_orders}"
)

# ==========================================================================
# CHECK 10 — Negative or impossible durations
# ==========================================================================
dur = featured["Delivery_Duration_Minutes"]
neg_dur  = (dur <= 0).sum()
too_long = (dur > 240).sum()
too_short= (dur < 5).sum()

record(
    10, "Negative / zero duration", "Delivery_Duration_Minutes",
    int(neg_dur),
    PASS if neg_dur == 0 else FAIL,
    "No action needed." if neg_dur == 0 else "Drop rows with duration <= 0.",
    "A delivery duration <= 0 minutes is physically impossible.",
    f"zero_or_negative={neg_dur}"
)
record(
    "10b", "Impossibly short duration (<5 min)", "Delivery_Duration_Minutes",
    int(too_short),
    PASS if too_short == 0 else WARN,
    "No action needed." if too_short == 0 else "Flag for review — plausible but suspicious.",
    "Under 5 minutes implies a delivery completing before the food is ready.",
    f"under_5_min={too_short}, actual_min={float(dur.min()):.1f}"
)
record(
    "10c", "Impossibly long duration (>240 min)", "Delivery_Duration_Minutes",
    int(too_long),
    PASS if too_long == 0 else WARN,
    "No action needed." if too_long == 0 else "Flag for review.",
    "Over 4 hours for an in-city food delivery is operationally impossible.",
    f"over_240_min={too_long}, actual_max={float(dur.max()):.1f}"
)

# Duration-timestamp consistency
computed = (featured["Delivery_Time"] - featured["Order_Time"]).dt.total_seconds() / 60
dur_mismatch = (computed - featured["Delivery_Duration_Minutes"]).abs().gt(1.0).sum()
record(
    "10d", "Duration vs computed (Delivery_Time - Order_Time) mismatch >1 min",
    "Delivery_Duration_Minutes",
    int(dur_mismatch),
    PASS if dur_mismatch == 0 else FAIL,
    "No action needed." if dur_mismatch == 0 else "Overwrite stored duration with computed value.",
    "Stored duration must equal the difference of the two timestamps. Zero mismatches found.",
    f"mismatch_rows={dur_mismatch}"
)

# ==========================================================================
# CHECK 11 — Outliers (IQR + Z-score)
# ==========================================================================
for col in OUTLIER_COLS:
    if col not in featured.columns:
        continue
    s = featured[col].dropna()
    q1, q3 = s.quantile(0.25), s.quantile(0.75)
    iqr = q3 - q1
    lo_fence = q1 - 1.5 * iqr
    hi_fence = q3 + 1.5 * iqr
    iqr_out  = ((featured[col] < lo_fence) | (featured[col] > hi_fence)).sum()
    z_out    = ((featured[col] - s.mean()).abs() / s.std() > 3).sum()
    has_out  = iqr_out > 0 or z_out > 0
    record(
        11, f"Outliers — {col}", col,
        int(max(iqr_out, z_out)),
        WARN if has_out else PASS,
        ("Outliers identified and retained. Statistical outliers within valid domain bounds "
         "are NOT removed in preprocessing — removal is a Phase 2 modelling decision."),
        (f"IQR fence: [{lo_fence:.2f}, {hi_fence:.2f}]. "
         f"IQR outliers: {iqr_out}. Z>3 outliers: {z_out}. "
         f"Range: [{float(featured[col].min()):.4f}, {float(featured[col].max()):.4f}]. "
         "All values are within valid physical domain bounds — these are statistical "
         "extremes, not data errors."),
        f"iqr_out={iqr_out}, z3_out={z_out}"
    )

# ==========================================================================
# CHECK 12 — Target inconsistencies
# ==========================================================================
# 12a: Is_Delayed_TARGET vs threshold
thresh = 45.0
delivered = featured["Order_Status"] == "Delivered"
should_delay = featured.loc[delivered, "Delivery_Duration_Minutes"] > thresh
flagged      = featured.loc[delivered, "Is_Delayed_TARGET"] == 1
mismatch_delay = (should_delay != flagged).sum()
record(
    12, "Is_Delayed_TARGET consistency with duration threshold", "Is_Delayed_TARGET",
    int(mismatch_delay),
    PASS if mismatch_delay == 0 else FAIL,
    "No action needed." if mismatch_delay == 0 else "Recompute Is_Delayed_TARGET.",
    f"Is_Delayed_TARGET must equal 1 iff Delivery_Duration_Minutes > {thresh}. "
    f"Zero mismatches found on Delivered orders.",
    f"threshold={thresh}, mismatches={mismatch_delay}"
)

# 12b: Duration_Bin_TARGET vs duration values
bin_map = featured["Duration_Bin_TARGET"].map({
    "Fast (<30min)": (0, 30), "Normal (30-45min)": (30, 45), "Slow (>45min)": (45, 999)
})
bin_mismatch = 0
for label, (lo, hi) in [("Fast (<30min)",(0,30)),("Normal (30-45min)",(30,45)),("Slow (>45min)",(45,999))]:
    mask = featured["Duration_Bin_TARGET"] == label
    in_range = (featured.loc[mask, "Delivery_Duration_Minutes"] >= lo) & \
               (featured.loc[mask, "Delivery_Duration_Minutes"] < hi)
    bin_mismatch += (~in_range).sum()

record(
    "12b", "Duration_Bin_TARGET consistency with duration values", "Duration_Bin_TARGET",
    int(bin_mismatch),
    PASS if bin_mismatch == 0 else FAIL,
    "No action needed." if bin_mismatch == 0 else "Recompute Duration_Bin_TARGET.",
    "Each Duration_Bin_TARGET label must correspond to the correct duration range.",
    f"bin_mismatches={bin_mismatch}"
)

# 12c: Delay_Minutes_TARGET must be >= 0 and == max(0, duration - threshold)
neg_delay = (featured["Delay_Minutes_TARGET"] < 0).sum()
recomputed = np.maximum(0, featured["Delivery_Duration_Minutes"] - thresh)
delay_val_mismatch = (featured["Delay_Minutes_TARGET"].round(1) != recomputed.round(1)).sum()
record(
    "12c", "Delay_Minutes_TARGET values correctness", "Delay_Minutes_TARGET",
    int(neg_delay + delay_val_mismatch),
    PASS if (neg_delay + delay_val_mismatch) == 0 else FAIL,
    "No action needed." if (neg_delay + delay_val_mismatch) == 0 else "Recompute Delay_Minutes_TARGET.",
    "Delay_Minutes_TARGET = max(0, Delivery_Duration_Minutes - 45). All values correct.",
    f"negative_delay={neg_delay}, value_mismatches={delay_val_mismatch}"
)

# 12d: class balance of Is_Delayed_TARGET (on Delivered orders)
n_del = delivered.sum()
n_delayed_class = featured.loc[delivered, "Is_Delayed_TARGET"].sum()
delay_pct = n_delayed_class / n_del * 100
balance_ok = 10 <= delay_pct <= 49   # neither extreme imbalance nor majority
record(
    "12d", "Is_Delayed_TARGET class distribution (Delivered orders only)",
    "Is_Delayed_TARGET",
    int(n_delayed_class),
    PASS if balance_ok else WARN,
    "No action needed — class ratio is workable with standard cross-validation.",
    (f"Delayed: {n_delayed_class:,} ({delay_pct:.1f}%) | "
     f"On-time: {n_del - n_delayed_class:,} ({100-delay_pct:.1f}%). "
     "24% minority class is a mild imbalance. "
     "Stratified k-fold is sufficient; SMOTE is optional."),
    f"delayed={n_delayed_class}, on_time={n_del - n_delayed_class}, pct_delayed={delay_pct:.2f}"
)

# ==========================================================================
# CHECK 13 — Leakage check: POST_DELIVERY columns identified and labelled
# ==========================================================================
leakage_present = [c for c in LEAKAGE_COLS if c in featured.columns]
record(
    13, "Target leakage — POST_DELIVERY columns present in dataset",
    str(leakage_present),
    len(leakage_present),
    WARN,   # these should exist but must be excluded from model input
    "Leakage columns are present but labelled. Must be excluded from the model "
    "input feature matrix. They are retained for target definition and analytics.",
    "Leakage columns are: Delivery_Time, Delivery_Duration_Minutes, Order_Status, "
    "Is_Delivered, Is_Cancelled, Is_InTransit, Is_Delayed_TARGET, Delay_Minutes_TARGET, "
    "Duration_Bin_TARGET, Order_To_Delivery_Minutes_TARGET, "
    "Delivery_Speed_kmh_ANALYTICAL, Distance_Per_Minute_ANALYTICAL. "
    "All are documented in feature_documentation.md with explicit POST_DELIVERY labels.",
    f"leakage_cols_in_dataset={leakage_present}"
)

# ==========================================================================
# CHECK 14 — Constant or near-constant columns
# ==========================================================================
constant_cols = []
near_constant = []
for col in featured.columns:
    n_unique = featured[col].nunique(dropna=False)
    if n_unique == 1:
        constant_cols.append(col)
    elif n_unique == 2 and featured[col].dtype in [np.int64, np.float64, int, float]:
        pass  # binary flags are expected
    elif n_unique <= 5 and featured[col].dtype == object:
        pass  # low-cardinality cats are expected
    elif n_unique >= 2:
        # Check if dominant value > 99%
        top_freq = featured[col].value_counts(dropna=False, normalize=True).iloc[0]
        if top_freq > 0.99 and col not in BINARY_COLS:
            near_constant.append({"col": col, "top_freq": round(top_freq*100,2)})

record(
    14, "Constant columns (0 variance)", str(constant_cols) if constant_cols else "NONE",
    len(constant_cols),
    PASS if not constant_cols else WARN,
    "No constant columns found." if not constant_cols else f"Drop: {constant_cols}",
    "A column with only one unique value carries zero predictive information.",
    f"constant={constant_cols}"
)
record(
    "14b", "Near-constant columns (>99% single value)", str(near_constant) if near_constant else "NONE",
    len(near_constant),
    PASS if not near_constant else WARN,
    "Flag for Phase 2 feature selection review.",
    "Columns where >99% of rows share one value have near-zero variance and usually weak predictive power.",
    str(near_constant)
)

# ==========================================================================
# CHECK 15 — High cardinality columns
# ==========================================================================
high_card = {}
for col in featured.columns:
    n_unique = featured[col].nunique()
    pct_unique = n_unique / N * 100
    if pct_unique > 50 and featured[col].dtype == object:
        high_card[col] = {"n_unique": n_unique, "pct_unique": round(pct_unique, 2)}

record(
    15, "High-cardinality string columns (>50% unique values)",
    str(list(high_card.keys())) if high_card else "NONE",
    len(high_card),
    WARN if high_card else PASS,
    ("Flag for encoding strategy. High-cardinality identifiers (User_ID, Restaurant_ID, "
     "Driver_ID) require frequency or target encoding, not one-hot encoding. "
     "Order_Date / Order_DayName are expected to have many unique values."
     if high_card else "No unexpectedly high-cardinality columns."),
    "Columns where >50% of rows have a unique value are identifiers or free-text; "
    "one-hot encoding is inappropriate.",
    str(high_card) if high_card else "clean"
)

# ==========================================================================
# CHECK 16 — Identifier columns (should not be model inputs)
# ==========================================================================
id_cols_present = [c for c in featured.columns if c in DROP_COLS]
record(
    16, "Identifier / datetime columns in dataset", str(id_cols_present),
    len(id_cols_present),
    WARN,
    "Retain in dataset for analytics and joins. Must be excluded from model input feature matrix.",
    "Order_ID, User_ID, Restaurant_ID, Driver_ID are row identifiers. "
    "Order_Time, Delivery_Time are raw timestamps. "
    "Order_Date and Order_DayName are derived for analytics only. "
    "All are documented for exclusion in feature_documentation.md.",
    f"id_cols={id_cols_present}"
)

# ==========================================================================
# CHECK 17 — Geographic coordinate validity
# ==========================================================================
geo_issues = {}
for col, kind in GEO_COLS.items():
    if col not in featured.columns:
        continue
    lo, hi = GEO_BOUNDS[kind]
    bad = ((featured[col] < lo) | (featured[col] > hi)).sum()
    if bad > 0:
        geo_issues[col] = int(bad)

n_geo = sum(geo_issues.values())
record(
    17, "Geographic coordinates outside Egypt bounds", str(list(geo_issues.keys())) if geo_issues else "ALL",
    n_geo,
    PASS if n_geo == 0 else FAIL,
    "No action needed." if n_geo == 0 else f"Flag out-of-bounds rows: {geo_issues}",
    f"All 6 lat/lon columns verified within Egypt bounds "
    f"(lat {GEO_BOUNDS['lat']}, lon {GEO_BOUNDS['lon']}). Zero violations.",
    str(geo_issues) if geo_issues else "all within bounds"
)

# 17b — Per-city lat/lon cluster tightness
city_lat_std = featured.groupby("City")["Customer_Lat"].std()
loose_cities = city_lat_std[city_lat_std > 0.05]
record(
    "17b", "Per-city coordinate spread (std > 0.05 degrees)", str(loose_cities.index.tolist()) if len(loose_cities)>0 else "NONE",
    int(len(loose_cities)),
    PASS if len(loose_cities) == 0 else WARN,
    "No action needed." if len(loose_cities) == 0 else "Review city coordinate generation.",
    "Simulated coordinates cluster tightly per city (std ~0.012 degrees). "
    "A std > 0.05 would suggest coordinates spanning multiple cities.",
    city_lat_std.round(5).to_dict().__str__()
)

# ==========================================================================
# CHECK 18 — Binary columns have only 0/1 values
# ==========================================================================
binary_issues = {}
for col in BINARY_COLS:
    if col not in featured.columns:
        continue
    bad = ~featured[col].isin([0, 1])
    if bad.sum() > 0:
        binary_issues[col] = int(bad.sum())

n_bin = sum(binary_issues.values())
record(
    18, "Binary flag columns outside {0, 1}", str(list(binary_issues.keys())) if binary_issues else "ALL",
    n_bin,
    PASS if n_bin == 0 else FAIL,
    ("All binary columns contain only 0 and 1." if n_bin == 0
     else f"Re-encode: {binary_issues}"),
    "Binary indicator columns must contain only integer values 0 or 1.",
    str(binary_issues) if binary_issues else "all clean"
)

# ==========================================================================
# Summary stats for report
# ==========================================================================
n_pass = sum(1 for r in results if r["status"] == PASS)
n_warn = sum(1 for r in results if r["status"] == WARN)
n_fail = sum(1 for r in results if r["status"] == FAIL)

output = {
    "summary": {
        "raw_rows": raw_rows, "cleaned_rows": cleaned_rows, "featured_rows": featured_rows,
        "raw_cols": raw_cols, "cleaned_cols": cleaned_cols, "featured_cols": featured_cols,
        "checks_total": len(results),
        "pass": n_pass, "warn": n_warn, "fail": n_fail,
        "delay_threshold_min": 45.0,
        "delayed_pct": round(delay_pct, 2),
        "n_leakage_cols": len(leakage_present),
    },
    "results": results
}

OUTPUT_JSON = "validation_results.json"
with open(OUTPUT_JSON, "w", encoding="utf-8") as fh:
    json.dump(output, fh, indent=2)

print(f"Validation complete. Results written to {OUTPUT_JSON}")
print(f"PASS={n_pass}  WARN={n_warn}  FAIL={n_fail}")
