# Phase 3 Machine Learning Dataset Quality Assessment Report
## Food Delivery Analytics: Delivery Performance and Delay Prediction

**Date:** 2026-10-03  
**Phase:** 3 — ML Dataset Final Quality Assessment & Feature Readiness  
**Dataset Assessed:** [`data/processed/food_delivery_ml_10k.csv`](file:///c:/FoodDeliveryAnalytics/data/processed/food_delivery_ml_10k.csv)  
**Row Count:** 8,520 rows (Completed Deliveries: `Order_Status == 'Delivered'`)  
**Column Count:** 27 columns (26 ML Features + 1 Target `Is_Delayed_TARGET`)  

---

## 1. Executive Summary

This report presents a thorough quality assessment of the Phase 3 Machine Learning Dataset [`data/processed/food_delivery_ml_10k.csv`](file:///c:/FoodDeliveryAnalytics/data/processed/food_delivery_ml_10k.csv). The dataset was audited across target distribution, numerical integrity, categorical cardinality, temporal validity, leakage isolation, and feature-target relationships.

### Assessment Summary Table
| Dimension | Audit Status | Key Metric / Observation |
|---|---|---|
| **Target Distribution** | ✅ Verified | 6,453 On-Time (75.74%) vs 2,067 Delayed (24.26%) |
| **Class Imbalance** | ⚠️ Mild Imbalance | 3.122 : 1 majority-to-minority ratio |
| **Missing Values** | ✅ 0 Nulls | 0 missing values across all 27 columns |
| **Constant Features** | ✅ None | All numerical & categorical features have $>1$ unique value |
| **Extreme Outliers** | ✅ Managed | $<0.2\%$ distance outliers; geo-coordinate clusters match city geography |
| **Target Leakage** | ✅ 0 Leakage | 100% post-delivery & duration-derived features isolated |
| **High-Cardinality IDs** | ✅ 0 Identifiers | All pure IDs (`Order_ID`, `User_ID`, `Driver_ID`, `Restaurant_ID`) removed |

---

## 2. Target Variable Assessment

- **Primary Target Variable:** `Is_Delayed_TARGET` ($1 = \text{Delayed} > 45\text{ min}$, $0 = \text{On-Time}$).
- **Target Row Subset:** 8,520 completed deliveries (`Order_Status == 'Delivered'`).

### Target Value Counts & Percentages

| Target Class | Description | Count | Percentage |
|---|---|---|---|
| **`0`** | On-Time Delivery ($\le 45$ min) | 6,453 | **75.739%** |
| **`1`** | Delayed Delivery ($> 45$ min) | 2,067 | **24.261%** |
| **Total** | Completed Deliveries | 8,520 | **100.000%** |

### Class Imbalance Analysis
- **Class Imbalance Ratio:** **3.122 : 1** (Majority On-Time to Minority Delayed).
- **Imbalance Assessment:** Mild-to-moderate class imbalance. 
- **Modeling Recommendations:**
  1. Do NOT rely on raw Classification Accuracy as the evaluation metric (a naive majority classifier gets ~75.7% accuracy).
  2. Primary evaluation metrics must be **PR-AUC (Precision-Recall Area Under Curve)**, **ROC-AUC**, **$F_1$-Score**, and **Recall for Class 1 (Delayed)**.
  3. Set `scale_pos_weight ≈ 3.12` in Gradient Boosted Trees (XGBoost / LightGBM) or `class_weight='balanced'` in Random Forest / Logistic Regression. Oversampling (SMOTE) is optional and likely unnecessary given the mild 76/24 split.

---

## 3. Numerical Features Assessment

The ML dataset contains 18 numerical columns (9 continuous floats, 4 discrete integers, 5 binary flags). All 18 columns contain **0 missing values**.

### Summary Statistics & Distribution Audit Table

| Feature Name | Data Type | Nulls | Unique | Min | Max | Mean | Median | Std Dev | Outliers (1.5×IQR) | Outlier % |
|---|---|---|---|---|---|---|---|---|---|---|
| `Quantity` | `int64` | 0 | 5 | 1.0000 | 5.0000 | 3.0011 | 3.0000 | 1.4118 | 0 | 0.00% |
| `Total_Price` | `float64` | 0 | 7,532 | 30.1700 | 749.8500 | 268.7830 | 234.5700 | 170.4930 | 0 | 0.00% |
| `Price_Per_Item` | `float64` | 0 | 6,115 | 30.0000 | 149.9900 | 89.6098 | 89.3050 | 34.8069 | 0 | 0.00% |
| `Is_Large_Order` | `int64` | 0 | 2 | 0.0000 | 1.0000 | 0.4008 | 0.0000 | 0.4901 | 0 | 0.00% |
| `Delivery_Distance_km` | `float64` | 0 | 8,520 | 0.0354 | 5.3491 | 2.1523 | 2.0994 | 1.0376 | 4 | 0.05% |
| `Driver_To_Restaurant_km` | `float64` | 0 | 8,516 | 0.0387 | 5.4861 | 2.1604 | 2.1128 | 1.0391 | 3 | 0.04% |
| `Total_Trip_km` | `float64` | 0 | 8,516 | 0.2110 | 9.6056 | 4.3127 | 4.2007 | 1.5530 | 16 | 0.19% |
| `Restaurant_Lat` | `float64` | 0 | 8,518 | 27.1609 | 31.2201 | 30.1180 | 30.5872 | 1.2733 | 1,222 | 14.34%* |
| `Restaurant_Lon` | `float64` | 0 | 8,520 | 29.8988 | 31.5220 | 31.0630 | 31.2102 | 0.4887 | 1,211 | 14.21%* |
| `Customer_Lat` | `float64` | 0 | 8,519 | 27.1609 | 31.2201 | 30.1178 | 30.5860 | 1.2731 | 1,222 | 14.34%* |
| `Customer_Lon` | `float64` | 0 | 8,519 | 29.8987 | 31.5220 | 31.0628 | 31.2095 | 0.4885 | 1,211 | 14.21%* |
| `Driver_Lat` | `float64` | 0 | 8,520 | 27.1609 | 31.2201 | 30.1180 | 30.5863 | 1.2733 | 1,222 | 14.34%* |
| `Driver_Lon` | `float64` | 0 | 8,518 | 29.8987 | 31.5220 | 31.0625 | 31.2091 | 0.4885 | 1,211 | 14.21%* |
| `Order_Hour` | `int64` | 0 | 24 | 0.0000 | 23.0000 | 11.4969 | 12.0000 | 6.9044 | 0 | 0.00% |
| `Order_DayOfWeek` | `int64` | 0 | 7 | 0.0000 | 6.0000 | 3.0282 | 3.0000 | 2.0556 | 0 | 0.00% |
| `Is_Weekend` | `int64` | 0 | 2 | 0.0000 | 1.0000 | 0.3001 | 0.0000 | 0.4583 | 0 | 0.00% |
| `Is_RushHour` | `int64` | 0 | 2 | 0.0000 | 1.0000 | 0.2880 | 0.0000 | 0.4529 | 0 | 0.00% |
| `Traffic_Level_Enc` | `int64` | 0 | 3 | 0.0000 | 2.0000 | 0.8399 | 1.0000 | 0.8489 | 0 | 0.00% |

*\*Note on Geo-Coordinates:* The 14.2% outlier rate flagged by the standard $1.5 \times \text{IQR}$ rule for latitude/longitude is an artifact of multi-city geography. The dataset covers 7 distinct Egyptian cities spanning latitudes 27.16°N (Assiut) to 31.22°N (Alexandria). These are natural geographic clusters, not erroneous data points.

---

## 4. Categorical Features Assessment

The ML dataset contains **8 categorical string columns**. All 8 columns have **0 missing values**.

### Category Cardinality & Frequency Audit Table

| Feature Name | Dtype | Unique | Category Counts & Percentages | Rare Categories (<5%) | Status |
|---|---|---|---|---|---|
| `City` | `str` | 7 | Zagazig (14.6%), Cairo (14.4%), Assiut (14.3%), Tanta (14.2%), Alexandria (14.2%), Giza (14.2%), Mansoura (14.0%) | None | Balanced (Ready) |
| `Item_Name` | `str` | 9 | Burger (11.6%), Pizza (11.4%), Shawarma (11.4%), Salad (11.3%), Koshary (11.3%), Pasta (11.2%), Sandwich (10.9%), Fried Chicken (10.8%), Sushi (10.3%) | None | Balanced (Ready) |
| `Payment_Method` | `str` | 3 | Wallet (33.6%), Credit Card (33.5%), Cash (32.9%) | None | Balanced (Ready) |
| `Driver_Vehicle` | `str` | 3 | Bicycle (33.6%), Motorbike (33.5%), Car (33.0%) | None | Balanced (Ready) |
| `Traffic_Level` | `str` | 3 | Low (45.3%), High (29.3%), Medium (25.4%) | None | Balanced (Ready) |
| `Time_Of_Day_Segment` | `str` | 6 | Afternoon (21.1%), Late Night (20.8%), Evening (16.7%), Early Morning (16.6%), Morning (12.5%), Night (12.3%) | None | Balanced (Ready) |
| `Order_Value_Tier` | `str` | 4 | Standard (49.1%), Premium (23.0%), Budget (15.6%), Luxury (12.3%) | None | Balanced (Ready) |
| `Distance_Bin` | `str` | 4 | Medium [1-3km] (62.4%), Long [3-5km] (22.5%), Short [<1km] (14.9%), Very Long [>5km] (0.13%) | `Very Long (>5km)` ($N=11, 0.13\%$) | Rare Category Present |

### Rare Category Handling Recommendation
`Distance_Bin` contains a rare category: `Very Long (>5km)` with 11 instances ($0.13\%$). 
- *Recommendation:* Keep as an ordinal tier or merge into `Long (3-5km)` during one-hot encoding if tree-split instability occurs.

---

## 5. Datetime & Derived Temporal Features Audit

- **Explicit Datetime Columns:** **0** (All raw datetime strings like `Order_Time` and `Delivery_Time` have been removed).
- **Derived Temporal Features Present:** 5 pre-order features (`Order_Hour`, `Order_DayOfWeek`, `Is_Weekend`, `Is_RushHour`, `Time_Of_Day_Segment`).
- **Temporal Integrity Confirmation:** Verified 100% pre-order. No post-delivery completion timestamps or execution durations are encoded.

---

## 6. Final Leakage Audit

A secondary automated regex audit was performed on all 27 column names searching for post-outcome terms (`time`, `duration`, `speed`, `status`, `delivered`, `cancelled`).

- **Audit Output:** Only `Time_Of_Day_Segment` matched the search term.
- **Verification:** `Time_Of_Day_Segment` is derived strictly from `Order_Hour` at order placement time.
- **Leakage Status:** **0 Target Leakage Columns Present.**

---

## 7. Feature-Target Relationships (Exploratory Analysis)

### Pearson Linear Correlation with `Is_Delayed_TARGET`

| Numerical Feature | Correlation ($r$) | Direction | Signal Assessment |
|---|---|---|---|
| `Is_Large_Order` | $+0.0277$ | Positive | Slightly higher delay probability for large quantity orders |
| `Is_RushHour` | $-0.0256$ | Negative | Simulated feature artifact |
| `Quantity` | $+0.0227$ | Positive | Larger items require more prep time |
| `Price_Per_Item` | $-0.0189$ | Negative | Weak linear signal |
| `Delivery_Distance_km` | $-0.0145$ | Negative | Near-zero linear correlation (simulation characteristic) |
| `Order_Hour` | $-0.0144$ | Negative | Diurnal variation |
| `Total_Trip_km` | $-0.0130$ | Negative | Weak linear signal |
| `Is_Weekend` | $-0.0098$ | Negative | Weak linear signal |
| `Traffic_Level_Enc` | $-0.0084$ | Negative | Near-zero linear correlation (simulation characteristic) |
| `Driver_To_Restaurant_km` | $-0.0050$ | Negative | Weak linear signal |
| `Total_Price` | $+0.0048$ | Positive | Weak linear signal |

### Categorical Delay Rates (% Delayed)

| Categorical Feature | Category Breakdowns (% Delayed) | Delay Rate Range |
|---|---|---|
| `City` | Zagazig (24.66%), Tanta (24.48%), Assiut (24.47%), Mansoura (24.35%), Giza (24.07%), Cairo (24.00%), Alexandria (23.78%) | 23.78% – 24.66% |
| `Item_Name` | Shawarma (25.54%), Pizza (25.44%), Pasta (24.97%), Sushi (24.60%), Koshary (23.98%), Burger (23.76%), Salad (23.52%), Sandwich (23.52%), Fried Chicken (22.97%) | 22.97% – 25.54% |
| `Driver_Vehicle` | Car (25.33%), Bicycle (24.27%), Motorbike (23.19%) | 23.19% – 25.33% |
| `Traffic_Level` | Medium (25.90%), Low (24.14%), High (23.03%) | 23.03% – 25.90% |
| `Distance_Bin` | Very Long (36.36%*), Short (25.28%), Medium (24.18%), Long (23.74%) | 23.74% – 36.36% |

### Critical Modeling Principle: Non-Linearity
As established in Phase 1 and emphasized in project directives, **low linear correlation does NOT justify feature removal**. Non-linear tree algorithms (Decision Trees, Random Forests, XGBoost, LightGBM) evaluate non-linear feature splits and higher-order feature interactions (e.g. `Distance_Bin` $\times$ `Traffic_Level_Enc` $\times$ `Order_Hour`). All 26 pre-order features are retained based on domain validity and temporal safety.

---

## 8. Final Feature Readiness & Preprocessing Blueprint

### A. Features Ready for Modeling (14 Features — Direct Input for Tree Models)
- **Discrete & Continuous Numerics:** `Quantity`, `Total_Price`, `Price_Per_Item`, `Delivery_Distance_km`, `Driver_To_Restaurant_km`, `Total_Trip_km`, `Order_Hour`, `Order_DayOfWeek`.
- **Binary Flags:** `Is_Weekend`, `Is_RushHour`, `Is_Large_Order`, `Is_High_Traffic`, `Traffic_Level_Enc`, `Is_Weekday`.

---

### B. Features Requiring Encoding (8 Categorical Features)
1. **Nominal One-Hot Encoding (for non-ordinal categories):**
   - `City` (7 categories)
   - `Item_Name` (9 categories)
   - `Payment_Method` (3 categories)
   - `Driver_Vehicle` (3 categories)
   - `Traffic_Level` (3 categories)
2. **Ordinal Encoding (for ordered categories):**
   - `Time_Of_Day_Segment` (Late Night=0, Early Morning=1, Morning=2, Afternoon=3, Evening=4, Night=5)
   - `Distance_Bin` (Short=0, Medium=1, Long=2, Very Long=3)
   - `Order_Value_Tier` (Budget=0, Standard=1, Premium=2, Luxury=3)

---

### C. Features Requiring Scaling / Transformation (For Linear / Distance-Based Models Only)
- **Log Transformation:** `Total_Price`, `Delivery_Distance_km`, `Total_Trip_km` (to handle right-skewness for Logistic Regression or Neural Networks).
- **Standard Scaling:** All numerical features & spatial coordinates (`Restaurant_Lat`, `Restaurant_Lon`, etc.) required for Logistic Regression, SVM, or KNN. (Not required for tree-based models).

---

### D. Remaining Risks & Modeling Considerations
1. **Synthetic Independence:** Features in this dataset have independent uniform distributions. Tree ensemble algorithms (Random Forest / LightGBM) are recommended to capture subtle multi-feature interactions.
2. **Evaluation Metric Selection:** Do NOT use raw Accuracy. Evaluate models using **PR-AUC**, **ROC-AUC**, and **$F_1$-Score**.
3. **Class Weight Adjustment:** Use `scale_pos_weight = 3.12` in XGBoost/LightGBM or `class_weight='balanced'` in Random Forest to handle the 76/24 majority/minority balance.

---

## 9. Next Steps

- **Dataset File:** [`data/processed/food_delivery_ml_10k.csv`](file:///c:/FoodDeliveryAnalytics/data/processed/food_delivery_ml_10k.csv) is certified 100% clean, leakage-free, and ready for model prototyping.
- **Model Training:** **0 models trained.** Baseline model training will begin in Phase 4.
