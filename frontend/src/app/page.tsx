import { getBackendHealth, getOverview } from "@/lib/api";
import { TickerForm } from "@/components/ticker-form";
import { OverviewCharts } from "@/components/overview-charts";
import { DashboardAnchor } from "@/components/navigation";
import { DeskTranslator } from "@/components/desk-translator";
import { TickerIntelligence } from "@/components/ticker-intelligence";
import { PricingLab } from "@/components/pricing-lab";

export const dynamic = "force-dynamic";
const percent = (value: number | null) => value === null ? "Unavailable" : new Intl.NumberFormat("en", { style: "percent", minimumFractionDigits: 2, maximumFractionDigits: 2 }).format(value);
const price = (value: number | null) => value === null ? "Unavailable" : new Intl.NumberFormat("en", { minimumFractionDigits: 2, maximumFractionDigits: 2 }).format(value);

export default async function Overview({ searchParams }: { searchParams: Promise<{ ticker?: string | string[] }> }) {
  const params = await searchParams;
  const ticker = (typeof params.ticker === "string" ? params.ticker : "AAPL").trim().toUpperCase();
  const [result, health] = await Promise.all([getOverview(ticker), getBackendHealth()]);
  const data = result.data;
  return <>
    <DashboardAnchor ticker={ticker} />
    <div id="overview" className="page-heading">
      <div><p className="eyebrow"><span className="eyebrow-line" /> EQUITY / RESEARCH WORKSPACE</p><h1>Market <span>overview.</span></h1>
        <p className="page-description">One place to review the underlying, inspect realized risk, and test model assumptions.</p></div>
      <TickerForm ticker={ticker} />
    </div>
    {result.error && <div role="alert" className="error-panel">
      <h2>Overview unavailable for {ticker || "this ticker"}</h2><p>{result.error}</p>
      <p>No substitute prices or metrics are displayed. Try another ticker or reload the overview.</p>
    </div>}
    {data && <div key={data.ticker}>
      <OverviewCharts history={data.history} currency={data.currency} summary={<>
        <div className="instrument-bar">
          <div className="instrument-identity"><span className="ticker-avatar" aria-hidden="true">{data.ticker.charAt(0)}</span>
            <div><p className="instrument-eyebrow">SELECTED UNDERLYING</p><h2>{data.ticker} · Historical overview</h2><p className="instrument-subtitle">{data.currency ?? "Currency unavailable"} / share <span aria-hidden="true"> · </span> {data.history.length} daily observations</p></div>
          </div>
          <div className="instrument-actions"><div className="session-meta"><p>Latest session <strong>{data.as_of}</strong></p><p>Retrieved {new Date(data.timestamp).toLocaleString("en-GB", { timeZone: "UTC", day: "2-digit", month: "short", hour: "2-digit", minute: "2-digit" })} UTC</p></div>
            <a className="instrument-link" href="#pricing-lab">Open Pricing Lab <span aria-hidden="true">↗</span></a></div>
        </div>
        <div className="metrics-grid">
          <Metric index="01" label="Spot · last daily close" value={price(data.spot)} detail={`${data.currency ?? "Currency unavailable"} per share · historical, not live`} />
          <Metric index="02" label="Daily change" value={percent(data.daily_change_pct)} detail={`${price(data.daily_change)} ${data.currency ?? "currency unknown"} · previous close comparison`} />
          <Metric index="03" label="HV20" value={percent(data.hv20)} detail="20-session realized volatility · annualized" accent />
          <Metric index="04" label="HV30" value={percent(data.hv30)} detail="30-session realized volatility · annualized" accent />
        </div>
        <div className="data-context" aria-label="Research data context">
          <div><span>Source</span><strong>{data.source}</strong></div>
          <div><span>Spot basis</span><strong>Latest completed daily close · not live</strong></div>
          <div><span>Volatility basis</span><strong>Adjusted returns · 252 sessions/year</strong></div>
        </div>
      </>} />
    </div>}
    <TickerIntelligence key={`news-${ticker}-${data?.timestamp ?? "unavailable"}`} ticker={ticker} />
    {data?.desk_translator && <DeskTranslator key={`explanation-${ticker}`} items={data.desk_translator.items} context="Overview" />}
    {!data && <section id="volatility" className="planned-panel" style={{ marginTop: 20 }}><div className="planned-top"><span className="section-number">02</span><h2>Volatility</h2></div><p>Historical volatility is unavailable until a valid price history can be loaded. Implied volatility is not implemented.</p></section>}
    <PricingLab key={`pricing-${ticker}-${data?.as_of ?? "manual"}-${data?.spot ?? "missing"}`} reference={data?.spot != null ? { ticker: data.ticker, spot: data.spot, currency: data.currency, asOf: data.as_of } : null} />
    <section id="option-chain" className="planned-panel planned-chain" aria-labelledby="chain-title">
      <div><div className="planned-top"><span className="section-number">04</span><h2 id="chain-title">Option Chain</h2><span className="planned-label">Planned · not built</span></div>
        <p>Real contract quotes are not connected yet. This section will show expiry, strike, bid/ask, and quote quality when that data is available.</p></div>
      <div className="planned-scope"><span>Expiry & strike</span><span>Bid / ask</span><span>Quote quality</span></div>
    </section>
    <div className="methodology">
      <div className="methodology-top"><details>
        <summary>Methodology & data limitations</summary>
        <div className="methodology-body">
          {data ? <><p>{data.units}. Estimator: {data.volatility_basis}.</p>
            <p>HV20 needs 21 valid closes; HV30 needs 31. Annualization uses 252 sessions. Unavailable values are never interpreted as zero. Realized volatility is historical; implied volatility is not implemented.</p>
            <ul>{data.warnings.map(warning => <li key={warning}>{warning}</li>)}</ul></>
            : <p>Historical analytics require valid price data. The Pricing Lab remains available because it uses user-supplied model assumptions.</p>}
          <p>Pricing Lab uses dividend-adjusted European Black–Scholes with ACT/365 for day inputs. Its output and Greeks are theoretical and are not observed market prices or sensitivities. Delta and Gamma use a one-unit spot move; Vega uses one volatility percentage point; Theta uses one calendar day. Greeks are local sensitivities and unavailable at expiry or effectively zero volatility. Implied volatility is not implemented.</p>
        </div>
      </details><span role="status" className={`connection ${health === "connected" ? "" : "offline"}`}><span className="status-dot" />{health === "connected" ? "Backend connected" : "Backend unavailable"}</span></div>
      {data && <p className="source-line">End-of-day observations, not live quotes · Adjusted closes for HV · No missing-price interpolation</p>}
    </div>
  </>;
}

function Metric({ index, label, value, detail, accent = false }: { index: string; label: string; value: string; detail: string; accent?: boolean }) {
  return <section className="metric"><div className="metric-top"><h3>{label}</h3><span className="metric-index">{index}</span></div>
    <p className={`metric-value ${value === "Unavailable" ? "unavailable" : accent ? "metric-accent" : ""}`}>{value}</p><p className="metric-detail">{detail}</p>
  </section>;
}
