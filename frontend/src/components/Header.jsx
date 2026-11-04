import React from 'react';
import StatusIndicator from './StatusIndicator';

/**
 * Header Component
 * Modern Indigo AI platform header displaying system branding and backend connectivity status.
 */
export default function Header({ backendStatus, onRefreshStatus, isCheckingStatus }) {
  return (
    <header className="border-b border-slate-200/80 dark:border-white/[0.08] bg-white/80 dark:bg-[#090A0F]/80 backdrop-blur-xl sticky top-0 z-10 shadow-xs">
      <div className="max-w-6xl mx-auto px-4 sm:px-6 py-3.5 flex flex-wrap items-center justify-between gap-3">
        <div className="flex items-center space-x-3">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-indigo-600 to-violet-500 text-white flex items-center justify-center font-black text-lg tracking-wider shadow-md shadow-indigo-500/25">
            ISL
          </div>
          <div>
            <h1 className="text-base sm:text-lg font-bold text-slate-900 dark:text-white leading-tight">
              Indian Sign Language Recognition
            </h1>
            <p className="text-xs text-slate-500 dark:text-slate-400 hidden sm:block">
              AI-Based 26-Class Alphabet Fingerspelling &bull; CNN V4 Active (86.3% Acc)
            </p>
          </div>
        </div>

        <StatusIndicator
          status={backendStatus}
          onRefresh={onRefreshStatus}
          isChecking={isCheckingStatus}
        />
      </div>
    </header>
  );
}