import type { Metadata } from "next";
import { Navigation } from "@/components/navigation";
import "./globals.css";

export const metadata: Metadata = {
  title: "Equity Options Analytics Dashboard",
  description: "A compact learning project for equity options and historical volatility.",
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return <html lang="en"><body>
    <div className="mx-auto max-w-6xl px-5 py-8 sm:px-8">
      <header className="mb-8">
        <p className="mb-2 text-xs font-bold tracking-widest text-cyan-800">CAPITAL MARKETS · LEARNING PROJECT</p>
        <p className="mb-6 text-2xl font-semibold tracking-tight">Equity Options Analytics Dashboard</p>
        <Navigation />
      </header>
      <main>{children}</main>
      <footer className="mt-12 border-t border-slate-200 pt-5 text-sm text-slate-600">
        Educational V1 · Assumptions and data limitations accompany each result.
      </footer>
    </div>
  </body></html>;
}
