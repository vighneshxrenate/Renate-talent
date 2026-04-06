"use client";

interface SuccessCardProps {
  onReset: () => void;
}

export default function SuccessCard({ onReset }: SuccessCardProps) {
  return (
    <div className="text-center py-12 px-6">
      <div className="mx-auto w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mb-6">
        <svg
          className="w-8 h-8 text-green-600"
          fill="none"
          viewBox="0 0 24 24"
          strokeWidth={2}
          stroke="currentColor"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            d="M4.5 12.75l6 6 9-13.5"
          />
        </svg>
      </div>
      <h2 className="text-2xl font-semibold text-gray-900 mb-2">
        Submission Received
      </h2>
      <p className="text-gray-600 mb-8">
        Your resume has been submitted successfully. We&apos;ll be in touch!
      </p>
      <button
        onClick={onReset}
        className="text-indigo-600 hover:text-indigo-800 font-medium cursor-pointer"
      >
        Submit another resume
      </button>
    </div>
  );
}
