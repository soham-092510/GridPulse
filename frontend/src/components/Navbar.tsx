import React from 'react';
import { 
  Zap, 
  Radio, 
  TrendingUp, 
  AlertTriangle, 
  Calendar, 
  Sliders, 
  Layers, 
  Building2, 
  Activity
} from 'lucide-react';

interface NavbarProps {
  activeTab: string;
  setActiveTab: (tab: string) => void;
  systemMode: string;
  setSystemMode: (mode: string) => void;
  isConnected: boolean;
  anomalyCount: number;
}

export const Navbar: React.FC<NavbarProps> = ({
  activeTab,
  setActiveTab,
  systemMode,
  setSystemMode,
  isConnected,
  anomalyCount
}) => {
  const navItems = [
    { id: 'live', label: 'Live Operations', icon: Activity },
    { id: 'gateway', label: 'Data Gateway', icon: Radio },
    { id: 'forecast', label: 'Forecasts', icon: TrendingUp },
    { id: 'anomalies', label: 'Anomalies', icon: AlertTriangle, badge: anomalyCount },
    { id: 'daily', label: 'Daily Retrospective', icon: Calendar },
    { id: 'flexibility', label: 'Flexibility & Control', icon: Sliders },
    { id: 'whatif', label: 'What-If Planner', icon: Layers },
    { id: 'discom', label: 'DISCOM Feeders', icon: Building2 },
  ];

  return (
    <header className="sticky top-0 z-50 border-b border-slate-200 bg-white/95 backdrop-blur-md shadow-sm">
      <div className="mx-auto flex max-w-7xl items-center justify-between px-4 py-3 sm:px-6">
        {/* Brand & Logo */}
        <div className="flex items-center space-x-3">
          <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-emerald-600 text-white shadow-md shadow-emerald-600/20">
            <Zap className="h-6 w-6" />
          </div>
          <div>
            <div className="flex items-center space-x-2">
              <span className="text-xl font-bold tracking-tight text-slate-900">
                Neighbour<span className="text-emerald-600">Flex</span>
              </span>
              <span className="rounded-md border border-emerald-200 bg-emerald-50 px-1.5 py-0.5 text-[10px] font-semibold text-emerald-700 uppercase tracking-wider">
                PS3 Schneider
              </span>
            </div>
            <p className="text-[11px] text-slate-500 font-medium">Real-Time AI Neighbourhood Energy Intelligence & Flexibility</p>
          </div>
        </div>

        {/* Operating Mode & Telemetry Status */}
        <div className="flex items-center space-x-3">
          <div className="flex items-center space-x-1 rounded-lg border border-slate-200 bg-slate-100 p-1 text-xs">
            {['DIGITAL_TWIN', 'LIVE', 'REPLAY'].map((mode) => (
              <button
                key={mode}
                onClick={() => setSystemMode(mode)}
                className={`rounded-md px-2.5 py-1 text-xs font-semibold transition-all ${
                  systemMode === mode
                    ? 'bg-white text-emerald-700 shadow-sm'
                    : 'text-slate-600 hover:text-slate-900'
                }`}
              >
                {mode === 'DIGITAL_TWIN' ? 'Digital Twin' : mode === 'LIVE' ? 'Live Meter' : 'Replay'}
              </button>
            ))}
          </div>

          <div className="flex items-center space-x-2 rounded-lg border border-slate-200 bg-slate-50 px-3 py-1.5 text-xs">
            <span className={`relative flex h-2.5 w-2.5`}>
              {isConnected && (
                <span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-emerald-500 opacity-75"></span>
              )}
              <span className={`relative inline-flex h-2.5 w-2.5 rounded-full ${isConnected ? 'bg-emerald-500' : 'bg-amber-500'}`}></span>
            </span>
            <span className="font-mono text-[11px] font-medium text-slate-700">
              {isConnected ? 'STREAM 1s' : 'CONNECTING'}
            </span>
          </div>
        </div>
      </div>

      {/* Navigation Sub-bar */}
      <nav className="border-t border-slate-100 bg-slate-50/50 px-4 sm:px-6">
        <div className="mx-auto flex max-w-7xl space-x-1 overflow-x-auto py-1.5">
          {navItems.map((item) => {
            const Icon = item.icon;
            const isActive = activeTab === item.id;
            return (
              <button
                key={item.id}
                onClick={() => setActiveTab(item.id)}
                className={`group flex items-center space-x-2 whitespace-nowrap rounded-lg px-3 py-1.5 text-xs font-semibold transition-all ${
                  isActive
                    ? 'bg-emerald-50 text-emerald-700 shadow-xs border border-emerald-200/60'
                    : 'text-slate-600 hover:bg-slate-100 hover:text-slate-900'
                }`}
              >
                <Icon className={`h-4 w-4 ${isActive ? 'text-emerald-600' : 'text-slate-500 group-hover:text-slate-800'}`} />
                <span>{item.label}</span>
                {item.badge !== undefined && item.badge > 0 && (
                  <span className="flex h-4 min-w-4 items-center justify-center rounded-full bg-red-600 px-1 text-[10px] font-bold text-white animate-pulse">
                    {item.badge}
                  </span>
                )}
              </button>
            );
          })}
        </div>
      </nav>
    </header>
  );
};
