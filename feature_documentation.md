# Feature Documentation
## Food Delivery Analytics: Delivery Performance and Delay Prediction

**Document version:** 1.0  
**Dataset:** `Datasets/Order_delivery_featured.csv`  
**Produced by:** `feature_engineering.py` (runs on top of `preprocessing_pipeline.py` output)  
**Total columns in featured dataset:** 55 (23 raw + 15 preprocessing + 17 feature-engineering)

---

## Critical: Temporal Availability and Target Leakage

Every column in this dataset is classified by **when the information becomes available**:

| Label | Meaning | May be used as ML input? |
|---|---|---|
| **PRE_ORDER** | Known at the moment the customer places the order | ✅ Yes |
| **IN_DELIVERY** | Known only while the delivery is active | ⚠️ Context-dependent |
| **POST_DELIVERY** | Known only after the delivery is complete | ❌ No — leakage risk |

> **Rule:** Any column derived from `Delivery_Time` or `Delivery_Duration_Minutes` is **POST_DELIVERY**. Using it as a model input feature would allow the model to "see the future" — a classic form of target leakage that produces unrealistically high training scores and fails completely at inference time.

> **Note on this dataset:** `Driver_Availability` is a snapshot field (the driver's status when the dataset was extracted, not when the order was placed). It is technically PRE_ORDER in structure but semantically unreliable as a pre-order signal.

---

## Section 1: Raw Source Columns (unchanged from original CSV)

These 23 columns come directly from `Datasets/Order_delivery.csv`.

| Column | Type | Availability | Safe as ML input? | Notes |
|---|---|---|---|---|
| `Order_ID` | Integer ID | PRE_ORDER | ❌ Drop before modelling | Primary key; no predictive signal |
| `User_ID` | String ID | PRE_ORDER | ⚠️ Frequency-encode only | 9,000 unique users; high cardinality |
| `Restaurant_ID` | Integer ID | PRE_ORDER | ⚠️ Frequency-encode only | 1,000 unique restaurants; high cardinality |
| `Driver_ID` | Integer ID | PRE_ORDER | ⚠️ Frequency-encode only | 500 drivers; high cardinality; all drivers use all vehicle types |
| `Item_Name` | String category | PRE_ORDER | ✅ One-hot encode | 9 balanced categories |
| `Quantity` | Integer 1–5 | PRE_ORDER | ✅ | Proxy for order preparation complexity |
| `Total_Price` | Float (EGP) | PRE_ORDER | ✅ | Right-skewed; consider log transform for linear models |
| `Order_Time` | Datetime | PRE_ORDER | ✅ Extract features from it | Parse format: `%Y-%m-%d %H:%M` in cleaned CSV |
| `Delivery_Time` | Datetime | **POST_DELIVERY** | ❌ Never use as input | Outcome timestamp; basis for duration computation |
| `Delivery_Duration_Minutes` | Integer (min) | **POST_DELIVERY** | ❌ Target variable only | Range 15–60 min; primary regression target |
| `City` | String category | PRE_ORDER | ✅ One-hot or ordinal encode | 7 cities, balanced; captures geographic effects |
| `Payment_Method` | String category | PRE_ORDER | ✅ | 3 balanced categories; weak signal expected |
| `Order_Status` | String category | **POST_DELIVERY** | ❌ Filter column only | Delivered / Cancelled / In Transit; use to filter for model training |
| `Driver_Vehicle` | String category | PRE_ORDER | ✅ | Per-order vehicle type (not a driver property) |
| `Restaurant_Lat` | Float (degrees) | PRE_ORDER | ⚠️ Redundant with City | Strong negative skew from geographic distribution |
| `Restaurant_Lon` | Float (degrees) | PRE_ORDER | ⚠️ Redundant with City | Same |
| `Customer_Lat` | Float (degrees) | PRE_ORDER | ⚠️ Redundant with City | Same |
| `Customer_Lon` | Float (degrees) | PRE_ORDER | ⚠️ Redundant with City | Same |
| `Driver_Lat` | Float (degrees) | PRE_ORDER | ✅ Use via Driver_To_Restaurant_km | Driver's position at dispatch |
| `Driver_Lon` | Float (degrees) | PRE_ORDER | ✅ Use via Driver_To_Restaurant_km | Same |
| `Delivery_Distance_km` | Float (km) | PRE_ORDER | ✅ | Restaurant-to-customer Haversine distance; range 0.009–5.60 km |
| `Traffic_Level` | String category | PRE_ORDER | ✅ Use encoded version | Ordinal: Low / Medium / High |
| `Driver_Availability` | String category | PRE_ORDER* | ⚠️ Use with caution | *Snapshot field — value is the driver's status at dataset extraction, not at order time |

---

## Section 2: Preprocessing-Derived Columns

Added by `preprocessing_pipeline.py`. These 15 columns extend the raw data.

| Column | Formula | Availability | Safe as ML input? |
|---|---|---|---|
| `Restaurant_Geo_Imputed` | 1 if Restaurant_Lat/Lon was city-median imputed | PRE_ORDER | ✅ |
| `Customer_Geo_Imputed` | 1 if Customer_Lat/Lon was city-median imputed | PRE_ORDER | ✅ |
| `Driver_Geo_Imputed` | 1 if Driver_Lat/Lon was city-median imputed | PRE_ORDER | ✅ |
| `Same_Location_Flag` | 1 if restaurant and customer share identical coordinates | PRE_ORDER | ✅ |
| `Order_Hour` | `Order_Time.hour` (0–23) | PRE_ORDER | ✅ |
| `Order_DayOfWeek` | `Order_Time.dayofweek` (0=Mon … 6=Sun) | PRE_ORDER | ✅ |
| `Order_DayOfMonth` | `Order_Time.day` (1–31) | PRE_ORDER | ✅ |
| `Is_Weekend` | 1 if `Order_DayOfWeek` ∈ {5, 6} | PRE_ORDER | ✅ |
| `Is_RushHour` | 1 if `Order_Hour` ∈ {7,8,9,18,19,20,21} | PRE_ORDER | ✅ |
| `Price_Per_Item` | `Total_Price / Quantity` | PRE_ORDER | ✅ |
| `Traffic_Level_Enc` | Low=0, Medium=1, High=2 | PRE_ORDER | ✅ |
| `Driver_Online` | Online=1, Offline=0 | PRE_ORDER* | ⚠️ Snapshot field |
| `Is_Delivered` | 1 if `Order_Status == 'Delivered'` | **POST_DELIVERY** | ❌ |
| `Is_Cancelled` | 1 if `Order_Status == 'Cancelled'` | **POST_DELIVERY** | ❌ |
| `Is_InTransit` | 1 if `Order_Status == 'In Transit'` | **POST_DELIVERY** | ❌ |

---

## Section 3: Feature-Engineering Columns

Added by `feature_engineering.py`. These 17 columns are the new additions in this phase.

---

### 3.1 PRE_ORDER Temporal Features

#### `Order_Date`
- **Formula:** `Order_Time.dt.date`
- **Type:** Date
- **Availability:** PRE_ORDER
- **Safe as ML input:** ❌ No — date is too specific and will not generalise; use `Order_DayOfWeek`, `Order_Month`, `Is_Weekend` instead
- **Use in analytics:** ✅ Group daily order volumes, trend charts
- **Example values:** `2025-06-01`, `2025-06-16`
- **Validation:** Range 2025-06-01 to 2025-06-16 (16-day dataset window)

---

#### `Order_Month`
- **Formula:** `Order_Time.dt.month`
- **Type:** Integer (1–12)
- **Availability:** PRE_ORDER
- **Safe as ML input:** ✅ Yes — only month 6 in this dataset; meaningful when data spans multiple months
- **Rationale:** Seasonal demand variation differs by month (Ramadan, summer peaks, etc.)
- **Example values:** `6`
- **Validation:** All values = 6 in current dataset

---

#### `Order_DayName`
- **Formula:** `Order_Time.dt.day_name()`
- **Type:** String (Monday … Sunday)
- **Availability:** PRE_ORDER
- **Safe as ML input:** ⚠️ Use `Order_DayOfWeek` (integer) for modelling; this is the readable label
- **Use in analytics:** ✅ Day-of-week performance tables, bar charts
- **Example values:** `Monday`, `Sunday`, `Friday`
- **Validation:** 7 unique values covering the full week

---

#### `Time_Of_Day_Segment`
- **Formula:** Map `Order_Hour` to 6 named time bands:

  | Segment | Hours | Typical context |
  |---|---|---|
  | Late Night | 00:00–04:59 | Off-peak, minimal traffic |
  | Early Morning | 05:00–08:59 | Breakfast, morning commute |
  | Morning | 09:00–11:59 | Mid-morning, lower demand |
  | Afternoon | 12:00–16:59 | Lunch peak, post-lunch |
  | Evening | 17:00–20:59 | Dinner rush, heavy traffic |
  | Night | 21:00–23:59 | Late-night orders |

- **Type:** Ordinal string category
- **Availability:** PRE_ORDER
- **Safe as ML input:** ✅ Yes — ordinal-encode or one-hot encode
- **Rationale:** Non-linear time-of-day effect; captures demand and traffic patterns better than raw hour for tree-based models
- **Validation:** All 100,002 rows assigned to exactly one segment; no nulls

---

#### `Is_Weekday`
- **Formula:** `1 - Is_Weekend` (1 if Monday–Friday, 0 if Saturday–Sunday)
- **Type:** Binary integer (0 or 1)
- **Availability:** PRE_ORDER
- **Safe as ML input:** ✅ Yes — but note it is perfectly collinear with `Is_Weekend`; use only one in linear models
- **Rationale:** Explicit weekday flag for readability in feature importance plots
- **Validation:** `Is_Weekday + Is_Weekend == 1` for all rows (no contradictions)

---

### 3.2 PRE_ORDER Geographic Features

#### `Driver_To_Restaurant_km`
- **Formula:** `Haversine(Driver_Lat, Driver_Lon, Restaurant_Lat, Restaurant_Lon)`
  - Haversine formula: `d = 2R × arcsin(√(sin²(Δφ/2) + cos(φ₁)cos(φ₂)sin²(Δλ/2)))`
  - where R = 6371 km, φ = latitude in radians, λ = longitude in radians
- **Type:** Float (km), 6 decimal places
- **Availability:** PRE_ORDER — both the driver's position and restaurant location are known at dispatch
- **Safe as ML input:** ✅ Yes
- **Rationale:** The distance the driver must travel to pick up the order before the customer-leg begins. This is a proxy for the "first-mile" portion of total delivery time.
- **Interpretation:** A driver 4 km from the restaurant will take longer to start the customer-leg than one 0.5 km away
- **Range in dataset:** ~0.009 to ~5.60 km (mirrors the distribution of Delivery_Distance_km — same city-bounded coordinates)
- **Validation:** All values ≥ 0; no nulls; mean ≈ 2.17 km, corr with duration ≈ 0.00 (simulation artefact — in real data this would be positive)

---

#### `Total_Trip_km`
- **Formula:** `Driver_To_Restaurant_km + Delivery_Distance_km`
- **Type:** Float (km)
- **Availability:** PRE_ORDER
- **Safe as ML input:** ✅ Yes
- **Rationale:** The complete physical distance the driver travels: from starting position, to restaurant, to customer. More informative than either component alone because it captures the full workload of a single delivery.
- **Note on collinearity:** Correlated with both `Driver_To_Restaurant_km` and `Delivery_Distance_km`. In regularised linear models, use at most two of the three. Tree-based models handle the collinearity naturally.
- **Validation:** `Total_Trip_km >= Delivery_Distance_km` for all rows; `Total_Trip_km >= Driver_To_Restaurant_km` for all rows

---

#### `Distance_Bin`
- **Formula:** `pd.cut(Delivery_Distance_km, bins=[0, 1, 3, 5, ∞])`

  | Bin | Range | Label |
  |---|---|---|
  | 1 | [0, 1) km | Short (<1km) |
  | 2 | [1, 3) km | Medium (1-3km) |
  | 3 | [3, 5) km | Long (3-5km) |
  | 4 | [5, ∞) km | Very Long (>5km) |

- **Type:** Ordinal category
- **Availability:** PRE_ORDER
- **Safe as ML input:** ✅ Yes — label/ordinal encode
- **Rationale:** Non-linear distance grouping for decision-tree splits and bar-chart analytics. Bin boundaries chosen to match natural distribution quartiles (~p25=1.36, ~p75=2.92)
- **Validation:** 100,002 rows assigned; no nulls; Very Long bin contains ~30 rows (IQR outliers)

---

### 3.3 PRE_ORDER Order Features

#### `Order_Value_Tier`
- **Formula:** `pd.cut(Total_Price, bins=[0, 100, 300, 500, ∞])`

  | Tier | Range (EGP) | Label |
  |---|---|---|
  | 1 | [0, 100) | Budget (<100) |
  | 2 | [100, 300) | Standard (100-300) |
  | 3 | [300, 500) | Premium (300-500) |
  | 4 | [500, ∞) | Luxury (>500) |

- **Type:** Ordinal category
- **Availability:** PRE_ORDER
- **Safe as ML input:** ✅ Yes
- **Rationale:** Captures price-tier effects without exposing raw price to linear models where its right-skew could distort coefficient estimation. Bin boundaries reflect approximate quartiles of Total_Price.
- **Validation:** All rows assigned; no nulls

---

#### `Is_Large_Order`
- **Formula:** `1 if Quantity >= 4 else 0`
- **Type:** Binary integer (0 or 1)
- **Availability:** PRE_ORDER
- **Safe as ML input:** ✅ Yes
- **Rationale:** Orders of 4–5 items represent the top 40% by size. Large orders plausibly take longer to prepare and package at the restaurant, adding to total delivery time.
- **Threshold justification:** Quantity is discrete 1–5; Quantity ≥ 4 cleanly separates the top two values. A continuous quantity variable is also retained.
- **Validation:** Binary only; `Is_Large_Order.sum() ≈ 39,609` (~39.6% of orders)

---

#### `Is_High_Traffic`
- **Formula:** `1 if Traffic_Level_Enc == 2 (High) else 0`
- **Type:** Binary integer (0 or 1)
- **Availability:** PRE_ORDER
- **Safe as ML input:** ✅ Yes — but note it is derivable from `Traffic_Level_Enc`; use only one in linear models
- **Rationale:** Binary flag for the most severe traffic condition; useful as a direct binary signal alongside the ordinal encoding for models that benefit from explicit interaction terms
- **Validation:** `Is_High_Traffic.sum() ≈ 29,221` (~29.2% of orders)

---

### 3.4 POST_DELIVERY Outcome Features (Targets — no model input use)

> ⛔ **These columns MUST NOT appear in any model's input feature matrix.**  
> They may only be used as the `y` (target) in supervised learning, or in retrospective analytics after predictions have been made.

---

#### `Is_Delayed_TARGET`
- **Formula:** `1 if Delivery_Duration_Minutes > delay_threshold else 0`
  - `delay_threshold` = p75 of `Delivery_Duration_Minutes` among `Order_Status == 'Delivered'` rows
  - Value in current dataset: **45 minutes**
- **Type:** Binary integer (0 or 1)
- **Availability:** POST_DELIVERY
- **Role:** **PRIMARY CLASSIFICATION TARGET** for the binary delay prediction model
- **Leakage:** Yes — requires `Delivery_Duration_Minutes` which is only known post-delivery
- **Threshold rationale:** The 75th percentile represents the upper quartile of performance — orders taking longer than 75% of all delivered orders are classified as delayed. This is a standard SLA interpretation ("top quartile of worst performance"). The threshold is computed dynamically from data so it self-adjusts to future dataset updates.
- **Class balance (Delivered orders only):** ~25% delayed, ~75% on-time — mild imbalance, manageable without heavy resampling

---

#### `Delay_Minutes_TARGET`
- **Formula:** `max(0, Delivery_Duration_Minutes - delay_threshold)`
- **Type:** Float (minutes), non-negative
- **Availability:** POST_DELIVERY
- **Role:** **PRIMARY REGRESSION TARGET** for quantifying how late a delivery was
- **Leakage:** Yes
- **Interpretation:** Zero = on-time or fast delivery. Positive = number of minutes beyond the SLA threshold. A value of 10 means the order was 10 minutes later than the p75 benchmark.
- **Range:** 0 to ~15 minutes in this dataset (duration is bounded at 60 min, threshold is 45 min → max excess = 15 min)

---

#### `Duration_Bin_TARGET`
- **Formula:** `pd.cut(Delivery_Duration_Minutes, bins=[0, 30, 45, ∞])`

  | Bin | Range | Label | Interpretation |
  |---|---|---|---|
  | 1 | [0, 30) min | Fast (<30min) | Excellent service |
  | 2 | [30, 45) min | Normal (30-45min) | Standard service |
  | 3 | [45, ∞) min | Slow (>45min) | Below SLA |

- **Type:** Ordinal category
- **Availability:** POST_DELIVERY
- **Role:** **MULTI-CLASS CLASSIFICATION TARGET** for 3-tier service quality prediction
- **Leakage:** Yes
- **Bin boundary rationale:** 30 min = p25 of duration (fast quartile); 45 min = p75 of duration (slow quartile). These are natural distribution break-points confirmed by the percentile analysis.

---

#### `Order_To_Delivery_Minutes_TARGET`
- **Formula:** `(Delivery_Time - Order_Time).total_seconds() / 60`
- **Type:** Float (minutes)
- **Availability:** POST_DELIVERY
- **Role:** Explicit audit of stored `Delivery_Duration_Minutes`; useful for analytics validation
- **Leakage:** Yes — requires `Delivery_Time`
- **Note:** Verified to match `Delivery_Duration_Minutes` exactly (0 mismatches > 1 min). This column is redundant for modelling but valuable as an independent cross-check. If the two values ever diverge, this column identifies the discrepancy.

---

### 3.5 POST_DELIVERY Analytics-Only Features

> ⚠️ **Analytics metrics derived after delivery completes. Do not use as model inputs.**

---

#### `Delivery_Speed_kmh_ANALYTICAL`
- **Formula:** `(Delivery_Distance_km / Delivery_Duration_Minutes) × 60`
- **Type:** Float (km/h)
- **Availability:** POST_DELIVERY
- **Role:** Performance analytics metric — average speed during the customer-leg of delivery
- **Leakage:** Yes
- **Interpretation:** A speed of 6 km/h = walking pace (bicycle in heavy traffic). A speed of 20 km/h = typical urban motorbike speed.
- **Typical range in dataset:** 0.5–20 km/h (mean ≈ 3.76 km/h — low because distance is small and duration is long; these are short urban deliveries)
- **Validation:** All values > 0; no infinities (duration is never 0 in this dataset)

---

#### `Distance_Per_Minute_ANALYTICAL`
- **Formula:** `Delivery_Distance_km / Delivery_Duration_Minutes`
- **Type:** Float (km/min)
- **Availability:** POST_DELIVERY
- **Role:** Efficiency ratio for driver performance monitoring
- **Leakage:** Yes
- **Relationship to speed:** `Distance_Per_Minute_ANALYTICAL = Delivery_Speed_kmh_ANALYTICAL / 60`
- **Note:** Included separately from speed for use in per-minute efficiency comparisons in dashboards

---

## Section 4: Features NOT Created and Why

The following features from the original request were considered and **not created** because the required source columns do not exist in the dataset:

| Requested Feature | Reason Not Created |
|---|---|
| `preparation_duration_minutes` | Requires a "preparation start" or "pickup" timestamp. Only `Order_Time` and `Delivery_Time` exist — no intermediate pickup timestamp is recorded. |
| `pickup_duration_minutes` | Same reason — no pickup/handoff timestamp exists. |
| `expected_delivery_difference` | Requires an "estimated delivery time" field, which is not present in the dataset. Cannot synthesise a meaningful estimate without a route/distance model. |

---

## Section 5: Safe ML Feature Set Summary

When building the delay prediction model, the input feature matrix should consist **only** of PRE_ORDER features. The recommended feature set for Phase 4 is:

### Numeric features (ready to use directly)
| Feature | Source | Notes |
|---|---|---|
| `Quantity` | Raw | 1–5 |
| `Total_Price` | Raw | Consider log transform for linear models |
| `Price_Per_Item` | Preprocessing | Decouples price from quantity |
| `Delivery_Distance_km` | Raw | Primary distance measure |
| `Driver_To_Restaurant_km` | Feature engineering | First-leg proxy |
| `Total_Trip_km` | Feature engineering | Full-trip distance |
| `Order_Hour` | Preprocessing | 0–23 |
| `Order_DayOfWeek` | Preprocessing | 0–6 |
| `Order_DayOfMonth` | Preprocessing | 1–31 |
| `Traffic_Level_Enc` | Preprocessing | 0/1/2 ordinal |
| `Driver_Online` | Preprocessing | 0/1 binary (use with caution — snapshot field) |

### Binary features
| Feature | Source | Notes |
|---|---|---|
| `Is_Weekend` | Preprocessing | 0/1 |
| `Is_Weekday` | Feature engineering | Redundant with Is_Weekend; use only one |
| `Is_RushHour` | Preprocessing | 0/1 |
| `Is_Large_Order` | Feature engineering | Quantity ≥ 4 |
| `Is_High_Traffic` | Feature engineering | Traffic == High |
| `Same_Location_Flag` | Preprocessing | 0/1 |

### Categorical features (require encoding)
| Feature | Source | Encoding recommendation |
|---|---|---|
| `City` | Raw | One-hot (7 categories) |
| `Driver_Vehicle` | Raw | One-hot (3 categories) |
| `Payment_Method` | Raw | One-hot (3 categories) |
| `Item_Name` | Raw | One-hot (9 categories) |
| `Traffic_Level` | Raw | Ordinal (use Traffic_Level_Enc instead) |
| `Time_Of_Day_Segment` | Feature engineering | Ordinal or one-hot (6 categories) |
| `Distance_Bin` | Feature engineering | Ordinal (4 bins) |
| `Order_Value_Tier` | Feature engineering | Ordinal (4 tiers) |

### Columns to EXCLUDE from model input (leakage or identifier)
| Column | Reason |
|---|---|
| `Order_ID` | Identifier — no signal |
| `User_ID` | High cardinality identifier — aggregate separately |
| `Restaurant_ID` | High cardinality identifier — aggregate separately |
| `Driver_ID` | High cardinality identifier — aggregate separately |
| `Order_Time` | Raw datetime — extract components instead |
| `Delivery_Time` | POST_DELIVERY timestamp |
| `Delivery_Duration_Minutes` | Target variable |
| `Order_Status` | POST_DELIVERY outcome (use as filter, not feature) |
| `Is_Delivered`, `Is_Cancelled`, `Is_InTransit` | POST_DELIVERY status flags |
| `Is_Delayed_TARGET` | Primary classification target |
| `Delay_Minutes_TARGET` | Primary regression target |
| `Duration_Bin_TARGET` | Multi-class classification target |
| `Order_To_Delivery_Minutes_TARGET` | Redundant with Delivery_Duration_Minutes |
| `Delivery_Speed_kmh_ANALYTICAL` | POST_DELIVERY analytics metric |
| `Distance_Per_Minute_ANALYTICAL` | POST_DELIVERY analytics metric |
| `Order_Date` | Date — too specific; use day-of-week/month/hour instead |
| `Order_DayName` | Redundant with Order_DayOfWeek |
| `Driver_Availability` | Snapshot field — semantically unreliable as pre-order signal |

---

## Section 6: Target Variable Decision

The primary classification target for the delay prediction model is **`Is_Delayed_TARGET`**.

### Delay threshold: 45 minutes
- Computed as the **p75 of `Delivery_Duration_Minutes`** among `Order_Status == 'Delivered'` rows
- Represents: orders in the top 25% slowest deliveries are "delayed"
- Class distribution among Delivered orders: ~75% on-time, ~25% delayed
- This is a mild imbalance — standard cross-validation handles it; SMOTE is optional

### Alternative targets
- `Delay_Minutes_TARGET` for regression (how many minutes over the threshold)
- `Duration_Bin_TARGET` for three-class classification (Fast / Normal / Slow)

---

*Document generated for Food Delivery Analytics project — Phase 2: Feature Engineering*
