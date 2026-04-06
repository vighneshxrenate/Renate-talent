import SubmissionForm from "@/components/SubmissionForm";

export default function Home() {
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
          <SubmissionForm />
        </div>
      </div>
    </main>
  );
}
