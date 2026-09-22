"use client";

import { useRouter } from "next/navigation";
import { useTransition } from "react";

export function TickerForm({ ticker }: { ticker: string }) {
  const router = useRouter();
  const [pending, startTransition] = useTransition();
  return <form aria-label="Choose underlying" className="ticker-form" onSubmit={(event) => {
    event.preventDefault();
    const value = String(new FormData(event.currentTarget).get("ticker") ?? "").trim().toUpperCase();
    startTransition(() => {
      if (value === ticker) router.refresh();
      else router.push(`/?ticker=${encodeURIComponent(value)}#overview`);
    });
  }}>
    <div><label htmlFor="ticker" className="ticker-label">Equity ticker</label>
      <div className="ticker-input-wrap"><svg width="15" height="15" viewBox="0 0 20 20" fill="none" stroke="currentColor" strokeWidth="1.5" aria-hidden="true"><circle cx="8" cy="8" r="5"/><path d="m12 12 5 5"/></svg><input key={ticker} id="ticker" name="ticker" defaultValue={ticker} required maxLength={20}
        pattern="[A-Za-z0-9][A-Za-z0-9.\-]{0,19}" autoCapitalize="characters" spellCheck={false}
        className="ticker-input" /></div></div>
    <button disabled={pending} className="ticker-submit">
      {pending ? "Loading…" : "Load overview"}<span aria-hidden="true">↗</span>
    </button>
    {pending && <p role="status" className="ticker-pending">Fetching the selected ticker. Displayed results retain their ticker label until the request finishes.</p>}
  </form>;
}
