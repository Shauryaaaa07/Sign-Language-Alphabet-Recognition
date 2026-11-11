import React from 'react';
import { Link } from 'react-router-dom';
import { ShieldCheck, Cpu, Hand } from 'lucide-react';

/**
 * Footer Component
 * Modern Indigo AI platform footer with navigation links, tech stack details, and research provenance.
 */
export default function Footer() {
  return (
    <footer className="border-t border-slate-200/80 dark:border-white/[0.08] bg-white/70 dark:bg-[#090A0F]/80 backdrop-blur-xl transition-colors mt-auto">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 sm:py-10">
        <div className="grid grid-cols-1 md:grid-cols-12 gap-8 pb-8 border-b border-slate-200/80 dark:border-white/[0.08]">
          {/* Brand & Mission (5 cols) */}
          <div className="md:col-span-5 space-y-3.5">
            <div className="flex items-center space-x-2.5">
              <div className="w-8 h-8 rounded-xl bg-gradient-to-tr from-indigo-600 to-violet-500 text-white flex items-center justify-center font-bold text-xs shadow-md shadow-indigo-500/25">
                <Hand className="w-4 h-4" />
              </div>
              <span className="font-extrabold text-base tracking-tight text-slate-900 dark:text-white">
                Sign<span className="bg-gradient-to-r from-indigo-500 to-violet-400 bg-clip-text text-transparent">AI</span>
              </span>
              <span className="text-[10px] font-bold uppercase tracking-wider px-2 py-0.5 rounded-full border border-indigo-200 dark:border-indigo-800/60 bg-indigo-50 dark:bg-indigo-950/60 text-indigo-700 dark:text-indigo-300">
                A–Z Alphabet
              </span>
            </div>
            <p className="text-sm font-bold text-slate-900 dark:text-slate-100">
              Your Hands. Your Voice.
            </p>
            <p className="text-xs text-slate-600 dark:text-slate-400 leading-relaxed max-w-sm font-normal">
              An educational accessibility web platform recognizing Indian Sign Language (ISL) fingerspelling poses
              across 26 alphabet classes, assembling words with live stabilization, and converting recognized signs into spoken English.
            </p>
            <div className="flex items-center space-x-3 pt-1 font-mono text-[11px] text-slate-500 dark:text-slate-400">
              <span className="flex items-center space-x-1">
                <Cpu className="w-3.5 h-3.5 text-indigo-500" />
                <span>308k Parameters</span>
              </span>
              <span>/</span>
              <span className="flex items-center space-x-1">
                <ShieldCheck className="w-3.5 h-3.5 text-emerald-500" />
                <span>86.34% Test Accuracy</span>
              </span>
            </div>
          </div>

          {/* Navigation Links (3 cols) */}
          <div className="md:col-span-3 space-y-3">
            <h4 className="text-xs uppercase font-bold tracking-wider text-slate-900 dark:text-white">
              Navigation
            </h4>
            <ul className="space-y-2 text-xs text-slate-600 dark:text-slate-400">
              <li>
                <Link to="/" className="hover:text-indigo-600 dark:hover:text-indigo-400 transition-colors">
                  Overview
                </Link>
              </li>
              <li>
                <Link to="/studio" className="font-semibold text-indigo-600 dark:text-indigo-400 hover:underline">
                  Recognition Studio
                </Link>
              </li>
              <li>
                <Link to="/learn" className="hover:text-indigo-600 dark:hover:text-indigo-400 transition-colors">
                  Alphabet Library (A–Z)
                </Link>
              </li>
              <li>
                <Link to="/dashboard" className="hover:text-indigo-600 dark:hover:text-indigo-400 transition-colors">
                  System Health &amp; Telemetry
                </Link>
              </li>
              <li>
                <Link to="/performance" className="hover:text-indigo-600 dark:hover:text-indigo-400 transition-colors">
                  Benchmark Reports
                </Link>
              </li>
              <li>
                <Link to="/about" className="hover:text-indigo-600 dark:hover:text-indigo-400 transition-colors">
                  Technical Architecture
                </Link>
              </li>
            </ul>
          </div>

          {/* Research & Data Hygiene (4 cols) */}
          <div className="md:col-span-4 space-y-3">
            <h4 className="text-xs uppercase font-bold tracking-wider text-slate-900 dark:text-white">
              Research &amp; Open Standards
            </h4>
            <p className="text-xs text-slate-600 dark:text-slate-400 leading-relaxed font-normal">
              Engineered with FastAPI, TensorFlow 2.16, and React 19. Designed with complete disclosure of monocular 2D limits
              and static keyframe approximations for dynamic gestures.
            </p>
            <div className="pt-2 font-mono text-[11px] text-slate-500 dark:text-slate-400 space-y-1">
              <div>Dataset: RealSign ISL (CC0 1.0 Public Domain)</div>
              <div>Independent Test Split: 5,161 held-out images</div>
            </div>
          </div>
        </div>

        {/* Bottom Bar: Copyright & Standards */}
        <div className="pt-6 flex flex-col sm:flex-row items-center justify-between text-xs text-slate-500 dark:text-slate-400 font-mono">
          <div>
            &copy; 2026 SignAI. Open Academic Research &amp; Accessibility Platform.
          </div>
          <div className="mt-3 sm:mt-0 flex items-center space-x-3">
            <span>26 Classes (A–Z)</span>
            <span>&bull;</span>
            <span>Local Inference</span>
            <span>&bull;</span>
            <span>Zero Remote Telemetry</span>
          </div>
        </div>
      </div>
    </footer>
  );
}