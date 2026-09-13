import "server-only";

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
