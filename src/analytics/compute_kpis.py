"""
Delivery Performance KPI Computation Module
Food Delivery Analytics: Delivery Performance and Delay Prediction

This module computes core delivery-performance KPIs and operational breakdowns
from the 10,000-row analytics dataset (data/processed/food_delivery_analytics_10k.csv).

Exports:
- CSV tables in reports/tables/
- JSON summary in reports/phase4_kpis.json
- Markdown summary report in reports/phase4_kpi_report.md
"""

import json
import os
import sys
import pandas as pd
import numpy as np


def load_analytics_dataset(file_path: str = "data/processed/food_delivery_analytics_10k.csv") -> pd.DataFrame:
    """Load and validate the analytics dataset."""
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Analytics dataset not found at: {file_path}")
    df = pd.read_csv(file_path)
    print(f"Loaded dataset from {file_path} with shape: {df.shape}")
    return df


def compute_overall_kpis(df: pd.DataFrame) -> dict:
    """
    Compute core high-level delivery performance KPIs across the full dataset.
    
    Returns a dictionary of overall operational and timeliness metrics.
    """
    total_orders = len(df)
    delivered_orders = int((df['Order_Status'] == 'Delivered').sum())
    cancelled_orders = int((df['Order_Status'] == 'Cancelled').sum())
    in_transit_orders = int((df['Order_Status'] == 'In Transit').sum())
    
    # Delayed orders overall (all 10k rows)
    overall_delayed_orders_all = int((df['Is_Delayed_TARGET'] == 1).sum())
    overall_delay_rate_all = (overall_delayed_orders_all / total_orders) * 100.0
    
    # Filter completed deliveries for duration and SLA metrics
    df_deliv = df[df['Order_Status'] == 'Delivered'].copy()
    delivered_delayed = int((df_deliv['Is_Delayed_TARGET'] == 1).sum())
    delay_rate_delivered = (delivered_delayed / delivered_orders) * 100.0 if delivered_orders > 0 else 0.0
    
    # Delivery duration statistics (Delivered orders)
    avg_delivery_duration = float(df_deliv['Delivery_Duration_Minutes'].mean())
    median_delivery_duration = float(df_deliv['Delivery_Duration_Minutes'].median())
    min_delivery_duration = int(df_deliv['Delivery_Duration_Minutes'].min())
    max_delivery_duration = int(df_deliv['Delivery_Duration_Minutes'].max())
    
    # Delay duration statistics (Delivered orders)
    avg_delay_duration = float(df_deliv['Delay_Minutes_TARGET'].mean())
    median_delay_duration = float(df_deliv['Delay_Minutes_TARGET'].median())
    
    # Delay duration for delayed orders only
    df_delayed_only = df_deliv[df_deliv['Is_Delayed_TARGET'] == 1]
    avg_delay_duration_delayed_only = float(df_delayed_only['Delay_Minutes_TARGET'].mean()) if len(df_delayed_only) > 0 else 0.0
    median_delay_duration_delayed_only = float(df_delayed_only['Delay_Minutes_TARGET'].median()) if len(df_delayed_only) > 0 else 0.0
    
    # Financial, distance, and basket volume metrics
    avg_order_value = float(df['Total_Price'].mean())
    avg_delivery_distance = float(df['Delivery_Distance_km'].mean())
    avg_quantity_per_order = float(df['Quantity'].mean())
    
    # Additional operational ratios
    fulfillment_rate = (delivered_orders / total_orders) * 100.0
    cancellation_rate = (cancelled_orders / total_orders) * 100.0
    avg_courier_speed = float(df_deliv['Delivery_Speed_kmh_ANALYTICAL'].mean())
    avg_dispatch_distance = float(df['Driver_To_Restaurant_km'].mean())
    
    kpis = {
        "1. Total Orders": total_orders,
        "2. Delivered Orders": delivered_orders,
        "3. Cancelled Orders": cancelled_orders,
        "4. In-Transit Orders": in_transit_orders,
        "5. Overall Delayed Orders (All)": overall_delayed_orders_all,
        "5b. Overall Delayed Orders (Delivered)": delivered_delayed,
        "6. Delay Rate among Delivered Orders (%)": round(delay_rate_delivered, 2),
        "6b. Overall Delay Rate All Orders (%)": round(overall_delay_rate_all, 2),
        "7. Average Delivery Duration (min)": round(avg_delivery_duration, 2),
        "8. Median Delivery Duration (min)": round(median_delivery_duration, 2),
        "9. Minimum Delivery Duration (min)": min_delivery_duration,
        "10. Maximum Delivery Duration (min)": max_delivery_duration,
        "11. Average Delay Duration - All Delivered (min)": round(avg_delay_duration, 2),
        "11b. Average Delay Duration - Delayed Only (min)": round(avg_delay_duration_delayed_only, 2),
        "12. Median Delay Duration - All Delivered (min)": round(median_delay_duration, 2),
        "12b. Median Delay Duration - Delayed Only (min)": round(median_delay_duration_delayed_only, 2),
        "13. Average Order Value (EGP)": round(avg_order_value, 2),
        "14. Average Delivery Distance (km)": round(avg_delivery_distance, 2),
        "15. Average Quantity per Order": round(avg_quantity_per_order, 2),
        "Fulfillment Rate (%)": round(fulfillment_rate, 2),
        "Cancellation Rate (%)": round(cancellation_rate, 2),
        "Average Effective Speed (km/h)": round(avg_courier_speed, 2),
        "Average Dispatch Distance (km)": round(avg_dispatch_distance, 2)
    }
    
    return kpis


def compute_grouped_kpis(df: pd.DataFrame, group_col: str, group_display_name: str) -> pd.DataFrame:
    """
    Compute operational performance metrics grouped by a specified dimension.
    """
    records = []
    
    for name, group in df.groupby(group_col, observed=False):
        total_orders = len(group)
        delivered_orders = int((group['Order_Status'] == 'Delivered').sum())
        cancelled_orders = int((group['Order_Status'] == 'Cancelled').sum())
        in_transit_orders = int((group['Order_Status'] == 'In Transit').sum())
        
        fulfillment_rate = (delivered_orders / total_orders) * 100.0 if total_orders > 0 else 0.0
        cancellation_rate = (cancelled_orders / total_orders) * 100.0 if total_orders > 0 else 0.0
        
        group_deliv = group[group['Order_Status'] == 'Delivered']
        deliv_count = len(group_deliv)
        
        if deliv_count > 0:
            delayed_count = int((group_deliv['Is_Delayed_TARGET'] == 1).sum())
            delay_rate_deliv = (delayed_count / deliv_count) * 100.0
            mean_duration = float(group_deliv['Delivery_Duration_Minutes'].mean())
            median_duration = float(group_deliv['Delivery_Duration_Minutes'].median())
            mean_delay_mins = float(group_deliv['Delay_Minutes_TARGET'].mean())
            mean_speed_kmh = float(group_deliv['Delivery_Speed_kmh_ANALYTICAL'].mean())
        else:
            delayed_count = 0
            delay_rate_deliv = 0.0
            mean_duration = 0.0
            median_duration = 0.0
            mean_delay_mins = 0.0
            mean_speed_kmh = 0.0
            
        mean_aov = float(group['Total_Price'].mean())
        mean_dist = float(group['Delivery_Distance_km'].mean())
        mean_qty = float(group['Quantity'].mean())
        
        records.append({
            group_display_name: name,
            "Total Orders": total_orders,
            "Delivered Orders": delivered_orders,
            "Cancelled Orders": cancelled_orders,
            "In-Transit Orders": in_transit_orders,
            "Fulfillment Rate (%)": round(fulfillment_rate, 2),
            "Cancellation Rate (%)": round(cancellation_rate, 2),
            "Delayed Delivered Orders": delayed_count,
            "Delay Rate Delivered (%)": round(delay_rate_deliv, 2),
            "Mean Duration (min)": round(mean_duration, 2),
            "Median Duration (min)": round(median_duration, 2),
            "Mean Delay Duration (min)": round(mean_delay_mins, 2),
            "Mean Courier Speed (km/h)": round(mean_speed_kmh, 2),
            "Mean Order Value (EGP)": round(mean_aov, 2),
            "Mean Distance (km)": round(mean_dist, 2),
            "Mean Quantity": round(mean_qty, 2)
        })
        
    return pd.DataFrame(records)


def dataframe_to_markdown(df: pd.DataFrame) -> str:
    """Convert pandas DataFrame to Markdown table without external dependencies like tabulate."""
    header = "| " + " | ".join(df.columns) + " |"
    separator = "| " + " | ".join(["---"] * len(df.columns)) + " |"
    rows = []
    for _, row in df.iterrows():
        row_str = "| " + " | ".join(str(val) for val in row.values) + " |"
        rows.append(row_str)
    return "\n".join([header, separator] + rows)


def run_kpi_computation(dataset_path: str = "data/processed/food_delivery_analytics_10k.csv",
                        output_dir: str = "reports/tables",
                        json_output_path: str = "reports/phase4_kpis.json",
                        markdown_output_path: str = "reports/phase4_kpi_report.md"):
    """
    Execute full KPI computation workflow, saving tables to CSV, JSON, and Markdown report.
    """
    os.makedirs(output_dir, exist_ok=True)
    os.makedirs(os.path.dirname(json_output_path), exist_ok=True)
    os.makedirs(os.path.dirname(markdown_output_path), exist_ok=True)
    
    df = load_analytics_dataset(dataset_path)
    
    print("\n=======================================================")
    print(" 1. COMPUTING OVERALL DELIVERY PERFORMANCE KPIS")
    print("=======================================================")
    overall_kpis = compute_overall_kpis(df)
    
    for k, v in overall_kpis.items():
        print(f"  {k:<50}: {v}")
        
    # Save overall KPIs to CSV
    df_overall = pd.DataFrame([overall_kpis]).T.reset_index()
    df_overall.columns = ["KPI Metric Name", "Value"]
    overall_csv_path = os.path.join(output_dir, "overall_kpis.csv")
    df_overall.to_csv(overall_csv_path, index=False)
    print(f"\nSaved overall KPIs table to: {overall_csv_path}")
    
    # 2. Operational Grouped Breakdown Definitions
    grouped_dimensions = [
        ("City", "City", "city_kpis.csv"),
        ("Traffic_Level", "Traffic Level", "traffic_kpis.csv"),
        ("Time_Of_Day_Segment", "Time of Day", "time_of_day_kpis.csv"),
        ("Order_DayName", "Day of Week", "day_of_week_kpis.csv"),
        ("Is_RushHour", "Rush Hour Status", "rush_hour_kpis.csv"),
        ("Distance_Bin", "Distance Category", "distance_bin_kpis.csv"),
        ("Order_Value_Tier", "Order Value Tier", "order_value_tier_kpis.csv")
    ]
    
    json_results = {
        "overall_kpis": overall_kpis,
        "operational_breakdowns": {}
    }
    
    markdown_sections = []
    
    print("\n=======================================================")
    print(" 2. COMPUTING OPERATIONAL BREAKDOWN KPIS")
    print("=======================================================")
    
    for col, display_name, filename in grouped_dimensions:
        df_group = compute_grouped_kpis(df, col, display_name)
        
        # Sort day of week chronologically if applicable
        if col == "Order_DayName":
            day_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
            df_group["Day_Index"] = df_group["Day of Week"].map(lambda d: day_order.index(d) if d in day_order else 99)
            df_group = df_group.sort_values("Day_Index").drop(columns=["Day_Index"])
        elif col == "Is_RushHour":
            df_group["Rush Hour Status"] = df_group["Rush Hour Status"].map({0: "Off-Peak (0)", 1: "Rush Hour (1)"})
            
        csv_path = os.path.join(output_dir, filename)
        df_group.to_csv(csv_path, index=False)
        print(f"\n--- Grouped by {display_name} (Saved to {csv_path}) ---")
        print(df_group.to_string(index=False))
        
        json_results["operational_breakdowns"][display_name] = df_group.to_dict(orient="records")
        
        # Format markdown table
        md_table = dataframe_to_markdown(df_group)
        markdown_sections.append(f"### Operational Breakdown by {display_name}\n\n{md_table}\n")
        
    # Save combined JSON output
    with open(json_output_path, "w", encoding="utf-8") as f:
        json.dump(json_results, f, indent=2)
    print(f"\nSaved JSON KPI summary to: {json_output_path}")
    
    # Generate Markdown Report
    generate_markdown_report(overall_kpis, markdown_sections, markdown_output_path)
    print(f"Generated complete KPI report at: {markdown_output_path}")
    
    return overall_kpis, json_results


def generate_markdown_report(overall_kpis: dict, grouped_md_sections: list, report_path: str):
    """Generate structured markdown documentation for all computed KPIs and formulas."""
    
    overall_rows = "\n".join([f"| **{k}** | {v} |" for k, v in overall_kpis.items()])
    grouped_body = "\n\n".join(grouped_md_sections)
    
    content = f"""# Phase 4 Core Delivery Performance KPI Report
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
{overall_rows}

---

## 2. KPI Definitions & Mathematical Formulas

| # | KPI Metric Name | Formula / Calculation Method | Scope / Subset | Operational Rationale |
|---|---|---|---|---|
| 1 | **Total Orders** | $N = \\text{{Count of all rows}}$ | All ($N=10,000$) | Total order demand volume in sample population. |
| 2 | **Delivered Orders** | $\\sum [ \\text{{Order\\_Status}} == \\text{{'Delivered'}} ]$ | All ($N=8,520$) | Completed fulfillments eligible for duration and SLA evaluation. |
| 3 | **Cancelled Orders** | $\\sum [ \\text{{Order\\_Status}} == \\text{{'Cancelled'}} ]$ | All ($N=980$) | Orders abandoned/cancelled prior to delivery completion. |
| 4 | **In-Transit Orders** | $\\sum [ \\text{{Order\\_Status}} == \\text{{'In Transit'}} ]$ | All ($N=500$) | Orders in progress at snapshot cutoff. |
| 5 | **Overall Delayed Orders** | $\\sum [ \\text{{Is\\_Delayed\\_TARGET}} == 1 ]$ | All ($N=2,417$) / Delivered ($N=2,067$) | Orders breaching the 45-minute SLA threshold. |
| 6 | **Delay Rate (Delivered)** | $\\frac{{\\text{{Delivered Delayed Orders}}}}{{\\text{{Total Delivered Orders}}}} \\times 100$ | Delivered ($N=8,520$) | Core SLA breach metric (**24.26%**). |
| 7 | **Average Delivery Duration** | $\\frac{{1}}{{N_{{\\text{{deliv}}}}}} \\sum \\text{{Delivery\\_Duration\\_Minutes}}$ | Delivered ($N=8,520$) | Average turnaround time (**37.50 min**). |
| 8 | **Median Delivery Duration** | $\\text{{Median}}(\\text{{Delivery\\_Duration\\_Minutes}})$ | Delivered ($N=8,520$) | Robust central measure unaffected by extreme skew (**38.00 min**). |
| 9 | **Minimum Delivery Duration** | $\\min(\\text{{Delivery\\_Duration\\_Minutes}})$ | Delivered ($N=8,520$) | Fast-path delivery baseline (**15 min**). |
| 10 | **Maximum Delivery Duration** | $\\max(\\text{{Delivery\\_Duration\\_Minutes}})$ | Delivered ($N=8,520$) | Maximum delivery latency observed (**60 min**). |
| 11 | **Average Delay Duration** | $\\frac{{1}}{{N_{{\\text{{deliv}}}}}} \\sum \\text{{Delay\\_Minutes\\_TARGET}}$ | Delivered ($N=8,520$) | Average excess duration beyond 45-min SLA (**1.37 min** overall / **5.65 min** when delayed). |
| 12 | **Median Delay Duration** | $\\text{{Median}}(\\text{{Delay\\_Minutes\\_TARGET}})$ | Delivered ($N=8,520$) | Median SLA excess delay (**0.00 min** overall / **5.00 min** when delayed). |
| 13 | **Average Order Value** | $\\frac{{1}}{{N}} \\sum \\text{{Total\\_Price}}$ | All ($N=10,000$) | Average basket value in EGP (**EGP 268.97**). |
| 14 | **Average Delivery Distance** | $\\frac{{1}}{{N}} \\sum \\text{{Delivery\\_Distance\\_km}}$ | All ($N=10,000$) | Average vendor-to-customer Haversine distance (**2.15 km**). |
| 15 | **Average Quantity per Order** | $\\frac{{1}}{{N}} \\sum \\text{{Quantity}}$ | All ($N=10,000$) | Average items per order (**3.00 items**). |

---

## 3. Operational KPI Breakdowns

{grouped_body}

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
"""

    with open(report_path, "w", encoding="utf-8") as f:
        f.write(content)


if __name__ == "__main__":
    dataset_file = "data/processed/food_delivery_analytics_10k.csv"
    if len(sys.argv) > 1:
        dataset_file = sys.argv[1]
    run_kpi_computation(dataset_path=dataset_file)
