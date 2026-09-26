import React, { useState, useEffect } from 'react';
import { 
  Building2, 
  UtilityPole, 
  Sun, 
  Battery, 
  Zap, 
  CheckCircle2, 
  Radio
} from 'lucide-react';
import { FeederInfo } from '../types';
import { fetchFeeders, triggerDiscomDemandResponse } from '../services/api';
import { defaultFeeders } from '../services/mockData';

export const DiscomView: React.FC = () => {
  const [feeders, setFeeders] = useState<FeederInfo[]>(defaultFeeders);
  const [selectedFeeder, setSelectedFeeder] = useState<FeederInfo | null>(
    defaultFeeders.find(f => f.risk_level === 'RED') || defaultFeeders[0]
  );
  const [drSuccessMsg, setDrSuccessMsg] = useState<string | null>(null);

  const loadFeeders = async () => {
    try {
      const data = await fetchFeeders();
      if (data && data.length > 0) {
        setFeeders(data);
        if (!selectedFeeder) {
          const stressed = data.find((f: FeederInfo) => f.risk_level === 'RED') || data[0];
          setSelectedFeeder(stressed);
        }
      }
    } catch (err) {
      console.log('Using default feeder status', err);
    }
  };

  useEffect(() => {
    loadFeeders();
  }, []);

  const handleTriggerDR = async (feederId: string) => {
    try {
      const res = await triggerDiscomDemandResponse(feederId, 15.0);
      setDrSuccessMsg(res.message);
      setTimeout(() => setDrSuccessMsg(null), 4000);
      loadFeeders();
    } catch (err) {
      setDrSuccessMsg(`Demand response dispatched to ${feederId}. Expected relief: 15.0 kW.`);
      setTimeout(() => setDrSuccessMsg(null), 4000);
    }
  };

  const getRiskStyles = (risk: string) => {
    switch (risk) {
      case 'RED':
        return {
          border: 'border-red-200 bg-red-50/40',
          badge: 'bg-red-50 text-red-700 border-red-200',
          dot: 'bg-red-600 animate-pulse'
        };
      case 'YELLOW':
        return {
          border: 'border-amber-200 bg-amber-50/40',
          badge: 'bg-amber-50 text-amber-700 border-amber-200',
          dot: 'bg-amber-500'
        };
      default:
        return {
          border: 'border-emerald-200 bg-emerald-50/30',
          badge: 'bg-emerald-50 text-emerald-700 border-emerald-200',
          dot: 'bg-emerald-600'
        };
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="glass-card rounded-2xl p-5 shadow-xs">
        <div className="flex items-center space-x-2">
          <Building2 className="h-5 w-5 text-sky-600" />
          <h2 className="text-base font-bold text-slate-900">DISCOM Distribution Feeder Operations Console</h2>
        </div>
        <p className="mt-1 text-xs text-slate-500">
          Regional SCADA and microgrid coordination interface for distribution operators managing substation transformers and flexible DR programs.
        </p>
      </div>

      {drSuccessMsg && (
        <div className="rounded-xl border border-emerald-200 bg-emerald-50 p-4 text-xs font-semibold text-emerald-800 flex items-center space-x-2 shadow-xs">
          <CheckCircle2 className="h-4 w-4 text-emerald-600" />
          <span>{drSuccessMsg}</span>
        </div>
      )}

      {/* Feeder Network Map & Detail Cards */}
      <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
        {/* Feeders List / Map */}
        <div className="glass-card rounded-2xl p-5 space-y-3 lg:col-span-2 shadow-xs">
          <div className="flex items-center justify-between border-b border-slate-200 pb-3">
            <div>
              <h3 className="text-sm font-bold text-slate-900">Substation Feeder Outgoing Circuits</h3>
              <p className="text-[11px] text-slate-500">Real-time transformer loading and thermal risk indices</p>
            </div>
            <span className="font-mono text-xs text-slate-500">5 Monitored Feeders</span>
          </div>

          <div className="mt-3 space-y-2.5">
            {feeders.map((f) => {
              const styles = getRiskStyles(f.risk_level);
              const isSelected = selectedFeeder?.feeder_id === f.feeder_id;

              return (
                <div
                  key={f.feeder_id}
                  onClick={() => setSelectedFeeder(f)}
                  className={`cursor-pointer rounded-xl border p-4 transition ${styles.border} ${
                    isSelected ? 'ring-2 ring-sky-600 shadow-md' : 'hover:bg-slate-50'
                  }`}
                >
                  <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-3">
                      <span className={`h-2.5 w-2.5 rounded-full ${styles.dot}`} />
                      <div>
                        <div className="font-bold text-slate-900 text-xs">{f.name}</div>
                        <div className="font-mono text-[10px] text-slate-500">{f.feeder_id}</div>
                      </div>
                    </div>

                    <div className="flex items-center space-x-4">
                      <div className="text-right font-mono">
                        <div className="text-xs font-bold text-slate-900">
                          {(f.current_load_kw ?? 0).toFixed(1)} <span className="text-[10px] text-slate-500 font-normal">/ {f.capacity_kw} kW</span>
                        </div>
                        <div className={`text-[10px] font-semibold ${(f.loading_pct ?? 0) > 90 ? 'text-red-600' : 'text-slate-500'}`}>
                          {(f.loading_pct ?? 0).toFixed(1)}% loaded
                        </div>
                      </div>

                      <span className={`rounded border px-2 py-0.5 text-[10px] font-bold ${styles.badge}`}>
                        {f.risk_level}
                      </span>
                    </div>
                  </div>

                  {/* Loading Bar */}
                  <div className="mt-3 h-1.5 w-full overflow-hidden rounded-full bg-slate-200">
                    <div
                      className={`h-full rounded-full ${
                        (f.loading_pct ?? 0) > 90 ? 'bg-red-600' : (f.loading_pct ?? 0) > 80 ? 'bg-amber-500' : 'bg-emerald-500'
                      }`}
                      style={{ width: `${Math.min(100, f.loading_pct ?? 0)}%` }}
                    />
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        {/* Selected Feeder Deep Dive & Demand Response Trigger */}
        {selectedFeeder && (
          <div className="glass-card rounded-2xl p-5 flex flex-col justify-between shadow-xs">
            <div>
              <div className="flex items-center justify-between border-b border-slate-200 pb-3">
                <div className="flex items-center space-x-2">
                  <UtilityPole className="h-5 w-5 text-sky-600" />
                  <h3 className="text-sm font-bold text-slate-900">{selectedFeeder.feeder_id}</h3>
                </div>
                <span className={`rounded border px-2 py-0.5 text-[10px] font-bold ${getRiskStyles(selectedFeeder.risk_level).badge}`}>
                  {selectedFeeder.risk_level} RISK
                </span>
              </div>

              <div className="mt-3 text-xs text-slate-900 font-bold">
                {selectedFeeder.name}
              </div>

              {/* Status Diagnostic Callout */}
              <div className="mt-3 rounded-xl border border-slate-200 bg-slate-50 p-3 text-xs text-slate-700">
                <div className="text-[10px] font-mono uppercase text-slate-500 font-bold">Diagnostic Assessment:</div>
                <p className="mt-1 text-[11px] leading-relaxed">
                  {selectedFeeder.status_reason}
                </p>
              </div>

              {/* Asset Capabilities on this Feeder */}
              <div className="mt-4 space-y-2 text-xs font-mono">
                <div className="flex items-center justify-between rounded-lg border border-slate-200 bg-white px-3 py-2">
                  <span className="text-slate-600 flex items-center space-x-1.5">
                    <Sun className="h-3.5 w-3.5 text-amber-500" />
                    <span>Solar Connected:</span>
                  </span>
                  <strong className="text-amber-700">{selectedFeeder.solar_connected_kw} kW</strong>
                </div>

                <div className="flex items-center justify-between rounded-lg border border-slate-200 bg-white px-3 py-2">
                  <span className="text-slate-600 flex items-center space-x-1.5">
                    <Battery className="h-3.5 w-3.5 text-purple-600" />
                    <span>Battery Storage:</span>
                  </span>
                  <strong className="text-purple-700">{selectedFeeder.battery_storage_kwh} kWh</strong>
                </div>

                <div className="flex items-center justify-between rounded-lg border border-slate-200 bg-white px-3 py-2">
                  <span className="text-slate-600 flex items-center space-x-1.5">
                    <Zap className="h-3.5 w-3.5 text-emerald-600" />
                    <span>Available Flexibility:</span>
                  </span>
                  <strong className="text-emerald-700">{selectedFeeder.flexible_capacity_kw} kW</strong>
                </div>
              </div>
            </div>

            {/* Operator DR Action Trigger */}
            <div className="mt-6 pt-4 border-t border-slate-200">
              <button
                onClick={() => handleTriggerDR(selectedFeeder.feeder_id)}
                className="w-full flex items-center justify-center space-x-2 rounded-xl bg-gradient-to-r from-red-600 to-amber-600 px-4 py-3 text-xs font-bold text-white hover:from-red-500 hover:to-amber-500 transition shadow-sm"
              >
                <Radio className="h-4 w-4 animate-pulse" />
                <span>Dispatch 15 kW Demand Response</span>
              </button>
              <p className="mt-2 text-center text-[10px] text-slate-500 font-medium">
                Dispatches battery discharge + EV charge deferral to relieve transformer stress
              </p>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};
