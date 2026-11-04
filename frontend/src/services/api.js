/**
 * ISL Backend API Service
 * =======================
 * Manages HTTP communication with the FastAPI backend service.
 */

// Configurable base URL; defaults to local development backend
export const API_BASE_URL =
  import.meta.env.VITE_API_URL || 'http://localhost:8000';

/**
 * Checks the runtime health and model loading status of the backend.
 * @returns {Promise<{ ok: boolean, data?: object, error?: string }>}
 */
export async function checkBackendHealth() {
  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), 4000);

  try {
    const response = await fetch(`${API_BASE_URL}/health`, {
      method: 'GET',
      signal: controller.signal,
    });
    clearTimeout(timeoutId);

    if (!response.ok) {
      return {
        ok: false,
        error: `Backend returned HTTP status ${response.status}`,
      };
    }

    const data = await response.json();
    return { ok: true, data };
  } catch (err) {
    clearTimeout(timeoutId);
    const message =
      err.name === 'AbortError'
        ? 'Connection timed out'
        : 'Cannot reach backend server. Ensure FastAPI is running on port 8000.';
    return { ok: false, error: message };
  }
}

/**
 * Sends an uploaded hand gesture image or webcam frame blob to the backend /predict endpoint.
 * @param {File|Blob} imageFile - The image File or Blob object to classify.
 * @returns {Promise<object>} - Parsed JSON PredictionResponse.
 */
export async function predictSignGesture(imageFile) {
  if (!imageFile) {
    throw new Error('Please select an image file first.');
  }

  // Construct multipart/form-data payload with exact field name 'file'
  const formData = new FormData();
  if (imageFile instanceof Blob && !imageFile.name) {
    formData.append('file', imageFile, 'webcam_frame.jpg');
  } else {
    formData.append('file', imageFile);
  }

  try {
    // Note: Do NOT set Content-Type header manually so the browser sets multipart boundary
    const response = await fetch(`${API_BASE_URL}/predict`, {
      method: 'POST',
      body: formData,
    });

    const data = await response.json().catch(() => null);

    if (!response.ok) {
      const errorDetail =
        data && data.detail
          ? data.detail
          : `Prediction failed with HTTP status ${response.status}`;
      throw new Error(errorDetail);
    }

    return data;
  } catch (err) {
    if (err.message.includes('Failed to fetch') || err.message.includes('NetworkError')) {
      throw new Error(
        'Network error: Failed to communicate with FastAPI backend. Ensure the server is online at ' +
          API_BASE_URL
      );
    }
    throw err;
  }
}
