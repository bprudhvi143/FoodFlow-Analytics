/**
 * FoodFlow Analytics API Service Layer
 * Typescript interfaces and async fetch functions for FastAPI backend.
 */

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api';

// ============================================================================
// TypeScript Response Interfaces
// ============================================================================

export interface HealthResponse {
  status: string;
  dataset_loaded: boolean;
  total_records: number;
  dataset_path: string;
}

export interface OverviewAnalytics {
  total_orders: number;
  delivered_orders: number;
  cancelled_orders: number;
  in_transit_orders: number;
  delivery_completion_rate: number;
  cancellation_rate: number;
  in_transit_rate: number;
  delay_rate: number;
  overall_delay_rate: number;
  average_delivery_duration: number;
  median_delivery_duration: number;
  average_delay_among_delayed_orders: number;
  average_order_value: number;
  average_delivery_distance: number;
  average_quantity: number;
}

export interface CityAnalyticsItem {
  city: string;
  order_count: number;
  delivered_orders: number;
  average_delivery_duration: number;
  delay_rate: number;
  average_delay: number;
  average_order_value: number;
}

export interface TrafficAnalyticsItem {
  traffic_level: string;
  order_count: number;
  delivered_orders: number;
  delay_rate: number;
  average_delivery_duration: number;
}

export interface StatusAnalyticsItem {
  status: string;
  count: number;
  percentage: number;
}

export interface DurationBinItem {
  bin_start: number;
  bin_end: number;
  bin_label: string;
  count: number;
  percentage: number;
}

export interface TimeOfDayAnalyticsItem {
  segment: string;
  order_count: number;
  delivered_orders: number;
  delay_rate: number;
  average_duration: number;
}

export interface DayOfWeekAnalyticsItem {
  day_name: string;
  day_of_week_index: number;
  order_count: number;
  delivered_orders: number;
  delay_rate: number;
  average_duration: number;
}

export interface VehicleAnalyticsItem {
  vehicle: string;
  order_count: number;
  delivered_orders: number;
  delay_rate: number;
  average_duration: number;
  average_speed_kmh: number;
}

export interface OrderQuantityAnalyticsItem {
  quantity: number;
  order_count: number;
  delivered_orders: number;
  delay_rate: number;
  average_duration: number;
  average_order_value: number;
}

export interface OrderValueAnalyticsItem {
  order_value_tier: string;
  order_count: number;
  delivered_orders: number;
  delay_rate: number;
  average_order_value: number;
  average_duration: number;
}

export interface DistanceBinItem {
  distance_bin: string;
  order_count: number;
  delivered_orders: number;
  delay_rate: number;
  average_duration: number;
  average_distance_km: number;
}

export interface DistanceAnalyticsResponse {
  correlation_distance_duration: number;
  correlation_distance_delay: number;
  distance_bins: DistanceBinItem[];
}

export interface InsightItem {
  id: string;
  category: string;
  title: string;
  description: string;
  metric: string;
  direction: string;
  sample_size: number;
  supporting_metric?: string;
}

export interface FiltersResponse {
  cities: string[];
  traffic_levels: string[];
  vehicles: string[];
  payment_methods: string[];
  distance_bins: string[];
  order_value_tiers: string[];
  time_segments: string[];
  days_of_week: string[];
}

export interface AnalyticsQueryParams {
  city?: string;
  traffic_level?: string;
  time_of_day?: string;
  day_of_week?: string;
  vehicle?: string;
  payment_method?: string;
  distance_bin?: string;
  order_value_tier?: string;
  is_rush_hour?: number;
}

// ============================================================================
// Data Explorer Interfaces
// ============================================================================

export interface ExplorerSummary {
  total_rows: number;
  total_columns: number;
  unique_users: number;
  unique_restaurants: number;
  unique_drivers: number;
  unique_cities: number;
  file_size_kb: number;
}

export interface ColumnSchemaItem {
  column_name: string;
  data_type: string;
  unique_count: number;
  missing_count: number;
  missing_percentage: number;
  sample_values: string[];
}

export interface NumericalStatItem {
  column_name: string;
  count: number;
  mean: number;
  std: number;
  min: number;
  p25: number;
  median: number;
  p75: number;
  max: number;
}

export interface CategoricalStatItem {
  column_name: string;
  unique_count: number;
  top_value: string;
  top_count: number;
  value_counts: Record<string, number>;
}

export interface ExplorerSummaryStats {
  numerical_stats: NumericalStatItem[];
  categorical_stats: CategoricalStatItem[];
}

export interface ExplorerRecordsQueryParams {
  page?: number;
  page_size?: number;
  search?: string;
  city?: string;
  traffic_level?: string;
  vehicle?: string;
  order_status?: string;
  sort_by?: string;
  sort_order?: 'asc' | 'desc';
}

export interface ExplorerRecordsResponse {
  page: number;
  page_size: number;
  total_records: number;
  total_pages: number;
  records: Record<string, any>[];
}

// ============================================================================
// Helper Utilities
// ============================================================================

function buildQueryString(params?: Record<string, any>): string {
  if (!params) return '';
  const query = new URLSearchParams();
  Object.entries(params).forEach(([key, value]) => {
    if (value !== undefined && value !== null && value !== '') {
      query.append(key, String(value));
    }
  });
  const str = query.toString();
  return str ? `?${str}` : '';
}

async function fetchJson<T>(endpoint: string, params?: Record<string, any>, signal?: AbortSignal): Promise<T> {
  const url = `${API_BASE_URL}${endpoint}${buildQueryString(params)}`;
  const response = await fetch(url, { signal });
  if (!response.ok) {
    const errorText = await response.text();
    throw new Error(`API error (${response.status}): ${errorText || response.statusText}`);
  }
  return response.json();
}

// ============================================================================
// API Service Functions
// ============================================================================

export const apiService = {
  getHealth: (signal?: AbortSignal) => fetchJson<HealthResponse>('/health', undefined, signal),
  getOverview: (params?: AnalyticsQueryParams, signal?: AbortSignal) => fetchJson<OverviewAnalytics>('/analytics/overview', params, signal),
  getCityAnalytics: (params?: AnalyticsQueryParams, signal?: AbortSignal) => fetchJson<CityAnalyticsItem[]>('/analytics/city', params, signal),
  getTrafficAnalytics: (params?: AnalyticsQueryParams, signal?: AbortSignal) => fetchJson<TrafficAnalyticsItem[]>('/analytics/traffic', params, signal),
  getStatusAnalytics: (params?: AnalyticsQueryParams, signal?: AbortSignal) => fetchJson<StatusAnalyticsItem[]>('/analytics/status', params, signal),
  getDurationDistribution: (params?: AnalyticsQueryParams, signal?: AbortSignal) => fetchJson<DurationBinItem[]>('/analytics/duration-distribution', params, signal),
  getTimeOfDayAnalytics: (params?: AnalyticsQueryParams, signal?: AbortSignal) => fetchJson<TimeOfDayAnalyticsItem[]>('/analytics/time-of-day', params, signal),
  getDayOfWeekAnalytics: (params?: AnalyticsQueryParams, signal?: AbortSignal) => fetchJson<DayOfWeekAnalyticsItem[]>('/analytics/day-of-week', params, signal),
  getVehicleAnalytics: (params?: AnalyticsQueryParams, signal?: AbortSignal) => fetchJson<VehicleAnalyticsItem[]>('/analytics/vehicle', params, signal),
  getOrderQuantityAnalytics: (params?: AnalyticsQueryParams, signal?: AbortSignal) => fetchJson<OrderQuantityAnalyticsItem[]>('/analytics/order-quantity', params, signal),
  getOrderValueAnalytics: (params?: AnalyticsQueryParams, signal?: AbortSignal) => fetchJson<OrderValueAnalyticsItem[]>('/analytics/order-value', params, signal),
  getDistanceAnalytics: (params?: AnalyticsQueryParams, signal?: AbortSignal) => fetchJson<DistanceAnalyticsResponse>('/analytics/distance', params, signal),
  getInsights: (params?: AnalyticsQueryParams, signal?: AbortSignal) => fetchJson<InsightItem[]>('/analytics/insights', params, signal),
  getFilters: (signal?: AbortSignal) => fetchJson<FiltersResponse>('/analytics/filters', undefined, signal),

  // Data Explorer Endpoints
  getExplorerSummary: (signal?: AbortSignal) => fetchJson<ExplorerSummary>('/explorer/summary', undefined, signal),
  getExplorerSchema: (signal?: AbortSignal) => fetchJson<ColumnSchemaItem[]>('/explorer/schema', undefined, signal),
  getExplorerSummaryStats: (signal?: AbortSignal) => fetchJson<ExplorerSummaryStats>('/explorer/summary-stats', undefined, signal),
  getExplorerRecords: (params?: ExplorerRecordsQueryParams, signal?: AbortSignal) => fetchJson<ExplorerRecordsResponse>('/explorer/records', params, signal),
};
