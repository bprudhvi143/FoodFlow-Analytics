# Phase 1 Data Quality Report
## Food Delivery Analytics: Delivery Performance and Delay Prediction

**Date:** 2025-06-16  
**Phase:** 1 — Dataset Understanding, Preprocessing, and Feature Engineering  
**Scripts:** `src/preprocessing/preprocess.py` · `src/preprocessing/feature_engineering.py`  
**Validation:** `validate_dataset.py` (33 checks · 26 PASS · 7 WARN · 0 FAIL)

---

## 1. Dataset Summary

| Property | Value |
|---|---|
| Source file | `data/raw/Order_delivery.csv` |
| Format | CSV, UTF-8, comma-separated |
| Raw rows | 100,002 |
| Raw columns | 23 |
| Date range | 01 Jun 2025 10:00 → 16 Jun 2025 10:00 (16 days) |
| Geography | 7 Egyptian cities: Cairo, Giza, Alexandria, Tanta, Mansoura, Zagazig, Assiut |
| Simulated dataset | Yes — variables generated independently (no real causal structure) |

---

## 2. Preprocessing Results

### Row-level changes

| Stage | Rows in | Rows out | Rows removed | Reason |
|---|---|---|---|---|
| Duplicate removal | 100,002 | 100,002 | 0 | No full-row or Order_ID duplicates |
| Missing values | 100,002 | 100,002 | 0 | Zero missing values across all 23 columns |
| Type coercion | 100,002 | 100,002 | 0 | All values coerced cleanly |
| Numerical validity | 100,002 | 100,002 | 0 | No values outside valid domain bounds |
| Datetime validation | 100,002 | 100,002 | 0 | No NaT, no chrono violations, no mismatches |
| Placeholder scan | 100,002 | 100,002 | 0 | No placeholder strings or zero values |
| **Final cleaned** | **100,002** | **100,002** | **0 total** | Dataset was already clean |

### Column-level changes

| Stage | Columns before | Columns after | New columns added |
|---|---|---|---|
| Raw | 23 | — | — |
| After preprocessing | 23 | 38 | +15 |
| After feature engineering | 38 | 55 | +17 |

#### 15 columns added by preprocessing

| Column | Formula / source | Purpose |
|---|---|---|
| `Restaurant_Geo_Imputed` | 1 if restaurant lat/lon was city-median imputed | Imputation audit flag |
| `Customer_Geo_Imputed` | 1 if customer lat/lon was city-median imputed | Imputation audit flag |
| `Driver_Geo_Imputed` | 1 if driver lat/lon was city-median imputed | Imputation audit flag |
| `Same_Location_Flag` | 1 if restaurant and customer share identical coords | Anomaly flag |
| `Order_Hour` | `Order_Time.hour` | Time-of-day feature |
| `Order_DayOfWeek` | `Order_Time.dayofweek` (0=Mon) | Day-of-week feature |
| `Order_DayOfMonth` | `Order_Time.day` | Calendar feature |
| `Is_Weekend` | 1 if Saturday or Sunday | Weekend flag |
| `Is_RushHour` | 1 if hour in {7–9, 18–21} | Rush-hour flag |
| `Price_Per_Item` | `Total_Price / Quantity` | Per-item price tier |
| `Traffic_Level_Enc` | Low=0, Medium=1, High=2 | Ordinal traffic encoding |
| `Driver_Online` | Online=1, Offline=0 | Binary availability encoding |
| `Is_Delivered` | 1 if `Order_Status == 'Delivered'` | Status flag (POST_DELIVERY) |
| `Is_Cancelled` | 1 if `Order_Status == 'Cancelled'` | Status flag (POST_DELIVERY) |
| `Is_InTransit` | 1 if `Order_Status == 'In Transit'` | Status flag (POST_DELIVERY) |

#### 17 columns added by feature engineering

| Column | Availability | Formula / description |
|---|---|---|
| `Order_Date` | PRE_ORDER | `Order_Time.date` |
| `Order_Month` | PRE_ORDER | `Order_Time.month` |
| `Order_DayName` | PRE_ORDER | Day name (Monday … Sunday) |
| `Time_Of_Day_Segment` | PRE_ORDER | 6 named time bands from Order_Hour |
| `Is_Weekday` | PRE_ORDER | `1 - Is_Weekend` |
| `Driver_To_Restaurant_km` | PRE_ORDER | Haversine(driver → restaurant) |
| `Total_Trip_km` | PRE_ORDER | `Driver_To_Restaurant_km + Delivery_Distance_km` |
| `Distance_Bin` | PRE_ORDER | Cut Delivery_Distance_km into 4 bands |
| `Order_Value_Tier` | PRE_ORDER | Cut Total_Price into 4 price tiers |
| `Is_Large_Order` | PRE_ORDER | 1 if Quantity ≥ 4 |
| `Is_High_Traffic` | PRE_ORDER | 1 if Traffic_Level == 'High' |
| `Is_Delayed_TARGET` ⛔ | POST_DELIVERY | 1 if Duration > 45 min — **primary classification target** |
| `Delay_Minutes_TARGET` ⛔ | POST_DELIVERY | `max(0, Duration − 45)` — **primary regression target** |
| `Duration_Bin_TARGET` ⛔ | POST_DELIVERY | Fast/Normal/Slow — multi-class target |
| `Order_To_Delivery_Minutes_TARGET` ⛔ | POST_DELIVERY | Computed duration audit column |
| `Delivery_Speed_kmh_ANALYTICAL` ⛔ | POST_DELIVERY | `(Distance / Duration) × 60` — analytics only |
| `Distance_Per_Minute_ANALYTICAL` ⛔ | POST_DELIVERY | `Distance / Duration` — analytics only |

> ⛔ = leakage risk — must NOT be used as model input features

---

## 3. Missing Value Treatment

**Result: no missing values were found.** All 23 raw columns are complete across all 100,002 rows.

The following treatment strategy is implemented in `preprocess.py` and will activate automatically if missing values appear in future data refreshes:

| Column type | Strategy | Justification |
|---|---|---|
| Identifiers (Order_ID, User_ID, Restaurant_ID, Driver_ID) | Drop row | Missing identifier corrupts entity-level aggregations |
| Datetime (Order_Time, Delivery_Time) | Drop row | Duration and temporal features cannot be computed |
| Order_Status (target) | Drop row | Imputing target introduces label noise |
| Delivery_Duration_Minutes (target) | Drop if ≤ 0.1%, flag if > 0.1% | Cannot safely impute regression target |
| Numerics (Quantity, Total_Price, Distance) | Drop if ≤ 0.1%, median if ≤ 1%, flag if > 1% | Median is robust to skew and does not extend range |
| Geo coordinates | City-median imputation + imputation flag | City coords accurate to ~4 km; flagged for transparency |
| Categoricals (City, Traffic_Level, etc.) | Mode if ≤ 0.5%, drop if > 0.5% | Low-cardinality; mode avoids fabricating rare categories |

---

## 4. Duplicate Treatment

- **Full-row duplicates:** 0 — no action
- **Duplicate Order_IDs:** 0 — no action
- Note: the dataset contains 100,002 rows (not 100,000); this is because Order_IDs 100001 and 100002 are legitimate additional orders, not duplicates

---

## 5. Data Type Corrections

| Column | Before | After |
|---|---|---|
| `Order_Time` | str (`DD-MM-YYYY HH:MM`) | datetime64[us] |
| `Delivery_Time` | str (`DD-MM-YYYY HH:MM`) | datetime64[us] |
| `Order_ID`, `Restaurant_ID`, `Driver_ID`, `Quantity`, `Delivery_Duration_Minutes` | int64 | Int64 (nullable) |
| All float columns | float64 | float64 (unchanged) |
| All string columns | str/object | str (standardised) |

---

## 6. Categorical Standardisation

| Check | Result |
|---|---|
| Leading/trailing whitespace | 0 rows affected |
| Capitalisation variants (e.g. 'high' → 'High') | 0 needed correction |
| Unexpected category values | 0 |
| User_ID format (U####) | 100,002 / 100,002 valid |

All 9 categorical columns contain only expected values with consistent capitalisation and no whitespace anomalies.

---

## 7. Numerical Validity Checks

| Column | Constraint checked | Violations |
|---|---|---|
| Quantity | 1 ≤ x ≤ 5 | 0 |
| Total_Price | > 0 EGP | 0 |
| Delivery_Duration_Minutes | 5 ≤ x ≤ 240 | 0 |
| Delivery_Distance_km | 0.001 ≤ x ≤ 100 km | 0 |
| All 6 lat/lon columns | Egypt bounds (lat 20–33°N, lon 24–38°E) | 0 |

---

## 8. Datetime Integrity Checks

| Check | Result |
|---|---|
| Unparseable Order_Time strings | 0 NaT |
| Unparseable Delivery_Time strings | 0 NaT |
| Delivery_Time < Order_Time | 0 violations |
| Delivery_Duration_Minutes ≠ computed difference (>1 min) | 0 mismatches |
| Order dates outside 2025 | 0 violations |

---

## 9. Statistical Outliers (noted, not removed)

| Column | IQR fence | Outlier count | Action |
|---|---|---|---|
| Total_Price | [−248, 759] EGP | 0 | None needed |
| Delivery_Duration_Minutes | [7.5, 67.5] min | 0 | None needed |
| Delivery_Distance_km | [−1.0, 5.28] km | 30 (0.03%) | Retained — valid long-distance deliveries |
| Driver_To_Restaurant_km | [−1.0, 5.28] km | 30 (0.03%) | Retained — same rows as above |
| Total_Trip_km | up to ~10 km | 360 (0.36%) | Retained — sum of two valid components |

Statistical outliers within valid domain bounds are NOT removed in preprocessing. Outlier treatment (winsorising, robust scaling) is a Phase 2 modelling decision.

---

## 10. Key Dataset Insights

1. **This is a simulated dataset.** Variables appear to have been generated independently. As a result:
   - Traffic_Level has zero correlation with Delivery_Duration (means differ by < 0.15 min across Low/Medium/High)
   - Delivery_Distance_km has Pearson r ≈ −0.002 with duration
   - All 500 drivers use all 3 vehicle types (vehicle is per-delivery, not per-driver)
   - Hourly order volume is perfectly flat (no real rush-hour pattern)

2. **Order_Status = 'In Transit'** rows appear uniformly across all 16 days (~300/day), not clustered on the final day as a real operational snapshot would show. These are likely a simulated status and should be excluded from delay prediction modelling.

3. **Cancelled orders** contain valid `Delivery_Duration_Minutes` values — this represents time-to-cancellation, not delivery time. These rows must be excluded when training the delay prediction model.

4. **Driver_Availability** is a snapshot field — it reflects the driver's status at the time the dataset was extracted, not at order placement. Use with caution as a model feature.

---

## 11. Target Variable

**Primary classification target:** `Is_Delayed_TARGET`
- Definition: 1 if `Delivery_Duration_Minutes` > 45 minutes
- Threshold: p75 of `Delivery_Duration_Minutes` among `Order_Status == 'Delivered'` rows
- Class distribution (Delivered orders only): 75.7% on-time · 24.3% delayed

**Primary regression target:** `Delay_Minutes_TARGET`
- Definition: `max(0, Delivery_Duration_Minutes − 45)`
- Represents minutes beyond the SLA threshold

**Multi-class target:** `Duration_Bin_TARGET`
- Fast (<30 min) · Normal (30–45 min) · Slow (>45 min)

---

## 12. Data Leakage Risks

The following 12 columns are POST_DELIVERY outcomes and must NEVER appear in the input feature matrix `X` of any predictive model:

| Column | Reason |
|---|---|
| `Delivery_Time` | Outcome timestamp |
| `Delivery_Duration_Minutes` | Primary target — the value we are predicting |
| `Order_Status` | Post-event status |
| `Is_Delivered`, `Is_Cancelled`, `Is_InTransit` | Derived from post-event status |
| `Is_Delayed_TARGET` | Classification target |
| `Delay_Minutes_TARGET` | Regression target |
| `Duration_Bin_TARGET` | Multi-class target |
| `Order_To_Delivery_Minutes_TARGET` | Redundant with duration |
| `Delivery_Speed_kmh_ANALYTICAL` | Requires duration |
| `Distance_Per_Minute_ANALYTICAL` | Requires duration |

Additionally, the following columns should be excluded from model inputs as identifiers or zero-variance columns:

- `Order_ID`, `User_ID`, `Restaurant_ID`, `Driver_ID` — identifiers
- `Order_Time`, `Delivery_Time` — raw timestamps (extract features from them instead)
- `Order_Date`, `Order_DayName` — analytics-only labels
- `Restaurant_Geo_Imputed`, `Customer_Geo_Imputed`, `Driver_Geo_Imputed`, `Same_Location_Flag`, `Order_Month` — all zero-variance (single value) in this dataset

---

## 13. Output Files

| File | Description | Rows | Columns |
|---|---|---|---|
| `data/raw/Order_delivery.csv` | Original dataset — **never modified** | 100,002 | 23 |
| `data/processed/Order_delivery_cleaned.csv` | Type-corrected, validated, encoded | 100,002 | 38 |
| `data/processed/Order_delivery_featured.csv` | Cleaned + all derived features + targets | 100,002 | 55 |

---

## 14. Validation Summary

33 checks across 18 quality dimensions — **26 PASS · 7 WARN · 0 FAIL**

All 7 warnings are expected and non-blocking:
- 4 warnings are statistical outliers retained intentionally
- 1 warning is for documented leakage columns (present but labelled)
- 1 warning is for zero-variance columns (present but excluded from model inputs)
- 1 warning is for identifier columns (present but excluded from model inputs)

**Dataset is ready for Phase 2: Exploratory Data Analysis and Visualisation.**
