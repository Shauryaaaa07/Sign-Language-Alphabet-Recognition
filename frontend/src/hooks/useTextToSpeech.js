import { useState, useEffect, useRef, useCallback } from 'react';
import {
  canSpeakText,
  filterEnglishVoices,
  getDefaultVoiceURI,
} from '../utils/speechLogic';

/**
 * useTextToSpeech Hook
 * ====================
 * Manages browser-native SpeechSynthesis lifecycle, asynchronous voice discovery,
 * utterance configuration, overlap prevention, and state transitions.
 */
export function useTextToSpeech() {
  const isSupported =
    typeof window !== 'undefined' && 'speechSynthesis' in window;

  const [speechStatus, setSpeechStatus] = useState(() =>
    isSupported ? 'ready' : 'unavailable'
  );
  const [errorMessage, setErrorMessage] = useState(null);
  const [voices, setVoices] = useState([]);
  const [selectedVoiceURI, setSelectedVoiceURI] = useState('');

  const utteranceRef = useRef(null);

  // Initialize SpeechSynthesis and subscribe to voice changes
  useEffect(() => {
    if (!isSupported) {
      return;
    }

    const synth = window.speechSynthesis;

    const populateVoices = () => {
      try {
        const available = synth.getVoices() || [];
        if (available.length > 0) {
          const filtered = filterEnglishVoices(available);
          setVoices(filtered);

          setSelectedVoiceURI((prev) => {
            if (prev && filtered.some((v) => v.voiceURI === prev)) {
              return prev;
            }
            return getDefaultVoiceURI(filtered);
          });
        }
      } catch (err) {
        console.warn('SpeechSynthesis voice discovery warning:', err);
      }
    };

    populateVoices();

    // Listen for asynchronous voice list population (Chrome, Edge)
    if (synth.onvoiceschanged !== undefined) {
      synth.onvoiceschanged = populateVoices;
    }

    // Teardown: cancel any in-flight speech when component unmounts
    return () => {
      try {
        synth.cancel();
      } catch {
        // Safe teardown
      }
    };
  }, [isSupported]);

  /**
   * Immediately stops ongoing speech and cancels queued utterances.
   */
  const stop = useCallback(() => {
    if (!isSupported) return;
    try {
      window.speechSynthesis.cancel();
    } catch {
      // Safe teardown
    }
    setSpeechStatus('ready');
    setErrorMessage(null);
  }, [isSupported]);

  /**
   * Speaks the provided text using the selected or default English voice.
   * Cancels any active utterance before starting to prevent overlapping speech.
   */
  const speak = useCallback(
    (textToSpeak) => {
      if (!isSupported) {
        setSpeechStatus('unavailable');
        setErrorMessage('Speech synthesis is not supported in this browser.');
        return;
      }

      if (!canSpeakText(textToSpeak)) {
        return;
      }

      const synth = window.speechSynthesis;

      // Rule: cancel previous speech before starting a new utterance to prevent overlap
      try {
        synth.cancel();
      } catch {
        // Safe cancellation
      }

      const utterance = new SpeechSynthesisUtterance(textToSpeak.trim());
      utteranceRef.current = utterance;

      // Sensible speech settings
      utterance.rate = 1.0;
      utterance.pitch = 1.0;
      utterance.volume = 1.0;

      // Assign chosen voice
      const allAvailable = synth.getVoices() || [];
      const chosenVoice =
        allAvailable.find((v) => v.voiceURI === selectedVoiceURI) ||
        allAvailable.find((v) => v.lang && v.lang.toLowerCase().startsWith('en')) ||
        null;

      if (chosenVoice) {
        utterance.voice = chosenVoice;
        utterance.lang = chosenVoice.lang;
      } else {
        utterance.lang = 'en-US';
      }

      utterance.onstart = () => {
        setSpeechStatus('speaking');
        setErrorMessage(null);
      };

      utterance.onend = () => {
        setSpeechStatus('finished');
      };

      utterance.onerror = (event) => {
        // Intentional cancellation/interruption is normal behavior, not a failure
        if (event.error === 'canceled' || event.error === 'interrupted') {
          setSpeechStatus('ready');
          return;
        }
        setSpeechStatus('error');
        setErrorMessage(
          event.error ? `Speech error: ${event.error}` : 'Speech synthesis failed.'
        );
      };

      try {
        synth.speak(utterance);
      } catch (err) {
        setSpeechStatus('error');
        setErrorMessage(err.message || 'Failed to start speech.');
      }
    },
    [isSupported, selectedVoiceURI]
  );

  return {
    speechStatus,
    errorMessage,
    voices,
    selectedVoiceURI,
    setSelectedVoiceURI,
    speak,
    stop,
    isSupported,
  };
}
