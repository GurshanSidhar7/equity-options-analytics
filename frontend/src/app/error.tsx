"use client";
export default function ErrorPage({ reset }: { reset: () => void }) {
  return <div role="alert" className="error-panel">
    <p className="eyebrow">CONNECTION INTERRUPTED</p>
    <h1>The workspace could not be displayed</h1>
    <p>Please try again. No substitute data will be shown.</p>
    <button onClick={reset} className="ticker-submit" style={{ marginTop: 18 }}>Try again <span aria-hidden="true">↗</span></button>
  </div>;
}
