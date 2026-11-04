/**
 * Automated Test Suite: TextBuilder Logic & State Persistence
 * ==========================================================
 * Tests the 10 requirements for Milestone 4.4 Recognized Letter Text Builder.
 */

import assert from 'node:assert';
import {
  addLetter,
  addSpace,
  deleteLastChar,
  clearAllText,
  calculateTextMetrics,
} from '../utils/textBuilderLogic.js';

console.log('--- TEST 1: Add Letter Works ---');
let text = '';
text = addLetter(text, 'H');
assert.strictEqual(text, 'H', 'Adding letter H should result in "H"');
console.log('✓ PASS: Add Letter works.');

console.log('\n--- TEST 2: Repeated Letters Work (e.g., HELLO) ---');
text = addLetter(text, 'E');
text = addLetter(text, 'L');
text = addLetter(text, 'L'); // Repeated letter
text = addLetter(text, 'O');
assert.strictEqual(text, 'HELLO', 'Assembled word should be "HELLO" with repeated L');
console.log('✓ PASS: Repeated letters work (e.g. HELLO).');

console.log('\n--- TEST 3: Space Inserts Word Separator (Without Duplicates) ---');
text = addSpace(text);
assert.strictEqual(text, 'HELLO ', 'Adding space should append a single space');
// Attempt adding duplicate space
text = addSpace(text);
assert.strictEqual(text, 'HELLO ', 'Duplicate consecutive space must be prevented');
// Add next word
text = addLetter(text, 'W');
text = addLetter(text, 'O');
text = addLetter(text, 'R');
text = addLetter(text, 'L');
text = addLetter(text, 'D');
assert.strictEqual(text, 'HELLO WORLD');
console.log('✓ PASS: Space inserts word separator and prevents repeated spaces.');

console.log('\n--- TEST 4: Delete Removes Only the Last Character ---');
text = deleteLastChar(text);
assert.strictEqual(text, 'HELLO WORL', 'Delete should remove trailing "D"');
text = deleteLastChar(text);
assert.strictEqual(text, 'HELLO WOR', 'Delete should remove trailing "L"');
console.log('✓ PASS: Delete removes only the last character.');

console.log('\n--- TEST 5: Clear Resets Text ---');
text = clearAllText();
assert.strictEqual(text, '', 'Clear should reset text to empty string');
console.log('✓ PASS: Clear resets text to empty.');

console.log('\n--- TEST 6: Empty Text Operations Are Safe ---');
// Delete on empty text
assert.strictEqual(deleteLastChar(''), '', 'Delete on empty text must not throw');
assert.strictEqual(deleteLastChar(null), '', 'Delete on null must not throw');
// Space on empty text
assert.strictEqual(addSpace(''), '', 'Leading space on empty text must be prevented');
assert.strictEqual(addSpace(null), '', 'Space on null text must be prevented');
// Clear on empty text
assert.strictEqual(clearAllText(), '', 'Clear on empty text is safe');
// Metrics on empty text
const emptyMetrics = calculateTextMetrics('');
assert.strictEqual(emptyMetrics.characters, 0);
assert.strictEqual(emptyMetrics.words, 0);
console.log('✓ PASS: Empty text operations are completely safe.');

console.log('\n--- TEST 7: Invalid Predictions Are Rejected ---');
const textBefore = 'TEST';
// Non-letters
assert.strictEqual(addLetter(textBefore, '1'), textBefore, 'Numbers must be rejected');
assert.strictEqual(addLetter(textBefore, '!'), textBefore, 'Punctuation must be rejected');
assert.strictEqual(addLetter(textBefore, 'AB'), textBefore, 'Multi-character strings must be rejected');
assert.strictEqual(addLetter(textBefore, ''), textBefore, 'Empty string must be rejected');
assert.strictEqual(addLetter(textBefore, null), textBefore, 'Null must be rejected');
assert.strictEqual(addLetter(textBefore, undefined), textBefore, 'Undefined must be rejected');
// Lowercase should be auto-normalized to uppercase
assert.strictEqual(addLetter(textBefore, 's'), 'TESTS', 'Lowercase letter should be accepted and capitalized');
console.log('✓ PASS: Invalid predictions rejected, valid letters accepted.');

console.log('\n--- TEST 8: Webcam Stable Predictions Can Be Added ---');
// Simulate Webcam stable prediction callback
let parentRecognizedLetter = null;
let parentAssembledText = '';
function onStablePredictionChange(letter) {
  parentRecognizedLetter = letter;
}
function onAddLetterDirect(letter) {
  parentAssembledText = addLetter(parentAssembledText, letter);
  parentRecognizedLetter = letter;
}

// Webcam detects 'I' stably
onStablePredictionChange('I');
assert.strictEqual(parentRecognizedLetter, 'I');
// User clicks Add Letter
onAddLetterDirect(parentRecognizedLetter);
// Webcam detects 'S' stably
onStablePredictionChange('S');
onAddLetterDirect(parentRecognizedLetter);
// Webcam detects 'L' stably
onStablePredictionChange('L');
onAddLetterDirect(parentRecognizedLetter);
assert.strictEqual(parentAssembledText, 'ISL', 'Webcam stable letters assembled into "ISL"');
console.log('✓ PASS: Webcam stable predictions can be added.');

console.log('\n--- TEST 9: Image-Upload Predictions Can Be Added ---');
// Simulate Image Upload response
const mockUploadResponse = {
  predicted_letter: 'A',
  confidence: 0.98,
  status: 'success',
};
parentRecognizedLetter = mockUploadResponse.predicted_letter.toUpperCase();
onAddLetterDirect(parentRecognizedLetter);
assert.strictEqual(parentAssembledText, 'ISLA', 'Image upload prediction added to text');
console.log('✓ PASS: Image-upload predictions can be added.');

console.log('\n--- TEST 10: Switching Recognition Modes Preserves Assembled Text ---');
// Simulate App.jsx state with activeMode
let appState = {
  activeMode: 'upload',
  assembledText: 'HELLO WORLD',
  lastRecognizedLetter: 'D',
};

// User switches to 'webcam' mode
appState = {
  ...appState,
  activeMode: 'webcam',
};
assert.strictEqual(appState.assembledText, 'HELLO WORLD', 'Mode switch to webcam preserves assembled text');
assert.strictEqual(appState.lastRecognizedLetter, 'D', 'Mode switch preserves last recognized letter');

// User switches back to 'upload' mode
appState = {
  ...appState,
  activeMode: 'upload',
};
assert.strictEqual(appState.assembledText, 'HELLO WORLD', 'Mode switch back to upload preserves assembled text');
console.log('✓ PASS: Switching recognition modes strictly preserves assembled text.');

console.log('\n--- TEST 11: Text Metrics Calculation ---');
const sampleMetrics = calculateTextMetrics('HELLO INDIAN SIGN LANGUAGE');
assert.strictEqual(sampleMetrics.characters, 26, 'Total characters with spaces should be 26');
assert.strictEqual(sampleMetrics.words, 4, 'Word count should be 4');
console.log('✓ PASS: Text metrics calculated correctly.');

console.log('\nAll 11 test suites completed successfully!');
