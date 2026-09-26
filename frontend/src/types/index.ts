export interface LiveTelemetry {
  type: string;
  timestamp: string;
  current_demand_kw: number;
  household_demand_kw: number;
  expected_demand_kw: number;
  demand_deviation_pct: number;
  solar_generation_kw: number;
  expected_solar_kw: number;
  battery_soc_pct: number;
  battery_power_kw: number;
  ev_charging_kw: number;
  ev_active_count: number;
  net_grid_import_kw: number;
  voltage_v: number;
  current_a: number;
  power_factor: number;
  ambient_temperature_c: number;
  cloud_cover_pct: number;
  solar_radiation_w_m2: number;
  reliability_risk_level: 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';
  reliability_risk_reason: string;
  feeder_loading_pct: number;
  active_scenario: string;
  active_anomalies: AnomalyEvent[];
}

export interface AnomalyEvent {
  event_id: string;
  timestamp: string;
  device_id?: string;
  anomaly_type: string;
  expected_value: number;
  actual_value: number;
  deviation_pct: number;
  severity: 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';
  root_cause?: string;
  diagnostic_details?: Record<string, any>;
  status: string;
}

export interface Device {
  device_id: string;
  name: string;
  device_type: string;
  manufacturer?: string;
  model?: string;
  location?: string;
  protocol: string;
  status: string;
  health_score: number;
  packets_received: number;
  packets_rejected: number;
  last_seen?: string;
}

export interface ForecastPoint {
  target_time: string;
  predicted_demand_kw: number;
  baseline_demand_kw: number;
  predicted_solar_kw: number;
  predicted_net_load_kw: number;
  lower_bound_kw: number;
  upper_bound_kw: number;
}

export interface ForecastAccuracy {
  horizon: string;
  mae_kw: number;
  rmse_kw: number;
  mape_pct: number;
  confidence_score_pct: number;
}

export interface MultiHorizonForecast {
  timestamp: string;
  horizon_15m: ForecastPoint[];
  horizon_1h: ForecastPoint[];
  horizon_6h: ForecastPoint[];
  horizon_24h: ForecastPoint[];
  accuracy_metrics: ForecastAccuracy[];
}

export interface OptimizationAction {
  action_id: string;
  timestamp: string;
  target_asset: string;
  action_type: string;
  command_payload: Record<string, any>;
  scheduled_start: string;
  scheduled_end: string;
  expected_peak_reduction_kw: number;
  actual_peak_reduction_kw: number;
  effectiveness_pct: number;
  status: 'RECOMMENDED' | 'APPROVED' | 'REJECTED' | 'EXECUTING' | 'COMPLETED';
}

export interface DailySummary {
  date_str: string;
  total_consumption_kwh: number;
  peak_demand_kw: number;
  peak_time: string;
  min_demand_kw: number;
  avg_demand_kw: number;
  solar_generation_kwh: number;
  grid_import_kwh: number;
  battery_throughput_kwh: number;
  anomaly_count: number;
  opt_actions_count: number;
  peak_reduction_achieved_kw: number;
  comparison_vs_7d_pct: number;
  comparison_vs_30d_pct: number;
  comparison_vs_same_weekday_pct: number;
  explanation: string;
  hourly_curve: {
    hour: string;
    demand_kw: number;
    baseline_kw: number;
    solar_kw: number;
    grid_import_kw: number;
  }[];
  events: AnomalyEvent[];
}

export interface FeederInfo {
  feeder_id: string;
  name: string;
  current_load_kw: number;
  capacity_kw: number;
  loading_pct: number;
  solar_connected_kw: number;
  battery_storage_kwh: number;
  flexible_capacity_kw: number;
  risk_level: 'GREEN' | 'YELLOW' | 'RED';
  status_reason: string;
}
