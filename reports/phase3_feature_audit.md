# Phase 3 Feature Audit & Classification Report
## Food Delivery Analytics: Delivery Performance and Delay Prediction

**Date:** 2026-10-03  
**Phase:** 3 — Data Preparation for Analytics and Machine Learning  
**Dataset Audited:** [`data/processed/food_delivery_10k.csv`](file:///c:/FoodDeliveryAnalytics/data/processed/food_delivery_10k.csv) (10,000 rows, 55 columns)  

---

## 1. Executive Summary

This feature audit inspects all **55 columns** of the Phase 2 representative modeling dataset. Every column is evaluated across 14 rigorous business, temporal, and technical dimensions to determine its role in:
1. **Delivery Performance Analytics** (cohort analysis, KPIs, dashboards, spatial/temporal performance profiling).
2. **Machine Learning Delay Prediction** (binary/regression target prediction without target leakage).

### Classification Taxonomy Definitions
- **`ML_FEATURE`**: Valid pre-order / dispatch predictor safe for machine learning inputs.
- **`TARGET`**: Ground-truth machine learning prediction outcome variable (binary, regression, or multi-class).
- **`LEAKAGE`**: Post-delivery or duration-derived column that reveals the future target outcome (must be excluded from ML inputs).
- **`IDENTIFIER`**: Primary key or high-cardinality entity ID (used for joins/aggregations, not raw ML inputs).
- **`ANALYTICAL_ONLY`**: Column providing context for reporting, dashboards, or row filtering (e.g., timestamps, status labels, dates).
- **`REMOVE`**: Zero-variance or uninformative feature recommended for removal prior to modeling.

---

## 2. Complete 55-Column Feature Audit Table

| # | Column Name | Data Type | Business Meaning | Temporal Availability | Target Leakage Risk? | Useful for Analytics? | Useful for ML? | Proposed Classification | Reason for Classification |
|---|---|---|---|---|---|---|---|---|---|
| 1 | `Order_ID` | `int64` | Primary key for delivery order | Order Placement | No | Yes (joins/counts) | No | **`IDENTIFIER`** | Primary key sequence number; no predictive generalization signal. |
| 2 | `User_ID` | `str` | Customer identifier (`U####`) | Order Placement | No | Yes (customer CLV) | No | **`IDENTIFIER`** | High-cardinality customer ID (9,000 unique values). Risk of severe overfitting. |
| 3 | `Restaurant_ID` | `int64` | Restaurant identifier | Order Placement | No | Yes (prep analytics) | Ambiguous | **`IDENTIFIER`** | High-cardinality ID (1,000 unique values). Candidate for target/frequency encoding in ML. |
| 4 | `Driver_ID` | `int64` | Delivery driver identifier | Dispatch | No | Yes (driver performance) | No | **`IDENTIFIER`** | High-cardinality driver ID (500 drivers). Simulated drivers use all vehicles uniformly. |
| 5 | `Item_Name` | `str` | Food item ordered (9 categories) | Order Placement | No | Yes (item popularity) | Yes | **`ML_FEATURE`** | Low-cardinality categorical proxy for kitchen preparation & packaging complexity. |
| 6 | `Quantity` | `int64` | Items ordered (1–5) | Order Placement | No | Yes (basket size) | Yes | **`ML_FEATURE`** | Direct discrete order size measure influencing kitchen load and packaging time. |
| 7 | `Total_Price` | `float64` | Total order value in EGP | Order Placement | No | Yes (revenue analysis) | Yes | **`ML_FEATURE`** | Continuous order value signal representing basket scale. |
| 8 | `Order_Time` | `str` (datetime) | Order placement timestamp | Order Placement | No | Yes (time-series trends) | No directly | **`ANALYTICAL_ONLY`** | Raw datetime string. Extracted components (`Order_Hour`, etc.) are used for ML. |
| 9 | `Delivery_Time` | `str` (datetime) | Delivery completion timestamp | Post-Delivery | **YES** | Yes (SLA verification) | No | **`LEAKAGE`** | Known only post-delivery. Direct subtraction with `Order_Time` leaks exact duration. |
| 10 | `Delivery_Duration_Minutes` | `int64` | Total delivery time (15–60 min) | Post-Delivery | **YES** | Yes (Primary KPI) | No as feature | **`TARGET`** | Continuous outcome duration. Serves as ground truth target basis; causes 100% leakage if used as input. |
| 11 | `City` | `str` | Delivery city (7 Egyptian cities) | Order Placement | No | Yes (regional KPIs) | Yes | **`ML_FEATURE`** | 7 balanced categories capturing regional traffic, geography, and urban density. |
| 12 | `Payment_Method` | `str` | Payment method (Cash/Wallet/Card) | Order Placement | No | Yes (channel mix) | Yes | **`ML_FEATURE`** | Pre-order category. Cash on delivery can introduce door handoff friction vs digital payments. |
| 13 | `Order_Status` | `str` | Final order status (Delivered/Cancelled/In Transit) | Post-Delivery / In-Progress | **YES** | Yes (Fulfillment KPI) | No as feature | **`ANALYTICAL_ONLY`** | Outcome state. Must be used as a **Row Filter** (train ML models only on `Order_Status == 'Delivered'`). |
| 14 | `Driver_Vehicle` | `str` | Vehicle type (Bicycle/Car/Motorbike) | Dispatch | No | Yes (fleet efficiency) | Yes | **`ML_FEATURE`** | Fleet mobility mode affecting urban speed profiles and traffic navigation. |
| 15 | `Restaurant_Lat` | `float64` | Restaurant latitude coordinate | Order Placement | No | Yes (spatial mapping) | Yes | **`ML_FEATURE`** | Exact spatial coordinate for geographic models and distance calculations. |
| 16 | `Restaurant_Lon` | `float64` | Restaurant longitude coordinate | Order Placement | No | Yes (spatial mapping) | Yes | **`ML_FEATURE`** | Exact spatial coordinate for geographic models. |
| 17 | `Customer_Lat` | `float64` | Customer latitude coordinate | Order Placement | No | Yes (spatial mapping) | Yes | **`ML_FEATURE`** | Exact customer location coordinate. |
| 18 | `Customer_Lon` | `float64` | Customer longitude coordinate | Order Placement | No | Yes (spatial mapping) | Yes | **`ML_FEATURE`** | Exact customer location coordinate. |
| 19 | `Driver_Lat` | `float64` | Driver latitude at dispatch | Dispatch | No | Yes (dispatch mapping) | Yes | **`ML_FEATURE`** | Driver starting location coordinate at dispatch. |
| 20 | `Driver_Lon` | `float64` | Driver longitude at dispatch | Dispatch | No | Yes (dispatch mapping) | Yes | **`ML_FEATURE`** | Driver starting location coordinate at dispatch. |
| 21 | `Delivery_Distance_km` | `float64` | Restaurant-to-customer distance (km) | Order Placement | No | Yes (distance SLA) | Yes | **`ML_FEATURE`** | Primary physical workload distance for the customer delivery leg (0.009–5.60 km). |
| 22 | `Traffic_Level` | `str` | Traffic level (Low/Medium/High) | Order Placement | No | Yes (traffic analysis) | Yes | **`ML_FEATURE`** | Pre-order environmental traffic condition indicator. |
| 23 | `Driver_Availability` | `str` | Driver status (Online/Offline) | Extraction Snapshot | No | Yes (fleet status) | No | **`ANALYTICAL_ONLY`** | System extraction snapshot (not live dispatch state). Unreliable pre-order signal. |
| 24 | `Restaurant_Geo_Imputed` | `int64` | Imputation flag (0/1) | Order Placement | No | Yes (audit flag) | No | **`REMOVE`** | **Zero variance** (100% values = 0 in dataset). Provides zero predictive signal. |
| 25 | `Customer_Geo_Imputed` | `int64` | Imputation flag (0/1) | Order Placement | No | Yes (audit flag) | No | **`REMOVE`** | **Zero variance** (100% values = 0 in dataset). |
| 26 | `Driver_Geo_Imputed` | `int64` | Imputation flag (0/1) | Order Placement | No | Yes (audit flag) | No | **`REMOVE`** | **Zero variance** (100% values = 0 in dataset). |
| 27 | `Same_Location_Flag` | `int64` | Same coords flag (0/1) | Order Placement | No | Yes (anomaly flag) | No | **`REMOVE`** | **Zero variance** (100% values = 0 in dataset). |
| 28 | `Order_Hour` | `int64` | Hour of day (0–23) | Order Placement | No | Yes (hourly trends) | Yes | **`ML_FEATURE`** | Key temporal predictor capturing diurnal demand cycles and traffic density. |
| 29 | `Order_DayOfWeek` | `int64` | Day of week index (0=Mon … 6=Sun) | Order Placement | No | Yes (weekly trends) | Yes | **`ML_FEATURE`** | Extracted numerical day index for weekly cycle prediction. |
| 30 | `Order_DayOfMonth` | `int64` | Day of month (1–31) | Order Placement | No | Yes (calendar trends) | Ambiguous | **`ANALYTICAL_ONLY`** | Numerical day of month (1–16). Too specific to 16-day window; poor long-term generalization. |
| 31 | `Is_Weekend` | `int64` | Weekend flag (0/1) | Order Placement | No | Yes (weekend vs weekday) | Yes | **`ML_FEATURE`** | Derived binary indicator for weekend traffic and demand shifts. |
| 32 | `Is_RushHour` | `int64` | Rush hour flag (0/1) | Order Placement | No | Yes (peak demand KPIs) | Yes | **`ML_FEATURE`** | Derived binary indicator for peak commuting and dining hours (7–9, 18–21). |
| 33 | `Price_Per_Item` | `float64` | Price per item in EGP | Order Placement | No | Yes (item tier analysis) | Yes | **`ML_FEATURE`** | Ratio feature decoupling order value from item quantity. |
| 34 | `Traffic_Level_Enc` | `int64` | Encoded traffic (Low=0, Med=1, High=2) | Order Placement | No | Yes (traffic stats) | Yes | **`ML_FEATURE`** | Pre-encoded ordinal integer representation of traffic level. |
| 35 | `Driver_Online` | `int64` | Binary driver online status (0/1) | Extraction Snapshot | No | Yes (availability stats) | No | **`ANALYTICAL_ONLY`** | Binary encoded driver availability extraction snapshot. |
| 36 | `Is_Delivered` | `int64` | Delivered flag (0/1) | Post-Delivery | **YES** | Yes (completion rate) | No | **`LEAKAGE`** | Derived directly from post-delivery `Order_Status`. |
| 37 | `Is_Cancelled` | `int64` | Cancelled flag (0/1) | Post-Delivery | **YES** | Yes (cancellation rate) | No | **`LEAKAGE`** | Derived directly from post-delivery `Order_Status`. |
| 38 | `Is_InTransit` | `int64` | In transit flag (0/1) | In-Progress | **YES** | Yes (active tracking) | No | **`LEAKAGE`** | Status flag during delivery execution; leaks outcome state. |
| 39 | `Order_Date` | `str` (date) | Order date (`YYYY-MM-DD`) | Order Placement | No | Yes (daily volume charts) | No | **`ANALYTICAL_ONLY`** | Specific calendar date; un-generalizable for future prediction models. |
| 40 | `Order_Month` | `int64` | Calendar month (6) | Order Placement | No | Yes (monthly reporting) | No | **`REMOVE`** | **Zero variance** (100% values = 6 in this 16-day June dataset). |
| 41 | `Order_DayName` | `str` | Day name (Monday … Sunday) | Order Placement | No | Yes (day-of-week tables) | No | **`ANALYTICAL_ONLY`** | String day name. Redundant with numerical `Order_DayOfWeek`. |
| 42 | `Time_Of_Day_Segment` | `str` | Named time band (6 segments) | Order Placement | No | Yes (segment reporting) | Yes | **`ML_FEATURE`** | 6 named time bands capturing non-linear diurnal operational shifts. |
| 43 | `Is_Weekday` | `int64` | Weekday flag (0/1) | Order Placement | No | Yes (weekday reporting) | Ambiguous | **`ANALYTICAL_ONLY`** | Binary flag; perfectly collinear with `Is_Weekend` (`Is_Weekday = 1 - Is_Weekend`). |
| 44 | `Driver_To_Restaurant_km` | `float64` | Driver to restaurant distance (km) | Dispatch | No | Yes (first-mile KPI) | Yes | **`ML_FEATURE`** | Physical first-mile dispatch distance (0.009–5.61 km). |
| 45 | `Total_Trip_km` | `float64` | Total trip distance (km) | Dispatch | No | Yes (total distance KPI) | Yes | **`ML_FEATURE`** | Sum of first-mile and customer leg distance (`Driver_To_Restaurant_km + Delivery_Distance_km`). |
| 46 | `Distance_Bin` | `str` | Distance tier (Short/Med/Long/V.Long) | Order Placement | No | Yes (tier reporting) | Yes | **`ML_FEATURE`** | Categorical/ordinal distance tier for decision-tree models. |
| 47 | `Order_Value_Tier` | `str` | Price tier (Budget/Standard/Premium/Luxury) | Order Placement | No | Yes (price tier reporting) | Yes | **`ML_FEATURE`** | Categorical/ordinal price tier for decision-tree models. |
| 48 | `Is_Large_Order` | `int64` | Large order flag (`Quantity >= 4`) | Order Placement | No | Yes (large order stats) | Yes | **`ML_FEATURE`** | Binary indicator for heavy kitchen preparation orders. |
| 49 | `Is_High_Traffic` | `int64` | Severe traffic flag (0/1) | Order Placement | No | Yes (high traffic stats) | Yes | **`ML_FEATURE`** | Binary indicator for severe traffic conditions. |
| 50 | `Is_Delayed_TARGET` | `int64` | Binary delay target (1 if >45 min) | Post-Delivery | **YES** | Yes (delay rate KPI) | **TARGET** | **`TARGET`** | **PRIMARY BINARY CLASSIFICATION TARGET ($y$)**. Known post-delivery. |
| 51 | `Delay_Minutes_TARGET` | `float64` | Delay excess in minutes (`max(0, Duration-45)`) | Post-Delivery | **YES** | Yes (delay magnitude KPI) | **TARGET** | **`TARGET`** | **PRIMARY REGRESSION TARGET ($y_{reg}$)**. Known post-delivery. |
| 52 | `Duration_Bin_TARGET` | `str` | Multi-class service tier (Fast/Normal/Slow) | Post-Delivery | **YES** | Yes (SLA tier KPI) | **TARGET** | **`TARGET`** | **MULTI-CLASS CLASSIFICATION TARGET ($y_{multi}$)**. Known post-delivery. |
| 53 | `Order_To_Delivery_Minutes_TARGET` | `float64` | Timestamp difference in minutes | Post-Delivery | **YES** | Yes (audit metric) | No | **`LEAKAGE`** | Redundant post-delivery audit metric. Identical to `Delivery_Duration_Minutes`. |
| 54 | `Delivery_Speed_kmh_ANALYTICAL` | `float64` | Delivery speed in km/h | Post-Delivery | **YES** | Yes (speed efficiency KPI) | No | **`ANALYTICAL_ONLY`** | Post-delivery speed metric. Uses actual duration; leaks target if used in ML. |
| 55 | `Distance_Per_Minute_ANALYTICAL` | `float64` | Distance covered per minute (km/min) | Post-Delivery | **YES** | Yes (pace efficiency KPI) | No | **`ANALYTICAL_ONLY`** | Post-delivery pace metric. Uses actual duration; leaks target if used in ML. |

---

## 3. Summary of Categorized Feature Sets

### A. Proposed Machine Learning Targets (3 Options)
1. **`Is_Delayed_TARGET`** — **Primary Binary Classification Target** ($1 = \text{Delayed} > 45\text{ min}$, $0 = \text{On-Time}$).
2. **`Delay_Minutes_TARGET`** — **Primary Regression Target** ($\max(0, \text{Duration} - 45)$ minutes late).
3. **`Duration_Bin_TARGET`** — **Multi-Class Classification Target** ($\text{Fast} [<30\text{m}]$, $\text{Normal} [30\text{–}45\text{m}]$, $\text{Slow} [>45\text{m}]$).

---

### B. Proposed Machine Learning Feature List (24 Safe Pre-Order / Dispatch Features)

#### 1. Numerical & Continuous Features (7)
- `Quantity` (1–5)
- `Total_Price` (EGP)
- `Price_Per_Item` (EGP)
- `Delivery_Distance_km` (km)
- `Driver_To_Restaurant_km` (km)
- `Total_Trip_km` (km)
- `Order_Hour` (0–23)
- `Order_DayOfWeek` (0–6)

#### 2. Categorical Features (8)
- `City` (7 categories)
- `Item_Name` (9 categories)
- `Payment_Method` (3 categories)
- `Driver_Vehicle` (3 categories)
- `Traffic_Level` (Low / Medium / High)
- `Time_Of_Day_Segment` (6 time bands)
- `Distance_Bin` (4 tiers)
- `Order_Value_Tier` (4 tiers)

#### 3. Binary Indicator & Spatial Flags (9)
- `Is_Weekend` (0/1)
- `Is_RushHour` (0/1)
- `Is_Large_Order` (0/1)
- `Is_High_Traffic` (0/1)
- `Traffic_Level_Enc` (0/1/2)
- Spatial coordinates (`Restaurant_Lat`, `Restaurant_Lon`, `Customer_Lat`, `Customer_Lon`, `Driver_Lat`, `Driver_Lon`)

---

### C. Target Leakage Columns (7 Columns — Exclude from ML Inputs)
1. `Delivery_Time` (Outcome timestamp)
2. `Is_Delivered` (Post-delivery status flag)
3. `Is_Cancelled` (Post-delivery cancellation flag)
4. `Is_InTransit` (Active delivery status flag)
5. `Order_To_Delivery_Minutes_TARGET` (Computed duration metric)
6. `Delivery_Speed_kmh_ANALYTICAL` (Speed calculated using actual duration)
7. `Distance_Per_Minute_ANALYTICAL` (Pace calculated using actual duration)

---

### D. Identifier Columns (4 Columns)
1. `Order_ID` (Primary key)
2. `User_ID` (Customer ID)
3. `Restaurant_ID` (Restaurant ID — candidate for target encoding in advanced models)
4. `Driver_ID` (Driver ID)

---

### E. Analytics-Only & Row Filter Columns (7 Columns)
1. `Order_Status` — **Critical Row Filter**: Delay prediction models must be trained **only** on rows where `Order_Status == 'Delivered'`.
2. `Order_Time` — Kept for timestamp charting.
3. `Order_Date` — Kept for daily volume trend analysis.
4. `Order_DayName` — Kept for human-readable day-of-week charts.
5. `Order_DayOfMonth` — Kept for calendar analytics; excluded from ML due to poor long-term generalization.
6. `Is_Weekday` — Perfectly collinear with `Is_Weekend` ($1 - \text{Is\_Weekend}$).
7. `Driver_Availability` / `Driver_Online` — System extraction snapshot field; un-generalizable for live dispatch prediction.

---

### F. Columns Recommended for Removal (5 Columns)
1. `Restaurant_Geo_Imputed` (100% zeros)
2. `Customer_Geo_Imputed` (100% zeros)
3. `Driver_Geo_Imputed` (100% zeros)
4. `Same_Location_Flag` (100% zeros)
5. `Order_Month` (100% values = 6 in this 16-day dataset)

---

## 5. Leakage and Temporal Availability Review

### A. Critical Data Science Challenge: The Decision Point Test
Every machine learning feature must satisfy the **Decision Point Test**:
> *"Would this information genuinely be available at the exact moment the platform needs to predict whether an order will be delayed?"*

In real-world logistics, delay prediction occurs at two potential decision points:
- **Decision Point A (Customer Checkout):** Prediction generated the instant the customer clicks *"Place Order"*.
- **Decision Point B (Driver Dispatch):** Prediction generated when the system matches and assigns a driver to the order.

In this project, we define the prediction point at **Driver Dispatch (Decision Point B)**. At driver dispatch, driver coordinates, vehicle assignment, and first-mile pickup distance (`Driver_To_Restaurant_km`) are known.

---

### B. Analysis of Questionable & Subtle Leakage Features

#### 1. Direct Target Leakage & Duration Derivatives
- **`Delivery_Duration_Minutes`**, **`Delay_Minutes_TARGET`**, **`Duration_Bin_TARGET`**, **`Is_Delayed_TARGET`**, **`Delivery_Time`**, **`Order_To_Delivery_Minutes_TARGET`**
- *Critique:* These columns are the target variables or direct mathematical transformations of the target outcome.
- *Verdict:* **100% DIRECT LEAKAGE.** Must be excluded from ML inputs.

---

#### 2. Indirect Target Leakage via Speed & Efficiency Metrics
- **`Delivery_Speed_kmh_ANALYTICAL`** $= (\text{Delivery\_Distance\_km} / \text{Delivery\_Duration\_Minutes}) \times 60$
- **`Distance_Per_Minute_ANALYTICAL`** $= \text{Delivery\_Distance\_km} / \text{Delivery\_Duration\_Minutes}$
- *Critique:* Although these feature names sound like innocent driver mobility metrics, their formulas use `Delivery_Duration_Minutes` (the actual target duration) in the denominator! In live inference, actual travel duration is unknown. If passed to a tree model, the model will reverse-engineer duration ($\text{Duration} = \text{Distance} / \text{Speed}$) and achieve 100% fake training accuracy that completely collapses in deployment.
- *Verdict:* **100% INDIRECT LEAKAGE.** Exclude from ML inputs.

---

#### 3. Post-Outcome Operational Status Encodings
- **`Order_Status`**, **`Is_Delivered`**, **`Is_Cancelled`**, **`Is_InTransit`**
- *Critique:* `Order_Status` reflects the final state of the order lifecycle. `Cancelled` orders in this dataset have durations representing time-to-cancellation (not delivery time). `In Transit` orders are active deliveries without a completed duration.
- *Verdict:* `Is_Delivered`, `Is_Cancelled`, and `Is_InTransit` represent **POST-OUTCOME LEAKAGE**. `Order_Status` must be used strictly as a **Row Filter** (`df['Order_Status'] == 'Delivered'`) prior to model training to isolate completed deliveries, but must NOT be included as a feature.

---

#### 4. Extraction Snapshot Fields
- **`Driver_Availability`** & **`Driver_Online`**
- *Critique:* As identified in the Phase 1 audit, `Driver_Availability` reflects the driver's online/offline status at the moment the database export occurred (system extraction snapshot), NOT their status when the order was dispatched. If a driver went offline hours after delivering an order, their historical row records "Offline".
- *Verdict:* **SEMANTICALLY UNRELIABLE SNAPSHOT FIELD.** Exclude from ML input features to prevent leakage of post-shift driver behavior.

---

#### 5. High-Cardinality & Meaningless Identifiers
- **`Order_ID`** (10,000 unique values): Sequential primary key. Zero predictive signal.
- **`User_ID`** (9,000 unique values): Customer ID with ~1.1 orders per user. Passing raw `User_ID` forces decision trees to memorize customer IDs, causing severe overfitting.
- **`Driver_ID`** (500 unique values): Drivers in this synthetic dataset are uniformly assigned across cities and vehicles. Raw ID causes split fragmentation without adding signal.
- **`Restaurant_ID`** (1,000 unique values): High-cardinality restaurant ID (~10 orders/restaurant).
- *Verdict:* Exclude `Order_ID`, `User_ID`, `Driver_ID`, and raw `Restaurant_ID` from baseline ML feature matrices. (`Restaurant_ID` is reserved as a candidate for target encoding in advanced iterations).

---

#### 6. Multicollinearity & Redundancy
- **`Is_Weekday` vs `Is_Weekend`:** `Is_Weekday = 1 - Is_Weekend` (perfect linear dependency). Keep `Is_Weekend` only for linear models.
- **`Order_DayOfMonth`:** Dataset spans 16 days (June 1–16). Using day-of-month (1–16) creates splits specific to this 2-week window that fail to generalize to future months. Relegate to `ANALYTICAL_ONLY`.

---

## 6. Final Recommended ML Feature Set, Target & Exclusions

### Primary Machine Learning Target
- **`Is_Delayed_TARGET`** (Binary Classification: $1$ if `Delivery_Duration_Minutes > 45`, $0$ otherwise).
- **Target Subset Filter:** `df[df['Order_Status'] == 'Delivered']` (8,520 rows in the 10k dataset).

---

### Final Recommended ML Feature Matrix (24 Safe Features)

```python
FINAL_ML_FEATURES = [
    # 1. Order & Basket Features
    'Quantity',
    'Total_Price',
    'Price_Per_Item',
    'Is_Large_Order',
    'Item_Name',
    'Payment_Method',

    # 2. Geographic & Distance Features
    'City',
    'Delivery_Distance_km',
    'Driver_To_Restaurant_km',
    'Total_Trip_km',
    'Distance_Bin',

    # 3. Spatial Coordinates
    'Restaurant_Lat',
    'Restaurant_Lon',
    'Customer_Lat',
    'Customer_Lon',
    'Driver_Lat',
    'Driver_Lon',

    # 4. Temporal Features
    'Order_Hour',
    'Order_DayOfWeek',
    'Is_Weekend',
    'Is_RushHour',
    'Time_Of_Day_Segment',

    # 5. Mobility & Traffic Features
    'Driver_Vehicle',
    'Traffic_Level_Enc'
]
```

---

### Complete List of Excluded Columns (30 Columns)

| Category | Columns Excluded | Reason |
|---|---|---|
| **Direct & Indirect Target Leakage** (10) | `Delivery_Time`, `Delivery_Duration_Minutes`, `Is_Delivered`, `Is_Cancelled`, `Is_InTransit`, `Order_To_Delivery_Minutes_TARGET`, `Delivery_Speed_kmh_ANALYTICAL`, `Distance_Per_Minute_ANALYTICAL`, `Delay_Minutes_TARGET`, `Duration_Bin_TARGET` | Leaks outcome timestamps, duration, or uses duration in metric formulas. |
| **Identifiers & High-Cardinality** (4) | `Order_ID`, `User_ID`, `Restaurant_ID`, `Driver_ID` | Primary keys and high-cardinality IDs causing severe overfitting. |
| **Analytics-Only & Redundant** (7) | `Order_Time`, `Order_Date`, `Order_DayName`, `Order_DayOfMonth`, `Is_Weekday`, `Driver_Availability`, `Driver_Online` | Un-generalizable dates, perfectly collinear flags, or extraction snapshot fields. |
| **Row Filter Only** (1) | `Order_Status` | Used to filter dataset to completed deliveries; excluded from feature matrix. |
| **Zero Variance** (5) | `Restaurant_Geo_Imputed`, `Customer_Geo_Imputed`, `Driver_Geo_Imputed`, `Same_Location_Flag`, `Order_Month` | Constant values with zero statistical variance. |

---

## 7. Next Steps

- The feature audit and temporal leakage review are complete.
- **Dataset State:** [`data/processed/food_delivery_10k.csv`](file:///c:/FoodDeliveryAnalytics/data/processed/food_delivery_10k.csv) remains **100% unmodified**.
- Models have **not** been trained.
