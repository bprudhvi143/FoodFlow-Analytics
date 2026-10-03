"""
Delivery Performance Exploratory Visualization Suite
Food Delivery Analytics: Delivery Performance and Delay Prediction

This script generates 11 core exploratory visualizations analyzing delivery performance,
durations, delay rates, spatial factors, temporal trends, and operational dimensions.

All figures are saved to: reports/phase4/charts/
"""

import os
import sys
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# Set global visual style
sns.set_theme(style="whitegrid", font_scale=1.1)
plt.rcParams['font.sans-serif'] = 'Arial'
plt.rcParams['axes.edgecolor'] = '#cccccc'
plt.rcParams['axes.linewidth'] = 0.8

# Color Palette Definitions
PRIMARY_COLOR = "#1f77b4"     # Deep Blue
SECONDARY_COLOR = "#ff7f0e"   # Orange
DELAY_COLOR = "#d62728"       # Crimson Red
ONTIME_COLOR = "#2ca02c"      # Emerald Green
ACCENT_COLOR = "#9467bd"      # Purple


def load_dataset(file_path: str = "data/processed/food_delivery_analytics_10k.csv") -> pd.DataFrame:
    """Load analytics dataset."""
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Dataset not found at {file_path}")
    df = pd.read_csv(file_path)
    return df


def generate_visualizations(df: pd.DataFrame, output_dir: str = "reports/phase4/charts"):
    """Generate and save all 11 core exploratory charts."""
    os.makedirs(output_dir, exist_ok=True)
    print(f"Generating 11 core visualizations in: {output_dir}")

    # Filter completed deliveries for duration and delay metrics
    df_deliv = df[df['Order_Status'] == 'Delivered'].copy()
    overall_delay_rate = df_deliv['Is_Delayed_TARGET'].mean() * 100

    # -------------------------------------------------------------------------
    # Chart 1: Delivery Duration Distribution
    # -------------------------------------------------------------------------
    fig, ax = plt.subplots(figsize=(10, 6))
    sns.histplot(df_deliv['Delivery_Duration_Minutes'], bins=30, kde=True, ax=ax,
                 color=PRIMARY_COLOR, edgecolor='white', alpha=0.7)
    
    ax.axvline(45, color=DELAY_COLOR, linestyle='--', linewidth=2.5, label='45-min SLA Threshold')
    mean_val = df_deliv['Delivery_Duration_Minutes'].mean()
    median_val = df_deliv['Delivery_Duration_Minutes'].median()
    ax.axvline(mean_val, color='#2c3e50', linestyle='-', linewidth=1.5, label=f'Mean ({mean_val:.1f} min)')
    ax.axvline(median_val, color='#8e44ad', linestyle=':', linewidth=1.5, label=f'Median ({median_val:.1f} min)')
    
    ax.set_title("Overall Delivery Duration Distribution & 45-Min SLA Threshold", fontsize=14, fontweight='bold', pad=15)
    ax.set_xlabel("Delivery Duration (Minutes)", fontsize=12)
    ax.set_ylabel("Number of Delivered Orders", fontsize=12)
    ax.legend(frameon=True, facecolor='white', framealpha=0.9)
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, "01_delivery_duration_distribution.png"), dpi=300)
    plt.close()
    print("  [OK] Saved 01_delivery_duration_distribution.png")

    # -------------------------------------------------------------------------
    # Chart 2: Delay vs Non-Delay Distribution
    # -------------------------------------------------------------------------
    fig, ax = plt.subplots(figsize=(8, 6))
    delay_counts = df_deliv['Is_Delayed_TARGET'].value_counts().sort_index()
    labels = ['On-Time (<=45 min)', 'Delayed (>45 min)']
    colors = [ONTIME_COLOR, DELAY_COLOR]
    
    wedges, texts, autotexts = ax.pie(delay_counts, labels=labels, autopct='%1.1f%%', startangle=140,
                                      colors=colors, wedgeprops=dict(width=0.4, edgecolor='white', linewidth=2),
                                      textprops=dict(fontsize=12, fontweight='bold'))
    
    plt.setp(autotexts, size=11, weight="bold", color="white")
    ax.set_title("SLA Delivery Performance Breakdown (Delivered Orders, N=8,520)", fontsize=14, fontweight='bold', pad=15)
    
    total_deliv = len(df_deliv)
    delayed_num = delay_counts.get(1, 0)
    ontime_num = delay_counts.get(0, 0)
    ax.text(0, 0, f"Total Delivered\n{total_deliv:,}\n\nOn-Time: {ontime_num:,}\nDelayed: {delayed_num:,}",
            ha='center', va='center', fontsize=11, color='#333333', fontweight='medium')
    
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, "02_delay_vs_nondelay_distribution.png"), dpi=300)
    plt.close()
    print("  [OK] Saved 02_delay_vs_nondelay_distribution.png")

    # -------------------------------------------------------------------------
    # Chart 3: Delivery Duration by City
    # -------------------------------------------------------------------------
    fig, ax = plt.subplots(figsize=(10, 6))
    city_order = sorted(df_deliv['City'].unique())
    sns.boxplot(data=df_deliv, x='City', y='Delivery_Duration_Minutes', hue='City', order=city_order, ax=ax,
                palette="Blues_r", boxprops=dict(alpha=0.8), showmeans=True, legend=False,
                meanprops=dict(marker='o', markerfacecolor='red', markeredgecolor='red', markersize=6))
    
    ax.set_title("Delivery Duration Distribution Across Cities", fontsize=14, fontweight='bold', pad=15)
    ax.set_xlabel("City", fontsize=12)
    ax.set_ylabel("Delivery Duration (Minutes)", fontsize=12)
    ax.axhline(45, color=DELAY_COLOR, linestyle='--', label='45-min SLA Cutoff', linewidth=1.5)
    ax.legend(loc='upper right')
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, "03_delivery_duration_by_city.png"), dpi=300)
    plt.close()
    print("  [OK] Saved 03_delivery_duration_by_city.png")

    # -------------------------------------------------------------------------
    # Chart 4: Delay Rate by City
    # -------------------------------------------------------------------------
    fig, ax = plt.subplots(figsize=(10, 6))
    city_delay = df_deliv.groupby('City')['Is_Delayed_TARGET'].mean() * 100
    city_delay = city_delay.sort_values(ascending=False)
    
    bars = ax.bar(city_delay.index, city_delay.values, color=PRIMARY_COLOR, width=0.6, alpha=0.85, edgecolor='#1b4f72')
    ax.axhline(overall_delay_rate, color=DELAY_COLOR, linestyle='--', linewidth=1.8,
               label=f'Overall Mean Delay Rate ({overall_delay_rate:.2f}%)')
    
    for bar in bars:
        height = bar.get_height()
        ax.annotate(f'{height:.2f}%',
                    xy=(bar.get_x() + bar.get_width() / 2, height),
                    xytext=(0, 4),
                    textcoords="offset points",
                    ha='center', va='bottom', fontsize=10, fontweight='bold')
        
    ax.set_title("SLA Delay Rate by City (%)", fontsize=14, fontweight='bold', pad=15)
    ax.set_xlabel("City", fontsize=12)
    ax.set_ylabel("Delay Rate (%)", fontsize=12)
    ax.set_ylim(0, max(city_delay.values) * 1.25)
    ax.legend(loc='upper right')
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, "04_delay_rate_by_city.png"), dpi=300)
    plt.close()
    print("  [OK] Saved 04_delay_rate_by_city.png")

    # -------------------------------------------------------------------------
    # Chart 5: Delivery Duration by Traffic Level
    # -------------------------------------------------------------------------
    fig, ax = plt.subplots(figsize=(9, 6))
    traffic_order = ['Low', 'Medium', 'High']
    sns.boxplot(data=df_deliv, x='Traffic_Level', y='Delivery_Duration_Minutes', hue='Traffic_Level', order=traffic_order, ax=ax,
                palette=["#2ecc71", "#f39c12", "#e74c3c"], boxprops=dict(alpha=0.8), showmeans=True, legend=False,
                meanprops=dict(marker='o', markerfacecolor='black', markeredgecolor='black', markersize=6))
    
    ax.set_title("Delivery Duration Distribution by Traffic Congestion Level", fontsize=14, fontweight='bold', pad=15)
    ax.set_xlabel("Traffic Level", fontsize=12)
    ax.set_ylabel("Delivery Duration (Minutes)", fontsize=12)
    ax.axhline(45, color=DELAY_COLOR, linestyle='--', label='45-min SLA Cutoff', linewidth=1.5)
    ax.legend(loc='upper right')
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, "05_delivery_duration_by_traffic.png"), dpi=300)
    plt.close()
    print("  [OK] Saved 05_delivery_duration_by_traffic.png")

    # -------------------------------------------------------------------------
    # Chart 6: Delay Rate by Traffic Level
    # -------------------------------------------------------------------------
    fig, ax = plt.subplots(figsize=(9, 6))
    traffic_delay = df_deliv.groupby('Traffic_Level')['Is_Delayed_TARGET'].mean().reindex(traffic_order) * 100
    
    bars = ax.bar(traffic_delay.index, traffic_delay.values, color=["#2ecc71", "#f39c12", "#e74c3c"],
                  width=0.55, alpha=0.85, edgecolor='black')
    
    for bar in bars:
        height = bar.get_height()
        ax.annotate(f'{height:.2f}%',
                    xy=(bar.get_x() + bar.get_width() / 2, height),
                    xytext=(0, 4),
                    textcoords="offset points",
                    ha='center', va='bottom', fontsize=11, fontweight='bold')
        
    ax.axhline(overall_delay_rate, color='#2c3e50', linestyle='--', label=f'Overall Average ({overall_delay_rate:.2f}%)')
    ax.set_title("SLA Delay Rate by Traffic Congestion Level (%)", fontsize=14, fontweight='bold', pad=15)
    ax.set_xlabel("Traffic Level", fontsize=12)
    ax.set_ylabel("Delay Rate (%)", fontsize=12)
    ax.set_ylim(0, max(traffic_delay.values) * 1.25)
    ax.legend(loc='upper right')
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, "06_delay_rate_by_traffic.png"), dpi=300)
    plt.close()
    print("  [OK] Saved 06_delay_rate_by_traffic.png")

    # -------------------------------------------------------------------------
    # Chart 7: Delivery Duration vs Delivery Distance
    # -------------------------------------------------------------------------
    fig, ax = plt.subplots(figsize=(10, 6))
    
    sns.regplot(data=df_deliv, x='Delivery_Distance_km', y='Delivery_Duration_Minutes', ax=ax,
                scatter_kws={'alpha': 0.25, 'color': PRIMARY_COLOR, 's': 20},
                line_kws={'color': DELAY_COLOR, 'linewidth': 2, 'label': 'Trend Line'})
    
    ax.axhline(45, color='#2c3e50', linestyle='--', label='45-min SLA Cutoff', linewidth=1.5)
    ax.set_title("Delivery Duration vs Delivery Distance (km)", fontsize=14, fontweight='bold', pad=15)
    ax.set_xlabel("Delivery Distance (km)", fontsize=12)
    ax.set_ylabel("Delivery Duration (Minutes)", fontsize=12)
    ax.legend(loc='upper right')
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, "07_duration_vs_distance.png"), dpi=300)
    plt.close()
    print("  [OK] Saved 07_duration_vs_distance.png")

    # -------------------------------------------------------------------------
    # Chart 8: Delay Rate by Time of Day
    # -------------------------------------------------------------------------
    fig, ax = plt.subplots(figsize=(10, 6))
    tod_order = ['Early Morning', 'Morning', 'Afternoon', 'Evening', 'Night', 'Late Night']
    tod_delay = df_deliv.groupby('Time_Of_Day_Segment')['Is_Delayed_TARGET'].mean().reindex(tod_order) * 100
    
    bars = ax.bar(tod_delay.index, tod_delay.values, color='#34495e', width=0.6, alpha=0.85, edgecolor='black')
    
    for bar in bars:
        height = bar.get_height()
        ax.annotate(f'{height:.2f}%',
                    xy=(bar.get_x() + bar.get_width() / 2, height),
                    xytext=(0, 4),
                    textcoords="offset points",
                    ha='center', va='bottom', fontsize=10, fontweight='bold')
        
    ax.axhline(overall_delay_rate, color=DELAY_COLOR, linestyle='--', label=f'Overall Average ({overall_delay_rate:.2f}%)')
    ax.set_title("SLA Delay Rate across Time of Day Segments (%)", fontsize=14, fontweight='bold', pad=15)
    ax.set_xlabel("Time of Day Segment", fontsize=12)
    ax.set_ylabel("Delay Rate (%)", fontsize=12)
    ax.set_ylim(0, max(tod_delay.values) * 1.25)
    ax.legend(loc='upper right')
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, "08_delay_rate_by_time_of_day.png"), dpi=300)
    plt.close()
    print("  [OK] Saved 08_delay_rate_by_time_of_day.png")

    # -------------------------------------------------------------------------
    # Chart 9: Delay Rate by Day of Week
    # -------------------------------------------------------------------------
    fig, ax = plt.subplots(figsize=(10, 6))
    dow_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    dow_delay = df_deliv.groupby('Order_DayName')['Is_Delayed_TARGET'].mean().reindex(dow_order) * 100
    
    ax.plot(dow_delay.index, dow_delay.values, marker='o', markersize=8, color=PRIMARY_COLOR,
            linewidth=2.5, label='Daily Delay Rate (%)')
    
    for i, (day, val) in enumerate(dow_delay.items()):
        ax.annotate(f'{val:.2f}%', xy=(i, val), xytext=(0, 8), textcoords="offset points",
                    ha='center', va='bottom', fontsize=10, fontweight='bold', color='#1b4f72')
        
    ax.axhline(overall_delay_rate, color=DELAY_COLOR, linestyle='--', label=f'Overall Average ({overall_delay_rate:.2f}%)')
    ax.set_title("SLA Delay Rate Trend Across Days of the Week (%)", fontsize=14, fontweight='bold', pad=15)
    ax.set_xlabel("Day of Week", fontsize=12)
    ax.set_ylabel("Delay Rate (%)", fontsize=12)
    ax.set_ylim(min(dow_delay.values) * 0.85, max(dow_delay.values) * 1.15)
    ax.legend(loc='upper right')
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, "09_delay_rate_by_day_of_week.png"), dpi=300)
    plt.close()
    print("  [OK] Saved 09_delay_rate_by_day_of_week.png")

    # -------------------------------------------------------------------------
    # Chart 10: Delivery Duration by Order Value Tier
    # -------------------------------------------------------------------------
    fig, ax = plt.subplots(figsize=(10, 6))
    tier_order = ['Budget (<100)', 'Standard (100-300)', 'Premium (300-500)', 'Luxury (>500)']
    sns.boxplot(data=df_deliv, x='Order_Value_Tier', y='Delivery_Duration_Minutes', hue='Order_Value_Tier', order=tier_order, ax=ax,
                palette="Purples_r", boxprops=dict(alpha=0.8), showmeans=True, legend=False,
                meanprops=dict(marker='o', markerfacecolor='black', markeredgecolor='black', markersize=6))
    
    ax.set_title("Delivery Duration Distribution by Order Value Tier", fontsize=14, fontweight='bold', pad=15)
    ax.set_xlabel("Order Value Tier (EGP)", fontsize=12)
    ax.set_ylabel("Delivery Duration (Minutes)", fontsize=12)
    ax.axhline(45, color=DELAY_COLOR, linestyle='--', label='45-min SLA Cutoff', linewidth=1.5)
    ax.legend(loc='upper right')
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, "10_duration_by_order_value_tier.png"), dpi=300)
    plt.close()
    print("  [OK] Saved 10_duration_by_order_value_tier.png")

    # -------------------------------------------------------------------------
    # Chart 11: Delay Rate by Rush-Hour Status
    # -------------------------------------------------------------------------
    fig, ax = plt.subplots(figsize=(8, 6))
    rush_delay = df_deliv.groupby('Is_RushHour')['Is_Delayed_TARGET'].mean() * 100
    labels = ['Off-Peak Hours (0)', 'Rush Hour (1)']
    
    bars = ax.bar(labels, rush_delay.values, color=['#27ae60', '#c0392b'], width=0.5, alpha=0.85, edgecolor='black')
    
    for bar in bars:
        height = bar.get_height()
        ax.annotate(f'{height:.2f}%',
                    xy=(bar.get_x() + bar.get_width() / 2, height),
                    xytext=(0, 4),
                    textcoords="offset points",
                    ha='center', va='bottom', fontsize=11, fontweight='bold')
        
    ax.axhline(overall_delay_rate, color='#2c3e50', linestyle='--', label=f'Overall Average ({overall_delay_rate:.2f}%)')
    ax.set_title("SLA Delay Rate Comparison: Rush Hour vs Off-Peak (%)", fontsize=14, fontweight='bold', pad=15)
    ax.set_xlabel("Operational Rush Hour Status", fontsize=12)
    ax.set_ylabel("Delay Rate (%)", fontsize=12)
    ax.set_ylim(0, max(rush_delay.values) * 1.3)
    ax.legend(loc='upper right')
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, "11_delay_rate_by_rush_hour.png"), dpi=300)
    plt.close()
    print("  [OK] Saved 11_delay_rate_by_rush_hour.png")

    print("\nAll 11 exploratory visualizations successfully created and saved!")


if __name__ == "__main__":
    dataset_path = "data/processed/food_delivery_analytics_10k.csv"
    if len(sys.argv) > 1:
        dataset_path = sys.argv[1]
    df = load_dataset(dataset_path)
    generate_visualizations(df)
