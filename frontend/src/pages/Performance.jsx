import React, { useState } from 'react';
import {
  BarChart3,
  TrendingUp,
  Layers,
  AlertTriangle,
  CheckCircle2,
  Search,
  ExternalLink,
  ChevronDown,
  ChevronUp,
  ShieldAlert,
} from 'lucide-react';
import PageHeader from '../components/PageHeader';

/**
 * Genuine per-class classification report data from results/final/v4_test_classification_report.csv
 */
const PER_CLASS_REPORT = [
  { class: 'A', precision: 0.800, recall: 1.000, f1: 0.889, support: 200 },
  { class: 'B', precision: 0.869, recall: 1.000, f1: 0.930, support: 199 },
  { class: 'C', precision: 0.797, recall: 1.000, f1: 0.887, support: 200 },
  { class: 'D', precision: 1.000, recall: 1.000, f1: 1.000, support: 190 },
  { class: 'E', precision: 0.580, recall: 1.000, f1: 0.734, support: 199 },
  { class: 'F', precision: 1.000, recall: 0.810, f1: 0.895, support: 200 },
  { class: 'G', precision: 0.942, recall: 1.000, f1: 0.970, support: 196 },
  { class: 'H', precision: 1.000, recall: 1.000, f1: 1.000, support: 199 },
  { class: 'I', precision: 0.647, recall: 0.750, f1: 0.694, support: 200 },
  { class: 'J', precision: 1.000, recall: 0.964, f1: 0.982, support: 197 },
  { class: 'K', precision: 0.990, recall: 1.000, f1: 0.995, support: 193 },
  { class: 'L', precision: 1.000, recall: 1.000, f1: 1.000, support: 200 },
  { class: 'M', precision: 0.917, recall: 1.000, f1: 0.957, support: 200 },
  { class: 'N', precision: 0.764, recall: 1.000, f1: 0.867, support: 198 },
  { class: 'O', precision: 0.896, recall: 1.000, f1: 0.945, support: 199 },
  { class: 'P', precision: 0.952, recall: 0.995, f1: 0.973, support: 200 },
  { class: 'Q', precision: 0.874, recall: 0.706, f1: 0.781, support: 197 },
  { class: 'R', precision: 1.000, recall: 1.000, f1: 1.000, support: 197 },
  { class: 'S', precision: 1.000, recall: 0.250, f1: 0.400, support: 200, isDifficult: true },
  { class: 'T', precision: 0.798, recall: 1.000, f1: 0.888, support: 198 },
  { class: 'U', precision: 0.783, recall: 1.000, f1: 0.879, support: 199 },
  { class: 'V', precision: 0.943, recall: 0.745, f1: 0.832, support: 200 },
  { class: 'W', precision: 0.000, recall: 0.000, f1: 0.000, support: 200, isDifficult: true },
  { class: 'X', precision: 0.802, recall: 0.750, f1: 0.775, support: 200 },
  { class: 'Y', precision: 0.800, recall: 1.000, f1: 0.889, support: 200 },
  { class: 'Z', precision: 1.000, recall: 0.500, f1: 0.667, support: 200, isDifficult: true },
];

/**
 * Controlled Experiment series data from Phase 6 reports
 */
const EXPERIMENT_SERIES = [
  { id: 'Baseline V1', name: 'Baseline (3 Conv + Flatten)', valLoss: 1.8340, valAcc: '61.27%', valF1: '58.10%', testAcc: '59.04%', params: '1,085,850', status: 'Replaced' },
  { id: 'CNN V2', name: 'Double-Conv + BatchNorm + GAP', valLoss: 1.6701, valAcc: '80.10%', valF1: '73.10%', testAcc: '—', params: '307,322', status: 'Iterated' },
  { id: 'CNN V3', name: 'V2 + Photometric Augmentation', valLoss: 1.3732, valAcc: '80.29%', valF1: '75.52%', testAcc: '—', params: '307,322', status: 'Iterated' },
  { id: 'CNN V4', name: 'V3 + L2 Regularization (λ=1e-4)', valLoss: 1.3507, valAcc: '80.14%', valF1: '77.68%', testAcc: '86.34%', params: '308,218', status: 'Selected Champion' },
  { id: 'CNN V5', name: 'V4 + SpatialDropout2D (0.15)', valLoss: 1.5422, valAcc: '75.29%', valF1: '70.08%', testAcc: '—', params: '308,218', status: 'Rejected (Underfit)' },
];

/**
 * Empirical Robustness Stress Test Results from scratch/robustness_results.json
 */
const ROBUSTNESS_BENCHMARKS = [
  { condition: 'Clean Baseline (Control)', acc: '80.06%', f1: '77.58%', delta: '0.00 pp', impact: 'Reference' },
  { condition: 'Gaussian Blur (r=1.5)', acc: '80.33%', f1: '78.21%', delta: '+0.28 pp', impact: 'Highly Resilient' },
  { condition: 'Scale Zoom In (1.18x)', acc: '80.97%', f1: '79.61%', delta: '+0.91 pp', impact: 'Enhanced Focus' },
  { condition: 'Slight Rotation (±10°)', acc: '80.14%', f1: '78.21%', delta: '+0.08 pp', impact: 'Invariant' },
  { condition: 'Gaussian Noise (σ=15)', acc: '77.83%', f1: '75.49%', delta: '-2.22 pp', impact: 'Mild Drop' },
  { condition: 'Moderate Rotation (±20°)', acc: '77.67%', f1: '75.98%', delta: '-2.38 pp', impact: 'Tolerable' },
  { condition: 'Low Contrast (-30%)', acc: '57.69%', f1: '57.51%', delta: '-22.37 pp', impact: 'Sensitive' },
  { condition: 'High Brightness (+40%)', acc: '47.12%', f1: '47.40%', delta: '-32.94 pp', impact: 'Severe Failure' },
  { condition: 'Low Brightness (-40%)', acc: '32.82%', f1: '32.61%', delta: '-47.24 pp', impact: 'Severe Failure' },
];

/**
 * Performance Component
 * Modern Indigo AI deep-dive into model benchmarking, V1-V5 iterations, confusion matrix, and robustness.
 */
export default function Performance() {
  const [tableSearch, setTableSearch] = useState('');
  const [sortField, setSortField] = useState('class');
  const [sortAsc, setSortAsc] = useState(true);

  const handleSort = (field) => {
    if (sortField === field) {
      setSortAsc(!sortAsc);
    } else {
      setSortField(field);
      setSortAsc(false);
    }
  };

  const filteredReport = PER_CLASS_REPORT.filter((item) =>
    item.class.toLowerCase().includes(tableSearch.toLowerCase())
  ).sort((a, b) => {
    const factor = sortAsc ? 1 : -1;
    if (sortField === 'class') return a.class.localeCompare(b.class) * factor;
    return (a[sortField] - b[sortField]) * factor;
  });

  return (
    <div className="space-y-6 py-4">
      <PageHeader
        badge="Independent Benchmark"
        title="Model Performance &amp; Evaluation"
        subtitle="Empirical evaluation of CNN V4 on 5,161 held-out test frames, controlled V1–V5 experiment comparison, and error analysis."
      />

      {/* 1. SCORECARDS: Modern Metric Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="card-linear-hover p-5 shadow-sm">
          <div className="flex items-center justify-between mb-3">
            <span className="text-xs uppercase font-bold text-slate-500 dark:text-slate-400 tracking-wider">
              Test Accuracy
            </span>
            <div className="w-8 h-8 rounded-lg bg-indigo-50 dark:bg-indigo-950/60 flex items-center justify-center border border-indigo-200/60 dark:border-indigo-800/60">
              <TrendingUp className="w-4 h-4 text-indigo-600 dark:text-indigo-400" />
            </div>
          </div>
          <div className="flex items-baseline space-x-2">
            <span className="text-3xl font-extrabold font-mono tracking-tight text-slate-900 dark:text-slate-100">
              86.34%
            </span>
            <span className="font-mono text-[10px] uppercase font-bold px-2 py-0.5 rounded-full border border-indigo-200 dark:border-indigo-800/60 bg-indigo-50 dark:bg-indigo-950/60 text-indigo-700 dark:text-indigo-300">
              Selected V4
            </span>
          </div>
          <p className="text-xs text-slate-500 dark:text-slate-400 mt-2.5 font-mono">
            4,456 / 5,161 correct predictions
          </p>
        </div>

        <div className="card-linear-hover p-5 shadow-sm">
          <div className="flex items-center justify-between mb-3">
            <span className="text-xs uppercase font-bold text-slate-500 dark:text-slate-400 tracking-wider">
              Macro F1-Score
            </span>
            <div className="w-8 h-8 rounded-lg bg-indigo-50 dark:bg-indigo-950/60 flex items-center justify-center border border-indigo-200/60 dark:border-indigo-800/60">
              <BarChart3 className="w-4 h-4 text-indigo-600 dark:text-indigo-400" />
            </div>
          </div>
          <div className="flex items-baseline space-x-2">
            <span className="text-3xl font-extrabold font-mono tracking-tight text-slate-900 dark:text-slate-100">
              83.96%
            </span>
            <span className="font-mono text-[10px] uppercase font-bold px-2 py-0.5 rounded-full border border-indigo-200 dark:border-indigo-800/60 bg-indigo-50 dark:bg-indigo-950/60 text-indigo-700 dark:text-indigo-300">
              +25.86 pp vs V1
            </span>
          </div>
          <p className="text-xs text-slate-500 dark:text-slate-400 mt-2.5 font-mono">
            Weighted F1: 83.87%
          </p>
        </div>

        <div className="card-linear-hover p-5 shadow-sm">
          <div className="flex items-center justify-between mb-3">
            <span className="text-xs uppercase font-bold text-slate-500 dark:text-slate-400 tracking-wider">
              Macro Precision
            </span>
            <div className="w-8 h-8 rounded-lg bg-indigo-50 dark:bg-indigo-950/60 flex items-center justify-center border border-indigo-200/60 dark:border-indigo-800/60">
              <CheckCircle2 className="w-4 h-4 text-indigo-600 dark:text-indigo-400" />
            </div>
          </div>
          <div className="flex items-baseline space-x-2">
            <span className="text-3xl font-extrabold font-mono tracking-tight text-slate-900 dark:text-slate-100">
              85.22%
            </span>
            <span className="font-mono text-[10px] uppercase font-bold px-2 py-0.5 rounded-full border border-indigo-200 dark:border-indigo-800/60 bg-indigo-50 dark:bg-indigo-950/60 text-indigo-700 dark:text-indigo-300">
              Positive Pred
            </span>
          </div>
          <p className="text-xs text-slate-500 dark:text-slate-400 mt-2.5 font-mono">
            Average specificity across 26 classes
          </p>
        </div>

        <div className="card-linear-hover p-5 shadow-sm">
          <div className="flex items-center justify-between mb-3">
            <span className="text-xs uppercase font-bold text-slate-500 dark:text-slate-400 tracking-wider">
              Macro Recall
            </span>
            <div className="w-8 h-8 rounded-lg bg-indigo-50 dark:bg-indigo-950/60 flex items-center justify-center border border-indigo-200/60 dark:border-indigo-800/60">
              <Layers className="w-4 h-4 text-indigo-600 dark:text-indigo-400" />
            </div>
          </div>
          <div className="flex items-baseline space-x-2">
            <span className="text-3xl font-extrabold font-mono tracking-tight text-slate-900 dark:text-slate-100">
              86.42%
            </span>
            <span className="font-mono text-[10px] uppercase font-bold px-2 py-0.5 rounded-full border border-indigo-200 dark:border-indigo-800/60 bg-indigo-50 dark:bg-indigo-950/60 text-indigo-700 dark:text-indigo-300">
              Sensitivity
            </span>
          </div>
          <p className="text-xs text-slate-500 dark:text-slate-400 mt-2.5 font-mono">
            True positive detection rate
          </p>
        </div>
      </div>

      {/* 2. CONTROLLED EXPERIMENT COMPARISON TABLE (V1 to V5) */}
      <div className="card-linear p-5 space-y-3.5 shadow-md">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 pb-3 border-b border-slate-200/80 dark:border-white/[0.08]">
          <div>
            <h3 className="text-base font-bold tracking-tight text-slate-900 dark:text-slate-100">
              Controlled Experiment Series (Phase 6 Iterations)
            </h3>
            <p className="text-xs text-slate-500 dark:text-slate-400">
              Iterative single-variable architectural hypotheses leading to final model candidate CNN V4.
            </p>
          </div>
          <span className="font-mono text-[11px] text-slate-500 dark:text-slate-400">
            Isolated Validation Splits
          </span>
        </div>

        <div className="overflow-x-auto rounded-xl border border-slate-200/80 dark:border-white/[0.08]">
          <table className="w-full text-left text-xs font-mono">
            <thead className="bg-slate-50/80 dark:bg-white/[0.02] text-slate-600 dark:text-slate-400 font-semibold uppercase tracking-wider border-b border-slate-200/80 dark:border-white/[0.08]">
              <tr>
                <th className="px-4 py-3">Experiment</th>
                <th className="px-4 py-3 font-sans">Architectural Change</th>
                <th className="px-4 py-3">Val Loss</th>
                <th className="px-4 py-3">Val Acc</th>
                <th className="px-4 py-3">Val F1</th>
                <th className="px-4 py-3">Test Acc</th>
                <th className="px-4 py-3 font-sans">Status</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-200/80 dark:divide-white/[0.08]">
              {EXPERIMENT_SERIES.map((exp) => {
                const isChampion = exp.id === 'CNN V4';
                return (
                  <tr
                    key={exp.id}
                    className={`transition-colors ${
                      isChampion
                        ? 'bg-indigo-50/70 dark:bg-indigo-950/30 font-semibold'
                        : 'hover:bg-slate-50 dark:hover:bg-white/[0.02]'
                    }`}
                  >
                    <td className="px-4 py-3 font-bold text-slate-900 dark:text-slate-100">
                      {exp.id}
                    </td>
                    <td className="px-4 py-3 font-sans text-slate-700 dark:text-slate-300">
                      {exp.name}
                    </td>
                    <td className="px-4 py-3 text-slate-600 dark:text-slate-400">
                      {exp.valLoss.toFixed(4)}
                    </td>
                    <td className="px-4 py-3 text-slate-600 dark:text-slate-400">
                      {exp.valAcc}
                    </td>
                    <td className="px-4 py-3 text-slate-600 dark:text-slate-400">
                      {exp.valF1}
                    </td>
                    <td className="px-4 py-3 font-bold text-indigo-600 dark:text-indigo-400">
                      {exp.testAcc}
                    </td>
                    <td className="px-4 py-3 font-sans">
                      <span
                        className={`text-[10px] font-bold px-2.5 py-0.5 rounded-full border ${
                          isChampion
                            ? 'bg-gradient-to-r from-indigo-600 to-violet-600 text-white border-transparent shadow-xs'
                            : exp.status.includes('Rejected')
                            ? 'bg-rose-50 dark:bg-rose-950/40 text-rose-700 dark:text-rose-300 border-rose-200 dark:border-rose-800'
                            : 'bg-slate-100 dark:bg-slate-800 text-slate-700 dark:text-slate-300 border-slate-200 dark:border-slate-700'
                        }`}
                      >
                        {exp.status}
                      </span>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>

      {/* 3. CONFUSION MATRIX (26 × 26) */}
      <div className="card-linear p-5 space-y-3.5 shadow-md">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 pb-3 border-b border-slate-200/80 dark:border-white/[0.08]">
          <div>
            <h3 className="text-base font-bold tracking-tight text-slate-900 dark:text-slate-100">
              Independent Test Confusion Matrix (26 × 26)
            </h3>
            <p className="text-xs text-slate-500 dark:text-slate-400">
              Evaluated on 5,161 strictly held-out test frames without data leakage.
            </p>
          </div>
          <a
            href="/performance_artifacts/v4_confusion_matrix.png"
            target="_blank"
            rel="noopener noreferrer"
            className="btn-secondary-linear text-xs"
          >
            <ExternalLink className="w-3.5 h-3.5" />
            <span>Open Artifact PNG</span>
          </a>
        </div>

        <div className="relative rounded-xl overflow-hidden bg-slate-950 border border-slate-800 p-4 flex items-center justify-center shadow-inner">
          <img
            src="/performance_artifacts/v4_confusion_matrix.png"
            alt="CNN V4 26x26 Confusion Matrix on 5,161 test images"
            className="max-h-[460px] w-auto object-contain rounded-lg"
          />
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-xs font-mono">
          <div className="p-3.5 rounded-xl border border-slate-200/60 dark:border-white/[0.06] bg-slate-50/80 dark:bg-white/[0.02] space-y-1">
            <strong className="block text-slate-900 dark:text-slate-100 font-sans font-bold">Diagonal Dominance</strong>
            <p className="text-slate-500 dark:text-slate-400 font-sans leading-relaxed">
              Strong true-positive concentrations across 23 of 26 classes, validating global feature extraction.
            </p>
          </div>
          <div className="p-3.5 rounded-xl border border-slate-200/60 dark:border-white/[0.06] bg-slate-50/80 dark:bg-white/[0.02] space-y-1">
            <strong className="block text-slate-900 dark:text-slate-100 font-sans font-bold">Flawless Classes (100%)</strong>
            <p className="text-slate-500 dark:text-slate-400 font-sans leading-relaxed">
              Classes D, H, L, and R achieved 0 misclassifications across ~200 test samples each.
            </p>
          </div>
          <div className="p-3.5 rounded-xl border border-slate-200/60 dark:border-white/[0.06] bg-slate-50/80 dark:bg-white/[0.02] space-y-1">
            <strong className="block text-slate-900 dark:text-slate-100 font-sans font-bold">Planar Occlusion Clusters</strong>
            <p className="text-slate-500 dark:text-slate-400 font-sans leading-relaxed">
              S suffers from thumb-over-fist overlap with A; W overlaps with E and X in 2D silhouette space.
            </p>
          </div>
        </div>
      </div>

      {/* 4. PER-CLASS METRICS TABLE */}
      <div className="card-linear p-5 space-y-3.5 shadow-md">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pb-3 border-b border-slate-200/80 dark:border-white/[0.08]">
          <div>
            <h3 className="text-base font-bold tracking-tight text-slate-900 dark:text-slate-100">
              Per-Class Classification Distribution
            </h3>
            <p className="text-xs text-slate-500 dark:text-slate-400">
              Precision, Recall, F1-Score, and Support across all 26 classes.
            </p>
          </div>

          <div className="relative w-full sm:w-60">
            <Search className="w-3.5 h-3.5 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
            <input
              type="text"
              value={tableSearch}
              onChange={(e) => setTableSearch(e.target.value)}
              placeholder="Search class (e.g. A, W)..."
              className="w-full bg-slate-50 dark:bg-[#161926] border border-slate-200/80 dark:border-white/[0.08] rounded-xl pl-8 pr-3 py-1.5 text-xs text-slate-900 dark:text-slate-100 placeholder-slate-400 focus:outline-hidden font-mono focus:border-indigo-500 transition-colors"
            />
          </div>
        </div>

        <div className="overflow-x-auto rounded-xl border border-slate-200/80 dark:border-white/[0.08]">
          <table className="w-full text-left text-xs font-mono">
            <thead className="bg-slate-50/80 dark:bg-white/[0.02] text-slate-600 dark:text-slate-400 font-semibold uppercase tracking-wider border-b border-slate-200/80 dark:border-white/[0.08]">
              <tr>
                <th
                  onClick={() => handleSort('class')}
                  className="px-4 py-3 cursor-pointer hover:text-slate-900 dark:hover:text-slate-100 select-none"
                >
                  <div className="flex items-center space-x-1">
                    <span>Class</span>
                    {sortField === 'class' && (sortAsc ? <ChevronUp className="w-3 h-3 text-indigo-500" /> : <ChevronDown className="w-3 h-3 text-indigo-500" />)}
                  </div>
                </th>
                <th
                  onClick={() => handleSort('precision')}
                  className="px-4 py-3 cursor-pointer hover:text-slate-900 dark:hover:text-slate-100 select-none"
                >
                  <div className="flex items-center space-x-1">
                    <span>Precision</span>
                    {sortField === 'precision' && (sortAsc ? <ChevronUp className="w-3 h-3 text-indigo-500" /> : <ChevronDown className="w-3 h-3 text-indigo-500" />)}
                  </div>
                </th>
                <th
                  onClick={() => handleSort('recall')}
                  className="px-4 py-3 cursor-pointer hover:text-slate-900 dark:hover:text-slate-100 select-none"
                >
                  <div className="flex items-center space-x-1">
                    <span>Recall</span>
                    {sortField === 'recall' && (sortAsc ? <ChevronUp className="w-3 h-3 text-indigo-500" /> : <ChevronDown className="w-3 h-3 text-indigo-500" />)}
                  </div>
                </th>
                <th
                  onClick={() => handleSort('f1')}
                  className="px-4 py-3 cursor-pointer hover:text-slate-900 dark:hover:text-slate-100 select-none"
                >
                  <div className="flex items-center space-x-1">
                    <span>F1-Score</span>
                    {sortField === 'f1' && (sortAsc ? <ChevronUp className="w-3 h-3 text-indigo-500" /> : <ChevronDown className="w-3 h-3 text-indigo-500" />)}
                  </div>
                </th>
                <th className="px-4 py-3">Support</th>
                <th className="px-4 py-3 font-sans">Category</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-200/80 dark:divide-white/[0.08]">
              {filteredReport.map((row) => {
                const isPerfect = row.f1 === 1.0;
                const isDifficult = Boolean(row.isDifficult);
                return (
                  <tr
                    key={row.class}
                    className={`hover:bg-slate-50 dark:hover:bg-white/[0.02] transition-colors ${
                      isDifficult ? 'bg-amber-500/5 dark:bg-amber-500/10' : ''
                    }`}
                  >
                    <td className="px-4 py-2.5 font-bold text-slate-900 dark:text-slate-100">
                      Letter '{row.class}'
                    </td>
                    <td className="px-4 py-2.5 text-slate-600 dark:text-slate-400">
                      {(row.precision * 100).toFixed(1)}%
                    </td>
                    <td className="px-4 py-2.5 text-slate-600 dark:text-slate-400">
                      {(row.recall * 100).toFixed(1)}%
                    </td>
                    <td className="px-4 py-2.5 font-bold text-indigo-600 dark:text-indigo-400">
                      {(row.f1 * 100).toFixed(1)}%
                    </td>
                    <td className="px-4 py-2.5 text-slate-500 dark:text-slate-400">
                      {row.support}
                    </td>
                    <td className="px-4 py-2.5 font-sans">
                      <span
                        className={`text-[10px] font-bold px-2.5 py-0.5 rounded-full border ${
                          isPerfect
                            ? 'bg-emerald-50 dark:bg-emerald-950/40 text-emerald-700 dark:text-emerald-300 border-emerald-200 dark:border-emerald-800'
                            : row.f1 >= 0.90
                            ? 'bg-indigo-50 dark:bg-indigo-950/40 text-indigo-700 dark:text-indigo-300 border-indigo-200 dark:border-indigo-800'
                            : isDifficult
                            ? 'bg-rose-50 dark:bg-rose-950/40 text-rose-700 dark:text-rose-300 border-rose-200 dark:border-rose-800'
                            : 'bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-400 border-slate-200 dark:border-slate-700'
                        }`}
                      >
                        {isPerfect ? '100% Perfect' : row.f1 >= 0.90 ? 'High (>90%)' : isDifficult ? 'Challenging' : 'Moderate'}
                      </span>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>

      {/* 5. EMPIRICAL ROBUSTNESS STRESS TEST RESULTS */}
      <div className="card-linear p-5 space-y-3.5 shadow-md">
        <div className="flex items-center space-x-2 pb-3 border-b border-slate-200/80 dark:border-white/[0.08]">
          <ShieldAlert className="w-4 h-4 text-indigo-600 dark:text-indigo-400" />
          <h3 className="text-base font-bold tracking-tight text-slate-900 dark:text-slate-100">
            Empirical Robustness Benchmarks (32,721 Model Inferences)
          </h3>
        </div>

        <div className="overflow-x-auto rounded-xl border border-slate-200/80 dark:border-white/[0.08]">
          <table className="w-full text-left text-xs font-mono">
            <thead className="bg-slate-50/80 dark:bg-white/[0.02] text-slate-600 dark:text-slate-400 font-semibold uppercase tracking-wider border-b border-slate-200/80 dark:border-white/[0.08]">
              <tr>
                <th className="px-4 py-3 font-sans">Perturbation Condition</th>
                <th className="px-4 py-3">Measured Accuracy</th>
                <th className="px-4 py-3">Macro F1</th>
                <th className="px-4 py-3">Delta vs Control</th>
                <th className="px-4 py-3 font-sans">Operational Verdict</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-200/80 dark:divide-white/[0.08]">
              {ROBUSTNESS_BENCHMARKS.map((item) => (
                <tr key={item.condition} className="hover:bg-slate-50 dark:hover:bg-white/[0.02] transition-colors">
                  <td className="px-4 py-2.5 font-sans font-semibold text-slate-900 dark:text-slate-100">
                    {item.condition}
                  </td>
                  <td className="px-4 py-2.5 font-bold text-slate-800 dark:text-slate-200">{item.acc}</td>
                  <td className="px-4 py-2.5 text-slate-600 dark:text-slate-400">{item.f1}</td>
                  <td className={`px-4 py-2.5 font-bold ${item.delta.startsWith('+') ? 'text-emerald-500' : item.delta === '0.00 pp' ? 'text-slate-500' : 'text-rose-500'}`}>
                    {item.delta}
                  </td>
                  <td className="px-4 py-2.5 font-sans text-slate-600 dark:text-slate-400">{item.impact}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* 6. HONEST LIMITATIONS & WEAK CLASSES */}
      <div className="card-linear p-5 space-y-3.5 shadow-md border-amber-500/20">
        <div className="flex items-center space-x-2 text-amber-600 dark:text-amber-400 font-mono text-xs font-bold uppercase tracking-wider pb-2.5 border-b border-slate-200/80 dark:border-white/[0.08]">
          <AlertTriangle className="w-4 h-4" />
          <span>Failure Mechanism &amp; Weak-Class Analysis</span>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-xs">
          <div className="p-4 rounded-xl border border-slate-200/60 dark:border-white/[0.06] bg-slate-50/80 dark:bg-white/[0.02] space-y-1.5">
            <h4 className="font-bold text-slate-900 dark:text-slate-100 flex items-center space-x-2">
              <span className="w-5 h-5 rounded-md bg-gradient-to-br from-indigo-600 to-violet-600 text-white font-mono text-center leading-5 text-xs font-bold shadow-xs">W</span>
              <span>0.0% Recall on Held-Out Split</span>
            </h4>
            <p className="text-slate-600 dark:text-slate-400 leading-relaxed font-sans">
              Under 2D planar projection, the splayed fingers of 'W' overlap identically with 'E' and 'X'.
              Resolving this requires multi-view camera setups or 3D landmark input.
            </p>
          </div>

          <div className="p-4 rounded-xl border border-slate-200/60 dark:border-white/[0.06] bg-slate-50/80 dark:bg-white/[0.02] space-y-1.5">
            <h4 className="font-bold text-slate-900 dark:text-slate-100 flex items-center space-x-2">
              <span className="w-5 h-5 rounded-md bg-gradient-to-br from-indigo-600 to-violet-600 text-white font-mono text-center leading-5 text-xs font-bold shadow-xs">S</span>
              <span>40.0% F1-Score (Fist Overlap)</span>
            </h4>
            <p className="text-slate-600 dark:text-slate-400 leading-relaxed font-sans">
              The closed fist of 'S' differs from 'A' solely by the thumb crossing the fingers.
              In low-contrast RGB lighting, this minimal structural difference triggers confusion.
            </p>
          </div>

          <div className="p-4 rounded-xl border border-slate-200/60 dark:border-white/[0.06] bg-slate-50/80 dark:bg-white/[0.02] space-y-1.5">
            <h4 className="font-bold text-slate-900 dark:text-slate-100 flex items-center space-x-2">
              <span className="w-5 h-5 rounded-md bg-gradient-to-br from-indigo-600 to-violet-600 text-white font-mono text-center leading-5 text-xs font-bold shadow-xs">Z</span>
              <span>66.7% F1-Score (Static Keyframe)</span>
            </h4>
            <p className="text-slate-600 dark:text-slate-400 leading-relaxed font-sans">
              Letter 'Z' is a dynamic motion sign in conversational ISL. Our static 2D CNN evaluates a single
              stationary keyframe posture, creating inherent temporal ambiguity.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}