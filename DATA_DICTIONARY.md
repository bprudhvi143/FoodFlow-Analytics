# FoodFlow Analytics — Data Dictionary
## Complete Data Schema Reference for `food_delivery_10k.csv`

**Project:** FoodFlow Analytics  
**Dataset Path:** [`data/processed/food_delivery_10k.csv`](file:///c:/FoodDeliveryAnalytics/data/processed/food_delivery_10k.csv) (and [`Datasets/food_delivery_10k.csv`](file:///c:/FoodDeliveryAnalytics/Datasets/food_delivery_10k.csv))  
**Total Records ($N$):** 10,000 rows  
**Total Fields ($K$):** 55 columns  
**Missing Cells:** 0 (0.00%)  
**Duplicate Rows:** 0 (0.00%)  
**Document Generated:** October 3, 2026  

---

## 1. Dataset Overview & High-Level Summary

The dataset represents **10,000 food delivery order transactions** across 7 major Egyptian cities (Alexandria, Assiut, Cairo, Giza, Mansoura, Tanta, Zagazig). Each record contains comprehensive operational data spanning order placement, basket composition, driver dispatch, geographic coordinates, traffic conditions, fulfillment outcomes, and delivery SLA performance metrics.

### Key Data Characteristics
- **Completeness:** 100% complete data across all 55 columns (0 missing values).
- **Uniqueness:** 10,000 unique `Order_ID` values; zero duplicate rows.
- **Fulfillment Outcome Breakdown:**
  - **Delivered (`Order_Status == 'Delivered'`):** 8,520 orders (**85.20%**)
  - **Cancelled (`Order_Status == 'Cancelled'`):** 980 orders (**9.80%**)
  - **In Transit (`Order_Status == 'In Transit'`):** 500 orders (**5.00%**)
- **Target Variables:**
  - `Is_Delayed_TARGET` (Binary SLA breach flag: $>45$ minutes): **2,417 delayed orders overall (24.17%)**; **2,067 delayed orders among completed deliveries (24.26%)**.
  - `Delay_Minutes_TARGET` (Continuous excess minutes beyond 45-min SLA): Range 0.0 to 15.0 minutes (Mean: **1.36 min** overall / **5.65 min** for delayed completed orders).

---

## 2. Complete 55-Column Data Dictionary Table

| # | Column Name | Data Type | Functional Category | Description & Operational Meaning | Missing Count | Unique Values / Range | Sample Values |
|---|---|---|---|---|---|---|---|
| 1 | `Order_ID` | `int64` | Identifier | Unique transaction identifier for each order | 0 | 10,000 unique (Range: 6 – 99,997) | `6`, `17`, `22` |
| 2 | `User_ID` | `string` | Identifier | Unique customer account identifier | 0 | 6,048 unique values | `'U7439'`, `'U9001'`, `'U9985'` |
| 3 | `Restaurant_ID` | `int64` | Identifier | Unique vendor/restaurant account identifier | 0 | 1,000 unique values (Range: 1 – 1,000) | `750`, `51`, `12` |
| 4 | `Driver_ID` | `int64` | Identifier | Unique courier driver account identifier | 0 | 500 unique values (Range: 1 – 500) | `270`, `129`, `405` |
| 5 | `Item_Name` | `string` | Order/Pricing | Primary food item name ordered | 0 | 9 unique values | `'Sushi'`, `'Pizza'`, `'Koshary'`, `'Shawarma'`, `'Sandwich'`, `'Fried Chicken'`, `'Burger'`, `'Salad'`, `'Pasta'` |
| 6 | `Quantity` | `int64` | Order/Pricing | Total number of items in the order basket | 0 | 5 unique values (Range: 1 – 5) | `1`, `2`, `3`, `4`, `5` |
| 7 | `Total_Price` | `float64` | Order/Pricing | Total gross order value in Egyptian Pounds (EGP) | 0 | 8,655 unique (Range: 30.02 – 749.85 EGP, Mean: 268.97) | `205.44`, `39.10`, `540.00` |
| 8 | `Order_Time` | `string` | Temporal | Timestamp when order was placed (`YYYY-MM-DD HH:MM`) | 0 | 8,014 unique timestamps | `'2025-06-04 12:16'`, `'2025-06-14 10:24'` |
| 9 | `Delivery_Time` | `string` | Temporal | Timestamp when order was delivered/completed | 0 | 8,050 unique timestamps | `'2025-06-04 12:45'`, `'2025-06-14 11:18'` |
| 10 | `Delivery_Duration_Minutes` | `int64` | Performance | Total fulfillment time in minutes from placement to handoff | 0 | 46 unique values (Range: 15 – 60 min, Mean: 37.48) | `29`, `54`, `42` |
| 11 | `City` | `string` | Spatial | Egyptian metropolitan region | 0 | 7 unique cities | `'Alexandria'`, `'Assiut'`, `'Cairo'`, `'Giza'`, `'Mansoura'`, `'Tanta'`, `'Zagazig'` |
| 12 | `Payment_Method` | `string` | Order/Pricing | Payment instrument used | 0 | 3 unique values | `'Credit Card'`, `'Cash'`, `'Wallet'` |
| 13 | `Order_Status` | `string` | Fulfillment | Primary fulfillment lifecycle state | 0 | 3 unique values | `'Delivered'` (8,520), `'Cancelled'` (980), `'In Transit'` (500) |
| 14 | `Driver_Vehicle` | `string` | Fleet | Courier vehicle transport type | 0 | 3 unique values | `'Bicycle'` (3,339), `'Motorbike'` (3,347), `'Car'` (3,314) |
| 15 | `Restaurant_Lat` | `float64` | Spatial | Latitude coordinate of vendor location | 0 | 9,998 unique (Range: 27.1609 – 31.2201) | `31.02414`, `30.57987` |
| 16 | `Restaurant_Lon` | `float64` | Spatial | Longitude coordinate of vendor location | 0 | 10,000 unique (Range: 29.8988 – 31.5220) | `31.38782`, `31.50381` |
| 17 | `Customer_Lat` | `float64` | Spatial | Latitude coordinate of customer delivery location | 0 | 9,998 unique (Range: 27.1609 – 31.2201) | `31.02900`, `30.60067` |
| 18 | `Customer_Lon` | `float64` | Spatial | Longitude coordinate of customer delivery location | 0 | 9,996 unique (Range: 29.8987 – 31.5220) | `31.37387`, `31.50432` |
| 19 | `Driver_Lat` | `float64` | Spatial | Latitude coordinate of driver position at assignment | 0 | 10,000 unique (Range: 27.1609 – 31.2201) | `31.02257`, `30.57371` |
| 20 | `Driver_Lon` | `float64` | Spatial | Longitude coordinate of driver position at assignment | 0 | 9,997 unique (Range: 29.8987 – 31.5220) | `31.38065`, `31.48456` |
| 21 | `Delivery_Distance_km` | `float64` | Spatial | Direct Haversine distance from vendor to customer (km) | 0 | 10,000 unique (Range: 0.0354 – 5.3491 km, Mean: 2.15) | `1.4368`, `2.3062` |
| 22 | `Traffic_Level` | `string` | Traffic | Categorical road congestion severity | 0 | 3 unique values | `'Low'` (4,525), `'Medium'` (2,551), `'High'` (2,924) |
| 23 | `Driver_Availability` | `string` | Fleet | Courier connectivity status at order placement | 0 | 2 unique values | `'Online'` (8,999), `'Offline'` (1,001) |
| 24 | `Restaurant_Geo_Imputed` | `int64` | Metadata | Binary flag indicating if vendor coords were imputed | 0 | 1 unique value (`0`) | `0` (Constant) |
| 25 | `Customer_Geo_Imputed` | `int64` | Metadata | Binary flag indicating if customer coords were imputed | 0 | 1 unique value (`0`) | `0` (Constant) |
| 26 | `Driver_Geo_Imputed` | `int64` | Metadata | Binary flag indicating if driver coords were imputed | 0 | 1 unique value (`0`) | `0` (Constant) |
| 27 | `Same_Location_Flag` | `int64` | Metadata | Binary flag indicating identical vendor/customer coords | 0 | 1 unique value (`0`) | `0` (Constant) |
| 28 | `Order_Hour` | `int64` | Temporal | Hour of day when order was placed (0 to 23) | 0 | 24 unique values (Range: 0 – 23) | `12`, `10`, `3` |
| 29 | `Order_DayOfWeek` | `int64` | Temporal | Day of week index (0=Monday to 6=Sunday) | 0 | 7 unique values (Range: 0 – 6) | `2`, `5`, `0` |
| 30 | `Order_DayOfMonth` | `int64` | Temporal | Day of month (1 to 16 in sample window) | 0 | 16 unique values (Range: 1 – 16) | `4`, `14`, `1` |
| 31 | `Is_Weekend` | `int64` | Temporal | Binary flag for weekend (Friday, Saturday, Sunday) | 0 | 2 unique values | `0` (Weekday), `1` (Weekend) |
| 32 | `Is_RushHour` | `int64` | Temporal | Binary flag for peak meal hours (12–14, 18–21) | 0 | 2 unique values | `0` (Off-Peak), `1` (Rush Hour) |
| 33 | `Price_Per_Item` | `float64` | Order/Pricing | Unit item price in EGP (`Total_Price / Quantity`) | 0 | 6,818 unique (Range: 30.00 – 149.99 EGP, Mean: 89.59) | `68.48`, `39.10` |
| 34 | `Traffic_Level_Enc` | `int64` | Traffic | Ordinal encoding for traffic (0=Low, 1=Medium, 2=High) | 0 | 3 unique values | `0`, `1`, `2` |
| 35 | `Driver_Online` | `int64` | Fleet | Binary flag for driver online status (1=Online, 0=Offline) | 0 | 2 unique values | `1` (Online), `0` (Offline) |
| 36 | `Is_Delivered` | `int64` | Fulfillment | Binary flag indicating completed delivery | 0 | 2 unique values | `1` (Delivered: 8,520), `0` (Not Delivered: 1,480) |
| 37 | `Is_Cancelled` | `int64` | Fulfillment | Binary flag indicating order cancellation | 0 | 2 unique values | `0` (Active: 9,020), `1` (Cancelled: 980) |
| 38 | `Is_InTransit` | `int64` | Fulfillment | Binary flag indicating order in progress | 0 | 2 unique values | `0` (Finished/Cancelled: 9,500), `1` (In Transit: 500) |
| 39 | `Order_Date` | `string` | Temporal | Calendar date string (`YYYY-MM-DD`) | 0 | 16 unique dates (June 1–16, 2025) | `'2025-06-04'`, `'2025-06-14'` |
| 40 | `Order_Month` | `int64` | Temporal | Calendar month number (6=June) | 0 | 1 unique value (`6`) | `6` (Constant) |
| 41 | `Order_DayName` | `string` | Temporal | Name of day of week | 0 | 7 unique values | `'Monday'`, `'Tuesday'`, `'Wednesday'`, `'Thursday'`, `'Friday'`, `'Saturday'`, `'Sunday'` |
| 42 | `Time_Of_Day_Segment` | `string` | Temporal | 4-hour period segment name | 0 | 6 unique values | `'Early Morning'`, `'Morning'`, `'Afternoon'`, `'Evening'`, `'Night'`, `'Late Night'` |
| 43 | `Is_Weekday` | `int64` | Temporal | Binary flag for Monday through Thursday | 0 | 2 unique values | `1` (Weekday), `0` (Weekend) |
| 44 | `Driver_To_Restaurant_km` | `float64` | Spatial | Haversine distance from driver position to vendor (km) | 0 | 9,995 unique (Range: 0.0387 – 5.4861 km, Mean: 2.17) | `0.7052`, `1.9664` |
| 45 | `Total_Trip_km` | `float64` | Spatial | Total courier distance (`Driver_To_Restaurant + Delivery_Distance`) | 0 | 9,993 unique (Range: 0.2110 – 9.6056 km, Mean: 4.32) | `2.1420`, `4.2726` |
| 46 | `Distance_Bin` | `string` | Spatial | Binned distance category for vendor-to-customer | 0 | 4 unique values | `'Short (<1km)'`, `'Medium (1-3km)'`, `'Long (3-5km)'`, `'Very Long (>5km)'` |
| 47 | `Order_Value_Tier` | `string` | Order/Pricing | Binned gross price tier category | 0 | 4 unique values | `'Budget (<100)'`, `'Standard (100-300)'`, `'Premium (300-500)'`, `'Luxury (>500)'` |
| 48 | `Is_Large_Order` | `int64` | Order/Pricing | Binary flag for high value order (`Total_Price > 300 EGP`) | 0 | 2 unique values | `0` (Standard: 6,003), `1` (Large: 3,997) |
| 49 | `Is_High_Traffic` | `int64` | Traffic | Binary flag for high congestion (`Traffic_Level == 'High'`) | 0 | 2 unique values | `0` (Low/Med: 7,076), `1` (High: 2,924) |
| 50 | `Is_Delayed_TARGET` | `int64` | **Target Variable** | **Primary Classification Target:** 1 if duration > 45 min | 0 | 2 unique values | `0` (On-Time: 7,583), `1` (Delayed: 2,417) |
| 51 | `Delay_Minutes_TARGET` | `float64` | **Target Variable** | **Primary Regression Target:** $\max(0, \text{Duration} - 45)$ | 0 | 16 unique values (Range: 0.0 – 15.0 min, Mean: 1.36) | `0.0`, `9.0`, `5.0` |
| 52 | `Duration_Bin_TARGET` | `string` | **Target Variable** | Multi-class SLA duration category | 0 | 3 unique values | `'Fast (<30min)'`, `'Normal (30-45min)'`, `'Slow (>45min)'` |
| 53 | `Order_To_Delivery_Minutes_TARGET` | `float64` | **Target Variable** | Continuous total duration duplicate target field | 0 | 46 unique values (Range: 15.0 – 60.0 min, Mean: 37.48) | `29.0`, `54.0` |
| 54 | `Delivery_Speed_kmh_ANALYTICAL` | `float64` | Operational Ratio | Effective courier trip speed ($\text{km} / \text{hours}$) | 0 | 9,350 unique (Range: 0.0408 – 17.3275 km/h, Mean: 3.75) | `2.9727`, `2.5624` |
| 55 | `Distance_Per_Minute_ANALYTICAL` | `float64` | Operational Ratio | Speed index ($\text{Delivery\_Distance\_km} / \text{Duration\_Minutes}$) | 0 | 9,603 unique (Range: 0.0007 – 0.2888 km/min, Mean: 0.0625) | `0.0495`, `0.0427` |

---

## 3. Targeted Operational Dimension Mapping

| Core Analytical Concept | Primary Dataset Fields | Purpose & Calculation Logic |
|---|---|---|
| **Order Status** | `Order_Status`, `Is_Delivered`, `Is_Cancelled`, `Is_InTransit` | Categorizes order lifecycle. `Order_Status` is used for primary filtering (`Delivered`: 8,520; `Cancelled`: 980; `In Transit`: 500). |
| **Delivery Duration** | `Delivery_Duration_Minutes`, `Order_To_Delivery_Minutes_TARGET` | Measure of total fulfillment turnaround in minutes ($15 \text{ to } 60$ minutes). |
| **SLA Delay** | `Is_Delayed_TARGET`, `Delay_Minutes_TARGET`, `Duration_Bin_TARGET` | Primary targets. SLA threshold is set at $45$ minutes. Orders $>45$ min are flagged delayed (`Is_Delayed_TARGET == 1`). |
| **City** | `City` | 7 urban centers in Egypt: Alexandria, Assiut, Cairo, Giza, Mansoura, Tanta, Zagazig. |
| **Traffic Severity** | `Traffic_Level`, `Traffic_Level_Enc`, `Is_High_Traffic` | Congestion classification (`Low`: 4,525, `Medium`: 2,551, `High`: 2,924). |
| **Driver Vehicle Type** | `Driver_Vehicle` | Transport mode (`Motorbike`: 3,347, `Bicycle`: 3,339, `Car`: 3,314). |
| **Trip & Dispatch Distance** | `Delivery_Distance_km`, `Driver_To_Restaurant_km`, `Total_Trip_km`, `Distance_Bin` | Haversine distance measures. Vendor-to-customer mean is **2.15 km**; driver dispatch mean is **2.17 km**. |
| **Order Value & Pricing** | `Total_Price`, `Price_Per_Item`, `Order_Value_Tier`, `Is_Large_Order` | Gross order pricing in EGP (Mean: **EGP 268.97**) and tier buckets (`Budget`, `Standard`, `Premium`, `Luxury`). |
| **Basket Quantity** | `Quantity` | Item count per order ($1 \text{ to } 5$ items, Mean: **3.00 items**). |
| **Time of Day** | `Time_Of_Day_Segment`, `Order_Hour` | 6 4-hour temporal segments (`Early Morning`, `Morning`, `Afternoon`, `Evening`, `Night`, `Late Night`) & hour (0–23). |
| **Day of Week** | `Order_DayName`, `Order_DayOfWeek`, `Is_Weekend`, `Is_Weekday` | Day of week breakdown (Monday to Sunday) and weekend/weekday binary indicators. |

---

## 4. Confirmed Machine Learning Target Variables

> [!IMPORTANT]
> **Target Leakage Safeguard:** The target variables below are calculated post-fulfillment and MUST be strictly excluded from model feature inputs during Phase 5 machine learning training.

1. **`Is_Delayed_TARGET` (Binary Classification Target):**
   - **Definition:** Indicates whether the total delivery duration exceeded the 45-minute SLA threshold.
   - **Formula:** $\text{Is\_Delayed\_TARGET} = \begin{cases} 1 & \text{if } \text{Delivery\_Duration\_Minutes} > 45 \\ 0 & \text{if } \text{Delivery\_Duration\_Minutes} \le 45 \end{cases}$
   - **Dataset Baseline:** 2,417 delayed orders overall (**24.17%**); 2,067 delayed orders among completed deliveries (**24.26%**).

2. **`Delay_Minutes_TARGET` (Continuous Regression Target):**
   - **Definition:** Continuous measure of excess delivery duration beyond the 45-minute promise time.
   - **Formula:** $\text{Delay\_Minutes\_TARGET} = \max(0, \text{Delivery\_Duration\_Minutes} - 45)$
   - **Dataset Baseline:** Range 0.0 to 15.0 minutes; overall mean **1.36 minutes**; mean among delayed completed orders **5.65 minutes**.
