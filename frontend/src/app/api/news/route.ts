import { NextRequest, NextResponse } from "next/server";

export async function GET(request: NextRequest) {
  const ticker = request.nextUrl.searchParams.get("ticker") ?? "";
  if (!/^[A-Za-z0-9][A-Za-z0-9.\-]{0,19}$/.test(ticker)) {
    return NextResponse.json({ detail: "Enter a valid equity ticker." }, { status: 422 });
  }
  const baseUrl = process.env.API_BASE_URL ?? "http://127.0.0.1:8000";
  try {
    const response = await fetch(`${baseUrl.replace(/\/$/, "")}/api/news?ticker=${encodeURIComponent(ticker)}`, {
      cache: "no-store", signal: AbortSignal.timeout(12000),
    });
    return NextResponse.json(await response.json(), { status: response.status });
  } catch {
    return NextResponse.json({ detail: "Recent ticker news is temporarily unavailable." }, { status: 503 });
  }
}
