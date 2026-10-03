"""
Analytics Calculation Service for FoodFlow Analytics.
Loads food_delivery_10k.csv and provides dynamic calculation routines.
"""

import os
import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional

from src.backend.config import settings
from src.backend.models.schemas import (
    OverviewAnalytics, CityAnalyticsItem, TrafficAnalyticsItem, StatusAnalyticsItem,
    DurationBinItem, TimeOfDayAnalyticsItem, DayOfWeekAnalyticsItem, VehicleAnalyticsItem,
    OrderQuantityAnalyticsItem, OrderValueAnalyticsItem, DistanceAnalyticsResponse, DistanceBinItem,
    InsightItem, FiltersResponse
)


class AnalyticsService:
    def __init__(self, csv_path: str = settings.DATASET_PATH):
        self.csv_path = csv_path
        self._df: Optional[pd.DataFrame] = None
        self.load_dataset()

    def load_dataset(self):
        if not os.path.exists(self.csv_path):
            # Fallback check
            alt_path = "data/processed/food_delivery_10k.csv" if os.path.exists("data/processed/food_delivery_10k.csv") else "Datasets/food_delivery_10k.csv"
            if os.path.exists(alt_path):
                self.csv_path = alt_path
            else:
                raise FileNotFoundError(f"Analytics dataset not found at {self.csv_path}")

        self._df = pd.read_csv(self.csv_path)

    @property
    def df(self) -> pd.DataFrame:
        if self._df is None:
            self.load_dataset()
        return self._df

    def filter_df(
        self,
        city: Optional[str] = None,
        traffic_level: Optional[str] = None,
        time_of_day: Optional[str] = None,
        day_of_week: Optional[str] = None,
        vehicle: Optional[str] = None,
        payment_method: Optional[str] = None,
        distance_bin: Optional[str] = None,
        order_value_tier: Optional[str] = None,
        is_rush_hour: Optional[int] = None
    ) -> pd.DataFrame:
        """Apply optional query parameter filters to the dataset."""
        filtered = self.df.copy()

        if city:
            filtered = filtered[filtered['City'].str.lower() == city.lower()]
        if traffic_level:
            filtered = filtered[filtered['Traffic_Level'].str.lower() == traffic_level.lower()]
        if time_of_day:
            filtered = filtered[filtered['Time_Of_Day_Segment'].str.lower() == time_of_day.lower()]
        if day_of_week:
            filtered = filtered[filtered['Order_DayName'].str.lower() == day_of_week.lower()]
        if vehicle:
            filtered = filtered[filtered['Driver_Vehicle'].str.lower() == vehicle.lower()]
        if payment_method:
            filtered = filtered[filtered['Payment_Method'].str.lower() == payment_method.lower()]
        if distance_bin:
            filtered = filtered[filtered['Distance_Bin'].str.lower() == distance_bin.lower()]
        if order_value_tier:
            filtered = filtered[filtered['Order_Value_Tier'].str.lower() == order_value_tier.lower()]
        if is_rush_hour is not None:
            filtered = filtered[filtered['Is_RushHour'] == is_rush_hour]

        return filtered

    def get_overview(self, df: Optional[pd.DataFrame] = None) -> OverviewAnalytics:
        d = df if df is not None else self.df
        total_orders = len(d)
        if total_orders == 0:
            return OverviewAnalytics(
                total_orders=0, delivered_orders=0, cancelled_orders=0, in_transit_orders=0,
                delivery_completion_rate=0.0, cancellation_rate=0.0, in_transit_rate=0.0,
                delay_rate=0.0, overall_delay_rate=0.0, average_delivery_duration=0.0,
                median_delivery_duration=0.0, average_delay_among_delayed_orders=0.0,
                average_order_value=0.0, average_delivery_distance=0.0, average_quantity=0.0
            )

        delivered = int((d['Order_Status'] == 'Delivered').sum())
        cancelled = int((d['Order_Status'] == 'Cancelled').sum())
        in_transit = int((d['Order_Status'] == 'In Transit').sum())

        comp_rate = round((delivered / total_orders) * 100.0, 2)
        canc_rate = round((cancelled / total_orders) * 100.0, 2)
        intransit_rate = round((in_transit / total_orders) * 100.0, 2)
        overall_delay_rate = round(((d['Is_Delayed_TARGET'] == 1).sum() / total_orders) * 100.0, 2)

        deliv_df = d[d['Order_Status'] == 'Delivered']
        if len(deliv_df) > 0:
            delay_rate = round((deliv_df['Is_Delayed_TARGET'] == 1).mean() * 100.0, 2)
            avg_dur = round(float(deliv_df['Delivery_Duration_Minutes'].mean()), 2)
            med_dur = round(float(deliv_df['Delivery_Duration_Minutes'].median()), 2)

            delayed_only = deliv_df[deliv_df['Is_Delayed_TARGET'] == 1]
            avg_delay_delayed = round(float(delayed_only['Delay_Minutes_TARGET'].mean()), 2) if len(delayed_only) > 0 else 0.0
        else:
            delay_rate = 0.0
            avg_dur = 0.0
            med_dur = 0.0
            avg_delay_delayed = 0.0

        avg_aov = round(float(d['Total_Price'].mean()), 2)
        avg_dist = round(float(d['Delivery_Distance_km'].mean()), 2)
        avg_qty = round(float(d['Quantity'].mean()), 2)

        return OverviewAnalytics(
            total_orders=total_orders,
            delivered_orders=delivered,
            cancelled_orders=cancelled,
            in_transit_orders=in_transit,
            delivery_completion_rate=comp_rate,
            cancellation_rate=canc_rate,
            in_transit_rate=intransit_rate,
            delay_rate=delay_rate,
            overall_delay_rate=overall_delay_rate,
            average_delivery_duration=avg_dur,
            median_delivery_duration=med_dur,
            average_delay_among_delayed_orders=avg_delay_delayed,
            average_order_value=avg_aov,
            average_delivery_distance=avg_dist,
            average_quantity=avg_qty
        )

    def get_city_analytics(self, df: Optional[pd.DataFrame] = None) -> List[CityAnalyticsItem]:
        d = df if df is not None else self.df
        results = []
        for city_name, group in d.groupby('City', observed=False):
            order_count = len(group)
            deliv_group = group[group['Order_Status'] == 'Delivered']
            
            if len(deliv_group) > 0:
                avg_dur = round(float(deliv_group['Delivery_Duration_Minutes'].mean()), 2)
                delay_rate = round(float(deliv_group['Is_Delayed_TARGET'].mean() * 100.0), 2)
                avg_delay = round(float(deliv_group['Delay_Minutes_TARGET'].mean()), 2)
            else:
                avg_dur = 0.0
                delay_rate = 0.0
                avg_delay = 0.0
                
            avg_aov = round(float(group['Total_Price'].mean()), 2)

            results.append(CityAnalyticsItem(
                city=city_name,
                order_count=order_count,
                delivered_orders=len(deliv_group),
                average_delivery_duration=avg_dur,
                delay_rate=delay_rate,
                average_delay=avg_delay,
                average_order_value=avg_aov
            ))

        return sorted(results, key=lambda x: x.order_count, reverse=True)

    def get_traffic_analytics(self, df: Optional[pd.DataFrame] = None) -> List[TrafficAnalyticsItem]:
        d = df if df is not None else self.df
        results = []
        traffic_order = ['Low', 'Medium', 'High']
        for traffic in traffic_order:
            group = d[d['Traffic_Level'] == traffic]
            if len(group) == 0:
                continue
            order_count = len(group)
            deliv_group = group[group['Order_Status'] == 'Delivered']

            if len(deliv_group) > 0:
                delay_rate = round(float(deliv_group['Is_Delayed_TARGET'].mean() * 100.0), 2)
                avg_dur = round(float(deliv_group['Delivery_Duration_Minutes'].mean()), 2)
            else:
                delay_rate = 0.0
                avg_dur = 0.0

            results.append(TrafficAnalyticsItem(
                traffic_level=traffic,
                order_count=order_count,
                delivered_orders=len(deliv_group),
                delay_rate=delay_rate,
                average_delivery_duration=avg_dur
            ))
        return results

    def get_status_analytics(self, df: Optional[pd.DataFrame] = None) -> List[StatusAnalyticsItem]:
        d = df if df is not None else self.df
        total = len(d)
        results = []
        statuses = ['Delivered', 'Cancelled', 'In Transit']
        for s in statuses:
            cnt = int((d['Order_Status'] == s).sum())
            pct = round((cnt / total * 100.0), 2) if total > 0 else 0.0
            results.append(StatusAnalyticsItem(
                status=s,
                count=cnt,
                percentage=pct
            ))
        return results

    def get_duration_distribution(self, df: Optional[pd.DataFrame] = None) -> List[DurationBinItem]:
        d = df if df is not None else self.df
        deliv_df = d[d['Order_Status'] == 'Delivered']
        total_deliv = len(deliv_df)

        bins = [(15, 25), (25, 35), (35, 45), (45, 55), (55, 65)]
        results = []

        for start, end in bins:
            if end == 65:
                # Include upper bound 60 min
                count = int(((deliv_df['Delivery_Duration_Minutes'] >= start) & (deliv_df['Delivery_Duration_Minutes'] <= 60)).sum())
                label = f"{start}-60 min"
            else:
                count = int(((deliv_df['Delivery_Duration_Minutes'] >= start) & (deliv_df['Delivery_Duration_Minutes'] < end)).sum())
                label = f"{start}-{end} min"

            pct = round((count / total_deliv * 100.0), 2) if total_deliv > 0 else 0.0
            results.append(DurationBinItem(
                bin_start=start,
                bin_end=min(end, 60),
                bin_label=label,
                count=count,
                percentage=pct
            ))

        return results

    def get_time_of_day_analytics(self, df: Optional[pd.DataFrame] = None) -> List[TimeOfDayAnalyticsItem]:
        d = df if df is not None else self.df
        tod_order = ['Early Morning', 'Morning', 'Afternoon', 'Evening', 'Night', 'Late Night']
        results = []

        for seg in tod_order:
            group = d[d['Time_Of_Day_Segment'] == seg]
            if len(group) == 0:
                continue
            order_count = len(group)
            deliv_group = group[group['Order_Status'] == 'Delivered']

            if len(deliv_group) > 0:
                delay_rate = round(float(deliv_group['Is_Delayed_TARGET'].mean() * 100.0), 2)
                avg_dur = round(float(deliv_group['Delivery_Duration_Minutes'].mean()), 2)
            else:
                delay_rate = 0.0
                avg_dur = 0.0

            results.append(TimeOfDayAnalyticsItem(
                segment=seg,
                order_count=order_count,
                delivered_orders=len(deliv_group),
                delay_rate=delay_rate,
                average_duration=avg_dur
            ))

        return results

    def get_day_of_week_analytics(self, df: Optional[pd.DataFrame] = None) -> List[DayOfWeekAnalyticsItem]:
        d = df if df is not None else self.df
        days_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        results = []

        for idx, day in enumerate(days_order):
            group = d[d['Order_DayName'] == day]
            if len(group) == 0:
                continue
            order_count = len(group)
            deliv_group = group[group['Order_Status'] == 'Delivered']

            if len(deliv_group) > 0:
                delay_rate = round(float(deliv_group['Is_Delayed_TARGET'].mean() * 100.0), 2)
                avg_dur = round(float(deliv_group['Delivery_Duration_Minutes'].mean()), 2)
            else:
                delay_rate = 0.0
                avg_dur = 0.0

            results.append(DayOfWeekAnalyticsItem(
                day_name=day,
                day_of_week_index=idx,
                order_count=order_count,
                delivered_orders=len(deliv_group),
                delay_rate=delay_rate,
                average_duration=avg_dur
            ))

        return results

    def get_vehicle_analytics(self, df: Optional[pd.DataFrame] = None) -> List[VehicleAnalyticsItem]:
        d = df if df is not None else self.df
        vehicles = ['Bicycle', 'Motorbike', 'Car']
        results = []

        for v in vehicles:
            group = d[d['Driver_Vehicle'] == v]
            if len(group) == 0:
                continue
            order_count = len(group)
            deliv_group = group[group['Order_Status'] == 'Delivered']

            if len(deliv_group) > 0:
                delay_rate = round(float(deliv_group['Is_Delayed_TARGET'].mean() * 100.0), 2)
                avg_dur = round(float(deliv_group['Delivery_Duration_Minutes'].mean()), 2)
                avg_speed = round(float(deliv_group['Delivery_Speed_kmh_ANALYTICAL'].mean()), 2)
            else:
                delay_rate = 0.0
                avg_dur = 0.0
                avg_speed = 0.0

            results.append(VehicleAnalyticsItem(
                vehicle=v,
                order_count=order_count,
                delivered_orders=len(deliv_group),
                delay_rate=delay_rate,
                average_duration=avg_dur,
                average_speed_kmh=avg_speed
            ))

        return results

    def get_order_quantity_analytics(self, df: Optional[pd.DataFrame] = None) -> List[OrderQuantityAnalyticsItem]:
        d = df if df is not None else self.df
        results = []

        for q in sorted(d['Quantity'].unique()):
            group = d[d['Quantity'] == q]
            order_count = len(group)
            deliv_group = group[group['Order_Status'] == 'Delivered']

            if len(deliv_group) > 0:
                delay_rate = round(float(deliv_group['Is_Delayed_TARGET'].mean() * 100.0), 2)
                avg_dur = round(float(deliv_group['Delivery_Duration_Minutes'].mean()), 2)
            else:
                delay_rate = 0.0
                avg_dur = 0.0

            avg_aov = round(float(group['Total_Price'].mean()), 2)

            results.append(OrderQuantityAnalyticsItem(
                quantity=int(q),
                order_count=order_count,
                delivered_orders=len(deliv_group),
                delay_rate=delay_rate,
                average_duration=avg_dur,
                average_order_value=avg_aov
            ))

        return results

    def get_order_value_analytics(self, df: Optional[pd.DataFrame] = None) -> List[OrderValueAnalyticsItem]:
        d = df if df is not None else self.df
        tier_order = ['Budget (<100)', 'Standard (100-300)', 'Premium (300-500)', 'Luxury (>500)']
        results = []

        for tier in tier_order:
            group = d[d['Order_Value_Tier'] == tier]
            if len(group) == 0:
                continue
            order_count = len(group)
            deliv_group = group[group['Order_Status'] == 'Delivered']

            if len(deliv_group) > 0:
                delay_rate = round(float(deliv_group['Is_Delayed_TARGET'].mean() * 100.0), 2)
                avg_dur = round(float(deliv_group['Delivery_Duration_Minutes'].mean()), 2)
            else:
                delay_rate = 0.0
                avg_dur = 0.0

            avg_aov = round(float(group['Total_Price'].mean()), 2)

            results.append(OrderValueAnalyticsItem(
                order_value_tier=tier,
                order_count=order_count,
                delivered_orders=len(deliv_group),
                delay_rate=delay_rate,
                average_order_value=avg_aov,
                average_duration=avg_dur
            ))

        return results

    def get_distance_analytics(self, df: Optional[pd.DataFrame] = None) -> DistanceAnalyticsResponse:
        d = df if df is not None else self.df
        deliv_df = d[d['Order_Status'] == 'Delivered']

        if len(deliv_df) > 1:
            corr_dur = round(float(deliv_df['Delivery_Distance_km'].corr(deliv_df['Delivery_Duration_Minutes'])), 4)
            corr_delay = round(float(deliv_df['Delivery_Distance_km'].corr(deliv_df['Is_Delayed_TARGET'])), 4)
        else:
            corr_dur = 0.0
            corr_delay = 0.0

        bins_order = ['Short (<1km)', 'Medium (1-3km)', 'Long (3-5km)', 'Very Long (>5km)']
        distance_bin_items = []

        for db in bins_order:
            group = d[d['Distance_Bin'] == db]
            if len(group) == 0:
                continue
            order_count = len(group)
            deliv_group = group[group['Order_Status'] == 'Delivered']

            if len(deliv_group) > 0:
                delay_rate = round(float(deliv_group['Is_Delayed_TARGET'].mean() * 100.0), 2)
                avg_dur = round(float(deliv_group['Delivery_Duration_Minutes'].mean()), 2)
            else:
                delay_rate = 0.0
                avg_dur = 0.0

            avg_dist = round(float(group['Delivery_Distance_km'].mean()), 2)

            distance_bin_items.append(DistanceBinItem(
                distance_bin=db,
                order_count=order_count,
                delivered_orders=len(deliv_group),
                delay_rate=delay_rate,
                average_duration=avg_dur,
                average_distance_km=avg_dist
            ))

        return DistanceAnalyticsResponse(
            correlation_distance_duration=corr_dur,
            correlation_distance_delay=corr_delay,
            distance_bins=distance_bin_items
        )

    def get_insights(self, df: Optional[pd.DataFrame] = None) -> List[InsightItem]:
        """Dynamically compute descriptive, non-causal analytical insights from dataset statistics."""
        d = df if df is not None else self.df
        insights: List[InsightItem] = []
        MIN_SAMPLE = 10  # Minimum sample size threshold to report pattern

        if len(d) == 0:
            return insights

        deliv_df = d[d['Order_Status'] == 'Delivered']

        # 1. Traffic Dynamics Insight
        if 'Traffic_Level' in d.columns and len(deliv_df) > 0:
            traffic_stats = []
            for t, grp in deliv_df.groupby('Traffic_Level'):
                if len(grp) >= MIN_SAMPLE:
                    rate = float(grp['Is_Delayed_TARGET'].mean() * 100.0)
                    traffic_stats.append((t, rate, len(grp)))
            
            if traffic_stats:
                traffic_stats.sort(key=lambda x: x[1], reverse=True)
                hi_traffic, hi_rate, count = traffic_stats[0]
                lo_traffic, lo_rate, _ = traffic_stats[-1]
                
                insights.append(InsightItem(
                    id="ins-traffic",
                    category="Traffic Dynamics",
                    title=f"{hi_traffic} Traffic Highest Observed Delay Rate",
                    description=f"Orders placed during {hi_traffic} traffic levels exhibited the highest observed SLA delay rate ({hi_rate:.2f}%), compared to {lo_traffic} traffic ({lo_rate:.2f}%).",
                    metric=f"{hi_rate:.2f}% Delay Rate",
                    direction="elevation" if hi_rate > 24.0 else "neutral",
                    sample_size=count,
                    supporting_metric=f"{hi_traffic} Traffic: {hi_rate:.2f}% ({count} delivered orders)"
                ))

        # 2. Geographic Performance Insight
        if 'City' in d.columns and len(deliv_df) > 0:
            city_stats = []
            for c, grp in deliv_df.groupby('City'):
                if len(grp) >= MIN_SAMPLE:
                    avg_dur = float(grp['Delivery_Duration_Minutes'].mean())
                    city_stats.append((c, avg_dur, len(grp)))
            
            if city_stats:
                city_stats.sort(key=lambda x: x[1], reverse=True)
                long_city, long_dur, count = city_stats[0]
                short_city, short_dur, _ = city_stats[-1]
                
                insights.append(InsightItem(
                    id="ins-city",
                    category="Geographic Performance",
                    title=f"{long_city} Longest Observed Mean Duration",
                    description=f"{long_city} recorded the longest observed average delivery duration ({long_dur:.2f} min) among cities, while {short_city} averaged {short_dur:.2f} min.",
                    metric=f"{long_dur:.2f} min Avg Duration",
                    direction="elevation",
                    sample_size=count,
                    supporting_metric=f"{long_city}: {long_dur:.2f} min vs {short_city}: {short_dur:.2f} min"
                ))

        # 3. Fleet Mobility Insight
        if 'Driver_Vehicle' in d.columns and len(deliv_df) > 0:
            vehicle_stats = []
            for v, grp in deliv_df.groupby('Driver_Vehicle'):
                if len(grp) >= MIN_SAMPLE:
                    rate = float(grp['Is_Delayed_TARGET'].mean() * 100.0)
                    vehicle_stats.append((v, rate, len(grp)))
            
            if vehicle_stats:
                vehicle_stats.sort(key=lambda x: x[1])
                best_v, best_rate, count = vehicle_stats[0]
                worst_v, worst_rate, _ = vehicle_stats[-1]
                
                insights.append(InsightItem(
                    id="ins-vehicle",
                    category="Fleet Mobility",
                    title=f"{best_v} Lowest Observed Delay Rate",
                    description=f"{best_v} orders showed the lowest observed SLA delay rate ({best_rate:.2f}%) among vehicle categories, compared to {worst_v} ({worst_rate:.2f}%).",
                    metric=f"{best_rate:.2f}% Delay Rate",
                    direction="positive",
                    sample_size=count,
                    supporting_metric=f"{best_v}: {best_rate:.2f}% vs {worst_v}: {worst_rate:.2f}%"
                ))

        # 4. Spatial & Distance Correlation Insight
        if 'Delivery_Distance_km' in deliv_df.columns and len(deliv_df) > 1:
            corr = float(deliv_df['Delivery_Distance_km'].corr(deliv_df['Delivery_Duration_Minutes']))
            short_grp = deliv_df[deliv_df['Delivery_Distance_km'] < 1.0]
            short_dur = float(short_grp['Delivery_Duration_Minutes'].mean()) if len(short_grp) > 0 else 0.0
            
            insights.append(InsightItem(
                id="ins-distance",
                category="Distance & Spatial",
                title="Fixed Operational Overhead Dominance",
                description=f"Delivery distance exhibits a Pearson correlation of r = {corr:.4f} with turnaround duration for trips, indicating kitchen prep and dispatch overhead dominate total turnaround time.",
                metric=f"r = {corr:.4f}",
                direction="neutral",
                sample_size=len(deliv_df),
                supporting_metric=f"Correlation r = {corr:.4f}; Short distance (<1km) duration: {short_dur:.2f} min"
            ))

        # 5. Basket Size Dynamics Insight
        if 'Quantity' in d.columns and len(deliv_df) > 0:
            qty_stats = []
            for q, grp in deliv_df.groupby('Quantity'):
                if len(grp) >= MIN_SAMPLE:
                    rate = float(grp['Is_Delayed_TARGET'].mean() * 100.0)
                    qty_stats.append((int(q), rate, len(grp)))
            
            if len(qty_stats) >= 2:
                qty_stats.sort(key=lambda x: x[1], reverse=True)
                hi_q, hi_rate, count = qty_stats[0]
                lo_q, lo_rate, _ = qty_stats[-1]
                
                insights.append(InsightItem(
                    id="ins-quantity",
                    category="Basket Dynamics",
                    title=f"{hi_q}-Item Orders Highest Observed Delay Rate",
                    description=f"Orders with {hi_q} items were associated with a higher observed SLA delay rate ({hi_rate:.2f}%) than {lo_q}-item orders ({lo_rate:.2f}%).",
                    metric=f"{hi_rate:.2f}% Delay Rate",
                    direction="negative",
                    sample_size=count,
                    supporting_metric=f"{hi_q} items: {hi_rate:.2f}% vs {lo_q} items: {lo_rate:.2f}%"
                ))

        # 6. Temporal Weekly Trends Insight
        if 'Order_DayName' in d.columns and len(deliv_df) > 0:
            day_stats = []
            for day_name, grp in deliv_df.groupby('Order_DayName'):
                if len(grp) >= MIN_SAMPLE:
                    rate = float(grp['Is_Delayed_TARGET'].mean() * 100.0)
                    day_stats.append((day_name, rate, len(grp)))
            
            if day_stats:
                day_stats.sort(key=lambda x: x[1], reverse=True)
                hi_day, hi_rate, count = day_stats[0]
                lo_day, lo_rate, _ = day_stats[-1]
                
                insights.append(InsightItem(
                    id="ins-day",
                    category="Temporal Trends",
                    title=f"{hi_day} Peak Observed Weekly Delay",
                    description=f"{hi_day} recorded the highest observed daily SLA delay rate ({hi_rate:.2f}%) across the operating week, compared to {lo_day} ({lo_rate:.2f}%).",
                    metric=f"{hi_rate:.2f}% Delay Rate",
                    direction="negative",
                    sample_size=count,
                    supporting_metric=f"{hi_day}: {hi_rate:.2f}% vs {lo_day}: {lo_rate:.2f}%"
                ))

        # 7. Rush Hour Surge Insight
        if 'Is_RushHour' in d.columns and len(deliv_df) > 0:
            rush_grp = deliv_df[deliv_df['Is_RushHour'] == 1]
            offpeak_grp = deliv_df[deliv_df['Is_RushHour'] == 0]
            
            if len(rush_grp) >= MIN_SAMPLE and len(offpeak_grp) >= MIN_SAMPLE:
                rush_rate = float(rush_grp['Is_Delayed_TARGET'].mean() * 100.0)
                offpeak_rate = float(offpeak_grp['Is_Delayed_TARGET'].mean() * 100.0)
                
                insights.append(InsightItem(
                    id="ins-rush",
                    category="Operational Signals",
                    title="Rush Hour vs Off-Peak Delay Pattern",
                    description=f"Orders during Rush Hour windows recorded an observed SLA delay rate of {rush_rate:.2f}%, compared to {offpeak_rate:.2f}% during off-peak hours.",
                    metric=f"{rush_rate:.2f}% Rush Delay Rate",
                    direction="neutral",
                    sample_size=len(rush_grp),
                    supporting_metric=f"Rush Hour: {rush_rate:.2f}% vs Off-Peak: {offpeak_rate:.2f}%"
                ))

        return insights

    def get_filters(self) -> FiltersResponse:
        d = self.df
        return FiltersResponse(
            cities=sorted(list(d['City'].unique())),
            traffic_levels=['Low', 'Medium', 'High'],
            vehicles=['Bicycle', 'Motorbike', 'Car'],
            payment_methods=sorted(list(d['Payment_Method'].unique())),
            distance_bins=['Short (<1km)', 'Medium (1-3km)', 'Long (3-5km)', 'Very Long (>5km)'],
            order_value_tiers=['Budget (<100)', 'Standard (100-300)', 'Premium (300-500)', 'Luxury (>500)'],
            time_segments=['Early Morning', 'Morning', 'Afternoon', 'Evening', 'Night', 'Late Night'],
            days_of_week=['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        )


# Global Service Singleton
analytics_service = AnalyticsService()
