import React from 'react';
import { Plus, AlertCircle, Clock, CheckCircle2, Layers, Sparkles } from 'lucide-react';

/**
 * PredictionResult Component
 * Displays CNN V4 model predictions, confidence metrics, and top-3 candidate distribution
 * using Modern Indigo AI (Linear & Cursor style) aesthetics.
 */
export default function PredictionResult({
  prediction,
  isPredicting,
  error,
  onAddLetterDirect,
}) {
  if (error) {
    return (
      <div className="card-linear p-6 flex flex-col items-center justify-center text-center h-full min-h-[360px] border-rose-500/20 shadow-lg">
        <div className="w-12 h-12 rounded-xl bg-rose-500/10 text-rose-600 dark:text-rose-400 flex items-center justify-center mb-3 border border-rose-500/20">
          <AlertCircle className="w-6 h-6" />
        </div>
        <h3 className="text-base font-bold text-slate-900 dark:text-white">
          Recognition Failed
        </h3>
        <p className="text-xs text-rose-600 dark:text-rose-400 mt-1 max-w-sm leading-relaxed">
          {error}
        </p>
        <p className="text-[11px] text-slate-400 mt-3 font-mono">
          Ensure hand gesture is clearly visible, well-lit, and centered in frame.
        </p>
      </div>
    );
  }

  if (isPredicting) {
    return (
      <div className="card-linear p-6 flex flex-col items-center justify-center text-center h-full min-h-[360px] shadow-lg">
        <div className="w-12 h-12 rounded-xl bg-indigo-50 dark:bg-indigo-950/60 text-indigo-600 dark:text-indigo-400 flex items-center justify-center mb-4 border border-indigo-200 dark:border-indigo-800/60">
          <div className="w-6 h-6 border-2 border-indigo-200 dark:border-indigo-800 border-t-indigo-600 dark:border-t-indigo-400 rounded-full animate-spin" />
        </div>
        <h3 className="text-base font-bold text-slate-900 dark:text-white">
          Evaluating Gesture...
        </h3>
        <p className="text-xs text-slate-500 dark:text-slate-400 mt-1 font-mono">
          Passing 128×128 tensor through CNN V4 model
        </p>
      </div>
    );
  }

  if (!prediction) {
    return (
      <div className="card-linear p-6 flex flex-col items-center justify-center text-center h-full min-h-[360px] text-slate-400 shadow-lg">
        <div className="w-12 h-12 rounded-xl bg-slate-100 dark:bg-white/[0.04] flex items-center justify-center mb-3 text-indigo-500 border border-slate-200/80 dark:border-white/[0.08]">
          <Sparkles className="w-5 h-5" />
        </div>
        <h3 className="text-sm font-bold text-slate-800 dark:text-slate-200">
          Awaiting Gesture Input
        </h3>
        <p className="text-xs text-slate-500 dark:text-slate-400 mt-1 max-w-xs leading-relaxed font-normal">
          Start the webcam or upload an image to trigger real-time ISL fingerspelling recognition.
        </p>
      </div>
    );
  }

  const confidencePct = (prediction.confidence * 100).toFixed(1);
  const predictedLetter = (prediction.predicted_letter || prediction.predicted_class || '').toUpperCase();

  return (
    <div className="card-linear p-6 flex flex-col h-full justify-between shadow-lg">
      <div>
        {/* Header Telemetry */}
        <div className="flex items-center justify-between pb-3 border-b border-slate-200/80 dark:border-white/[0.08]">
          <div className="flex items-center space-x-1.5">
            <span className="w-2.5 h-2.5 rounded-full bg-emerald-500 shadow-sm shadow-emerald-500/50 animate-pulse" />
            <span className="text-xs uppercase font-bold text-slate-800 dark:text-slate-200 tracking-wider">
              Prediction Output
            </span>
          </div>
          <span className="text-xs text-slate-500 dark:text-slate-400 font-mono flex items-center space-x-1">
            {prediction.inference_time_ms != null ? (
              <>
                <Clock className="w-3.5 h-3.5 text-slate-400" />
                <span>{prediction.inference_time_ms} ms</span>
              </>
            ) : (
              <>
                <CheckCircle2 className="w-3.5 h-3.5 text-emerald-500" />
                <span>Verified</span>
              </>
            )}
          </span>
        </div>

        {/* Hero Character Display */}
        <div className="my-6 text-center">
          <span className="text-[11px] uppercase tracking-wider text-slate-400 dark:text-slate-500 block mb-2 font-semibold">
            Recognized Alphabet
          </span>
          <div className="inline-flex items-center justify-center w-28 h-28 rounded-2xl bg-gradient-to-br from-indigo-600 via-indigo-600 to-violet-600 text-white font-extrabold text-7xl font-mono shadow-xl shadow-indigo-500/25 border border-indigo-400/30">
            {predictedLetter}
          </div>

          <div className="mt-3 flex items-center justify-center space-x-2">
            <span className="text-2xl font-bold font-mono tracking-tight text-slate-900 dark:text-white">
              {confidencePct}%
            </span>
            <span className="text-xs text-slate-500 dark:text-slate-400 font-mono">
              Confidence
            </span>
          </div>

          {/* Minimal Solid Confidence Rule */}
          <div className="mt-2 w-48 mx-auto bg-slate-100 dark:bg-white/[0.08] rounded-full h-1.5 overflow-hidden">
            <div
              className="bg-gradient-to-r from-indigo-600 to-violet-500 h-full rounded-full transition-all duration-300"
              style={{ width: `${Math.min(100, Math.max(5, prediction.confidence * 100))}%` }}
            />
          </div>

          {/* Quick Direct Add Button */}
          {onAddLetterDirect && (
            <div className="mt-4">
              <button
                type="button"
                onClick={() => onAddLetterDirect(predictedLetter)}
                className="btn-secondary-linear"
                title={`Add '${predictedLetter}' to Text Builder`}
              >
                <Plus className="w-3.5 h-3.5 text-indigo-500" />
                <span>Append '{predictedLetter}'</span>
              </button>
            </div>
          )}
        </div>

        {/* Top 3 Ranked Candidates */}
        {prediction.top_predictions && prediction.top_predictions.length > 0 && (
          <div className="mt-4 pt-4 border-t border-slate-200/80 dark:border-white/[0.08]">
            <div className="flex items-center justify-between mb-2">
              <h4 className="text-xs uppercase tracking-wider text-slate-700 dark:text-slate-300 font-bold flex items-center space-x-1">
                <Layers className="w-3.5 h-3.5 text-indigo-500" />
                <span>Top Candidates</span>
              </h4>
              <span className="text-[10px] text-slate-400 font-mono">Softmax Dist</span>
            </div>

            <div className="space-y-1.5">
              {prediction.top_predictions.map((candidate, idx) => {
                const candLetter = (candidate.letter || candidate.class || '').toUpperCase();
                const candPct = (candidate.confidence * 100).toFixed(1);
                const isTop = idx === 0;

                return (
                  <div
                    key={candLetter || idx}
                    className={`flex items-center justify-between px-3 py-2 rounded-xl border text-xs transition-colors ${
                      isTop
                        ? 'bg-indigo-50/80 dark:bg-indigo-950/40 border-indigo-200 dark:border-indigo-800/60 font-semibold text-slate-900 dark:text-white'
                        : 'bg-slate-50 dark:bg-white/[0.02] border-slate-200/80 dark:border-white/[0.06] text-slate-600 dark:text-slate-400'
                    }`}
                  >
                    <div className="flex items-center space-x-2">
                      <span className="font-mono text-[11px] text-slate-400 w-4">
                        #{idx + 1}
                      </span>
                      <span className="font-mono font-bold text-sm">'{candLetter}'</span>
                    </div>

                    <div className="flex items-center space-x-2">
                      <div className="w-20 bg-slate-200 dark:bg-white/[0.08] h-1.5 rounded-full overflow-hidden">
                        <div
                          className={`h-full ${isTop ? 'bg-gradient-to-r from-indigo-600 to-violet-500' : 'bg-slate-400 dark:bg-slate-600'}`}
                          style={{ width: `${candPct}%` }}
                        />
                      </div>
                      <span className="font-mono text-xs w-12 text-right">
                        {candPct}%
                      </span>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        )}
      </div>

      {/* Model Spec Micro-Footer */}
      <div className="mt-4 pt-3 border-t border-slate-200/80 dark:border-white/[0.08] font-mono text-[11px] text-slate-400 text-center">
        CNN V4 &bull; 86.34% Test Accuracy &bull; 308,218 Parameters
      </div>
    </div>
  );
}