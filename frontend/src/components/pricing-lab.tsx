"use client";

import { FormEvent, useState } from "react";

interface PricingResult {
  option_type: "call" | "put";
  model_price: number;
  intrinsic_value: number;
  time_value: number;
  time_to_expiry_years: number;
  units: string;
  model: string;
}

const money = (value: number) => new Intl.NumberFormat("en", {
  minimumFractionDigits: 2,
  maximumFractionDigits: 4,
}).format(value);

export function PricingLab() {
  const [result, setResult] = useState<PricingResult | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [pending, setPending] = useState(false);

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setPending(true);
    setError(null);
    const values = new FormData(event.currentTarget);
    const payload = {
      spot: Number(values.get("spot")),
      strike: Number(values.get("strike")),
      time_to_expiry: Number(values.get("time_to_expiry")),
      time_unit: values.get("time_unit"),
      volatility: Number(values.get("volatility")),
      risk_free_rate: Number(values.get("risk_free_rate")),
      dividend_yield: Number(values.get("dividend_yield")),
      option_type: values.get("option_type"),
    };
    try {
      const response = await fetch("/api/pricing", {
        method: "POST",
        headers: { "content-type": "application/json" },
        body: JSON.stringify(payload),
      });
      const body = await response.json();
      if (!response.ok) {
        const detail = typeof body.detail === "string" ? body.detail : "Check that every input is valid.";
        throw new Error(detail);
      }
      setResult(body as PricingResult);
    } catch (reason) {
      setResult(null);
      setError(reason instanceof Error ? reason.message : "Pricing is unavailable.");
    } finally {
      setPending(false);
    }
  }

  return <section id="pricing-lab" className="pricing-lab" aria-labelledby="pricing-title">
    <div className="pricing-heading">
      <div><p className="pricing-kicker"><span>03</span> THEORETICAL PRICING</p>
        <h2 id="pricing-title">Pricing Lab</h2>
        <p>Explore a dividend-adjusted European Black–Scholes value. Inputs are assumptions, not observed option quotes.</p>
      </div>
      <span className="model-badge">European · Black–Scholes</span>
    </div>
    <div className="pricing-workspace">
      <form className="pricing-form" onSubmit={submit}>
        <fieldset className="option-toggle"><legend>Option type</legend>
          <label><input type="radio" name="option_type" value="call" defaultChecked /><span>Call</span></label>
          <label><input type="radio" name="option_type" value="put" /><span>Put</span></label>
        </fieldset>
        <div className="pricing-fields">
          <NumberField name="spot" label="Spot (S)" defaultValue="100" min="0.01" step="0.01" detail="Currency / share" />
          <NumberField name="strike" label="Strike (K)" defaultValue="100" min="0.01" step="0.01" detail="Currency / share" />
          <NumberField name="time_to_expiry" label="Time to expiry" defaultValue="30" min="0" step="0.01" detail="Converted using ACT/365" />
          <label className="pricing-field"><span>Time unit</span><select name="time_unit" defaultValue="days"><option value="days">Days</option><option value="years">Years (T)</option></select><small>Choose days or years</small></label>
          <NumberField name="volatility" label="Volatility (σ)" defaultValue="0.20" min="0" step="0.01" detail="Decimal: 0.20 = 20%" />
          <NumberField name="risk_free_rate" label="Risk-free rate (r)" defaultValue="0.05" step="0.001" detail="Decimal: 0.05 = 5%" />
          <NumberField name="dividend_yield" label="Dividend yield (q)" defaultValue="0.02" step="0.001" detail="Continuous decimal yield" />
        </div>
        <button className="price-button" type="submit" disabled={pending}>{pending ? "Calculating…" : "Calculate model value"}<span aria-hidden="true">→</span></button>
      </form>
      <div className="pricing-output" aria-live="polite">
        <p className="output-label">MODEL OUTPUT</p>
        {error && <div role="alert" className="pricing-error">{error}</div>}
        {!result && !error && <div className="output-empty"><span>ƒ</span><h3>Set assumptions and calculate</h3><p>The result will come from the Python pricing engine.</p></div>}
        {result && <>
          <div className="primary-output"><span>{result.option_type.toUpperCase()} MODEL VALUE</span><strong>{money(result.model_price)}</strong><small>currency units per share</small></div>
          <div className="output-breakdown">
            <div><span>Intrinsic value</span><strong>{money(result.intrinsic_value)}</strong></div>
            <div><span>Time value</span><strong>{money(result.time_value)}</strong></div>
          </div>
          <p className="output-meta">T = {result.time_to_expiry_years.toFixed(6)} years · {result.model}</p>
        </>}
        <div className="output-note"><strong>Theoretical value, not a market price.</strong><p>Constant volatility, rates, and dividend yield; European exercise only. Time value is model value minus spot intrinsic value and can be negative for some dividend-paying European options.</p></div>
      </div>
    </div>
  </section>;
}

function NumberField({ name, label, defaultValue, detail, min, step }: { name: string; label: string; defaultValue: string; detail: string; min?: string; step: string }) {
  return <label className="pricing-field"><span>{label}</span><input name={name} type="number" defaultValue={defaultValue} min={min} step={step} required inputMode="decimal" /><small>{detail}</small></label>;
}
