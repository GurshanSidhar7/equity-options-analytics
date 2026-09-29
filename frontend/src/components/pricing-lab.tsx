"use client";

import { FormEvent, useRef, useState } from "react";
import { GreekCurve } from "@/components/greek-curve";

export interface GreekValues {
  delta: number | null;
  gamma: number | null;
  vega_per_vol_point: number | null;
  theta_per_day: number | null;
}

export interface GreekCurvePoint extends GreekValues {
  spot: number;
}

interface PricingResult {
  option_type: "call" | "put";
  spot: number;
  model_price: number;
  intrinsic_value: number;
  time_value: number;
  time_to_expiry_years: number;
  units: string;
  model: string;
  greeks: GreekValues;
  greek_curve: GreekCurvePoint[];
  greek_units: string;
}

const money = (value: number) => new Intl.NumberFormat("en", {
  minimumFractionDigits: 2,
  maximumFractionDigits: 4,
}).format(value);

interface SpotReference {
  ticker: string;
  spot: number;
  currency: string | null;
  asOf: string;
}

interface PricingInputs {
  spot: number;
  strike: number;
  time_to_expiry: number;
  time_unit: string;
  volatility: number;
  risk_free_rate: number;
  dividend_yield: number;
  option_type: string;
}

function readInputs(form: HTMLFormElement): PricingInputs {
  const values = new FormData(form);
  return {
    spot: Number(values.get("spot")),
    strike: Number(values.get("strike")),
    time_to_expiry: Number(values.get("time_to_expiry")),
    time_unit: String(values.get("time_unit")),
    volatility: Number(values.get("volatility")),
    risk_free_rate: Number(values.get("risk_free_rate")),
    dividend_yield: Number(values.get("dividend_yield")),
    option_type: String(values.get("option_type")),
  };
}

export function PricingLab({ reference }: { reference: SpotReference | null }) {
  const [result, setResult] = useState<PricingResult | null>(null);
  const [submitted, setSubmitted] = useState<PricingInputs | null>(null);
  const [inputsChanged, setInputsChanged] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [pending, setPending] = useState(false);
  const formRef = useRef<HTMLFormElement>(null);

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setPending(true);
    setError(null);
    const payload = readInputs(event.currentTarget);
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
      setSubmitted(payload);
      setInputsChanged(formRef.current !== null && JSON.stringify(readInputs(formRef.current)) !== JSON.stringify(payload));
    } catch (reason) {
      setResult(null);
      setSubmitted(null);
      setInputsChanged(false);
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
      <form ref={formRef} className="pricing-form" onSubmit={submit} onChange={event => {
        if (submitted) setInputsChanged(JSON.stringify(readInputs(event.currentTarget)) !== JSON.stringify(submitted));
      }}>
        <div className="assumption-source" role="note"><span>STARTING INPUTS</span>
          {reference ? <p><strong>{reference.ticker} close: {money(reference.spot)} {reference.currency ?? "currency units"} per share</strong> · completed session {reference.asOf}. Spot starts from this historical close. Strike starts at the same number for illustration, not from a listed contract. Edit both as needed; time, volatility, rate, and yield are sample assumptions.</p>
            : <p><strong>Sample assumptions</strong> are ready to edit. No valid historical close is available to prefill spot or strike.</p>}
        </div>
        <fieldset className="option-toggle"><legend>Option type</legend>
          <label><input type="radio" name="option_type" value="call" defaultChecked /><span>Call</span></label>
          <label><input type="radio" name="option_type" value="put" /><span>Put</span></label>
        </fieldset>
        <div className="pricing-fields">
          <NumberField name="spot" label="Spot (S)" defaultValue={reference ? String(reference.spot) : "100"} min="0.01" step="any" detail={reference ? "Latest completed close · editable" : "Sample value · currency / share"} />
          <NumberField name="strike" label="Strike (K)" defaultValue={reference ? String(reference.spot) : "100"} min="0.01" step="any" detail={reference ? "Illustrative strike · edit for contract" : "Sample value · currency / share"} />
          <NumberField name="time_to_expiry" label="Time to expiry" defaultValue="30" min="0" step="0.01" detail="Converted using ACT/365" />
          <label className="pricing-field"><span>Time unit</span><select name="time_unit" defaultValue="days"><option value="days">Days</option><option value="years">Years (T)</option></select><small>Choose days or years</small></label>
          <NumberField name="volatility" label="Volatility (σ)" defaultValue="0.20" min="0" step="0.01" detail="Decimal: 0.20 = 20%" />
          <NumberField name="risk_free_rate" label="Risk-free rate (r)" defaultValue="0.05" step="0.001" detail="Decimal: 0.05 = 5%" />
          <NumberField name="dividend_yield" label="Dividend yield (q)" defaultValue="0.02" step="0.001" detail="Continuous decimal yield" />
        </div>
        <button className="price-button" type="submit" disabled={pending}>{pending ? "Calculating…" : "Calculate model value"}<span aria-hidden="true">→</span></button>
      </form>
      <div className="pricing-output" aria-live="polite">
        <p className="output-label">{inputsChanged ? "PREVIOUS MODEL OUTPUT" : "MODEL OUTPUT"}</p>
        {result && inputsChanged && <p className="pricing-stale" role="status">Inputs changed. Calculate again to update the model value, Greeks, and chart.</p>}
        {error && <div role="alert" className="pricing-error">{error}</div>}
        {!result && !error && <div className="output-empty"><span>ƒ</span><h3>Set assumptions and calculate</h3><p>The result will come from the Python pricing engine.</p></div>}
        {result && <>
          <div className="primary-output"><span>{result.option_type.toUpperCase()} MODEL VALUE</span><strong>{money(result.model_price)}</strong><small>currency units per share</small></div>
          <div className="output-breakdown">
            <div><span>Intrinsic value</span><strong>{money(result.intrinsic_value)}</strong></div>
            <div><span>Time value</span><strong>{money(result.time_value)}</strong></div>
          </div>
          <p className="output-meta">T = {result.time_to_expiry_years.toFixed(6)} years · {result.model}</p>
          {submitted && <p className="submitted-inputs">Calculated from: {submitted.option_type} · S {submitted.spot} · K {submitted.strike} · {submitted.time_to_expiry} {submitted.time_unit} · σ {submitted.volatility} · r {submitted.risk_free_rate} · q {submitted.dividend_yield}</p>}
          <div className="greeks-output" aria-label="Model Greeks">
            <h3>Local sensitivities</h3>
            <div className="greeks-grid">
              <GreekMetric name="Delta" value={result.greeks.delta} unit="price / +1 spot" />
              <GreekMetric name="Gamma" value={result.greeks.gamma} unit="Delta / +1 spot" />
              <GreekMetric name="Vega" value={result.greeks.vega_per_vol_point} unit="price / +1 vol point" />
              <GreekMetric name="Theta" value={result.greeks.theta_per_day} unit="price / calendar day" />
            </div>
            <p>Per share. A volatility point is 0.01 decimal; a calendar day uses ACT/365. Other inputs stay fixed.</p>
            {result.greeks.delta === null && <p>Greeks are unavailable at expiry or effectively zero volatility, where the smooth model formulas do not apply.</p>}
          </div>
        </>}
        <div className="output-note"><strong>Theoretical value, not a market price.</strong><p>Constant volatility, rates, and dividend yield; European exercise only. Time value is model value minus spot intrinsic value and can be negative for some dividend-paying European options.</p></div>
      </div>
    </div>
    {result && result.greek_curve.length > 0 && <GreekCurve points={result.greek_curve} currentSpot={result.spot} current={result.greeks} />}
  </section>;
}

function GreekMetric({ name, value, unit }: { name: string; value: number | null; unit: string }) {
  return <div className="greek-metric"><span>{name}</span><strong>{value === null ? "Unavailable" : value.toFixed(4)}</strong><small>{unit}</small></div>;
}

function NumberField({ name, label, defaultValue, detail, min, step }: { name: string; label: string; defaultValue: string; detail: string; min?: string; step: string }) {
  return <label className="pricing-field"><span>{label}</span><input name={name} type="number" defaultValue={defaultValue} min={min} step={step} required inputMode="decimal" /><small>{detail}</small></label>;
}
