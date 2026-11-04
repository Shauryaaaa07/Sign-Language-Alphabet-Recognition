import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import {
  Camera,
  BookOpen,
  ArrowRight,
  AlertCircle,
  Eye,
  Cpu,
  Layers,
  Volume2,
  ShieldCheck,
  Sparkles,
  CheckCircle2,
} from 'lucide-react';

/**
 * Home Component
 * Modern Indigo AI (Linear & Cursor style) landing page for SignAI.
 * Combines obsidian/porcelain surfaces, electric indigo accents,
 * smooth rounded cards, and empirical 26-class ISL recognition benchmarks.
 */
export default function Home({ backendStatus }) {
  const isOnline = backendStatus === 'connected';

  // Interactive specimen preview state for hero
  const [activeSpecimen, setActiveSpecimen] = useState('L');

  const specimens = {
    L: { letter: 'L', conf: '99.8%', latency: '108ms', desc: 'Orthogonal vertical index and horizontal thumb forming distinct L angle.' },
    A: { letter: 'A', conf: '94.1%', latency: '112ms', desc: 'Compact closed fist with thumb resting vertically along the lateral index.' },
    B: { letter: 'B', conf: '96.4%', latency: '105ms', desc: 'Four upright parallel fingers with thumb folded across anterior palm.' },
    C: { letter: 'C', conf: '98.5%', latency: '110ms', desc: 'Curved phalanges and opposing thumb forming visible anatomical C-arc.' },
  };

  const currentSpecimen = specimens[activeSpecimen] || specimens.L;

  const pipeline = [
    {
      num: '01',
      title: 'Monocular Capture',
      category: 'Input Normalization',
      icon: Eye,
      desc: 'Acquires live camera stream frames at 500ms intervals or raw image files, center-cropping and bilinearly interpolating to 128×128 sRGB tensors scaled to [0, 1].',
    },
    {
      num: '02',
      title: 'Convolutional Inference',
      category: 'Feature Extraction',
      icon: Cpu,
      desc: 'Three double-convolution blocks with Batch Normalization and L2 regularization extract geometric contours, projecting into 26 Softmax class probabilities.',
    },
    {
      num: '03',
      title: 'Temporal Stabilization',
      category: 'Jitter Suppression',
      icon: Layers,
      desc: 'A sliding 3-frame consensus window requires consecutive agreement with ≥ 75% confidence before committing letters to the sentence buffer.',
    },
    {
      num: '04',
      title: 'Speech Vocalization',
      category: 'Multimodal Synthesis',
      icon: Volume2,
      desc: 'Assembles recognized characters into fluent phrases with deletion and spacing controls, synthesizing audible English speech via W3C Web Speech API.',
    },
  ];

  const coreFeatures = [
    {
      tag: 'Vision Engine',
      title: 'In-Flight Concurrency Guard',
      icon: ShieldCheck,
      desc: 'Guarantees that rapid video streaming cannot flood the HTTP transport layer, automatically dropping lagging frames to maintain real-time responsiveness.',
    },
    {
      tag: 'Audio Output',
      title: 'Native Speech Synthesis',
      icon: Volume2,
      desc: 'Converts constructed sign sentences into clear spoken audio directly within the browser, with English voice selection and zero cloud subscription dependencies.',
    },
    {
      tag: 'Alphabet Scope',
      title: 'Complete 26-Class Vocabulary',
      icon: Sparkles,
      desc: 'Evaluates the full English alphabet (A through Z) without class reduction, backed by independent test evaluation on 5,161 held-out images.',
    },
    {
      tag: 'Workspace',
      title: 'Tactile Sentence Builder',
      icon: CheckCircle2,
      desc: 'Full-featured sentence composition canvas with space insertion, backspacing, character telemetry counters, and one-click clipboard export.',
    },
  ];

  return (
    <div className="space-y-10 sm:space-y-12 py-4 sm:py-6">
      {/* 1. HERO SECTION: Modern Indigo Linear Architecture */}
      <section className="relative">
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 lg:gap-10 items-center">
          {/* Left Column: Typography & Intentional Hierarchy (7 cols) */}
          <div className="lg:col-span-7 space-y-5">
            {/* Status Pill Badge */}
            <div className="inline-flex items-center space-x-2 px-3 py-1 rounded-full border border-slate-200/80 dark:border-white/[0.08] bg-white/80 dark:bg-[#0F111A]/80 backdrop-blur-md text-xs shadow-xs">
              <span className={`w-2 h-2 rounded-full ${isOnline ? 'bg-emerald-500 shadow-xs shadow-emerald-500/50' : 'bg-amber-500 shadow-xs shadow-amber-500/50'} animate-pulse`} />
              <span className="font-semibold text-slate-800 dark:text-slate-200">
                {isOnline ? 'CNN V4 Online' : 'SignAI Platform Active'}
              </span>
              <span className="text-slate-400 dark:text-slate-600">/</span>
              <span className="text-slate-600 dark:text-slate-400 font-medium">26 Alphabet Classes</span>
            </div>

            {/* Display Headline */}
            <div className="space-y-2">
              <h1 className="text-4xl sm:text-6xl lg:text-7xl font-extrabold tracking-tight text-slate-900 dark:text-white leading-[1.05]">
                Your Hands.{' '}
                <span className="bg-gradient-to-r from-indigo-500 via-indigo-400 to-violet-400 bg-clip-text text-transparent">
                  Your Voice.
                </span>
              </h1>
              <p className="text-xs sm:text-sm font-semibold uppercase tracking-wider text-indigo-600 dark:text-indigo-400 pt-1">
                Indian Sign Language Alphabet Recognition (A–Z)
              </p>
            </div>

            {/* Narrative Body */}
            <p className="text-base sm:text-lg text-slate-600 dark:text-slate-300 max-w-xl leading-relaxed font-normal">
              An accessible computer vision platform engineered to bridge communication barriers.
              Translate Indian Sign Language fingerspelling poses into real-time text and natural spoken English
              using an audited 26-class deep convolutional neural network.
            </p>

            {/* CTAs */}
            <div className="flex flex-wrap items-center gap-3 pt-1">
              <Link to="/studio" className="btn-indigo">
                <Camera className="w-4 h-4" />
                <span>Start Recognizing</span>
                <ArrowRight className="w-4 h-4 ml-0.5" />
              </Link>

              <Link to="/learn" className="btn-secondary-linear">
                <BookOpen className="w-4 h-4 text-indigo-500 dark:text-indigo-400" />
                <span>Explore Alphabet A–Z</span>
              </Link>
            </div>

            {/* Audited Spec Snapshot Cards */}
            <div className="pt-4 border-t border-slate-200/80 dark:border-white/[0.08] grid grid-cols-3 gap-3 sm:gap-4">
              <div className="p-3 rounded-xl bg-slate-100/60 dark:bg-white/[0.03] border border-slate-200/60 dark:border-white/[0.06]">
                <span className="text-2xl sm:text-3xl font-bold tracking-tight text-slate-900 dark:text-white block font-mono">
                  86.34%
                </span>
                <span className="text-[11px] font-medium uppercase tracking-wider text-slate-500 dark:text-slate-400">
                  Test Accuracy
                </span>
              </div>
              <div className="p-3 rounded-xl bg-slate-100/60 dark:bg-white/[0.03] border border-slate-200/60 dark:border-white/[0.06]">
                <span className="text-2xl sm:text-3xl font-bold tracking-tight text-slate-900 dark:text-white block font-mono">
                  83.96%
                </span>
                <span className="text-[11px] font-medium uppercase tracking-wider text-slate-500 dark:text-slate-400">
                  Macro F1
                </span>
              </div>
              <div className="p-3 rounded-xl bg-slate-100/60 dark:bg-white/[0.03] border border-slate-200/60 dark:border-white/[0.06]">
                <span className="text-2xl sm:text-3xl font-bold tracking-tight text-slate-900 dark:text-white block font-mono">
                  308k
                </span>
                <span className="text-[11px] font-medium uppercase tracking-wider text-slate-500 dark:text-slate-400">
                  Parameters
                </span>
              </div>
            </div>
          </div>

          {/* Right Column: Sleek Specimen Viewer Card (5 cols) */}
          <div className="lg:col-span-5">
            <div className="card-linear p-5 space-y-4 shadow-xl">
              {/* Specimen Header & Selector Tabs */}
              <div className="flex items-center justify-between pb-3 border-b border-slate-200/80 dark:border-white/[0.08]">
                <div className="flex items-center space-x-2">
                  <span className="w-2 h-2 rounded-full bg-indigo-500" />
                  <span className="font-semibold text-xs text-slate-900 dark:text-slate-100 uppercase tracking-wider">
                    Interactive Pose Specimen
                  </span>
                </div>
                <div className="flex space-x-1.5 bg-slate-100 dark:bg-[#161926] p-1 rounded-lg border border-slate-200/60 dark:border-white/[0.06]">
                  {Object.keys(specimens).map((char) => (
                    <button
                      key={char}
                      type="button"
                      onClick={() => setActiveSpecimen(char)}
                      className={`w-7 h-7 rounded-md text-xs font-bold transition-all ${
                        activeSpecimen === char
                          ? 'bg-gradient-to-r from-indigo-600 to-violet-600 text-white shadow-xs'
                          : 'text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white'
                      }`}
                    >
                      {char}
                    </button>
                  ))}
                </div>
              </div>

              {/* High-Contrast Frame */}
              <div className="relative aspect-square w-full rounded-xl bg-slate-950 border border-slate-800/80 flex items-center justify-center overflow-hidden group">
                <img
                  src={`/alphabet_samples/${currentSpecimen.letter}.jpg`}
                  alt={`Indian Sign Language Letter ${currentSpecimen.letter}`}
                  className="w-full h-full object-cover transition-transform duration-500 group-hover:scale-105"
                />

                {/* Overlaid Editorial Metadata */}
                <div className="absolute top-3 left-3 bg-slate-950/85 backdrop-blur-md text-white text-xs px-2.5 py-1 rounded-lg border border-white/10 flex items-center space-x-2 shadow-sm">
                  <span className="w-2 h-2 rounded-full bg-indigo-400 animate-pulse" />
                  <span className="font-semibold font-mono">Pose: '{currentSpecimen.letter}'</span>
                </div>

                <div className="absolute bottom-3 right-3 bg-slate-950/85 backdrop-blur-md text-emerald-400 text-xs font-mono font-semibold px-2.5 py-1 rounded-lg border border-emerald-500/20 shadow-sm">
                  Confidence: {currentSpecimen.conf}
                </div>
              </div>

              {/* Specimen Anatomical Description */}
              <div className="p-3.5 bg-slate-50/80 dark:bg-white/[0.02] rounded-xl border border-slate-200/60 dark:border-white/[0.06] text-xs space-y-1.5">
                <div className="flex justify-between text-slate-600 dark:text-slate-400">
                  <span className="font-medium">Input Tensor</span>
                  <span className="font-mono font-semibold text-slate-900 dark:text-slate-100">128 × 128 × 3 RGB</span>
                </div>
                <div className="flex justify-between text-slate-600 dark:text-slate-400">
                  <span className="font-medium">Inference Latency</span>
                  <span className="font-mono font-semibold text-indigo-600 dark:text-indigo-400">{currentSpecimen.latency}</span>
                </div>
                <p className="text-slate-500 dark:text-slate-400 pt-1 text-[11px] leading-relaxed border-t border-slate-200/60 dark:border-white/[0.06]">
                  {currentSpecimen.desc}
                </p>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* 2. SPECIFICATION STRIP: Modern Metric Cards */}
      <section className="card-linear overflow-hidden shadow-md">
        <div className="p-4 sm:p-5 border-b border-slate-200/80 dark:border-white/[0.08] flex flex-col sm:flex-row sm:items-center justify-between gap-2 bg-slate-50/50 dark:bg-white/[0.02]">
          <div>
            <span className="text-xs uppercase tracking-wider text-indigo-600 dark:text-indigo-400 font-bold block mb-0.5">
              Empirical Evaluation Standard
            </span>
            <h2 className="text-lg sm:text-xl font-bold tracking-tight text-slate-900 dark:text-slate-100">
              Verified 26-Class Benchmark Metrics
            </h2>
          </div>
          <span className="text-xs text-slate-500 dark:text-slate-400 font-mono">
            Partition: 5,161 strictly held-out test images
          </span>
        </div>

        <div className="grid grid-cols-2 md:grid-cols-4 divide-y md:divide-y-0 divide-x-0 md:divide-x divide-slate-200/80 dark:divide-white/[0.08] font-mono">
          <div className="p-4 sm:p-5 space-y-1">
            <span className="text-xs uppercase font-medium text-slate-500 dark:text-slate-400 block font-sans">Overall Accuracy</span>
            <span className="text-2xl sm:text-3xl font-extrabold text-slate-900 dark:text-slate-100 block">
              86.34%
            </span>
            <span className="text-[11px] text-slate-500 dark:text-slate-400 block">4,456 / 5,161 Correct</span>
          </div>

          <div className="p-4 sm:p-5 space-y-1">
            <span className="text-xs uppercase font-medium text-slate-500 dark:text-slate-400 block font-sans">Macro F1-Score</span>
            <span className="text-2xl sm:text-3xl font-extrabold text-slate-900 dark:text-slate-100 block">
              83.96%
            </span>
            <span className="text-[11px] text-slate-500 dark:text-slate-400 block">Weighted F1: 83.87%</span>
          </div>

          <div className="p-4 sm:p-5 space-y-1">
            <span className="text-xs uppercase font-medium text-slate-500 dark:text-slate-400 block font-sans">Macro Precision</span>
            <span className="text-2xl sm:text-3xl font-extrabold text-slate-900 dark:text-slate-100 block">
              85.22%
            </span>
            <span className="text-[11px] text-slate-500 dark:text-slate-400 block">Macro Recall: 86.42%</span>
          </div>

          <div className="p-4 sm:p-5 space-y-1">
            <span className="text-xs uppercase font-medium text-slate-500 dark:text-slate-400 block font-sans">Flawless Classes</span>
            <span className="text-2xl sm:text-3xl font-extrabold text-indigo-600 dark:text-indigo-400 block">
              4 Classes
            </span>
            <span className="text-[11px] text-slate-500 dark:text-slate-400 block">100% on D, H, L, R</span>
          </div>
        </div>
      </section>

      {/* 3. HOW IT WORKS: Disciplined Step-by-Step Flow */}
      <section className="space-y-4">
        <div className="pb-3 border-b border-slate-200/80 dark:border-white/[0.08] flex items-center justify-between">
          <div>
            <span className="text-xs uppercase tracking-wider text-indigo-600 dark:text-indigo-400 font-bold block mb-0.5">
              Technical Pipeline
            </span>
            <h2 className="text-xl sm:text-2xl font-bold tracking-tight text-slate-900 dark:text-slate-100">
              How SignAI Operates
            </h2>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          {pipeline.map(({ num, title, category, desc, icon: Icon }) => (
            <div
              key={num}
              className="card-linear-hover p-5 flex flex-col justify-between"
            >
              <div>
                <div className="flex items-center justify-between mb-3">
                  <span className="text-xs font-bold text-white bg-gradient-to-r from-indigo-600 to-violet-600 px-2 py-0.5 rounded-md shadow-xs">
                    {num}
                  </span>
                  <div className="w-8 h-8 rounded-lg bg-indigo-50 dark:bg-indigo-950/50 border border-indigo-200/60 dark:border-indigo-800/60 flex items-center justify-center text-indigo-600 dark:text-indigo-400">
                    <Icon className="w-4 h-4" />
                  </div>
                </div>
                <span className="text-[11px] uppercase tracking-wider text-slate-500 dark:text-slate-400 block mb-1 font-semibold">
                  {category}
                </span>
                <h3 className="text-base font-bold text-slate-900 dark:text-slate-100 mb-1.5 tracking-tight">
                  {title}
                </h3>
                <p className="text-xs text-slate-600 dark:text-slate-400 leading-relaxed font-normal">
                  {desc}
                </p>
              </div>
            </div>
          ))}
        </div>
      </section>

      {/* 4. CORE FEATURES: Architectural Grid */}
      <section className="space-y-4">
        <div className="pb-3 border-b border-slate-200/80 dark:border-white/[0.08]">
          <span className="text-xs uppercase tracking-wider text-indigo-600 dark:text-indigo-400 font-bold block mb-0.5">
            Product Capabilities
          </span>
          <h2 className="text-xl sm:text-2xl font-bold tracking-tight text-slate-900 dark:text-slate-100">
            Engineered for Precision &amp; Usability
          </h2>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {coreFeatures.map(({ tag, title, desc, icon: Icon }) => (
            <div
              key={title}
              className="card-linear-hover p-5 space-y-2.5"
            >
              <div className="flex items-center justify-between">
                <span className="text-[10px] uppercase font-bold text-indigo-700 dark:text-indigo-300 bg-indigo-50 dark:bg-indigo-950/60 px-2.5 py-0.5 rounded-full border border-indigo-200/80 dark:border-indigo-800/60">
                  {tag}
                </span>
                <div className="w-7 h-7 rounded-lg bg-slate-100 dark:bg-white/[0.05] flex items-center justify-center text-slate-600 dark:text-slate-300">
                  <Icon className="w-3.5 h-3.5" />
                </div>
              </div>
              <h3 className="text-base font-bold text-slate-900 dark:text-slate-100 tracking-tight">
                {title}
              </h3>
              <p className="text-xs sm:text-sm text-slate-600 dark:text-slate-400 leading-relaxed font-normal">
                {desc}
              </p>
            </div>
          ))}
        </div>
      </section>

      {/* 5. ACADEMIC LIMITATIONS CALLOUT: Grounded Honesty */}
      <section className="card-linear p-5 sm:p-6 space-y-3.5 border-amber-500/20 dark:border-amber-500/20">
        <div className="flex items-center space-x-2 text-amber-600 dark:text-amber-400 text-xs font-bold uppercase tracking-wider">
          <AlertCircle className="w-4 h-4 shrink-0" />
          <span>Academic Scope &amp; Physical Boundaries</span>
        </div>

        <h3 className="text-lg sm:text-xl font-bold tracking-tight text-slate-900 dark:text-slate-100">
          Transparent Operational Boundaries
        </h3>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 pt-1 text-xs text-slate-600 dark:text-slate-400 leading-relaxed font-normal">
          <div className="p-3.5 rounded-xl bg-slate-50/60 dark:bg-white/[0.02] border border-slate-200/60 dark:border-white/[0.06] space-y-1">
            <strong className="block text-slate-900 dark:text-slate-200 font-semibold font-mono text-xs">
              01 / Static Keyframes (J &amp; Z)
            </strong>
            <p>
              Natural ISL for letters J and Z requires motion paths in 3D space. SignAI processes static 2D images,
              classifying standard terminal keyframes rather than the dynamic trajectory.
            </p>
          </div>
          <div className="p-3.5 rounded-xl bg-slate-50/60 dark:bg-white/[0.02] border border-slate-200/60 dark:border-white/[0.06] space-y-1">
            <strong className="block text-slate-900 dark:text-slate-200 font-semibold font-mono text-xs">
              02 / Monocular Occlusion (W &amp; S)
            </strong>
            <p>
              In 2D silhouette space, finger splaying on W collapses into E and X, causing 0% recall on the test set.
              Class S is confused with A due to thumb-over-fist overlap.
            </p>
          </div>
          <div className="p-3.5 rounded-xl bg-slate-50/60 dark:bg-white/[0.02] border border-slate-200/60 dark:border-white/[0.06] space-y-1">
            <strong className="block text-slate-900 dark:text-slate-200 font-semibold font-mono text-xs">
              03 / Lighting Sensitivity
            </strong>
            <p>
              Empirical testing across 32,721 model evaluations reveals that underexposure (-40% brightness) collapses
              accuracy to 32.82%. Adequate room lighting is essential.
            </p>
          </div>
        </div>
      </section>

      {/* 6. CLOSING CTA BANNER */}
      <section className="relative overflow-hidden rounded-2xl p-6 sm:p-8 text-center space-y-3.5 bg-gradient-to-br from-indigo-950 via-slate-900 to-[#0F111A] text-white border border-indigo-500/25 shadow-xl">
        <div className="absolute top-0 right-1/4 w-96 h-96 bg-indigo-500/10 rounded-full blur-3xl pointer-events-none" />
        <span className="text-xs uppercase tracking-wider text-indigo-400 font-bold block">
          Begin Recognition Session
        </span>
        <h2 className="text-2xl sm:text-3xl font-bold tracking-tight max-w-xl mx-auto">
          Start Translating Indian Sign Language Alphabet Poses
        </h2>
        <p className="text-slate-300 text-sm max-w-lg mx-auto leading-relaxed font-normal">
          Open the Recognition Studio to test live webcam video capture, inspect confidence metrics,
          and vocalize assembled sentences.
        </p>
        <div className="pt-2">
          <Link
            to="/studio"
            className="inline-flex items-center space-x-2.5 px-6 py-3 rounded-xl text-sm font-semibold text-slate-950 bg-white hover:bg-slate-100 transition-all shadow-lg hover:shadow-xl hover:scale-[1.02] active:scale-[0.98]"
          >
            <Camera className="w-4 h-4 text-indigo-600" />
            <span>Launch Recognition Studio</span>
            <ArrowRight className="w-4 h-4 ml-0.5" />
          </Link>
        </div>
      </section>
    </div>
  );
}