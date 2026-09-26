import { 
  LiveTelemetry, 
  MultiHorizonForecast, 
  DailySummary, 
  FeederInfo, 
  OptimizationAction, 
  Device 
} from '../types';

export const defaultTelemetry: LiveTelemetry = {
  type: 'LIVE_TELEMETRY',
  timestamp: new Date().toISOString(),
  current_demand_kw: 84.6,
  household_demand_kw: 68.2,
  expected_demand_kw: 74.0,
  demand_deviation_pct: 14.3,
  solar_generation_kw: 48.5,
  expected_solar_kw: 52.0,
  battery_soc_pct: 74.0,
  battery_power_kw: 12.0, // (+) Discharging
  ev_charging_kw: 16.4,
  ev_active_count: 6,
  net_grid_import_kw: 24.1,
  voltage_v: 416.0,
  current_a: 122.5,
  power_factor: 0.96,
  ambient_temperature_c: 32.4,
  cloud_cover_pct: 18.0,
  solar_radiation_w_m2: 680.0,
  reliability_risk_level: 'LOW',
  reliability_risk_reason: 'Feeder load stable within safe thermal bounds. Headroom: 40.4 kW available.',
  feeder_loading_pct: 67.2,
  active_scenario: 'NORMAL',
  active_anomalies: [
    {
      event_id: 'EVT-1042',
      timestamp: new Date().toISOString(),
      device_id: 'COMMUNITY_FEEDER_01',
      anomaly_type: 'demand_spike',
      expected_value: 74.0,
      actual_value: 84.6,
      deviation_pct: 14.3,
      severity: 'MEDIUM',
      root_cause: 'Elevated ambient temperature (32.4°C) driving domestic air-conditioning cooling load coupled with 6 active EV sessions.',
      status: 'ACTIVE'
    }
  ]
};

export const defaultDevices: Device[] = [
  {
    device_id: 'SMART_METER_MAIN',
    name: 'Neighbourhood Main Substation Feeder Meter',
    device_type: 'smart_meter',
    manufacturer: 'Schneider Electric',
    model: 'PowerLogic PM8000',
    location: 'Distribution Transformer DT-04, Sector 7',
    protocol: 'mqtt',
    status: 'online',
    health_score: 1.0,
    packets_received: 45120,
    packets_rejected: 4,
    last_seen: new Date().toISOString()
  },
  {
    device_id: 'ROOFTOP_SOLAR_ARRAY',
    name: 'Community Rooftop Solar PV Aggregator',
    device_type: 'solar_inverter',
    manufacturer: 'Schneider Electric',
    model: 'Conext CL 60',
    location: 'Rooftop Cluster (40 homes)',
    protocol: 'modbus',
    status: 'online',
    health_score: 0.98,
    packets_received: 44980,
    packets_rejected: 12,
    last_seen: new Date().toISOString()
  },
  {
    device_id: 'COMMUNITY_BATTERY_01',
    name: 'Community Energy Storage System (BESS)',
    device_type: 'battery_bms',
    manufacturer: 'Schneider Electric',
    model: 'EcoStruxure 100kWh',
    location: 'Substation Enclosure A',
    protocol: 'can_gateway',
    status: 'online',
    health_score: 1.0,
    packets_received: 45050,
    packets_rejected: 2,
    last_seen: new Date().toISOString()
  },
  {
    device_id: 'EV_CHARGER_CLUSTER',
    name: 'Smart EV Charging Fleet Gateway (20 Bays)',
    device_type: 'ev_charger',
    manufacturer: 'Schneider Electric',
    model: 'EVlink Pro AC 22kW',
    location: 'Community Parking Lot & Garages',
    protocol: 'ocpp',
    status: 'online',
    health_score: 0.99,
    packets_received: 44800,
    packets_rejected: 6,
    last_seen: new Date().toISOString()
  },
  {
    device_id: 'WEATHER_STATION_01',
    name: 'Microclimate & Solar Irradiance Station',
    device_type: 'weather_station',
    manufacturer: 'Open-Meteo Integration',
    model: 'SLDC Micro-Station API',
    location: 'Neighbourhood Mast',
    protocol: 'rest',
    status: 'online',
    health_score: 1.0,
    packets_received: 2880,
    packets_rejected: 0,
    last_seen: new Date().toISOString()
  }
];

export const defaultForecasts: MultiHorizonForecast = {
  timestamp: new Date().toISOString(),
  horizon_15m: [
    { target_time: '+3m', predicted_demand_kw: 85.1, baseline_demand_kw: 74.2, predicted_solar_kw: 48.0, predicted_net_load_kw: 37.1, lower_bound_kw: 78.5, upper_bound_kw: 91.7 },
    { target_time: '+6m', predicted_demand_kw: 85.8, baseline_demand_kw: 74.8, predicted_solar_kw: 47.4, predicted_net_load_kw: 38.4, lower_bound_kw: 78.2, upper_bound_kw: 93.4 },
    { target_time: '+9m', predicted_demand_kw: 86.4, baseline_demand_kw: 75.3, predicted_solar_kw: 46.8, predicted_net_load_kw: 39.6, lower_bound_kw: 78.0, upper_bound_kw: 94.8 },
    { target_time: '+12m', predicted_demand_kw: 87.2, baseline_demand_kw: 75.9, predicted_solar_kw: 46.0, predicted_net_load_kw: 41.2, lower_bound_kw: 77.8, upper_bound_kw: 96.6 },
    { target_time: '+15m', predicted_demand_kw: 88.0, baseline_demand_kw: 76.5, predicted_solar_kw: 45.2, predicted_net_load_kw: 42.8, lower_bound_kw: 77.5, upper_bound_kw: 98.5 }
  ],
  horizon_1h: [
    { target_time: '+15m', predicted_demand_kw: 88.0, baseline_demand_kw: 76.5, predicted_solar_kw: 45.2, predicted_net_load_kw: 42.8, lower_bound_kw: 77.5, upper_bound_kw: 98.5 },
    { target_time: '+30m', predicted_demand_kw: 91.5, baseline_demand_kw: 78.2, predicted_solar_kw: 38.0, predicted_net_load_kw: 53.5, lower_bound_kw: 79.2, upper_bound_kw: 103.8 },
    { target_time: '+45m', predicted_demand_kw: 95.2, baseline_demand_kw: 80.5, predicted_solar_kw: 24.0, predicted_net_load_kw: 71.2, lower_bound_kw: 81.4, upper_bound_kw: 109.0 },
    { target_time: '+60m', predicted_demand_kw: 98.8, baseline_demand_kw: 82.0, predicted_solar_kw: 10.0, predicted_net_load_kw: 88.8, lower_bound_kw: 83.5, upper_bound_kw: 114.1 }
  ],
  horizon_6h: [
    { target_time: '+1h', predicted_demand_kw: 98.8, baseline_demand_kw: 82.0, predicted_solar_kw: 10.0, predicted_net_load_kw: 88.8, lower_bound_kw: 83.5, upper_bound_kw: 114.1 },
    { target_time: '+2h', predicted_demand_kw: 104.2, baseline_demand_kw: 84.5, predicted_solar_kw: 0.0, predicted_net_load_kw: 104.2, lower_bound_kw: 87.0, upper_bound_kw: 121.4 },
    { target_time: '+3h', predicted_demand_kw: 96.0, baseline_demand_kw: 78.0, predicted_solar_kw: 0.0, predicted_net_load_kw: 96.0, lower_bound_kw: 80.2, upper_bound_kw: 111.8 },
    { target_time: '+4h', predicted_demand_kw: 82.5, baseline_demand_kw: 68.0, predicted_solar_kw: 0.0, predicted_net_load_kw: 82.5, lower_bound_kw: 69.0, upper_bound_kw: 96.0 },
    { target_time: '+5h', predicted_demand_kw: 64.0, baseline_demand_kw: 54.0, predicted_solar_kw: 0.0, predicted_net_load_kw: 64.0, lower_bound_kw: 52.0, upper_bound_kw: 76.0 },
    { target_time: '+6h', predicted_demand_kw: 48.0, baseline_demand_kw: 42.0, predicted_solar_kw: 0.0, predicted_net_load_kw: 48.0, lower_bound_kw: 38.0, upper_bound_kw: 58.0 }
  ],
  horizon_24h: Array.from({ length: 24 }, (_, i) => ({
    target_time: `${i}:00`,
    predicted_demand_kw: Math.round(45 + 35 * Math.sin((i - 6) / 12 * Math.PI) + (18 <= i && i <= 21 ? 25 : 0)),
    baseline_demand_kw: Math.round(40 + 30 * Math.sin((i - 6) / 12 * Math.PI) + (18 <= i && i <= 21 ? 20 : 0)),
    predicted_solar_kw: (7 <= i && i <= 17) ? Math.round(75 * Math.sin((i - 7) / 10 * Math.PI)) : 0,
    predicted_net_load_kw: Math.max(0, Math.round(45 + 35 * Math.sin((i - 6) / 12 * Math.PI) - ((7 <= i && i <= 17) ? 75 * Math.sin((i - 7) / 10 * Math.PI) : 0))),
    lower_bound_kw: Math.max(20, Math.round(35 + 25 * Math.sin((i - 6) / 12 * Math.PI))),
    upper_bound_kw: Math.round(55 + 45 * Math.sin((i - 6) / 12 * Math.PI) + 15)
  })),
  accuracy_metrics: [
    { horizon: '15m', mae_kw: 2.4, rmse_kw: 3.6, mape_pct: 3.8, confidence_score_pct: 96.2 },
    { horizon: '1h', mae_kw: 4.1, rmse_kw: 5.8, mape_pct: 5.4, confidence_score_pct: 94.6 },
    { horizon: '6h', mae_kw: 6.3, rmse_kw: 8.7, mape_pct: 7.9, confidence_score_pct: 92.1 },
    { horizon: '24h', mae_kw: 8.9, rmse_kw: 11.5, mape_pct: 9.8, confidence_score_pct: 90.2 }
  ]
};

export const defaultActions: OptimizationAction[] = [
  {
    action_id: 'ACT-BATT-7B2F',
    timestamp: new Date().toISOString(),
    target_asset: 'COMMUNITY_BATTERY_01',
    action_type: 'BATTERY_DISCHARGE',
    command_payload: { discharge_rate_kw: 18.0, target_soc_min: 25.0 },
    scheduled_start: new Date().toISOString(),
    scheduled_end: new Date(Date.now() + 45 * 60000).toISOString(),
    expected_peak_reduction_kw: 18.0,
    actual_peak_reduction_kw: 17.6,
    effectiveness_pct: 98.0,
    status: 'RECOMMENDED'
  },
  {
    action_id: 'ACT-EV-4A1C',
    timestamp: new Date().toISOString(),
    target_asset: 'EV_CHARGER_FLEET',
    action_type: 'SHIFT_EV_LOAD',
    command_payload: { curtail_kw: 12.5, shift_to_time: '23:30', consenting_vehicles: 5 },
    scheduled_start: new Date().toISOString(),
    scheduled_end: new Date(Date.now() + 120 * 60000).toISOString(),
    expected_peak_reduction_kw: 12.5,
    actual_peak_reduction_kw: 12.8,
    effectiveness_pct: 102.4,
    status: 'RECOMMENDED'
  },
  {
    action_id: 'ACT-PUMP-9E3D',
    timestamp: new Date(Date.now() - 3600000).toISOString(),
    target_asset: 'MUNICIPAL_WATER_PUMP_A',
    action_type: 'CURTAIL_FLEXIBLE_LOAD',
    command_payload: { curtail_kw: 8.0 },
    scheduled_start: new Date(Date.now() - 3600000).toISOString(),
    scheduled_end: new Date().toISOString(),
    expected_peak_reduction_kw: 8.0,
    actual_peak_reduction_kw: 8.0,
    effectiveness_pct: 100.0,
    status: 'APPROVED'
  }
];

export const defaultDailySummary: DailySummary = {
  date_str: '2026-09-21',
  total_consumption_kwh: 1842.0,
  peak_demand_kw: 104.5,
  peak_time: '18:42',
  min_demand_kw: 28.4,
  avg_demand_kw: 76.8,
  solar_generation_kwh: 612.0,
  grid_import_kwh: 1230.0,
  battery_throughput_kwh: 54.2,
  anomaly_count: 2,
  opt_actions_count: 3,
  peak_reduction_achieved_kw: 18.4,
  comparison_vs_7d_pct: 11.2,
  comparison_vs_30d_pct: 13.4,
  comparison_vs_same_weekday_pct: 14.8,
  explanation: "Today's consumption is 14.8% above the normal Monday profile. The largest deviation occurred between 6:15 PM and 7:10 PM (+28 kW). Ambient temperature was 3.4°C above normal driving high air conditioning cooling demand, combined with simultaneous uncoordinated evening EV arrivals.",
  hourly_curve: Array.from({ length: 24 }, (_, h) => {
    const dem = Math.round(45 + 35 * Math.sin((h - 6) / 12 * Math.PI) + (18 <= h && h <= 21 ? 35 : 0));
    const sol = (7 <= h && h <= 17) ? Math.round(75 * Math.sin((h - 7) / 10 * Math.PI)) : 0;
    return {
      hour: `${String(h).padStart(2, '0')}:00`,
      demand_kw: dem,
      baseline_kw: Math.round(dem / 1.148),
      solar_kw: sol,
      grid_import_kw: Math.max(0, dem - sol)
    };
  }),
  events: [
    {
      event_id: 'EVT-1042',
      timestamp: '2026-09-21T18:42:00',
      device_id: 'COMMUNITY_FEEDER_01',
      anomaly_type: 'demand_spike',
      expected_value: 72.0,
      actual_value: 104.5,
      deviation_pct: 45.1,
      severity: 'HIGH',
      root_cause: 'Sudden 45% evening energy spike driven by temperature cooling surge (+3.4°C) and coincident EV charging.',
      status: 'RESOLVED'
    },
    {
      event_id: 'EVT-1043',
      timestamp: '2026-09-21T14:15:00',
      device_id: 'ROOFTOP_SOLAR_ARRAY',
      anomaly_type: 'solar_underperformance',
      expected_value: 68.0,
      actual_value: 42.0,
      deviation_pct: -38.2,
      severity: 'MEDIUM',
      root_cause: 'Transient cloud cover reduced rooftop PV generation by 38% for 45 minutes.',
      status: 'RESOLVED'
    }
  ]
};

export const defaultCalendarDays = Array.from({ length: 20 }, (_, i) => {
  const day = i + 1;
  const dateStr = `2026-09-${String(day).padStart(2, '0')}`;
  const isCritical = (day === 12);
  const isWarning = (day === 5 || day === 18);
  return {
    date: dateStr,
    day,
    status: isCritical ? 'CRITICAL' : isWarning ? 'WARNING' : 'NORMAL',
    peak_demand_kw: isCritical ? 118.4 : isWarning ? 108.2 : 82.5,
    total_kwh: isCritical ? 2120.0 : isWarning ? 1940.0 : 1650.0,
    anomaly_count: isCritical ? 3 : isWarning ? 1 : 0,
    has_optimization: true
  };
});

export const defaultFeeders: FeederInfo[] = [
  {
    feeder_id: 'FDR-01',
    name: 'Feeder 1 - Sector 4 Residential',
    current_load_kw: 68.4,
    capacity_kw: 120.0,
    loading_pct: 57.0,
    solar_connected_kw: 45.0,
    battery_storage_kwh: 100.0,
    flexible_capacity_kw: 24.0,
    risk_level: 'GREEN',
    status_reason: 'Optimal headroom. Solar generation offsetting 35% of local load.'
  },
  {
    feeder_id: 'FDR-02',
    name: 'Feeder 2 - Commercial High Street',
    current_load_kw: 82.1,
    capacity_kw: 130.0,
    loading_pct: 63.2,
    solar_connected_kw: 30.0,
    battery_storage_kwh: 50.0,
    flexible_capacity_kw: 18.0,
    risk_level: 'GREEN',
    status_reason: 'Stable afternoon commercial load within safe thermal envelope.'
  },
  {
    feeder_id: 'FDR-03',
    name: 'Feeder 3 - Mixed Residential & Schools',
    current_load_kw: 108.5,
    capacity_kw: 125.0,
    loading_pct: 86.8,
    solar_connected_kw: 25.0,
    battery_storage_kwh: 80.0,
    flexible_capacity_kw: 15.0,
    risk_level: 'YELLOW',
    status_reason: 'Moderate thermal stress. Evening cooking and lighting ramp detected.'
  },
  {
    feeder_id: 'FDR-04',
    name: 'Feeder 4 - Sector 7 Dense Community (Active Pilot)',
    current_load_kw: 114.2,
    capacity_kw: 125.0,
    loading_pct: 91.4,
    solar_connected_kw: 80.0,
    battery_storage_kwh: 100.0,
    flexible_capacity_kw: 32.0,
    risk_level: 'RED',
    status_reason: 'Impending transformer thermal overload: Demand +28%, Solar -18%, simultaneous EV charging cluster.'
  },
  {
    feeder_id: 'FDR-05',
    name: 'Feeder 5 - Municipal Water & Services',
    current_load_kw: 42.0,
    capacity_kw: 100.0,
    loading_pct: 42.0,
    solar_connected_kw: 15.0,
    battery_storage_kwh: 20.0,
    flexible_capacity_kw: 12.0,
    risk_level: 'GREEN',
    status_reason: 'Pumps operating on scheduled off-peak window.'
  }
];
