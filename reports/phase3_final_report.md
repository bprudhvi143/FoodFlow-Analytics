# Phase 3 Final Data Preparation & Preprocessing Pipeline Report
## Food Delivery Analytics: Delivery Performance and Delay Prediction

**Date:** 2026-10-03  
**Phase:** 3 — Complete Phase 3 Finalization  
**Preprocessing Module:** [`src/ml/preprocessing.py`](file:///c:/FoodDeliveryAnalytics/src/ml/preprocessing.py)  
**Validation Suite:** [`src/ml/validate_preprocessing.py`](file:///c:/FoodDeliveryAnalytics/src/ml/validate_preprocessing.py)  

---

## 1. Executive Summary

Phase 3 is finalized with the completion of a leakage-free, fully reproducible machine learning preprocessing pipeline and dataset architecture. 

Starting from the Phase 2 representative modeling dataset ([`food_delivery_10k.csv`](file:///c:/FoodDeliveryAnalytics/data/processed/food_delivery_10k.csv)), two distinct datasets were engineered: an **Analytics Dataset** for operational reporting and dashboarding, and a **Machine Learning Dataset** for delivery delay prediction.

All preprocessing transformations (`OneHotEncoder`, `OrdinalEncoder`, `StandardScaler`) are encapsulated in an `sklearn.compose.ColumnTransformer` pipeline fitted **strictly on training data** post train/test split, ensuring zero data leakage.

---

## 2. Dataset Architecture & Inventory

| Dataset | Workspace Path | Rows | Columns | Purpose & Scope |
|---|---|---|---|---|
| **Original 10k Sample** | [`data/processed/food_delivery_10k.csv`](file:///c:/FoodDeliveryAnalytics/data/processed/food_delivery_10k.csv) | 10,000 | 55 | Phase 2 representative modeling population (100% untouched). |
| **Analytics Dataset** | [`data/processed/food_delivery_analytics_10k.csv`](file:///c:/FoodDeliveryAnalytics/data/processed/food_delivery_analytics_10k.csv) | 10,000 | 50 | Operational reporting, SLA benchmarking, and dashboard visualisations across all order statuses (Delivered, Cancelled, In Transit). |
| **Machine Learning Dataset** | [`data/processed/food_delivery_ml_10k.csv`](file:///c:/FoodDeliveryAnalytics/data/processed/food_delivery_ml_10k.csv) | 8,520 | 27 | Completed delivery delay prediction dataset (26 safe pre-order features + 1 target `Is_Delayed_TARGET`). |

---

## 3. Target Variable & Class Distribution

- **Primary Target Column:** `Is_Delayed_TARGET` ($1 = \text{Delayed} > 45\text{ min}$, $0 = \text{On-Time}$).
- **Population:** 8,520 completed deliveries (`Order_Status == 'Delivered'`).
- **Class Breakdown:**
  - **On-Time (`0`):** 6,453 orders (**75.74%**)
  - **Delayed (`1`):** 2,067 orders (**24.26%**)
- **Class Imbalance Ratio:** **3.122 : 1** (Majority On-Time : Minority Delayed).
- **Stratified Split:** 80/20 train/test split yields **6,816 train samples** (24.27% delayed) and **1,704 test samples** (24.24% delayed).

---

## 4. Final Machine Learning Feature Set (26 Features)

### A. Numerical Features (18)
`Quantity`, `Total_Price`, `Price_Per_Item`, `Is_Large_Order`, `Delivery_Distance_km`, `Driver_To_Restaurant_km`, `Total_Trip_km`, `Restaurant_Lat`, `Restaurant_Lon`, `Customer_Lat`, `Customer_Lon`, `Driver_Lat`, `Driver_Lon`, `Order_Hour`, `Order_DayOfWeek`, `Is_Weekend`, `Is_RushHour`, `Traffic_Level_Enc`.

### B. Nominal Categorical Features (5 — One-Hot Encoded)
- `City` (7 categories $\rightarrow$ 6 dummy columns)
- `Item_Name` (9 categories $\rightarrow$ 8 dummy columns)
- `Payment_Method` (3 categories $\rightarrow$ 2 dummy columns)
- `Driver_Vehicle` (3 categories $\rightarrow$ 2 dummy columns)
- `Traffic_Level` (3 categories $\rightarrow$ 2 dummy columns)

### C. Ordinal Categorical Features (3 — Ordinal Encoded)
- `Time_Of_Day_Segment` (Late Night=0, Early Morning=1, Morning=2, Afternoon=3, Evening=4, Night=5)
- `Distance_Bin` (Short=0, Medium=1, Long=2, Very Long=3)
- `Order_Value_Tier` (Budget=0, Standard=1, Premium=2, Luxury=3)

---

## 5. Excluded Leakage & Identifier Columns (28 Columns Excluded)

### Excluded Leakage Columns (8)
1. `Delivery_Time` (Outcome completion timestamp)
2. `Delivery_Duration_Minutes` (Continuous duration target)
3. `Is_Delivered` (Post-delivery status flag)
4. `Is_Cancelled` (Post-delivery cancellation flag)
5. `Is_InTransit` (Active delivery status flag)
6. `Order_To_Delivery_Minutes_TARGET` (Computed duration metric)
7. `Delivery_Speed_kmh_ANALYTICAL` (Post-delivery metric using duration)
8. `Distance_Per_Minute_ANALYTICAL` (Post-delivery metric using duration)

### Excluded Pure Identifiers (4)
1. `Order_ID` (Primary key sequence)
2. `User_ID` (High-cardinality customer ID)
3. `Restaurant_ID` (High-cardinality restaurant ID)
4. `Driver_ID` (High-cardinality driver ID)

### Excluded Analytics-Only, Snapshot & Zero-Variance Columns (16)
`Order_Time`, `Order_Date`, `Order_DayName`, `Order_DayOfMonth`, `Is_Weekday`, `Driver_Availability`, `Driver_Online`, `Order_Status`, `Restaurant_Geo_Imputed`, `Customer_Geo_Imputed`, `Driver_Geo_Imputed`, `Same_Location_Flag`, `Order_Month`, `Delay_Minutes_TARGET`, `Duration_Bin_TARGET`, `Is_High_Traffic`.

---

## 6. Preprocessing Strategy & Pipeline Architecture

The preprocessing pipeline is built using `sklearn.compose.ColumnTransformer` inside [`src/ml/preprocessing.py`](file:///c:/FoodDeliveryAnalytics/src/ml/preprocessing.py):

```
                                  ┌──────────────────────────┐
                                  │   food_delivery_ml_10k   │
                                  └────────────┬─────────────┘
                                               │
                                      train_test_split
                                     (test_size=0.20, seed=42)
                                               │
                      ┌────────────────────────┴────────────────────────┐
                      ▼                                                 ▼
             X_train (6,816 rows)                              X_test (1,704 rows)
                      │                                                 │
            fit_transform()                                        transform()
                      │                                                 │
                      ▼                                                 ▼
          ┌───────────────────────┐                         ┌───────────────────────┐
          │ ColumnTransformer     │                         │ ColumnTransformer     │
          │                       │                         │                       │
          │ • Num: Passthrough/   │                         │ (Fitted on X_train)   │
          │   StandardScaler      │                         │                       │
          │ • Nom: OneHotEncoder  │                         │                       │
          │ • Ord: OrdinalEncoder │                         │                       │
          └───────────┬───────────┘                         └───────────┬───────────┘
                      │                                                 │
                      ▼                                                 ▼
           X_train_df (41 cols)                              X_test_df (41 cols)
```

- **Encoded Feature Dimensionality:** 26 input features $\rightarrow$ **41 encoded numeric columns**.
- **Data Leakage Guarantee:** `preprocessor.fit_transform()` is called **only on `X_train`**. `X_test` is transformed using the fitted training pipeline.

---

## 7. Automated Validation Results (`src/ml/validate_preprocessing.py`)

- **Check 1 (Train/Test Split Dimensions):** PASSED (6,816 train / 1,704 test = 8,520 total).
- **Check 2 (Stratified Target Distribution):** PASSED (Train: 24.27% delayed, Test: 24.24% delayed).
- **Check 3 (Feature Taxonomies):** PASSED (18 Numerical, 5 Nominal, 3 Ordinal = 26 features).
- **Check 4 (Zero Target Leakage):** PASSED (0 leakage columns present in X_train/X_test).
- **Check 5 (Zero Identifiers):** PASSED (0 identifier columns present in X_train/X_test).
- **Check 6 (Fitting Isolation):** PASSED (Preprocessor fitted strictly on X_train).
- **Check 7 (Feature Names Preserved):** PASSED (41 encoded columns output with feature names).
- **Check 8 (Reproducibility):** PASSED (100% deterministic with `random_state=42`).

---

## 8. Remaining Concerns & Recommendations for Phase 4

1. **Evaluation Metric Selection:** Plain Accuracy is misleading (~75.7% baseline for majority classifier). Evaluate Phase 4 models using **PR-AUC**, **ROC-AUC**, and **$F_1$-score**.
2. **Model Class Weight Tuning:** Use `scale_pos_weight = 3.12` in XGBoost/LightGBM or `class_weight='balanced'` in Random Forest to handle the 76/24 class split.
3. **Synthetic Independence:** Variables in this dataset were synthetically generated. Tree ensembles (Random Forest, Gradient Boosted Trees) are recommended over linear models to capture non-linear feature interactions.

---

## 9. Conclusion

Phase 3 is officially complete. All datasets, feature configurations, pipeline scripts, validation checks, and reports have been generated and verified.

- **Dataset State:** All datasets are saved in `data/processed/`.
- **Model Training:** **0 models trained.** Phase 4 model training is ready to commence upon request.
