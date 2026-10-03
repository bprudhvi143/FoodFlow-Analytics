# Phase 3 Dataset Design & Specification Report
## Food Delivery Analytics: Delivery Performance and Delay Prediction

**Date:** 2026-10-03  
**Phase:** 3 — Dataset Creation for Analytics and Machine Learning  
**Input Dataset:** [`data/processed/food_delivery_10k.csv`](file:///c:/FoodDeliveryAnalytics/data/processed/food_delivery_10k.csv) (10,000 rows, 55 columns)  
**Output Datasets:**
1. **Analytics Dataset:** [`data/processed/food_delivery_analytics_10k.csv`](file:///c:/FoodDeliveryAnalytics/data/processed/food_delivery_analytics_10k.csv)
2. **Machine Learning Dataset:** [`data/processed/food_delivery_ml_10k.csv`](file:///c:/FoodDeliveryAnalytics/data/processed/food_delivery_ml_10k.csv)  

---

## 1. Executive Summary

Based on the finalized Phase 3 feature audit, two logically separate datasets have been created from the Phase 2 10,000-row representative sample. The original modeling dataset [`data/processed/food_delivery_10k.csv`](file:///c:/FoodDeliveryAnalytics/data/processed/food_delivery_10k.csv) remains **100% unmodified**.

- **Analytics Dataset:** Preserves 10,000 rows across all order statuses (Delivered, Cancelled, In Transit) and 50 columns containing operational metrics, timestamps, status labels, duration, delay targets, and efficiency KPIs for performance analysis and visualization dashboards.
- **Machine Learning Dataset:** Isolates 8,520 completed deliveries (`Order_Status == 'Delivered'`) and 27 columns (26 safe pre-order features + 1 target `Is_Delayed_TARGET`). All direct/indirect leakage columns, pure identifiers, and zero-variance columns have been strictly removed.

---

## 2. Dataset Design & Specifications

### Summary Comparison Table

| Property | Analytics Dataset | Machine Learning Dataset |
|---|---|---|
| **Target File Path** | [`data/processed/food_delivery_analytics_10k.csv`](file:///c:/FoodDeliveryAnalytics/data/processed/food_delivery_analytics_10k.csv) | [`data/processed/food_delivery_ml_10k.csv`](file:///c:/FoodDeliveryAnalytics/data/processed/food_delivery_ml_10k.csv) |
| **Secondary Copy Path** | [`Datasets/food_delivery_analytics_10k.csv`](file:///c:/FoodDeliveryAnalytics/Datasets/food_delivery_analytics_10k.csv) | [`Datasets/food_delivery_ml_10k.csv`](file:///c:/FoodDeliveryAnalytics/Datasets/food_delivery_ml_10k.csv) |
| **Primary Purpose** | Operational reporting, SLA benchmarking, performance visualisations | Predictive modeling for delivery delay classification |
| **Row Population** | **10,000 rows** (All statuses: 8,520 Delivered, 980 Cancelled, 500 In Transit) | **8,520 rows** (Filtered to completed deliveries: `Order_Status == 'Delivered'`) |
| **Column Count** | **50 columns** | **27 columns** (26 ML Features + 1 Target `Is_Delayed_TARGET`) |
| **Missing Values** | **0 nulls** | **0 nulls** |
| **Target Leakage Columns** | Retained for analytics and outcome benchmarking | **0 (Strictly Excluded)** |
| **Identifier Columns** | Retained (`Order_ID`, `User_ID`, `Restaurant_ID`, `Driver_ID`) | **0 (Strictly Excluded)** |

---

## 3. Analytics Dataset Column Inventory (50 Columns)

The Analytics Dataset retains 10,000 rows and 50 columns. Five zero-variance columns (`Restaurant_Geo_Imputed`, `Customer_Geo_Imputed`, `Driver_Geo_Imputed`, `Same_Location_Flag`, `Order_Month`) were dropped.

### Column Categories in Analytics Dataset
1. **Identifiers (4):** `Order_ID`, `User_ID`, `Restaurant_ID`, `Driver_ID`.
2. **Order Specs (7):** `Item_Name`, `Quantity`, `Total_Price`, `Price_Per_Item`, `Order_Value_Tier`, `Is_Large_Order`, `Payment_Method`.
3. **Geography & Distance (11):** `City`, `Delivery_Distance_km`, `Driver_To_Restaurant_km`, `Total_Trip_km`, `Distance_Bin`, `Restaurant_Lat`, `Restaurant_Lon`, `Customer_Lat`, `Customer_Lon`, `Driver_Lat`, `Driver_Lon`.
4. **Fleet & Traffic (6):** `Driver_Vehicle`, `Driver_Availability`, `Driver_Online`, `Traffic_Level`, `Traffic_Level_Enc`, `Is_High_Traffic`.
5. **Timestamps & Temporal (9):** `Order_Time`, `Delivery_Time`, `Order_Date`, `Order_DayName`, `Order_Hour`, `Order_DayOfWeek`, `Order_DayOfMonth`, `Time_Of_Day_Segment`, `Is_Weekend`, `Is_Weekday`, `Is_RushHour`.
6. **Fulfillment & Outcomes (5):** `Order_Status`, `Is_Delivered`, `Is_Cancelled`, `Is_InTransit`, `Delivery_Duration_Minutes`.
7. **Targets & Benchmarks (4):** `Is_Delayed_TARGET`, `Delay_Minutes_TARGET`, `Duration_Bin_TARGET`, `Order_To_Delivery_Minutes_TARGET`.
8. **Analytical Efficiency Metrics (2):** `Delivery_Speed_kmh_ANALYTICAL`, `Distance_Per_Minute_ANALYTICAL`.

---

## 4. Machine Learning Dataset Column Inventory (27 Columns)

The Machine Learning Dataset contains **8,520 rows** (completed deliveries) and **27 columns** (26 pre-order features + 1 target variable).

### A. Target Column (1 Column)
- **`Is_Delayed_TARGET`**: Ground-truth binary target ($1 = \text{Delayed} > 45\text{ min}$, $0 = \text{On-Time}$). Class distribution: 6,452 On-Time (75.73%) vs 2,068 Delayed (24.27%).

### B. Legitimate ML Features (26 Columns)

| # | Feature Name | Data Type | Feature Sub-Type | Description |
|---|---|---|---|---|
| 1 | `Quantity` | `int64` | Order Spec (Discrete) | Number of food items ordered (1–5) |
| 2 | `Total_Price` | `float64` | Order Spec (Continuous) | Total order value in EGP (30–750 EGP) |
| 3 | `Price_Per_Item` | `float64` | Order Spec (Continuous) | Average price per item (`Total_Price / Quantity`) |
| 4 | `Is_Large_Order` | `int64` | Order Spec (Binary Flag) | 1 if `Quantity >= 4`, else 0 |
| 5 | `Item_Name` | `str` | Order Spec (Categorical) | Food item ordered (9 categories) |
| 6 | `Payment_Method` | `str` | Transaction (Categorical) | Payment method (Cash, Credit Card, Wallet) |
| 7 | `City` | `str` | Geography (Categorical) | Delivery city (7 Egyptian cities) |
| 8 | `Delivery_Distance_km` | `float64` | Distance (Continuous) | Restaurant-to-customer Haversine distance (km) |
| 9 | `Driver_To_Restaurant_km` | `float64` | Distance (Continuous) | Driver dispatch to restaurant Haversine distance (km) |
| 10 | `Total_Trip_km` | `float64` | Distance (Continuous) | Total physical trip distance (`Driver_To_Restaurant_km + Delivery_Distance_km`) |
| 11 | `Distance_Bin` | `str` | Distance (Ordinal Category)| Bucketed distance tier (Short, Medium, Long, Very Long) |
| 12 | `Order_Value_Tier` | `str` | Order Spec (Ordinal Category)| Bucketed price tier (Budget, Standard, Premium, Luxury) |
| 13 | `Restaurant_Lat` | `float64` | Spatial Coordinate | Restaurant latitude coordinate |
| 14 | `Restaurant_Lon` | `float64` | Spatial Coordinate | Restaurant longitude coordinate |
| 15 | `Customer_Lat` | `float64` | Spatial Coordinate | Customer drop-off latitude coordinate |
| 16 | `Customer_Lon` | `float64` | Spatial Coordinate | Customer drop-off longitude coordinate |
| 17 | `Driver_Lat` | `float64` | Spatial Coordinate | Driver dispatch starting latitude coordinate |
| 18 | `Driver_Lon` | `float64` | Spatial Coordinate | Driver dispatch starting longitude coordinate |
| 19 | `Order_Hour` | `int64` | Temporal (Discrete) | Hour of order placement (0–23) |
| 20 | `Order_DayOfWeek` | `int64` | Temporal (Discrete) | Day of week index (0=Mon … 6=Sun) |
| 21 | `Is_Weekend` | `int64` | Temporal (Binary Flag) | 1 if Saturday or Sunday, else 0 |
| 22 | `Is_RushHour` | `int64` | Temporal (Binary Flag) | 1 if hours in {7–9, 18–21}, else 0 |
| 23 | `Time_Of_Day_Segment` | `str` | Temporal (Categorical) | 6 named time bands (Late Night … Night) |
| 24 | `Driver_Vehicle` | `str` | Mobility (Categorical) | Driver vehicle mode (Bicycle, Car, Motorbike) |
| 25 | `Traffic_Level` | `str` | Environment (Categorical) | Traffic density level (Low, Medium, High) |
| 26 | `Traffic_Level_Enc` | `int64` | Environment (Ordinal) | Encoded traffic level (Low=0, Medium=1, High=2) |

---

## 5. Detailed Rationale for All Exclusions from ML Dataset

| # | Excluded Column | Category | Reason for Exclusion |
|---|---|---|---|
| 1 | `Delivery_Time` | **Leakage** | Post-delivery completion timestamp. Subtraction with `Order_Time` leaks exact duration. |
| 2 | `Delivery_Duration_Minutes` | **Leakage** | Post-delivery continuous duration. Basis of the target variable; direct 100% target leakage. |
| 3 | `Is_Delivered` | **Leakage** | Post-delivery status flag derived from `Order_Status`. |
| 4 | `Is_Cancelled` | **Leakage** | Post-delivery status flag derived from `Order_Status`. |
| 5 | `Is_InTransit` | **Leakage** | Active delivery status flag. |
| 6 | `Order_To_Delivery_Minutes_TARGET` | **Leakage** | Post-delivery computed duration audit metric. Identical to `Delivery_Duration_Minutes`. |
| 7 | `Delivery_Speed_kmh_ANALYTICAL` | **Leakage** | Post-delivery metric calculated using actual duration ($\text{Distance} / \text{Duration}$). Leaks target outcome. |
| 8 | `Distance_Per_Minute_ANALYTICAL` | **Leakage** | Post-delivery metric calculated using actual duration ($\text{Distance} / \text{Duration}$). Leaks target outcome. |
| 9 | `Delay_Minutes_TARGET` | **Target (Secondary)** | Continuous regression target. Excluded to keep binary classification dataset focused. |
| 10 | `Duration_Bin_TARGET` | **Target (Secondary)** | Multi-class target. Excluded from binary classification dataset. |
| 11 | `Order_ID` | **Identifier** | Sequential primary key (1–10,000). Zero predictive signal. |
| 12 | `User_ID` | **Identifier** | High-cardinality customer ID (9,000 unique). Causes severe decision tree overfitting. |
| 13 | `Restaurant_ID` | **Identifier** | High-cardinality restaurant ID (1,000 unique). Raw ID causes tree split fragmentation. |
| 14 | `Driver_ID` | **Identifier** | High-cardinality driver ID (500 unique). Uniform simulated assignment across drivers. |
| 15 | `Order_Status` | **Row Filter Only** | Used to filter dataset rows to `Order_Status == 'Delivered'` (8,520 rows). Excluded from feature matrix. |
| 16 | `Order_Time` | **Analytics Only** | Raw placement timestamp string. Extracted components (`Order_Hour`, etc.) are used for ML. |
| 17 | `Order_Date` | **Analytics Only** | Specific calendar date (`YYYY-MM-DD`). Poor long-term model generalization. |
| 18 | `Order_DayName` | **Analytics Only** | String day name. Redundant with integer `Order_DayOfWeek`. |
| 19 | `Order_DayOfMonth` | **Analytics Only** | Numerical day index (1–16). Too specific to 16-day dataset window. |
| 20 | `Is_Weekday` | **Redundant** | Perfectly collinear with `Is_Weekend` ($1 - \text{Is\_Weekend}$). |
| 21 | `Driver_Availability` | **Unreliable Snapshot** | System extraction snapshot field (reflects database export time, not order dispatch time). |
| 22 | `Driver_Online` | **Unreliable Snapshot** | Binary encoded system extraction snapshot status. |
| 23 | `Restaurant_Geo_Imputed` | **Zero Variance** | 100% values = 0 in dataset. Provides zero statistical variance. |
| 24 | `Customer_Geo_Imputed` | **Zero Variance** | 100% values = 0 in dataset. |
| 25 | `Driver_Geo_Imputed` | **Zero Variance** | 100% values = 0 in dataset. |
| 26 | `Same_Location_Flag` | **Zero Variance** | 100% values = 0 in dataset. |
| 27 | `Order_Month` | **Zero Variance** | 100% values = 6 in this 16-day June dataset. |

---

## 6. Machine-Readable Feature Configuration

The dataset feature configuration is programmatically maintained in [`src/config/features.py`](file:///c:/FoodDeliveryAnalytics/src/config/features.py), defining:
- `PRIMARY_TARGET` (`Is_Delayed_TARGET`)
- `ML_FEATURE_COLUMNS` (26 features)
- `LEAKAGE_COLUMNS` (8 columns)
- `IDENTIFIER_COLUMNS` (4 columns)
- `ANALYTICAL_ONLY_COLUMNS` (8 columns)
- `ZERO_VARIANCE_COLUMNS` (5 columns)

---

## 7. Verification Results

- **Analytics Dataset:** [`data/processed/food_delivery_analytics_10k.csv`](file:///c:/FoodDeliveryAnalytics/data/processed/food_delivery_analytics_10k.csv) — **10,000 rows, 50 columns, 0 nulls** (PASSED)
- **ML Dataset:** [`data/processed/food_delivery_ml_10k.csv`](file:///c:/FoodDeliveryAnalytics/data/processed/food_delivery_ml_10k.csv) — **8,520 rows, 27 columns, 0 nulls** (PASSED)
- **Source Dataset:** [`data/processed/food_delivery_10k.csv`](file:///c:/FoodDeliveryAnalytics/data/processed/food_delivery_10k.csv) remains **100% unmodified** (PASSED)
- **Model Training:** **0 models trained** (PASSED)
