import React, { useState, useRef, useCallback } from 'react';
import { Camera, CameraOff, Plus, AlertCircle, CheckCircle2, Layers, RefreshCw } from 'lucide-react';
import { predictSignGesture } from '../services/api';

/**
 * WebcamRecognition Component
 * Modern Indigo AI layout for real-time webcam video stream capture, concurrency locking,
 * consecutive confidence stability (3 frames >= 75%), and dual raw/stabilized output.
 */
export default function WebcamRecognition({
  backendConnected,
  onStablePredictionChange,
  onAddLetterDirect,
}) {
  // Camera & Stream State
  const [isCameraActive, setIsCameraActive] = useState(false);
  const [isStartingCamera, setIsStartingCamera] = useState(false);
  const [cameraError, setCameraError] = useState(null);
  const [isProcessing, setIsProcessing] = useState(false);

  // Recognition Results State
  const [rawPrediction, setRawPrediction] = useState(null);
  const [stablePrediction, setStablePrediction] = useState(null);
  const [candidateLetter, setCandidateLetter] = useState(null);
  const [consecutiveCount, setConsecutiveCount] = useState(0);

  // Element & Stream References
  const videoRef = useRef(null);
  const canvasRef = useRef(null);
  const streamRef = useRef(null);
  const intervalRef = useRef(null);

  // Concurrency & Stability References
  const isProcessingRef = useRef(false);
  const isCameraActiveRef = useRef(false);
  const candidateLetterRef = useRef(null);
  const consecutiveCountRef = useRef(0);

  const MIN_CONFIDENCE_THRESHOLD = 0.75;
  const REQUIRED_CONSECUTIVE_FRAMES = 3;

  const handlePrediction = useCallback((pred) => {
    setRawPrediction(pred);

    const letter = (pred.predicted_letter || pred.predicted_class || '').toUpperCase();
    const conf = pred.confidence;

    if (conf >= MIN_CONFIDENCE_THRESHOLD) {
      if (letter === candidateLetterRef.current) {
        consecutiveCountRef.current += 1;
      } else {
        candidateLetterRef.current = letter;
        consecutiveCountRef.current = 1;
      }

      if (consecutiveCountRef.current >= REQUIRED_CONSECUTIVE_FRAMES) {
        setStablePrediction(letter);
        if (onStablePredictionChange) {
          onStablePredictionChange(letter);
        }
      }
    } else {
      candidateLetterRef.current = null;
      consecutiveCountRef.current = 0;
    }

    setCandidateLetter(candidateLetterRef.current);
    setConsecutiveCount(consecutiveCountRef.current);
  }, [onStablePredictionChange]);

  const handlePredictionError = useCallback(() => {
    candidateLetterRef.current = null;
    consecutiveCountRef.current = 0;
    setCandidateLetter(null);
    setConsecutiveCount(0);
  }, []);

  const stopCamera = useCallback(() => {
    if (intervalRef.current) {
      clearInterval(intervalRef.current);
      intervalRef.current = null;
    }

    if (streamRef.current) {
      streamRef.current.getTracks().forEach((track) => {
        try {
          track.stop();
        } catch {
          // Track stop fallback
        }
      });
      streamRef.current = null;
    }

    if (videoRef.current) {
      videoRef.current.srcObject = null;
    }

    isCameraActiveRef.current = false;
    isProcessingRef.current = false;
    setIsCameraActive(false);
    setIsProcessing(false);
    setIsStartingCamera(false);
    setCameraError(null);

    candidateLetterRef.current = null;
    consecutiveCountRef.current = 0;
    setCandidateLetter(null);
    setConsecutiveCount(0);
    setRawPrediction(null);
    setStablePrediction(null);
  }, []);

  const captureFrame = useCallback(async () => {
    if (!isCameraActiveRef.current || isProcessingRef.current) {
      return;
    }

    const video = videoRef.current;
    const canvas = canvasRef.current;
    if (!video || !canvas || video.readyState < 2) {
      return;
    }

    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    canvas.width = video.videoWidth || 640;
    canvas.height = video.videoHeight || 480;
    ctx.drawImage(video, 0, 0, canvas.width, canvas.height);

    const base64Data = canvas.toDataURL('image/jpeg', 0.85);

    isProcessingRef.current = true;
    setIsProcessing(true);

    try {
      const result = await predictSignGesture(base64Data);
      if (isCameraActiveRef.current) {
        handlePrediction(result);
      }
    } catch {
      if (isCameraActiveRef.current) {
        handlePredictionError();
      }
    } finally {
      isProcessingRef.current = false;
      setIsProcessing(false);
    }
  }, [handlePrediction, handlePredictionError]);

  const startCamera = async () => {
    setCameraError(null);
    setIsStartingCamera(true);

    try {
      if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
        throw new Error('Webcam media devices API is not supported in this browser environment.');
      }

      const stream = await navigator.mediaDevices.getUserMedia({
        video: {
          width: { ideal: 640 },
          height: { ideal: 480 },
          facingMode: 'user',
        },
        audio: false,
      });

      streamRef.current = stream;
      if (videoRef.current) {
        videoRef.current.srcObject = stream;
        await videoRef.current.play();
      }

      isCameraActiveRef.current = true;
      setIsCameraActive(true);
      setIsStartingCamera(false);

      intervalRef.current = setInterval(() => {
        captureFrame();
      }, 500);
    } catch (err) {
      setIsStartingCamera(false);
      isCameraActiveRef.current = false;
      setIsCameraActive(false);

      let msg = 'Failed to access webcam. Please check browser camera permissions.';
      if (err.name === 'NotAllowedError' || err.name === 'PermissionDeniedError') {
        msg = 'Camera permission denied. Please allow camera access in your browser settings.';
      } else if (err.name === 'NotFoundError' || err.name === 'DevicesNotFoundError') {
        msg = 'No video input devices detected on your system.';
      } else if (err.message) {
        msg = err.message;
      }
      setCameraError(msg);
    }
  };

  return (
    <div className="space-y-6">
      {/* Offscreen Canvas for Frame Capture */}
      <canvas ref={canvasRef} className="hidden" aria-hidden="true" />

      {/* Main Studio Viewport Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-start">
        {/* Left Column: Camera Viewport (7 cols) */}
        <div className="lg:col-span-7 card-linear p-5 shadow-lg">
          <div className="flex items-center justify-between pb-3 mb-3 border-b border-slate-200/80 dark:border-white/[0.08]">
            <div className="flex items-center space-x-2">
              <span className={`w-2.5 h-2.5 rounded-full ${isCameraActive ? 'bg-emerald-500 shadow-sm shadow-emerald-500/50 animate-pulse' : 'bg-slate-400'}`} />
              <span className="text-xs uppercase font-bold text-slate-800 dark:text-slate-200 tracking-wider">
                Webcam Feed
              </span>
            </div>
            <span className="text-xs text-slate-500 dark:text-slate-400 font-mono">
              {isCameraActive ? '500ms Continuous Stream' : 'Standby'}
            </span>
          </div>

          {/* Camera Viewport */}
          <div className="relative aspect-video w-full rounded-xl bg-slate-950 flex items-center justify-center overflow-hidden border border-slate-800 shadow-inner">
            <video
              ref={videoRef}
              autoPlay
              playsInline
              muted
              className={`w-full h-full object-cover transform -scale-x-100 ${
                isCameraActive ? 'block' : 'hidden'
              }`}
            />

            {!isCameraActive && !cameraError && (
              <div className="text-center p-6 text-slate-400">
                <div className="w-14 h-14 rounded-2xl bg-white/[0.04] border border-white/10 flex items-center justify-center mx-auto mb-3 text-slate-400">
                  <Camera className="w-7 h-7" />
                </div>
                <p className="text-sm font-semibold text-slate-200">Webcam Inactive</p>
                <p className="text-xs text-slate-400 mt-1">
                  Click 'Start Camera' to initiate real-time fingerspelling recognition.
                </p>
              </div>
            )}

            {cameraError && (
              <div className="text-center p-6 text-rose-400 max-w-sm">
                <AlertCircle className="w-10 h-10 mx-auto mb-2 text-rose-500" />
                <p className="text-sm font-semibold">Camera Access Error</p>
                <p className="text-xs text-slate-400 mt-1 leading-relaxed">{cameraError}</p>
              </div>
            )}

            {/* Target Crosshairs Box */}
            {isCameraActive && (
              <div className="absolute inset-0 pointer-events-none flex items-center justify-center">
                <div className="w-48 h-48 sm:w-56 sm:h-56 border border-indigo-400/40 rounded-xl relative flex flex-col justify-between p-2">
                  <span className="text-[10px] uppercase font-bold tracking-wider text-indigo-300 bg-slate-950/80 backdrop-blur-md px-2 py-0.5 rounded self-start border border-indigo-500/20">
                    Hand Target
                  </span>
                  <div className="absolute top-0 left-0 w-3 h-3 border-t-2 border-l-2 border-indigo-400 rounded-tl" />
                  <div className="absolute top-0 right-0 w-3 h-3 border-t-2 border-r-2 border-indigo-400 rounded-tr" />
                  <div className="absolute bottom-0 left-0 w-3 h-3 border-b-2 border-l-2 border-indigo-400 rounded-bl" />
                  <div className="absolute bottom-0 right-0 w-3 h-3 border-b-2 border-r-2 border-indigo-400 rounded-br" />
                </div>
              </div>
            )}

            {/* Processing Indicator */}
            {isCameraActive && isProcessing && (
              <div className="absolute top-3 right-3 bg-slate-950/80 backdrop-blur-md text-white px-2.5 py-1 rounded-lg text-[10px] font-mono flex items-center space-x-1.5 border border-white/10 shadow-sm">
                <div className="w-2.5 h-2.5 border-2 border-white/30 border-t-indigo-400 rounded-full animate-spin" />
                <span>Inferring</span>
              </div>
            )}
          </div>

          {/* Controls Bar */}
          <div className="mt-4 pt-4 border-t border-slate-200/80 dark:border-white/[0.08] flex items-center justify-between">
            <span className="text-xs text-slate-500 dark:text-slate-400 font-mono">
              Input: 128×128 RGB Bilinear
            </span>

            <div>
              {isCameraActive ? (
                <button
                  type="button"
                  onClick={stopCamera}
                  className="inline-flex items-center space-x-1.5 px-4 py-2 rounded-xl text-xs sm:text-sm font-semibold bg-rose-600 hover:bg-rose-700 text-white transition-colors shadow-sm"
                >
                  <CameraOff className="w-4 h-4" />
                  <span>Stop Camera</span>
                </button>
              ) : (
                <button
                  type="button"
                  onClick={startCamera}
                  disabled={isStartingCamera || !backendConnected}
                  className="btn-indigo"
                >
                  {isStartingCamera ? (
                    <>
                      <RefreshCw className="w-4 h-4 animate-spin" />
                      <span>Starting...</span>
                    </>
                  ) : (
                    <>
                      <Camera className="w-4 h-4" />
                      <span>Start Camera</span>
                    </>
                  )}
                </button>
              )}
            </div>
          </div>
        </div>

        {/* Right Column: Telemetry & Results (5 cols) */}
        <div className="lg:col-span-5 flex flex-col space-y-4">
          {/* Card 1: Stabilized Output */}
          <div className="card-linear p-5 shadow-lg">
            <div className="flex items-center justify-between mb-3 pb-2 border-b border-slate-200/80 dark:border-white/[0.08]">
              <span className="text-xs uppercase font-bold text-slate-800 dark:text-slate-200 tracking-wider">
                Stabilized Output
              </span>
              <span className="text-[10px] uppercase font-bold tracking-wider text-indigo-700 dark:text-indigo-300 bg-indigo-50 dark:bg-indigo-950/60 px-2 py-0.5 rounded-full border border-indigo-200 dark:border-indigo-800/60">
                3 Consecutive &ge; 75%
              </span>
            </div>

            <div className="flex items-center space-x-4 py-2">
              <div
                className={`w-20 h-20 rounded-2xl flex items-center justify-center font-bold text-4xl font-mono border transition-all ${
                  stablePrediction
                    ? 'bg-gradient-to-br from-emerald-500 to-teal-600 text-white border-emerald-400 shadow-lg shadow-emerald-500/25'
                    : 'bg-slate-100 dark:bg-white/[0.04] text-slate-400 border-slate-200 dark:border-white/[0.08]'
                }`}
              >
                {stablePrediction || '—'}
              </div>

              <div className="flex-1 space-y-2">
                <div>
                  <h4 className="text-sm font-bold text-slate-900 dark:text-white">
                    {stablePrediction ? `Verified: '${stablePrediction}'` : 'Awaiting Steady Pose'}
                  </h4>
                  <p className="text-xs text-slate-500 dark:text-slate-400">
                    {stablePrediction ? 'Held consistently across 3+ frames.' : 'Hold hand steady inside frame.'}
                  </p>
                </div>

                {/* Progress Bar */}
                <div className="space-y-1">
                  <div className="flex items-center justify-between font-mono text-[11px] text-slate-500 dark:text-slate-400">
                    <span>Target: {candidateLetter || 'None'}</span>
                    <span>{consecutiveCount} / {REQUIRED_CONSECUTIVE_FRAMES}</span>
                  </div>
                  <div className="w-full bg-slate-100 dark:bg-white/[0.08] h-1.5 rounded-full overflow-hidden">
                    <div
                      className={`h-full transition-all duration-300 ${
                        consecutiveCount >= 3 ? 'bg-gradient-to-r from-emerald-500 to-teal-400' : 'bg-gradient-to-r from-indigo-600 to-violet-500'
                      }`}
                      style={{
                        width: `${Math.min(100, (consecutiveCount / REQUIRED_CONSECUTIVE_FRAMES) * 100)}%`,
                      }}
                    />
                  </div>
                </div>

                {stablePrediction && onAddLetterDirect && (
                  <button
                    type="button"
                    onClick={() => onAddLetterDirect(stablePrediction)}
                    className="mt-2 inline-flex items-center space-x-1 px-3 py-1.5 rounded-lg text-xs font-semibold bg-emerald-600 hover:bg-emerald-700 text-white transition-all shadow-sm shadow-emerald-600/20"
                  >
                    <Plus className="w-3.5 h-3.5" />
                    <span>Append '{stablePrediction}'</span>
                  </button>
                )}
              </div>
            </div>
          </div>

          {/* Card 2: Current Raw Frame */}
          <div className="card-linear p-5 flex-1 shadow-lg">
            <div className="flex items-center justify-between mb-3 pb-2 border-b border-slate-200/80 dark:border-white/[0.08]">
              <span className="text-xs uppercase font-bold text-slate-800 dark:text-slate-200 tracking-wider">
                Raw Frame Classification
              </span>
              {rawPrediction && (
                <span className="text-[10px] font-mono font-semibold px-2 py-0.5 rounded-full border border-indigo-200 dark:border-indigo-800/60 bg-indigo-50 dark:bg-indigo-950/60 text-indigo-700 dark:text-indigo-300">
                  {(rawPrediction.confidence * 100).toFixed(1)}% Conf
                </span>
              )}
            </div>

            {rawPrediction ? (
              <div className="space-y-4">
                <div className="flex items-center space-x-3">
                  <span className="text-3xl font-bold font-mono text-slate-900 dark:text-white">
                    {(rawPrediction.predicted_letter || rawPrediction.predicted_class || '').toUpperCase()}
                  </span>
                  <div className="flex-1">
                    <div className="flex items-center justify-between text-xs font-mono text-slate-500 dark:text-slate-400 mb-1">
                      <span>Softmax</span>
                      <span>{(rawPrediction.confidence * 100).toFixed(1)}%</span>
                    </div>
                    <div className="w-full bg-slate-100 dark:bg-white/[0.08] h-1.5 rounded-full overflow-hidden">
                      <div
                        className="h-full bg-gradient-to-r from-indigo-600 to-violet-500"
                        style={{ width: `${(rawPrediction.confidence * 100).toFixed(1)}%` }}
                      />
                    </div>
                  </div>
                </div>

                {/* Top 3 Alternative Candidates */}
                {rawPrediction.top_predictions && rawPrediction.top_predictions.length > 0 && (
                  <div>
                    <h5 className="text-[10px] uppercase tracking-wider text-slate-500 dark:text-slate-400 mb-2 flex items-center space-x-1 font-semibold">
                      <Layers className="w-3 h-3 text-indigo-500" />
                      <span>Top 3 Distribution</span>
                    </h5>
                    <div className="space-y-1.5">
                      {rawPrediction.top_predictions.slice(0, 3).map((item, idx) => {
                        const candLetter = (item.letter || item.class || '').toUpperCase();
                        return (
                          <div key={candLetter || idx} className="flex items-center space-x-2 text-xs font-mono">
                            <span className="w-5 font-bold text-slate-700 dark:text-slate-300">
                              {candLetter}
                            </span>
                            <div className="flex-1 bg-slate-100 dark:bg-white/[0.08] h-1.5 rounded-full overflow-hidden">
                              <div
                                className={`h-full ${idx === 0 ? 'bg-gradient-to-r from-indigo-600 to-violet-500' : 'bg-slate-400 dark:bg-slate-600'}`}
                                style={{ width: `${(item.confidence * 100).toFixed(1)}%` }}
                              />
                            </div>
                            <span className="text-slate-500 dark:text-slate-400 text-[11px] w-12 text-right">
                              {(item.confidence * 100).toFixed(1)}%
                            </span>
                          </div>
                        );
                      })}
                    </div>
                  </div>
                )}
              </div>
            ) : (
              <div className="h-28 flex items-center justify-center text-center text-slate-400 dark:text-slate-500 text-xs">
                Stream standby. Start camera to inspect live frames.
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Engineering Architecture Notice */}
      <div className="card-linear p-4 text-xs text-slate-600 dark:text-slate-400 flex items-start space-x-3 shadow-sm">
        <CheckCircle2 className="w-4 h-4 text-indigo-600 dark:text-indigo-400 shrink-0 mt-0.5" />
        <div className="space-y-0.5">
          <p className="font-bold text-slate-900 dark:text-white">
            CNN V4 Evaluation Pipeline: 86.34% Test Accuracy | 308,218 Parameters
          </p>
          <p className="leading-relaxed">
            Monocular 2D hand poses are sampled at 500ms intervals. To eliminate jitter between transitions,
            classification outputs are stabilized using a 3-frame sliding consensus window with &ge; 75% confidence thresholding.
          </p>
        </div>
      </div>
    </div>
  );
}