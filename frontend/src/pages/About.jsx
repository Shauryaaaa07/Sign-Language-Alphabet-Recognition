import React from 'react';
import {
  Heart,
  Cpu,
  Layers,
  Globe,
  Terminal,
  Code2,
  Database,
  Compass,
  ArrowRight,
  AlertTriangle,
} from 'lucide-react';
import PageHeader from '../components/PageHeader';

/**
 * About Component
 * Technical architecture and project presentation page for SignAI in Modern Indigo AI style.
 * Covers problem formulation, objectives, three-tier architecture, tech stack,
 * dataset provenance, CNN V4 specifications, and honest boundaries.
 */
export default function About() {
  const objectives = [
    {
      num: '01',
      title: 'Monocular 2D Recognition',
      desc: 'Classify static Indian Sign Language (ISL) fingerspelling alphabet hand poses (A–Z) from single webcam frames with high confidence and sub-120ms latency.',
    },
    {
      num: '02',
      title: 'Temporal Stabilization',
      desc: 'Filter transitory motion jitter through a client-side 3-consecutive-frame consensus buffer requiring ≥ 75% confidence before committing letters.',
    },
    {
      num: '03',
      title: 'Multimodal Vocalization',
      desc: 'Convert assembled alphabet words into clear, audible English audio via browser-native SpeechSynthesis, closing the communication loop for hearing listeners.',
    },
  ];

  const techStack = [
    { name: 'React 19', role: 'Frontend Presentation', desc: 'Component architecture with Tailwind CSS 4, Linear/Cursor design tokens, and smooth reactive state.' },
    { name: 'FastAPI', role: 'Inference Microservice', desc: 'Asynchronous Python web server with single-instance lifespan model caching and strict schema validation.' },
    { name: 'TensorFlow & Keras 3', role: 'Deep Learning Core', desc: 'CNN V4 architecture featuring Double-Conv blocks, Batch Normalization, GAP, and L2 regularization.' },
    { name: 'Pillow & OpenCV', role: 'Image Preprocessing', desc: 'Safe binary rasterization, aspect-ratio preservation, bilinear resampling, and [0, 1] normalization.' },
    { name: 'Web Speech API', role: 'Voice Synthesis', desc: 'W3C browser-native speech synthesis with automated local voice discovery and zero cloud subscription fees.' },
    { name: 'Node.js & Vite 8', role: 'Tooling & Testing', desc: 'High-speed HMR development server, Rollup static compilation, and zero-dependency unit test runners.' },
  ];

  return (
    <div className="space-y-6 py-4 max-w-5xl mx-auto">
      <PageHeader
        badge="Academic Project Architecture"
        title="About SignAI Platform"
        subtitle="Indian Sign Language Alphabet Recognition and Speech Synthesis System."
      />

      {/* 1. PROBLEM STATEMENT */}
      <section className="card-linear p-5 sm:p-6 space-y-3 shadow-md">
        <div className="flex items-center space-x-2.5 pb-3 border-b border-slate-200/80 dark:border-white/[0.08]">
          <Heart className="w-4 h-4 text-rose-500" />
          <h2 className="text-base font-bold tracking-tight text-slate-900 dark:text-slate-100">
            Problem Statement &amp; Societal Significance
          </h2>
        </div>

        <p className="text-xs sm:text-sm text-slate-700 dark:text-slate-300 leading-relaxed font-normal">
          Over <strong>18 million individuals</strong> in India live with hearing and speech impairments, relying on Indian Sign
          Language (ISL) as their principal medium of communication and expression. However, the overwhelming majority of hearing citizens
          do not comprehend ISL, and certified interpreters remain severely scarce across schools, healthcare clinics, and civic institutions.
        </p>

        <p className="text-xs sm:text-sm text-slate-700 dark:text-slate-300 leading-relaxed font-normal">
          <strong>SignAI</strong> addresses this acute communication barrier by delivering an accessible, zero-cost, browser-based
          assistive platform. By interpreting fingerspelled alphabet gestures into legible text and spoken English in real time, SignAI empowers
          deaf signers to communicate directly with hearing interlocutors without intermediaries.
        </p>
      </section>

      {/* 2. PROJECT OBJECTIVES */}
      <section className="space-y-4">
        <div className="pb-3 border-b border-slate-200/80 dark:border-white/[0.08] flex items-center space-x-2">
          <Compass className="w-4 h-4 text-indigo-600 dark:text-indigo-400" />
          <h2 className="text-base font-bold tracking-tight text-slate-900 dark:text-slate-100">
            Primary Engineering Objectives
          </h2>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {objectives.map(({ num, title, desc }) => (
            <div
              key={num}
              className="card-linear-hover p-5 space-y-2 flex flex-col justify-between shadow-sm"
            >
              <div>
                <span className="text-xs font-bold text-white bg-gradient-to-r from-indigo-600 to-violet-600 px-2 py-0.5 rounded-md inline-block mb-2 shadow-xs">
                  Objective {num}
                </span>
                <h3 className="text-sm font-bold text-slate-900 dark:text-slate-100 tracking-tight">
                  {title}
                </h3>
                <p className="text-xs text-slate-600 dark:text-slate-400 leading-relaxed mt-1.5 font-normal">
                  {desc}
                </p>
              </div>
            </div>
          ))}
        </div>
      </section>

      {/* 3. SYSTEM ARCHITECTURE & DATA FLOW */}
      <section className="card-linear p-5 sm:p-6 space-y-4 shadow-md">
        <div className="flex items-center space-x-2 pb-3 border-b border-slate-200/80 dark:border-white/[0.08]">
          <Layers className="w-4 h-4 text-indigo-600 dark:text-indigo-400" />
          <h2 className="text-base font-bold tracking-tight text-slate-900 dark:text-slate-100">
            Three-Tier Decoupled Architecture
          </h2>
        </div>

        {/* Visual Pipeline Flow */}
        <div className="grid grid-cols-1 sm:grid-cols-5 gap-3 items-center text-center font-mono">
          <div className="p-4 rounded-xl border border-slate-200/80 dark:border-white/[0.08] bg-slate-50/80 dark:bg-white/[0.02]">
            <Globe className="w-6 h-6 text-indigo-600 dark:text-indigo-400 mx-auto mb-2" />
            <h4 className="text-xs font-bold text-slate-900 dark:text-slate-100 font-sans">React 19 Client</h4>
            <p className="text-[10px] text-slate-500 dark:text-slate-400 mt-0.5">Capture / Buffer &bull; 6 Routes</p>
          </div>

          <div className="hidden sm:flex justify-center text-indigo-400">
            <ArrowRight className="w-5 h-5 animate-pulse" />
          </div>

          <div className="p-4 rounded-xl border border-slate-200/80 dark:border-white/[0.08] bg-slate-50/80 dark:bg-white/[0.02]">
            <Terminal className="w-6 h-6 text-indigo-600 dark:text-indigo-400 mx-auto mb-2" />
            <h4 className="text-xs font-bold text-slate-900 dark:text-slate-100 font-sans">FastAPI Service</h4>
            <p className="text-[10px] text-slate-500 dark:text-slate-400 mt-0.5">Pillow Resampling &bull; Port 8000</p>
          </div>

          <div className="hidden sm:flex justify-center text-indigo-400">
            <ArrowRight className="w-5 h-5 animate-pulse" />
          </div>

          <div className="p-4 rounded-xl border border-slate-200/80 dark:border-white/[0.08] bg-slate-50/80 dark:bg-white/[0.02]">
            <Cpu className="w-6 h-6 text-indigo-600 dark:text-indigo-400 mx-auto mb-2" />
            <h4 className="text-xs font-bold text-slate-900 dark:text-slate-100 font-sans">CNN V4 Core</h4>
            <p className="text-[10px] text-slate-500 dark:text-slate-400 mt-0.5">308k Params &bull; 86.3% Acc</p>
          </div>
        </div>

        <p className="text-xs text-slate-600 dark:text-slate-400 leading-relaxed font-normal pt-1">
          The presentation layer accesses the user's camera safely via HTML5 <code>getUserMedia</code>, center-crops the video feed to a square canvas, and posts image blobs to the backend every ~500ms with in-flight concurrency locking. The FastAPI service transforms the payload into a 128×128 normalized float32 tensor, invokes CNN V4 in memory, and returns prediction telemetry. A client-side state machine validates consecutive frame stability before appending verified characters to the sentence buffer.
        </p>
      </section>

      {/* 4. TECHNOLOGY STACK */}
      <section className="space-y-4">
        <div className="pb-3 border-b border-slate-200/80 dark:border-white/[0.08] flex items-center space-x-2">
          <Code2 className="w-4 h-4 text-indigo-600 dark:text-indigo-400" />
          <h2 className="text-base font-bold tracking-tight text-slate-900 dark:text-slate-100">
            Technology Stack &amp; Dependencies
          </h2>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
          {techStack.map(({ name, role, desc }) => (
            <div
              key={name}
              className="card-linear-hover p-4 space-y-1.5 shadow-sm"
            >
              <span className="text-[10px] font-bold uppercase tracking-wider text-indigo-600 dark:text-indigo-400 block">
                {role}
              </span>
              <h3 className="text-sm font-bold text-slate-900 dark:text-slate-100">
                {name}
              </h3>
              <p className="text-xs text-slate-600 dark:text-slate-400 leading-relaxed font-normal">
                {desc}
              </p>
            </div>
          ))}
        </div>
      </section>

      {/* 5. DATASET & CNN MODEL ARCHITECTURE */}
      <section className="card-linear p-5 sm:p-6 space-y-3.5 shadow-md">
        <div className="flex items-center space-x-2 pb-3 border-b border-slate-200/80 dark:border-white/[0.08]">
          <Database className="w-4 h-4 text-indigo-600 dark:text-indigo-400" />
          <h2 className="text-base font-bold tracking-tight text-slate-900 dark:text-slate-100">
            Dataset Provenance &amp; CNN V4 Topology
          </h2>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 text-xs">
          <div className="space-y-2 p-4 rounded-xl border border-slate-200/60 dark:border-white/[0.06] bg-slate-50/80 dark:bg-white/[0.02]">
            <h4 className="font-bold text-slate-900 dark:text-slate-100 font-sans">Dataset Hygiene (RealSign ISL)</h4>
            <ul className="space-y-1 text-slate-600 dark:text-slate-400 font-sans">
              <li>&bull; License: Creative Commons Zero (CC0 1.0 Universal).</li>
              <li>&bull; Clean Samples: 25,085 total across 26 classes (A–Z).</li>
              <li>&bull; Quarantined: 890 cross-split duplicates + 2 corrupt ASCII scripts.</li>
              <li>&bull; Held-Out Test Set: 5,161 strictly isolated images.</li>
            </ul>
          </div>

          <div className="space-y-2 p-4 rounded-xl border border-slate-200/60 dark:border-white/[0.06] bg-slate-50/80 dark:bg-white/[0.02]">
            <h4 className="font-bold text-slate-900 dark:text-slate-100 font-sans">CNN V4 Topology Specifications</h4>
            <ul className="space-y-1 text-slate-600 dark:text-slate-400 font-sans">
              <li>&bull; Input: 128 × 128 × 3 sRGB normalized to [0, 1].</li>
              <li>&bull; 3 Double-Conv Blocks: 32, 64, 128 filters with Batch Normalization.</li>
              <li>&bull; Regularization: L2 penalty (&lambda; = 0.0001) on all 8 kernels + 0.40 Dropout.</li>
              <li>&bull; Parameters: 308,218 total (307,322 trainable, 896 non-trainable).</li>
            </ul>
          </div>
        </div>
      </section>

      {/* 6. LIMITATIONS & FUTURE SCOPE */}
      <section className="card-linear p-5 sm:p-6 space-y-3.5 shadow-md border-amber-500/20">
        <div className="flex items-center space-x-2 text-amber-600 dark:text-amber-400 font-mono text-xs font-bold uppercase tracking-wider pb-2.5 border-b border-slate-200/80 dark:border-white/[0.08]">
          <AlertTriangle className="w-4 h-4" />
          <span>Research Scope, Boundaries &amp; Future Work</span>
        </div>

        <div className="space-y-3 text-xs text-slate-700 dark:text-slate-300 leading-relaxed font-sans">
          <p>
            <strong>Static Alphabet Scope:</strong> SignAI is engineered and evaluated as an educational prototype for static fingerspelling alphabet poses (A–Z). Natural conversational ISL encompasses continuous multi-gesture flow, facial expressions, and spatial grammar, requiring sequence modeling (e.g. MediaPipe Hands with Bi-LSTM or Transformers).
          </p>
          <p>
            <strong>Dynamic Gestures (J &amp; Z):</strong> The letters J and Z require movement trajectories in natural ISL. Our static 2D CNN recognizes static keyframe representations. Future iterations will incorporate sliding temporal window sequence networks.
          </p>
          <p>
            <strong>Photometric Illumination Boundaries:</strong> Our empirical robustness evaluation across 32,721 model inferences proves that while the network is robust to optical defocus (+0.28 pp) and natural wrist tilts (+0.08 pp), severe underexposure (-40% brightness) collapses accuracy to 32.82%. Adequate lighting is an essential operational prerequisite.
          </p>
        </div>
      </section>
    </div>
  );
}