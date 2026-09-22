import { getBackendHealth, getOverview } from "@/lib/api";
import { TickerForm } from "@/components/ticker-form";
import { OverviewCharts } from "@/components/overview-charts";
import { DashboardAnchor } from "@/components/navigation";
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
        <p className="page-description">Explore price behaviour. Understand the risk behind the movement.</p></div>
      <TickerForm ticker={ticker} />
    </div>
    {result.error && <div role="alert" className="error-panel">
      <h2>Overview unavailable for {ticker || "this ticker"}</h2><p>{result.error}</p>
      <p>No substitute prices or metrics are displayed. Try another ticker or reload the overview.</p>
    </div>}
    {data && <div key={data.ticker}>
      <div className="instrument-bar">
        <div className="instrument-identity"><span className="ticker-avatar" aria-hidden="true">{data.ticker.charAt(0)}</span>
          <div><h2>{data.ticker} · Historical overview</h2><p className="instrument-subtitle">{data.currency ?? "Currency unavailable"} / share <span aria-hidden="true"> · </span> {data.history.length} daily observations</p></div>
        </div>
        <div className="session-meta"><p>Latest session <strong>{data.as_of}</strong></p><p>Retrieved {new Date(data.timestamp).toLocaleString("en-GB", { timeZone: "UTC", day: "2-digit", month: "short", hour: "2-digit", minute: "2-digit" })} UTC</p></div>
      </div>
      <div className="metrics-grid">
        <Metric index="01" label="Spot · last daily close" value={price(data.spot)} detail={`${data.currency ?? "Currency unavailable"} per share · historical, not live`} />
        <Metric index="02" label="Daily change" value={percent(data.daily_change_pct)} detail={`${price(data.daily_change)} ${data.currency ?? "currency unknown"} · previous close comparison`} />
        <Metric index="03" label="HV20" value={percent(data.hv20)} detail="20-session realized volatility · annualized" accent />
        <Metric index="04" label="HV30" value={percent(data.hv30)} detail="30-session realized volatility · annualized" accent />
      </div>
      <OverviewCharts history={data.history} currency={data.currency} />
    </div>}
    {!data && <section id="volatility" className="planned-panel" style={{ marginTop: 20 }}><div className="planned-top"><span className="section-number">04</span><h2>Volatility</h2></div><p>Historical volatility is unavailable until a valid price history can be loaded. Implied volatility is not implemented.</p></section>}
    <div className="planned-grid">
      <section id="option-chain" className="planned-panel" aria-labelledby="chain-title">
        <div className="planned-top"><span className="section-number">02</span><h2 id="chain-title">Option Chain</h2><span className="planned-label">Planned · not built</span></div>
        <p>The next layer of the underlying: option contracts organised by strike and expiry. Option quotes are not connected yet.</p>
        <div className="planned-scope"><span>Expiry & strike</span><span>Bid / ask</span><span>Quote quality</span></div>
      </section>
      <PricingLab />
    </div>
    <div className="methodology">
      <div className="methodology-top"><details>
        <summary>Methodology & data limitations</summary>
        <div className="methodology-body">
          {data ? <><p>{data.units}. Estimator: {data.volatility_basis}.</p>
            <p>HV20 needs 21 valid closes; HV30 needs 31. Annualization uses 252 sessions. Unavailable values are never interpreted as zero. Realized volatility is historical; implied volatility is not implemented.</p>
            <ul>{data.warnings.map(warning => <li key={warning}>{warning}</li>)}</ul></>
            : <p>Historical analytics require valid price data. The Pricing Lab remains available because it uses user-supplied model assumptions.</p>}
          <p>Pricing Lab uses dividend-adjusted European Black–Scholes with ACT/365 for day inputs. Its output is theoretical and is not an observed market price. Greeks and implied volatility are not implemented.</p>
        </div>
      </details><span role="status" className={`connection ${health === "connected" ? "" : "offline"}`}><span className="status-dot" />{health === "connected" ? "Backend connected" : "Backend unavailable"}</span></div>
      {data && <p className="source-line">SOURCE: {data.source} · End-of-day observations, not live quotes · Adjusted closes for HV · No missing-price interpolation</p>}
    </div>
  </>;
}

function Metric({ index, label, value, detail, accent = false }: { index: string; label: string; value: string; detail: string; accent?: boolean }) {
  return <section className="metric"><div className="metric-top"><h3>{label}</h3><span className="metric-index">{index}</span></div>
    <p className={`metric-value ${value === "Unavailable" ? "unavailable" : accent ? "metric-accent" : ""}`}>{value}</p><p className="metric-detail">{detail}</p>
  </section>;
}
