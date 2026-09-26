import React, { useState, useEffect } from 'react';
import { Navbar } from './components/Navbar';
import { LiveMonitorView } from './views/LiveMonitorView';
import { GatewayView } from './views/GatewayView';
import { ForecastView } from './views/ForecastView';
import { AnomaliesView } from './views/AnomaliesView';
import { DailyAnalysisView } from './views/DailyAnalysisView';
import { FlexibilityView } from './views/FlexibilityView';
import { WhatIfView } from './views/WhatIfView';
import { DiscomView } from './views/DiscomView';
import { LiveTelemetry } from './types';
import { wsClient } from './services/websocket';
import { fetchLiveState } from './services/api';
import { defaultTelemetry } from './services/mockData';
import { ErrorBoundary } from './components/ErrorBoundary';

// Bulletproof merge to ensure NO property is ever undefined or null
function safeMergeTelemetry(prev: LiveTelemetry, incoming: Partial<LiveTelemetry>): LiveTelemetry {
  if (!incoming || typeof incoming !== 'object') return prev;

  const currentDemand = typeof incoming.current_demand_kw === 'number' ? incoming.current_demand_kw : (prev.current_demand_kw ?? 84.6);
  const householdDemand = typeof incoming.household_demand_kw === 'number' ? incoming.household_demand_kw : (prev.household_demand_kw ?? currentDemand);

  return {
    type: 'LIVE_TELEMETRY',
    timestamp: incoming.timestamp || prev.timestamp || new Date().toISOString(),
    current_demand_kw: currentDemand,
    household_demand_kw: householdDemand,
    expected_demand_kw: typeof incoming.expected_demand_kw === 'number' ? incoming.expected_demand_kw : (prev.expected_demand_kw ?? 74.0),
    demand_deviation_pct: typeof incoming.demand_deviation_pct === 'number' ? incoming.demand_deviation_pct : (prev.demand_deviation_pct ?? 14.3),
    solar_generation_kw: typeof incoming.solar_generation_kw === 'number' ? incoming.solar_generation_kw : (prev.solar_generation_kw ?? 48.5),
    expected_solar_kw: typeof incoming.expected_solar_kw === 'number' ? incoming.expected_solar_kw : (prev.expected_solar_kw ?? 52.0),
    battery_soc_pct: typeof incoming.battery_soc_pct === 'number' ? incoming.battery_soc_pct : (prev.battery_soc_pct ?? 74.0),
    battery_power_kw: typeof incoming.battery_power_kw === 'number' ? incoming.battery_power_kw : (prev.battery_power_kw ?? 12.0),
    ev_charging_kw: typeof incoming.ev_charging_kw === 'number' ? incoming.ev_charging_kw : (prev.ev_charging_kw ?? 16.4),
    ev_active_count: typeof incoming.ev_active_count === 'number' ? incoming.ev_active_count : (prev.ev_active_count ?? 6),
    net_grid_import_kw: typeof incoming.net_grid_import_kw === 'number' ? incoming.net_grid_import_kw : (prev.net_grid_import_kw ?? 24.1),
    voltage_v: typeof incoming.voltage_v === 'number' ? incoming.voltage_v : (prev.voltage_v ?? 416.0),
    current_a: typeof incoming.current_a === 'number' ? incoming.current_a : (prev.current_a ?? 122.5),
    power_factor: typeof incoming.power_factor === 'number' ? incoming.power_factor : (prev.power_factor ?? 0.96),
    ambient_temperature_c: typeof incoming.ambient_temperature_c === 'number' ? incoming.ambient_temperature_c : (prev.ambient_temperature_c ?? 32.4),
    cloud_cover_pct: typeof incoming.cloud_cover_pct === 'number' ? incoming.cloud_cover_pct : (prev.cloud_cover_pct ?? 18.0),
    solar_radiation_w_m2: typeof incoming.solar_radiation_w_m2 === 'number' ? incoming.solar_radiation_w_m2 : (prev.solar_radiation_w_m2 ?? 680.0),
    reliability_risk_level: incoming.reliability_risk_level || prev.reliability_risk_level || 'LOW',
    reliability_risk_reason: incoming.reliability_risk_reason || prev.reliability_risk_reason || 'Feeder operating normally',
    feeder_loading_pct: typeof incoming.feeder_loading_pct === 'number' ? incoming.feeder_loading_pct : (prev.feeder_loading_pct ?? 67.2),
    active_scenario: incoming.active_scenario || prev.active_scenario || 'NORMAL',
    active_anomalies: (incoming.active_anomalies && Array.isArray(incoming.active_anomalies))
      ? incoming.active_anomalies
      : (prev.active_anomalies || [])
  };
}

export const App: React.FC = () => {
  const [activeTab, setActiveTab] = useState<string>('live');
  const [systemMode, setSystemMode] = useState<string>('DIGITAL_TWIN');
  const [telemetry, setTelemetry] = useState<LiveTelemetry>(defaultTelemetry);
  const [isConnected, setIsConnected] = useState<boolean>(false);

  useEffect(() => {
    // 1. Initial REST fetch
    fetchLiveState()
      .then((data) => {
        if (data) {
          setTelemetry((prev) => safeMergeTelemetry(prev, data));
          setIsConnected(true);
        }
      })
      .catch((err) => {
        console.log('[NeighbourFlex] Resilient startup using default baseline telemetry.', err);
      });

    // 2. Connect WebSocket stream
    wsClient.connect();
    const unsubscribe = wsClient.subscribe((data) => {
      if (data) {
        setTelemetry((prev) => safeMergeTelemetry(prev, data));
        setIsConnected(true);
      }
    });

    // 3. Resilient fallback polling every 2.5s if WS is reconnecting
    const pollInterval = setInterval(() => {
      if (!wsClient.isConnected()) {
        fetchLiveState()
          .then((data) => {
            if (data) {
              setTelemetry((prev) => safeMergeTelemetry(prev, data));
              setIsConnected(true);
            }
          })
          .catch(() => setIsConnected(false));
      }
    }, 2500);

    return () => {
      unsubscribe();
      clearInterval(pollInterval);
    };
  }, []);

  const anomalyCount = telemetry?.active_anomalies?.length || 0;

  return (
    <div className="min-h-screen bg-slate-50 text-slate-900 flex flex-col selection:bg-emerald-600 selection:text-white">
      <Navbar
        activeTab={activeTab}
        setActiveTab={setActiveTab}
        systemMode={systemMode}
        setSystemMode={setSystemMode}
        isConnected={isConnected}
        anomalyCount={anomalyCount}
      />

      <main className="flex-1 mx-auto w-full max-w-7xl px-4 py-6 sm:px-6">
        <ErrorBoundary compact>
          {activeTab === 'live' && <LiveMonitorView telemetry={telemetry} />}
          {activeTab === 'gateway' && <GatewayView />}
          {activeTab === 'forecast' && <ForecastView />}
          {activeTab === 'anomalies' && <AnomaliesView />}
          {activeTab === 'daily' && <DailyAnalysisView />}
          {activeTab === 'flexibility' && <FlexibilityView />}
          {activeTab === 'whatif' && <WhatIfView />}
          {activeTab === 'discom' && <DiscomView />}
        </ErrorBoundary>
      </main>

      <footer className="border-t border-slate-200 bg-white py-4 text-center text-xs text-slate-500">
        <div className="mx-auto max-w-7xl px-4 flex flex-col sm:flex-row items-center justify-between gap-2">
          <div>
            <strong className="text-slate-800">NeighbourFlex</strong> • Real-Time AI Neighbourhood Energy Intelligence & Flexibility Platform
          </div>
          <div className="font-mono text-[11px] text-slate-500">
            Schneider Electric Innovation Challenge • Problem Statement 3
          </div>
        </div>
      </footer>
    </div>
  );
};

export default App;
