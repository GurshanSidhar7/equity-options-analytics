import { expect, test } from "@playwright/test";
import type { Overview } from "../src/lib/types";

const overviewTranslator = (page: import("@playwright/test").Page) => page.getByRole("region", { name: "Overview Desk Translator" });

test("ticker intelligence shows four recent source articles and survives ticker changes", async ({ page }) => {
  await page.goto("/");
  const news = page.getByRole("region", { name: "Ticker Intelligence for AAPL" });
  await expect(news.getByRole("article")).toHaveCount(4);
  await expect(news).toContainText("Yahoo Finance");
  await expect(news).toContainText("Company named in headline");
  await expect(news).toContainText("AAPL named in headline");
  await expect(news.locator("time").first()).toHaveAttribute("datetime", "2026-10-01T15:00:00Z");
  await expect(news.locator("time").first()).toContainText("01 Oct 2026");
  const link = news.getByRole("link", { name: "Read article: AAPL synthetic test coverage 1", exact: true });
  await expect(link).toHaveAttribute("href", "https://example.com/AAPL/test/0");
  await expect(link).toHaveAttribute("target", "_blank");
  await expect(link).toHaveAttribute("rel", "noopener noreferrer");
  await expect(news.getByRole("article").nth(1).locator(".news-summary")).toHaveCount(0);
  await expect(news).toContainText("does not establish what caused a price movement");
  await page.getByLabel("Equity ticker", { exact: true }).fill("MSFT");
  await page.getByRole("button", { name: "Load overview" }).click();
  await expect(page.getByRole("region", { name: "Ticker Intelligence for MSFT" }).getByRole("article")).toHaveCount(4);
  await expect(page.getByRole("region", { name: "Ticker Intelligence for AAPL" })).toHaveCount(0);
  await expect(page.getByRole("navigation").getByRole("link")).toHaveCount(4);
});

for (const status of ["not_configured", "unavailable", "rate_limited", "empty"] as const) {
  test(`news ${status} does not block historical analytics`, async ({ page }) => {
    const messages = {
      not_configured: "Ticker news is not configured for this environment.",
      unavailable: "Recent ticker news is temporarily unavailable.",
      rate_limited: "The news provider's request limit was reached. Please try again later.",
      empty: "No recent ticker-specific articles were returned.",
    };
    await page.route("**/api/news?*", route => route.fulfill({ json: { ticker: "AAPL", status, message: messages[status], articles: [] } }));
    await page.goto("/");
    await expect(page.getByRole("region", { name: "Ticker Intelligence for AAPL" })).toContainText(messages[status]);
    await expect(page.getByRole("heading", { name: "AAPL · Historical overview" })).toBeVisible();
    await expect(page.locator(".js-plotly-plot")).toHaveCount(2);
    await expect(overviewTranslator(page)).toBeVisible();
  });
}

test("HTTP news failure is graceful and loading is independent", async ({ page }) => {
  let release: (() => void) | undefined;
  const gate = new Promise<void>(resolve => { release = resolve; });
  await page.route("**/api/news?*", async route => { await gate; await route.fulfill({ status: 503, json: { detail: "Provider failure" } }); });
  await page.goto("/");
  const news = page.getByRole("region", { name: "Ticker Intelligence for AAPL" });
  await expect(news).toContainText("Loading recent ticker news");
  await expect(page.getByText("139.00", { exact: true }).first()).toBeVisible();
  await expect(overviewTranslator(page)).toBeVisible();
  release?.();
  await expect(news).toContainText("Recent ticker news is temporarily unavailable");
  await expect(news.getByRole("article")).toHaveCount(0);
});

test("Overview translator uses fixture analytics and keyboard-accessible math controls", async ({ page }) => {
  await page.goto("/?ticker=MSFT");
  const translator = overviewTranslator(page);
  await expect(translator.getByRole("button", { name: "Plain English", exact: true })).toHaveAttribute("aria-pressed", "true");
  await expect(translator.locator('[data-explanation="latest-close"]')).toContainText("MSFT");
  await expect(translator.locator(".math-expression")).toHaveCount(0);
  const math = translator.getByRole("button", { name: "Show the Math", exact: true });
  await math.focus();
  await page.keyboard.press("Enter");
  await expect(math).toHaveAttribute("aria-pressed", "true");
  await expect(translator.locator('[data-explanation="hv20"]')).toContainText("sqrt(252)");
  await expect(translator.locator('[data-explanation="hv30"]')).toContainText("last 30 log returns");
  await expect(translator.locator('[data-explanation="daily-change"]')).toContainText("276.0000");
  // Capture the same backend response the server page uses, rather than calculate HV in JS.
  const fixture: Overview = await (await page.request.get("http://127.0.0.1:8120/api/overview?ticker=MSFT")).json();
  await expect(translator.locator('[data-explanation="hv20"]')).toContainText(fixture.desk_translator!.items.find(row => row.id === "hv20")!.numerical_example);
  await expect(translator.locator('[data-explanation="hv30"]')).toContainText(fixture.desk_translator!.items.find(row => row.id === "hv30")!.numerical_example);
  await translator.getByRole("button", { name: "Plain English", exact: true }).click();
  await expect(translator.locator(".math-expression")).toHaveCount(0);
});

test("Pricing translator matches submitted values through edits and recalculation", async ({ page }) => {
  await page.goto("/#pricing-lab");
  const lab = page.locator("#pricing-lab");
  await lab.getByRole("spinbutton", { name: "Spot (S)" }).fill("100");
  await lab.getByRole("spinbutton", { name: "Strike (K)" }).fill("100");
  await lab.getByRole("spinbutton", { name: /^Time to expiry/ }).fill("1");
  await lab.getByRole("combobox", { name: /^Time unit/ }).selectOption("years");
  await lab.getByRole("button", { name: "Calculate model value" }).click();
  const translator = lab.getByRole("region", { name: "Pricing Lab Desk Translator" });
  await expect(translator).toBeVisible();
  await expect(translator.locator('[data-explanation="delta"]')).toContainText("0.586851 currency units increase");
  const original = await translator.innerText();
  await lab.getByRole("spinbutton", { name: "Spot (S)" }).fill("101");
  await lab.getByRole("spinbutton", { name: "Volatility (σ)" }).fill("0.4");
  await expect(lab).toContainText("Inputs changed. Calculate again");
  expect(await translator.innerText()).toBe(original);
  await translator.getByRole("button", { name: "Show the Math" }).click();
  await expect(translator.locator('[data-explanation="delta"]')).toContainText("0.586851 × 1");
  await expect(translator.locator('[data-explanation="vega"]')).toContainText("20.00% to 21.00%");
  await expect(translator.getByRole("heading", { name: "Model Sensitivity Check" })).toBeVisible();
  await lab.getByRole("button", { name: "Calculate model value" }).click();
  await expect(translator.locator('[data-explanation="vega"]')).toContainText("40.00% to 41.00%");
  await expect(translator.locator('[data-explanation="spot-strike"]')).toContainText("1.00% above");
});

test("both context features and Pricing explanations fit a mobile screen", async ({ page }, testInfo) => {
  await page.setViewportSize({ width: 390, height: 844 });
  await page.goto("/");
  const news = page.getByRole("region", { name: "Ticker Intelligence for AAPL" });
  await expect(news.getByRole("article")).toHaveCount(4);
  await news.scrollIntoViewIfNeeded();
  await news.screenshot({ path: testInfo.outputPath("ticker-intelligence-mobile.png") });
  const overview = overviewTranslator(page);
  await overview.getByRole("button", { name: "Show the Math" }).click();
  await expect.poll(() => page.evaluate(() => document.documentElement.scrollWidth <= innerWidth)).toBe(true);
  const cards = await news.getByRole("article").evaluateAll(nodes => nodes.map(node => node.getBoundingClientRect().left));
  expect(new Set(cards).size).toBe(1);
  const lab = page.locator("#pricing-lab");
  await lab.getByRole("button", { name: "Calculate model value" }).click();
  const pricing = lab.getByRole("region", { name: "Pricing Lab Desk Translator" });
  await pricing.getByRole("button", { name: "Show the Math" }).click();
  await expect(pricing.getByRole("heading", { name: "Model Sensitivity Check" })).toBeVisible();
  await expect.poll(() => page.evaluate(() => document.documentElement.scrollWidth <= innerWidth)).toBe(true);
  await pricing.screenshot({ path: testInfo.outputPath("desk-translator-mobile.png") });
});
