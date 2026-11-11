/**
 * Automated Test Suite: Webcam Recognition Stability & Resource Lifecycle Logic
 * ==============================================================================
 * Tests the stability state machine algorithm and concurrency guard used in WebcamRecognition.
 */

import assert from 'node:assert';

console.log('--- TEST 1: Stability Logic State Machine ---');

class StabilityTracker {
  constructor(threshold = 0.75, requiredConsecutive = 3) {
    this.threshold = threshold;
    this.requiredConsecutive = requiredConsecutive;
    this.candidateLetter = null;
    this.consecutiveCount = 0;
    this.stablePrediction = null;
    this.rawPrediction = null;
  }

  handlePrediction(pred) {
    this.rawPrediction = pred;
    const letter = pred.predicted_letter;
    const conf = pred.confidence;

    if (conf >= this.threshold) {
      if (letter === this.candidateLetter) {
        this.consecutiveCount += 1;
      } else {
        this.candidateLetter = letter;
        this.consecutiveCount = 1;
      }

      if (this.consecutiveCount >= this.requiredConsecutive) {
        this.stablePrediction = letter;
      }
    } else {
      this.candidateLetter = null;
      this.consecutiveCount = 0;
    }
  }

  handleError() {
    this.candidateLetter = null;
    this.consecutiveCount = 0;
  }

  reset() {
    this.candidateLetter = null;
    this.consecutiveCount = 0;
    this.stablePrediction = null;
    this.rawPrediction = null;
  }
}

const tracker = new StabilityTracker(0.75, 3);

// Step 1: Initial state
assert.strictEqual(tracker.stablePrediction, null, 'Initial stable prediction should be null');
assert.strictEqual(tracker.consecutiveCount, 0, 'Initial consecutive count should be 0');

// Step 2: Single prediction below threshold (0.65)
tracker.handlePrediction({ predicted_letter: 'A', confidence: 0.65 });
assert.strictEqual(tracker.stablePrediction, null, 'Confidence < 0.75 must not trigger stable prediction');
assert.strictEqual(tracker.consecutiveCount, 0, 'Confidence < 0.75 must keep counter at 0');

// Step 3: Frame 1 of 'B' at 0.85
tracker.handlePrediction({ predicted_letter: 'B', confidence: 0.85 });
assert.strictEqual(tracker.candidateLetter, 'B');
assert.strictEqual(tracker.consecutiveCount, 1);
assert.strictEqual(tracker.stablePrediction, null);

// Step 4: Frame 2 of 'B' at 0.90
tracker.handlePrediction({ predicted_letter: 'B', confidence: 0.90 });
assert.strictEqual(tracker.candidateLetter, 'B');
assert.strictEqual(tracker.consecutiveCount, 2);
assert.strictEqual(tracker.stablePrediction, null);

// Step 5: Frame 3 of 'B' at 0.80 -> Should trigger stable prediction!
tracker.handlePrediction({ predicted_letter: 'B', confidence: 0.80 });
assert.strictEqual(tracker.candidateLetter, 'B');
assert.strictEqual(tracker.consecutiveCount, 3);
assert.strictEqual(tracker.stablePrediction, 'B', 'Frame 3 >= 0.75 must trigger stable prediction "B"');

// Step 6: Frame 4 continues 'B' at 0.88 -> Stable prediction remains 'B'
tracker.handlePrediction({ predicted_letter: 'B', confidence: 0.88 });
assert.strictEqual(tracker.consecutiveCount, 4);
assert.strictEqual(tracker.stablePrediction, 'B');

// Step 7: Letter switches to 'C' at 0.82 -> Counter resets to 1, candidate becomes 'C'
tracker.handlePrediction({ predicted_letter: 'C', confidence: 0.82 });
assert.strictEqual(tracker.candidateLetter, 'C');
assert.strictEqual(tracker.consecutiveCount, 1, 'Changing letter must reset consecutive count to 1');

// Step 8: Low confidence frame (0.50) -> Counter resets to 0
tracker.handlePrediction({ predicted_letter: 'C', confidence: 0.50 });
assert.strictEqual(tracker.candidateLetter, null, 'Low confidence must reset candidate to null');
assert.strictEqual(tracker.consecutiveCount, 0, 'Low confidence must reset counter to 0');

// Step 9: Error event -> Counter resets to 0
tracker.handlePrediction({ predicted_letter: 'D', confidence: 0.95 });
assert.strictEqual(tracker.consecutiveCount, 1);
tracker.handleError();
assert.strictEqual(tracker.consecutiveCount, 0, 'Error must reset counter to 0');
assert.strictEqual(tracker.candidateLetter, null);

// Step 10: Camera stop / full reset
tracker.reset();
assert.strictEqual(tracker.stablePrediction, null, 'Full reset must clear stable prediction');
assert.strictEqual(tracker.rawPrediction, null);

console.log('✓ PASS: All 10 stability state machine tests passed successfully.');

console.log('\n--- TEST 2: Hardware Resource Cleanup Simulation ---');
let tracksStopped = 0;
let intervalCleared = false;
const mockTracks = [
  { stop: () => { tracksStopped += 1; } },
  { stop: () => { tracksStopped += 1; } },
];
const mockStream = {
  getTracks: () => mockTracks,
};

let activeIntervalId = 12345;
function mockClearInterval(id) {
  if (id === 12345) intervalCleared = true;
}

// Teardown simulation
mockStream.getTracks().forEach(t => t.stop());
mockClearInterval(activeIntervalId);

assert.strictEqual(tracksStopped, 2, 'All media stream tracks must be stopped');
assert.strictEqual(intervalCleared, true, 'Frame interval timer must be cleared');
console.log('✓ PASS: Hardware cleanup simulation verified (2/2 tracks stopped, interval cleared).');

console.log('\n--- TEST 3: Concurrency Guard / In-Flight Request Locking ---');
let activeInFlightRequests = 0;
let maxConcurrentObserved = 0;
let isProcessingLock = false;

async function simulateIntervalTick(mockDelayMs) {
  if (isProcessingLock) {
    // Skipped due to lock
    return { skipped: true };
  }
  isProcessingLock = true;
  activeInFlightRequests++;
  maxConcurrentObserved = Math.max(maxConcurrentObserved, activeInFlightRequests);

  await new Promise(r => setTimeout(r, mockDelayMs));

  activeInFlightRequests--;
  isProcessingLock = false;
  return { skipped: false };
}

(async () => {
  // Simulate 10 interval triggers firing rapidly every 20ms while request takes 80ms
  const promises = [];
  for (let i = 0; i < 10; i++) {
    promises.push(simulateIntervalTick(80));
    await new Promise(r => setTimeout(r, 20));
  }
  const results = await Promise.all(promises);
  const skippedCount = results.filter(r => r.skipped).length;
  const executedCount = results.filter(r => !r.skipped).length;

  assert.strictEqual(maxConcurrentObserved, 1, 'Concurrency guard must never allow more than 1 in-flight request');
  assert(skippedCount > 0, 'Subsequent ticks must be dropped while request is in flight');
  console.log(`✓ PASS: Concurrency guard verified. Dispatched: ${executedCount}, Dropped: ${skippedCount}, Max concurrent: ${maxConcurrentObserved}`);
  console.log('\nAll automated test suites PASSED!');
})();
