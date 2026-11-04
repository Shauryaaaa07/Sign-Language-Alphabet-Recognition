import React from 'react';

/**
 * PageHeader Component
 * Sleek modern Linear-style header for interior platform pages.
 */
export default function PageHeader({ badge, title, subtitle, actions, children }) {
  return (
    <div className="pb-5 border-b border-slate-200/80 dark:border-white/[0.08]">
      <div className="flex flex-col md:flex-row md:items-end md:justify-between gap-4">
        <div className="space-y-1.5 max-w-3xl">
          {badge && (
            <div className="inline-flex items-center space-x-1.5 text-[11px] font-semibold uppercase tracking-wider px-2.5 py-0.5 rounded-full bg-indigo-50 dark:bg-indigo-950/60 text-indigo-700 dark:text-indigo-300 border border-indigo-200 dark:border-indigo-800/60">
              <span className="w-1.5 h-1.5 rounded-full bg-indigo-500 animate-pulse" />
              <span>{badge}</span>
            </div>
          )}
          <h1 className="text-2xl sm:text-3xl lg:text-4xl font-extrabold tracking-tight text-slate-900 dark:text-white">
            {title}
          </h1>
          {subtitle && (
            <p className="text-sm sm:text-base text-slate-600 dark:text-slate-400 leading-relaxed font-normal">
              {subtitle}
            </p>
          )}
        </div>
        {actions && <div className="flex items-center space-x-2.5 shrink-0">{actions}</div>}
      </div>
      {children && <div className="mt-4">{children}</div>}
    </div>
  );
}
