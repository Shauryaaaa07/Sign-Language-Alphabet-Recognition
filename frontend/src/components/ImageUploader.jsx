import React, { useState, useRef } from 'react';
import { UploadCloud, Image as ImageIcon, Trash2, Play, AlertCircle, CheckCircle2 } from 'lucide-react';

const MAX_FILE_SIZE = 10 * 1024 * 1024; // 10 MB limit
const ALLOWED_TYPES = ['image/jpeg', 'image/png', 'image/webp', 'image/bmp'];

/**
 * ImageUploader Component
 * Modern Indigo AI drag-and-drop file upload with preview and validation.
 */
export default function ImageUploader({
  selectedFile,
  previewUrl,
  onFileSelect,
  onClearFile,
  onPredict,
  isPredicting,
  backendConnected,
}) {
  const [isDragOver, setIsDragOver] = useState(false);
  const [validationError, setValidationError] = useState(null);
  const fileInputRef = useRef(null);

  const validateAndSelect = (file) => {
    setValidationError(null);

    if (!file) return;

    if (!ALLOWED_TYPES.includes(file.type) && !file.name.match(/\.(jpg|jpeg|png|webp|bmp)$/i)) {
      setValidationError('Please upload a valid image file (JPEG, PNG, or WebP).');
      return;
    }

    if (file.size === 0) {
      setValidationError('The selected image file is empty (0 bytes).');
      return;
    }

    if (file.size > MAX_FILE_SIZE) {
      setValidationError(
        `File size (${(file.size / (1024 * 1024)).toFixed(1)} MB) exceeds the 10 MB limit.`
      );
      return;
    }

    onFileSelect(file);
  };

  const handleDragOver = (e) => {
    e.preventDefault();
    setIsDragOver(true);
  };

  const handleDragLeave = (e) => {
    e.preventDefault();
    setIsDragOver(false);
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setIsDragOver(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      validateAndSelect(e.dataTransfer.files[0]);
    }
  };

  const handleInputChange = (e) => {
    if (e.target.files && e.target.files[0]) {
      validateAndSelect(e.target.files[0]);
    }
  };

  const formatFileSize = (bytes) => {
    if (bytes < 1024) return `${bytes} B`;
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
    return `${(bytes / (1024 * 1024)).toFixed(2)} MB`;
  };

  return (
    <div className="card-linear p-6 flex flex-col justify-between shadow-lg">
      <div>
        <div className="flex items-center justify-between mb-4 pb-3 border-b border-slate-200/80 dark:border-white/[0.08]">
          <div className="flex items-center space-x-2">
            <UploadCloud className="w-4 h-4 text-indigo-600 dark:text-indigo-400" />
            <h2 className="text-base font-bold tracking-tight text-slate-900 dark:text-white">
              Upload Pose Image
            </h2>
          </div>
          {selectedFile && (
            <button
              type="button"
              onClick={() => {
                setValidationError(null);
                onClearFile();
                if (fileInputRef.current) fileInputRef.current.value = '';
              }}
              disabled={isPredicting}
              className="inline-flex items-center space-x-1 text-xs font-mono text-rose-500 hover:text-rose-600 dark:hover:text-rose-400 hover:underline disabled:opacity-50 transition-colors"
            >
              <Trash2 className="w-3.5 h-3.5" />
              <span>Clear</span>
            </button>
          )}
        </div>

        {/* Upload Drop Zone / Preview Container */}
        {!previewUrl ? (
          <div
            onDragOver={handleDragOver}
            onDragLeave={handleDragLeave}
            onDrop={handleDrop}
            onClick={() => fileInputRef.current?.click()}
            className={`border-2 border-dashed rounded-xl p-8 text-center cursor-pointer transition-all flex flex-col items-center justify-center min-h-[260px] ${
              isDragOver
                ? 'border-indigo-500 bg-indigo-500/10 dark:bg-indigo-500/15'
                : 'border-slate-300 dark:border-white/[0.1] hover:border-indigo-400/60 dark:hover:border-indigo-500/40 bg-slate-50/60 dark:bg-white/[0.02]'
            }`}
          >
            <input
              ref={fileInputRef}
              type="file"
              accept=".jpg,.jpeg,.png,.webp,.bmp"
              onChange={handleInputChange}
              className="hidden"
            />
            <div className="w-12 h-12 rounded-xl bg-indigo-50 dark:bg-indigo-950/60 text-indigo-600 dark:text-indigo-400 flex items-center justify-center mb-3 border border-indigo-200/60 dark:border-indigo-800/60 shadow-xs">
              <UploadCloud className="w-6 h-6" />
            </div>
            <p className="text-sm font-bold text-slate-800 dark:text-slate-200">
              Select or drop hand gesture image
            </p>
            <p className="text-xs text-slate-500 dark:text-slate-400 mt-1">
              Supports JPEG, PNG, or WebP up to 10 MB
            </p>
          </div>
        ) : (
          <div className="space-y-4">
            <div className="relative rounded-xl overflow-hidden bg-slate-950 border border-slate-800 aspect-square max-h-[280px] mx-auto flex items-center justify-center">
              <img
                src={previewUrl}
                alt="Selected hand sign preview"
                className="max-h-full max-w-full object-contain"
              />
              <div className="absolute top-2.5 right-2.5 bg-slate-950/80 backdrop-blur-md text-white text-[10px] font-mono px-2 py-0.5 rounded-md border border-white/10 flex items-center space-x-1 shadow-sm">
                <ImageIcon className="w-3 h-3 text-indigo-400" />
                <span>{formatFileSize(selectedFile?.size || 0)}</span>
              </div>
            </div>

            <div className="flex items-center justify-between text-xs text-slate-600 dark:text-slate-400 bg-slate-100/70 dark:bg-white/[0.03] px-3 py-2 rounded-xl border border-slate-200/80 dark:border-white/[0.08]">
              <span className="font-mono truncate max-w-[200px]">{selectedFile?.name}</span>
              <span className="flex items-center space-x-1 text-emerald-600 dark:text-emerald-400 font-mono font-semibold">
                <CheckCircle2 className="w-3.5 h-3.5" />
                <span>Ready</span>
              </span>
            </div>
          </div>
        )}

        {/* Validation Error */}
        {validationError && (
          <div className="mt-4 p-3 rounded-xl bg-rose-500/10 border border-rose-500/20 text-xs text-rose-600 dark:text-rose-400 flex items-start space-x-2">
            <AlertCircle className="w-4 h-4 shrink-0 mt-0.5 text-rose-500" />
            <span>{validationError}</span>
          </div>
        )}
      </div>

      {/* Action CTA Button */}
      <div className="mt-6 pt-4 border-t border-slate-200/80 dark:border-white/[0.08]">
        <button
          type="button"
          onClick={onPredict}
          disabled={!selectedFile || isPredicting || !backendConnected}
          className="btn-indigo w-full justify-center disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {isPredicting ? (
            <>
              <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
              <span>Inference in progress...</span>
            </>
          ) : (
            <>
              <Play className="w-3.5 h-3.5 fill-white" />
              <span>Recognize Gesture</span>
            </>
          )}
        </button>
      </div>
    </div>
  );
}