import React from 'react';

/**
 * StatCard Component
 * Modern Indigo AI scorecard for KPIs and benchmark metrics.
 */
export default function StatCard({
  title,
  value,
  subtitle,
  badge,
  badgeType = 'default',
  icon: Icon,
}) {
  const getBadgeStyle = () => {
    switch (badgeType) {
      case 'success':
        return 'bg-emerald-50 dark:bg-emerald-950/40 text-emerald-700 dark:text-emerald-400 border-emerald-200 dark:border-emerald-800';
      case 'warning':
        return 'bg-amber-50 dark:bg-amber-950/40 text-amber-700 dark:text-amber-400 border-amber-200 dark:border-amber-800';
      case 'info':
        return 'bg-indigo-50 dark:bg-indigo-950/60 text-indigo-700 dark:text-indigo-300 border-indigo-200 dark:border-indigo-800/60';
      case 'default':
      default:
        return 'bg-slate-100 dark:bg-white/[0.04] text-slate-700 dark:text-slate-300 border-slate-200/80 dark:border-white/[0.08]';
    }
  };

  return (
    <div className="card-linear-hover p-5">
      <div className="flex items-center justify-between mb-3">
        <span className="text-xs uppercase tracking-wider text-slate-500 dark:text-slate-400 font-bold">
          {title}
        </span>
        {Icon && (
          <div className="w-8 h-8 rounded-lg bg-indigo-50 dark:bg-indigo-950/60 text-indigo-600 dark:text-indigo-400 flex items-center justify-center border border-indigo-200/60 dark:border-indigo-800/60 shadow-xs">
            <Icon className="w-4 h-4" />
          </div>
        )}
      </div>

      <div className="flex items-baseline space-x-2">
        <span className="text-2xl sm:text-3xl font-extrabold tracking-tight text-slate-900 dark:text-white font-mono">
          {value}
        </span>
        {badge && (
          <span className={`font-mono text-[10px] uppercase font-bold px-2 py-0.5 rounded-full border ${getBadgeStyle()}`}>
            {badge}
          </span>
        )}
      </div>

      {subtitle && (
        <p className="text-xs text-slate-500 dark:text-slate-400 mt-2.5 pt-2 border-t border-slate-200/60 dark:border-white/[0.06] leading-relaxed">
          {subtitle}
        </p>
      )}
    </div>
  );
}