"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

const sections = [["/", "Overview"], ["/option-chain", "Option Chain"],
  ["/pricing-lab", "Pricing Lab"], ["/volatility", "Volatility"]];

export function Navigation() {
  const pathname = usePathname();
  return <nav aria-label="Main navigation" className="flex flex-wrap gap-2 border-b border-slate-200 pb-4">
    {sections.map(([href, label]) => <Link key={href} href={href}
      aria-current={pathname === href ? "page" : undefined}
      className={`rounded-lg px-4 py-2 text-sm font-medium transition-colors ${pathname === href ? "bg-slate-900 text-white" : "text-slate-600 hover:bg-slate-100"}`}>
      {label}
    </Link>)}
  </nav>;
}
