import { NextRequest, NextResponse } from "next/server";

export async function POST(request: NextRequest) {
  const baseUrl = process.env.API_BASE_URL ?? "http://127.0.0.1:8000";
  try {
    const response = await fetch(`${baseUrl.replace(/\/$/, "")}/api/pricing`, {
      method: "POST",
      headers: { "content-type": "application/json" },
      body: await request.text(),
      cache: "no-store",
      signal: AbortSignal.timeout(5000),
    });
    const body = await response.json();
    return NextResponse.json(body, { status: response.status });
  } catch {
    return NextResponse.json({ detail: "Pricing service is unavailable. Check the backend connection." }, { status: 503 });
  }
}
