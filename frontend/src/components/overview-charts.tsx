"use client";

import { useEffect, useRef, useState } from "react";
import type { ReactNode } from "react";
import type { HistoryPoint } from "@/lib/types";

function Chart({ history, kind, currency }: { history: HistoryPoint[]; kind: "price" | "volatility"; currency: string | null }) {
  const ref = useRef<HTMLDivElement>(null);
  const [failed, setFailed] = useState(false);
  const keys = kind === "price" ? ["close"] as const : ["hv20", "hv30"] as const;
  const hasValues = history.some(row => keys.some(key => row[key] !== null));
  useEffect(() => {
    const element = ref.current;
    if (!element || !hasValues) return;
    let disposed = false;
    let observer: ResizeObserver | undefined;
    let purge: (() => void) | undefined;
    setFailed(false);
    async function draw() {
      const Plotly = await import("plotly.js-basic-dist-min");
      if (disposed || !element) return;
      purge = () => Plotly.purge(element);
      const fields = kind === "price" ? ["close"] as const : ["hv20", "hv30"] as const;
      await Plotly.newPlot(element, fields.map((field, index) => ({
        x: history.map(row => row.date), y: history.map(row => row[field]),
        type: "scatter", mode: "lines", connectgaps: false,
        name: field === "close" ? "Daily close" : field.toUpperCase(),
        line: { color: index === 0 ? "#4b5d49" : "#90661f", width: 2.3 },
        hovertemplate: kind === "price" ? "%{x}<br>%{y:.2f}<extra>%{fullData.name}</extra>" : "%{x}<br>%{y:.2%}<extra>%{fullData.name}</extra>",
      })), {
        height: element.clientHeight, width: element.clientWidth, autosize: true, hovermode: "x unified", showlegend: false,
        margin: { t: 20, r: 16, b: 45, l: 53 },
        xaxis: { type: "date", nticks: 5, automargin: true, showgrid: false, zeroline: false, tickfont: { size: 11 }, tickcolor: "transparent" },
        yaxis: { tickformat: kind === "price" ? ",.2f" : ".1%", automargin: true, gridcolor: "#e0d8cb", zeroline: false, nticks: 5, tickfont: { size: 11 } },
        legend: { orientation: "h", y: 1.15 },
        paper_bgcolor: "transparent", plot_bgcolor: "transparent",
        font: { family: "Inter, Arial, sans-serif", color: "#6c675f", size: 11 },
        hoverlabel: { bgcolor: "#292520", bordercolor: "#292520", font: { color: "#ffffff", size: 12 } },
      }, { responsive: false, displayModeBar: false });
      if (disposed) { purge(); return; }
      observer = new ResizeObserver(() => {
        if (!disposed && element.isConnected && element.offsetWidth > 0 && element.offsetHeight > 0) {
          // Keep the SVG aligned with the responsive container in both dimensions.
          void Plotly.relayout(element, { width: element.clientWidth, height: element.clientHeight }).catch(() => {});
        }
      });
      observer.observe(element);
    }
    void draw().catch(() => { if (!disposed) setFailed(true); });
    return () => { disposed = true; observer?.disconnect(); purge?.(); };
  }, [history, kind, currency, hasValues]);
  if (!hasValues) return <p className="chart-empty">Unavailable — no valid {kind === "price" ? "closing prices" : "complete volatility windows"} in the returned history.</p>;
  return <>
    {failed && <p role="status">Chart unavailable. The historical values are listed below.</p>}
    <div ref={ref} role="img" aria-label={kind === "price" ? "Historical daily closing prices" : "Annualized HV20 and HV30 historical volatility"} className={`history-plot ${kind}-plot`} />
  </>;
}

const percent = (value: number | null) => value === null ? "Unavailable" : new Intl.NumberFormat("en", { style: "percent", maximumFractionDigits: 2 }).format(value);

export function OverviewCharts({ history, currency, summary }: { history: HistoryPoint[]; currency: string | null; summary: ReactNode }) {
  return <>
    <div className="charts-grid">
      <article className="chart-panel price-focus">
        <div className="overview-summary">{summary}</div>
        <div className="panel-header"><div><span className="panel-eyebrow">01 / OVERVIEW</span><h2>Historical Price</h2><p>Daily closing price · {currency ?? "currency unavailable"} per share</p></div><span className="chart-chip">1D observations</span></div>
        <div className="chart-frame"><Chart history={history} kind="price" currency={currency} /></div>
        <div className="chart-footer"><span>Split-adjusted · excludes dividend adjustments</span><span>Drag to zoom</span></div>
      </article>
      <section id="volatility" className="chart-panel" aria-labelledby="volatility-title">
        <div className="panel-header"><div><span className="panel-eyebrow">02 / VOLATILITY</span><h2 id="volatility-title">Realized Volatility</h2><p>Annualized historical risk · 252 trading sessions</p></div><span className="chart-chip">Historical</span></div>
        <div className="chart-legend"><span><i style={{ background: "#4b5d49" }} />HV20</span><span><i style={{ background: "#90661f" }} />HV30</span></div>
        <div className="chart-frame"><Chart history={history} kind="volatility" currency={currency} /></div>
        <div className="chart-footer"><span>Adjusted log returns · sample standard deviation</span><span>No implied volatility</span></div>
      </section>
    </div>
    <details className="data-disclosure">
      <summary>Inspect historical observations <span className="disclosure-meta"> · {history.length} rows · prices & volatility</span></summary>
      <div className="table-wrap"><table className="history-table">
        <caption>Prices in {currency ?? "an unspecified provider currency"}; volatility displayed as percentages. Missing values remain unavailable.</caption>
        <thead><tr>{["Session", "Close", "Adjusted close", "HV20", "HV30"].map(label => <th key={label}>{label}</th>)}</tr></thead>
        <tbody>{history.map(row => <tr key={row.date}>
          <td>{row.date}</td><td>{row.close?.toFixed(2) ?? "Unavailable"}</td>
          <td>{row.adjusted_close?.toFixed(2) ?? "Unavailable"}</td>
          <td>{percent(row.hv20)}</td><td>{percent(row.hv30)}</td>
        </tr>)}</tbody>
      </table></div>
    </details>
  </>;
}
