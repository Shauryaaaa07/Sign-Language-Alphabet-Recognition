import React, { useState, useEffect } from 'react';
import {
  Volume2,
  Square,
  Copy,
  Check,
  Trash2,
  Space as SpaceIcon,
  Delete as BackspaceIcon,
  Plus,
  Type,
  AlertTriangle,
} from 'lucide-react';
import {
  addLetter,
  addSpace,
  deleteLastChar,
  clearAllText,
  calculateTextMetrics,
} from '../utils/textBuilderLogic';
import { useTextToSpeech } from '../hooks/useTextToSpeech';

/**
 * TextBuilder Component
 * Modern Indigo AI sentence builder with character assembly, backspacing, and text-to-speech vocalization.
 */
export default function TextBuilder({
  text,
  onTextChange,
  activeLetter,
}) {
  const [showConfirmClear, setShowConfirmClear] = useState(false);
  const [copied, setCopied] = useState(false);

  // Browser-native Text-to-Speech hook
  const {
    speechStatus,
    errorMessage: speechError,
    voices,
    selectedVoiceURI,
    setSelectedVoiceURI,
    speak,
    stop: stopSpeech,
    isSupported: isSpeechSupported,
  } = useTextToSpeech();

  // Auto-reset clear confirmation prompt after 3 seconds
  useEffect(() => {
    if (!showConfirmClear) return;
    const timer = setTimeout(() => setShowConfirmClear(false), 3000);
    return () => clearTimeout(timer);
  }, [showConfirmClear]);

  // Reset copied notification after 2 seconds
  useEffect(() => {
    if (!copied) return;
    const timer = setTimeout(() => setCopied(false), 2000);
    return () => clearTimeout(timer);
  }, [copied]);

  const isValidLetter = Boolean(
    activeLetter && typeof activeLetter === 'string' && /^[A-Z]$/i.test(activeLetter.trim())
  );
  const formattedLetter = isValidLetter ? activeLetter.trim().toUpperCase() : null;

  const metrics = calculateTextMetrics(text);
  const isTextEmpty = !text || text.trim().length === 0;
  const endsWithSpace = Boolean(text && text.endsWith(' '));

  const handleAddLetter = () => {
    if (!formattedLetter) return;
    const newText = addLetter(text, formattedLetter);
    onTextChange(newText);
  };

  const handleAddSpace = () => {
    if (isTextEmpty || endsWithSpace) return;
    const newText = addSpace(text);
    onTextChange(newText);
  };

  const handleDelete = () => {
    if (!text || text.length === 0) return;
    const newText = deleteLastChar(text);
    onTextChange(newText);
  };

  const handleClear = () => {
    if (!showConfirmClear) {
      setShowConfirmClear(true);
      return;
    }
    const newText = clearAllText();
    onTextChange(newText);
    setShowConfirmClear(false);
    stopSpeech();
  };

  const handleCopy = async () => {
    if (!text || text.trim().length === 0) return;
    try {
      if (navigator.clipboard && navigator.clipboard.writeText) {
        await navigator.clipboard.writeText(text);
        setCopied(true);
      }
    } catch {
      // Fallback
    }
  };

  const handleSpeak = () => {
    if (isTextEmpty) return;
    speak(text);
  };

  const isSpeaking = speechStatus === 'speaking';

  return (
    <div className="card-linear p-6 space-y-5 shadow-lg">
      {/* Header with Title and Telemetry */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pb-4 border-b border-slate-200/80 dark:border-white/[0.08]">
        <div className="flex items-center space-x-2.5">
          <div className="w-8 h-8 rounded-lg bg-indigo-50 dark:bg-indigo-950/60 text-indigo-600 dark:text-indigo-400 flex items-center justify-center border border-indigo-200/60 dark:border-indigo-800/60 shadow-xs">
            <Type className="w-4 h-4" />
          </div>
          <div>
            <h3 className="text-base font-bold tracking-tight text-slate-900 dark:text-white">
              Sentence Builder &amp; Vocalizer
            </h3>
            <p className="text-xs text-slate-500 dark:text-slate-400">
              Assemble recognized alphabet characters into words and synthesize into English speech.
            </p>
          </div>
        </div>

        {/* Text Metrics Counters */}
        <div className="flex items-center space-x-2 font-mono text-xs">
          <span className="px-2.5 py-1 rounded-full border border-slate-200/80 dark:border-white/[0.08] bg-slate-50 dark:bg-white/[0.03] text-slate-700 dark:text-slate-300">
            {metrics.charCount} {metrics.charCount === 1 ? 'char' : 'chars'}
          </span>
          <span className="px-2.5 py-1 rounded-full border border-slate-200/80 dark:border-white/[0.08] bg-slate-50 dark:bg-white/[0.03] text-slate-700 dark:text-slate-300">
            {metrics.wordCount} {metrics.wordCount === 1 ? 'word' : 'words'}
          </span>
        </div>
      </div>

      {/* Main Assembled Text Canvas */}
      <div className="relative">
        <div
          role="region"
          aria-label="Constructed sentence text display"
          className="w-full min-h-[110px] max-h-[220px] overflow-y-auto p-5 rounded-xl bg-slate-50 dark:bg-[#08090E] border border-slate-200/80 dark:border-white/[0.08] font-mono text-xl sm:text-2xl text-slate-900 dark:text-white tracking-wide break-words flex items-center justify-start shadow-inner"
        >
          {text ? (
            <span className="leading-relaxed">
              {text}
              <span className="inline-block w-2.5 h-6 ml-1 bg-indigo-500 dark:bg-indigo-400 animate-pulse align-middle rounded-xs" />
            </span>
          ) : (
            <span className="text-slate-400 dark:text-slate-500 text-sm font-sans select-none italic">
              Constructed sentence will appear here. Add letters from the recognition panel above...
            </span>
          )}
        </div>

        {/* Copy Button */}
        {text && text.trim().length > 0 && (
          <button
            type="button"
            onClick={handleCopy}
            className="absolute top-3 right-3 px-2.5 py-1.5 rounded-lg border border-slate-200/80 dark:border-white/[0.1] bg-white/90 dark:bg-[#161926]/90 backdrop-blur-md text-slate-700 dark:text-slate-300 hover:text-slate-900 dark:hover:text-white transition-all text-xs font-mono flex items-center space-x-1.5 shadow-sm"
            title="Copy sentence to clipboard"
            aria-label="Copy sentence text"
          >
            {copied ? (
              <span className="flex items-center space-x-1 text-emerald-600 dark:text-emerald-400 font-bold">
                <Check className="w-3.5 h-3.5" />
                <span>Copied</span>
              </span>
            ) : (
              <>
                <Copy className="w-3.5 h-3.5 text-indigo-500" />
                <span>Copy</span>
              </>
            )}
          </button>
        )}
      </div>

      {/* Action Controls Toolbar */}
      <div className="flex flex-wrap items-center justify-between gap-3 pt-1">
        {/* Left Editing Controls: Add, Space, Delete, Clear */}
        <div className="flex flex-wrap items-center gap-2">
          {/* Add Active Letter */}
          <button
            type="button"
            onClick={handleAddLetter}
            disabled={!formattedLetter}
            className="btn-indigo disabled:opacity-40 disabled:cursor-not-allowed"
            title={formattedLetter ? `Add '${formattedLetter}' to text` : 'No valid letter recognized yet'}
          >
            <Plus className="w-4 h-4" />
            <span>
              Add Letter {formattedLetter ? `('${formattedLetter}')` : ''}
            </span>
          </button>

          {/* Space Separator */}
          <button
            type="button"
            onClick={handleAddSpace}
            disabled={isTextEmpty || endsWithSpace}
            className="btn-secondary-linear disabled:opacity-40 disabled:cursor-not-allowed"
            title={endsWithSpace ? 'Space already added' : 'Insert space'}
          >
            <SpaceIcon className="w-3.5 h-3.5 text-indigo-500 dark:text-indigo-400" />
            <span>Space</span>
          </button>

          {/* Backspace Delete */}
          <button
            type="button"
            onClick={handleDelete}
            disabled={!text || text.length === 0}
            className="btn-secondary-linear disabled:opacity-40 disabled:cursor-not-allowed"
            title="Delete last character"
          >
            <BackspaceIcon className="w-3.5 h-3.5 text-slate-400" />
            <span>Delete</span>
          </button>

          {/* Clear Buffer */}
          <button
            type="button"
            onClick={handleClear}
            disabled={!text || text.length === 0}
            className={`inline-flex items-center space-x-1.5 px-3.5 py-2 rounded-xl text-xs sm:text-sm font-semibold transition-all disabled:opacity-40 disabled:cursor-not-allowed ${
              showConfirmClear
                ? 'bg-rose-600 text-white shadow-sm'
                : 'border border-slate-200/80 dark:border-white/[0.08] bg-white dark:bg-[#161926] text-slate-700 dark:text-slate-300 hover:text-rose-600 dark:hover:text-rose-400 hover:border-rose-300'
            }`}
            title="Reset sentence text"
          >
            <Trash2 className="w-3.5 h-3.5" />
            <span>{showConfirmClear ? 'Confirm Clear?' : 'Clear'}</span>
          </button>
        </div>

        {/* Right Voice Conversion Controls */}
        <div className="flex flex-wrap items-center gap-2">
          {/* Voice Selector */}
          {voices && voices.length > 1 && (
            <select
              value={selectedVoiceURI || ''}
              onChange={(e) => setSelectedVoiceURI(e.target.value)}
              disabled={isSpeaking}
              className="border border-slate-200/80 dark:border-white/[0.08] bg-white dark:bg-[#161926] text-slate-800 dark:text-slate-200 text-xs rounded-xl px-3 py-2 focus:outline-hidden font-mono max-w-[150px] truncate shadow-xs"
              title="Select speech synthesis voice"
            >
              {voices.map((v) => (
                <option key={v.voiceURI} value={v.voiceURI}>
                  {v.name} ({v.lang})
                </option>
              ))}
            </select>
          )}

          {/* Speak Button */}
          <button
            type="button"
            onClick={handleSpeak}
            disabled={isTextEmpty || !isSpeechSupported || isSpeaking}
            className={`inline-flex items-center space-x-1.5 px-4 py-2 rounded-xl text-xs sm:text-sm font-semibold text-white transition-all shadow-md disabled:opacity-40 disabled:cursor-not-allowed ${
              isSpeaking
                ? 'bg-gradient-to-r from-indigo-600 to-violet-600 animate-pulse shadow-indigo-500/25'
                : 'bg-gradient-to-r from-emerald-600 to-teal-600 hover:from-emerald-700 hover:to-teal-700 shadow-emerald-500/25'
            }`}
            title="Read sentence aloud in English"
          >
            <Volume2 className="w-4 h-4" />
            <span>{isSpeaking ? 'Speaking...' : 'Speak'}</span>
          </button>

          {/* Stop Speech */}
          {isSpeaking && (
            <button
              type="button"
              onClick={stopSpeech}
              className="inline-flex items-center space-x-1.5 px-3 py-2 rounded-xl text-xs sm:text-sm font-semibold bg-rose-600 hover:bg-rose-700 text-white transition-colors shadow-sm"
              title="Stop audio playback"
            >
              <Square className="w-3.5 h-3.5 fill-white" />
              <span>Stop</span>
            </button>
          )}
        </div>
      </div>

      {/* Voice Status & Error Alerts */}
      {speechError && (
        <div className="p-3 rounded-xl bg-amber-500/10 border border-amber-500/20 text-xs text-amber-700 dark:text-amber-300 flex items-start space-x-2">
          <AlertTriangle className="w-4 h-4 shrink-0 text-amber-500 mt-0.5" />
          <span>{speechError}</span>
        </div>
      )}

      {!isSpeechSupported && (
        <p className="font-mono text-[11px] text-slate-400 italic">
          Web Speech API is not supported by your current browser environment.
        </p>
      )}
    </div>
  );
}