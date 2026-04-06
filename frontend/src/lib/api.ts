import { College, Industry, SubmissionResponse } from "./types";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api";

export async function fetchColleges(): Promise<College[]> {
  const res = await fetch(`${API_URL}/colleges`);
  if (!res.ok) throw new Error("Failed to fetch colleges");
  return res.json();
}

export async function fetchIndustries(): Promise<Industry[]> {
  const res = await fetch(`${API_URL}/industries`);
  if (!res.ok) throw new Error("Failed to fetch industries");
  return res.json();
}

export async function submitResume(
  formData: FormData
): Promise<SubmissionResponse> {
  const res = await fetch(`${API_URL}/submissions`, {
    method: "POST",
    body: formData,
  });

  if (!res.ok) {
    const error = await res.json();
    const detail = error.detail;
    if (typeof detail === "string") {
      throw new Error(detail);
    }
    if (Array.isArray(detail)) {
      throw new Error(detail.map((e: { msg: string }) => e.msg).join(", "));
    }
    throw new Error("Submission failed");
  }

  return res.json();
}
