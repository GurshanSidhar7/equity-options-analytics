import { SectionPlaceholder } from "@/components/section-placeholder";
import { getBackendHealth } from "@/lib/api";

export const dynamic = "force-dynamic";

export default async function Overview() {
  const health = await getBackendHealth();
  return <>
    <SectionPlaceholder title="Overview"
    description="The starting point for learning about the underlying equity, historical returns, and realized volatility."
    limitation="Scaffolding only. No data, calculations, charts, or analytics endpoints have been implemented. Features will be built one learning day at a time." />
    <section aria-labelledby="backend-health-title" className="mt-6 rounded-xl border border-slate-200 bg-white p-6">
      <h2 id="backend-health-title" className="text-lg font-semibold">Application connection</h2>
      <p role="status" className={`mt-3 text-sm font-medium ${health === "connected" ? "text-emerald-800" : "text-amber-800"}`}>
        {health === "connected" ? "Backend connected" : "Backend unavailable"}
      </p>
      <p className="mt-2 text-sm text-slate-600">
        {health === "connected"
          ? "The application service responded. No market-data feed is connected."
          : "The application service could not be reached or returned an unexpected response. Refresh to check again."}
      </p>
      <a href="/" className="mt-3 inline-block text-sm underline">Check again</a>
    </section>
  </>;
}
