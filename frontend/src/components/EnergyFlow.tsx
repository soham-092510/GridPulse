import React from 'react';
import { Sun, Battery, Car, Home, UtilityPole } from 'lucide-react';

interface EnergyFlowProps {
  solarKw: number;
  gridKw: number;
  batteryKw: number;
  batterySoc: number;
  evKw: number;
  demandKw: number;
}

export const EnergyFlow: React.FC<EnergyFlowProps> = ({
  solarKw = 0,
  gridKw = 0,
  batteryKw = 0,
  batterySoc = 75,
  evKw = 0,
  demandKw = 65
}) => {
  const safeSolar = solarKw ?? 0;
  const safeGrid = gridKw ?? 0;
  const safeBatteryKw = batteryKw ?? 0;
  const safeBatterySoc = batterySoc ?? 75;
  const safeEv = evKw ?? 0;
  const safeDemand = demandKw ?? 65;

  const isBatteryDischarging = safeBatteryKw > 0.5;
  const isBatteryCharging = safeBatteryKw < -0.5;

  return (
    <div className="glass-card rounded-2xl p-5 shadow-xs">
      <div className="flex items-center justify-between border-b border-slate-200 pb-3">
        <div>
          <h3 className="text-sm font-bold text-slate-900">Live Neighbourhood Power Balance</h3>
          <p className="text-[11px] text-slate-500">Dynamic bus routing & real-time energy flow</p>
        </div>
        <div className="flex items-center space-x-3 text-xs">
          <span className="flex items-center space-x-1.5">
            <span className="h-2.5 w-2.5 rounded-full bg-amber-500"></span>
            <span className="text-slate-700 font-medium">Solar PV</span>
          </span>
          <span className="flex items-center space-x-1.5">
            <span className="h-2.5 w-2.5 rounded-full bg-sky-600"></span>
            <span className="text-slate-700 font-medium">Grid Feeder</span>
          </span>
          <span className="flex items-center space-x-1.5">
            <span className="h-2.5 w-2.5 rounded-full bg-emerald-600"></span>
            <span className="text-slate-700 font-medium">Battery BESS</span>
          </span>
        </div>
      </div>

      <div className="relative mt-4 flex items-center justify-center py-4 bg-slate-50/50 rounded-xl border border-slate-100">
        <svg className="w-full max-w-2xl h-52 overflow-visible" viewBox="0 0 640 220">
          {/* Lines from Sources to Central Bus (x=320, y=110) */}
          {/* Solar (x=100, y=50) -> Bus */}
          <path
            d="M 160 50 Q 240 50 320 110"
            fill="none"
            stroke="#D97706"
            strokeWidth="3"
            strokeOpacity="0.25"
          />
          {safeSolar > 1 && (
            <path
              d="M 160 50 Q 240 50 320 110"
              fill="none"
              stroke="#D97706"
              strokeWidth="3"
              className="animate-flow-forward"
            />
          )}

          {/* Grid (x=100, y=170) -> Bus */}
          <path
            d="M 160 170 Q 240 170 320 110"
            fill="none"
            stroke="#0284C7"
            strokeWidth="3"
            strokeOpacity="0.25"
          />
          {safeGrid > 1 && (
            <path
              d="M 160 170 Q 240 170 320 110"
              fill="none"
              stroke="#0284C7"
              strokeWidth="3"
              className="animate-flow-forward"
            />
          )}

          {/* Battery (x=320, y=20) <-> Bus (x=320, y=110) */}
          <path
            d="M 320 50 L 320 110"
            fill="none"
            stroke="#7C3AED"
            strokeWidth="3"
            strokeOpacity="0.25"
          />
          {isBatteryDischarging && (
            <path
              d="M 320 50 L 320 110"
              fill="none"
              stroke="#059669"
              strokeWidth="3"
              className="animate-flow-forward"
            />
          )}
          {isBatteryCharging && (
            <path
              d="M 320 50 L 320 110"
              fill="none"
              stroke="#7C3AED"
              strokeWidth="3"
              className="animate-flow-reverse"
            />
          )}

          {/* Bus (x=320, y=110) -> Domestic Homes (x=520, y=50) */}
          <path
            d="M 320 110 Q 400 50 480 50"
            fill="none"
            stroke="#059669"
            strokeWidth="3"
            strokeOpacity="0.25"
          />
          {safeDemand > 1 && (
            <path
              d="M 320 110 Q 400 50 480 50"
              fill="none"
              stroke="#059669"
              strokeWidth="3"
              className="animate-flow-forward"
            />
          )}

          {/* Bus (x=320, y=110) -> EV Fleet (x=520, y=170) */}
          <path
            d="M 320 110 Q 400 170 480 170"
            fill="none"
            stroke="#059669"
            strokeWidth="3"
            strokeOpacity="0.25"
          />
          {safeEv > 1 && (
            <path
              d="M 320 110 Q 400 170 480 170"
              fill="none"
              stroke="#059669"
              strokeWidth="3"
              className="animate-flow-forward"
            />
          )}

          {/* Central Distribution Bus Node */}
          <circle cx="320" cy="110" r="14" fill="#FFFFFF" stroke="#059669" strokeWidth="3" />
          <circle cx="320" cy="110" r="6" fill="#059669" />
        </svg>

        {/* Overlay Node Cards */}
        {/* Solar Node */}
        <div className="absolute left-4 top-2 flex items-center space-x-2.5 rounded-xl border border-amber-200 bg-white px-3 py-2 shadow-sm">
          <div className="rounded-lg bg-amber-50 p-2 text-amber-600">
            <Sun className="h-5 w-5" />
          </div>
          <div>
            <div className="text-[10px] uppercase font-semibold text-slate-500">Solar PV Array</div>
            <div className="font-mono text-sm font-bold text-amber-600">{safeSolar.toFixed(1)} kW</div>
          </div>
        </div>

        {/* Grid Node */}
        <div className="absolute bottom-2 left-4 flex items-center space-x-2.5 rounded-xl border border-sky-200 bg-white px-3 py-2 shadow-sm">
          <div className="rounded-lg bg-sky-50 p-2 text-sky-600">
            <UtilityPole className="h-5 w-5" />
          </div>
          <div>
            <div className="text-[10px] uppercase font-semibold text-slate-500">Feeder Grid Import</div>
            <div className="font-mono text-sm font-bold text-sky-600">{safeGrid.toFixed(1)} kW</div>
          </div>
        </div>

        {/* Battery Node (Top Center) */}
        <div className="absolute -top-1 left-1/2 -translate-x-1/2 flex items-center space-x-2.5 rounded-xl border border-purple-200 bg-white px-3 py-1.5 shadow-sm">
          <div className="rounded-lg bg-purple-50 p-1.5 text-purple-600">
            <Battery className="h-4 w-4" />
          </div>
          <div>
            <div className="text-[10px] uppercase font-semibold text-slate-500">
              Community BESS ({safeBatterySoc.toFixed(0)}% SOC)
            </div>
            <div className="font-mono text-xs font-bold text-purple-700">
              {safeBatteryKw > 0 ? `+${safeBatteryKw.toFixed(1)} kW Discharging` : safeBatteryKw < 0 ? `${safeBatteryKw.toFixed(1)} kW Charging` : 'Idle / Standby'}
            </div>
          </div>
        </div>

        {/* Domestic Demand Node (Top Right) */}
        <div className="absolute right-4 top-2 flex items-center space-x-2.5 rounded-xl border border-emerald-200 bg-white px-3 py-2 shadow-sm">
          <div className="rounded-lg bg-emerald-50 p-2 text-emerald-600">
            <Home className="h-5 w-5" />
          </div>
          <div>
            <div className="text-[10px] uppercase font-semibold text-slate-500">100 Households</div>
            <div className="font-mono text-sm font-bold text-slate-900">{safeDemand.toFixed(1)} kW</div>
          </div>
        </div>

        {/* EV Fleet Node (Bottom Right) */}
        <div className="absolute bottom-2 right-4 flex items-center space-x-2.5 rounded-xl border border-emerald-200 bg-white px-3 py-2 shadow-sm">
          <div className="rounded-lg bg-emerald-50 p-2 text-emerald-600">
            <Car className="h-5 w-5" />
          </div>
          <div>
            <div className="text-[10px] uppercase font-semibold text-slate-500">EV Smart Chargers</div>
            <div className="font-mono text-sm font-bold text-slate-900">{safeEv.toFixed(1)} kW</div>
          </div>
        </div>
      </div>
    </div>
  );
};
