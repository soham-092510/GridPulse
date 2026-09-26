import React, { useState, useEffect } from 'react';
import { 
  Calendar as CalendarIcon, 
  CheckCircle2, 
  AlertTriangle, 
  Flame, 
  HelpCircle
} from 'lucide-react';
import { 
  ResponsiveContainer, 
  AreaChart, 
  Area, 
  Line, 
  XAxis, 
  YAxis, 
  Tooltip, 
  CartesianGrid, 
  Legend 
} from 'recharts';
import { DailySummary } from '../types';
import { fetchMonthCalendar, fetchDailyAnalysis } from '../services/api';
import { defaultCalendarDays, defaultDailySummary } from '../services/mockData';

export const DailyAnalysisView: React.FC = () => {
  const [selectedDate, setSelectedDate] = useState<string>('2026-09-21');
  const [calendarDays, setCalendarDays] = useState<any[]>(defaultCalendarDays);
  const [dayData, setDayData] = useState<DailySummary>(defaultDailySummary);

  useEffect(() => {
    async function loadCalendar() {
      try {
        const res = await fetchMonthCalendar(9, 2026);
        if (res && res.days && res.days.length > 0) {
          setCalendarDays(res.days);
        }
      } catch (err) {
        console.log('Using default calendar', err);
      }
    }
    loadCalendar();
  }, []);

  useEffect(() => {
    async function loadDay() {
      try {
        const res = await fetchDailyAnalysis(selectedDate);
        if (res && res.date_str) {
          setDayData(res);
        }
      } catch (err) {
        console.log('Using default day retrospective', err);
      }
    }
    loadDay();
  }, [selectedDate]);

  return (
    <div className="space-y-6">
      {/* Top Header */}
      <div className="glass-card rounded-2xl p-5 shadow-xs">
        <div className="flex items-center space-x-2">
          <CalendarIcon className="h-5 w-5 text-emerald-600" />
          <h2 className="text-base font-bold text-slate-900">Daily Retrospective & Day-by-Day Historical Explorer</h2>
        </div>
        <p className="mt-1 text-xs text-slate-500">
          Every day's continuous measurements are consolidated into historical memory, refining baseline understanding and future decisions.
        </p>
      </div>

      {/* Interactive September 2026 Calendar */}
      <div className="glass-card rounded-2xl p-5 shadow-xs">
        <div className="flex items-center justify-between border-b border-slate-200 pb-3">
          <div>
            <h3 className="text-sm font-bold text-slate-900">September 2026 Calendar</h3>
            <p className="text-[11px] text-slate-500">Click any day to inspect its full 24-hour retrospective and anomaly history</p>
          </div>
          <div className="flex items-center space-x-3 text-xs font-medium">
            <span className="flex items-center space-x-1 text-emerald-700">
              <CheckCircle2 className="h-3.5 w-3.5" />
              <span>Normal</span>
            </span>
            <span className="flex items-center space-x-1 text-amber-700">
              <AlertTriangle className="h-3.5 w-3.5" />
              <span>Anomaly</span>
            </span>
            <span className="flex items-center space-x-1 text-red-700">
              <Flame className="h-3.5 w-3.5" />
              <span>Peak Spike</span>
            </span>
          </div>
        </div>

        {/* Days Grid */}
        <div className="mt-4 grid grid-cols-7 gap-2">
          {['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'].map((dayName) => (
            <div key={dayName} className="text-center font-mono text-[11px] font-bold text-slate-500 uppercase py-1">
              {dayName}
            </div>
          ))}

          {calendarDays.map((d) => {
            const dateStr = d.date;
            const isSelected = selectedDate === dateStr;
            const isNormal = d.status === 'NORMAL';
            const isWarning = d.status === 'WARNING';
            const isCritical = d.status === 'CRITICAL';

            return (
              <button
                key={dateStr}
                onClick={() => setSelectedDate(dateStr)}
                className={`group relative flex flex-col items-center justify-between rounded-xl border p-2.5 transition-all ${
                  isSelected
                    ? 'border-emerald-600 bg-emerald-50/60 shadow-md ring-2 ring-emerald-500/20'
                    : 'border-slate-200 bg-white hover:bg-slate-50 hover:border-slate-300'
                }`}
              >
                <div className="flex w-full items-center justify-between">
                  <span className={`font-mono text-xs font-bold ${isSelected ? 'text-emerald-800' : 'text-slate-800'}`}>
                    {d.day}
                  </span>
                  <div>
                    {isCritical ? (
                      <Flame className="h-3.5 w-3.5 text-red-600 animate-pulse" />
                    ) : isWarning ? (
                      <AlertTriangle className="h-3.5 w-3.5 text-amber-600" />
                    ) : (
                      <CheckCircle2 className="h-3.5 w-3.5 text-emerald-600" />
                    )}
                  </div>
                </div>

                <div className="mt-1 text-left w-full font-mono text-[10px] text-slate-500">
                  <div>{d.peak_demand_kw ? `${d.peak_demand_kw.toFixed(0)} kW` : '104 kW'}</div>
                </div>
              </button>
            );
          })}
        </div>
      </div>

      {/* Selected Day Retrospective Analysis */}
      <div className="space-y-6">
        {/* Day Key Metrics */}
        <div className="grid grid-cols-2 gap-3 sm:grid-cols-3 lg:grid-cols-6">
          <div className="glass-card rounded-xl p-4 shadow-xs">
            <div className="text-[11px] font-semibold text-slate-500 uppercase">Total Consumption</div>
            <div className="mt-1.5 font-mono text-xl font-bold text-slate-900">{(dayData.total_consumption_kwh ?? 1620).toLocaleString()} <span className="text-xs text-slate-500 font-normal">kWh</span></div>
            <div className="mt-1 text-[10px] text-slate-500">24-hour aggregated</div>
          </div>

          <div className="glass-card rounded-xl p-4 shadow-xs">
            <div className="text-[11px] font-semibold text-slate-500 uppercase">Peak Demand</div>
            <div className="mt-1.5 font-mono text-xl font-bold text-red-600">{(dayData.peak_demand_kw ?? 104.5).toFixed(1)} <span className="text-xs text-slate-500 font-normal">kW</span></div>
            <div className="mt-1 text-[10px] text-slate-500">at {dayData.peak_time || '19:45'}</div>
          </div>

          <div className="glass-card rounded-xl p-4 shadow-xs">
            <div className="text-[11px] font-semibold text-slate-500 uppercase">Average Demand</div>
            <div className="mt-1.5 font-mono text-xl font-bold text-slate-900">{(dayData.avg_demand_kw ?? 67.5).toFixed(1)} <span className="text-xs text-slate-500 font-normal">kW</span></div>
            <div className="mt-1 text-[10px] text-slate-500">Min: {(dayData.min_demand_kw ?? 35.0).toFixed(1)} kW</div>
          </div>

          <div className="glass-card rounded-xl p-4 shadow-xs">
            <div className="text-[11px] font-semibold text-slate-500 uppercase">Solar Generation</div>
            <div className="mt-1.5 font-mono text-xl font-bold text-amber-600">{(dayData.solar_generation_kwh ?? 420).toFixed(0)} <span className="text-xs text-slate-500 font-normal">kWh</span></div>
            <div className="mt-1 text-[10px] text-emerald-600 font-medium">Clean local energy</div>
          </div>

          <div className="glass-card rounded-xl p-4 shadow-xs">
            <div className="text-[11px] font-semibold text-slate-500 uppercase">Net Grid Import</div>
            <div className="mt-1.5 font-mono text-xl font-bold text-sky-600">{(dayData.grid_import_kwh ?? 1200).toFixed(0)} <span className="text-xs text-slate-500 font-normal">kWh</span></div>
            <div className="mt-1 text-[10px] text-slate-500">Substation supply</div>
          </div>

          <div className="glass-card rounded-xl p-4 shadow-xs">
            <div className="text-[11px] font-semibold text-slate-500 uppercase">Peak Shaving Impact</div>
            <div className="mt-1.5 font-mono text-xl font-bold text-emerald-600">-{(dayData.peak_reduction_achieved_kw ?? 18.5).toFixed(1)} <span className="text-xs text-slate-500 font-normal">kW</span></div>
            <div className="mt-1 text-[10px] text-emerald-600 font-medium">Flexibility dispatch</div>
          </div>
        </div>

        {/* Historical Baseline Comparison Pill Grid */}
        <div className="grid grid-cols-1 gap-4 lg:grid-cols-3">
          <div className="glass-card rounded-xl p-4 shadow-xs">
            <div className="text-[11px] font-semibold text-slate-500 uppercase">vs 7-Day Rolling Average</div>
            <div className="mt-1 flex items-baseline space-x-2">
              <span className={`font-mono text-xl font-bold ${(dayData.comparison_vs_7d_pct ?? 0) > 0 ? 'text-amber-700' : 'text-emerald-700'}`}>
                {(dayData.comparison_vs_7d_pct ?? 0) > 0 ? `+${(dayData.comparison_vs_7d_pct ?? 0).toFixed(1)}%` : `${(dayData.comparison_vs_7d_pct ?? 0).toFixed(1)}%`}
              </span>
              <span className="text-xs text-slate-500">recent trend</span>
            </div>
          </div>

          <div className="glass-card rounded-xl p-4 shadow-xs">
            <div className="text-[11px] font-semibold text-slate-500 uppercase">vs 30-Day Monthly Average</div>
            <div className="mt-1 flex items-baseline space-x-2">
              <span className={`font-mono text-xl font-bold ${(dayData.comparison_vs_30d_pct ?? 0) > 0 ? 'text-amber-700' : 'text-emerald-700'}`}>
                {(dayData.comparison_vs_30d_pct ?? 0) > 0 ? `+${(dayData.comparison_vs_30d_pct ?? 0).toFixed(1)}%` : `${(dayData.comparison_vs_30d_pct ?? 0).toFixed(1)}%`}
              </span>
              <span className="text-xs text-slate-500">seasonal baseline</span>
            </div>
          </div>

          <div className="glass-card rounded-xl p-4 shadow-xs">
            <div className="text-[11px] font-semibold text-slate-500 uppercase">vs Same Weekday Average</div>
            <div className="mt-1 flex items-baseline space-x-2">
              <span className={`font-mono text-xl font-bold ${(dayData.comparison_vs_same_weekday_pct ?? 0) > 0 ? 'text-amber-700' : 'text-emerald-700'}`}>
                {(dayData.comparison_vs_same_weekday_pct ?? 0) > 0 ? `+${(dayData.comparison_vs_same_weekday_pct ?? 0).toFixed(1)}%` : `${(dayData.comparison_vs_same_weekday_pct ?? 0).toFixed(1)}%`}
              </span>
              <span className="text-xs text-slate-500">weekday pattern</span>
            </div>
          </div>
        </div>

        {/* Why is Today Different? AI Attribution Box */}
        <div className="glass-card rounded-2xl p-5 border-emerald-200 bg-emerald-50/50 shadow-xs">
          <div className="flex items-center space-x-2 text-emerald-800">
            <HelpCircle className="h-5 w-5" />
            <h3 className="text-sm font-bold text-slate-900">Why was {selectedDate} different? (AI Diagnostic Attribution)</h3>
          </div>
          <p className="mt-2 text-xs leading-relaxed text-slate-800 font-medium">
            {dayData.explanation}
          </p>
        </div>

        {/* 24-Hour Diurnal Hourly Chart */}
        <div className="glass-card rounded-2xl p-5 shadow-xs">
          <div className="flex items-center justify-between border-b border-slate-200 pb-3">
            <div>
              <h3 className="text-sm font-bold text-slate-900">24-Hour Energy Profile ({selectedDate})</h3>
              <p className="text-[11px] text-slate-500">Actual demand vs stratified historical expectation and rooftop solar</p>
            </div>
          </div>

          <div className="mt-4 h-72 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={dayData.hourly_curve}>
                <defs>
                  <linearGradient id="dayDemandGrad" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#059669" stopOpacity={0.2}/>
                    <stop offset="95%" stopColor="#059669" stopOpacity={0}/>
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="#F1F5F9" />
                <XAxis dataKey="hour" stroke="#94A3B8" tick={{ fontSize: 11 }} />
                <YAxis stroke="#94A3B8" tick={{ fontSize: 11 }} unit=" kW" />
                <Tooltip
                  contentStyle={{ backgroundColor: '#FFFFFF', borderColor: '#E2E8F0', borderRadius: '8px', boxShadow: '0 4px 6px -1px rgba(0,0,0,0.1)' }}
                  labelStyle={{ color: '#64748B', fontSize: '11px', fontWeight: 'bold' }}
                  itemStyle={{ fontSize: '12px' }}
                />
                <Legend wrapperStyle={{ fontSize: '11px', paddingTop: '10px' }} />
                <Area type="monotone" dataKey="demand_kw" name="Actual Demand (kW)" stroke="#059669" strokeWidth={2} fill="url(#dayDemandGrad)" />
                <Line type="monotone" dataKey="baseline_kw" name="Historical Baseline (kW)" stroke="#94A3B8" strokeDasharray="4 4" strokeWidth={1.5} dot={false} />
                <Area type="monotone" dataKey="solar_kw" name="Solar Generation (kW)" stroke="#D97706" strokeWidth={1.5} fill="none" />
                <Line type="monotone" dataKey="grid_import_kw" name="Grid Import (kW)" stroke="#0284C7" strokeWidth={1.5} dot={false} />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>
    </div>
  );
};
