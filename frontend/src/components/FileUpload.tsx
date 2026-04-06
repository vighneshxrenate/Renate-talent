"use client";

import { useCallback, useRef, useState } from "react";

interface FileUploadProps {
  error?: string;
  onFileSelect: (files: FileList | null) => void;
}

export default function FileUpload({ error, onFileSelect }: FileUploadProps) {
  const [fileName, setFileName] = useState<string | null>(null);
  const [fileSize, setFileSize] = useState<string | null>(null);
  const [dragOver, setDragOver] = useState(false);
  const inputRef = useRef<HTMLInputElement>(null);

  const formatSize = (bytes: number) => {
    if (bytes < 1024) return `${bytes} B`;
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
    return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
  };

  const handleFiles = useCallback(
    (files: FileList | null) => {
      if (files && files.length > 0) {
        setFileName(files[0].name);
        setFileSize(formatSize(files[0].size));
      } else {
        setFileName(null);
        setFileSize(null);
      }
      onFileSelect(files);
    },
    [onFileSelect]
  );

  const clearFile = () => {
    setFileName(null);
    setFileSize(null);
    if (inputRef.current) inputRef.current.value = "";
    onFileSelect(null);
  };

  return (
    <div>
      <label className="block text-sm font-medium text-gray-700 mb-1">
        Resume <span className="text-red-500">*</span>
      </label>

      {fileName ? (
        <div className="flex items-center gap-3 p-4 border border-gray-200 rounded-lg bg-gray-50">
          <svg
            className="w-8 h-8 text-red-500 shrink-0"
            fill="currentColor"
            viewBox="0 0 20 20"
          >
            <path d="M4 4a2 2 0 012-2h4.586A2 2 0 0112 2.586L15.414 6A2 2 0 0116 7.414V16a2 2 0 01-2 2H6a2 2 0 01-2-2V4z" />
          </svg>
          <div className="flex-1 min-w-0">
            <p className="text-sm font-medium text-gray-900 truncate">
              {fileName}
            </p>
            <p className="text-xs text-gray-500">{fileSize}</p>
          </div>
          <button
            type="button"
            onClick={clearFile}
            className="text-gray-400 hover:text-gray-600 cursor-pointer"
          >
            <svg className="w-5 h-5" viewBox="0 0 20 20" fill="currentColor">
              <path d="M6.28 5.22a.75.75 0 00-1.06 1.06L8.94 10l-3.72 3.72a.75.75 0 101.06 1.06L10 11.06l3.72 3.72a.75.75 0 101.06-1.06L11.06 10l3.72-3.72a.75.75 0 00-1.06-1.06L10 8.94 6.28 5.22z" />
            </svg>
          </button>
        </div>
      ) : (
        <label
          htmlFor="resume-input"
          className={`flex flex-col items-center justify-center p-8 border-2 border-dashed rounded-lg cursor-pointer transition-colors ${
            dragOver
              ? "border-indigo-500 bg-indigo-50"
              : error
                ? "border-red-300 bg-red-50"
                : "border-gray-300 hover:border-gray-400 bg-white"
          }`}
          onDragOver={(e) => {
            e.preventDefault();
            setDragOver(true);
          }}
          onDragLeave={() => setDragOver(false)}
          onDrop={(e) => {
            e.preventDefault();
            setDragOver(false);
            if (e.dataTransfer.files.length > 0) {
              const dt = new DataTransfer();
              dt.items.add(e.dataTransfer.files[0]);
              if (inputRef.current) {
                inputRef.current.files = dt.files;
              }
              handleFiles(dt.files);
            }
          }}
        >
          <svg
            className="w-10 h-10 text-gray-400 mb-3"
            fill="none"
            viewBox="0 0 24 24"
            strokeWidth={1.5}
            stroke="currentColor"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              d="M3 16.5v2.25A2.25 2.25 0 005.25 21h13.5A2.25 2.25 0 0021 18.75V16.5m-13.5-9L12 3m0 0l4.5 4.5M12 3v13.5"
            />
          </svg>
          <p className="text-sm text-gray-600">
            <span className="font-medium text-indigo-600">
              Click to upload
            </span>{" "}
            or drag and drop
          </p>
          <p className="text-xs text-gray-500 mt-1">PDF only, max 5MB</p>
        </label>
      )}

      <input
        ref={inputRef}
        id="resume-input"
        type="file"
        accept=".pdf,application/pdf"
        className="sr-only"
        onChange={(e) => handleFiles(e.target.files)}
      />

      {error && <p className="mt-1 text-sm text-red-600">{error}</p>}
    </div>
  );
}
