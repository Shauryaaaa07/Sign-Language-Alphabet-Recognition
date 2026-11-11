import React from 'react';
import { RefreshCw } from 'lucide-react';

/**
 * StatusIndicator Component
 * Displays real-time FastAPI backend connectivity with sleek Modern Indigo AI pill badge.
 */
export default function StatusIndicator({ status, onRefresh, isChecking }) {
  const getBadgeStyle = () => {
    switch (status) {
      case 'connected':
        return {
          container: 'bg-emerald-50 dark:bg-emerald-950/40 border-emerald-200 dark:border-emerald-800 text-emerald-800 dark:text-emerald-300',
          dot: 'bg-emerald-500 shadow-xs shadow-emerald-500/50',
          label: 'Backend Online',
        };
      case 'disconnected':
        return {
          container: 'bg-rose-50 dark:bg-rose-950/40 border-rose-200 dark:border-rose-800 text-rose-800 dark:text-rose-300',
          dot: 'bg-rose-500 shadow-xs shadow-rose-500/50',
          label: 'Backend Offline',
        };
      case 'degraded':
        return {
          container: 'bg-amber-50 dark:bg-amber-950/40 border-amber-200 dark:border-amber-800 text-amber-800 dark:text-amber-300',
          dot: 'bg-amber-500 shadow-xs shadow-amber-500/50',
          label: 'Model Degraded',
        };
      case 'checking':
      default:
        return {
          container: 'bg-slate-100 dark:bg-slate-800 border-slate-300 dark:border-slate-700 text-slate-700 dark:text-slate-300',
          dot: 'bg-indigo-400 animate-pulse',
          label: 'Connecting...',
        };
    }
  };

  const style = getBadgeStyle();

  return (
    <div className="flex items-center space-x-2">
      <div
        className={`inline-flex items-center space-x-1.5 px-2.5 py-1 rounded-full border font-mono text-xs ${style.container}`}
        title={`FastAPI backend status: ${status}`}
      >
        <span className={`w-2 h-2 rounded-full ${style.dot}`} />
        <span className="font-semibold">{style.label}</span>
      </div>

      {onRefresh && (
        <button
          type="button"
          onClick={onRefresh}
          disabled={isChecking}
          title="Refresh backend status"
          className="p-1 rounded-lg text-slate-500 hover:text-slate-900 dark:hover:text-slate-100 hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors disabled:opacity-50"
        >
          <RefreshCw className={`w-3.5 h-3.5 ${isChecking ? 'animate-spin' : ''}`} />
        </button>
      )}
    </div>
  );
}