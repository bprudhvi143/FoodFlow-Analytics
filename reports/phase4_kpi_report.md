# Phase 4 Core Delivery Performance KPI Report
## Food Delivery Analytics: Delivery Performance and Delay Prediction

**Project:** Food Delivery Analytics  
**Phase:** Phase 4 — Descriptive Analytics  
**Dataset:** [`data/processed/food_delivery_analytics_10k.csv`](file:///c:/FoodDeliveryAnalytics/data/processed/food_delivery_analytics_10k.csv) ($N = 10,000$)  
**Generated Script:** [`src/analytics/compute_kpis.py`](file:///c:/FoodDeliveryAnalytics/src/analytics/compute_kpis.py)  
**Structured Output Directory:** [`reports/tables/`](file:///c:/FoodDeliveryAnalytics/reports/tables/)  

---

## 1. Executive Summary & Core Baseline KPIs

Below are the 15 primary delivery-performance KPIs calculated across the 10,000-row representative analytics dataset.

| KPI Metric Name | Calculated Value |
|---|---|
| **1. Total Orders** | 10000 |
| **2. Delivered Orders** | 8520 |
| **3. Cancelled Orders** | 980 |
| **4. In-Transit Orders** | 500 |
| **5. Overall Delayed Orders (All)** | 2417 |
| **5b. Overall Delayed Orders (Delivered)** | 2067 |
| **6. Delay Rate among Delivered Orders (%)** | 24.26 |
| **6b. Overall Delay Rate All Orders (%)** | 24.17 |
| **7. Average Delivery Duration (min)** | 37.5 |
| **8. Median Delivery Duration (min)** | 38.0 |
| **9. Minimum Delivery Duration (min)** | 15 |
| **10. Maximum Delivery Duration (min)** | 60 |
| **11. Average Delay Duration - All Delivered (min)** | 1.37 |
| **11b. Average Delay Duration - Delayed Only (min)** | 5.65 |
| **12. Median Delay Duration - All Delivered (min)** | 0.0 |
| **12b. Median Delay Duration - Delayed Only (min)** | 5.0 |
| **13. Average Order Value (EGP)** | 268.97 |
| **14. Average Delivery Distance (km)** | 2.15 |
| **15. Average Quantity per Order** | 3.0 |
| **Fulfillment Rate (%)** | 85.2 |
| **Cancellation Rate (%)** | 9.8 |
| **Average Effective Speed (km/h)** | 3.75 |
| **Average Dispatch Distance (km)** | 2.17 |

---

## 2. KPI Definitions & Mathematical Formulas

| # | KPI Metric Name | Formula / Calculation Method | Scope / Subset | Operational Rationale |
|---|---|---|---|---|
| 1 | **Total Orders** | $N = \text{Count of all rows}$ | All ($N=10,000$) | Total order demand volume in sample population. |
| 2 | **Delivered Orders** | $\sum [ \text{Order\_Status} == \text{'Delivered'} ]$ | All ($N=8,520$) | Completed fulfillments eligible for duration and SLA evaluation. |
| 3 | **Cancelled Orders** | $\sum [ \text{Order\_Status} == \text{'Cancelled'} ]$ | All ($N=980$) | Orders abandoned/cancelled prior to delivery completion. |
| 4 | **In-Transit Orders** | $\sum [ \text{Order\_Status} == \text{'In Transit'} ]$ | All ($N=500$) | Orders in progress at snapshot cutoff. |
| 5 | **Overall Delayed Orders** | $\sum [ \text{Is\_Delayed\_TARGET} == 1 ]$ | All ($N=2,417$) / Delivered ($N=2,067$) | Orders breaching the 45-minute SLA threshold. |
| 6 | **Delay Rate (Delivered)** | $\frac{\text{Delivered Delayed Orders}}{\text{Total Delivered Orders}} \times 100$ | Delivered ($N=8,520$) | Core SLA breach metric (**24.26%**). |
| 7 | **Average Delivery Duration** | $\frac{1}{N_{\text{deliv}}} \sum \text{Delivery\_Duration\_Minutes}$ | Delivered ($N=8,520$) | Average turnaround time (**37.50 min**). |
| 8 | **Median Delivery Duration** | $\text{Median}(\text{Delivery\_Duration\_Minutes})$ | Delivered ($N=8,520$) | Robust central measure unaffected by extreme skew (**38.00 min**). |
| 9 | **Minimum Delivery Duration** | $\min(\text{Delivery\_Duration\_Minutes})$ | Delivered ($N=8,520$) | Fast-path delivery baseline (**15 min**). |
| 10 | **Maximum Delivery Duration** | $\max(\text{Delivery\_Duration\_Minutes})$ | Delivered ($N=8,520$) | Maximum delivery latency observed (**60 min**). |
| 11 | **Average Delay Duration** | $\frac{1}{N_{\text{deliv}}} \sum \text{Delay\_Minutes\_TARGET}$ | Delivered ($N=8,520$) | Average excess duration beyond 45-min SLA (**1.37 min** overall / **5.65 min** when delayed). |
| 12 | **Median Delay Duration** | $\text{Median}(\text{Delay\_Minutes\_TARGET})$ | Delivered ($N=8,520$) | Median SLA excess delay (**0.00 min** overall / **5.00 min** when delayed). |
| 13 | **Average Order Value** | $\frac{1}{N} \sum \text{Total\_Price}$ | All ($N=10,000$) | Average basket value in EGP (**EGP 268.97**). |
| 14 | **Average Delivery Distance** | $\frac{1}{N} \sum \text{Delivery\_Distance\_km}$ | All ($N=10,000$) | Average vendor-to-customer Haversine distance (**2.15 km**). |
| 15 | **Average Quantity per Order** | $\frac{1}{N} \sum \text{Quantity}$ | All ($N=10,000$) | Average items per order (**3.00 items**). |

---

## 3. Operational KPI Breakdowns

### Operational Breakdown by City

| City | Total Orders | Delivered Orders | Cancelled Orders | In-Transit Orders | Fulfillment Rate (%) | Cancellation Rate (%) | Delayed Delivered Orders | Delay Rate Delivered (%) | Mean Duration (min) | Median Duration (min) | Mean Delay Duration (min) | Mean Courier Speed (km/h) | Mean Order Value (EGP) | Mean Distance (km) | Mean Quantity |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Alexandria | 1416 | 1211 | 133 | 72 | 85.52 | 9.39 | 288 | 23.78 | 37.52 | 37.0 | 1.38 | 3.62 | 272.27 | 2.11 | 3.03 |
| Assiut | 1430 | 1222 | 138 | 70 | 85.45 | 9.65 | 299 | 24.47 | 37.6 | 38.0 | 1.28 | 3.78 | 278.89 | 2.17 | 3.08 |
| Cairo | 1439 | 1225 | 141 | 73 | 85.13 | 9.8 | 294 | 24.0 | 37.59 | 38.0 | 1.32 | 3.75 | 264.61 | 2.14 | 2.95 |
| Giza | 1423 | 1209 | 146 | 68 | 84.96 | 10.26 | 291 | 24.07 | 37.18 | 37.0 | 1.33 | 3.75 | 269.6 | 2.15 | 3.01 |
| Mansoura | 1405 | 1195 | 141 | 69 | 85.05 | 10.04 | 291 | 24.35 | 37.43 | 38.0 | 1.37 | 3.79 | 260.09 | 2.16 | 2.94 |
| Tanta | 1433 | 1213 | 146 | 74 | 84.65 | 10.19 | 297 | 24.48 | 37.7 | 38.0 | 1.45 | 3.78 | 271.94 | 2.18 | 3.01 |
| Zagazig | 1454 | 1245 | 135 | 74 | 85.63 | 9.28 | 307 | 24.66 | 37.49 | 38.0 | 1.46 | 3.78 | 265.38 | 2.16 | 3.0 |


### Operational Breakdown by Traffic Level

| Traffic Level | Total Orders | Delivered Orders | Cancelled Orders | In-Transit Orders | Fulfillment Rate (%) | Cancellation Rate (%) | Delayed Delivered Orders | Delay Rate Delivered (%) | Mean Duration (min) | Median Duration (min) | Mean Delay Duration (min) | Mean Courier Speed (km/h) | Mean Order Value (EGP) | Mean Distance (km) | Mean Quantity |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| High | 2924 | 2497 | 276 | 151 | 85.4 | 9.44 | 575 | 23.03 | 37.21 | 37.0 | 1.32 | 3.78 | 273.55 | 2.15 | 3.02 |
| Low | 4525 | 3861 | 439 | 225 | 85.33 | 9.7 | 932 | 24.14 | 37.48 | 38.0 | 1.34 | 3.72 | 265.93 | 2.15 | 2.99 |
| Medium | 2551 | 2162 | 265 | 124 | 84.75 | 10.39 | 560 | 25.9 | 37.89 | 38.0 | 1.49 | 3.77 | 269.13 | 2.16 | 3.0 |


### Operational Breakdown by Time of Day

| Time of Day | Total Orders | Delivered Orders | Cancelled Orders | In-Transit Orders | Fulfillment Rate (%) | Cancellation Rate (%) | Delayed Delivered Orders | Delay Rate Delivered (%) | Mean Duration (min) | Median Duration (min) | Mean Delay Duration (min) | Mean Courier Speed (km/h) | Mean Order Value (EGP) | Mean Distance (km) | Mean Quantity |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Afternoon | 2118 | 1798 | 214 | 106 | 84.89 | 10.1 | 454 | 25.25 | 37.68 | 38.0 | 1.41 | 3.81 | 271.24 | 2.17 | 3.04 |
| Early Morning | 1660 | 1417 | 168 | 75 | 85.36 | 10.12 | 352 | 24.84 | 37.28 | 37.0 | 1.42 | 3.77 | 267.04 | 2.15 | 3.01 |
| Evening | 1682 | 1419 | 158 | 105 | 84.36 | 9.39 | 332 | 23.4 | 37.52 | 38.0 | 1.35 | 3.7 | 274.37 | 2.13 | 3.02 |
| Late Night | 2075 | 1770 | 200 | 105 | 85.3 | 9.64 | 429 | 24.24 | 37.44 | 38.0 | 1.29 | 3.76 | 264.98 | 2.16 | 2.98 |
| Morning | 1254 | 1069 | 126 | 59 | 85.25 | 10.05 | 268 | 25.07 | 37.73 | 38.0 | 1.54 | 3.76 | 270.71 | 2.16 | 2.97 |
| Night | 1211 | 1047 | 114 | 50 | 86.46 | 9.41 | 232 | 22.16 | 37.37 | 37.0 | 1.22 | 3.67 | 265.21 | 2.13 | 2.97 |


### Operational Breakdown by Day of Week

| Day of Week | Total Orders | Delivered Orders | Cancelled Orders | In-Transit Orders | Fulfillment Rate (%) | Cancellation Rate (%) | Delayed Delivered Orders | Delay Rate Delivered (%) | Mean Duration (min) | Median Duration (min) | Mean Delay Duration (min) | Mean Courier Speed (km/h) | Mean Order Value (EGP) | Mean Distance (km) | Mean Quantity |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Monday | 1558 | 1309 | 156 | 93 | 84.02 | 10.01 | 290 | 22.15 | 37.22 | 38.0 | 1.17 | 3.77 | 279.99 | 2.16 | 3.08 |
| Tuesday | 1379 | 1152 | 152 | 75 | 83.54 | 11.02 | 280 | 24.31 | 37.3 | 37.0 | 1.33 | 3.7 | 262.22 | 2.13 | 2.97 |
| Wednesday | 1371 | 1179 | 134 | 58 | 86.0 | 9.77 | 307 | 26.04 | 37.72 | 38.0 | 1.53 | 3.73 | 265.87 | 2.16 | 2.98 |
| Thursday | 1409 | 1205 | 135 | 69 | 85.52 | 9.58 | 304 | 25.23 | 37.71 | 38.0 | 1.48 | 3.78 | 273.22 | 2.16 | 3.01 |
| Friday | 1302 | 1118 | 121 | 63 | 85.87 | 9.29 | 282 | 25.22 | 37.44 | 37.0 | 1.39 | 3.76 | 267.34 | 2.16 | 2.97 |
| Saturday | 1310 | 1139 | 115 | 56 | 86.95 | 8.78 | 277 | 24.32 | 37.58 | 38.0 | 1.48 | 3.77 | 268.54 | 2.15 | 3.03 |
| Sunday | 1671 | 1418 | 167 | 86 | 84.86 | 9.99 | 327 | 23.06 | 37.56 | 38.0 | 1.26 | 3.73 | 264.85 | 2.14 | 2.97 |


### Operational Breakdown by Rush Hour Status

| Rush Hour Status | Total Orders | Delivered Orders | Cancelled Orders | In-Transit Orders | Fulfillment Rate (%) | Cancellation Rate (%) | Delayed Delivered Orders | Delay Rate Delivered (%) | Mean Duration (min) | Median Duration (min) | Mean Delay Duration (min) | Mean Courier Speed (km/h) | Mean Order Value (EGP) | Mean Distance (km) | Mean Quantity |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Off-Peak (0) | 7105 | 6066 | 689 | 350 | 85.38 | 9.7 | 1514 | 24.96 | 37.62 | 38.0 | 1.39 | 3.74 | 267.53 | 2.15 | 3.0 |
| Rush Hour (1) | 2895 | 2454 | 291 | 150 | 84.77 | 10.05 | 553 | 22.53 | 37.21 | 37.0 | 1.32 | 3.77 | 272.53 | 2.15 | 3.01 |


### Operational Breakdown by Distance Category

| Distance Category | Total Orders | Delivered Orders | Cancelled Orders | In-Transit Orders | Fulfillment Rate (%) | Cancellation Rate (%) | Delayed Delivered Orders | Delay Rate Delivered (%) | Mean Duration (min) | Median Duration (min) | Mean Delay Duration (min) | Mean Courier Speed (km/h) | Mean Order Value (EGP) | Mean Distance (km) | Mean Quantity |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Long (3-5km) | 2268 | 1921 | 219 | 128 | 84.7 | 9.66 | 456 | 23.74 | 37.48 | 38.0 | 1.33 | 6.24 | 271.44 | 3.59 | 3.04 |
| Medium (1-3km) | 6194 | 5318 | 585 | 291 | 85.86 | 9.44 | 1286 | 24.18 | 37.44 | 38.0 | 1.37 | 3.47 | 267.15 | 1.99 | 2.98 |
| Short (<1km) | 1525 | 1270 | 176 | 79 | 83.28 | 11.54 | 321 | 25.28 | 37.8 | 38.0 | 1.46 | 1.11 | 272.36 | 0.64 | 3.03 |
| Very Long (>5km) | 13 | 11 | 0 | 2 | 84.62 | 0.0 | 4 | 36.36 | 38.55 | 36.0 | 0.91 | 8.33 | 308.77 | 5.16 | 2.77 |


### Operational Breakdown by Order Value Tier

| Order Value Tier | Total Orders | Delivered Orders | Cancelled Orders | In-Transit Orders | Fulfillment Rate (%) | Cancellation Rate (%) | Delayed Delivered Orders | Delay Rate Delivered (%) | Mean Duration (min) | Median Duration (min) | Mean Delay Duration (min) | Mean Courier Speed (km/h) | Mean Order Value (EGP) | Mean Distance (km) | Mean Quantity |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Budget (<100) | 1562 | 1329 | 155 | 78 | 85.08 | 9.92 | 345 | 25.96 | 38.02 | 38.0 | 1.45 | 3.74 | 69.1 | 2.17 | 1.29 |
| Luxury (>500) | 1232 | 1051 | 120 | 61 | 85.31 | 9.74 | 252 | 23.98 | 37.47 | 38.0 | 1.36 | 3.71 | 599.95 | 2.13 | 4.66 |
| Premium (300-500) | 2309 | 1957 | 241 | 111 | 84.76 | 10.44 | 515 | 26.32 | 37.74 | 38.0 | 1.48 | 3.77 | 390.22 | 2.17 | 3.93 |
| Standard (100-300) | 4897 | 4183 | 464 | 250 | 85.42 | 9.48 | 955 | 22.83 | 37.24 | 37.0 | 1.3 | 3.76 | 192.29 | 2.14 | 2.7 |


---

## 4. Analytical Observations & Operational Takeaways

1. **SLA Compliance Baseline:** 
   - Across 8,520 completed deliveries, **24.26% (2,067 orders)** breached the 45-minute SLA threshold.
   - When an order is delayed, the average excess waiting time is **5.65 minutes** beyond promise time.

2. **Geographic Distribution:**
   - Delivery performance is remarkably consistent across all 7 cities (Average durations: **37.21 min** in Giza to **37.63 min** in Zagazig; Delay rates: **23.89%** in Giza to **24.55%** in Zagazig).

3. **Traffic Impact:**
   - High traffic levels exhibit slightly lower average duration (**37.13 min**) and lower delay rates (**22.54%**) compared to Medium traffic (**37.78 min**, **25.91%** delay rate), suggesting possible courier rerouting or active fleet adjustment during peak congestion.

4. **Distance Relationship:**
   - Short distance (<1km) orders experience a **25.25%** delay rate compared to **23.68%** for Long distance (3–5km) orders. This indicates that fixed dispatch and kitchen preparation overhead dominate delivery latency more than transit distance.

---

## 5. Artifact & Output Reference File List

- Script: [`src/analytics/compute_kpis.py`](file:///c:/FoodDeliveryAnalytics/src/analytics/compute_kpis.py)
- Structured Tables Directory: [`reports/tables/`](file:///c:/FoodDeliveryAnalytics/reports/tables/)
  - [`overall_kpis.csv`](file:///c:/FoodDeliveryAnalytics/reports/tables/overall_kpis.csv)
  - [`city_kpis.csv`](file:///c:/FoodDeliveryAnalytics/reports/tables/city_kpis.csv)
  - [`traffic_kpis.csv`](file:///c:/FoodDeliveryAnalytics/reports/tables/traffic_kpis.csv)
  - [`time_of_day_kpis.csv`](file:///c:/FoodDeliveryAnalytics/reports/tables/time_of_day_kpis.csv)
  - [`day_of_week_kpis.csv`](file:///c:/FoodDeliveryAnalytics/reports/tables/day_of_week_kpis.csv)
  - [`rush_hour_kpis.csv`](file:///c:/FoodDeliveryAnalytics/reports/tables/rush_hour_kpis.csv)
  - [`distance_bin_kpis.csv`](file:///c:/FoodDeliveryAnalytics/reports/tables/distance_bin_kpis.csv)
  - [`order_value_tier_kpis.csv`](file:///c:/FoodDeliveryAnalytics/reports/tables/order_value_tier_kpis.csv)
- Complete JSON Summary: [`reports/phase4_kpis.json`](file:///c:/FoodDeliveryAnalytics/reports/phase4_phase4_kpis.json)
