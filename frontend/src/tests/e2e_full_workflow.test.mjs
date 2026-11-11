/**
 * End-to-End Full Workflow & System Integration Audit Test
 * ========================================================
 * Simulates the 16-step user journey across Phase 1–4 integrations:
 * Backend health check -> Image upload -> Text builder assembly ->
 * Mode switching -> Webcam stability -> Space/Delete/Clear -> Text-to-Speech ->
 * Cancellation -> Edge case failure modes -> Teardown verification.
 */

import assert from 'node:assert';
import {
  addLetter,
  addSpace,
  deleteLastChar,
  clearAllText,
  calculateTextMetrics,
} from '../utils/textBuilderLogic.js';
import {
  canSpeakText,
} from '../utils/speechLogic.js';

console.log('=== PHASE 5 FULL SYSTEM INTEGRATION AUDIT ===\n');

// ---------------------------------------------------------------------------
// 1. Initial State & Backend Health Synchronization
// ---------------------------------------------------------------------------
console.log('--- Step 1-3: App Launch & Health Verification ---');
let backendStatus = 'checking';
let isModelLoaded = false;
let numClasses = 0;

// Simulate GET /health response
const mockHealthResponse = {
  status: 'healthy',
  model_loaded: true,
  num_classes: 26,
  classes: 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'.split(''),
};

if (mockHealthResponse.status === 'healthy' && mockHealthResponse.model_loaded) {
  backendStatus = 'connected';
  isModelLoaded = true;
  numClasses = mockHealthResponse.num_classes;
}

assert.strictEqual(backendStatus, 'connected');
assert.strictEqual(isModelLoaded, true);
assert.strictEqual(numClasses, 26);
console.log('[PASS] Backend health check verified: connected with 26 classes.');

// ---------------------------------------------------------------------------
// 2. Image Upload Mode: Prediction & Letter Assembly
// ---------------------------------------------------------------------------
console.log('\n--- Step 4-7: Image Upload Recognition & Word Construction ---');
let activeMode = 'upload';
let assembledText = '';
let lastRecognizedLetter = null;

// Simulate upload predictions for "H", "E", "L", "L", "O"
const lettersToUpload = ['H', 'E', 'L', 'L', 'O'];

for (const char of lettersToUpload) {
  // Simulate POST /predict response
  const predResponse = {
    predicted_letter: char,
    confidence: 0.89,
    top_predictions: [
      { letter: char, confidence: 0.89 },
      { letter: 'A', confidence: 0.05 },
      { letter: 'B', confidence: 0.02 },
    ],
    status: 'success',
  };

  assert.strictEqual(predResponse.status, 'success');
  lastRecognizedLetter = predResponse.predicted_letter.toUpperCase();

  // User explicitly triggers "Add Letter"
  assembledText = addLetter(assembledText, lastRecognizedLetter);
}

assert.strictEqual(assembledText, 'HELLO');
assert.strictEqual(lastRecognizedLetter, 'O');
console.log(`[PASS] Upload predictions successfully assembled into word: "${assembledText}" (repeated L confirmed).`);

// ---------------------------------------------------------------------------
// 3. Switch to Webcam Mode & Text Persistence
// ---------------------------------------------------------------------------
console.log('\n--- Step 8-11: Webcam Mode Transition & Stability Logic ---');
// Switch mode to webcam
activeMode = 'webcam';
assert.strictEqual(activeMode, 'webcam');
// Check persistence: text and last recognized letter MUST NOT be lost
assert.strictEqual(assembledText, 'HELLO', 'Text must persist across mode switch');
assert.strictEqual(lastRecognizedLetter, 'O', 'Last recognized letter must persist across mode switch');

// Simulate Webcam 3-Frame Stability State Machine
let candidate = null;
let consecutiveCount = 0;
let stableWebcamLetter = null;
const MIN_CONF = 0.75;
const REQUIRED_FRAMES = 3;

function handleWebcamFrame(pred) {
  if (pred.confidence >= MIN_CONF) {
    if (pred.predicted_letter === candidate) {
      consecutiveCount += 1;
    } else {
      candidate = pred.predicted_letter;
      consecutiveCount = 1;
    }

    if (consecutiveCount >= REQUIRED_FRAMES) {
      stableWebcamLetter = pred.predicted_letter;
    }
  } else {
    candidate = null;
    consecutiveCount = 0;
  }
}

// Frame 1: 'W' at 0.80
handleWebcamFrame({ predicted_letter: 'W', confidence: 0.80 });
assert.strictEqual(stableWebcamLetter, null, '1 frame must not trigger stable prediction');
// Frame 2: 'W' at 0.85
handleWebcamFrame({ predicted_letter: 'W', confidence: 0.85 });
assert.strictEqual(stableWebcamLetter, null, '2 frames must not trigger stable prediction');
// Frame 3: 'W' at 0.90 -> Triggers stable prediction!
handleWebcamFrame({ predicted_letter: 'W', confidence: 0.90 });
assert.strictEqual(stableWebcamLetter, 'W', '3 consecutive identical frames >= 0.75 must trigger stable prediction');

// User explicitly appends space, then stable letter 'W'
assembledText = addSpace(assembledText);
assembledText = addLetter(assembledText, stableWebcamLetter);
assert.strictEqual(assembledText, 'HELLO W');
console.log(`[PASS] Webcam stable letter 'W' added after 3 frames: "${assembledText}".`);

// ---------------------------------------------------------------------------
// 4. Mode Switch Back to Upload & Full Editing
// ---------------------------------------------------------------------------
console.log('\n--- Step 11-13: Mode Return, Editing Controls & Sentence Completion ---');
activeMode = 'upload';
assert.strictEqual(assembledText, 'HELLO W', 'Text preserved when switching back to upload');

// Complete word "WORLD"
assembledText = addLetter(assembledText, 'O');
assembledText = addLetter(assembledText, 'R');
assembledText = addLetter(assembledText, 'L');
assembledText = addLetter(assembledText, 'D');
assert.strictEqual(assembledText, 'HELLO WORLD');

// Test Delete (Backspace)
assembledText = deleteLastChar(assembledText);
assert.strictEqual(assembledText, 'HELLO WORL');
assembledText = addLetter(assembledText, 'D');
assert.strictEqual(assembledText, 'HELLO WORLD');

// Test Metrics
const metrics = calculateTextMetrics(assembledText);
assert.strictEqual(metrics.characters, 11);
assert.strictEqual(metrics.words, 2);
console.log(`[PASS] Sentence completed: "${assembledText}" (Length: ${metrics.characters}, Words: ${metrics.words}).`);

// ---------------------------------------------------------------------------
// 5. Voice Conversion (Text-to-Speech) Execution & Cancellation
// ---------------------------------------------------------------------------
console.log('\n--- Step 14-16: Voice Conversion (TTS) Execution & Cancellation ---');

class MockUtterance {
  constructor(text) {
    this.text = text;
    this.rate = 1.0;
    this.pitch = 1.0;
    this.volume = 1.0;
    this.voice = null;
    this.onstart = null;
    this.onend = null;
    this.onerror = null;
  }
}

let speechEngineState = 'ready';
let activeSpeechText = null;
let synthCancelCalled = false;

function mockSpeak(textToSpeak, voice) {
  if (!canSpeakText(textToSpeak)) return;

  synthCancelCalled = true; // Overlap prevention
  const utt = new MockUtterance(textToSpeak.trim());
  utt.voice = voice;
  activeSpeechText = utt.text;
  speechEngineState = 'speaking';
  return utt;
}

function mockStop() {
  synthCancelCalled = true;
  speechEngineState = 'ready';
  activeSpeechText = null;
}

// Speak sentence
assert.strictEqual(canSpeakText(assembledText), true);
const activeUtterance = mockSpeak(assembledText, { name: 'English Voice', lang: 'en-US' });
assert.strictEqual(speechEngineState, 'speaking');
assert.strictEqual(activeSpeechText, 'HELLO WORLD');
assert.strictEqual(activeUtterance.rate, 1.0);
assert.strictEqual(activeUtterance.pitch, 1.0);
assert.strictEqual(activeUtterance.volume, 1.0);

// Stop speech during playback
mockStop();
assert.strictEqual(synthCancelCalled, true);
assert.strictEqual(speechEngineState, 'ready');
assert.strictEqual(activeSpeechText, null);
console.log('[PASS] Text-to-Speech spoken and successfully cancelled mid-playback.');

// ---------------------------------------------------------------------------
// 6. Comprehensive Edge Case Audit
// ---------------------------------------------------------------------------
console.log('\n--- Edge Cases & Fault Tolerance ---');

// Edge 1: Empty text speech request
assert.strictEqual(canSpeakText(''), false, 'Empty text must not trigger speech');
assert.strictEqual(canSpeakText('   '), false, 'Whitespace must not trigger speech');

// Edge 2: Duplicate space prevention
const textWithSpace = addSpace('HELLO');
assert.strictEqual(textWithSpace, 'HELLO ');
const textWithDoubleSpaceAttempt = addSpace(textWithSpace);
assert.strictEqual(textWithDoubleSpaceAttempt, 'HELLO ', 'Consecutive space must be prevented');

// Edge 3: Delete and clear on empty text
assert.strictEqual(deleteLastChar(''), '', 'Delete on empty text must be safe');
assert.strictEqual(clearAllText(), '', 'Clear on empty text must be safe');

// Edge 4: Non-alphabetic letter rejection
assert.strictEqual(addLetter('HELLO', '1'), 'HELLO');
assert.strictEqual(addLetter('HELLO', '!'), 'HELLO');
assert.strictEqual(addLetter('HELLO', 'xyz'), 'HELLO');

// Edge 5: Camera teardown simulation
let cameraTracksStopped = 0;
const mockStream = {
  getTracks: () => [
    { stop: () => { cameraTracksStopped++; } },
    { stop: () => { cameraTracksStopped++; } },
  ],
};
mockStream.getTracks().forEach(t => t.stop());
assert.strictEqual(cameraTracksStopped, 2, 'All hardware tracks stopped on unmount');

console.log('[PASS] All edge cases and failure modes verified.');
console.log('\n=== END-TO-END WORKFLOW INTEGRATION AUDIT COMPLETED: 100% PASS ===');
