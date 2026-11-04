/**
 * Speech Logic Utilities
 * ======================
 * Pure helper functions for text-to-speech voice filtering, text validation,
 * speech settings, and utterance configuration.
 */

/**
 * Validates whether the provided text is eligible for speech synthesis.
 * Must be non-empty and contain at least one non-whitespace character.
 *
 * @param {string} text - Candidate text to speak.
 * @returns {boolean} - True if eligible, false otherwise.
 */
export function canSpeakText(text) {
  if (!text || typeof text !== 'string') return false;
  return text.trim().length > 0;
}

/**
 * Filters a list of SpeechSynthesisVoice objects, prioritizing English voices.
 * If no English voices exist, falls back to the full voice list.
 *
 * @param {Array<{ lang: string, voiceURI: string, name: string }>} voices
 * @returns {Array<{ lang: string, voiceURI: string, name: string }>}
 */
export function filterEnglishVoices(voices) {
  if (!Array.isArray(voices) || voices.length === 0) return [];
  const enVoices = voices.filter(
    (v) => v && typeof v.lang === 'string' && v.lang.toLowerCase().startsWith('en')
  );
  return enVoices.length > 0 ? enVoices : voices;
}

/**
 * Selects the optimal default voice from a voice list:
 * Prefers an English default voice, then any English voice, then the first available voice.
 *
 * @param {Array<{ lang: string, voiceURI: string, default?: boolean }>} voiceList
 * @returns {string} - voiceURI of the best matching voice, or empty string.
 */
export function getDefaultVoiceURI(voiceList) {
  if (!Array.isArray(voiceList) || voiceList.length === 0) return '';
  const defaultEn = voiceList.find(
    (v) => v.default && v.lang && v.lang.toLowerCase().startsWith('en')
  );
  if (defaultEn) return defaultEn.voiceURI;

  const firstEn = voiceList.find(
    (v) => v.lang && v.lang.toLowerCase().startsWith('en')
  );
  if (firstEn) return firstEn.voiceURI;

  return voiceList[0] ? voiceList[0].voiceURI : '';
}

/**
 * Speech status badge configuration for UI rendering.
 */
export const SPEECH_STATUS_CONFIG = {
  ready: {
    label: 'Speech Ready',
    bg: 'bg-slate-100',
    border: 'border-slate-200',
    text: 'text-slate-600',
    dot: 'bg-slate-400',
  },
  speaking: {
    label: 'Speaking...',
    bg: 'bg-blue-50',
    border: 'border-blue-200',
    text: 'text-blue-700',
    dot: 'bg-blue-500 animate-ping',
  },
  finished: {
    label: 'Speech Finished',
    bg: 'bg-emerald-50',
    border: 'border-emerald-200',
    text: 'text-emerald-700',
    dot: 'bg-emerald-500',
  },
  unavailable: {
    label: 'Speech Unavailable',
    bg: 'bg-amber-50',
    border: 'border-amber-200',
    text: 'text-amber-700',
    dot: 'bg-amber-500',
  },
  error: {
    label: 'Speech Error',
    bg: 'bg-rose-50',
    border: 'border-rose-200',
    text: 'text-rose-700',
    dot: 'bg-rose-500',
  },
};
