"use client";

import { useId, useState } from "react";
import type { ExplanationItem } from "@/lib/types";

const number = (value: number | null) => value === null ? "Unavailable" : new Intl.NumberFormat("en", { maximumFractionDigits: 6 }).format(value);

export function DeskTranslator({ items, context }: { items: ExplanationItem[]; context: string }) {
  const [math, setMath] = useState(false);
  const id = useId();
  return <section className="desk-translator context-panel" aria-label={`${context} Desk Translator`}>
    <div className="context-heading"><div><p className="panel-eyebrow">DESK TRANSLATOR · {context}</p><h2>Desk Translator</h2><p>Same analytics. Plain-English intuition.</p></div>
      <div className="explanation-toggle" role="group" aria-label={`${context} explanation mode`}>
        <button type="button" aria-pressed={!math} aria-controls={id} onClick={() => setMath(false)}>Plain English</button>
        <button type="button" aria-pressed={math} aria-controls={id} onClick={() => setMath(true)}>Show the Math</button>
      </div>
    </div>
    <div id={id} className="explanation-grid">
      {items.filter(item => math || item.id !== "sensitivity-check").map(item => <article className="explanation-card" key={item.id} data-explanation={item.id}>
        <h3>{item.title}</h3><p>{item.plain_english}</p>
        {math ? <><p className="math-expression">{item.math_expression}</p><p className="numerical-example">{item.numerical_example}</p>
          <dl className="explanation-values">{item.values.map(value => <div key={value.label}><dt>{value.label}</dt><dd>{number(value.value)} <small>{value.unit}</small></dd></div>)}</dl>
          <p className="context-note">{item.technical_note}</p></>
          : <p className="context-note">{item.why_it_matters}</p>}
      </article>)}
    </div>
  </section>;
}
