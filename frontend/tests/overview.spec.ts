import { expect, test } from "@playwright/test";

test("ticker selection replaces metrics and renders both charts", async ({ page }, testInfo) => {
  const errors: string[] = [];
  page.on("pageerror", error => errors.push(error.message));
  await page.goto("/");
  await expect(page.getByRole("heading", { name: "AAPL · Historical overview" })).toBeVisible();
  await expect(page.getByText("139.00", { exact: true }).first()).toBeVisible();
  await expect(page.locator(".js-plotly-plot")).toHaveCount(2);
  await page.getByLabel("Equity ticker", { exact: true }).fill("msft");
  await page.getByRole("button", { name: "Load overview" }).click();
  await expect(page.getByRole("heading", { name: "MSFT · Historical overview" })).toBeVisible();
  await expect(page.getByText("278.00", { exact: true }).first()).toBeVisible();
  await expect(page.getByRole("heading", { name: "AAPL · Historical overview" })).toHaveCount(0);
  await expect(page.locator(".js-plotly-plot .scatterlayer .trace")).toHaveCount(3);
  await page.evaluate(() => window.scrollTo({ top: 0, behavior: "instant" }));
  await page.screenshot({ path: testInfo.outputPath("desktop-overview.png"), fullPage: true });
  await page.setViewportSize({ width: 390, height: 844 });
  await expect.poll(() => page.evaluate(() => document.documentElement.scrollWidth <= innerWidth)).toBe(true);
  await expect.poll(() => page.locator(".js-plotly-plot").evaluateAll(plots => plots.every(plot => {
    const svg = plot.querySelector("svg.main-svg");
    return svg !== null && svg.getBoundingClientRect().width <= plot.clientWidth + 1;
  }))).toBe(true);
  await page.evaluate(() => window.scrollTo({ top: 0, behavior: "instant" }));
  await page.screenshot({ path: testInfo.outputPath("mobile-overview.png"), fullPage: true });
  expect(errors).toEqual([]);
});

test("all four sections share one page and preserve the selected ticker", async ({ page }) => {
  await page.goto("/?ticker=MSFT");
  for (const [name, id] of [["Overview", "overview"], ["Option Chain", "option-chain"], ["Pricing Lab", "pricing-lab"], ["Volatility", "volatility"]]) {
    const link = page.getByRole("navigation").getByRole("link", { name, exact: true });
    await link.click();
    await expect(page).toHaveURL(`http://127.0.0.1:3120/?ticker=MSFT#${id}`);
    await expect(page.locator(`#${id}`)).toBeInViewport();
    await expect(link).toHaveAttribute("aria-current", "location");
  }
  await expect(page.locator("#option-chain")).toContainText("Planned · not built");
  await expect(page.locator("#pricing-lab")).toContainText("European · Black–Scholes");
  await page.getByText("Methodology & data limitations", { exact: true }).click();
  await expect(page.getByText(/HV20 needs 21 valid closes/)).toBeVisible();
});

test("Pricing Lab calculates call and put values through the Python API", async ({ page }) => {
  await page.goto("/#pricing-lab");
  const lab = page.locator("#pricing-lab");
  await lab.getByRole("button", { name: "Calculate model value" }).click();
  await expect(lab.getByText("CALL MODEL VALUE")).toBeVisible();
  await expect(lab.getByText("2.4056", { exact: true }).first()).toBeVisible();
  await lab.getByText("Put", { exact: true }).click();
  await lab.getByRole("button", { name: "Calculate model value" }).click();
  await expect(lab.getByText("PUT MODEL VALUE")).toBeVisible();
  await expect(lab.getByText("2.1598", { exact: true }).first()).toBeVisible();
  await expect(lab).toContainText("Theoretical value, not a market price.");
});

test("previous section URLs redirect into the unified dashboard", async ({ page }) => {
  await page.goto("/pricing-lab?ticker=MSFT");
  await expect(page).toHaveURL("http://127.0.0.1:3120/?ticker=MSFT#pricing-lab");
  await expect(page.getByRole("heading", { name: "MSFT · Historical overview" })).toBeVisible();
  await expect(page.locator("#pricing-lab")).toBeInViewport();
});

test("insufficient history and provider errors never display invented metrics", async ({ page }) => {
  await page.goto("/?ticker=SHORT");
  const hv30 = page.locator("section").filter({ has: page.getByRole("heading", { name: "HV30", exact: true }) });
  await expect(hv30.getByText("Unavailable", { exact: true })).toBeVisible();
  await page.getByLabel("Equity ticker", { exact: true }).fill("BAD");
  await page.getByRole("button", { name: "Load overview" }).click();
  await expect(page.getByRole("alert").filter({ hasText: "Overview unavailable" })).toContainText("Provider unavailable");
  await expect(page.getByRole("heading", { name: "HV20", exact: true })).toHaveCount(0);
  await expect(page.locator(".js-plotly-plot")).toHaveCount(0);
});

test("latest gaps show unavailable cards and mobile charts fit", async ({ page }) => {
  await page.setViewportSize({ width: 390, height: 844 });
  await page.goto("/?ticker=GAP");
  const spot = page.locator("section").filter({ has: page.getByRole("heading", { name: "Spot · last daily close", exact: true }) });
  await expect(spot.getByText("Unavailable", { exact: true })).toBeVisible();
  await expect(page.locator(".js-plotly-plot")).toHaveCount(2);
  await expect.poll(() => page.evaluate(() => document.documentElement.scrollWidth <= innerWidth)).toBe(true);
  await expect(page.getByRole("navigation").getByRole("link")).toHaveCount(4);
});
