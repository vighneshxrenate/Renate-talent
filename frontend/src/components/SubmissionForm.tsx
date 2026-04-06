"use client";

import { useState } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { submissionSchema, SubmissionFormData } from "@/lib/validation";
import { submitResume } from "@/lib/api";
import { useCollegesAndIndustries } from "@/hooks/useCollegesAndIndustries";
import FileUpload from "./FileUpload";
import FormError from "./FormError";
import SuccessCard from "./SuccessCard";

export default function SubmissionForm() {
  const { colleges, industries, loading, error: dataError } = useCollegesAndIndustries();
  const [submitted, setSubmitted] = useState(false);
  const [serverError, setServerError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);

  const {
    register,
    handleSubmit,
    reset,
    setValue,
    trigger,
    formState: { errors },
  } = useForm<SubmissionFormData>({
    resolver: zodResolver(submissionSchema),
    defaultValues: {
      student_name: "",
      email: "",
      phone: "",
      college_id: "",
      industry_id: "",
      note: "",
    },
  });

  const onSubmit = async (data: SubmissionFormData) => {
    setSubmitting(true);
    setServerError(null);

    const formData = new FormData();
    formData.append("student_name", data.student_name);
    formData.append("email", data.email);
    formData.append("phone", data.phone);
    formData.append("college_id", data.college_id);
    formData.append("industry_id", data.industry_id);
    if (data.note) formData.append("note", data.note);
    formData.append("resume", data.resume[0]);

    try {
      await submitResume(formData);
      setSubmitted(true);
    } catch (err) {
      setServerError(
        err instanceof Error ? err.message : "Something went wrong"
      );
    } finally {
      setSubmitting(false);
    }
  };

  const handleReset = () => {
    reset();
    setSubmitted(false);
    setServerError(null);
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center py-16">
        <div className="h-8 w-8 animate-spin rounded-full border-4 border-gray-200 border-t-indigo-600" />
      </div>
    );
  }

  if (dataError) {
    return (
      <div className="text-center py-16 px-6">
        <p className="text-red-600">Failed to load form data. Please refresh the page.</p>
      </div>
    );
  }

  if (submitted) {
    return <SuccessCard onReset={handleReset} />;
  }

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
      {serverError && (
        <FormError
          message={serverError}
          onDismiss={() => setServerError(null)}
        />
      )}

      {/* College */}
      <div>
        <label
          htmlFor="college_id"
          className="block text-sm font-medium text-gray-700 mb-1"
        >
          College / University <span className="text-red-500">*</span>
        </label>
        <select
          {...register("college_id")}
          id="college_id"
          className="w-full rounded-lg border border-gray-300 px-3 py-2.5 text-gray-900 focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 bg-white"
        >
          <option value="">Select your college</option>
          {colleges.map((c) => (
            <option key={c.id} value={c.id}>
              {c.name}
            </option>
          ))}
        </select>
        {errors.college_id && (
          <p className="mt-1 text-sm text-red-600">
            {errors.college_id.message}
          </p>
        )}
      </div>

      {/* Industry */}
      <div>
        <label
          htmlFor="industry_id"
          className="block text-sm font-medium text-gray-700 mb-1"
        >
          Target Industry <span className="text-red-500">*</span>
        </label>
        <select
          {...register("industry_id")}
          id="industry_id"
          className="w-full rounded-lg border border-gray-300 px-3 py-2.5 text-gray-900 focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 bg-white"
        >
          <option value="">Select your industry</option>
          {industries.map((i) => (
            <option key={i.id} value={i.id}>
              {i.name}
            </option>
          ))}
        </select>
        {errors.industry_id && (
          <p className="mt-1 text-sm text-red-600">
            {errors.industry_id.message}
          </p>
        )}
      </div>

      {/* Name */}
      <div>
        <label
          htmlFor="student_name"
          className="block text-sm font-medium text-gray-700 mb-1"
        >
          Full Name <span className="text-red-500">*</span>
        </label>
        <input
          {...register("student_name")}
          id="student_name"
          type="text"
          placeholder="Enter your full name"
          className="w-full rounded-lg border border-gray-300 px-3 py-2.5 text-gray-900 placeholder-gray-400 focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500"
        />
        {errors.student_name && (
          <p className="mt-1 text-sm text-red-600">
            {errors.student_name.message}
          </p>
        )}
      </div>

      {/* Email */}
      <div>
        <label
          htmlFor="email"
          className="block text-sm font-medium text-gray-700 mb-1"
        >
          Email <span className="text-red-500">*</span>
        </label>
        <input
          {...register("email")}
          id="email"
          type="email"
          placeholder="you@example.com"
          className="w-full rounded-lg border border-gray-300 px-3 py-2.5 text-gray-900 placeholder-gray-400 focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500"
        />
        {errors.email && (
          <p className="mt-1 text-sm text-red-600">{errors.email.message}</p>
        )}
      </div>

      {/* Phone */}
      <div>
        <label
          htmlFor="phone"
          className="block text-sm font-medium text-gray-700 mb-1"
        >
          Phone <span className="text-red-500">*</span>
        </label>
        <input
          {...register("phone")}
          id="phone"
          type="tel"
          placeholder="+91 98765 43210"
          className="w-full rounded-lg border border-gray-300 px-3 py-2.5 text-gray-900 placeholder-gray-400 focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500"
        />
        {errors.phone && (
          <p className="mt-1 text-sm text-red-600">{errors.phone.message}</p>
        )}
      </div>

      {/* Resume Upload */}
      <FileUpload
        error={errors.resume?.message as string | undefined}
        onFileSelect={(files) => {
          setValue("resume", files as unknown as FileList, {
            shouldValidate: true,
          });
        }}
      />

      {/* Note */}
      <div>
        <label
          htmlFor="note"
          className="block text-sm font-medium text-gray-700 mb-1"
        >
          Short Note{" "}
          <span className="text-gray-400 font-normal">(optional)</span>
        </label>
        <textarea
          {...register("note")}
          id="note"
          rows={3}
          placeholder="Tell us about yourself or why you belong to this industry..."
          className="w-full rounded-lg border border-gray-300 px-3 py-2.5 text-gray-900 placeholder-gray-400 focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 resize-none"
        />
        {errors.note && (
          <p className="mt-1 text-sm text-red-600">{errors.note.message}</p>
        )}
      </div>

      {/* Submit */}
      <button
        type="submit"
        disabled={submitting}
        className="w-full rounded-lg bg-indigo-600 px-4 py-3 text-sm font-semibold text-white hover:bg-indigo-700 focus:outline-2 focus:outline-offset-2 focus:outline-indigo-600 disabled:opacity-50 disabled:cursor-not-allowed cursor-pointer transition-colors"
      >
        {submitting ? (
          <span className="flex items-center justify-center gap-2">
            <span className="h-4 w-4 animate-spin rounded-full border-2 border-white border-t-transparent" />
            Submitting...
          </span>
        ) : (
          "Submit Application"
        )}
      </button>
    </form>
  );
}
