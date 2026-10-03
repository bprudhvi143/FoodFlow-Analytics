"""
Explorer Service for FoodFlow Analytics Data Explorer.
Provides dataset summaries, column schema metadata, numerical/categorical stats, and paginated records search.
"""

import os
import math
import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional

from src.backend.config import settings
from src.backend.models.schemas import (
    ExplorerSummary, ColumnSchemaItem, NumericalStatItem, CategoricalStatItem,
    ExplorerSummaryStats, ExplorerRecordsResponse
)


class ExplorerService:
    def __init__(self, csv_path: str = settings.DATASET_PATH):
        self.csv_path = csv_path
        self._df: Optional[pd.DataFrame] = None

    def load_dataset(self) -> pd.DataFrame:
        if self._df is None:
            if not os.path.exists(self.csv_path):
                alt_path = "data/processed/food_delivery_10k.csv" if os.path.exists("data/processed/food_delivery_10k.csv") else "Datasets/food_delivery_10k.csv"
                if os.path.exists(alt_path):
                    self.csv_path = alt_path
                else:
                    raise FileNotFoundError(f"Dataset not found at {self.csv_path}")
            self._df = pd.read_csv(self.csv_path)
        return self._df

    def get_summary(self) -> ExplorerSummary:
        df = self.load_dataset()
        file_kb = round(os.path.getsize(self.csv_path) / 1024.0, 2) if os.path.exists(self.csv_path) else 0.0
        return ExplorerSummary(
            total_rows=len(df),
            total_columns=len(df.columns),
            unique_users=int(df['User_ID'].nunique()) if 'User_ID' in df.columns else 0,
            unique_restaurants=int(df['Restaurant_ID'].nunique()) if 'Restaurant_ID' in df.columns else 0,
            unique_drivers=int(df['Driver_ID'].nunique()) if 'Driver_ID' in df.columns else 0,
            unique_cities=int(df['City'].nunique()) if 'City' in df.columns else 0,
            file_size_kb=file_kb
        )

    def get_schema(self) -> List[ColumnSchemaItem]:
        df = self.load_dataset()
        schema_items = []
        total_rows = len(df)
        for col in df.columns:
            dt = str(df[col].dtype)
            missing = int(df[col].isna().sum())
            missing_pct = round((missing / total_rows) * 100.0, 2) if total_rows > 0 else 0.0
            unique_cnt = int(df[col].nunique(dropna=True))
            samples = [str(x) for x in df[col].dropna().unique()[:3]]
            schema_items.append(ColumnSchemaItem(
                column_name=col,
                data_type=dt,
                unique_count=unique_cnt,
                missing_count=missing,
                missing_percentage=missing_pct,
                sample_values=samples
            ))
        return schema_items

    def get_summary_stats(self) -> ExplorerSummaryStats:
        df = self.load_dataset()
        num_cols = df.select_dtypes(include=[np.number]).columns
        cat_cols = df.select_dtypes(include=['object', 'category']).columns

        num_stats: List[NumericalStatItem] = []
        for col in num_cols:
            s = df[col].dropna()
            if len(s) == 0:
                continue
            num_stats.append(NumericalStatItem(
                column_name=col,
                count=int(len(s)),
                mean=round(float(s.mean()), 2),
                std=round(float(s.std()), 2) if len(s) > 1 else 0.0,
                min=round(float(s.min()), 2),
                p25=round(float(s.quantile(0.25)), 2),
                median=round(float(s.median()), 2),
                p75=round(float(s.quantile(0.75)), 2),
                max=round(float(s.max()), 2)
            ))

        cat_stats: List[CategoricalStatItem] = []
        for col in cat_cols:
            s = df[col].dropna()
            if len(s) == 0:
                continue
            vc = s.value_counts()
            top_val = str(vc.index[0]) if len(vc) > 0 else "N/A"
            top_cnt = int(vc.iloc[0]) if len(vc) > 0 else 0
            vc_dict = {str(k): int(v) for k, v in vc.head(10).items()}
            cat_stats.append(CategoricalStatItem(
                column_name=col,
                unique_count=int(s.nunique()),
                top_value=top_val,
                top_count=top_cnt,
                value_counts=vc_dict
            ))

        return ExplorerSummaryStats(
            numerical_stats=num_stats,
            categorical_stats=cat_stats
        )

    def get_records(
        self,
        page: int = 1,
        page_size: int = 20,
        search: Optional[str] = None,
        city: Optional[str] = None,
        traffic_level: Optional[str] = None,
        vehicle: Optional[str] = None,
        order_status: Optional[str] = None,
        sort_by: Optional[str] = None,
        sort_order: Optional[str] = 'asc'
    ) -> ExplorerRecordsResponse:
        df = self.load_dataset()
        filtered = df

        if city:
            filtered = filtered[filtered['City'].str.lower() == city.lower()]
        if traffic_level:
            filtered = filtered[filtered['Traffic_Level'].str.lower() == traffic_level.lower()]
        if vehicle:
            filtered = filtered[filtered['Driver_Vehicle'].str.lower() == vehicle.lower()]
        if order_status:
            filtered = filtered[filtered['Order_Status'].str.lower() == order_status.lower()]

        if search:
            s_lower = search.strip().lower()
            mask = pd.Series(False, index=filtered.index)
            search_cols = ['City', 'Order_Status', 'Driver_Vehicle', 'Payment_Method', 'Item_Name', 'Traffic_Level', 'Time_Of_Day_Segment', 'Order_DayName']
            for c in search_cols:
                if c in filtered.columns:
                    mask = mask | (filtered[c].astype(str).str.lower().str.contains(s_lower, na=False))
            for id_col in ['Order_ID', 'User_ID', 'Restaurant_ID', 'Driver_ID']:
                if id_col in filtered.columns:
                    mask = mask | (filtered[id_col].astype(str).str.lower().str.contains(s_lower, na=False))
            filtered = filtered[mask]

        if sort_by and sort_by in filtered.columns:
            ascending = (sort_order.lower() != 'desc')
            filtered = filtered.sort_values(by=sort_by, ascending=ascending)

        total_records = len(filtered)
        page_size = max(1, min(100, page_size))
        total_pages = math.ceil(total_records / page_size) if total_records > 0 else 1
        page = max(1, min(page, total_pages)) if total_pages > 0 else 1

        start_idx = (page - 1) * page_size
        end_idx = start_idx + page_size
        sliced = filtered.iloc[start_idx:end_idx]

        records_dict = sliced.replace({np.nan: None}).to_dict(orient='records')

        return ExplorerRecordsResponse(
            page=page,
            page_size=page_size,
            total_records=total_records,
            total_pages=total_pages,
            records=records_dict
        )


explorer_service = ExplorerService()
