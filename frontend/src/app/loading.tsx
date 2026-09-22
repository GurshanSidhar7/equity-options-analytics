export default function Loading() {
  return <div aria-busy="true">
    <p className="eyebrow">THE UNDERLYING, FIRST</p><h1>Overview</h1>
    <p role="status" className="page-description">Loading historical prices and analytics…</p>
    <div aria-hidden="true" className="loading-placeholder" style={{ height: 125, marginTop: 30 }} />
    <div aria-hidden="true" className="charts-grid" style={{ marginTop: 20 }}>
      <div className="loading-placeholder" style={{ height: 370 }} /><div className="loading-placeholder" style={{ height: 370 }} />
    </div>
  </div>;
}
