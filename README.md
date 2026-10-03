# FoodFlow Analytics — Egyptian Food Delivery Performance Platform

[![Backend Pytest](https://img.shields.io/badge/Pytest-19%20Passed-brightgreen)](file:///c:/FoodDeliveryAnalytics/tests/test_analytics_backend.py)
[![TypeScript](https://img.shields.io/badge/TypeScript-0%20Errors-blue)](file:///c:/FoodDeliveryAnalytics/tsconfig.json)
[![Build Status](https://img.shields.io/badge/Vite%20Build-Passing-success)](file:///c:/FoodDeliveryAnalytics/dist)
[![Python Version](https://img.shields.io/badge/Python-3.12-blue)](file:///c:/FoodDeliveryAnalytics/requirements.txt)
[![React Version](https://img.shields.io/badge/React-18-cyan)](file:///c:/FoodDeliveryAnalytics/package.json)

> **FoodFlow Analytics** is an end-to-end operational performance dashboard, REST API backend, data explorer, and automated reporting system for food delivery operations across 7 major Egyptian municipalities.

---

## 1. Project Overview

FoodFlow Analytics translates raw logistics records into actionable operational insights for food delivery management in Egypt. Built with a modern **FastAPI** Python backend and a **Vite + React + TypeScript** single-page application frontend, the system processes 10,000 delivery orders across 55 analytical fields.

The platform provides multi-dimensional dynamic filtering, key performance indicator (KPI) tracking, SLA delay threshold monitoring (45-minute benchmark), interactive raw record exploring, schema inspection, statistical distribution summaries, and one-click PDF/print report generation.

---

## 2. Problem Statement

In competitive urban food delivery markets across Egypt (e.g., Cairo, Alexandria, Giza), Service Level Agreement (SLA) breaches—where orders exceed the target 45-minute turnaround time—and order cancellations directly impact customer satisfaction, restaurant reputation, and driver retention.

Operations teams often lack unified, dynamic tools to:
1. Isolate SLA delay hotspots across specific municipalities, traffic congestion levels, and fleet vehicle types.
2. Evaluate basket size and order value impacts on fulfillment turnaround.
3. Dynamically slice operational data in real-time without static database queries.
4. Export executive-ready analytical reports with consistent baseline metrics.

FoodFlow Analytics addresses these challenges by delivering a high-performance interactive dashboard backed by live calculation APIs.

---

## 3. Project Objectives

- **Dataset Audit & Pipeline**: Process, clean, and engineer raw delivery records into a representative 10,000-order analytical dataset.
- **FastAPI Analytics Backend**: Build a scalable, high-speed Python REST API offering 18 endpoints with full query-filter support.
- **Dynamic Filtering Engine**: Enable real-time recalibration of all metrics across 8 filter dimensions (City, Traffic Level, Vehicle Type, Payment Method, Distance Bin, Order Value Tier, Time Segment, Day of Week).
- **Interactive Overview & Deep Dives**: Visualize SLA fulfillment rates, duration histograms, municipal delay tables, temporal delay patterns, and fleet mobility metrics.
- **Data Explorer**: Provide raw record pagination, search, sorting, column schema metadata inspection, and summary statistics.
- **Automated Analytical Reports**: Generate publication-ready executive reports with native `@media print` PDF stylesheet formatting.
- **Quality & Parity Verification**: Maintain 100% test coverage for API endpoints and 0 TypeScript compilation errors.

---

## 4. Dataset Description

- **Primary Analytical File**: `data/processed/food_delivery_10k.csv`
- **Total Population**: 10,000 food delivery orders
- **Schema Width**: 55 columns (23 raw fields + 32 engineered analytical & target features)
- **Geographic Coverage**: 7 Egyptian Municipalities (*Cairo, Alexandria, Giza, Mansoura, Tanta, Zagazig, Assiut*)
- **Temporal Coverage**: 7 Days a week across 6 time-of-day segments (*Early Morning, Morning, Afternoon, Evening, Night, Late Night*)

### Core Schema Fields:
- **Identifiers**: `Order_ID`, `User_ID`, `Restaurant_ID`, `Driver_ID`
- **Order Details**: `Item_Name`, `Quantity`, `Total_Price`, `Order_Value_Tier`
- **Lifecycle & Status**: `Order_Time`, `Delivery_Time`, `Delivery_Duration_Minutes`, `Order_Status` (`Delivered`, `Cancelled`, `In Transit`)
- **Fleet & Mobility**: `Driver_Vehicle` (`Bicycle`, `Motorbike`, `Car`), `Driver_Availability`, `Delivery_Speed_kmh_ANALYTICAL`
- **Spatial & Traffic**: `City`, `Traffic_Level` (`Low`, `Medium`, `High`), `Delivery_Distance_km`, `Distance_Bin`
- **Target Variables**: `Is_Delayed_TARGET` (1 if Duration > 45 min, 0 otherwise), `Delay_Minutes_TARGET` (`max(0, Duration - 45)`)

---

## 5. Key Dataset Statistics

The table below outlines the baseline operational metrics across the full 10,000-order benchmark dataset:

| Operational Metric | Value | Notes / Computation |
| :--- | :--- | :--- |
| **Total Orders** | **10,000** | Full dataset benchmark population |
| **Delivered Orders** | **8,520** | Completed fulfillment (**85.20%** completion rate) |
| **Cancelled Orders** | **980** | Order cancellations (**9.80%** cancellation rate) |
| **In-Transit Orders** | **500** | Active / pending deliveries (**5.00%** in-transit rate) |
| **Overall SLA Delay Rate** | **24.17%** | 2,417 delayed orders out of 10,000 total orders |
| **Delivered SLA Delay Rate** | **24.26%** | 2,067 delayed orders out of 8,520 completed deliveries (>45 min) |
| **Mean Delivery Duration** | **37.48 min** | All orders mean turnaround duration |
| **Delivered Mean Duration** | **37.50 min** | Mean turnaround for completed orders |
| **Median Delivery Duration**| **38.00 min** | Median turnaround for completed orders |
| **Mean Delay (Delayed Orders)**| **5.64 min** | Mean excess duration beyond 45m threshold (all delayed) |
| **Mean Delay (Delivered Delayed)**| **5.65 min** | Mean excess duration beyond 45m threshold (delivered delayed) |
| **Average Order Value (AOV)** | **EGP 268.97** | Mean transaction amount |
| **Average Delivery Distance** | **2.15 km** | Mean restaurant-to-customer distance |

---

## 6. Technology Stack

### Backend
- **Language**: Python 3.12
- **Framework**: FastAPI 0.115+
- **Data Engine**: Pandas 2.2+, NumPy 2.0+
- **Server**: Uvicorn (ASGI)
- **Validation & Schemas**: Pydantic v2
- **Testing**: Pytest 9.1+, Starlette TestClient

### Frontend
- **Framework**: React 18
- **Build Tool**: Vite 5.4
- **Language**: TypeScript 5.5+
- **Styling**: Tailwind CSS 3.4, Vanilla CSS Design Tokens
- **Icons**: Lucide React
- **Export System**: HTML5 `@media print` CSS Stylesheet

---

## 7. System Architecture

```
                                 ┌──────────────────────────────────────────────┐
                                 │          Vite + React + TypeScript           │
                                 │       Tailwind CSS + Lucide + Print CSS      │
                                 └──────────────────────┬───────────────────────┘
                                                        │
                                                  HTTP / REST API
                                                        │
                                 ┌──────────────────────▼───────────────────────┐
                                 │             FastAPI Python Backend           │
                                 │       (Python 3.12 + Pandas + NumPy)         │
                                 └──────────────────────┬───────────────────────┘
                                                        │
                                           Dynamic Analytics Engine
                                                        │
                                 ┌──────────────────────▼───────────────────────┐
                                 │      Cleaned Production Dataset (10,000)     │
                                 │   data/processed/food_delivery_10k.csv      │
                                 └──────────────────────────────────────────────┘
```

---

## 8. Backend Architecture

The backend follows a clean modular service-oriented architecture located in `src/backend/`:

```
src/backend/
├── config.py             # Global settings & dataset path configuration
├── main.py               # FastAPI application entry point & CORS configuration
├── models/
│   └── schemas.py        # Pydantic v2 data models & API response schemas
├── routers/
│   ├── analytics.py      # Analytics API router (/api/analytics/*)
│   ├── explorer.py       # Data Explorer API router (/api/explorer/*)
│   └── health.py         # System health check router (/api/health)
└── services/
    ├── analytics.py      # Dynamic pandas analytical calculation service & insights generator
    └── explorer.py       # Data pagination, column filtering, schema metadata & distribution service
```

### Key Backend Features:
- **In-Memory Caching**: Dataset loaded into Pandas DataFrame on startup for millisecond analytical responses.
- **Dynamic Query Filtering**: Standardized `filter_df()` method filters DataFrame across all query parameters before applying aggregator functions.
- **Robust Exception Handling**: Graceful fallback structures for empty filter matches and malformed parameters.

---

## 9. Frontend Architecture

The frontend is a single-page TypeScript React application located in `src/`:

```
src/
├── App.tsx               # Main application layout, state management, dashboard views
├── main.tsx              # React DOM mounting entrypoint
├── index.css             # Glassmorphism theme tokens & custom CSS components
├── services/
│   └── api.ts            # Axios/Fetch API client wrapping all 18 backend endpoints
└── vite-env.d.ts         # Vite TypeScript environment declarations
```

---

## 10. Analytics Capabilities

1. **Dynamic Metric Recalibration**: Selecting any combination of filters immediately recalculates sample size $N$, fulfillment rate, SLA delay rate, mean duration, and average order value.
2. **City Municipal Performance**: Comparative analysis across all 7 Egyptian municipalities to identify regional turnaround variations.
3. **SLA Duration Distribution**: 5-bin histogram (15–25m, 25–35m, 35–45m, 45–55m, 55–60m) featuring a visual SLA marker line at 45 minutes.
4. **Traffic Congestion Dynamics**: Evaluation of SLA delay rates across Low, Medium, and High traffic levels.
5. **Temporal Delay Patterns**: Turnaround time and delay rate tracking across 6 time-of-day segments and 7 days of the week.
6. **Fleet Mobility Analysis**: Speed ($km/h$), duration, and SLA delay comparison across Bicycles, Motorbikes, and Cars.
7. **Spatial & Distance Analysis**: Distance binning (<1km, 1-3km, 3-5km, >5km) and Pearson correlation calculation between trip distance, duration ($r = -0.0119$), and SLA delay ($r = -0.0090$).

---

## 11. Dashboard Pages & Views

1. **Overview & KPIs**: Core metric summary cards, City Delivery performance bar chart, and SLA Duration Distribution histogram.
2. **Geographic Performance**: Comprehensive Metropolitan Market Breakdown table listing all 7 Egyptian cities with completed orders, delay rates, and average order values.
3. **Traffic & Temporal**: Line chart of daily SLA delay trends and time-of-day segment cards.
4. **Diagnostic Insights**: Dynamic insight cards highlighting observed statistical patterns, sample sizes ($N$), direction indicators, and method disclaimers.
5. **Data Explorer**: Interactive raw 10,000-order preview table with pagination, column search/filter, Column Schema inspector, and Summary Distributions.
6. **Analytical Reports**: Publication-ready Phase 4 Executive Report complete with key metrics, tables, recommendations, and one-click PDF/print export.

---

## 12. API Endpoints

The FastAPI backend exposes 18 RESTful endpoints under `/api`:

### System & Health
- `GET /api/health` — System status, dataset load check, total record count.

### Analytics Engine (`/api/analytics`)
- `GET /api/analytics/overview` — Overall KPIs and summary stats (supports filter params).
- `GET /api/analytics/city` — Grouped city delivery metrics.
- `GET /api/analytics/traffic` — Grouped traffic congestion metrics.
- `GET /api/analytics/status` — Fulfillment status counts and percentages.
- `GET /api/analytics/duration-distribution` — Delivery duration histogram bins.
- `GET /api/analytics/time-of-day` — Time-of-day segment turnaround & delay rates.
- `GET /api/analytics/day-of-week` — Weekly turnaround time & delay rates.
- `GET /api/analytics/vehicle` — Fleet vehicle speed, duration & delay rates.
- `GET /api/analytics/order-quantity` — Metrics by item count (1 to 5 items).
- `GET /api/analytics/order-value` — Metrics by order value tier.
- `GET /api/analytics/distance` — Distance binning & Pearson correlation metrics.
- `GET /api/analytics/insights` — Dynamic descriptive non-causal insight items.
- `GET /api/analytics/filters` | Distinct filter options present in dataset.

### Data Explorer (`/api/explorer`)
- `GET /api/explorer/summary` — High-level metadata & entity counts (users, restaurants, drivers, cities).
- `GET /api/explorer/schema` — Metadata for all 55 dataset columns (dtype, nulls, unique values, examples).
- `GET /api/explorer/summary-stats` — Descriptive statistics for numerical and categorical columns.
- `GET /api/explorer/records` — Paginated raw record explorer with search & column filtering.

---

## 13. Filtering System

All analytical endpoints accept optional query parameters for dynamic data slicing:

| Query Parameter | Allowed Values / Format | Description |
| :--- | :--- | :--- |
| `city` | `Cairo`, `Alexandria`, `Giza`, `Mansoura`, `Tanta`, `Zagazig`, `Assiut` | Filter by delivery city |
| `traffic_level` | `Low`, `Medium`, `High` | Filter by traffic congestion |
| `vehicle` | `Bicycle`, `Motorbike`, `Car` | Filter by fleet vehicle modal type |
| `payment_method` | `Cash`, `Wallet`, `Credit Card` | Filter by customer payment method |
| `distance_bin` | `Short (<1km)`, `Medium (1-3km)`, `Long (3-5km)`, `Very Long (>5km)` | Filter by trip distance band |
| `order_value_tier`| `Budget (<100)`, `Standard (100-300)`, `Premium (300-500)`, `Luxury (>500)` | Filter by order price tier |
| `time_of_day` | `Early Morning`, `Morning`, `Afternoon`, `Evening`, `Night`, `Late Night` | Filter by 4-hour temporal segment |
| `day_of_week` | `Monday`, `Tuesday`, `Wednesday`, `Thursday`, `Friday`, `Saturday`, `Sunday` | Filter by order day of week |

---

## 14. Analytical Methodology

1. **SLA Delay Threshold**: An order is classified as delayed (`Is_Delayed_TARGET = 1`) if its `Delivery_Duration_Minutes` exceeds **45 minutes**.
2. **Completed Delivery Scoping**: Duration and SLA delay statistics are computed exclusively on completed orders (`Order_Status = 'Delivered'`).
3. **Descriptive Non-Causal Framework**: All insights report purely observational patterns ($N$, observed percentages, mean differences). The platform explicitly clarifies that observed correlations (e.g., traffic vs delay) do not imply direct physical causality without controlled A/B testing.

---

## 15. Key Findings

1. **Municipal Performance**: Delivery duration remains remarkably consistent across all 7 cities, averaging between 37.1 and 37.8 minutes. Cairo recorded the highest order volume (1,439 orders).
2. **Dominance of Fixed Operational Overhead**: Pearson correlation between trip distance and turnaround duration is near zero ($r = -0.0119$), demonstrating that kitchen preparation, order pickup, and dispatch queueing dominate total turnaround time compared to physical transit.
3. **Fleet Mobility**: Bicycles, Motorbikes, and Cars show comparable SLA delay rates (~24.0% to 24.5%), reflecting urban traffic constraints in dense Egyptian commercial sectors.
4. **Basket Size Impact**: Larger basket sizes (4–5 items) show a slight elevation in SLA delay rates (+1.2%), pointing to potential kitchen preparation bottlenecks for multi-item orders.

---

## 16. Data Limitations

1. **Synthetic Simulation Artefacts**: The dataset originated from a simulated platform. Consequently, variables such as `Traffic_Level` and `Delivery_Distance_km` display weaker correlations with delivery duration ($r \approx -0.01$) than would typically be observed in empirical sensor telemetry.
2. **Static Historical Benchmark**: Operational metrics reflect the 10,000-order benchmark file (`food_delivery_10k.csv`); real-time streaming database integration is out of scope for the current phase.

---

## 17. Testing & Verification

The project includes an automated test suite verifying backend functionality, API calculation accuracy, and TypeScript compilation.

### Run Backend Pytest Suite
```bash
.venv\Scripts\python -m pytest tests/
```
*Output: **19 passed** in 1.38 seconds.*

### Run Independent Data Parity Validation
```bash
.venv\Scripts\python tests/validate_backend_independent.py
```
*Output: **PASSED** (100% parity between API responses and direct Pandas calculations).*

### Run TypeScript Compilation Check
```bash
npx tsc --noEmit
```
*Output: **0 errors**.*

### Run Production Build
```bash
npm run build
```
*Output: **Build complete** (`dist/` generated cleanly in 10.74s).*

---

## 18. How to Run Locally

### Prerequisites
- Python 3.12+
- Node.js 18+ and `npm`

### Step 1: Clone Repository & Set Up Environment
```bash
git clone https://github.com/user/FoodDeliveryAnalytics.git
cd FoodDeliveryAnalytics

# Create and activate Python virtual environment
python -m venv .venv
# Windows PowerShell / CMD:
.venv\Scripts\activate
# macOS / Linux:
source .venv/bin/activate

# Install Python dependencies
pip install -r requirements.txt

# Install Frontend dependencies
npm install
```

### Step 2: Launch FastAPI Backend Server
```bash
.venv\Scripts\python -m uvicorn src.backend.main:app --reload --port 8000
```
Backend API will be live at: `http://localhost:8000` (Swagger docs at `http://localhost:8000/docs`).

### Step 3: Launch React Frontend Dashboard
In a second terminal window:
```bash
npm run dev
```
Dashboard will be live at: `http://localhost:5173`

---

## 19. Project Structure

```
FoodDeliveryAnalytics/
├── data/
│   ├── raw/
│   │   └── Order_delivery.csv              # Original 100k raw dataset (read-only)
│   └── processed/
│       ├── Order_delivery_cleaned.csv      # Cleaned full dataset
│       ├── Order_delivery_featured.csv     # Engineered full dataset (55 features)
│       └── food_delivery_10k.csv           # Production 10,000 benchmark dataset
├── dist/                                   # Vite production build output
├── node_modules/                           # Node.js dependencies
├── reports/                                # Analytical Markdown reports & exported charts
│   └── tables/                             # Exported KPI CSV tables
├── src/
│   ├── App.tsx                             # Main React SPA component & dashboard views
│   ├── index.css                           # Glassmorphism styling tokens & Tailwind setup
│   ├── main.tsx                            # React DOM mounting script
│   ├── analytics/                          # Standalone Python analytics generation scripts
│   ├── backend/                            # FastAPI backend application
│   │   ├── config.py                       # App settings & dataset path config
│   │   ├── main.py                         # FastAPI app entrypoint & CORS setup
│   │   ├── models/
│   │   │   └── schemas.py                  # Pydantic v2 schemas
│   │   ├── routers/
│   │   │   ├── analytics.py                # Analytics endpoints router
│   │   │   ├── explorer.py                 # Explorer endpoints router
│   │   │   └── health.py                   # Health check endpoint router
│   │   └── services/
│   │       ├── analytics.py                # Pandas analytics service & insights logic
│   │       └── explorer.py                 # Explorer pagination & schema statistics
│   ├── preprocessing/                      # Data pipeline scripts (cleaning & features)
│   └── services/
│       └── api.ts                          # Axios/Fetch frontend API client
├── tests/
│   ├── test_analytics_backend.py           # Backend Pytest test suite (19 tests)
│   ├── test_filter_scenarios.py            # Automated filter validation script
│   └── validate_backend_independent.py    # Independent Pandas vs FastAPI validation
├── package.json                            # Frontend npm configuration & scripts
├── PROJECT_AUDIT.md                        # Final project audit documentation
├── README.md                               # Project documentation (this file)
├── tailwind.config.js                      # Tailwind CSS configuration
├── tsconfig.json                           # TypeScript configuration
└── vite.config.ts                          # Vite build configuration
```

---

## 20. Current Status

The **FoodFlow Analytics** platform is fully finalized through **STEP 10 (Project Finalization)**:
- [x] Dataset cleaning, auditing, and feature engineering
- [x] Fast, dynamic FastAPI analytics backend
- [x] React single-page application frontend
- [x] Dynamic 8-dimension query filter bar
- [x] Overview KPI dashboard & distribution histograms
- [x] Delivery Analytics deep dives (Cities, Traffic, Temporal, Fleet)
- [x] Interactive Data Explorer with pagination and schema metadata
- [x] Publication-ready PDF/Print report export
- [x] Comprehensive test suite & zero TypeScript errors
- [x] Production build validation

---

## 21. Deferred AI/ML Enhancement

> ⚠️ **NOTICE ON AI/ML MODULES**:  
> Machine Learning models (e.g., XGBoost / LightGBM delay prediction classifiers, ETA duration regression models, and SHAP feature importance visualizers) are **explicitly deferred to a future project phase**.  
> The current completed repository delivers the complete core data analytics, dynamic filtering, interactive dashboard, REST API backend, and reporting platform. Predictive AI/ML pipelines will be integrated as a separate enhancement module in future updates.

---

*FoodFlow Analytics — Developed as an End-to-End Operational Analytics & Reporting Platform.*
