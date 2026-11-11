/**
 * TextBuilder Logic Utilities
 * ===========================
 * Pure helper functions for text assembly, validation, space handling,
 * and text metric calculations for the ISL Recognized Letter Text Builder.
 */

/**
 * Validates and appends a single ISL alphabet letter (A–Z) to the existing text.
 * Rejects invalid, non-alphabetic, or multi-character inputs.
 *
 * @param {string} currentText - The existing assembled text.
 * @param {string} letter - The candidate letter to append.
 * @returns {string} - Updated assembled text.
 */
export function addLetter(currentText, letter) {
  const text = currentText || '';
  if (!letter || typeof letter !== 'string') return text;

  const normalized = letter.trim().toUpperCase();
  // Strictly enforce single alphabet character A–Z
  if (!/^[A-Z]$/.test(normalized)) {
    return text;
  }

  return text + normalized;
}

/**
 * Appends a single space separator.
 * Prevents leading spaces on empty text and repeated consecutive spaces.
 *
 * @param {string} currentText - The existing assembled text.
 * @returns {string} - Updated text with single trailing space, or unchanged.
 */
export function addSpace(currentText) {
  const text = currentText || '';
  if (text.length === 0) return text;
  if (text.endsWith(' ')) return text;
  return text + ' ';
}

/**
 * Removes the last character from the assembled text.
 * Safely handles empty string without throwing errors.
 *
 * @param {string} currentText - The existing assembled text.
 * @returns {string} - Updated text with the final character removed.
 */
export function deleteLastChar(currentText) {
  const text = currentText || '';
  if (text.length === 0) return '';
  return text.slice(0, -1);
}

/**
 * Resets the assembled text.
 *
 * @returns {string} - Empty string.
 */
export function clearAllText() {
  return '';
}

/**
 * Computes character count and word count from the assembled text.
 *
 * @param {string} text - The assembled text.
 * @returns {{ characters: number, words: number }}
 */
export function calculateTextMetrics(text) {
  const str = text || '';
  const characters = str.length;
  const words = str.trim().length > 0 ? str.trim().split(/\s+/).length : 0;
  return { characters, words };
}
