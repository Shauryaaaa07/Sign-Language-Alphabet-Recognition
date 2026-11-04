import React, { useState } from 'react';
import { Camera, UploadCloud, Info, AlertCircle } from 'lucide-react';
import PageHeader from '../components/PageHeader';
import ImageUploader from '../components/ImageUploader';
import PredictionResult from '../components/PredictionResult';
import WebcamRecognition from '../components/WebcamRecognition';
import TextBuilder from '../components/TextBuilder';
import { predictSignGesture } from '../services/api';
import { addLetter } from '../utils/textBuilderLogic';

/**
 * Studio Component
 * Dedicated recognition workspace for SignAI in Modern Indigo AI style.
 * Houses live webcam video streams, image uploads, telemetry, and full-width sentence builder.
 */
export default function Studio({
  backendStatus,
  assembledText,
  setAssembledText,
  lastRecognizedLetter,
  setLastRecognizedLetter,
}) {
  const [activeMode, setActiveMode] = useState('webcam');

  // Upload and inference state
  const [selectedFile, setSelectedFile] = useState(null);
  const [previewUrl, setPreviewUrl] = useState(null);
  const [isPredicting, setIsPredicting] = useState(false);
  const [prediction, setPrediction] = useState(null);
  const [error, setError] = useState(null);

  const handleFileSelect = (file) => {
    if (previewUrl) {
      URL.revokeObjectURL(previewUrl);
    }
    setSelectedFile(file);
    setPreviewUrl(URL.createObjectURL(file));
    setPrediction(null);
    setError(null);
  };

  const handleClearFile = () => {
    if (previewUrl) {
      URL.revokeObjectURL(previewUrl);
    }
    setSelectedFile(null);
    setPreviewUrl(null);
    setPrediction(null);
    setError(null);
  };

  const handlePredict = async () => {
    if (!selectedFile || isPredicting) return;

    setIsPredicting(true);
    setError(null);

    try {
      const response = await predictSignGesture(selectedFile);
      setPrediction(response);
      const letter = response?.predicted_letter || response?.predicted_class;
      if (letter) {
        setLastRecognizedLetter(letter.toUpperCase());
      }
    } catch (err) {
      setError(err.message || 'Failed to classify hand gesture.');
      setPrediction(null);
    } finally {
      setIsPredicting(false);
    }
  };

  const handleAddLetterDirect = (letter) => {
    if (!letter) return;
    setAssembledText((prev) => addLetter(prev, letter));
    setLastRecognizedLetter(letter.toUpperCase());
  };

  return (
    <div className="space-y-6 py-4">
      <PageHeader
        badge="CNN V4 Active Core"
        title="Recognition Studio"
        subtitle="Capture live Indian Sign Language alphabet hand poses, verify confidence scores, assemble text, and vocalize speech."
      />

      {/* Backend Status Warning when offline */}
      {backendStatus !== 'connected' && (
        <div className="p-3.5 rounded-xl bg-amber-500/10 border border-amber-500/20 text-xs sm:text-sm text-amber-700 dark:text-amber-300 flex items-start space-x-3">
          <AlertCircle className="w-5 h-5 shrink-0 text-amber-500 mt-0.5" />
          <div className="space-y-1">
            <p className="font-bold">FastAPI Backend Status: {backendStatus}</p>
            <p className="text-xs leading-relaxed font-mono">
              Backend not responding on port 8000. Verify that <code>python -m uvicorn backend.main:app --port 8000</code> is running.
            </p>
          </div>
        </div>
      )}

      {/* Mode Selector Segmented Tabs */}
      <div className="flex justify-center">
        <div className="p-1 rounded-full bg-slate-100 dark:bg-[#161926] border border-slate-200/80 dark:border-white/[0.08] inline-flex space-x-1 shadow-sm">
          <button
            type="button"
            onClick={() => setActiveMode('webcam')}
            className={`flex items-center space-x-2 px-5 py-2 rounded-full text-xs sm:text-sm font-semibold transition-all ${
              activeMode === 'webcam'
                ? 'bg-gradient-to-r from-indigo-600 to-violet-600 text-white shadow-md shadow-indigo-500/25'
                : 'text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white'
            }`}
          >
            <Camera className="w-4 h-4" />
            <span>Live Webcam Stream</span>
          </button>

          <button
            type="button"
            onClick={() => setActiveMode('upload')}
            className={`flex items-center space-x-2 px-5 py-2 rounded-full text-xs sm:text-sm font-semibold transition-all ${
              activeMode === 'upload'
                ? 'bg-gradient-to-r from-indigo-600 to-violet-600 text-white shadow-md shadow-indigo-500/25'
                : 'text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white'
            }`}
          >
            <UploadCloud className="w-4 h-4" />
            <span>Image File Upload</span>
          </button>
        </div>
      </div>

      {/* Input Workspace & Prediction Results */}
      {activeMode === 'upload' ? (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-5 items-stretch">
          <ImageUploader
            selectedFile={selectedFile}
            previewUrl={previewUrl}
            onFileSelect={handleFileSelect}
            onClearFile={handleClearFile}
            onPredict={handlePredict}
            isPredicting={isPredicting}
            backendConnected={backendStatus === 'connected'}
          />

          <PredictionResult
            prediction={prediction}
            isPredicting={isPredicting}
            error={error}
            onAddLetterDirect={handleAddLetterDirect}
          />
        </div>
      ) : (
        <WebcamRecognition
          backendConnected={backendStatus === 'connected'}
          onStablePredictionChange={(letter) => setLastRecognizedLetter(letter.toUpperCase())}
          onAddLetterDirect={handleAddLetterDirect}
        />
      )}

      {/* Recognized Letter Text Builder Section (Full Width) */}
      <div>
        <TextBuilder
          text={assembledText}
          onTextChange={setAssembledText}
          activeLetter={lastRecognizedLetter}
        />
      </div>

      {/* Supported Alphabet Quick-Picker Bar & Instructions */}
      <div className="card-linear p-4 sm:p-5 space-y-3 shadow-md">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 pb-3 border-b border-slate-200/80 dark:border-white/[0.08]">
          <h3 className="text-xs uppercase font-bold text-slate-800 dark:text-slate-200 flex items-center space-x-1.5 tracking-wider">
            <Info className="w-3.5 h-3.5 text-indigo-500" />
            <span>Alphabet Quick-Select (26 Classes: A–Z)</span>
          </h3>
          <span className="text-[11px] text-slate-500 dark:text-slate-400 font-mono">
            Click any letter to test sentence assembly
          </span>
        </div>

        <div className="flex flex-wrap gap-1.5">
          {'ABCDEFGHIJKLMNOPQRSTUVWXYZ'.split('').map((char) => (
            <button
              key={char}
              type="button"
              onClick={() => setLastRecognizedLetter(char)}
              title={`Select '${char}' as active character`}
              className={`w-8 h-8 rounded-lg border text-xs font-mono font-bold flex items-center justify-center transition-all ${
                lastRecognizedLetter === char
                  ? 'bg-gradient-to-r from-indigo-600 to-violet-600 text-white border-transparent shadow-md shadow-indigo-500/25 scale-105'
                  : 'bg-slate-50 dark:bg-white/[0.03] border-slate-200 dark:border-white/[0.08] text-slate-700 dark:text-slate-300 hover:border-indigo-400 hover:text-indigo-600 dark:hover:text-indigo-400'
              }`}
            >
              {char}
            </button>
          ))}
        </div>

        <p className="text-[11px] text-slate-500 dark:text-slate-400 leading-relaxed pt-1">
          Dynamic signs notice: In natural ISL, letters <strong>J</strong> and <strong>Z</strong> require motion strokes.
          This 2D CNN model classifies static keyframe poses captured from standard frontal postures.
        </p>
      </div>
    </div>
  );
}