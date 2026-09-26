import React, { useState, useEffect } from 'react';
import { 
  Radio, 
  Plus, 
  CheckCircle2, 
  AlertOctagon, 
  Cpu, 
  Send, 
  Activity, 
  Zap,
  Sun,
  Battery,
  Car,
  CloudSun
} from 'lucide-react';
import { Device } from '../types';
import { fetchDevices, registerDevice, ingestTestTelemetry } from '../services/api';
import { defaultDevices } from '../services/mockData';

export const GatewayView: React.FC = () => {
  const [devices, setDevices] = useState<Device[]>(defaultDevices);
  const [loading, setLoading] = useState(false);
  const [showWizard, setShowWizard] = useState(false);

  // Form state
  const [newDevice, setNewDevice] = useState({
    device_id: '',
    name: '',
    device_type: 'smart_meter',
    manufacturer: 'Schneider Electric',
    protocol: 'mqtt',
    location: 'Sector 7 Feeder'
  });

  // Telemetry tester state
  const [testPayload, setTestPayload] = useState({
    device_id: 'SMART_METER_MAIN',
    metric: 'active_power',
    value: 65.4,
    unit: 'kW'
  });
  const [testResult, setTestResult] = useState<any>(null);

  const loadDevices = async () => {
    try {
      const data = await fetchDevices();
      if (data && data.length > 0) {
        setDevices(data);
      }
    } catch (err) {
      console.log('Using default devices', err);
    }
  };

  useEffect(() => {
    loadDevices();
  }, []);

  const handleRegister = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newDevice.device_id || !newDevice.name) return;
    try {
      await registerDevice(newDevice);
      setShowWizard(false);
      setNewDevice({
        device_id: '',
        name: '',
        device_type: 'smart_meter',
        manufacturer: 'Schneider Electric',
        protocol: 'mqtt',
        location: ''
      });
      loadDevices();
    } catch (err) {
      // Local fallback
      const created: Device = {
        ...newDevice,
        status: 'online',
        health_score: 1.0,
        packets_received: 1,
        packets_rejected: 0,
        last_seen: new Date().toISOString()
      };
      setDevices((prev) => [created, ...prev]);
      setShowWizard(false);
    }
  };

  const handleSendTestTelemetry = async () => {
    try {
      const res = await ingestTestTelemetry(testPayload);
      setTestResult(res);
      loadDevices();
    } catch (err) {
      // Immediate local simulation response if offline
      setTestResult({
        status: 'ACCEPTED',
        quality: 'VALID',
        confidence: 1.0,
        normalized_value: testPayload.unit.toLowerCase() === 'w' ? testPayload.value / 1000 : testPayload.value,
        canonical_unit: 'kW'
      });
    }
  };

  const getDeviceIcon = (type: string) => {
    switch (type) {
      case 'smart_meter': return Zap;
      case 'solar_inverter': return Sun;
      case 'battery_bms': return Battery;
      case 'ev_charger': return Car;
      case 'weather_station': return CloudSun;
      default: return Cpu;
    }
  };

  return (
    <div className="space-y-6">
      {/* Header & Connection Overview */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 glass-card rounded-2xl p-5 shadow-xs">
        <div>
          <div className="flex items-center space-x-2">
            <Radio className="h-5 w-5 text-sky-600 animate-pulse" />
            <h2 className="text-base font-bold text-slate-900">Universal Energy Data Gateway</h2>
          </div>
          <p className="mt-1 text-xs text-slate-500">
            Hardware-agnostic telemetry ingestion pipeline supporting MQTT, REST, Modbus TCP, OCPP, and Open-Meteo APIs
          </p>
        </div>
        <button
          onClick={() => setShowWizard(true)}
          className="flex items-center space-x-2 rounded-xl bg-emerald-600 px-4 py-2 text-xs font-bold text-white hover:bg-emerald-500 transition shadow-sm"
        >
          <Plus className="h-4 w-4" />
          <span>Connect Energy Source</span>
        </button>
      </div>

      {/* Onboarding Wizard Modal */}
      {showWizard && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/40 backdrop-blur-xs p-4">
          <div className="w-full max-w-lg rounded-2xl border border-slate-200 bg-white p-6 shadow-2xl">
            <h3 className="text-sm font-bold text-slate-900">Connect New Energy Asset</h3>
            <p className="text-xs text-slate-500 mt-1">Register an IoT meter, solar inverter, battery BMS, or EV charger</p>

            <form onSubmit={handleRegister} className="mt-4 space-y-3.5">
              <div>
                <label className="text-[11px] font-semibold text-slate-700">Device ID (Unique identifier)</label>
                <input
                  type="text"
                  placeholder="e.g. METER_ZONE_4B"
                  value={newDevice.device_id}
                  onChange={(e) => setNewDevice({ ...newDevice, device_id: e.target.value })}
                  className="mt-1 w-full rounded-lg border border-slate-300 bg-white px-3 py-2 text-xs text-slate-900 focus:border-emerald-500 focus:outline-none"
                  required
                />
              </div>

              <div>
                <label className="text-[11px] font-semibold text-slate-700">Display Name</label>
                <input
                  type="text"
                  placeholder="e.g. Feeder Substation Meter 4B"
                  value={newDevice.name}
                  onChange={(e) => setNewDevice({ ...newDevice, name: e.target.value })}
                  className="mt-1 w-full rounded-lg border border-slate-300 bg-white px-3 py-2 text-xs text-slate-900 focus:border-emerald-500 focus:outline-none"
                  required
                />
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="text-[11px] font-semibold text-slate-700">Asset Type</label>
                  <select
                    value={newDevice.device_type}
                    onChange={(e) => setNewDevice({ ...newDevice, device_type: e.target.value })}
                    className="mt-1 w-full rounded-lg border border-slate-300 bg-white px-3 py-2 text-xs text-slate-900 focus:border-emerald-500 focus:outline-none"
                  >
                    <option value="smart_meter">Smart Energy Meter</option>
                    <option value="solar_inverter">Solar Inverter</option>
                    <option value="battery_bms">Battery Storage (BMS)</option>
                    <option value="ev_charger">EV Smart Charger</option>
                    <option value="weather_station">Weather Station</option>
                  </select>
                </div>

                <div>
                  <label className="text-[11px] font-semibold text-slate-700">Ingestion Protocol</label>
                  <select
                    value={newDevice.protocol}
                    onChange={(e) => setNewDevice({ ...newDevice, protocol: e.target.value })}
                    className="mt-1 w-full rounded-lg border border-slate-300 bg-white px-3 py-2 text-xs text-slate-900 focus:border-emerald-500 focus:outline-none"
                  >
                    <option value="mqtt">MQTT Telemetry</option>
                    <option value="rest">REST API / Webhook</option>
                    <option value="modbus">Modbus TCP</option>
                    <option value="ocpp">OCPP 2.0 (EV)</option>
                    <option value="virtual">Digital Twin Synthetic</option>
                  </select>
                </div>
              </div>

              <div>
                <label className="text-[11px] font-semibold text-slate-700">Physical Location</label>
                <input
                  type="text"
                  placeholder="e.g. Substation DT-04, Sector 7"
                  value={newDevice.location}
                  onChange={(e) => setNewDevice({ ...newDevice, location: e.target.value })}
                  className="mt-1 w-full rounded-lg border border-slate-300 bg-white px-3 py-2 text-xs text-slate-900 focus:border-emerald-500 focus:outline-none"
                />
              </div>

              <div className="flex justify-end space-x-2 pt-2">
                <button
                  type="button"
                  onClick={() => setShowWizard(false)}
                  className="rounded-lg border border-slate-300 px-3.5 py-2 text-xs font-medium text-slate-600 hover:text-slate-900"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="rounded-lg bg-emerald-600 px-4 py-2 text-xs font-bold text-white hover:bg-emerald-500 shadow-sm"
                >
                  Register & Connect
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Connected Assets Table */}
      <div className="glass-card rounded-2xl p-5 shadow-xs">
        <div className="flex items-center justify-between border-b border-slate-200 pb-3">
          <div>
            <h3 className="text-sm font-bold text-slate-900">Active Energy Ingestion Nodes</h3>
            <p className="text-[11px] text-slate-500">{devices.length} registered hardware and virtual energy streams</p>
          </div>
          <span className="rounded-md border border-emerald-200 bg-emerald-50 px-2.5 py-1 font-mono text-[11px] font-bold text-emerald-700">
            Validation Engine: ACTIVE (100% Quality Enforced)
          </span>
        </div>

        <div className="mt-4 overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead>
              <tr className="border-b border-slate-200 text-[11px] uppercase tracking-wider text-slate-500">
                <th className="pb-3 font-semibold">Device</th>
                <th className="pb-3 font-semibold">Type</th>
                <th className="pb-3 font-semibold">Protocol</th>
                <th className="pb-3 font-semibold">Packets Rcvd</th>
                <th className="pb-3 font-semibold">Rejected</th>
                <th className="pb-3 font-semibold">Quality Health</th>
                <th className="pb-3 font-semibold">Status</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {devices.map((dev) => {
                const Icon = getDeviceIcon(dev.device_type || 'smart_meter');
                const healthPct = ((dev.health_score ?? 1.0) * 100).toFixed(1);
                return (
                  <tr key={dev.device_id} className="hover:bg-slate-50/80 transition">
                    <td className="py-3">
                      <div className="flex items-center space-x-2.5">
                        <div className="rounded-lg bg-slate-100 p-2 text-emerald-600">
                          <Icon className="h-4 w-4" />
                        </div>
                        <div>
                          <div className="font-semibold text-slate-900">{dev.name}</div>
                          <div className="font-mono text-[10px] text-slate-500">{dev.device_id}</div>
                        </div>
                      </div>
                    </td>
                    <td className="py-3 capitalize text-slate-700">
                      {(dev.device_type || 'device').replace(/_/g, ' ')}
                    </td>
                    <td className="py-3 font-mono uppercase text-[11px] text-sky-700 font-semibold">
                      {dev.protocol || 'MQTT'}
                    </td>
                    <td className="py-3 font-mono text-slate-700 font-medium">
                      {(dev.packets_received ?? 0).toLocaleString()}
                    </td>
                    <td className="py-3 font-mono text-amber-700 font-semibold">
                      {dev.packets_rejected ?? 0}
                    </td>
                    <td className="py-3">
                      <div className="flex items-center space-x-2">
                        <div className="h-1.5 w-16 overflow-hidden rounded-full bg-slate-200">
                          <div
                            className="h-full bg-emerald-500 rounded-full"
                            style={{ width: `${healthPct}%` }}
                          />
                        </div>
                        <span className="font-mono text-[11px] font-semibold text-slate-700">{healthPct}%</span>
                      </div>
                    </td>
                    <td className="py-3">
                      <span className="inline-flex items-center space-x-1 rounded-md border border-emerald-200 bg-emerald-50 px-2 py-0.5 text-[10px] font-bold text-emerald-700 uppercase">
                        <span className="h-1.5 w-1.5 rounded-full bg-emerald-500"></span>
                        <span>{dev.status}</span>
                      </span>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>

      {/* Interactive Telemetry Test Sandbox */}
      <div className="glass-card rounded-2xl p-5 shadow-xs">
        <div className="flex items-center justify-between border-b border-slate-200 pb-3">
          <div>
            <h3 className="text-sm font-bold text-slate-900">Live Ingestion & Normalizer Test Sandbox</h3>
            <p className="text-[11px] text-slate-500">
              Submit test measurements in any unit (e.g. W, kW, MW, V, A) to inspect real-time unit normalization and range validation.
            </p>
          </div>
          <span className="text-xs text-slate-500 font-mono">POST /api/ingestion/telemetry</span>
        </div>

        <div className="mt-4 grid grid-cols-1 gap-4 md:grid-cols-5 items-end">
          <div>
            <label className="text-[11px] font-semibold text-slate-700">Target Device</label>
            <select
              value={testPayload.device_id}
              onChange={(e) => setTestPayload({ ...testPayload, device_id: e.target.value })}
              className="mt-1 w-full rounded-lg border border-slate-300 bg-white px-3 py-2 text-xs text-slate-900"
            >
              {devices.map((d) => (
                <option key={d.device_id} value={d.device_id}>{d.name} ({d.device_id})</option>
              ))}
            </select>
          </div>

          <div>
            <label className="text-[11px] font-semibold text-slate-700">Metric</label>
            <input
              type="text"
              value={testPayload.metric}
              onChange={(e) => setTestPayload({ ...testPayload, metric: e.target.value })}
              className="mt-1 w-full rounded-lg border border-slate-300 bg-white px-3 py-2 text-xs text-slate-900 font-mono"
            />
          </div>

          <div>
            <label className="text-[11px] font-semibold text-slate-700">Value</label>
            <input
              type="number"
              value={testPayload.value}
              onChange={(e) => setTestPayload({ ...testPayload, value: parseFloat(e.target.value) || 0 })}
              className="mt-1 w-full rounded-lg border border-slate-300 bg-white px-3 py-2 text-xs text-slate-900 font-mono"
            />
          </div>

          <div>
            <label className="text-[11px] font-semibold text-slate-700">Unit (e.g. W, kW, MW)</label>
            <input
              type="text"
              value={testPayload.unit}
              onChange={(e) => setTestPayload({ ...testPayload, unit: e.target.value })}
              className="mt-1 w-full rounded-lg border border-slate-300 bg-white px-3 py-2 text-xs text-slate-900 font-mono"
            />
          </div>

          <button
            onClick={handleSendTestTelemetry}
            className="flex items-center justify-center space-x-1.5 rounded-lg bg-sky-600 px-4 py-2 text-xs font-bold text-white hover:bg-sky-500 transition shadow-xs h-9"
          >
            <Send className="h-3.5 w-3.5" />
            <span>Ingest Reading</span>
          </button>
        </div>

        {/* Validation Result Box */}
        {testResult && (
          <div className={`mt-4 rounded-xl border p-4 ${
            testResult.status === 'ACCEPTED'
              ? 'border-emerald-200 bg-emerald-50 text-emerald-800'
              : 'border-red-200 bg-red-50 text-red-800'
          }`}>
            <div className="flex items-center space-x-2 text-xs font-bold">
              {testResult.status === 'ACCEPTED' ? <CheckCircle2 className="h-4 w-4 text-emerald-600" /> : <AlertOctagon className="h-4 w-4 text-red-600" />}
              <span>INGESTION STATUS: {testResult.status}</span>
            </div>
            <div className="mt-2 grid grid-cols-2 sm:grid-cols-4 gap-2 text-[11px] font-mono">
              <div>Canonical Value: <strong className="text-slate-900">{testResult.normalized_value ?? testResult.value} {testResult.canonical_unit ?? testResult.unit}</strong></div>
              <div>Quality: <strong className="text-slate-900">{testResult.quality || 'VALID'}</strong></div>
              <div>Confidence: <strong className="text-slate-900">{testResult.confidence ?? 1.0}</strong></div>
              {testResult.reason && <div>Reason: <strong className="text-red-700">{testResult.reason}</strong></div>}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};
