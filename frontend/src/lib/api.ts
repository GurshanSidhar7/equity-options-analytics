import "server-only";
import type { Overview } from "./types";

export async function getOverview(ticker: string): Promise<{ data: Overview | null; error: string | null }> {
  const baseUrl = process.env.API_BASE_URL ?? "http://127.0.0.1:8000";
  try {
    const response = await fetch(`${baseUrl.replace(/\/$/, "")}/api/overview?ticker=${encodeURIComponent(ticker)}`, {
      cache: "no-store", signal: AbortSignal.timeout(20000),
    });
    if (!response.ok) {
      const body = await response.json();
      return { data: null, error: typeof body.detail === "string" ? body.detail : "Enter a valid equity ticker, such as AAPL or MSFT." };
    }
    return { data: await response.json(), error: null };
  } catch {
    return { data: null, error: "Overview is unavailable. Check the backend connection and try again." };
  }
}

export type BackendHealth = "connected" | "unavailable";

export async function getBackendHealth(): Promise<BackendHealth> {
  const baseUrl = process.env.API_BASE_URL ?? "http://127.0.0.1:8000";
  try {
    const response = await fetch(`${baseUrl.replace(/\/$/, "")}/health`, {
      cache: "no-store",
      signal: AbortSignal.timeout(3000),
    });
    if (!response.ok) return "unavailable";
    const body: unknown = await response.json();
    return body !== null && typeof body === "object" && "status" in body && body.status === "ok"
      ? "connected"
      : "unavailable";
  } catch {
    return "unavailable";
  }
}
