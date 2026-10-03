import React, { useState, useEffect, useCallback } from 'react';
import {
  Activity,
  AlertCircle,
  BarChart3,
  Bike,
  Building2,
  Calendar,
  CheckCircle2,
  ChevronLeft,
  ChevronRight,
  Clock,
  Compass,
  Database,
  DollarSign,
  FileCode,
  FileText,
  Filter,
  Layers,
  MapPin,
  Printer,
  RefreshCw,
  Search,
  Server,
  ShieldAlert,
  ShoppingBag,
  SlidersHorizontal,
  Store,
  Table,
  TrendingUp,
  Truck,
  Users,
  XCircle,
  Zap
} from 'lucide-react';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
  LineChart,
  Line,
  Legend,
  ReferenceLine,
  AreaChart,
  Area
} from 'recharts';
import {
  apiService,
  OverviewAnalytics,
  CityAnalyticsItem,
  TrafficAnalyticsItem,
  StatusAnalyticsItem,
  DurationBinItem,
  TimeOfDayAnalyticsItem,
  DayOfWeekAnalyticsItem,
  VehicleAnalyticsItem,
  OrderQuantityAnalyticsItem,
  OrderValueAnalyticsItem,
  DistanceAnalyticsResponse,
  InsightItem,
  FiltersResponse,
  AnalyticsQueryParams,
  ExplorerSummary,
  ColumnSchemaItem,
  ExplorerSummaryStats,
  ExplorerRecordsResponse,
  ExplorerRecordsQueryParams
} from './services/api';

// Brand Chart Color Palette
const COLORS = {
  primary: '#0ea5e9',
  secondary: '#8b5cf6',
  success: '#10b981',
  warning: '#f59e0b',
  danger: '#ef4444',
  slateDark: '#1e293b',
  slateLight: '#94a3b8',
  pieColors: ['#10b981', '#ef4444', '#f59e0b'],
  trafficColors: ['#10b981', '#f59e0b', '#ef4444']
};

export default function App() {
  // Navigation State
  const [activeTab, setActiveTab] = useState<'overview' | 'city' | 'traffic' | 'fleet' | 'insights' | 'explorer' | 'reports'>('overview');

  // Backend Health & Filter Choices
  const [backendOnline, setBackendOnline] = useState<boolean | null>(null);
  const [filterChoices, setFilterChoices] = useState<FiltersResponse | null>(null);

  // Selected Query Filter State
  const [queryParams, setQueryParams] = useState<AnalyticsQueryParams>({
    city: '',
    traffic_level: '',
    time_of_day: '',
    day_of_week: '',
    vehicle: '',
    payment_method: '',
    distance_bin: '',
    order_value_tier: ''
  });

  // Analytics Data States
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  const [overview, setOverview] = useState<OverviewAnalytics | null>(null);
  const [cityData, setCityData] = useState<CityAnalyticsItem[]>([]);
  const [trafficData, setTrafficData] = useState<TrafficAnalyticsItem[]>([]);
  const [statusData, setStatusData] = useState<StatusAnalyticsItem[]>([]);
  const [durationBins, setDurationBins] = useState<DurationBinItem[]>([]);
  const [timeOfDayData, setTimeOfDayData] = useState<TimeOfDayAnalyticsItem[]>([]);
  const [dayOfWeekData, setDayOfWeekData] = useState<DayOfWeekAnalyticsItem[]>([]);
  const [vehicleData, setVehicleData] = useState<VehicleAnalyticsItem[]>([]);
  const [quantityData, setQuantityData] = useState<OrderQuantityAnalyticsItem[]>([]);
  const [orderValueData, setOrderValueData] = useState<OrderValueAnalyticsItem[]>([]);
  const [distanceData, setDistanceData] = useState<DistanceAnalyticsResponse | null>(null);
  const [insights, setInsights] = useState<InsightItem[]>([]);

  // Data Explorer State
  const [explorerSubTab, setExplorerSubTab] = useState<'records' | 'schema' | 'stats'>('records');
  const [explorerSummary, setExplorerSummary] = useState<ExplorerSummary | null>(null);
  const [columnSchema, setColumnSchema] = useState<ColumnSchemaItem[]>([]);
  const [explorerStats, setExplorerStats] = useState<ExplorerSummaryStats | null>(null);
  const [explorerRecords, setExplorerRecords] = useState<ExplorerRecordsResponse | null>(null);

  const [explorerLoading, setExplorerLoading] = useState<boolean>(false);
  const [explorerPage, setExplorerPage] = useState<number>(1);
  const [explorerPageSize, setExplorerPageSize] = useState<number>(20);
  const [explorerSearch, setExplorerSearch] = useState<string>('');
  const [explorerCityFilter, setExplorerCityFilter] = useState<string>('');
  const [explorerVehicleFilter, setExplorerVehicleFilter] = useState<string>('');
  const [explorerStatusFilter, setExplorerStatusFilter] = useState<string>('');
  const [schemaSearch, setSchemaSearch] = useState<string>('');

  // Ref to hold the current AbortController to prevent race conditions
  const abortControllerRef = React.useRef<AbortController | null>(null);

  // Fetch API Analytics Data
  const loadAnalyticsData = useCallback(async (paramsToUse?: AnalyticsQueryParams) => {
    // Cancel any pending request
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
    }
    const controller = new AbortController();
    abortControllerRef.current = controller;

    setLoading(true);
    setError(null);
    const activeParams = paramsToUse ?? queryParams;

    try {
      // 1. Health Check
      const health = await apiService.getHealth(controller.signal);
      setBackendOnline(health.dataset_loaded);

      // 2. Fetch Filter Choices if not loaded
      if (!filterChoices) {
        const filters = await apiService.getFilters(controller.signal);
        setFilterChoices(filters);
      }

      // 3. Parallel API Fetching with Selected Query Filters
      const [
        ovRes,
        cityRes,
        trafficRes,
        statusRes,
        durationRes,
        timeOfDayRes,
        dayOfWeekRes,
        vehicleRes,
        qtyRes,
        valueRes,
        distanceRes,
        insightsRes
      ] = await Promise.all([
        apiService.getOverview(activeParams, controller.signal),
        apiService.getCityAnalytics(activeParams, controller.signal),
        apiService.getTrafficAnalytics(activeParams, controller.signal),
        apiService.getStatusAnalytics(activeParams, controller.signal),
        apiService.getDurationDistribution(activeParams, controller.signal),
        apiService.getTimeOfDayAnalytics(activeParams, controller.signal),
        apiService.getDayOfWeekAnalytics(activeParams, controller.signal),
        apiService.getVehicleAnalytics(activeParams, controller.signal),
        apiService.getOrderQuantityAnalytics(activeParams, controller.signal),
        apiService.getOrderValueAnalytics(activeParams, controller.signal),
        apiService.getDistanceAnalytics(activeParams, controller.signal),
        apiService.getInsights(activeParams, controller.signal)
      ]);

      setOverview(ovRes);
      setCityData(cityRes);
      setTrafficData(trafficRes);
      setStatusData(statusRes);
      setDurationBins(durationRes);
      setTimeOfDayData(timeOfDayRes);
      setDayOfWeekData(dayOfWeekRes);
      setVehicleData(vehicleRes);
      setQuantityData(qtyRes);
      setOrderValueData(valueRes);
      setDistanceData(distanceRes);
      setInsights(insightsRes);
    } catch (err: any) {
      if (err.name === 'AbortError') {
        // Silently ignore aborted requests to prevent race condition flickers
        return;
      }
      console.error("Error loading analytics data:", err);
      setBackendOnline(false);
      setError(err.message || "Failed to connect to FastAPI backend at http://localhost:8000.");
    } finally {
      if (abortControllerRef.current === controller) {
        setLoading(false);
      }
    }
  }, [queryParams, filterChoices]);

  useEffect(() => {
    loadAnalyticsData();
  }, [loadAnalyticsData]);

  // Fetch Explorer Metadata (Summary, Schema, Stats)
  const loadExplorerMetadata = useCallback(async () => {
    try {
      const [sumRes, schRes, statRes] = await Promise.all([
        apiService.getExplorerSummary(),
        apiService.getExplorerSchema(),
        apiService.getExplorerSummaryStats()
      ]);
      setExplorerSummary(sumRes);
      setColumnSchema(schRes);
      setExplorerStats(statRes);
    } catch (err) {
      console.error("Error loading explorer metadata:", err);
    }
  }, []);

  // Fetch Paginated Explorer Records
  const loadExplorerRecords = useCallback(async () => {
    setExplorerLoading(true);
    try {
      const res = await apiService.getExplorerRecords({
        page: explorerPage,
        page_size: explorerPageSize,
        search: explorerSearch,
        city: explorerCityFilter,
        vehicle: explorerVehicleFilter,
        order_status: explorerStatusFilter
      });
      setExplorerRecords(res);
    } catch (err) {
      console.error("Error loading explorer records:", err);
    } finally {
      setExplorerLoading(false);
    }
  }, [explorerPage, explorerPageSize, explorerSearch, explorerCityFilter, explorerVehicleFilter, explorerStatusFilter]);

  useEffect(() => {
    if (activeTab === 'explorer') {
      loadExplorerMetadata();
      loadExplorerRecords();
    }
  }, [activeTab, loadExplorerMetadata, loadExplorerRecords]);

  // Handle Query Param Filter Change
  const handleFilterChange = (field: keyof AnalyticsQueryParams, value: string) => {
    const updated = {
      ...queryParams,
      [field]: value
    };
    setQueryParams(updated);
  };

  const handleApplyFilters = () => {
    loadAnalyticsData(queryParams);
  };

  const handleResetFilters = () => {
    const resetState: AnalyticsQueryParams = {
      city: '',
      traffic_level: '',
      time_of_day: '',
      day_of_week: '',
      vehicle: '',
      payment_method: '',
      distance_bin: '',
      order_value_tier: ''
    };
    setQueryParams(resetState);
    loadAnalyticsData(resetState);
  };

  // Active filter counter
  const activeFilterCount = Object.values(queryParams).filter(Boolean).length;

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col">
      {/* ==================================================================== */}
      {/* 1. Header Navigation Bar */}
      {/* ==================================================================== */}
      <header className="border-b border-slate-800 bg-slate-900/80 backdrop-blur-md sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-3.5 flex flex-col sm:flex-row items-center justify-between gap-4">
          <div className="flex items-center gap-3">
            <div className="p-2.5 bg-sky-500/10 border border-sky-500/20 rounded-xl text-sky-400">
              <Zap className="w-6 h-6" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h1 className="text-xl font-bold tracking-tight text-white font-heading">FoodFlow Analytics</h1>
                <span className="text-xs font-semibold px-2 py-0.5 rounded-full bg-slate-800 text-sky-400 border border-slate-700">
                  v1.0 FastAPI
                </span>
              </div>
              <p className="text-xs text-slate-400">
                Live Performance & Diagnostic Analytics (<span className="font-mono text-slate-300">food_delivery_10k.csv</span>)
              </p>
            </div>
          </div>

          <div className="flex items-center gap-3">
            {/* Backend Status Indicator */}
            <div className={`flex items-center gap-2 text-xs px-3 py-1.5 rounded-full border ${
              backendOnline
                ? 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20'
                : 'bg-rose-500/10 text-rose-400 border-rose-500/20'
            }`}>
              <span className={`w-2 h-2 rounded-full ${backendOnline ? 'bg-emerald-400 animate-pulse' : 'bg-rose-400'}`}></span>
              <Server className="w-3.5 h-3.5" />
              <span>{backendOnline ? 'Backend Connected' : 'Backend Offline'}</span>
            </div>

            {/* Refresh Button */}
            <button
              onClick={() => loadAnalyticsData()}
              disabled={loading}
              className="flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 transition disabled:opacity-50"
              title="Refresh Data from API"
            >
              <RefreshCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin' : ''}`} />
              <span>Refresh</span>
            </button>
          </div>
        </div>
      </header>

      {/* ==================================================================== */}
      {/* 2. Interactive Multi-Filter Control Bar */}
      {/* ==================================================================== */}
      <section className="bg-slate-900 border-b border-slate-800/80 px-4 py-3">
        <div className="max-w-7xl mx-auto flex flex-col lg:flex-row lg:items-center justify-between gap-3 text-xs">
          <div className="flex items-center gap-2 text-slate-400 shrink-0">
            <Filter className="w-4 h-4 text-sky-400" />
            <span className="font-medium text-slate-300">Filter Dataset:</span>
            {activeFilterCount > 0 && (
              <span className="px-2 py-0.5 rounded-full text-[10px] font-bold bg-sky-500/20 text-sky-300 border border-sky-500/30">
                {activeFilterCount} Active
              </span>
            )}
          </div>

          <div className="flex flex-wrap items-center gap-2 flex-1">
            {/* 1. City Dropdown */}
            <select
              value={queryParams.city || ''}
              onChange={e => handleFilterChange('city', e.target.value)}
              className="bg-slate-950 text-slate-200 border border-slate-800 rounded-lg px-2.5 py-1.5 focus:outline-none focus:border-sky-500"
            >
              <option value="">All Cities (7 Markets)</option>
              {filterChoices?.cities.map(c => (
                <option key={c} value={c}>{c}</option>
              ))}
            </select>

            {/* 2. Traffic Dropdown */}
            <select
              value={queryParams.traffic_level || ''}
              onChange={e => handleFilterChange('traffic_level', e.target.value)}
              className="bg-slate-950 text-slate-200 border border-slate-800 rounded-lg px-2.5 py-1.5 focus:outline-none focus:border-sky-500"
            >
              <option value="">All Traffic Levels</option>
              {filterChoices?.traffic_levels.map(t => (
                <option key={t} value={t}>{t} Traffic</option>
              ))}
            </select>

            {/* 3. Time of Day Dropdown */}
            <select
              value={queryParams.time_of_day || ''}
              onChange={e => handleFilterChange('time_of_day', e.target.value)}
              className="bg-slate-950 text-slate-200 border border-slate-800 rounded-lg px-2.5 py-1.5 focus:outline-none focus:border-sky-500"
            >
              <option value="">All Time Segments</option>
              {filterChoices?.time_segments.map(ts => (
                <option key={ts} value={ts}>{ts}</option>
              ))}
            </select>

            {/* 4. Day of Week Dropdown */}
            <select
              value={queryParams.day_of_week || ''}
              onChange={e => handleFilterChange('day_of_week', e.target.value)}
              className="bg-slate-950 text-slate-200 border border-slate-800 rounded-lg px-2.5 py-1.5 focus:outline-none focus:border-sky-500"
            >
              <option value="">All Days of Week</option>
              {filterChoices?.days_of_week.map(dw => (
                <option key={dw} value={dw}>{dw}</option>
              ))}
            </select>

            {/* 5. Vehicle Dropdown */}
            <select
              value={queryParams.vehicle || ''}
              onChange={e => handleFilterChange('vehicle', e.target.value)}
              className="bg-slate-950 text-slate-200 border border-slate-800 rounded-lg px-2.5 py-1.5 focus:outline-none focus:border-sky-500"
            >
              <option value="">All Vehicle Types</option>
              {filterChoices?.vehicles.map(v => (
                <option key={v} value={v}>{v}</option>
              ))}
            </select>

            {/* 6. Distance Bin Dropdown */}
            <select
              value={queryParams.distance_bin || ''}
              onChange={e => handleFilterChange('distance_bin', e.target.value)}
              className="bg-slate-950 text-slate-200 border border-slate-800 rounded-lg px-2.5 py-1.5 focus:outline-none focus:border-sky-500"
            >
              <option value="">All Distance Categories</option>
              {filterChoices?.distance_bins.map(d => (
                <option key={d} value={d}>{d}</option>
              ))}
            </select>

            {/* 7. Order Value Tier Dropdown */}
            <select
              value={queryParams.order_value_tier || ''}
              onChange={e => handleFilterChange('order_value_tier', e.target.value)}
              className="bg-slate-950 text-slate-200 border border-slate-800 rounded-lg px-2.5 py-1.5 focus:outline-none focus:border-sky-500"
            >
              <option value="">All Price Tiers</option>
              {filterChoices?.order_value_tiers.map(pt => (
                <option key={pt} value={pt}>{pt}</option>
              ))}
            </select>

            {/* Apply & Reset Buttons */}
            <div className="flex items-center gap-2">
              <button
                onClick={handleApplyFilters}
                className="px-3 py-1.5 font-semibold bg-sky-500 hover:bg-sky-400 text-white rounded-lg transition"
              >
                Apply Filters
              </button>
              {activeFilterCount > 0 && (
                <button
                  onClick={handleResetFilters}
                  className="text-slate-400 hover:text-slate-200 font-medium underline px-2 py-1.5"
                >
                  Reset Filters
                </button>
              )}
            </div>
          </div>

          <div className="text-slate-400 shrink-0">
            Filtered Sample: <span className="font-semibold text-white">{overview ? overview.total_orders.toLocaleString() : '...'}</span> orders
          </div>
        </div>
      </section>

      {/* ==================================================================== */}
      {/* 3. Primary Dashboard Navigation Tabs */}
      {/* ==================================================================== */}
      <div className="border-b border-slate-800 bg-slate-900/40">
        <div className="max-w-7xl mx-auto px-4 flex gap-6">
          <button
            onClick={() => setActiveTab('overview')}
            className={`py-3 px-1 border-b-2 text-xs font-semibold flex items-center gap-2 transition ${
              activeTab === 'overview'
                ? 'border-sky-400 text-sky-400'
                : 'border-transparent text-slate-400 hover:text-slate-200'
            }`}
          >
            <BarChart3 className="w-4 h-4" /> Overview & KPIs
          </button>
          <button
            onClick={() => setActiveTab('city')}
            className={`py-3 px-1 border-b-2 text-xs font-semibold flex items-center gap-2 transition ${
              activeTab === 'city'
                ? 'border-sky-400 text-sky-400'
                : 'border-transparent text-slate-400 hover:text-slate-200'
            }`}
          >
            <Building2 className="w-4 h-4" /> Geographic Performance
          </button>
          <button
            onClick={() => setActiveTab('traffic')}
            className={`py-3 px-1 border-b-2 text-xs font-semibold flex items-center gap-2 transition ${
              activeTab === 'traffic'
                ? 'border-sky-400 text-sky-400'
                : 'border-transparent text-slate-400 hover:text-slate-200'
            }`}
          >
            <Activity className="w-4 h-4" /> Traffic & Temporal
          </button>
          <button
            onClick={() => setActiveTab('fleet')}
            className={`py-3 px-1 border-b-2 text-xs font-semibold flex items-center gap-2 transition ${
              activeTab === 'fleet'
                ? 'border-sky-400 text-sky-400'
                : 'border-transparent text-slate-400 hover:text-slate-200'
            }`}
          >
            <Truck className="w-4 h-4" /> Fleet & Basket Dynamics
          </button>
          <button
            onClick={() => setActiveTab('insights')}
            className={`py-3 px-1 border-b-2 text-xs font-semibold flex items-center gap-2 transition ${
              activeTab === 'insights'
                ? 'border-sky-400 text-sky-400'
                : 'border-transparent text-slate-400 hover:text-slate-200'
            }`}
          >
            <Compass className="w-4 h-4" /> Diagnostic Insights
          </button>
          <button
            onClick={() => setActiveTab('explorer')}
            className={`py-3 px-1 border-b-2 text-xs font-semibold flex items-center gap-2 transition ${
              activeTab === 'explorer'
                ? 'border-sky-400 text-sky-400'
                : 'border-transparent text-slate-400 hover:text-slate-200'
            }`}
          >
            <Database className="w-4 h-4" /> Data Explorer
          </button>
          <button
            onClick={() => setActiveTab('reports')}
            className={`py-3 px-1 border-b-2 text-xs font-semibold flex items-center gap-2 transition ${
              activeTab === 'reports'
                ? 'border-sky-400 text-sky-400'
                : 'border-transparent text-slate-400 hover:text-slate-200'
            }`}
          >
            <FileText className="w-4 h-4" /> Analytical Reports
          </button>
        </div>
      </div>

      {/* ==================================================================== */}
      {/* 4. Main Body Content Area */}
      {/* ==================================================================== */}
      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-6 space-y-6">
        {/* Error Alert Display */}
        {error && (
          <div className="p-4 rounded-xl bg-rose-500/10 border border-rose-500/30 text-rose-300 flex items-start gap-3">
            <AlertCircle className="w-5 h-5 text-rose-400 shrink-0 mt-0.5" />
            <div className="flex-1 text-sm">
              <h4 className="font-semibold text-rose-200">Analytics API Connection Error</h4>
              <p className="mt-0.5 text-xs text-rose-300/80">{error}</p>
              <button
                onClick={() => loadAnalyticsData()}
                className="mt-2 text-xs font-medium px-3 py-1 bg-rose-500/20 hover:bg-rose-500/30 border border-rose-500/40 rounded-md transition text-rose-200"
              >
                Retry Request
              </button>
            </div>
          </div>
        )}

        {/* Loading Spinner / Skeleton */}
        {loading && !error && (
          <div className="py-20 text-center space-y-3">
            <RefreshCw className="w-8 h-8 text-sky-400 animate-spin mx-auto" />
            <p className="text-sm text-slate-400">Computing analytics from <span className="font-mono text-slate-200">food_delivery_10k.csv</span>...</p>
          </div>
        )}

        {/* Empty Filter State */}
        {!loading && overview && overview.total_orders === 0 && (
          <div className="py-16 text-center space-y-3 glass-card p-8">
            <ShieldAlert className="w-10 h-10 text-amber-400 mx-auto" />
            <h3 className="text-lg font-semibold text-white">No Orders Match the Selected Filter</h3>
            <p className="text-xs text-slate-400 max-w-md mx-auto">
              No delivery records in the dataset match the selected combination of city, traffic, vehicle, or price filters.
            </p>
            <button
              onClick={handleResetFilters}
              className="px-4 py-2 text-xs font-medium bg-sky-500 hover:bg-sky-400 text-white rounded-lg transition"
            >
              Reset All Filters
            </button>
          </div>
        )}

        {/* ================================================================== */}
        {/* OVERVIEW TAB CONTENT (DYNAMIC REPLACEMENT OF ALL HARDCODED VALUES) */}
        {/* ================================================================== */}
        {!loading && overview && overview.total_orders > 0 && activeTab === 'overview' && (
          <div className="space-y-6">
            {/* A. 6 Executive KPI Metric Cards */}
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-6 gap-4">
              {/* Card 1: Total Orders */}
              <div className="glass-card p-4 flex flex-col justify-between">
                <div className="flex items-center justify-between text-slate-400 mb-2">
                  <span className="text-xs font-medium">Total Orders</span>
                  <ShoppingBag className="w-4 h-4 text-sky-400" />
                </div>
                <div className="text-2xl font-bold text-white font-heading">
                  {overview.total_orders.toLocaleString()}
                </div>
                <div className="text-[11px] text-slate-400 mt-1">
                  All initialized orders
                </div>
              </div>

              {/* Card 2: Completion Rate */}
              <div className="glass-card p-4 flex flex-col justify-between">
                <div className="flex items-center justify-between text-slate-400 mb-2">
                  <span className="text-xs font-medium">Fulfillment Rate</span>
                  <CheckCircle2 className="w-4 h-4 text-emerald-400" />
                </div>
                <div className="text-2xl font-bold text-emerald-400 font-heading">
                  {overview.delivery_completion_rate.toFixed(2)}%
                </div>
                <div className="text-[11px] text-slate-400 mt-1">
                  {overview.delivered_orders.toLocaleString()} completed
                </div>
              </div>

              {/* Card 3: SLA Delay Rate */}
              <div className="glass-card p-4 flex flex-col justify-between">
                <div className="flex items-center justify-between text-slate-400 mb-2">
                  <span className="text-xs font-medium">SLA Delay Rate</span>
                  <AlertCircle className="w-4 h-4 text-rose-400" />
                </div>
                <div className="text-2xl font-bold text-rose-400 font-heading">
                  {overview.delay_rate.toFixed(2)}%
                </div>
                <div className="text-[11px] text-slate-400 mt-1">
                  Orders &gt; 45 minutes SLA
                </div>
              </div>

              {/* Card 4: Avg Delivery Duration */}
              <div className="glass-card p-4 flex flex-col justify-between">
                <div className="flex items-center justify-between text-slate-400 mb-2">
                  <span className="text-xs font-medium">Avg Duration</span>
                  <Clock className="w-4 h-4 text-violet-400" />
                </div>
                <div className="text-2xl font-bold text-white font-heading">
                  {overview.average_delivery_duration.toFixed(2)} <span className="text-xs font-normal text-slate-400">min</span>
                </div>
                <div className="text-[11px] text-slate-400 mt-1">
                  Median: {overview.median_delivery_duration.toFixed(1)} min
                </div>
              </div>

              {/* Card 5: Avg SLA Excess Delay */}
              <div className="glass-card p-4 flex flex-col justify-between">
                <div className="flex items-center justify-between text-slate-400 mb-2">
                  <span className="text-xs font-medium">Avg SLA Delay</span>
                  <ShieldAlert className="w-4 h-4 text-amber-400" />
                </div>
                <div className="text-2xl font-bold text-amber-400 font-heading">
                  {overview.average_delay_among_delayed_orders.toFixed(2)} <span className="text-xs font-normal text-slate-400">min</span>
                </div>
                <div className="text-[11px] text-slate-400 mt-1">
                  Delayed orders excess time
                </div>
              </div>

              {/* Card 6: Average Order Value */}
              <div className="glass-card p-4 flex flex-col justify-between">
                <div className="flex items-center justify-between text-slate-400 mb-2">
                  <span className="text-xs font-medium">Avg Order Value</span>
                  <DollarSign className="w-4 h-4 text-emerald-400" />
                </div>
                <div className="text-2xl font-bold text-white font-heading">
                  EGP {overview.average_order_value.toFixed(2)}
                </div>
                <div className="text-[11px] text-slate-400 mt-1">
                  Avg Dist: {overview.average_delivery_distance.toFixed(2)} km
                </div>
              </div>
            </div>

            {/* B. Overview Main Visual Grid */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {/* 1. City Delivery Performance Chart */}
              <div className="glass-card p-5 flex flex-col">
                <div className="flex items-center justify-between mb-4">
                  <div>
                    <h3 className="text-base font-semibold text-white font-heading">City Delivery Performance</h3>
                    <p className="text-xs text-slate-400">Mean Duration (min) & SLA Delay Rate (%) by City</p>
                  </div>
                  <Building2 className="w-5 h-5 text-sky-400" />
                </div>
                <div className="h-64 w-full">
                  <ResponsiveContainer width="100%" height="100%">
                    <BarChart data={cityData} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                      <CartesianGrid strokeDasharray="3 3" stroke="#334155" vertical={false} />
                      <XAxis dataKey="city" stroke="#94a3b8" tick={{ fontSize: 11 }} />
                      <YAxis yAxisId="left" stroke="#94a3b8" tick={{ fontSize: 11 }} domain={[0, 50]} />
                      <YAxis yAxisId="right" orientation="right" stroke="#ef4444" tick={{ fontSize: 11 }} domain={[0, 40]} />
                      <Tooltip
                        contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', borderRadius: '8px', fontSize: '12px' }}
                        formatter={(val: number, name: string) => [
                          name === 'delay_rate' ? `${val}%` : `${val} min`,
                          name === 'delay_rate' ? 'SLA Delay Rate' : 'Mean Duration'
                        ]}
                      />
                      <Legend wrapperStyle={{ fontSize: '11px', paddingTop: '10px' }} />
                      <Bar yAxisId="left" dataKey="average_delivery_duration" name="Mean Duration (min)" fill={COLORS.primary} radius={[4, 4, 0, 0]} />
                      <Bar yAxisId="right" dataKey="delay_rate" name="SLA Delay Rate (%)" fill={COLORS.danger} radius={[4, 4, 0, 0]} />
                    </BarChart>
                  </ResponsiveContainer>
                </div>
              </div>

              {/* 2. Delivery Duration Distribution (Histogram with 45-min SLA cutoff) */}
              <div className="glass-card p-5 flex flex-col">
                <div className="flex items-center justify-between mb-4">
                  <div>
                    <h3 className="text-base font-semibold text-white font-heading">Delivery Duration Distribution</h3>
                    <p className="text-xs text-slate-400">Fulfillment turnaround binned frequency & SLA threshold</p>
                  </div>
                  <Clock className="w-5 h-5 text-violet-400" />
                </div>
                <div className="h-64 w-full">
                  <ResponsiveContainer width="100%" height="100%">
                    <BarChart data={durationBins} margin={{ top: 10, right: 10, left: -10, bottom: 0 }}>
                      <CartesianGrid strokeDasharray="3 3" stroke="#334155" vertical={false} />
                      <XAxis dataKey="bin_label" stroke="#94a3b8" tick={{ fontSize: 11 }} />
                      <YAxis stroke="#94a3b8" tick={{ fontSize: 11 }} />
                      <Tooltip
                        contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', borderRadius: '8px', fontSize: '12px' }}
                        formatter={(val: number) => [`${val.toLocaleString()} orders`, 'Frequency']}
                      />
                      <Bar dataKey="count" name="Order Volume" fill={COLORS.secondary} radius={[4, 4, 0, 0]} />
                      <ReferenceLine x="45-55 min" stroke={COLORS.danger} strokeDasharray="3 3" label={{ value: '45m SLA', fill: COLORS.danger, fontSize: 10 }} />
                    </BarChart>
                  </ResponsiveContainer>
                </div>
              </div>

              {/* 3. Traffic Level Congestion Analysis */}
              <div className="glass-card p-5 flex flex-col">
                <div className="flex items-center justify-between mb-4">
                  <div>
                    <h3 className="text-base font-semibold text-white font-heading">Traffic Level vs Delay Rate</h3>
                    <p className="text-xs text-slate-400">Observed SLA delay rates across congestion levels</p>
                  </div>
                  <Activity className="w-5 h-5 text-amber-400" />
                </div>
                <div className="h-64 w-full">
                  <ResponsiveContainer width="100%" height="100%">
                    <BarChart data={trafficData} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                      <CartesianGrid strokeDasharray="3 3" stroke="#334155" vertical={false} />
                      <XAxis dataKey="traffic_level" stroke="#94a3b8" tick={{ fontSize: 11 }} />
                      <YAxis stroke="#94a3b8" tick={{ fontSize: 11 }} domain={[0, 35]} />
                      <Tooltip
                        contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', borderRadius: '8px', fontSize: '12px' }}
                        formatter={(val: number) => [`${val}%`, 'SLA Delay Rate']}
                      />
                      <Bar dataKey="delay_rate" name="Delay Rate (%)" fill={COLORS.warning} radius={[4, 4, 0, 0]}>
                        {trafficData.map((entry, index) => (
                          <Cell key={`cell-${index}`} fill={COLORS.trafficColors[index % COLORS.trafficColors.length]} />
                        ))}
                      </Bar>
                    </BarChart>
                  </ResponsiveContainer>
                </div>
              </div>

              {/* 4. Order Outcome Status Donut Chart */}
              <div className="glass-card p-5 flex flex-col">
                <div className="flex items-center justify-between mb-4">
                  <div>
                    <h3 className="text-base font-semibold text-white font-heading">Order Outcome Distribution</h3>
                    <p className="text-xs text-slate-400">Delivered vs Cancelled vs In Transit breakdown</p>
                  </div>
                  <Layers className="w-5 h-5 text-emerald-400" />
                </div>
                <div className="h-64 w-full flex items-center justify-center">
                  <ResponsiveContainer width="100%" height="100%">
                    <PieChart>
                      <Pie
                        data={statusData}
                        dataKey="count"
                        nameKey="status"
                        cx="50%"
                        cy="50%"
                        innerRadius={60}
                        outerRadius={90}
                        paddingAngle={4}
                      >
                        {statusData.map((entry, index) => (
                          <Cell key={`cell-${index}`} fill={COLORS.pieColors[index % COLORS.pieColors.length]} />
                        ))}
                      </Pie>
                      <Tooltip
                        contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', borderRadius: '8px', fontSize: '12px' }}
                        formatter={(val: number, name: string) => [`${val.toLocaleString()} orders (${((val / overview.total_orders) * 100).toFixed(1)}%)`, name]}
                      />
                      <Legend wrapperStyle={{ fontSize: '11px', paddingTop: '10px' }} />
                    </PieChart>
                  </ResponsiveContainer>
                </div>
              </div>
            </div>

            {/* C. Distance Analysis & Diagnostic Correlation Banner */}
            {distanceData && (
              <div className="glass-card p-5 border border-slate-800">
                <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-4 mb-4">
                  <div>
                    <div className="flex items-center gap-2">
                      <Compass className="w-5 h-5 text-sky-400" />
                      <h3 className="text-base font-semibold text-white font-heading">Distance vs Delivery Latency Analysis</h3>
                    </div>
                    <p className="text-xs text-slate-400 mt-0.5">
                      Empirical correlation between Haversine trip distance (km) and delivery duration (min)
                    </p>
                  </div>
                  <div className="flex items-center gap-3 bg-slate-900 border border-slate-800 px-4 py-2 rounded-xl text-xs">
                    <div>
                      <span className="text-slate-400">Pearson Correlation (r):</span>{' '}
                      <span className="font-mono font-bold text-sky-400">{distanceData.correlation_distance_duration.toFixed(4)}</span>
                    </div>
                    <div className="w-px h-4 bg-slate-800"></div>
                    <div>
                      <span className="text-slate-400">Fixed Overhead Signal:</span>{' '}
                      <span className="font-semibold text-emerald-400">Dominant</span>
                    </div>
                  </div>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                  {distanceData.distance_bins.map((bin) => (
                    <div key={bin.distance_bin} className="bg-slate-900/60 border border-slate-800 p-3.5 rounded-xl">
                      <div className="text-xs font-semibold text-slate-300">{bin.distance_bin}</div>
                      <div className="text-lg font-bold text-white mt-1 font-heading">{bin.average_duration.toFixed(2)} min</div>
                      <div className="flex items-center justify-between text-[11px] text-slate-400 mt-2 pt-2 border-t border-slate-800/80">
                        <span>Delay Rate: <strong className="text-rose-400">{bin.delay_rate.toFixed(1)}%</strong></span>
                        <span>Avg Dist: {bin.average_distance_km.toFixed(2)} km</span>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}

        {/* ================================================================== */}
        {/* GEOGRAPHIC TAB CONTENT */}
        {/* ================================================================== */}
        {!loading && cityData.length > 0 && activeTab === 'city' && (
          <div className="space-y-6">
            <div className="glass-card p-5">
              <h3 className="text-lg font-semibold text-white mb-1 font-heading">Metropolitan Market Breakdown</h3>
              <p className="text-xs text-slate-400 mb-4">Detailed delivery performance across all 7 Egyptian cities</p>
              
              <div className="overflow-x-auto">
                <table className="w-full text-xs text-left text-slate-300">
                  <thead className="bg-slate-900 text-slate-400 uppercase font-mono">
                    <tr>
                      <th className="p-3">City Name</th>
                      <th className="p-3">Total Orders</th>
                      <th className="p-3">Completed Deliveries</th>
                      <th className="p-3">SLA Delay Rate (%)</th>
                      <th className="p-3">Mean Duration (min)</th>
                      <th className="p-3">Mean Delay (min)</th>
                      <th className="p-3">Avg Order Value (EGP)</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-800">
                    {cityData.map(c => (
                      <tr key={c.city} className="hover:bg-slate-900/40">
                        <td className="p-3 font-semibold text-white">{c.city}</td>
                        <td className="p-3">{c.order_count.toLocaleString()}</td>
                        <td className="p-3">{c.delivered_orders.toLocaleString()}</td>
                        <td className="p-3 font-bold text-rose-400">{c.delay_rate.toFixed(2)}%</td>
                        <td className="p-3">{c.average_delivery_duration.toFixed(2)} min</td>
                        <td className="p-3">{c.average_delay.toFixed(2)} min</td>
                        <td className="p-3">EGP {c.average_order_value.toFixed(2)}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        )}

        {/* ================================================================== */}
        {/* TRAFFIC & TEMPORAL TAB CONTENT */}
        {/* ================================================================== */}
        {!loading && activeTab === 'traffic' && (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <div className="glass-card p-5">
              <h3 className="text-base font-semibold text-white mb-1 font-heading">Day of Week Delay Patterns</h3>
              <p className="text-xs text-slate-400 mb-4">Observed SLA delay rates from Monday to Sunday</p>
              <div className="h-64 w-full">
                <ResponsiveContainer width="100%" height="100%">
                  <LineChart data={dayOfWeekData}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
                    <XAxis dataKey="day_name" stroke="#94a3b8" tick={{ fontSize: 11 }} />
                    <YAxis stroke="#94a3b8" tick={{ fontSize: 11 }} domain={[15, 30]} />
                    <Tooltip contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', fontSize: '12px' }} />
                    <Line type="monotone" dataKey="delay_rate" name="Delay Rate (%)" stroke={COLORS.primary} strokeWidth={3} dot={{ r: 5 }} />
                  </LineChart>
                </ResponsiveContainer>
              </div>
            </div>

            <div className="glass-card p-5">
              <h3 className="text-base font-semibold text-white mb-1 font-heading">Time of Day Segment Breakdown</h3>
              <p className="text-xs text-slate-400 mb-4">SLA delay rates across 6 4-hour temporal segments</p>
              <div className="h-64 w-full">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={timeOfDayData}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
                    <XAxis dataKey="segment" stroke="#94a3b8" tick={{ fontSize: 10 }} />
                    <YAxis stroke="#94a3b8" tick={{ fontSize: 11 }} domain={[0, 30]} />
                    <Tooltip contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', fontSize: '12px' }} />
                    <Bar dataKey="delay_rate" name="Delay Rate (%)" fill={COLORS.secondary} radius={[4, 4, 0, 0]} />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </div>
          </div>
        )}

        {/* ================================================================== */}
        {/* FLEET & BASKET TAB CONTENT */}
        {/* ================================================================== */}
        {!loading && activeTab === 'fleet' && (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Courier Vehicle Performance */}
            <div className="glass-card p-5">
              <h3 className="text-base font-semibold text-white mb-1 font-heading">Courier Vehicle Transport Mode</h3>
              <p className="text-xs text-slate-400 mb-4">Delay rate & speed across Bicycle, Motorbike, and Car</p>
              <div className="h-64 w-full">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={vehicleData}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
                    <XAxis dataKey="vehicle" stroke="#94a3b8" />
                    <YAxis stroke="#94a3b8" domain={[0, 30]} />
                    <Tooltip contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', fontSize: '12px' }} />
                    <Bar dataKey="delay_rate" name="Delay Rate (%)" fill={COLORS.primary} radius={[4, 4, 0, 0]} />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </div>

            {/* Order Item Quantity Dynamics */}
            <div className="glass-card p-5">
              <h3 className="text-base font-semibold text-white mb-1 font-heading">Item Quantity vs SLA Delay Rate</h3>
              <p className="text-xs text-slate-400 mb-4">Impact of basket item count (1 to 5 items) on fulfillment time</p>
              <div className="h-64 w-full">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={quantityData}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
                    <XAxis dataKey="quantity" stroke="#94a3b8" tickFormatter={(q) => `${q} Item(s)`} />
                    <YAxis stroke="#94a3b8" domain={[0, 30]} />
                    <Tooltip contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', fontSize: '12px' }} />
                    <Bar dataKey="delay_rate" name="Delay Rate (%)" fill={COLORS.danger} radius={[4, 4, 0, 0]} />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </div>
          </div>
        )}

        {/* ================================================================== */}
        {/* DIAGNOSTIC INSIGHTS TAB CONTENT */}
        {/* ================================================================== */}
        {!loading && activeTab === 'insights' && (
          <div className="space-y-4">
            {/* Non-causal Disclaimer Alert Banner */}
            <div className="p-3.5 rounded-xl bg-sky-500/10 border border-sky-500/20 text-sky-300 flex items-center gap-2.5 text-xs">
              <ShieldAlert className="w-4 h-4 text-sky-400 shrink-0" />
              <span>
                <strong>Methodological Disclaimer:</strong> Observed relationships describe patterns in this dataset and do not establish causation.
              </span>
            </div>

            <div className="flex items-center justify-between">
              <div>
                <h3 className="text-lg font-semibold text-white font-heading">Descriptive Diagnostic Observations</h3>
                <p className="text-xs text-slate-400">Dynamically generated from grouped API calculations</p>
              </div>
              <span className="text-xs font-mono bg-sky-500/10 text-sky-400 px-3 py-1 rounded-full border border-sky-500/20">
                {insights.length} Dynamic Insights
              </span>
            </div>

            {insights.length === 0 ? (
              <div className="glass-card p-8 text-center text-slate-400 text-xs">
                Insufficient group sample observations to generate diagnostic signals for the active filter selection.
              </div>
            ) : (
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {insights.map(item => (
                  <div
                    key={item.id}
                    className={`glass-card p-4 space-y-2.5 border-l-4 ${
                      item.direction === 'positive'
                        ? 'border-l-emerald-500'
                        : item.direction === 'negative' || item.direction === 'elevation'
                        ? 'border-l-rose-500'
                        : 'border-l-sky-500'
                    }`}
                  >
                    <div className="flex items-center justify-between gap-2">
                      <span className="text-[10px] font-bold uppercase tracking-wider text-sky-400 bg-sky-500/10 px-2 py-0.5 rounded border border-sky-500/20">
                        {item.category}
                      </span>
                      <span className="text-[10px] font-mono text-slate-400 bg-slate-900 px-2 py-0.5 rounded border border-slate-800">
                        N = {item.sample_size.toLocaleString()} orders
                      </span>
                    </div>

                    <h4 className="text-sm font-semibold text-white font-heading">{item.title}</h4>
                    <p className="text-xs text-slate-300 leading-relaxed">{item.description}</p>

                    <div className="pt-2 border-t border-slate-800/80 flex items-center justify-between text-xs font-mono">
                      <span className="text-slate-400">Observed Metric:</span>
                      <span className={`font-bold ${
                        item.direction === 'positive'
                          ? 'text-emerald-400'
                          : item.direction === 'negative' || item.direction === 'elevation'
                          ? 'text-rose-400'
                          : 'text-sky-400'
                      }`}>
                        {item.metric}
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}
        {/* ================================================================== */}
        {/* DATA EXPLORER TAB CONTENT */}
        {/* ================================================================== */}
        {activeTab === 'explorer' && (
          <div className="space-y-6">
            {/* A. High-Level Dataset Summary Metrics Cards */}
            {explorerSummary && (
              <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-4">
                <div className="glass-card p-4">
                  <div className="flex items-center justify-between text-slate-400 mb-1">
                    <span className="text-[11px] font-medium">Total Records</span>
                    <Database className="w-4 h-4 text-sky-400" />
                  </div>
                  <div className="text-xl font-bold text-white font-heading">
                    {explorerSummary.total_rows.toLocaleString()}
                  </div>
                  <div className="text-[10px] text-slate-400 mt-0.5">Dataset rows</div>
                </div>

                <div className="glass-card p-4">
                  <div className="flex items-center justify-between text-slate-400 mb-1">
                    <span className="text-[11px] font-medium">Total Fields</span>
                    <FileCode className="w-4 h-4 text-violet-400" />
                  </div>
                  <div className="text-xl font-bold text-white font-heading">
                    {explorerSummary.total_columns}
                  </div>
                  <div className="text-[10px] text-slate-400 mt-0.5">Schema columns</div>
                </div>

                <div className="glass-card p-4">
                  <div className="flex items-center justify-between text-slate-400 mb-1">
                    <span className="text-[11px] font-medium">Unique Customers</span>
                    <Users className="w-4 h-4 text-emerald-400" />
                  </div>
                  <div className="text-xl font-bold text-emerald-400 font-heading">
                    {explorerSummary.unique_users.toLocaleString()}
                  </div>
                  <div className="text-[10px] text-slate-400 mt-0.5">User_ID accounts</div>
                </div>

                <div className="glass-card p-4">
                  <div className="flex items-center justify-between text-slate-400 mb-1">
                    <span className="text-[11px] font-medium">Restaurants</span>
                    <Store className="w-4 h-4 text-amber-400" />
                  </div>
                  <div className="text-xl font-bold text-amber-400 font-heading">
                    {explorerSummary.unique_restaurants.toLocaleString()}
                  </div>
                  <div className="text-[10px] text-slate-400 mt-0.5">Merchant partners</div>
                </div>

                <div className="glass-card p-4">
                  <div className="flex items-center justify-between text-slate-400 mb-1">
                    <span className="text-[11px] font-medium">Couriers</span>
                    <Truck className="w-4 h-4 text-sky-400" />
                  </div>
                  <div className="text-xl font-bold text-sky-400 font-heading">
                    {explorerSummary.unique_drivers.toLocaleString()}
                  </div>
                  <div className="text-[10px] text-slate-400 mt-0.5">Active Driver_IDs</div>
                </div>

                <div className="glass-card p-4">
                  <div className="flex items-center justify-between text-slate-400 mb-1">
                    <span className="text-[11px] font-medium">Markets</span>
                    <Building2 className="w-4 h-4 text-purple-400" />
                  </div>
                  <div className="text-xl font-bold text-purple-400 font-heading">
                    {explorerSummary.unique_cities}
                  </div>
                  <div className="text-[10px] text-slate-400 mt-0.5">Egyptian cities</div>
                </div>
              </div>
            )}

            {/* B. Explorer Sub-Tab Control Bar */}
            <div className="flex flex-wrap items-center justify-between gap-4 bg-slate-900 border border-slate-800 p-2 rounded-xl">
              <div className="flex gap-2 text-xs font-medium">
                <button
                  onClick={() => setExplorerSubTab('records')}
                  className={`px-3 py-1.5 rounded-lg flex items-center gap-1.5 transition ${
                    explorerSubTab === 'records'
                      ? 'bg-sky-500 text-white font-semibold'
                      : 'text-slate-400 hover:text-white hover:bg-slate-800'
                  }`}
                >
                  <Table className="w-3.5 h-3.5" />
                  <span>Orders Table Preview</span>
                </button>
                <button
                  onClick={() => setExplorerSubTab('schema')}
                  className={`px-3 py-1.5 rounded-lg flex items-center gap-1.5 transition ${
                    explorerSubTab === 'schema'
                      ? 'bg-sky-500 text-white font-semibold'
                      : 'text-slate-400 hover:text-white hover:bg-slate-800'
                  }`}
                >
                  <FileCode className="w-3.5 h-3.5" />
                  <span>Column Schema ({columnSchema.length})</span>
                </button>
                <button
                  onClick={() => setExplorerSubTab('stats')}
                  className={`px-3 py-1.5 rounded-lg flex items-center gap-1.5 transition ${
                    explorerSubTab === 'stats'
                      ? 'bg-sky-500 text-white font-semibold'
                      : 'text-slate-400 hover:text-white hover:bg-slate-800'
                  }`}
                >
                  <BarChart3 className="w-3.5 h-3.5" />
                  <span>Summary Distributions</span>
                </button>
              </div>

              {explorerRecords && explorerSubTab === 'records' && (
                <div className="text-xs text-slate-400 font-mono">
                  Showing <strong className="text-white">{(explorerRecords.page - 1) * explorerRecords.page_size + 1}</strong> to{' '}
                  <strong className="text-white">{Math.min(explorerRecords.page * explorerRecords.page_size, explorerRecords.total_records)}</strong> of{' '}
                  <strong className="text-sky-400">{explorerRecords.total_records.toLocaleString()}</strong> orders
                </div>
              )}
            </div>

            {/* C. SUB-TAB 1: ORDERS TABLE PREVIEW */}
            {explorerSubTab === 'records' && (
              <div className="glass-card p-5 space-y-4">
                {/* Search & Table Filter Header */}
                <div className="flex flex-col sm:flex-row items-center justify-between gap-3 text-xs">
                  <div className="relative flex-1 max-w-md w-full">
                    <Search className="w-4 h-4 text-slate-400 absolute left-3 top-2.5" />
                    <input
                      type="text"
                      placeholder="Search Order ID, Restaurant, City, Vehicle, Item..."
                      value={explorerSearch}
                      onChange={e => {
                        setExplorerSearch(e.target.value);
                        setExplorerPage(1);
                      }}
                      className="w-full bg-slate-950 border border-slate-800 rounded-lg pl-9 pr-3 py-2 text-slate-200 placeholder-slate-500 focus:outline-none focus:border-sky-500"
                    />
                  </div>

                  <div className="flex flex-wrap items-center gap-2">
                    <select
                      value={explorerCityFilter}
                      onChange={e => {
                        setExplorerCityFilter(e.target.value);
                        setExplorerPage(1);
                      }}
                      className="bg-slate-950 text-slate-200 border border-slate-800 rounded-lg px-2.5 py-1.5 focus:outline-none focus:border-sky-500"
                    >
                      <option value="">All Cities</option>
                      {filterChoices?.cities.map(c => (
                        <option key={c} value={c}>{c}</option>
                      ))}
                    </select>

                    <select
                      value={explorerVehicleFilter}
                      onChange={e => {
                        setExplorerVehicleFilter(e.target.value);
                        setExplorerPage(1);
                      }}
                      className="bg-slate-950 text-slate-200 border border-slate-800 rounded-lg px-2.5 py-1.5 focus:outline-none focus:border-sky-500"
                    >
                      <option value="">All Vehicles</option>
                      {filterChoices?.vehicles.map(v => (
                        <option key={v} value={v}>{v}</option>
                      ))}
                    </select>

                    <select
                      value={explorerStatusFilter}
                      onChange={e => {
                        setExplorerStatusFilter(e.target.value);
                        setExplorerPage(1);
                      }}
                      className="bg-slate-950 text-slate-200 border border-slate-800 rounded-lg px-2.5 py-1.5 focus:outline-none focus:border-sky-500"
                    >
                      <option value="">All Statuses</option>
                      <option value="Delivered">Delivered</option>
                      <option value="Cancelled">Cancelled</option>
                      <option value="In Transit">In Transit</option>
                    </select>
                  </div>
                </div>

                {/* Table Data Render */}
                {explorerLoading ? (
                  <div className="py-12 text-center text-slate-400 space-y-2">
                    <RefreshCw className="w-6 h-6 text-sky-400 animate-spin mx-auto" />
                    <p className="text-xs">Fetching page {explorerPage} from backend...</p>
                  </div>
                ) : explorerRecords && explorerRecords.records.length > 0 ? (
                  <div className="overflow-x-auto border border-slate-800 rounded-lg">
                    <table className="w-full text-xs text-left text-slate-300">
                      <thead className="bg-slate-900 text-slate-400 uppercase font-mono border-b border-slate-800">
                        <tr>
                          <th className="p-3">Order ID</th>
                          <th className="p-3">City</th>
                          <th className="p-3">Status</th>
                          <th className="p-3">Duration</th>
                          <th className="p-3">Total Price</th>
                          <th className="p-3">Distance</th>
                          <th className="p-3">Vehicle</th>
                          <th className="p-3">Traffic</th>
                          <th className="p-3">Time Segment</th>
                          <th className="p-3">Day Name</th>
                          <th className="p-3">Qty</th>
                          <th className="p-3">SLA Delay</th>
                        </tr>
                      </thead>
                      <tbody className="divide-y divide-slate-800/80">
                        {explorerRecords.records.map((r, i) => (
                          <tr key={r.Order_ID || i} className="hover:bg-slate-900/50 transition">
                            <td className="p-3 font-mono font-bold text-white">#{r.Order_ID}</td>
                            <td className="p-3 font-semibold text-sky-300">{r.City}</td>
                            <td className="p-3">
                              <span className={`px-2 py-0.5 rounded-full text-[10px] font-semibold border ${
                                r.Order_Status === 'Delivered'
                                  ? 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20'
                                  : r.Order_Status === 'Cancelled'
                                  ? 'bg-rose-500/10 text-rose-400 border-rose-500/20'
                                  : 'bg-amber-500/10 text-amber-400 border-amber-500/20'
                              }`}>
                                {r.Order_Status}
                              </span>
                            </td>
                            <td className="p-3 font-mono">{r.Delivery_Duration_Minutes} min</td>
                            <td className="p-3 font-mono text-emerald-400">EGP {Number(r.Total_Price).toFixed(2)}</td>
                            <td className="p-3 font-mono">{Number(r.Delivery_Distance_km).toFixed(2)} km</td>
                            <td className="p-3">{r.Driver_Vehicle}</td>
                            <td className="p-3">{r.Traffic_Level}</td>
                            <td className="p-3 text-slate-400">{r.Time_Of_Day_Segment}</td>
                            <td className="p-3 text-slate-400">{r.Order_DayName}</td>
                            <td className="p-3 font-mono">{r.Quantity}</td>
                            <td className="p-3">
                              {r.Is_Delayed_TARGET === 1 ? (
                                <span className="text-rose-400 font-bold font-mono">+{Number(r.Delay_Minutes_TARGET).toFixed(1)}m</span>
                              ) : (
                                <span className="text-slate-500 font-mono">On-Time</span>
                              )}
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                ) : (
                  <div className="py-12 text-center text-slate-400 space-y-2">
                    <ShieldAlert className="w-8 h-8 text-amber-400 mx-auto" />
                    <p className="text-sm font-semibold text-white">No Orders Match Search Query</p>
                    <p className="text-xs text-slate-400">Try adjusting your search term or filters.</p>
                  </div>
                )}

                {/* Pagination Controls Footer */}
                {explorerRecords && explorerRecords.total_pages > 0 && (
                  <div className="flex flex-col sm:flex-row items-center justify-between gap-4 pt-2 text-xs">
                    <div className="flex items-center gap-2">
                      <span className="text-slate-400">Per page:</span>
                      <select
                        value={explorerPageSize}
                        onChange={e => {
                          setExplorerPageSize(Number(e.target.value));
                          setExplorerPage(1);
                        }}
                        className="bg-slate-950 text-slate-200 border border-slate-800 rounded px-2 py-1 focus:outline-none"
                      >
                        <option value={10}>10</option>
                        <option value={20}>20</option>
                        <option value={50}>50</option>
                        <option value={100}>100</option>
                      </select>
                    </div>

                    <div className="flex items-center gap-3">
                      <button
                        onClick={() => setExplorerPage(p => Math.max(1, p - 1))}
                        disabled={explorerPage <= 1 || explorerLoading}
                        className="p-1.5 bg-slate-900 border border-slate-800 hover:bg-slate-800 rounded text-slate-300 disabled:opacity-40 transition"
                      >
                        <ChevronLeft className="w-4 h-4" />
                      </button>
                      <span className="font-mono text-slate-300">
                        Page <strong className="text-white">{explorerPage}</strong> of{' '}
                        <strong className="text-white">{explorerRecords.total_pages}</strong>
                      </span>
                      <button
                        onClick={() => setExplorerPage(p => Math.min(explorerRecords.total_pages, p + 1))}
                        disabled={explorerPage >= explorerRecords.total_pages || explorerLoading}
                        className="p-1.5 bg-slate-900 border border-slate-800 hover:bg-slate-800 rounded text-slate-300 disabled:opacity-40 transition"
                      >
                        <ChevronRight className="w-4 h-4" />
                      </button>
                    </div>
                  </div>
                )}
              </div>
            )}

            {/* D. SUB-TAB 2: COLUMN SCHEMA & TYPES */}
            {explorerSubTab === 'schema' && (
              <div className="glass-card p-5 space-y-4">
                <div className="flex items-center justify-between">
                  <div>
                    <h3 className="text-base font-semibold text-white font-heading">Dataset Schema Specification</h3>
                    <p className="text-xs text-slate-400">Complete list of all 55 features, datatypes, missing values, and sample values</p>
                  </div>
                  <div className="relative max-w-xs w-full">
                    <Search className="w-3.5 h-3.5 text-slate-400 absolute left-3 top-2.5" />
                    <input
                      type="text"
                      placeholder="Filter column names..."
                      value={schemaSearch}
                      onChange={e => setSchemaSearch(e.target.value)}
                      className="w-full bg-slate-950 border border-slate-800 rounded-lg pl-8 pr-3 py-1.5 text-xs text-slate-200 placeholder-slate-500 focus:outline-none focus:border-sky-500"
                    />
                  </div>
                </div>

                <div className="overflow-x-auto border border-slate-800 rounded-lg">
                  <table className="w-full text-xs text-left text-slate-300">
                    <thead className="bg-slate-900 text-slate-400 uppercase font-mono border-b border-slate-800">
                      <tr>
                        <th className="p-3">#</th>
                        <th className="p-3">Column Name</th>
                        <th className="p-3">Data Type</th>
                        <th className="p-3">Unique Values</th>
                        <th className="p-3">Missing Count (%)</th>
                        <th className="p-3">Sample Values</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-slate-800/80">
                      {columnSchema
                        .filter(col => col.column_name.toLowerCase().includes(schemaSearch.toLowerCase()))
                        .map((col, idx) => (
                          <tr key={col.column_name} className="hover:bg-slate-900/50 transition">
                            <td className="p-3 font-mono text-slate-500">{idx + 1}</td>
                            <td className="p-3 font-semibold text-white font-mono">{col.column_name}</td>
                            <td className="p-3">
                              <span className={`px-2 py-0.5 rounded text-[10px] font-mono border ${
                                col.data_type.includes('int')
                                  ? 'bg-sky-500/10 text-sky-400 border-sky-500/20'
                                  : col.data_type.includes('float')
                                  ? 'bg-purple-500/10 text-purple-400 border-purple-500/20'
                                  : 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20'
                              }`}>
                                {col.data_type}
                              </span>
                            </td>
                            <td className="p-3 font-mono">{col.unique_count.toLocaleString()}</td>
                            <td className="p-3 font-mono">
                              {col.missing_count === 0 ? (
                                <span className="text-emerald-400 font-semibold">0 (0%)</span>
                              ) : (
                                <span className="text-rose-400 font-semibold">{col.missing_count} ({col.missing_percentage}%)</span>
                              )}
                            </td>
                            <td className="p-3 font-mono text-slate-400 truncate max-w-xs">
                              {col.sample_values.join(', ')}
                            </td>
                          </tr>
                        ))}
                    </tbody>
                  </table>
                </div>
              </div>
            )}

            {/* E. SUB-TAB 3: NUMERICAL & CATEGORICAL STATS */}
            {explorerSubTab === 'stats' && explorerStats && (
              <div className="space-y-6">
                {/* Numerical Summary Statistics */}
                <div className="glass-card p-5 space-y-3">
                  <h3 className="text-base font-semibold text-white font-heading">Numerical Summary Statistics</h3>
                  <p className="text-xs text-slate-400">Descriptive metrics (mean, std, percentiles) for numerical features</p>
                  
                  <div className="overflow-x-auto border border-slate-800 rounded-lg">
                    <table className="w-full text-xs text-left text-slate-300">
                      <thead className="bg-slate-900 text-slate-400 uppercase font-mono border-b border-slate-800">
                        <tr>
                          <th className="p-3">Feature Name</th>
                          <th className="p-3">Count</th>
                          <th className="p-3">Mean</th>
                          <th className="p-3">Std Dev</th>
                          <th className="p-3">Min</th>
                          <th className="p-3">25%</th>
                          <th className="p-3">Median (50%)</th>
                          <th className="p-3">75%</th>
                          <th className="p-3">Max</th>
                        </tr>
                      </thead>
                      <tbody className="divide-y divide-slate-800/80">
                        {explorerStats.numerical_stats.map(ns => (
                          <tr key={ns.column_name} className="hover:bg-slate-900/50">
                            <td className="p-3 font-semibold text-white font-mono">{ns.column_name}</td>
                            <td className="p-3 font-mono">{ns.count.toLocaleString()}</td>
                            <td className="p-3 font-mono text-sky-400">{ns.mean}</td>
                            <td className="p-3 font-mono">{ns.std}</td>
                            <td className="p-3 font-mono">{ns.min}</td>
                            <td className="p-3 font-mono">{ns.p25}</td>
                            <td className="p-3 font-mono text-emerald-400">{ns.median}</td>
                            <td className="p-3 font-mono">{ns.p75}</td>
                            <td className="p-3 font-mono">{ns.max}</td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </div>

                {/* Categorical Distribution Cards */}
                <div className="glass-card p-5 space-y-3">
                  <h3 className="text-base font-semibold text-white font-heading">Categorical Feature Distributions</h3>
                  <p className="text-xs text-slate-400">Top frequency breakdown for categorical features</p>
                  
                  <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                    {explorerStats.categorical_stats.map(cs => (
                      <div key={cs.column_name} className="bg-slate-900/70 border border-slate-800 p-4 rounded-xl space-y-2">
                        <div className="flex items-center justify-between border-b border-slate-800 pb-2">
                          <span className="font-semibold text-sky-400 font-mono text-xs">{cs.column_name}</span>
                          <span className="text-[10px] text-slate-400 font-mono">{cs.unique_count} unique</span>
                        </div>
                        <div className="space-y-1.5 pt-1">
                          {Object.entries(cs.value_counts).map(([val, count]) => (
                            <div key={val} className="flex items-center justify-between text-xs">
                              <span className="text-slate-300 truncate max-w-[150px]">{val}</span>
                              <span className="font-mono text-slate-400">{count.toLocaleString()}</span>
                            </div>
                          ))}
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            )}
          </div>
        )}

        {/* ================================================================== */}
        {/* ANALYTICAL REPORT TAB CONTENT */}
        {/* ================================================================== */}
        {activeTab === 'reports' && overview && (
          <div className="space-y-8">
            {/* Report Header & PDF Export Action Bar */}
            <div className="glass-card p-6 flex flex-col md:flex-row md:items-center justify-between gap-4 border-l-4 border-l-sky-500">
              <div>
                <div className="flex items-center gap-2 mb-1">
                  <span className="px-2.5 py-0.5 rounded-full text-[10px] font-bold uppercase tracking-wider bg-sky-500/20 text-sky-300 border border-sky-500/30">
                    Phase 4 Analytical Report
                  </span>
                  <span className="text-xs text-slate-400 font-mono">Dataset: food_delivery_10k.csv</span>
                </div>
                <h2 className="text-2xl font-bold text-white font-heading">FoodFlow Delivery Performance & Diagnostic Report</h2>
                <p className="text-xs text-slate-400 mt-1">
                  Empirical analytics generated live from backend APIs &bull; N = {overview.total_orders.toLocaleString()} records
                </p>
              </div>

              <div className="flex items-center gap-3 no-print">
                <button
                  onClick={() => window.print()}
                  className="px-4 py-2 bg-sky-500 hover:bg-sky-400 text-white font-semibold text-xs rounded-xl flex items-center gap-2 shadow-lg shadow-sky-500/20 transition"
                >
                  <Printer className="w-4 h-4" />
                  <span>Export Report as PDF</span>
                </button>
              </div>
            </div>

            {/* MANDATORY NON-CAUSAL DISCLAIMER BANNER */}
            <div className="p-4 rounded-xl bg-amber-500/10 border border-amber-500/30 text-amber-300 flex items-start gap-3 text-xs leading-relaxed">
              <ShieldAlert className="w-5 h-5 text-amber-400 shrink-0 mt-0.5" />
              <div>
                <strong className="text-amber-200 block mb-0.5">Methodological Non-Causality Disclaimer:</strong>
                These findings describe observed patterns within the dataset and should not be interpreted as causal effects.
              </div>
            </div>

            {/* SECTION 1: EXECUTIVE SUMMARY */}
            <section className="glass-card p-6 space-y-4">
              <div className="border-b border-slate-800 pb-3">
                <h3 className="text-lg font-bold text-white font-heading flex items-center gap-2">
                  <span className="text-sky-400 font-mono text-sm">01.</span> Executive Summary
                </h3>
                <p className="text-xs text-slate-400">High-level operational performance metrics for the evaluated order sample</p>
              </div>

              <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 gap-3 font-mono">
                <div className="bg-slate-900/80 border border-slate-800 p-3 rounded-lg">
                  <div className="text-[10px] text-slate-400 uppercase">Total Orders</div>
                  <div className="text-lg font-bold text-white mt-1">{overview.total_orders.toLocaleString()}</div>
                </div>
                <div className="bg-slate-900/80 border border-slate-800 p-3 rounded-lg">
                  <div className="text-[10px] text-slate-400 uppercase">Completion Rate</div>
                  <div className="text-lg font-bold text-emerald-400 mt-1">{overview.delivery_completion_rate.toFixed(2)}%</div>
                  <div className="text-[10px] text-slate-500">{overview.delivered_orders.toLocaleString()} orders</div>
                </div>
                <div className="bg-slate-900/80 border border-slate-800 p-3 rounded-lg">
                  <div className="text-[10px] text-slate-400 uppercase">Cancellation Rate</div>
                  <div className="text-lg font-bold text-rose-400 mt-1">{overview.cancellation_rate.toFixed(2)}%</div>
                  <div className="text-[10px] text-slate-500">{overview.cancelled_orders.toLocaleString()} orders</div>
                </div>
                <div className="bg-slate-900/80 border border-slate-800 p-3 rounded-lg">
                  <div className="text-[10px] text-slate-400 uppercase">Overall SLA Delay Rate</div>
                  <div className="text-lg font-bold text-amber-400 mt-1">{overview.delay_rate.toFixed(2)}%</div>
                  <div className="text-[10px] text-slate-500">Delivered orders</div>
                </div>
                <div className="bg-slate-900/80 border border-slate-800 p-3 rounded-lg">
                  <div className="text-[10px] text-slate-400 uppercase">Mean Duration</div>
                  <div className="text-lg font-bold text-sky-400 mt-1">{overview.average_delivery_duration.toFixed(2)} min</div>
                  <div className="text-[10px] text-slate-500">Median: {overview.median_delivery_duration.toFixed(1)} min</div>
                </div>
                <div className="bg-slate-900/80 border border-slate-800 p-3 rounded-lg">
                  <div className="text-[10px] text-slate-400 uppercase">Avg Delay (Delayed)</div>
                  <div className="text-lg font-bold text-rose-400 mt-1">+{overview.average_delay_among_delayed_orders.toFixed(2)} min</div>
                </div>
                <div className="bg-slate-900/80 border border-slate-800 p-3 rounded-lg">
                  <div className="text-[10px] text-slate-400 uppercase">Gross Revenue</div>
                  <div className="text-lg font-bold text-emerald-400 mt-1">
                    EGP {((overview.total_orders * overview.average_order_value) / 1000).toFixed(1)}k
                  </div>
                </div>
                <div className="bg-slate-900/80 border border-slate-800 p-3 rounded-lg">
                  <div className="text-[10px] text-slate-400 uppercase">Avg Order Value</div>
                  <div className="text-lg font-bold text-white mt-1">EGP {overview.average_order_value.toFixed(2)}</div>
                </div>
                <div className="bg-slate-900/80 border border-slate-800 p-3 rounded-lg">
                  <div className="text-[10px] text-slate-400 uppercase">Avg Distance</div>
                  <div className="text-lg font-bold text-purple-400 mt-1">{overview.average_delivery_distance.toFixed(2)} km</div>
                </div>
                <div className="bg-slate-900/80 border border-slate-800 p-3 rounded-lg">
                  <div className="text-[10px] text-slate-400 uppercase">Avg Basket Qty</div>
                  <div className="text-lg font-bold text-sky-400 mt-1">{overview.average_quantity.toFixed(1)} items</div>
                </div>
              </div>

              <p className="text-xs text-slate-300 leading-relaxed pt-2">
                This report synthesizes fulfillment metrics across {overview.total_orders.toLocaleString()} food delivery orders.
                The overall delivery completion rate stands at <strong className="text-emerald-400">{overview.delivery_completion_rate.toFixed(2)}%</strong>, while
                cancellations account for <strong className="text-rose-400">{overview.cancellation_rate.toFixed(2)}%</strong> of total volume. Among completed orders,
                an observed SLA delay rate of <strong className="text-amber-400">{overview.delay_rate.toFixed(2)}%</strong> was recorded, with an average delay magnitude
                of <strong className="text-white">+{overview.average_delay_among_delayed_orders.toFixed(2)} minutes</strong> beyond estimated delivery windows.
              </p>
            </section>

            {/* SECTION 2: DELIVERY PERFORMANCE */}
            <section className="glass-card p-6 space-y-4">
              <div className="border-b border-slate-800 pb-3">
                <h3 className="text-lg font-bold text-white font-heading flex items-center gap-2">
                  <span className="text-sky-400 font-mono text-sm">02.</span> Delivery Performance & Fulfillment Status
                </h3>
                <p className="text-xs text-slate-400">Order outcome distribution and delivery duration dynamics</p>
              </div>

              <div className="overflow-x-auto border border-slate-800 rounded-lg">
                <table className="w-full text-xs text-left text-slate-300">
                  <thead className="bg-slate-900 text-slate-400 uppercase font-mono border-b border-slate-800">
                    <tr>
                      <th className="p-3">Order Outcome Status</th>
                      <th className="p-3">Order Volume</th>
                      <th className="p-3">Volume Share (%)</th>
                      <th className="p-3">SLA Delay Rate (%)</th>
                      <th className="p-3">Average Delivery Duration</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-800/80">
                    {statusData.map(st => (
                      <tr key={st.status} className="hover:bg-slate-900/50">
                        <td className="p-3 font-semibold text-white">
                          <span className={`px-2 py-0.5 rounded-full text-[10px] border ${
                            st.status === 'Delivered'
                              ? 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20'
                              : st.status === 'Cancelled'
                              ? 'bg-rose-500/10 text-rose-400 border-rose-500/20'
                              : 'bg-amber-500/10 text-amber-400 border-amber-500/20'
                          }`}>
                            {st.status}
                          </span>
                        </td>
                        <td className="p-3 font-mono">{st.count.toLocaleString()}</td>
                        <td className="p-3 font-mono font-semibold">{st.percentage.toFixed(2)}%</td>
                        <td className="p-3 font-mono">
                          {st.status === 'Delivered' ? (
                            <span className="text-amber-400 font-bold">{overview.delay_rate.toFixed(2)}%</span>
                          ) : (
                            <span className="text-slate-500">N/A</span>
                          )}
                        </td>
                        <td className="p-3 font-mono">
                          {st.status === 'Delivered' ? `${overview.average_delivery_duration.toFixed(2)} min` : 'N/A'}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </section>

            {/* SECTION 3: DELAY ANALYSIS */}
            <section className="glass-card p-6 space-y-4">
              <div className="border-b border-slate-800 pb-3">
                <h3 className="text-lg font-bold text-white font-heading flex items-center gap-2">
                  <span className="text-sky-400 font-mono text-sm">03.</span> Temporal & Operational Delay Analysis
                </h3>
                <p className="text-xs text-slate-400">Observed SLA delay rates across time segments, days of week, and rush hour windows</p>
              </div>

              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                {/* Time of Day Segment Breakdown */}
                <div className="space-y-2">
                  <h4 className="text-xs font-semibold text-sky-400 uppercase font-mono tracking-wider">Delay Rate by Time Segment</h4>
                  <div className="border border-slate-800 rounded-lg overflow-hidden">
                    <table className="w-full text-xs text-left text-slate-300">
                      <thead className="bg-slate-900 text-slate-400 uppercase font-mono border-b border-slate-800">
                        <tr>
                          <th className="p-2.5">Time Segment</th>
                          <th className="p-2.5">Orders</th>
                          <th className="p-2.5">Delay Rate</th>
                          <th className="p-2.5">Avg Duration</th>
                        </tr>
                      </thead>
                      <tbody className="divide-y divide-slate-800/80 font-mono">
                        {timeOfDayData.map(tod => (
                          <tr key={tod.segment} className="hover:bg-slate-900/50">
                            <td className="p-2.5 font-sans font-medium text-white">{tod.segment}</td>
                            <td className="p-2.5">{tod.order_count.toLocaleString()}</td>
                            <td className="p-2.5 font-bold text-amber-400">{tod.delay_rate.toFixed(2)}%</td>
                            <td className="p-2.5">{tod.average_duration.toFixed(1)}m</td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </div>

                {/* Day of Week Breakdown */}
                <div className="space-y-2">
                  <h4 className="text-xs font-semibold text-sky-400 uppercase font-mono tracking-wider">Delay Rate by Day of Week</h4>
                  <div className="border border-slate-800 rounded-lg overflow-hidden">
                    <table className="w-full text-xs text-left text-slate-300">
                      <thead className="bg-slate-900 text-slate-400 uppercase font-mono border-b border-slate-800">
                        <tr>
                          <th className="p-2.5">Day Name</th>
                          <th className="p-2.5">Orders</th>
                          <th className="p-2.5">Delay Rate</th>
                          <th className="p-2.5">Avg Duration</th>
                        </tr>
                      </thead>
                      <tbody className="divide-y divide-slate-800/80 font-mono">
                        {dayOfWeekData.map(dow => (
                          <tr key={dow.day_name} className="hover:bg-slate-900/50">
                            <td className="p-2.5 font-sans font-medium text-white">{dow.day_name}</td>
                            <td className="p-2.5">{dow.order_count.toLocaleString()}</td>
                            <td className="p-2.5 font-bold text-amber-400">{dow.delay_rate.toFixed(2)}%</td>
                            <td className="p-2.5">{dow.average_duration.toFixed(1)}m</td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </div>
              </div>
            </section>

            {/* SECTION 4: GEOGRAPHIC ANALYSIS */}
            <section className="glass-card p-6 space-y-4">
              <div className="border-b border-slate-800 pb-3">
                <h3 className="text-lg font-bold text-white font-heading flex items-center gap-2">
                  <span className="text-sky-400 font-mono text-sm">04.</span> Geographic Market Analysis
                </h3>
                <p className="text-xs text-slate-400">City-level comparison across all 7 evaluated Egyptian municipalities</p>
              </div>

              <div className="overflow-x-auto border border-slate-800 rounded-lg">
                <table className="w-full text-xs text-left text-slate-300">
                  <thead className="bg-slate-900 text-slate-400 uppercase font-mono border-b border-slate-800">
                    <tr>
                      <th className="p-3">City Market</th>
                      <th className="p-3">Total Orders</th>
                      <th className="p-3">Delivered</th>
                      <th className="p-3">Mean Duration</th>
                      <th className="p-3">SLA Delay Rate</th>
                      <th className="p-3">Avg Delay (Delayed)</th>
                      <th className="p-3">Avg Order Value</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-800/80 font-mono">
                    {cityData.map(c => (
                      <tr key={c.city} className="hover:bg-slate-900/50">
                        <td className="p-3 font-sans font-bold text-white">{c.city}</td>
                        <td className="p-3">{c.order_count.toLocaleString()}</td>
                        <td className="p-3 text-slate-400">{c.delivered_orders.toLocaleString()}</td>
                        <td className="p-3 font-semibold text-sky-400">{c.average_delivery_duration.toFixed(2)} min</td>
                        <td className="p-3 font-bold text-amber-400">{c.delay_rate.toFixed(2)}%</td>
                        <td className="p-3 text-rose-400">+{c.average_delay.toFixed(2)} min</td>
                        <td className="p-3 text-emerald-400">EGP {c.average_order_value.toFixed(2)}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </section>

            {/* SECTION 5 & 6: TRAFFIC AND VEHICLE ANALYSIS */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {/* Traffic Analysis */}
              <section className="glass-card p-6 space-y-4">
                <div className="border-b border-slate-800 pb-3">
                  <h3 className="text-base font-bold text-white font-heading flex items-center gap-2">
                    <span className="text-sky-400 font-mono text-xs">05.</span> Traffic Congestion Analysis
                  </h3>
                  <p className="text-xs text-slate-400">Observed impact of road traffic density on delivery duration</p>
                </div>

                <div className="overflow-x-auto border border-slate-800 rounded-lg">
                  <table className="w-full text-xs text-left text-slate-300 font-mono">
                    <thead className="bg-slate-900 text-slate-400 uppercase border-b border-slate-800">
                      <tr>
                        <th className="p-2.5 font-sans">Traffic Level</th>
                        <th className="p-2.5">Orders</th>
                        <th className="p-2.5">Delay Rate</th>
                        <th className="p-2.5">Avg Duration</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-slate-800/80">
                      {trafficData.map(tr => (
                        <tr key={tr.traffic_level} className="hover:bg-slate-900/50">
                          <td className="p-2.5 font-sans font-medium text-white">{tr.traffic_level} Traffic</td>
                          <td className="p-2.5">{tr.order_count.toLocaleString()}</td>
                          <td className="p-2.5 font-bold text-amber-400">{tr.delay_rate.toFixed(2)}%</td>
                          <td className="p-2.5 text-sky-400">{tr.average_delivery_duration.toFixed(2)} min</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </section>

              {/* Vehicle Fleet Analysis */}
              <section className="glass-card p-6 space-y-4">
                <div className="border-b border-slate-800 pb-3">
                  <h3 className="text-base font-bold text-white font-heading flex items-center gap-2">
                    <span className="text-sky-400 font-mono text-xs">06.</span> Vehicle Fleet Analysis
                  </h3>
                  <p className="text-xs text-slate-400">Fulfillment speed and delay rate by courier vehicle type</p>
                </div>

                <div className="overflow-x-auto border border-slate-800 rounded-lg">
                  <table className="w-full text-xs text-left text-slate-300 font-mono">
                    <thead className="bg-slate-900 text-slate-400 uppercase border-b border-slate-800">
                      <tr>
                        <th className="p-2.5 font-sans">Vehicle Category</th>
                        <th className="p-2.5">Orders</th>
                        <th className="p-2.5">Delay Rate</th>
                        <th className="p-2.5">Avg Duration</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-slate-800/80">
                      {vehicleData.map(v => (
                        <tr key={v.vehicle} className="hover:bg-slate-900/50">
                          <td className="p-2.5 font-sans font-medium text-white">{v.vehicle}</td>
                          <td className="p-2.5">{v.order_count.toLocaleString()}</td>
                          <td className="p-2.5 font-bold text-amber-400">{v.delay_rate.toFixed(2)}%</td>
                          <td className="p-2.5 text-sky-400">{v.average_duration.toFixed(2)} min</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </section>
            </div>

            {/* SECTION 7: ORDER CHARACTERISTICS & CORRELATIONS */}
            <section className="glass-card p-6 space-y-4">
              <div className="border-b border-slate-800 pb-3">
                <h3 className="text-lg font-bold text-white font-heading flex items-center gap-2">
                  <span className="text-sky-400 font-mono text-sm">07.</span> Order Basket & Pearson Correlations
                </h3>
                <p className="text-xs text-slate-400">Item quantity, price tiers, and linear correlation metrics</p>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {/* Quantity Table */}
                <div className="border border-slate-800 rounded-lg p-3 space-y-2">
                  <h4 className="text-xs font-semibold text-slate-300">Basket Item Quantity Dynamics</h4>
                  <table className="w-full text-xs text-left text-slate-300 font-mono">
                    <thead className="bg-slate-900 text-slate-400 uppercase border-b border-slate-800">
                      <tr>
                        <th className="p-2">Item Count</th>
                        <th className="p-2">Orders</th>
                        <th className="p-2">Delay Rate</th>
                        <th className="p-2">Avg Duration</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-slate-800/80">
                      {quantityData.map(q => (
                        <tr key={q.quantity}>
                          <td className="p-2 font-sans text-white">{q.quantity} Item(s)</td>
                          <td className="p-2">{q.order_count.toLocaleString()}</td>
                          <td className="p-2 font-bold text-amber-400">{q.delay_rate.toFixed(2)}%</td>
                          <td className="p-2">{q.average_duration.toFixed(1)}m</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>

                {/* Distance Correlations */}
                <div className="border border-slate-800 rounded-lg p-4 space-y-3">
                  <h4 className="text-xs font-semibold text-slate-300">Linear Distance Correlations</h4>
                  {distanceData && (
                    <div className="space-y-3 font-mono text-xs">
                      <div className="p-3 bg-slate-900 rounded-lg border border-slate-800 flex items-center justify-between">
                        <span className="text-slate-400">Pearson r (Distance vs Duration):</span>
                        <span className="font-bold text-sky-400">{distanceData.correlation_distance_duration.toFixed(4)}</span>
                      </div>
                      <div className="p-3 bg-slate-900 rounded-lg border border-slate-800 flex items-center justify-between">
                        <span className="text-slate-400">Pearson r (Distance vs Delay):</span>
                        <span className="font-bold text-amber-400">{distanceData.correlation_distance_delay.toFixed(4)}</span>
                      </div>
                      <p className="text-[11px] font-sans text-slate-400 leading-relaxed pt-1">
                        <strong>Observed Pattern:</strong> Delivery distance exhibits negligible linear correlation with total delivery duration (r = {distanceData.correlation_distance_duration.toFixed(4)}) and SLA delay (r = {distanceData.correlation_distance_delay.toFixed(4)}), indicating that urban delivery timelines in this dataset are predominantly governed by non-distance operational variables.
                      </p>
                    </div>
                  )}
                </div>
              </div>
            </section>

            {/* SECTION 8: KEY DIAGNOSTIC OBSERVATIONS */}
            <section className="glass-card p-6 space-y-4">
              <div className="border-b border-slate-800 pb-3">
                <h3 className="text-lg font-bold text-white font-heading flex items-center gap-2">
                  <span className="text-sky-400 font-mono text-sm">08.</span> Structured Key Observations
                </h3>
                <p className="text-xs text-slate-400">Categorized empirical observations derived from backend API calculations</p>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {insights.map(item => (
                  <div key={item.id} className="bg-slate-900/60 border border-slate-800 p-4 rounded-xl space-y-2">
                    <div className="flex items-center justify-between gap-2">
                      <span className="text-[10px] font-bold uppercase tracking-wider text-sky-400 bg-sky-500/10 px-2 py-0.5 rounded border border-sky-500/20">
                        [Descriptive Finding] &bull; {item.category}
                      </span>
                      <span className="text-[10px] font-mono text-slate-400">N = {item.sample_size.toLocaleString()}</span>
                    </div>
                    <h4 className="text-sm font-semibold text-white">{item.title}</h4>
                    <p className="text-xs text-slate-300 leading-relaxed">{item.description}</p>
                    <div className="text-xs font-mono text-sky-400 pt-1 border-t border-slate-800/80">
                      Metric: {item.metric}
                    </div>
                  </div>
                ))}
              </div>
            </section>

            {/* SECTION 9: METHODOLOGICAL DATA LIMITATIONS */}
            <section className="glass-card p-6 space-y-4">
              <div className="border-b border-slate-800 pb-3">
                <h3 className="text-lg font-bold text-white font-heading flex items-center gap-2">
                  <span className="text-sky-400 font-mono text-sm">09.</span> Methodological Data Limitations
                </h3>
                <p className="text-xs text-slate-400">Critical constraints and caveats governing the analytical interpretation</p>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-xs">
                <div className="p-4 bg-slate-900/60 border border-slate-800 rounded-xl space-y-1.5">
                  <h4 className="font-bold text-amber-300 font-mono">1. Observational Design Constraint</h4>
                  <p className="text-slate-300 leading-relaxed">
                    The dataset is purely observational without controlled experimental manipulation. Observed statistical relationships between variables (e.g., traffic or vehicle types) describe co-occurrence patterns and do not prove direct causality.
                  </p>
                </div>

                <div className="p-4 bg-slate-900/60 border border-slate-800 rounded-xl space-y-1.5">
                  <h4 className="font-bold text-amber-300 font-mono">2. Unobserved Confounding Variables</h4>
                  <p className="text-slate-300 leading-relaxed">
                    Key operational variables such as kitchen preparation time, ambient weather conditions, exact courier GPS trajectory data, and customer door-handover waiting times are not captured in the dataset.
                  </p>
                </div>

                <div className="p-4 bg-slate-900/60 border border-slate-800 rounded-xl space-y-1.5">
                  <h4 className="font-bold text-amber-300 font-mono">3. Fulfillment Selection Bias</h4>
                  <p className="text-slate-300 leading-relaxed">
                    Cancelled orders (9.80% of total sample) do not contain completed delivery duration records. Analyzing delivery duration exclusively on completed orders introduces survival bias.
                  </p>
                </div>

                <div className="p-4 bg-slate-900/60 border border-slate-800 rounded-xl space-y-1.5">
                  <h4 className="font-bold text-amber-300 font-mono">4. Regional Geographic Scope</h4>
                  <p className="text-slate-300 leading-relaxed">
                    Data collection is restricted to 7 specific Egyptian municipalities (Cairo, Giza, Alexandria, Mansoura, Tanta, Asyut, Zagazig). Operational dynamics may reflect local city infrastructure and traffic patterns.
                  </p>
                </div>
              </div>
            </section>
          </div>
        )}
      </main>

      {/* ==================================================================== */}
      {/* 5. Dashboard Footer */}
      {/* ==================================================================== */}
      <footer className="border-t border-slate-800/80 bg-slate-900/60 py-4 text-center text-xs text-slate-500">
        FoodFlow Analytics Dashboard &bull; Connected to FastAPI Backend (<span className="font-mono text-slate-400">http://localhost:8000</span>) &bull; Phase 4 Completed
      </footer>
    </div>
  );
}
