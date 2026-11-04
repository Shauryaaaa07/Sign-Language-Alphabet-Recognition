# Milestone 4.4 Report: Recognized Letter Text Builder Integration

**Project:** AI-Based Indian Sign Language (ISL) Alphabet Recognition and Voice Conversion System  
**Phase:** Phase 4 — Full-Stack Application Integration  
**Milestone:** 4.4 — Recognized Letter Text Builder  
**Date:** November 1, 2026  
**Status:** COMPLETE (Ready for User Review)

---

## 1. Executive Summary

Milestone 4.4 integrates an interactive text assembly system into the Indian Sign Language recognition frontend. Users can assemble individually recognized fingerspelling signs (A–Z) from both Image Upload and Live Webcam recognition modes into coherent words and sentences, complete with editing, space insertion, character deletion, and text metrics.

Key achievements:
1. **Dedicated TextBuilder Component ([`frontend/src/components/TextBuilder.jsx`](file:///c:/Users/shaur/OneDrive/Desktop/Sign%20Language%20Alphabet%20Recognition/frontend/src/components/TextBuilder.jsx)):** Created a responsive, accessible sentence constructor card displaying real-time assembled text, word/character metrics, ready-to-add letter indicator, and full text editing actions.
2. **Recognition Integration:** Wired both Image Upload predictions and Live Webcam stable classifications (3 consecutive frames with confidence $\ge 0.75$) into the shared active letter pipeline.
3. **Intentional Insertion Guard:** Completely avoids runaway automatic insertion while maintaining user autonomy. Letters are appended strictly when the user triggers "Add Letter", preventing inadvertent repeated character generation while holding static signs.
4. **State Persistence Across View Modes:** Lifted text builder state to the top-level [`App.jsx`](file:///c:/Users/shaur/OneDrive/Desktop/Sign%20Language%20Alphabet%20Recognition/frontend/src/App.jsx) container, guaranteeing that switching between "Upload Image" and "Live Webcam" modes never wipes or alters assembled text.
5. **Comprehensive Verification:** 11/11 automated unit tests passed, zero linter warnings (`oxlint`), and successful production build (`vite build`).

---

## 2. Architecture & State Management

### 2.1 State Lifting in `App.jsx`
To ensure that assembled sentences survive navigation between Image Upload and Webcam recognition modes:
- `assembledText` (`string`) and `lastRecognizedLetter` (`string | null`) are owned by `App.jsx`.
- When switching between modes (`'upload'` $\leftrightarrow$ `'webcam'`), only the active input cards unmount and remount.
- `TextBuilder` remains persistently mounted and bound to `App.jsx` state, ensuring zero accidental text loss.
- Webcam hardware tracks and capture loops are cleanly stopped when switching away from webcam mode, without affecting text state.

### 2.2 Component Hierarchy & Data Flow
```
App.jsx (Owns: assembledText, lastRecognizedLetter, activeMode)
 ├── Header.jsx (Backend health & status)
 ├── [Mode Switch: Upload vs. Webcam]
 │    ├── Upload Mode:
 │    │    ├── ImageUploader.jsx
 │    │    └── PredictionResult.jsx (Emits: onAddLetterDirect -> App.jsx)
 │    └── Webcam Mode:
 │         └── WebcamRecognition.jsx (Emits: onStablePredictionChange, onAddLetterDirect -> App.jsx)
 ├── TextBuilder.jsx (Receives: text, onTextChange, activeLetter)
 └── Alphabet Reference Card (Interactive letter preview & selector)
```

---

## 3. Text Builder Features & Editing Controls

| Control | Action | Validation & Edge Case Handling |
| :--- | :--- | :--- |
| **Add Letter** | Appends currently selected active letter (e.g., `'A'`) to assembled text | Accepts only valid uppercase single characters A–Z (`/^[A-Z]$/`). Disabled if no valid letter is active. Allows intentional consecutive repeats (e.g., `"LL"` in `"HELLO"`). |
| **Space** | Appends a single space separator (`" "`) | Disallowed when text is empty (no leading space). Disallowed if text already ends with a space (prevents double spaces). |
| **Delete** | Removes the final character (Backspace) | Safe on empty strings (no-op). Disabled when text length is zero. |
| **Clear Text** | Resets assembled text to empty string (`""`) | Features inline confirmation for texts longer than 3 characters (`"Confirm Clear?"` for 3 seconds) to prevent accidental loss without annoying native alert popups. |
| **Copy Text** | Copies assembled sentence to system clipboard | Includes fallback for non-secure contexts and displays a transient `"Copied!"` indicator for 2 seconds. |
| **Metrics** | Real-time Character and Word counters | Dynamically computes length and word count using boundary-safe regex (`/\s+/`). |

---

## 4. Recognition Pipeline Integration

### 4.1 Live Webcam Recognition Integration
- In [`WebcamRecognition.jsx`](file:///c:/Users/shaur/OneDrive/Desktop/Sign%20Language%20Alphabet%20Recognition/frontend/src/components/WebcamRecognition.jsx), when the 3-frame stability threshold ($\text{confidence} \ge 0.75$) is satisfied:
  ```javascript
  if (consecutiveCountRef.current >= REQUIRED_CONSECUTIVE_FRAMES) {
    setStablePrediction(letter);
    if (onStablePredictionChange) {
      onStablePredictionChange(letter);
    }
  }
  ```
- This updates `lastRecognizedLetter` in `App.jsx`.
- In `TextBuilder`, the button dynamically renders `Add Letter (L)` with a green "Ready to Add" badge.
- An optional quick-add shortcut button `Add 'L' to Sentence` is also provided directly on the Stable Prediction card.

### 4.2 Image Upload Recognition Integration
- In [`App.jsx`](file:///c:/Users/shaur/OneDrive/Desktop/Sign%20Language%20Alphabet%20Recognition/frontend/src/App.jsx), when `handlePredict` returns a valid inference response:
  ```javascript
  const response = await predictSignGesture(selectedFile);
  setPrediction(response);
  if (response && response.predicted_letter) {
    setLastRecognizedLetter(response.predicted_letter.toUpperCase());
  }
  ```
- In [`PredictionResult.jsx`](file:///c:/Users/shaur/OneDrive/Desktop/Sign%20Language%20Alphabet%20Recognition/frontend/src/components/PredictionResult.jsx), an `Add '[Letter]' to Sentence` action button is available directly beneath the predicted letter badge.

---

## 5. Verification & Testing

### 5.1 Static Code Quality & Linter
```bash
> cd frontend && npm run lint
oxlint
Found 0 warnings and 0 errors.
Finished in 21ms on 13 files with 104 rules using 11 threads.
```

### 5.2 Production Packaging Build
```bash
> cd frontend && npm run build
vite v8.3.5 building client environment for production...
✓ 24 modules transformed.
dist/index.html                   0.45 kB │ gzip:  0.29 kB
dist/assets/index-CUOxlNcZ.css   36.24 kB │ gzip:  7.08 kB
dist/assets/index-Sxri5vq5.js   264.16 kB │ gzip: 79.42 kB
✓ built in 177ms
```

### 5.3 Automated Unit Tests (`frontend/src/tests/text_builder.test.mjs`)
All 11 automated test cases passed without error:
1. **Test 1 (Add Letter):** Letter `'H'` appended to empty string $\rightarrow$ `'H'`. **(PASS)**
2. **Test 2 (Repeated Letters):** Appended `'E'`, `'L'`, `'L'`, `'O'` $\rightarrow$ `'HELLO'`. Confirms intentional repeats are supported. **(PASS)**
3. **Test 3 (Space Separator & Duplicate Prevention):** Appended space $\rightarrow$ `'HELLO '`. Attempted duplicate space $\rightarrow$ safely preserved as single space `'HELLO '`. Appended `'WORLD'` $\rightarrow$ `'HELLO WORLD'`. **(PASS)**
4. **Test 4 (Delete / Backspace):** Successfully removed trailing characters sequentially: `'HELLO WORL'`, then `'HELLO WOR'`. **(PASS)**
5. **Test 5 (Clear):** Reset text to empty string `""`. **(PASS)**
6. **Test 6 (Empty Text Safety):** Verified that `deleteLastChar('')`, `addSpace('')`, `clearAllText()`, and `calculateTextMetrics('')` execute safely without throwing or mutating. **(PASS)**
7. **Test 7 (Invalid Prediction Rejection):** Verified that non-alphabetic inputs (`'1'`, `'!'`, `'AB'`, `''`, `null`, `undefined`) are safely rejected, while lowercase letters are normalized to uppercase. **(PASS)**
8. **Test 8 (Webcam Integration):** Verified callback simulation adding stable webcam predictions `'I'`, `'S'`, `'L'` $\rightarrow$ `'ISL'`. **(PASS)**
9. **Test 9 (Upload Integration):** Verified callback simulation adding upload prediction `'A'` $\rightarrow$ `'ISLA'`. **(PASS)**
10. **Test 10 (Mode Switching Persistence):** Verified that toggling `activeMode` between `'upload'` and `'webcam'` retains `assembledText` (`'HELLO WORLD'`) and `lastRecognizedLetter`. **(PASS)**
11. **Test 11 (Metrics Calculation):** Verified character count (26) and word count (4) on `'HELLO INDIAN SIGN LANGUAGE'`. **(PASS)**

---

## 6. Changed & Created Files

| File | Status | Description |
| :--- | :--- | :--- |
| [`frontend/src/utils/textBuilderLogic.js`](file:///c:/Users/shaur/OneDrive/Desktop/Sign%20Language%20Alphabet%20Recognition/frontend/src/utils/textBuilderLogic.js) | **Created** | Pure helper functions for letter validation, space handling, deletion, and metrics calculation. |
| [`frontend/src/components/TextBuilder.jsx`](file:///c:/Users/shaur/OneDrive/Desktop/Sign%20Language%20Alphabet%20Recognition/frontend/src/components/TextBuilder.jsx) | **Created** | Interactive sentence constructor component with live display, editing actions, and metrics. |
| [`frontend/src/tests/text_builder.test.mjs`](file:///c:/Users/shaur/OneDrive/Desktop/Sign%20Language%20Alphabet%20Recognition/frontend/src/tests/text_builder.test.mjs) | **Created** | Comprehensive Node.js unit tests verifying all 10 milestone test requirements. |
| [`frontend/src/App.jsx`](file:///c:/Users/shaur/OneDrive/Desktop/Sign%20Language%20Alphabet%20Recognition/frontend/src/App.jsx) | **Updated** | Lifted text builder state, added direct insertion handlers, and integrated TextBuilder. |
| [`frontend/src/components/WebcamRecognition.jsx`](file:///c:/Users/shaur/OneDrive/Desktop/Sign%20Language%20Alphabet%20Recognition/frontend/src/components/WebcamRecognition.jsx) | **Updated** | Emits `onStablePredictionChange` and provides direct add-to-sentence action. |
| [`frontend/src/components/PredictionResult.jsx`](file:///c:/Users/shaur/OneDrive/Desktop/Sign%20Language%20Alphabet%20Recognition/frontend/src/components/PredictionResult.jsx) | **Updated** | Added quick add-to-sentence button for uploaded image predictions. |
| [`docs/reports/TEXT_BUILDER_MILESTONE_4_4_REPORT.md`](file:///c:/Users/shaur/OneDrive/Desktop/Sign%20Language%20Alphabet%20Recognition/docs/reports/TEXT_BUILDER_MILESTONE_4_4_REPORT.md) | **Created** | Comprehensive Milestone 4.4 documentation report. |

---

## 7. Known Limitations & Next Steps

1. **Static Fingerspelling Vocabulary:** Assembled text is formed from individual letter predictions (fingerspelling). Word completions, auto-correct, or grammar correction are not yet applied.
2. **Phase 5 Preparations:** Speech synthesis (Voice Conversion) and text-to-speech (TTS) audio output are reserved for Phase 5.
3. **No Database Persistence:** Assembled sentences exist in React component state for the current user session and are not stored in a database.

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
	docs/reports/WEBCAM_MILESTONE_4_3_REPORT.md
	frontend/src/components/
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
*(No commits or git pushes executed in adherence with project guidelines).*
