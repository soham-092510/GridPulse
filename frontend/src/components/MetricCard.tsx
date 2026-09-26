import React from 'react';
import { LucideIcon } from 'lucide-react';

interface MetricCardProps {
  title: string;
  value: string | number;
  unit?: string;
  icon: LucideIcon;
  iconColor?: string;
  delta?: {
    value: string | number;
    isPositiveGood?: boolean;
    label?: string;
  };
  subtitle?: string;
  badge?: {
    text: string;
    variant: 'green' | 'amber' | 'red' | 'blue' | 'purple';
  };
}

export const MetricCard: React.FC<MetricCardProps> = ({
  title,
  value,
  unit,
  icon: Icon,
  iconColor = 'text-emerald-600',
  delta,
  subtitle,
  badge
}) => {
  const badgeColors = {
    green: 'bg-emerald-50 text-emerald-700 border-emerald-200',
    amber: 'bg-amber-50 text-amber-700 border-amber-200',
    red: 'bg-red-50 text-red-700 border-red-200',
    blue: 'bg-sky-50 text-sky-700 border-sky-200',
    purple: 'bg-purple-50 text-purple-700 border-purple-200'
  };

  return (
    <div className="glass-card glass-card-hover rounded-xl p-4 transition-all duration-200">
      <div className="flex items-center justify-between">
        <span className="text-xs font-semibold text-slate-500 uppercase tracking-wider">{title}</span>
        <div className={`rounded-lg bg-slate-100 p-2 ${iconColor}`}>
          <Icon className="h-4 w-4" />
        </div>
      </div>

      <div className="mt-2.5 flex items-baseline space-x-1.5">
        <span className="font-mono text-2xl font-bold tracking-tight text-slate-900">{value}</span>
        {unit && <span className="font-mono text-xs font-semibold text-slate-500">{unit}</span>}
      </div>

      <div className="mt-2 flex items-center justify-between text-xs">
        {delta ? (
          <div className="flex items-center space-x-1 font-mono text-[11px]">
            <span
              className={`font-semibold ${
                Number(delta.value) > 0
                  ? delta.isPositiveGood ? 'text-emerald-600' : 'text-amber-600'
                  : delta.isPositiveGood ? 'text-amber-600' : 'text-emerald-600'
              }`}
            >
              {Number(delta.value) > 0 ? `+${delta.value}%` : `${delta.value}%`}
            </span>
            <span className="text-slate-500">{delta.label || 'vs baseline'}</span>
          </div>
        ) : subtitle ? (
          <span className="text-slate-500 text-[11px] truncate">{subtitle}</span>
        ) : <div />}

        {badge && (
          <span className={`rounded-md border px-2 py-0.5 text-[10px] font-bold uppercase tracking-wider ${badgeColors[badge.variant]}`}>
            {badge.text}
          </span>
        )}
      </div>
    </div>
  );
};
