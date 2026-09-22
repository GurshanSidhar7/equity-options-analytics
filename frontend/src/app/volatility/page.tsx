import { redirect } from "next/navigation";

// Preserve existing bookmarks while keeping the workspace on one page.
export default async function Volatility({ searchParams }: { searchParams: Promise<{ ticker?: string }> }) {
  const { ticker } = await searchParams;
  redirect(`/${ticker ? `?ticker=${encodeURIComponent(ticker)}` : ""}#volatility`);
}
