import React, { useState } from 'react';
import { NavLink, Link } from 'react-router-dom';
import {
  Camera,
  Menu,
  X,
  RefreshCw,
  Hand,
} from 'lucide-react';
import ThemeSwitcher from './ThemeSwitcher';

/**
 * Navbar Component
 * Authentic, clean modern navigation header with subtle borders and clear hierarchy.
 */
export default function Navbar({ backendStatus, onRefreshStatus, isCheckingStatus }) {
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  const navigationLinks = [
    { to: '/', label: 'Overview' },
    { to: '/studio', label: 'Studio', highlight: true },
    { to: '/learn', label: 'Alphabet A–Z' },
    { to: '/dashboard', label: 'Dashboard' },
    { to: '/performance', label: 'Benchmarks' },
    { to: '/about', label: 'Architecture' },
  ];

  const getStatusIndicator = () => {
    switch (backendStatus) {
      case 'connected':
        return {
          dotClass: 'bg-emerald-400 shadow-[0_0_8px_rgba(52,211,153,0.7)]',
          textClass: 'text-emerald-700 dark:text-emerald-300',
          bgClass: 'bg-emerald-500/10 border-emerald-500/25',
          label: 'CNN V4 Online',
        };
      case 'degraded':
        return {
          dotClass: 'bg-amber-400 shadow-[0_0_8px_rgba(251,191,36,0.7)]',
          textClass: 'text-amber-700 dark:text-amber-300',
          bgClass: 'bg-amber-500/10 border-amber-500/25',
          label: 'Degraded',
        };
      case 'disconnected':
        return {
          dotClass: 'bg-rose-400 shadow-[0_0_8px_rgba(244,63,94,0.7)]',
          textClass: 'text-rose-700 dark:text-rose-300',
          bgClass: 'bg-rose-500/10 border-rose-500/25',
          label: 'API Offline',
        };
      case 'checking':
      default:
        return {
          dotClass: 'bg-slate-400 animate-pulse',
          textClass: 'text-slate-600 dark:text-slate-400',
          bgClass: 'bg-slate-500/10 border-slate-500/20',
          label: 'Connecting...',
        };
    }
  };

  const status = getStatusIndicator();

  return (
    <nav className="sticky top-0 z-50 bg-white/80 dark:bg-[#090A0F]/80 backdrop-blur-xl border-b border-slate-200/80 dark:border-white/[0.08] transition-colors">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          {/* Brand Identity */}
          <div className="flex items-center space-x-8">
            <Link
              to="/"
              className="flex items-center space-x-2.5 group focus:outline-hidden"
              aria-label="SignAI Home"
            >
              <div className="w-8 h-8 rounded-xl bg-gradient-to-tr from-indigo-600 via-indigo-600 to-violet-500 text-white flex items-center justify-center font-bold text-sm shadow-md shadow-indigo-500/25 group-hover:scale-105 transition-all">
                <Hand className="w-4 h-4" />
              </div>
              <div className="flex items-baseline space-x-2">
                <span className="font-extrabold text-lg tracking-tight text-slate-900 dark:text-white">
                  Sign<span className="bg-gradient-to-r from-indigo-500 to-violet-400 bg-clip-text text-transparent">AI</span>
                </span>
                <span className="hidden sm:inline-flex items-center px-2 py-0.5 rounded-full text-[10px] font-mono font-medium bg-indigo-500/10 text-indigo-600 dark:text-indigo-400 border border-indigo-500/20">
                  ISL 26-Class
                </span>
              </div>
            </Link>

            {/* Desktop Navigation Links */}
            <div className="hidden lg:flex items-center space-x-1">
              {navigationLinks.map(({ to, label, highlight }) => (
                <NavLink
                  key={to}
                  to={to}
                  end={to === '/'}
                  className={({ isActive }) =>
                    `px-3 py-1.5 rounded-lg text-xs font-medium transition-all ${
                      isActive
                        ? 'bg-slate-100 dark:bg-white/[0.08] text-slate-900 dark:text-white font-semibold shadow-xs'
                        : highlight
                        ? 'text-indigo-600 dark:text-indigo-400 hover:bg-indigo-50 dark:hover:bg-indigo-500/10 font-semibold'
                        : 'text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white hover:bg-slate-100/60 dark:hover:bg-white/[0.04]'
                    }`
                  }
                >
                  {label}
                </NavLink>
              ))}
            </div>
          </div>

          {/* Right Header Utility Controls */}
          <div className="hidden sm:flex items-center space-x-3">
            {/* Status Indicator */}
            <div
              className={`inline-flex items-center space-x-1.5 px-3 py-1 rounded-full border text-xs font-mono font-medium ${status.bgClass} ${status.textClass}`}
              title={`FastAPI backend status: ${backendStatus}`}
            >
              <span className={`w-2 h-2 rounded-full ${status.dotClass}`} />
              <span>{status.label}</span>
              {onRefreshStatus && (
                <button
                  type="button"
                  onClick={onRefreshStatus}
                  disabled={isCheckingStatus}
                  aria-label="Refresh backend status"
                  className="ml-1 hover:opacity-75 focus:outline-hidden disabled:opacity-50"
                >
                  <RefreshCw className={`w-3 h-3 ${isCheckingStatus ? 'animate-spin' : ''}`} />
                </button>
              )}
            </div>

            {/* Studio Action Quick Button */}
            <Link to="/studio" className="btn-indigo text-xs py-1.5 px-3.5">
              <Camera className="w-3.5 h-3.5" />
              <span>Launch Studio</span>
            </Link>

            {/* Theme Selector */}
            <ThemeSwitcher />
          </div>

          {/* Mobile Menu Toggle Button */}
          <div className="flex sm:hidden items-center space-x-2">
            <ThemeSwitcher />
            <button
              type="button"
              onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
              aria-label="Toggle navigation menu"
              className="p-2 rounded-lg text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white hover:bg-slate-100 dark:hover:bg-slate-800 focus:outline-hidden"
            >
              {mobileMenuOpen ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
            </button>
          </div>
        </div>
      </div>

      {/* Mobile Menu Drawer */}
      {mobileMenuOpen && (
        <div className="sm:hidden border-b border-slate-200/80 dark:border-white/[0.08] bg-white dark:bg-[#090A0F] px-4 pt-3 pb-5 space-y-2">
          {navigationLinks.map(({ to, label }) => (
            <NavLink
              key={to}
              to={to}
              end={to === '/'}
              onClick={() => setMobileMenuOpen(false)}
              className={({ isActive }) =>
                `block px-3.5 py-2.5 rounded-lg text-sm font-medium transition-colors ${
                  isActive
                    ? 'bg-slate-100 dark:bg-white/[0.08] text-slate-900 dark:text-white font-semibold'
                    : 'text-slate-600 dark:text-slate-400 hover:bg-slate-50 dark:hover:bg-slate-800'
                }`
              }
            >
              {label}
            </NavLink>
          ))}

          <div className="pt-3 border-t border-slate-200/80 dark:border-white/[0.08] flex items-center justify-between">
            <div
              className={`inline-flex items-center space-x-1.5 px-3 py-1 rounded-full border text-xs font-mono font-medium ${status.bgClass} ${status.textClass}`}
            >
              <span className={`w-2 h-2 rounded-full ${status.dotClass}`} />
              <span>{status.label}</span>
            </div>

            <Link
              to="/studio"
              onClick={() => setMobileMenuOpen(false)}
              className="btn-indigo text-xs py-1.5 px-3"
            >
              <Camera className="w-3.5 h-3.5" />
              <span>Launch Studio</span>
            </Link>
          </div>
        </div>
      )}
    </nav>
  );
}