# Day 4.5 — Market Explainability & Ticker Intelligence

## 1. Purpose

Desk Translator expresses the same verified analytics in Plain English or Show the
Math. It bridges technical derivatives analysis and readers who need intuition,
units, and worked examples. Ticker Intelligence adds recent company context without
predicting direction or treating headlines as causes. This sprint was explicitly
approved outside the original sequence; Days 5–7 remain unimplemented.

## 2. Architecture

```text
Ticker → historical market-data provider → Python analytics → Overview result
                                                            ↓
                                                     Desk Translator
Submitted assumptions → Python Black–Scholes / Greeks → Pricing result
                                                            ↓
                                                     Desk Translator

Ticker → news provider → typed provider-independent candidates → normalization
       → ticker relevance filtering → UTC sorting → deduplication
       → up to four recent articles → Ticker Intelligence
```

The systems meet only in presentation. News never modifies model assumptions or
outputs. FastAPI adds typed `desk_translator` contracts to Overview and Pricing.
`explainability/` consumes existing outputs; only the sensitivity check invokes the
existing pricing function again. It does not duplicate Black–Scholes or Greeks.
`news/provider.py` handles I/O and Yahoo Finance parsing; `news/service.py` owns
selection, normalized public articles, and caching. `GET /api/news?ticker=...` is
independent of Overview. The browser calls a same-origin Next.js proxy, which calls
FastAPI. It never calls the external news provider directly. The current adapter requires no key.

The frontend has shared types and reusable components. It formats Python numbers
without calculating financial scenarios. Accessible mode buttons expose
`aria-pressed`; article links use semantic anchors and safe new-window attributes.
There are still exactly Overview, Volatility, Pricing Lab, and Option Chain.

## 3. Desk Translator: measurements, units, and examples

Inputs are the latest verified Overview result or the exact submitted pricing
request plus its Black–Scholes and Greek outputs. Outputs contain prose, purpose,
math, a worked example, technical notes, and labelled numerical values/units.
Missing measurements produce an explanation rather than invented numbers.

- **Latest close / daily change:** a completed daily Close, not a live quote.
  Change is `P_t − P_previous`; decimal simple return is `change / P_previous`.
  For 138 → 139, change is 1 currency unit and return is about 0.7246%.
  These use provider Close; adjusted Close is used for HV.
- **HV20 / HV30:** historical sample standard deviation (`ddof=1`) of the last
  20/30 adjusted daily log returns, times `sqrt(252)`. Returns are
  `ln(P_t/P_previous)`. Windows require 21/31 valid prices. They measure past
  variability, not IV or future movement. Annual decimals 0.24 and 0.20 become
  24% and 20%; their absolute difference is 4 percentage points. Python reports
  above/below/equal using exact comparisons, with no approximate-equality band.
- **Spot and strike:** `(S − K)/K × 100` is a percentage relationship, calculated
  in Python. Spot 103.2 and strike 100 gives 3.2% above. A call has positive spot
  intrinsic value there; a put has zero. No exchange-specific ATM threshold.
- **Model / intrinsic / time values:** currency units per option share. Intrinsic
  is `max(S−K,0)` for a call or `max(K−S,0)` for a put. Model time value is
  `model value − spot intrinsic`; it can be negative for dividend-paying European
  options. A payoff-at-current-spot example does not permit early European exercise.
- **Delta:** local model-price slope per +1 currency unit of spot:
  `ΔV ≈ Delta × ΔS`. It is not an expiry probability.
- **Gamma:** change in Delta per +1 spot unit:
  `Delta_new ≈ Delta + Gamma × ΔS`. Gamma can itself change afterward.
- **Vega:** price sensitivity per **one volatility percentage point**, meaning
  +0.01 decimal volatility. It describes 20% → 21%, not 20% → 120%.
- **Theta:** model-price change per calendar day elapsed, using ACT/365.
  It can be positive or negative. With less than a day remaining, the example
  is still a local tangent estimate, not a finite repricing past expiry.

Known example: `S=K=100, T=1, σ=0.20, r=0.05, q=0.02`, European call.
Model price ≈ 9.227006, intrinsic 0, model time value ≈ 9.227006.
Delta ≈ 0.586851; Gamma ≈ 0.018951. A +1 spot move locally estimates price change
+0.586851 and Delta ≈ 0.605802. Vega ≈ 0.379012 means a 20% → 21% scenario locally
estimates +0.379012 per share. Theta ≈ −0.013943 means a one-day tangent estimate
of −0.013943 per share. All other model inputs remain fixed.

Show the Math also includes **Model Sensitivity Check**: Delta-only,
`Delta × 1 + 0.5 × Gamma × 1²`, and `V(S+1) − V(S)` from the existing model.
The second derivative accounts for curvature and can improve a finite-move
approximation; improvement is not guaranteed for every input set. This is a
model sensitivity demonstration, not trading P&L. At `T ≤ 1e−12` or `σ ≤ 1e−12`,
smooth Greeks and their scenarios are unavailable; the existing model price remains.

Editing Pricing Lab inputs retains the old result and its exact explanation until
successful recalculation, following the existing stale-result indicator.

## 4. Ticker Intelligence

The user requested replacement of Alpha Vantage after seeing NVDA-tagged stories
whose headlines focused on Fortinet, Cisco, HPE, and Honeywell/Ecolab. Provider
association is useful evidence but does not establish that a story focuses on the
selected company. The earlier 0.20 relevance threshold was insufficient for this use.

The current adapter uses [Yahoo Finance ticker coverage](https://finance.yahoo.com/quote/NVDA/news/)
via `query1.finance.yahoo.com/v1/finance/search`. This is an **unofficial** endpoint,
like the existing historical-data adapter. It requests the exact symbol with fuzzy
matching disabled, one quote for issuer-name resolution, and up to 50 news entries.
There is no API-key requirement; the previous Alpha Vantage key is unused.
[Finnhub company news](https://finnhub.io/docs/api/company-news) was also evaluated:
its documented symbol-specific endpoint requires a separate key and covers North
American companies. Yahoo was chosen for an immediately usable, keyless integration,
with the explicit availability limitations below.

The adapter verifies an exact quote-symbol match and an equity/ETF instrument,
uses short/long issuer names supplied by that quote, and trims legal/share-class
suffixes. It rejects fuzzy matches instead of attaching another issuer's coverage.
Article association comes only from `relatedTickers`; publication epochs become UTC.
No invented company aliases, classifications, sentiment, sources, or summaries.

The service requires **all** of the following:

1. Explicit selected-ticker association.
2. The provider-resolved company name in the headline, matched with word boundaries,
   or an explicit stock-symbol form such as `$NVDA`, `(NVDA)`, or `NASDAQ: NVDA`.
   A mention only in the summary is insufficient; ordinary words such as CAT are
   not interpreted as symbols. It does not guess aliases such as Google for Alphabet.
3. A selected publication: Yahoo Finance, Reuters, Associated Press/AP, AFP,
   Bloomberg, CNBC, Financial Times, The Wall Street Journal/WSJ, Barron's/Barrons.com,
   MarketWatch, MT Newswires, Investor's Business Daily, BBC/BBC News, Fortune, or Quartz.
   Matching is case-insensitive. This is a project editorial policy, not a fact-check.
4. An aware, nonfuture publication timestamp within the **past seven days**.
5. A nonempty headline/source and a valid HTTP(S) article URL.

Eligible stories are normalized to UTC, sorted newest first, and deduplicated by
URL, normalized headline, and optional provider ID. URL identity ignores fragments
and common tracking parameters while preserving other query parameters. At most
four stories are returned; fewer results are preferable to unrelated padding.
`match_reason` explains the headline match and `selection_note` exposes the policy.

Provider snippets remain optional and capped at 600 characters. Yahoo's current
search entries commonly omit summaries, topics, and sentiment, so those fields are
left empty rather than generated. The provider-independent contracts still support
these optional fields. Generic topic context remains deterministic when supplied.
No full article bodies are fetched. Each card links to its publisher's supplied URL,
which may lead to Yahoo's syndicated copy or a paywall.

The process-local cache holds up to 128 tickers: **600 seconds** for successful/empty
responses, **60 seconds** for failure states. Retrieval time is preserved in cached
responses; workers have independent caches and simultaneous misses may duplicate
requests. External I/O never holds the shared cache lock. No database or Redis.
The provider uses an **eight-second HTTP timeout**, and the browser fetches news
independently of historical analytics. HTTP, timeout, connection, and malformed
response failures produce clean states; abandoned browser requests are cancelled.

`GET /api/news` returns ticker, retrieval time, provider, status, message, cache TTL,
selection note, and typed articles. Operational states return HTTP 200; invalid
ticker syntax returns 422. `not_configured` remains in the provider-independent
contract for future key-based adapters, but Yahoo does not require credentials.

## 5. Financial guardrails

News context is separate from Black–Scholes and realized-volatility inputs.
A headline and a close movement do not establish causality. Provider sentiment
is automated text context, not a direction forecast. Latest completed close is
not live; realized volatility is historical; user-entered volatility is not IV.
Model price is theoretical, not an observed quote or a valuation recommendation.
Greek scenarios are local approximations with other inputs fixed, not guarantees
of realized market-price changes. No arbitrage claim follows from a model output.

## 6. Limitations and validation

Coverage and availability depend on Yahoo's unofficial endpoint. A response can
contain at most 50 candidate stories; four means the newest eligible stories among
that batch, not comprehensive reporting. Strict filtering can return fewer than four
or none, even for a widely covered company. The publication list excludes some
useful reporting, and issuer-name matching can miss alternate company names. Names
such as Apple still depend on provider metadata to distinguish company references.
Headline/URL deduplication cannot detect every syndicated rewrite. Source claims
are not independently fact-checked; publication selection reduces a known source of
irrelevant/speculative coverage without guaranteeing truth. Mixed-company headlines
can pass when they directly name the selected issuer. Provider timestamps and
metadata may be incorrect. News is retrieved on demand, not streamed live. Summaries
are omitted when unavailable, and original source reading may require a subscription.

Validation compares structured explanation numbers to the existing model outputs,
checks sign handling, missing values, units, and nonsmooth boundaries. News tests
mock HTTP/provider responses, UTC ordering, relevance, deduplication, errors, and
TTL expiry. Browser tests use synthetic test-only providers/interception and verify
ticker changes, stale-input behavior, keyboard controls, independent failure/loading,
four article cards, safe links, and mobile layouts. No regular test uses live news.

Completed validation after the provider/UI refresh: **145 backend tests**, **15
Chromium browser tests**, production build, TypeScript, and diff checks passed.
Live ticker-provider responses and desktop/mobile layouts were also inspected.

## 7. Comprehension questions

1. Why are ticker metadata and a direct company headline both required?
2. Why normalize provider responses before selecting articles?
3. How do HV20 and implied volatility differ?
4. Why is Delta a local sensitivity, and how does Gamma refine an approximation?
5. Why does a headline near a price movement not establish causality?
6. What does one Vega point mean here, and what stays fixed?
7. Why use deterministic templates, and why bind them to the submitted result?
