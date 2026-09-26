import React, { useState, useEffect } from 'react';
import { 
  AlertTriangle, 
  CheckCircle, 
  HelpCircle
} from 'lucide-react';
import { AnomalyEvent } from '../types';
import { fetchActiveAnomalies, fetchAnomalyHistory } from '../services/api';
import { defaultTelemetry, defaultDailySummary } from '../services/mockData';

export const AnomaliesView: React.FC = () => {
  const [activeAnomalies, setActiveAnomalies] = useState<AnomalyEvent[]>(defaultTelemetry.active_anomalies);
  const [history, setHistory] = useState<AnomalyEvent[]>(defaultDailySummary.events);
  const [filterType, setFilterType] = useState<string>('ALL');

  const loadData = async () => {
    try {
      const [act, hist] = await Promise.all([fetchActiveAnomalies(), fetchAnomalyHistory()]);
      if (act && act.length > 0) setActiveAnomalies(act);
      if (hist && hist.length > 0) setHistory(hist);
    } catch (err) {
      console.log('Using default anomalies', err);
    }
  };

  useEffect(() => {
    loadData();
    const interval = setInterval(loadData, 6000);
    return () => clearInterval(interval);
  }, []);

  const getSeverityBadge = (sev: string) => {
    switch (sev) {
      case 'CRITICAL':
        return 'bg-red-50 text-red-700 border-red-200';
      case 'HIGH':
        return 'bg-orange-50 text-orange-700 border-orange-200';
      case 'MEDIUM':
        return 'bg-amber-50 text-amber-700 border-amber-200';
      default:
        return 'bg-slate-100 text-slate-700 border-slate-200';
    }
  };

  const filteredHistory = history.filter((item) => {
    if (filterType === 'ALL') return true;
    return item.anomaly_type === filterType;
  });

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="glass-card rounded-2xl p-5 shadow-xs">
        <div className="flex items-center space-x-2">
          <AlertTriangle className="h-5 w-5 text-amber-600" />
          <h2 className="text-base font-bold text-slate-900">Anomaly Detection & Root-Cause Investigation Center</h2>
        </div>
        <p className="mt-1 text-xs text-slate-500">
          Continuous physical-statistical deviation tracking correlating demand spikes, solar deficits, and EV clusters with environmental drivers.
        </p>
      </div>

      {/* Active Anomalies with In-Depth Root Cause Cards */}
      <div className="space-y-4">
        <h3 className="text-xs font-bold uppercase tracking-wider text-slate-500">
          Currently Active Anomalies ({activeAnomalies.length})
        </h3>

        {activeAnomalies.length === 0 ? (
          <div className="glass-card flex items-center space-x-3 rounded-2xl p-6 border-emerald-200 bg-emerald-50 text-emerald-800 shadow-xs">
            <CheckCircle className="h-6 w-6 text-emerald-600" />
            <div>
              <div className="text-sm font-bold">All Neighbourhood Feeder Metrics Operating Within Normal Envelope</div>
              <p className="text-xs text-emerald-700 mt-0.5">Live consumption, solar generation, and voltages match stratified historical expectations.</p>
            </div>
          </div>
        ) : (
          <div className="grid grid-cols-1 gap-4 lg:grid-cols-2">
            {activeAnomalies.map((a) => (
              <div key={a.event_id} className="glass-card rounded-2xl p-5 border-red-200 bg-red-50/40 shadow-xs">
                <div className="flex items-start justify-between">
                  <div>
                    <div className="flex items-center space-x-2">
                      <span className="font-mono text-xs font-bold text-red-700">{a.event_id}</span>
                      <span className={`rounded border px-2 py-0.5 text-[10px] font-bold ${getSeverityBadge(a.severity || 'MEDIUM')}`}>
                        {a.severity || 'MEDIUM'}
                      </span>
                    </div>
                    <h4 className="mt-1 text-sm font-bold text-slate-900 capitalize">
                      {(a.anomaly_type || 'ANOMALY').replace(/_/g, ' ')}
                    </h4>
                  </div>
                  <div className="text-right">
                    <span className="font-mono text-lg font-bold text-red-700">
                      {(a.deviation_pct ?? 0) > 0 ? `+${(a.deviation_pct ?? 0).toFixed(1)}%` : `${(a.deviation_pct ?? 0).toFixed(1)}%`}
                    </span>
                    <div className="text-[10px] text-slate-500">vs expected baseline</div>
                  </div>
                </div>

                {/* Expected vs Actual Pill */}
                <div className="mt-3 flex items-center space-x-4 rounded-xl border border-slate-200 bg-white p-3 font-mono text-xs shadow-xs">
                  <div>
                    <span className="text-slate-500 text-[10px] block font-sans">Expected Baseline:</span>
                    <strong className="text-slate-800">{(a.expected_value ?? 0).toFixed(1)} kW</strong>
                  </div>
                  <div className="text-slate-400">→</div>
                  <div>
                    <span className="text-slate-500 text-[10px] block font-sans">Actual Measured:</span>
                    <strong className="text-red-700">{(a.actual_value ?? 0).toFixed(1)} kW</strong>
                  </div>
                  <div className="text-slate-400">→</div>
                  <div>
                    <span className="text-slate-500 text-[10px] block font-sans">Net Gap:</span>
                    <strong className="text-amber-700">{Math.abs((a.actual_value ?? 0) - (a.expected_value ?? 0)).toFixed(1)} kW</strong>
                  </div>
                </div>

                {/* Root Cause AI Attribution */}
                <div className="mt-3 rounded-xl border border-sky-100 bg-sky-50/70 p-3">
                  <div className="flex items-center space-x-1.5 text-xs font-semibold text-sky-800">
                    <HelpCircle className="h-4 w-4" />
                    <span>Root-Cause Attribution:</span>
                  </div>
                  <p className="mt-1 text-xs text-sky-900 leading-relaxed font-medium">
                    {a.root_cause || 'Root-cause analysis in progress'}
                  </p>
                </div>

                <div className="mt-3 flex items-center justify-between text-[11px] text-slate-500 pt-1">
                  <span>Device: <strong className="text-slate-700 font-mono">{a.device_id || 'COMMUNITY_FEEDER'}</strong></span>
                  <span>{new Date(a.timestamp).toLocaleTimeString()}</span>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Historical Incident History Table */}
      <div className="glass-card rounded-2xl p-5 shadow-xs">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-slate-200 pb-3">
          <div>
            <h3 className="text-sm font-bold text-slate-900">Historical Energy Incident Log</h3>
            <p className="text-[11px] text-slate-500">Chronological repository of detected deviations and resolved events</p>
          </div>

          <div className="flex items-center space-x-2">
            <span className="text-[11px] text-slate-500 font-medium">Filter:</span>
            <select
              value={filterType}
              onChange={(e) => setFilterType(e.target.value)}
              className="rounded-lg border border-slate-300 bg-white px-2.5 py-1 text-xs text-slate-900"
            >
              <option value="ALL">All Anomalies</option>
              <option value="demand_spike">Demand Spikes</option>
              <option value="demand_drop">Demand Drops</option>
              <option value="solar_underperformance">Solar Deficits</option>
              <option value="ev_cluster">EV Clusters</option>
              <option value="night_anomaly">Night Baseload</option>
            </select>
          </div>
        </div>

        <div className="mt-4 overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead>
              <tr className="border-b border-slate-200 text-[11px] uppercase tracking-wider text-slate-500">
                <th className="pb-3 font-semibold">Incident ID</th>
                <th className="pb-3 font-semibold">Timestamp</th>
                <th className="pb-3 font-semibold">Type</th>
                <th className="pb-3 font-semibold">Deviation</th>
                <th className="pb-3 font-semibold">Severity</th>
                <th className="pb-3 font-semibold">Root Cause Summary</th>
                <th className="pb-3 font-semibold">Status</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {filteredHistory.map((item) => (
                <tr key={item.event_id} className="hover:bg-slate-50/80 transition">
                  <td className="py-3 font-mono font-bold text-slate-900">{item.event_id}</td>
                  <td className="py-3 text-slate-500 font-mono text-[11px]">
                    {item.timestamp ? new Date(item.timestamp).toLocaleString([], { month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' }) : 'Recent'}
                  </td>
                  <td className="py-3 capitalize text-slate-800 font-medium">
                    {(item.anomaly_type || 'ANOMALY').replace(/_/g, ' ')}
                  </td>
                  <td className="py-3 font-mono font-semibold">
                    <span className={(item.deviation_pct ?? 0) > 0 ? 'text-amber-700' : 'text-sky-700'}>
                      {(item.deviation_pct ?? 0) > 0 ? `+${(item.deviation_pct ?? 0).toFixed(1)}%` : `${(item.deviation_pct ?? 0).toFixed(1)}%`}
                    </span>
                  </td>
                  <td className="py-3">
                    <span className={`rounded border px-2 py-0.5 text-[10px] font-bold ${getSeverityBadge(item.severity || 'MEDIUM')}`}>
                      {item.severity || 'MEDIUM'}
                    </span>
                  </td>
                  <td className="py-3 text-slate-600 max-w-xs truncate text-[11px]">
                    {item.root_cause || 'Physical investigation in progress'}
                  </td>
                  <td className="py-3">
                    <span className="rounded bg-slate-100 px-2 py-0.5 font-mono text-[10px] text-slate-700 font-medium uppercase">
                      {item.status || 'ACTIVE'}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
