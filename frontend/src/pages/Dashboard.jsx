import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import {
  Cpu,
  ShieldCheck,
  BarChart3,
  Layers,
  ArrowRight,
  Camera,
  Server,
  RefreshCw,
  BookOpen,
  Activity,
  CheckCircle2,
} from 'lucide-react';
import PageHeader from '../components/PageHeader';
import { checkBackendHealth } from '../services/api';

/**
 * Dashboard Component
 * Modern Indigo AI analytics dashboard and system health telemetry for SignAI.
 */
export default function Dashboard({ backendStatus, onRefreshStatus, isCheckingStatus }) {
  const [healthData, setHealthData] = useState(null);

  useEffect(() => {
    checkBackendHealth().then((res) => {
      if (res.ok && res.data) {
        setHealthData(res.data);
      }
    });
  }, []);

  const isConnected = backendStatus === 'connected';

  const metrics = [
    {
      label: 'Independent Test Accuracy',
      value: '86.34%',
      badge: 'Held-out Split',
      subtitle: 'Evaluated on 5,161 clean test images (4,456 correct)',
      icon: ShieldCheck,
    },
    {
      label: 'Macro F1-Score',
      value: '83.96%',
      badge: 'Unweighted Mean',
      subtitle: 'Weighted F1: 83.87% | Macro Precision: 85.22%',
      icon: BarChart3,
    },
    {
      label: 'Alphabet Class Count',
      value: '26 Classes',
      badge: 'Full Scope',
      subtitle: 'A–Z fingerspelling poses without class reduction',
      icon: Layers,
    },
    {
      label: 'Model Parameters',
      value: '308,218',
      badge: 'CNN V4',
      subtitle: '307,322 trainable parameters with L2 regularization',
      icon: Cpu,
    },
  ];

  const pipelineStages = [
    {
      step: '01',
      title: 'Video Stream Capture',
      desc: 'HTML5 canvas crops centered 128×128 sRGB image buffer from webcam at 500ms intervals.',
    },
    {
      step: '02',
      title: 'Tensor Normalization',
      desc: 'FastAPI Pillow rasterization converts bytes into normalized [0.0, 1.0] float32 tensor.',
    },
    {
      step: '03',
      title: 'CNN V4 Deep Inference',
      desc: 'Three double-conv blocks with BatchNorm and GAP compute 26 Softmax class probabilities.',
    },
    {
      step: '04',
      title: 'Consensus & Speech',
      desc: '3-consecutive-frame sliding filter validates pose before vocalizing via Web Speech API.',
    },
  ];

  return (
    <div className="space-y-6 py-4">
      <PageHeader
        badge="System Telemetry"
        title="Project Dashboard"
        subtitle="Authoritative operational telemetry, backend connection health, and verified machine learning benchmarks."
        actions={
          <button
            type="button"
            onClick={onRefreshStatus}
            disabled={isCheckingStatus}
            className="btn-secondary-linear"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${isCheckingStatus ? 'animate-spin' : ''}`} />
            <span>Refresh Diagnostics</span>
          </button>
        }
      />

      {/* 1. KEY METRICS GRID: Balanced Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {metrics.map(({ label, value, badge, subtitle, icon: Icon }) => (
          <div
            key={label}
            className="card-linear-hover p-5 flex flex-col justify-between shadow-sm"
          >
            <div>
              <div className="flex items-center justify-between mb-3">
                <span className="text-xs uppercase font-bold text-slate-500 dark:text-slate-400 tracking-wider">
                  {label}
                </span>
                <div className="w-8 h-8 rounded-lg bg-indigo-50 dark:bg-indigo-950/60 text-indigo-600 dark:text-indigo-400 flex items-center justify-center border border-indigo-200/60 dark:border-indigo-800/60 shadow-xs">
                  <Icon className="w-4 h-4" />
                </div>
              </div>

              <div className="flex items-baseline space-x-2">
                <span className="text-3xl font-extrabold font-mono tracking-tight text-slate-900 dark:text-white">
                  {value}
                </span>
                <span className="font-mono text-[10px] uppercase font-bold px-2 py-0.5 rounded-full border border-indigo-200 dark:border-indigo-800/60 bg-indigo-50 dark:bg-indigo-950/60 text-indigo-700 dark:text-indigo-300">
                  {badge}
                </span>
              </div>
            </div>

            <p className="text-xs text-slate-500 dark:text-slate-400 mt-3 pt-2.5 border-t border-slate-200/60 dark:border-white/[0.06] leading-relaxed">
              {subtitle}
            </p>
          </div>
        ))}
      </div>

      {/* 2. SYSTEM HEALTH CARDS: Backend API & CNN Model */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-5 items-stretch">
        {/* Card 1: Backend API Health */}
        <div className="card-linear p-5 flex flex-col justify-between shadow-md">
          <div>
            <div className="flex items-center justify-between pb-3 border-b border-slate-200/80 dark:border-white/[0.08] mb-3">
              <div className="flex items-center space-x-2.5">
                <div className="w-8 h-8 rounded-lg bg-indigo-50 dark:bg-indigo-950/60 text-indigo-600 dark:text-indigo-400 flex items-center justify-center border border-indigo-200/60 dark:border-indigo-800/60">
                  <Server className="w-4 h-4" />
                </div>
                <div>
                  <h3 className="text-sm font-bold tracking-tight text-slate-900 dark:text-white">
                    FastAPI Microservice
                  </h3>
                  <span className="font-mono text-[11px] text-slate-500">http://127.0.0.1:8000</span>
                </div>
              </div>

              <span
                className={`inline-flex items-center space-x-1.5 px-2.5 py-1 rounded-full font-mono text-xs font-semibold border ${
                  isConnected
                    ? 'bg-emerald-50 dark:bg-emerald-950/40 text-emerald-800 dark:text-emerald-300 border-emerald-200 dark:border-emerald-800'
                    : 'bg-rose-50 dark:bg-rose-950/40 text-rose-800 dark:text-rose-300 border-rose-200 dark:border-rose-800'
                }`}
              >
                <span className={`w-2 h-2 rounded-full ${isConnected ? 'bg-emerald-500' : 'bg-rose-500'} animate-pulse`} />
                <span>{isConnected ? 'Connected' : 'Offline'}</span>
              </span>
            </div>

            <div className="space-y-2 text-xs font-mono">
              <div className="flex items-center justify-between p-2.5 rounded-xl bg-slate-50/80 dark:bg-white/[0.02] border border-slate-200/60 dark:border-white/[0.06]">
                <span className="text-slate-500 dark:text-slate-400">Health Endpoint</span>
                <span className="font-semibold text-slate-900 dark:text-white">GET /health</span>
              </div>
              <div className="flex items-center justify-between p-2.5 rounded-xl bg-slate-50/80 dark:bg-white/[0.02] border border-slate-200/60 dark:border-white/[0.06]">
                <span className="text-slate-500 dark:text-slate-400">Prediction Endpoint</span>
                <span className="font-semibold text-slate-900 dark:text-white">POST /predict</span>
              </div>
              <div className="flex items-center justify-between p-2.5 rounded-xl bg-slate-50/80 dark:bg-white/[0.02] border border-slate-200/60 dark:border-white/[0.06]">
                <span className="text-slate-500 dark:text-slate-400">Payload Boundary</span>
                <span className="font-semibold text-slate-900 dark:text-white">10 MB Max (Multipart/Base64)</span>
              </div>
            </div>
          </div>

          <div className="pt-3 border-t border-slate-200/80 dark:border-white/[0.08] mt-3 flex items-center justify-between font-mono text-[11px] text-slate-500 dark:text-slate-400">
            <span>FastAPI + Uvicorn Async Core</span>
            <span className="text-emerald-600 dark:text-emerald-400 font-semibold">CORS Permitted</span>
          </div>
        </div>

        {/* Card 2: CNN Model Health */}
        <div className="card-linear p-5 flex flex-col justify-between shadow-md">
          <div>
            <div className="flex items-center justify-between pb-3 border-b border-slate-200/80 dark:border-white/[0.08] mb-3">
              <div className="flex items-center space-x-2.5">
                <div className="w-8 h-8 rounded-lg bg-indigo-50 dark:bg-indigo-950/60 text-indigo-600 dark:text-indigo-400 flex items-center justify-center border border-indigo-200/60 dark:border-indigo-800/60">
                  <Cpu className="w-4 h-4" />
                </div>
                <div>
                  <h3 className="text-sm font-bold tracking-tight text-slate-900 dark:text-white">
                    CNN V4 Checkpoint
                  </h3>
                  <span className="font-mono text-[11px] text-slate-500">Keras In-Memory Model</span>
                </div>
              </div>

              <span className="inline-flex items-center space-x-1.5 px-2.5 py-1 rounded-full font-mono text-xs font-semibold bg-indigo-50 dark:bg-indigo-950/40 text-indigo-700 dark:text-indigo-300 border border-indigo-200 dark:border-indigo-800/60">
                <CheckCircle2 className="w-3.5 h-3.5 text-emerald-500" />
                <span>Active Lifespan</span>
              </span>
            </div>

            <div className="space-y-2 text-xs font-mono">
              <div className="flex items-center justify-between p-2.5 rounded-xl bg-slate-50/80 dark:bg-white/[0.02] border border-slate-200/60 dark:border-white/[0.06]">
                <span className="text-slate-500 dark:text-slate-400">Checkpoint File</span>
                <span className="text-[11px] text-slate-900 dark:text-white truncate max-w-[210px]">
                  {healthData?.model_name || 'isl_alphabet_cnn_v4_best.keras'}
                </span>
              </div>
              <div className="flex items-center justify-between p-2.5 rounded-xl bg-slate-50/80 dark:bg-white/[0.02] border border-slate-200/60 dark:border-white/[0.06]">
                <span className="text-slate-500 dark:text-slate-400">Input Specification</span>
                <span className="font-semibold text-slate-900 dark:text-white">128 × 128 × 3 sRGB</span>
              </div>
              <div className="flex items-center justify-between p-2.5 rounded-xl bg-slate-50/80 dark:bg-white/[0.02] border border-slate-200/60 dark:border-white/[0.06]">
                <span className="text-slate-500 dark:text-slate-400">Softmax Classes</span>
                <span className="font-semibold text-slate-900 dark:text-white">26 Output Neurons</span>
              </div>
            </div>
          </div>

          <div className="pt-3 border-t border-slate-200/80 dark:border-white/[0.08] mt-3 flex items-center justify-between font-mono text-[11px] text-slate-500 dark:text-slate-400">
            <span>TensorFlow 2.16 / Keras 3</span>
            <span className="text-indigo-600 dark:text-indigo-400 font-semibold">Zero Retraining Guard</span>
          </div>
        </div>
      </div>

      {/* 3. SYSTEM PIPELINE: Structured Flow */}
      <div className="card-linear p-5 space-y-3.5 shadow-md">
        <div className="flex items-center space-x-2.5 pb-3 border-b border-slate-200/80 dark:border-white/[0.08]">
          <Activity className="w-4 h-4 text-indigo-600 dark:text-indigo-400" />
          <h3 className="text-base font-bold tracking-tight text-slate-900 dark:text-white">
            Four-Stage Decoupled Pipeline
          </h3>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-4 gap-3.5">
          {pipelineStages.map(({ step, title, desc }) => (
            <div
              key={step}
              className="p-4 rounded-xl border border-slate-200/80 dark:border-white/[0.08] bg-slate-50/80 dark:bg-white/[0.02] space-y-1.5"
            >
              <span className="text-xs font-bold text-white bg-gradient-to-r from-indigo-600 to-violet-600 px-2 py-0.5 rounded-md inline-block shadow-xs">
                Stage {step}
              </span>
              <h4 className="text-sm font-bold text-slate-900 dark:text-white pt-1">{title}</h4>
              <p className="text-xs text-slate-600 dark:text-slate-400 leading-relaxed font-normal">
                {desc}
              </p>
            </div>
          ))}
        </div>
      </div>

      {/* 4. SHORTCUT NAVIGATION */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        <Link
          to="/studio"
          className="card-linear-hover p-4 flex items-center justify-between group shadow-sm"
        >
          <div className="flex items-center space-x-3">
            <div className="w-9 h-9 rounded-xl bg-gradient-to-br from-indigo-600 to-violet-600 text-white flex items-center justify-center shadow-md shadow-indigo-500/20 group-hover:scale-105 transition-transform">
              <Camera className="w-4 h-4" />
            </div>
            <div>
              <h4 className="text-sm font-bold text-slate-900 dark:text-white">Recognition Studio</h4>
              <p className="text-xs text-slate-500 dark:text-slate-400">Live webcam &amp; upload engine</p>
            </div>
          </div>
          <ArrowRight className="w-4 h-4 text-slate-400 group-hover:text-indigo-500 group-hover:translate-x-0.5 transition-all" />
        </Link>

        <Link
          to="/learn"
          className="card-linear-hover p-4 flex items-center justify-between group shadow-sm"
        >
          <div className="flex items-center space-x-3">
            <div className="w-9 h-9 rounded-xl bg-gradient-to-br from-indigo-600 to-violet-600 text-white flex items-center justify-center shadow-md shadow-indigo-500/20 group-hover:scale-105 transition-transform">
              <BookOpen className="w-4 h-4" />
            </div>
            <div>
              <h4 className="text-sm font-bold text-slate-900 dark:text-white">Alphabet Library</h4>
              <p className="text-xs text-slate-500 dark:text-slate-400">26 reference hand gestures</p>
            </div>
          </div>
          <ArrowRight className="w-4 h-4 text-slate-400 group-hover:text-indigo-500 group-hover:translate-x-0.5 transition-all" />
        </Link>

        <Link
          to="/performance"
          className="card-linear-hover p-4 flex items-center justify-between group shadow-sm"
        >
          <div className="flex items-center space-x-3">
            <div className="w-9 h-9 rounded-xl bg-gradient-to-br from-indigo-600 to-violet-600 text-white flex items-center justify-center shadow-md shadow-indigo-500/20 group-hover:scale-105 transition-transform">
              <BarChart3 className="w-4 h-4" />
            </div>
            <div>
              <h4 className="text-sm font-bold text-slate-900 dark:text-white">Benchmark Reports</h4>
              <p className="text-xs text-slate-500 dark:text-slate-400">V1–V5 experiment comparison</p>
            </div>
          </div>
          <ArrowRight className="w-4 h-4 text-slate-400 group-hover:text-indigo-500 group-hover:translate-x-0.5 transition-all" />
        </Link>
      </div>
    </div>
  );
}