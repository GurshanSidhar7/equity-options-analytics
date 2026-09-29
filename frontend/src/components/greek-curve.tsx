"use client";

import { useEffect, useRef, useState } from "react";
import type { GreekCurvePoint, GreekValues } from "@/components/pricing-lab";

type GreekKey = keyof GreekValues;

const choices: { key: GreekKey; label: string; unit: string }[] = [
  { key: "delta", label: "Delta", unit: "price / +1 spot" },
  { key: "gamma", label: "Gamma", unit: "Delta / +1 spot" },
  { key: "vega_per_vol_point", label: "Vega", unit: "price / +1 vol point" },
  { key: "theta_per_day", label: "Theta", unit: "price / calendar day" },
];

export function GreekCurve({ points, currentSpot, current }: { points: GreekCurvePoint[]; currentSpot: number; current: GreekValues }) {
  const [selected, setSelected] = useState<GreekKey>("delta");
  const [failed, setFailed] = useState(false);
  const ref = useRef<HTMLDivElement>(null);
  const choice = choices.find(item => item.key === selected)!;

  useEffect(() => {
    const element = ref.current;
    if (!element) return;
    let disposed = false;
    let observer: ResizeObserver | undefined;
    let purge: (() => void) | undefined;
    setFailed(false);
    async function draw() {
      const Plotly = await import("plotly.js-basic-dist-min");
      if (disposed || !element) return;
      purge = () => Plotly.purge(element);
      await Plotly.newPlot(element, [
        {
          x: points.map(point => point.spot), y: points.map(point => point[selected]),
          type: "scatter", mode: "lines", name: choice.label,
          line: { color: "#67eed5", width: 2.5 },
          hovertemplate: "Spot %{x:.2f}<br>%{y:.4f}<extra>%{fullData.name}</extra>",
        },
        {
          x: [currentSpot], y: [current[selected]], type: "scatter", mode: "markers", name: "Current input",
          marker: { color: "#c5adff", size: 10, line: { color: "#f3edff", width: 1 } },
          hovertemplate: "Current spot %{x:.2f}<br>%{y:.4f}<extra></extra>",
        },
      ], {
        height: 260, width: element.clientWidth, autosize: true, showlegend: false,
        margin: { t: 12, r: 20, b: 45, l: 60 },
        xaxis: { title: { text: "Spot · currency / share", font: { size: 10 } }, automargin: true, gridcolor: "#233047", zeroline: false },
        yaxis: { title: { text: choice.unit, font: { size: 10 } }, automargin: true, gridcolor: "#233047", zeroline: false },
        paper_bgcolor: "transparent", plot_bgcolor: "transparent",
        font: { family: "Arial, sans-serif", color: "#9cacc5", size: 10 },
        hoverlabel: { bgcolor: "#111c2d", bordercolor: "#111c2d", font: { color: "#ffffff", size: 11 } },
      }, { responsive: false, displayModeBar: false });
      if (disposed) { purge(); return; }
      observer = new ResizeObserver(() => {
        if (!disposed && element.isConnected && element.offsetWidth > 0) {
          void Plotly.relayout(element, { width: element.clientWidth }).catch(() => {});
        }
      });
      observer.observe(element);
    }
    void draw().catch(() => { if (!disposed) setFailed(true); });
    return () => { disposed = true; observer?.disconnect(); purge?.(); };
  }, [points, currentSpot, current, selected, choice.label, choice.unit]);

  return <div className="greek-curve-panel">
    <div className="greek-curve-heading"><div><h3>Greek vs spot</h3><p>Only spot varies; strike, time, volatility, rate, and dividend yield stay at the submitted values. Purple marks the submitted spot.</p></div>
      <label>Show Greek <select aria-label="Show Greek" value={selected} onChange={event => setSelected(event.target.value as GreekKey)}>{choices.map(item => <option value={item.key} key={item.key}>{item.label}</option>)}</select></label>
    </div>
    {failed && <p role="status">Greek chart unavailable. The values above are still available.</p>}
    <div ref={ref} role="img" aria-label={`${choice.label} versus spot for the submitted option assumptions`} className="greek-plot" />
  </div>;
}
