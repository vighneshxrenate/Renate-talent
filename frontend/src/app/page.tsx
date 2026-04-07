export const dynamic = "force-dynamic";

import { College, Industry } from "@/lib/types";
import SubmissionForm from "@/components/SubmissionForm";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api";

async function getFormData(): Promise<{
  colleges: College[];
  industries: Industry[];
}> {
  const [collegesRes, industriesRes] = await Promise.all([
    fetch(`${API_URL}/colleges`, { next: { revalidate: 3600 } }),
    fetch(`${API_URL}/industries`, { next: { revalidate: 3600 } }),
  ]);

  if (!collegesRes.ok || !industriesRes.ok) {
    throw new Error("Failed to load form data");
  }

  const [colleges, industries] = await Promise.all([
    collegesRes.json(),
    industriesRes.json(),
  ]);

  return { colleges, industries };
}

export default async function Home() {
  const { colleges, industries } = await getFormData();

  return (
    <main className="flex-1 flex items-start justify-center px-4 py-12 sm:py-16">
      <div className="w-full max-w-lg">
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold text-gray-900">
            Submit Your Resume
          </h1>
          <p className="mt-2 text-gray-600">
            Select your college, choose your target industry, and upload your
            resume to connect with top employers.
          </p>
        </div>

        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6 sm:p-8">
          <SubmissionForm colleges={colleges} industries={industries} />
        </div>
      </div>
    </main>
  );
}
