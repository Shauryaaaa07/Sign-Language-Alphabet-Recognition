import React from 'react';

/**
 * FeatureCard Component
 * Structured Modern Indigo AI feature card with clear hierarchy and subtle ambient hover.
 */
export default function FeatureCard({ icon: Icon, title, description, tag, onClick }) {
  return (
    <div
      onClick={onClick}
      className={`card-linear-hover p-6 ${onClick ? 'cursor-pointer' : ''}`}
    >
      <div className="flex items-center justify-between mb-4">
        <div className="w-9 h-9 rounded-xl bg-indigo-50 dark:bg-indigo-950/60 text-indigo-600 dark:text-indigo-400 flex items-center justify-center border border-indigo-200/60 dark:border-indigo-800/60 shadow-xs">
          <Icon className="w-4 h-4" />
        </div>
        {tag && (
          <span className="font-mono text-[10px] uppercase font-bold tracking-wider px-2.5 py-0.5 rounded-full border border-indigo-200 dark:border-indigo-800/60 bg-indigo-50 dark:bg-indigo-950/60 text-indigo-700 dark:text-indigo-300">
            {tag}
          </span>
        )}
      </div>

      <h3 className="text-base font-bold text-slate-900 dark:text-white mb-2 tracking-tight">
        {title}
      </h3>
      <p className="text-xs sm:text-sm text-slate-600 dark:text-slate-400 leading-relaxed font-normal">
        {description}
      </p>
    </div>
  );
}