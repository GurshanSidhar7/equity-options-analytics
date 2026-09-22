import type { Metadata } from "next";
import { Navigation } from "@/components/navigation";
import "./globals.css";

export const metadata: Metadata = {
  title: "Equity Options | Analytics Workspace",
  description: "A focused research workspace for historical equity prices and realized volatility.",
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return <html lang="en" data-theme="dark"><body>
    <a href="#main-content" className="skip-link">Skip to dashboard</a>
    <aside className="sidebar">
      <a href="#overview" className="brand" aria-label="Equity Options overview">
        <span className="brand-mark" aria-hidden="true"><svg viewBox="0 0 32 32" fill="none"><path d="M7 23V9h18M7 16h13M7 23h18" stroke="currentColor" strokeWidth="2" /><circle cx="24" cy="16" r="2" fill="currentColor" /></svg></span>
        <span>Equity Options<span className="brand-caption">ANALYTICS WORKSPACE</span></span>
      </a>
      <p className="nav-caption">WORKSPACE</p>
      <Navigation />
      <div className="sidebar-note"><span className="sidebar-note-rule" /><p>Understand the underlying.</p><p>Make the assumptions visible.</p></div>
      <div className="sidebar-footer"><span className="version-square">V1</span><div>Research edition<span>Learning, built into the process.</span></div></div>
    </aside>
    <div className="workspace-body">
      <header className="topbar"><div className="breadcrumb">Workspace <span>/</span> <strong>Equity analytics</strong></div><span className="topbar-tag"><span className="status-dot" /> Historical data</span></header>
      <main tabIndex={-1} id="main-content" className="main-content">{children}</main>
      <footer className="page-footer"><span>Equity Options Analytics</span><span>Historical observations. Explicit assumptions.</span></footer>
    </div>
  </body></html>;
}
