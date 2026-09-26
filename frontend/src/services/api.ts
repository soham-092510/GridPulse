const API_BASE = '/api';

export async function fetchLiveState() {
  const res = await fetch(`${API_BASE}/measurements/live`);
  if (!res.ok) throw new Error('Failed to fetch live state');
  return res.json();
}

export async function fetchDevices() {
  const res = await fetch(`${API_BASE}/devices`);
  if (!res.ok) throw new Error('Failed to fetch devices');
  return res.json();
}

export async function registerDevice(data: any) {
  const res = await fetch(`${API_BASE}/devices`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data)
  });
  if (!res.ok) throw new Error('Failed to register device');
  return res.json();
}

export async function fetchForecasts() {
  const res = await fetch(`${API_BASE}/forecasts/multi-horizon`);
  if (!res.ok) throw new Error('Failed to fetch forecasts');
  return res.json();
}

export async function fetchActiveAnomalies() {
  const res = await fetch(`${API_BASE}/anomalies/active`);
  if (!res.ok) throw new Error('Failed to fetch active anomalies');
  return res.json();
}

export async function fetchAnomalyHistory() {
  const res = await fetch(`${API_BASE}/anomalies/history`);
  if (!res.ok) throw new Error('Failed to fetch anomaly history');
  return res.json();
}

export async function injectDemoAnomaly(scenario: string) {
  const res = await fetch(`${API_BASE}/anomalies/inject`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ scenario, duration_ticks: 30 })
  });
  if (!res.ok) throw new Error('Failed to inject anomaly');
  return res.json();
}

export async function fetchOptimizationActions() {
  const res = await fetch(`${API_BASE}/optimization/actions`);
  if (!res.ok) throw new Error('Failed to fetch optimization actions');
  return res.json();
}

export async function approveOptimizationAction(action_id: string, approved: boolean) {
  const res = await fetch(`${API_BASE}/optimization/approve`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ action_id, approved })
  });
  if (!res.ok) throw new Error('Failed to update action');
  return res.json();
}

export async function recomputeOptimization() {
  const res = await fetch(`${API_BASE}/optimization/recompute`, {
    method: 'POST'
  });
  if (!res.ok) throw new Error('Failed to recompute schedule');
  return res.json();
}

export async function fetchMonthCalendar(month: number = 9, year: number = 2026) {
  const res = await fetch(`${API_BASE}/daily-analysis/calendar?month=${month}&year=${year}`);
  if (!res.ok) throw new Error('Failed to fetch calendar');
  return res.json();
}

export async function fetchDailyAnalysis(dateStr: string) {
  const res = await fetch(`${API_BASE}/daily-analysis/${dateStr}`);
  if (!res.ok) throw new Error('Failed to fetch daily analysis');
  return res.json();
}

export async function runWhatIfSimulation(params: {
  battery_capacity_kwh: number;
  ev_dr_participation_pct: number;
  solar_capacity_multiplier: number;
  simulated_temperature_offset_c: number;
}) {
  const res = await fetch(`${API_BASE}/what-if/simulate`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(params)
  });
  if (!res.ok) throw new Error('Failed to run simulation');
  return res.json();
}

export async function fetchFeeders() {
  const res = await fetch(`${API_BASE}/discom/feeders`);
  if (!res.ok) throw new Error('Failed to fetch feeders');
  return res.json();
}

export async function triggerDiscomDemandResponse(feeder_id: string, target_kw: number = 15.0) {
  const res = await fetch(`${API_BASE}/discom/trigger-dr`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ feeder_id, target_reduction_kw: target_kw })
  });
  if (!res.ok) throw new Error('Failed to trigger DR');
  return res.json();
}

export async function ingestTestTelemetry(payload: {
  device_id: string;
  metric: string;
  value: number;
  unit: string;
}) {
  const res = await fetch(`${API_BASE}/ingestion/telemetry`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload)
  });
  return res.json();
}
