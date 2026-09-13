"use client";
export default function ErrorPage({ reset }: { reset: () => void }) {
  return <div role="alert" className="rounded-xl border border-amber-300 bg-amber-50 p-6">
    <h1 className="text-xl font-semibold">This section could not be displayed</h1>
    <button onClick={reset} className="mt-4 cursor-pointer underline">Try again</button>
  </div>;
}
