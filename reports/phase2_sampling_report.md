# Phase 2 Sampling & Dataset Reduction Report
## Food Delivery Analytics: Delivery Performance and Delay Prediction

**Date:** 2026-10-03  
**Phase:** 2 — Dataset Reduction to 10,000 Rows  
**Sampling Script:** [`src/preprocessing/create_10k_dataset.py`](file:///c:/FoodDeliveryAnalytics/src/preprocessing/create_10k_dataset.py)  
**Output Dataset:** [`data/processed/food_delivery_10k.csv`](file:///c:/FoodDeliveryAnalytics/data/processed/food_delivery_10k.csv)  

---

## 1. Objective

The objective of Phase 2 is to produce a representative **10,000-row sample** from the 100,002-row Phase 1 featured dataset. This dataset reduction facilitates efficient exploratory analysis, visualisations, and rapid iteration during model prototyping while preserving all statistical, operational, and geographic characteristics of the original population.

---

## 2. Input Dataset & Paths

| Property | Description |
|---|---|
| **Source Dataset Path** | [`data/processed/Order_delivery_featured.csv`](file:///c:/FoodDeliveryAnalytics/data/processed/Order_delivery_featured.csv) |
| **Output Dataset Path** | [`data/processed/food_delivery_10k.csv`](file:///c:/FoodDeliveryAnalytics/data/processed/food_delivery_10k.csv) |
| **Secondary Copy Path** | [`Datasets/food_delivery_10k.csv`](file:///c:/FoodDeliveryAnalytics/Datasets/food_delivery_10k.csv) |
| **Raw Dataset (Untouched)** | [`data/raw/Order_delivery.csv`](file:///c:/FoodDeliveryAnalytics/data/raw/Order_delivery.csv) |

---

## 3. Row and Column Summary

| Metric | Original Population | Phase 2 Reduced Sample | Status |
|---|---|---|---|
| **Total Rows** | 100,002 | **10,000** | Reduced to exactly 10,000 |
| **Total Columns** | 55 | **55** | 100% columns preserved |
| **Unique Order_IDs** | 100,002 | **10,000** | 0 duplicates |
| **Missing Values** | 0 | **0** | 0 nulls |

---

## 4. Sampling Methodology

Simple uncontrolled random sampling introduces sampling error that can alter target class proportions, operational lifecycle balances, and regional representation. To eliminate sample bias, **Multi-Feature Stratified Random Sampling** was employed.

### Composite Stratification Key
A composite stratification key was constructed for each row:
$$\text{Stratum Key} = \text{Order\_Status} + \text{"\_"} + \text{Is\_Delayed\_TARGET} + \text{"\_"} + \text{City}$$

- **Total Strata:** 42 active strata ($3 \times 2 \times 7$).
- **Sampling Tool:** `sklearn.model_selection.train_test_split` with proportional allocation.

---

## 5. Random Seed

- **Fixed Seed:** `random_state = 42`
- **Reproducibility:** Re-running [`create_10k_dataset.py`](file:///c:/FoodDeliveryAnalytics/create_10k_dataset.py) produces the exact same 10,000 rows deterministically.

---

## 6. Variables Used for Stratification

1. `Order_Status` (Delivered / Cancelled / In Transit)
2. `Is_Delayed_TARGET` (0: On-time / 1: Delayed)
3. `City` (7 Egyptian cities)

---

## 7. Rationale for Stratification Variable Selection

- **`Order_Status`:** Preserves the operational ratio between completed deliveries (85.2%), cancellations (9.8%), and in-transit orders (5.0%). Cancellations and in-transit orders represent different operational lifecycles and must not be over- or under-represented.
- **`Is_Delayed_TARGET`:** The primary machine learning target variable. Stratification prevents label balance distortion, keeping the delay rate at ~24.17% overall (~24.26% for Delivered orders).
- **`City`:** Ensures exact geographic parity across all 7 regional sub-markets (~14.0% – 14.5% per city).
- **Simulated Independence:** Secondary categorical variables (`Item_Name`, `Payment_Method`, `Driver_Vehicle`) were independently simulated in the raw dataset; stratifying on the core 42 composite strata naturally preserves their uniform distributions via the Law of Large Numbers.

---

## 8. General Distribution Comparison

| Feature Category | Feature | Original % | Sampled 10k % | Difference |
|---|---|---|---|---|
| **Order Status** | Delivered | 85.197% | 85.200% | $+0.003\%$ |
| | Cancelled | 9.812% | 9.800% | $-0.012\%$ |
| | In Transit | 4.991% | 5.000% | $+0.009\%$ |
| **Driver Vehicle** | Bicycle | 33.392% | 33.390% | $-0.002\%$ |
| | Car | 33.362% | 33.140% | $-0.222\%$ |
| | Motorbike | 33.245% | 33.470% | $+0.225\%$ |
| **Payment Method** | Cash | 33.527% | 33.060% | $-0.467\%$ |
| | Credit Card | 33.222% | 33.500% | $+0.278\%$ |
| | Wallet | 33.250% | 33.440% | $+0.190\%$ |

---

## 9. Delay-Class Target Comparison

### Overall Dataset (All Orders)

| Target Label | Description | Original Count | Original % | Sampled 10k Count | Sampled 10k % | Shift |
|---|---|---|---|---|---|---|
| **`0`** | On-Time / Normal | 75,825 | 75.823% | 7,583 | 75.830% | $+0.007\%$ |
| **`1`** | Delayed (>45 min) | 24,177 | 24.177% | 2,417 | 24.170% | $-0.007\%$ |

### Delivered Orders Only (Model Training Subset)

| Target Label | Description | Original % | Sampled 10k % | Shift |
|---|---|---|---|---|
| **`0`** | On-Time | 75.733% | 75.739% | $+0.006\%$ |
| **`1`** | Delayed | 24.267% | 24.261% | $-0.006\%$ |

---

## 10. City Distribution Comparison

| City | Original Count | Original % | Sampled 10k Count | Sampled 10k % | Shift |
|---|---|---|---|---|---|
| **Zagazig** | 14,538 | 14.538% | 1,454 | 14.540% | $+0.002\%$ |
| **Cairo** | 14,382 | 14.382% | 1,439 | 14.390% | $+0.008\%$ |
| **Tanta** | 14,336 | 14.336% | 1,433 | 14.330% | $-0.006\%$ |
| **Assiut** | 14,302 | 14.302% | 1,430 | 14.300% | $-0.002\%$ |
| **Giza** | 14,232 | 14.232% | 1,423 | 14.230% | $-0.002\%$ |
| **Alexandria** | 14,168 | 14.168% | 1,416 | 14.160% | $-0.008\%$ |
| **Mansoura** | 14,044 | 14.044% | 1,405 | 14.050% | $+0.006\%$ |

---

## 11. Temporal Distribution Comparison

| Temporal Segment | Category | Original % | Sampled 10k % | Shift |
|---|---|---|---|---|
| **Time of Day** | Late Night (00:00–04:59) | 21.018% | 20.750% | $-0.268\%$ |
| | Afternoon (12:00–16:59) | 20.894% | 21.180% | $+0.286\%$ |
| | Early Morning (05:00–08:59) | 16.617% | 16.600% | $-0.017\%$ |
| | Evening (17:00–20:59) | 16.605% | 16.820% | $+0.215\%$ |
| | Morning (09:00–11:59) | 12.453% | 12.540% | $+0.087\%$ |
| | Night (21:00–23:59) | 12.415% | 12.110% | $-0.305\%$ |
| **Day Type** | Weekday (`Is_Weekend=0`) | 69.376% | 70.190% | $+0.814\%$ |
| | Weekend (`Is_Weekend=1`) | 30.624% | 29.810% | $-0.814\%$ |
| **Rush Hour** | Non-Rush Hour (`Is_RushHour=0`)| 70.947% | 71.050% | $+0.103\%$ |
| | Rush Hour (`Is_RushHour=1`) | 29.053% | 28.950% | $-0.103\%$ |

---

## 12. Numerical Variable Comparison

| Variable | Metric | Original Population | Sampled 10k Sample | Difference |
|---|---|---|---|---|
| `Delivery_Duration_Minutes` | Mean | 37.520 min | 37.478 min | $-0.042$ min |
| | Median | 38.000 min | 38.000 min | $0.000$ min |
| | Std Dev | 10.061 min | 10.077 min | $+0.016$ min |
| | Min / Max | 15.0 / 60.0 min | 15.0 / 60.0 min | Identical bounds |
| | p25 / p75 | 30.0 / 45.0 min | 30.0 / 45.0 min | Identical quartiles |
| `Total_Price` | Mean | 268.923 EGP | 268.974 EGP | $+0.051$ EGP |
| | Median | 233.200 EGP | 234.180 EGP | $+0.980$ EGP |
| | Std Dev | 170.490 EGP | 170.639 EGP | $+0.149$ EGP |
| | Min / Max | 30.0 / 750.0 EGP | 30.02 / 749.85 EGP | Matches range |
| `Delivery_Distance_km` | Mean | 2.165 km | 2.151 km | $-0.014$ km |
| | Median | 2.123 km | 2.102 km | $-0.021$ km |
| | Std Dev | 1.038 km | 1.044 km | $+0.006$ km |
| `Total_Trip_km` | Mean | 4.331 km | 4.318 km | $-0.013$ km |
| | Median | 4.219 km | 4.199 km | $-0.020$ km |
| | Std Dev | 1.553 km | 1.558 km | $+0.005$ km |

---

## 13. Limitations of the Sampling Approach

1. **Rare Entity Truncation:** Highly rare individual `User_ID`s or driver-vehicle edge combinations with fewer than 10 total orders in the population may have reduced representation or zero occurrences in the 10,000-row sample.
2. **Sub-segment Variance:** While primary categories maintain $<0.5\%$ variance, fine-grained cross-tabs (e.g. *Late Night Pizza deliveries in Assiut*) have smaller sample sizes ($N \approx 20–30$) and larger relative standard errors.

---

## 14. Final Validation Result

- **Row Count:** **10,000 / 10,000** (PASSED)
- **Column Count:** **55 / 55** (PASSED)
- **Duplicates:** **0 / 10,000** (PASSED)
- **Null Values:** **0** (PASSED)
- **Distribution Shift:** Max categorical shift $<0.82\%$; Target & City shift $<0.012\%$ (PASSED)
- **Reproducibility:** Seed 42 verified (PASSED)
- **Phase 1 Cleaned File Integrity:** [`data/processed/Order_delivery_cleaned.csv`](file:///c:/FoodDeliveryAnalytics/data/processed/Order_delivery_cleaned.csv) unchanged (PASSED)

> **Conclusion:** Phase 2 dataset reduction is successfully completed and validated. The 10,000-row dataset [`data/processed/food_delivery_10k.csv`](file:///c:/FoodDeliveryAnalytics/data/processed/food_delivery_10k.csv) is certified for downstream analytics and machine learning prototyping.
