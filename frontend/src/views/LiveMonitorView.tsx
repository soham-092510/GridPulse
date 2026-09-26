import React, { useState, useEffect } from 'react';
import { 
  Zap, 
  Sun, 
  Battery, 
  Car, 
  UtilityPole, 
  Thermometer, 
  ShieldAlert, 
  AlertTriangle,
  PlayCircle,
  RotateCcw
} from 'lucide-react';
import { ResponsiveContainer, AreaChart, Area, XAxis, YAxis, Tooltip, CartesianGrid, Legend } from 'recharts';
import { MetricCard } from '../components/MetricCard';
import { EnergyFlow } from '../components/EnergyFlow';
import { LiveTelemetry } from '../types';
import { injectDemoAnomaly } from '../services/api';
import { defaultTelemetry } from '../services/mockData';

interface LiveMonitorViewProps {
  telemetry: LiveTelemetry | null;
}

export const LiveMonitorView: React.FC<LiveMonitorViewProps> = ({ telemetry: incomingTelemetry }) => {
  const telemetry = incomingTelemetry || defaultTelemetry;
  const [historyPoints, setHistoryPoints] = useState<any[]>([]);
  const [injecting, setInjecting] = useState<string | null>(null);

  // Safe guarded values to prevent any runtime toFixed / undefined crashes
  const currentDemand = telemetry.current_demand_kw ?? 84.6;
  const householdDemand = telemetry.household_demand_kw ?? currentDemand;
  const expectedDemand = telemetry.expected_demand_kw ?? 74.0;
  const demandDeviation = telemetry.demand_deviation_pct ?? 0.0;
  const solarGen = telemetry.solar_generation_kw ?? 0.0;
  const expectedSolar = telemetry.expected_solar_kw ?? 0.0;
  const batterySoc = telemetry.battery_soc_pct ?? 74.0;
  const batteryPower = telemetry.battery_power_kw ?? 0.0;
  const evCharging = telemetry.ev_charging_kw ?? 0.0;
  const evCount = telemetry.ev_active_count ?? 0;
  const netGrid = telemetry.net_grid_import_kw ?? 0.0;
  const feederLoading = telemetry.feeder_loading_pct ?? 65.0;
  const voltage = telemetry.voltage_v ?? 415.0;
  const current = telemetry.current_a ?? 120.0;
  const powerFactor = telemetry.power_factor ?? 0.95;
  const tempC = telemetry.ambient_temperature_c ?? 30.0;
  const cloudPct = telemetry.cloud_cover_pct ?? 20.0;
  const solarRad = telemetry.solar_radiation_w_m2 ?? 600.0;
  const riskLevel = telemetry.reliability_risk_level || 'LOW';
  const riskReason = telemetry.reliability_risk_reason || 'Feeder operating normally';
  const firstAnomaly = (telemetry.active_anomalies && Array.isArray(telemetry.active_anomalies) && telemetry.active_anomalies.length > 0)
    ? telemetry.active_anomalies[0]
    : null;

  // Maintain rolling 25-point live chart in browser memory
  useEffect(() => {
    const timeLabel = new Date(telemetry.timestamp || Date.now()).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' });
    setHistoryPoints((prev) => {
      const next = [
        ...prev,
        {
          time: timeLabel,
          demand_kw: currentDemand,
          baseline_kw: expectedDemand,
          solar_kw: solarGen,
          grid_import_kw: netGrid,
        }
      ];
      return next.slice(-25); // keep last 25 ticks
    });
  }, [telemetry.timestamp, currentDemand, expectedDemand, solarGen, netGrid]);

  const handleInject = async (scenario: string) => {
    setInjecting(scenario);
    try {
      await injectDemoAnomaly(scenario);
    } catch (e) {
      console.error(e);
    } finally {
      setTimeout(() => setInjecting(null), 1500);
    }
  };

  const riskBadgeVariants: Record<string, 'green' | 'amber' | 'red'> = {
    LOW: 'green',
    MEDIUM: 'amber',
    HIGH: 'red',
    CRITICAL: 'red'
  };

  return (
    <div className="space-y-6">
      {/* Active Anomaly Banner if detected */}
      {firstAnomaly && (
        <div className="flex items-center justify-between rounded-xl border border-red-200 bg-red-50 p-4 shadow-xs">
          <div className="flex items-center space-x-3">
            <div className="rounded-lg bg-red-100 p-2 text-red-600 animate-pulse">
              <AlertTriangle className="h-5 w-5" />
            </div>
            <div>
              <div className="flex items-center space-x-2">
                <span className="text-xs font-bold text-red-800 uppercase tracking-wider">
                  Active Energy Anomaly: {(firstAnomaly.anomaly_type || 'ANOMALY').replace(/_/g, ' ')}
                </span>
                <span className="rounded bg-red-200/80 px-1.5 py-0.5 text-[10px] font-bold text-red-900">
                  {firstAnomaly.severity || 'ALERT'}
                </span>
              </div>
              <p className="text-xs text-red-700 mt-0.5 font-medium">{firstAnomaly.root_cause || 'Investigating physical root cause'}</p>
            </div>
          </div>
          <button
            onClick={() => handleInject('NORMAL')}
            className="rounded-lg border border-red-200 bg-white px-3 py-1.5 text-xs font-semibold text-red-700 hover:bg-red-100 transition shadow-xs"
          >
            Clear / Normal
          </button>
        </div>
      )}

      {/* KPI Cards Grid */}
      <div className="grid grid-cols-2 gap-3 sm:grid-cols-3 lg:grid-cols-6">
        <MetricCard
          title="Current Demand"
          value={currentDemand.toFixed(1)}
          unit="kW"
          icon={Zap}
          iconColor="text-emerald-600"
          delta={{
            value: demandDeviation.toFixed(1),
            isPositiveGood: false,
            label: 'vs baseline'
          }}
        />
        <MetricCard
          title="Rooftop Solar"
          value={solarGen.toFixed(1)}
          unit="kW"
          icon={Sun}
          iconColor="text-amber-500"
          subtitle={`Expected ${expectedSolar.toFixed(1)} kW`}
        />
        <MetricCard
          title="Community Battery"
          value={batterySoc.toFixed(0)}
          unit="%"
          icon={Battery}
          iconColor="text-purple-600"
          subtitle={
            batteryPower > 0
              ? `Discharging ${batteryPower.toFixed(1)} kW`
              : batteryPower < 0
              ? `Charging ${Math.abs(batteryPower).toFixed(1)} kW`
              : 'Standby / Idle'
          }
        />
        <MetricCard
          title="EV Fleet Charging"
          value={evCharging.toFixed(1)}
          unit="kW"
          icon={Car}
          iconColor="text-sky-600"
          subtitle={`${evCount} active sessions`}
        />
        <MetricCard
          title="Net Grid Import"
          value={netGrid.toFixed(1)}
          unit="kW"
          icon={UtilityPole}
          iconColor="text-slate-700"
          subtitle={`Transformer ${feederLoading.toFixed(1)}%`}
        />
        <MetricCard
          title="Reliability Risk"
          value={riskLevel}
          icon={ShieldAlert}
          iconColor={
            riskLevel === 'LOW'
              ? 'text-emerald-600'
              : riskLevel === 'MEDIUM'
              ? 'text-amber-500'
              : 'text-red-600'
          }
          badge={{
            text: riskLevel,
            variant: riskBadgeVariants[riskLevel] || 'green'
          }}
          subtitle={riskReason.length > 32 ? riskReason.slice(0, 32) + '...' : riskReason}
        />
      </div>

      {/* Dynamic Energy Flow Diagram */}
      <EnergyFlow
        solarKw={solarGen}
        gridKw={netGrid}
        batteryKw={batteryPower}
        batterySoc={batterySoc}
        evKw={evCharging}
        demandKw={householdDemand}
      />

      {/* Real-Time Live Power Curves & Demo Controls */}
      <div className="grid grid-cols-1 gap-6 lg:grid-cols-4">
        <div className="glass-card rounded-2xl p-5 lg:col-span-3">
          <div className="flex items-center justify-between border-b border-slate-200 pb-3">
            <div>
              <h3 className="text-sm font-bold text-slate-900">Live Telemetry Power Curves</h3>
              <p className="text-[11px] text-slate-500">Streamed at 1-2 second resolution with historical baseline comparison</p>
            </div>
            <div className="flex items-center space-x-3 text-xs font-mono">
              <span className="text-slate-500">V: <strong className="text-slate-800">{voltage.toFixed(0)}V</strong></span>
              <span className="text-slate-500">I: <strong className="text-slate-800">{current.toFixed(0)}A</strong></span>
              <span className="text-slate-500">PF: <strong className="text-slate-800">{powerFactor.toFixed(2)}</strong></span>
            </div>
          </div>

          <div className="mt-4 h-64 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={historyPoints}>
                <defs>
                  <linearGradient id="colorDemand" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#059669" stopOpacity={0.2}/>
                    <stop offset="95%" stopColor="#059669" stopOpacity={0}/>
                  </linearGradient>
                  <linearGradient id="colorSolar" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#D97706" stopOpacity={0.2}/>
                    <stop offset="95%" stopColor="#D97706" stopOpacity={0}/>
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="#F1F5F9" />
                <XAxis dataKey="time" stroke="#94A3B8" tick={{ fontSize: 10 }} />
                <YAxis stroke="#94A3B8" tick={{ fontSize: 10 }} unit=" kW" domain={[0, 'auto']} />
                <Tooltip
                  contentStyle={{ backgroundColor: '#FFFFFF', borderColor: '#E2E8F0', borderRadius: '8px', boxShadow: '0 4px 6px -1px rgba(0,0,0,0.1)' }}
                  labelStyle={{ color: '#64748B', fontSize: '11px', fontWeight: 'bold' }}
                  itemStyle={{ fontSize: '12px' }}
                />
                <Legend wrapperStyle={{ fontSize: '11px', paddingTop: '10px' }} />
                <Area type="monotone" dataKey="demand_kw" name="Actual Demand (kW)" stroke="#059669" strokeWidth={2} fill="url(#colorDemand)" />
                <Area type="monotone" dataKey="baseline_kw" name="Expected Baseline (kW)" stroke="#94A3B8" strokeDasharray="4 4" strokeWidth={1.5} fill="none" />
                <Area type="monotone" dataKey="solar_kw" name="Solar (kW)" stroke="#D97706" strokeWidth={2} fill="url(#colorSolar)" />
                <Area type="monotone" dataKey="grid_import_kw" name="Grid Import (kW)" stroke="#0284C7" strokeWidth={1.5} fill="none" />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Hackathon Demonstration Controls */}
        <div className="glass-card rounded-2xl p-5 flex flex-col justify-between">
          <div>
            <div className="flex items-center space-x-2 border-b border-slate-200 pb-3">
              <PlayCircle className="h-4 w-4 text-emerald-600" />
              <h3 className="text-sm font-bold text-slate-900">Scenario Lab</h3>
            </div>
            <p className="mt-2 text-xs text-slate-500 leading-relaxed">
              Inject real-world operational stressors to test instantaneous anomaly detection, root-cause attribution, and optimizer flexibility dispatch:
            </p>

            <div className="mt-4 space-y-2.5">
              <button
                onClick={() => handleInject('SPIKE')}
                disabled={injecting !== null}
                className="w-full flex items-center justify-between rounded-xl border border-red-200 bg-red-50 px-3.5 py-2.5 text-xs font-semibold text-red-800 hover:bg-red-100 transition disabled:opacity-50 shadow-xs"
              >
                <span>🔥 +35 kW Evening Heat Spike</span>
                <span className="text-[10px] rounded bg-red-200 px-1.5 py-0.5 text-red-900 font-bold">AC + EV Cluster</span>
              </button>

              <button
                onClick={() => handleInject('SOLAR_DROP')}
                disabled={injecting !== null}
                className="w-full flex items-center justify-between rounded-xl border border-amber-200 bg-amber-50 px-3.5 py-2.5 text-xs font-semibold text-amber-800 hover:bg-amber-100 transition disabled:opacity-50 shadow-xs"
              >
                <span>☁️ Sudden Solar Drop (-65%)</span>
                <span className="text-[10px] rounded bg-amber-200 px-1.5 py-0.5 text-amber-900 font-bold">Cloud Occlusion</span>
              </button>

              <button
                onClick={() => handleInject('NORMAL')}
                disabled={injecting !== null}
                className="w-full flex items-center justify-center space-x-1.5 rounded-xl border border-slate-200 bg-slate-50 px-3.5 py-2 text-xs font-semibold text-slate-700 hover:bg-slate-100 transition disabled:opacity-50 shadow-xs"
              >
                <RotateCcw className="h-3.5 w-3.5" />
                <span>Reset to Baseline Normal</span>
              </button>
            </div>
          </div>

          <div className="mt-4 rounded-xl border border-slate-200 bg-slate-50 p-3 text-[11px] text-slate-600">
            <div className="flex items-center justify-between font-mono">
              <span>Weather:</span>
              <span className="text-slate-900 font-medium">{tempC.toFixed(1)}°C | {cloudPct.toFixed(0)}% Cloud</span>
            </div>
            <div className="flex items-center justify-between font-mono mt-1">
              <span>Solar Rad:</span>
              <span className="text-slate-900 font-medium">{solarRad.toFixed(0)} W/m²</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
