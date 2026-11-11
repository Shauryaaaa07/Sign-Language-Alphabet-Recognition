# Milestone 4.5 Report: Text-to-Speech (Voice Conversion) Integration

**Project:** AI-Based Indian Sign Language (ISL) Alphabet Recognition and Voice Conversion System  
**Phase:** Phase 4 — Full-Stack Application Integration  
**Milestone:** 4.5 — Text-to-Speech (Voice Conversion)  
**Date:** November 1, 2026  
**Status:** COMPLETE (Ready for User Review)

---

## 1. Executive Summary

Milestone 4.5 incorporates browser-native Text-to-Speech (Voice Conversion) into the application, fulfilling the core end-to-end mission of the project: bridging Indian Sign Language alphabet recognition into audible spoken language.

Key accomplishments:
1. **Browser-Native Web Speech API Integration:** Utilizes `window.speechSynthesis` and `SpeechSynthesisUtterance`. Strictly zero external paid APIs, cloud audio tokens, or backend voice dependencies are required.
2. **Whole-Sentence Speech:** Synthesizes the user's intentionally assembled words and sentences from [`TextBuilder.jsx`](file:///c:/Users/shaur/OneDrive/Desktop/Sign%20Language%20Alphabet%20Recognition/frontend/src/components/TextBuilder.jsx), rather than distracting raw per-frame webcam predictions.
3. **Voice Discovery & Language Filtering:** Dynamically queries available system synthesis voices via `speechSynthesis.getVoices()` and filters for English voices (`en-US`, `en-GB`, `en-IN`, etc.), with asynchronous `voiceschanged` event handling and universal fallback.
4. **Lifecycle & Overlap Guard:** Strictly enforces single-utterance concurrency: cancels any active speech before starting a new utterance to eliminate overlapping echoes, and terminates ongoing speech on component teardown.
5. **State & Error Resilience:** Distinct UI states (`ready`, `speaking`, `finished`, `unavailable`, `error`) with graceful normalization of Chromium cancellation interrupts (`canceled`/`interrupted`).
6. **Rigorous Automated Testing:** Verified via 5 automated test suites with mock Web Speech API engines, zero linter warnings (`oxlint`), and successful production build (`vite build`).

---

## 2. Speech Implementation Details

### 2.1 Web Speech API Architecture
The voice conversion system is modularized into two dedicated units:
- [`frontend/src/utils/speechLogic.js`](file:///c:/Users/shaur/OneDrive/Desktop/Sign%20Language%20Alphabet%20Recognition/frontend/src/utils/speechLogic.js): Pure functional utilities for text speech eligibility verification (`canSpeakText`), English voice discovery and filtering (`filterEnglishVoices`), default voice URI resolution (`getDefaultVoiceURI`), and UI badge configuration (`SPEECH_STATUS_CONFIG`).
- [`frontend/src/hooks/useTextToSpeech.js`](file:///c:/Users/shaur/OneDrive/Desktop/Sign%20Language%20Alphabet%20Recognition/frontend/src/hooks/useTextToSpeech.js): React custom hook managing `speechSynthesis` lifecycle, event listeners, utterance instantiation, overlap prevention, and reactive state updates.

### 2.2 Utterance Configuration & Audio Properties
```javascript
const utterance = new SpeechSynthesisUtterance(textToSpeak.trim());

// Sensible, clear speech settings
utterance.rate = 1.0;   // Normal natural cadence
utterance.pitch = 1.0;  // Standard pitch
utterance.volume = 1.0; // Full volume

// Voice binding
if (chosenVoice) {
  utterance.voice = chosenVoice;
  utterance.lang = chosenVoice.lang;
} else {
  utterance.lang = 'en-US';
}
```

---

## 3. Voice Selection & Fallback Behavior

### 3.1 Asynchronous Voice Discovery
Browsers differ in how synthesis voices are loaded:
- **Safari / Firefox:** Voices are often immediately populated on initialization.
- **Google Chrome / Microsoft Edge:** Voices are populated asynchronously after initial page load, dispatching the `speechSynthesis.onvoiceschanged` event.

Our implementation subscribes to `synth.onvoiceschanged = populateVoices` while also executing an immediate discovery pass on mount:
```javascript
const populateVoices = () => {
  const available = synth.getVoices() || [];
  if (available.length > 0) {
    const filtered = filterEnglishVoices(available);
    setVoices(filtered);
    setSelectedVoiceURI((prev) => {
      if (prev && filtered.some((v) => v.voiceURI === prev)) return prev;
      return getDefaultVoiceURI(filtered);
    });
  }
};
```

### 3.2 Prioritization & Fallbacks
1. **English Preference:** Filters all system voices where `v.lang.toLowerCase().startsWith('en')`.
2. **Default English Selection:** Automatically selects the OS default English voice if flagged with `default: true`, or the first available English voice.
3. **OS Fallback:** If an operating system has no English voice installed, `filterEnglishVoices` falls back to the full voice list, selecting the first available voice without throwing runtime errors.
4. **Interactive Selector:** If multiple English voices are installed on the user's OS, a clean dropdown `<select>` menu allows switching between voices (e.g. Microsoft David, Microsoft Zira, Google US English).

---

## 4. Speech State Management & Concurrency Guards

### 4.1 State Machine
The speech controller transitions across 5 deterministic states:

| State | Badge Style | Trigger Event |
| :--- | :--- | :--- |
| **`ready`** | Grey pill (`bg-slate-100 text-slate-600`) | Initial state, or after stop / cancellation. |
| **`speaking`** | Blue pulsing pill (`bg-blue-50 text-blue-700 animate-ping`) | Fired by `utterance.onstart`. |
| **`finished`** | Emerald pill (`bg-emerald-50 text-emerald-700`) | Fired by `utterance.onend`. |
| **`unavailable`** | Amber pill (`bg-amber-50 text-amber-700`) | `!('speechSynthesis' in window)`. |
| **`error`** | Rose pill (`bg-rose-50 text-rose-700`) | Fired by `utterance.onerror` (real failure). |

### 4.2 Overlap Prevention & Safe Cancellation
To prevent unintelligible overlapping audio when clicking "Speak" multiple times:
```javascript
// Rule: Cancel previous speech before starting a new utterance
try {
  synth.cancel();
} catch {
  // Safe cancellation
}
synth.speak(utterance);
```

### 4.3 Chromium Cancellation Error Normalization
In Chromium-based browsers (Chrome, Edge, Brave), invoking `speechSynthesis.cancel()` dispatches an `onerror` event with `event.error === 'canceled'` or `'interrupted'`. Treating this as an error would flash false alarm banners to the user.
Our handler explicitly intercepts these cancellation events:
```javascript
utterance.onerror = (event) => {
  if (event.error === 'canceled' || event.error === 'interrupted') {
    setSpeechStatus('ready');
    return;
  }
  setSpeechStatus('error');
  setErrorMessage(event.error ? `Speech error: ${event.error}` : 'Speech synthesis failed.');
};
```

### 4.4 Lifecycle Teardown
When `<TextBuilder>` or `<App>` unmounts:
```javascript
return () => {
  try {
    synth.cancel();
  } catch {
    // Safe teardown
  }
};
```
All audio speech synthesis immediately terminates, ensuring no background speech continues after navigation.

---

## 5. Verification & Testing

### 5.1 Static Code Quality & Linter
```bash
> cd frontend && npm run lint
oxlint
Found 0 warnings and 0 errors.
Finished in 46ms on 16 files with 104 rules using 11 threads.
```

### 5.2 Production Packaging Build
```bash
> cd frontend && npm run build
vite v8.3.5 building client environment for production...
✓ 26 modules transformed.
dist/index.html                   0.45 kB │ gzip:  0.29 kB
dist/assets/index-NgiO0X9K.css   37.86 kB │ gzip:  7.29 kB
dist/assets/index-CsS28am2.js   271.24 kB │ gzip: 81.09 kB
✓ built in 293ms
```

### 5.3 Automated Unit Tests (`frontend/src/tests/speech_synthesis.test.mjs`)
All 5 automated test suites executed and passed:
1. **Test 1 (Text Eligibility):** Confirmed empty strings, whitespace, null, and undefined are rejected (`canSpeakText` returns `false`), while single characters and multi-word sentences are approved. **(PASS)**
2. **Test 2 (Voice Discovery & Prioritization):** Confirmed German/Hindi voices are filtered out when English voices are present, verified default voice selection (Zira), and verified fallback to all voices when no English voices exist. **(PASS)**
3. **Test 3 (Mock SpeechSynthesis State Machine & Overlap Prevention):**
   - Utterance dispatch transitioned status to `speaking`.
   - `finishCurrent()` transitioned status to `finished`.
   - Repeated `speakText()` calls triggered `cancel()` on previous utterances before queuing new ones.
   - `stopSpeaking()` immediately halted playback and reset status to `ready`.
   - Synthetic error (`audio-busy`) transitioned status to `error` and populated descriptive error message. **(PASS)**
4. **Test 4 (Browser Support Guard):** Verified fallback initialization to `unavailable` when `speechSynthesis` is absent. **(PASS)**
5. **Test 5 (TextBuilder Integration):** Tested end-to-end sequence: `addLetter('H')`, `addLetter('I')`, `addSpace()`, `addLetter('A')`, `addLetter('L')`, `addLetter('L')` $\rightarrow$ `'HI ALL'`. Executed speech synthesis, then performed character deletion and clear operations. **(PASS)**

### 5.4 Actual Browser Audio Testing Status (Honesty Notice)
- **Automated / Mock Status:** Fully verified through mock Web Speech API classes, state machine simulations, edge case testing, linter, and production build packaging.
- **Physical Speaker / Sound Card Boundary:** In headless development and CLI test environments, hardware audio DACs, sound cards, and physical speakers cannot be listened to by automated processes. Actual acoustic sound output must be verified interactively by an end user with speakers/headphones enabled in a browser session (Chrome/Firefox/Edge) at `http://localhost:5173`.

---

## 6. Changed & Created Files

| File | Status | Description |
| :--- | :--- | :--- |
| [`frontend/src/utils/speechLogic.js`](file:///c:/Users/shaur/OneDrive/Desktop/Sign%20Language%20Alphabet%20Recognition/frontend/src/utils/speechLogic.js) | **Created** | Pure helper functions for speech eligibility, English voice filtering, and UI status configurations. |
| [`frontend/src/hooks/useTextToSpeech.js`](file:///c:/Users/shaur/OneDrive/Desktop/Sign%20Language%20Alphabet%20Recognition/frontend/src/hooks/useTextToSpeech.js) | **Created** | React custom hook managing `speechSynthesis` lifecycle, asynchronous voices, overlap prevention, and error handling. |
| [`frontend/src/components/TextBuilder.jsx`](file:///c:/Users/shaur/OneDrive/Desktop/Sign%20Language%20Alphabet%20Recognition/frontend/src/components/TextBuilder.jsx) | **Updated** | Integrated Voice Conversion section with Speak button, Stop button, voice selector, and real-time status pill. |
| [`frontend/src/tests/speech_synthesis.test.mjs`](file:///c:/Users/shaur/OneDrive/Desktop/Sign%20Language%20Alphabet%20Recognition/frontend/src/tests/speech_synthesis.test.mjs) | **Created** | Automated unit tests simulating Web Speech API operations, state transitions, and concurrency. |
| [`docs/reports/TEXT_TO_SPEECH_MILESTONE_4_5_REPORT.md`](file:///c:/Users/shaur/OneDrive/Desktop/Sign%20Language%20Alphabet%20Recognition/docs/reports/TEXT_TO_SPEECH_MILESTONE_4_5_REPORT.md) | **Created** | Comprehensive Milestone 4.5 documentation report. |

---

## 7. Known Limitations & Next Steps

1. **Browser Engine Variability:** Web Speech synthesis voice quality depends on the host operating system's installed voices (e.g. SAPI5 on Windows, AVFoundation on macOS, eSpeak on Linux).
2. **User Gesture Requirement:** Some mobile browsers (Safari on iOS) require a direct user touch gesture to initiate audio playback. Because our Speak button is explicitly clicked by the user, this compliance requirement is naturally satisfied.
3. **No Microphone / Audio Input:** The system performs text-to-speech output only; voice-to-sign input is outside project scope.

---

## 8. Git Status

```bash
On branch main
Changes not staged for commit:
	modified:   frontend/src/App.jsx

Untracked files:
	backend/README.md
	backend/config.py
	backend/main.py
	backend/model_loader.py
	backend/prediction.py
	backend/schemas.py
	backend/tests/
	docs/reports/AUGMENTATION_SAMPLE_REVIEW.png
	docs/reports/BACKEND_MILESTONE_4_1_REPORT.md
	docs/reports/BASELINE_TRAINING_REPORT.md
	docs/reports/CLEANED_DATASET_VERIFICATION.md
	docs/reports/CLEANING_SIMULATION_REPORT.md
	docs/reports/CNN_MODEL_ARCHITECTURE.md
	docs/reports/DATASET_AUDIT_REPORT.md
	docs/reports/DATASET_CLEANING_PLAN.md
	docs/reports/EXCLUDED_FILES_MANIFEST.json
	docs/reports/FINAL_MODEL_EVALUATION_REPORT.md
	docs/reports/FRONTEND_MILESTONE_4_2_REPORT.md
	docs/reports/TEXT_BUILDER_MILESTONE_4_4_REPORT.md
	docs/reports/TEXT_TO_SPEECH_MILESTONE_4_5_REPORT.md
	docs/reports/WEBCAM_MILESTONE_4_3_REPORT.md
	frontend/src/components/
	frontend/src/hooks/
	frontend/src/services/
	frontend/src/tests/
	frontend/src/utils/
	results/classification_report.csv
	results/confusion_matrix.png
	results/per_class_metrics.png
	results/test_predictions.csv
	results/training_accuracy.png
	results/training_history.csv
	results/training_loss.png
	training/build_clean_dataset.py
	training/data_pipeline.py
	training/evaluate_model.py
	training/inspect_dataset.py
	training/label_classes.json
	training/model.py
	training/simulate_dataset_cleaning.py
	training/train_model.py
```
*(No commits or git pushes executed in compliance with project instructions).*
