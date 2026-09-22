"use client";

import { useEffect, useState } from "react";

const sections = [
  { id: "overview", label: "Overview", icon: "grid", number: "01" },
  { id: "option-chain", label: "Option Chain", icon: "rows", number: "02" },
  { id: "pricing-lab", label: "Pricing Lab", icon: "sliders", number: "03" },
  { id: "volatility", label: "Volatility", icon: "wave", number: "04" },
];

function NavIcon({ name }: { name: string }) {
  return <svg width="19" height="19" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" aria-hidden="true">
    {name === "grid" ? <><rect x="3" y="3" width="7" height="7" rx="1" /><rect x="14" y="3" width="7" height="7" rx="1" /><rect x="3" y="14" width="7" height="7" rx="1" /><rect x="14" y="14" width="7" height="7" rx="1" /></>
      : name === "rows" ? <><rect x="3" y="4" width="18" height="16" rx="2" /><path d="M3 10h18M3 15h18M10 4v16" /></>
      : name === "sliders" ? <><path d="M6 3v18M18 3v18M12 3v18" /><path d="M3 8h6M9 16h6M15 10h6" strokeWidth="3" /></>
      : <path d="M2 14h4l3-8 5 13 3-9 2 4h3" strokeLinecap="round" strokeLinejoin="round" />}
  </svg>;
}

export function Navigation() {
  const [active, setActive] = useState("overview");
  useEffect(() => {
    const update = () => setActive(window.location.hash.slice(1) || "overview");
    update();
    window.addEventListener("hashchange", update);
    return () => window.removeEventListener("hashchange", update);
  }, []);
  return <nav aria-label="Main navigation" className="workspace-nav">
    {sections.map(section => <a key={section.id} href={`#${section.id}`}
      aria-current={active === section.id ? "location" : undefined}
      onClick={() => setActive(section.id)} className={`nav-link ${active === section.id ? "is-active" : ""}`}>
      <NavIcon name={section.icon} /><span>{section.label}</span><span className="nav-number" aria-hidden="true">{section.number}</span>
    </a>)}
  </nav>;
}

// A server-rendered page may stream in after the browser's initial hash scroll.
// Run once the dashboard exists, including after changing the selected ticker.
export function DashboardAnchor({ ticker }: { ticker: string }) {
  useEffect(() => {
    const frame = requestAnimationFrame(() => {
      const id = window.location.hash.slice(1);
      if (id === "overview") window.scrollTo({ top: 0, behavior: "instant" });
      else if (sections.some(section => section.id === id)) document.getElementById(id)?.scrollIntoView({ behavior: "instant", block: "start" });
      window.dispatchEvent(new HashChangeEvent("hashchange"));
    });
    return () => cancelAnimationFrame(frame);
  }, [ticker]);
  return null;
}
