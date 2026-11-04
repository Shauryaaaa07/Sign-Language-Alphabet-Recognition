import React from 'react';
import { Sun, Moon, Laptop } from 'lucide-react';
import { useTheme } from '../context/useTheme';

/**
 * ThemeSwitcher Component
 * Modern Indigo AI segmented control enabling users to toggle between Light, Dark, and System theme modes.
 */
export default function ThemeSwitcher() {
  const { theme, setTheme } = useTheme();

  const options = [
    { value: 'light', label: 'Light', icon: Sun },
    { value: 'dark', label: 'Dark', icon: Moon },
    { value: 'system', label: 'Auto', icon: Laptop },
  ];

  return (
    <div
      role="radiogroup"
      aria-label="Theme preference selector"
      className="inline-flex items-center p-1 rounded-full bg-slate-100/90 dark:bg-[#161926]/90 border border-slate-200/80 dark:border-white/[0.08] shadow-xs"
    >
      {options.map(({ value, label, icon: Icon }) => {
        const isActive = theme === value;
        return (
          <button
            key={value}
            type="button"
            role="radio"
            aria-checked={isActive}
            onClick={() => setTheme(value)}
            title={`Switch to ${label} theme`}
            className={`flex items-center space-x-1 px-2.5 py-1 rounded-full text-xs font-medium transition-all ${
              isActive
                ? 'bg-white dark:bg-white/[0.1] text-slate-900 dark:text-white font-semibold shadow-xs'
                : 'text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white'
            }`}
          >
            <Icon className="w-3.5 h-3.5" />
            <span className="hidden sm:inline text-[11px] font-mono">{label}</span>
          </button>
        );
      })}
    </div>
  );
}