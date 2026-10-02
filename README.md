# Equity Options Analytics Dashboard

A compact, learning-first project for equity-options fundamentals and capital-markets
internship recruiting. Features are implemented one user-selected sprint at a time.

**Current status: Day 4.5 — Market Explainability & Ticker Intelligence.**

- **Overview:** ticker selection, latest completed daily close, daily change, HV20/HV30,
  Historical Price and Realized Volatility charts, deterministic Desk Translator,
  and Ticker Intelligence with up to four recent relevant company-news articles.
- **Volatility:** the existing HV20/HV30 chart within the same dashboard; no IV yet.
- **Pricing Lab:** user-supplied call/put assumptions with Python-computed model,
  intrinsic, and time values, four Greeks, a selected Greek-versus-spot chart,
  and result-bound explanations with a model sensitivity comparison.
- **Option Chain:** clearly labeled as planned, without fabricated metrics.
- Day 1 option-basics notebook remains educational only.
- No implied volatility, smile, database, strategy builder,
  rankings, or backtesting is implemented.

## Run locally

Requirements: Python 3.11+ and Node.js 22.14+ with npm. From the repository root:

```sh
python3 -m venv .venv
.venv/bin/python -m pip install -c backend/requirements-dev.lock -e './backend[dev]'
.venv/bin/python -m uvicorn app.main:app --app-dir backend --reload
```

In a second terminal:

```sh
cd frontend
npm ci
npm run dev
```

Open <http://localhost:3000>. The warm editorial analytics workspace presents all four
sections on one page; the top navigation
jumps between them without losing the selected ticker. Previous section URLs redirect
to the matching dashboard anchor. Methodology and observations expand in place.
The working flow runs from Overview to Volatility to Pricing Lab; the planned Option
Chain sits last. After a successful overview load, Pricing Lab starts with the latest
completed daily close for spot and the same number as an explicitly illustrative,
editable strike. The remaining inputs are sample assumptions, not market quotes.

Submit an equity ticker such as AAPL or MSFT using
**Load overview** or Enter. The backend needs outbound HTTPS access to Yahoo Finance.
No market-data key is needed. Provider failures display an error without fake metrics.

Next.js requests FastAPI on its server; browser CORS configuration is unnecessary.
The default API address is `http://127.0.0.1:8000`. Optionally copy `.env.example` to
`frontend/.env.local` and change `API_BASE_URL`. API docs: <http://127.0.0.1:8000/docs>.

## Deploy to Vercel

The root `vercel.json` deploys the Next.js frontend and FastAPI backend together
using [Vercel Services](https://vercel.com/docs/services) (currently beta). Keep the
project's Root Directory at the repository root, not `frontend/`. The frontend
receives `API_BASE_URL` automatically through a private backend binding; no
market-data key or manually configured backend hostname is required.

From the repository root:

```sh
npx vercel@latest login
npx vercel@latest deploy --prod
```

This uploads the current local code, including uncommitted changes. Choose your
Vercel account and create/link the Equity Options Analytics project. For automatic
deployments from GitHub, commit/push the current changes first, then import the
repository into Vercel with Root Directory `./`. See the
[deployment guide](docs/deployment.md) for verification and troubleshooting.

## Ticker-news coverage

Ticker Intelligence now uses [Yahoo Finance ticker coverage](https://finance.yahoo.com/quote/NVDA/news/)
through its unofficial search endpoint; **no news API key is needed**. Alpha Vantage
has been replaced. The old `ALPHA_VANTAGE_API_KEY` is no longer read by the app.

Stories must carry an exact selected-ticker association and name the provider-resolved
company or an explicit stock symbol in the headline. Only selected publications
are included, and articles must be within the past seven days. Examples include
Yahoo Finance, Reuters, Bloomberg, Barron's, MT Newswires, and CNBC. This is an
editorial selection policy, not independent verification of article claims.
The panel explains why each headline matched. It returns fewer than four when
eligible coverage is limited, and never substitutes peer-company stories to fill it.

Successful/empty responses are cached for ten minutes, failures for one minute.
The eight-second provider timeout remains independent of historical analytics.
Yahoo's unofficial endpoint can change, fail, or rate limit; failures produce an
explicit unavailable state. Snippets are shown only when actually supplied, capped
at 600 characters. There is no full-article scraping or generated summary.

## API

- `GET /health`: application liveness only.
- `GET /api/overview?ticker=AAPL`: real historical prices and Python analytics.
- `GET /api/news?ticker=AAPL`: normalized articles, UTC retrieval/publication timestamps,
  and explicit `ok`, `empty`, `not_configured`, `unavailable`, or `rate_limited` state.
- `POST /api/pricing`: theoretical dividend-adjusted European Black–Scholes result.
  Includes per-share Delta, Gamma, Vega per 1 volatility point, Theta per calendar
  day, and a model Greek-versus-spot curve. Greeks are unavailable at expiry or
  effectively zero volatility. See [Day 4 notes](docs/day-4.md).

Spot is a **latest completed daily close proxy**, not a live quote. Today's local
exchange date is excluded conservatively. Daily price change uses provider Close;
volatility uses split/dividend-adjusted Adj Close. HV20/HV30 use 20/30 **returns**
and require 21/31 valid prices. Annualized volatility and returns are decimals in
JSON; missing values are null. Overview and Pricing responses include structured
`desk_translator` explanations and Python-calculated numerical examples. `timestamp` is UTC retrieval time; `as_of` is the
latest included session date. Full conventions: [Day 2 notes](docs/day-2.md).

## Tests

From the repository root:

```sh
.venv/bin/python -m pytest backend/tests -q
```

From `frontend`:

```sh
npm run build
npm run typecheck
npx playwright install chromium
npm run test:e2e
```

Browser tests start a test-only backend on port 8120 and the built frontend on 3120;
those ports must be free. Fixtures are synthetic **test inputs only**. The production
application never loads them. Build before running browser tests.

## Learning notebook

```sh
.venv/bin/python -m pip install -r research/requirements.txt
.venv/bin/python research/run_notebook.py
```

Or open either notebook in `research/notebooks/` and select the project's `.venv`
Python interpreter. Research is never imported by production code.

## Layout and boundaries

```text
backend/app/api/           HTTP routes and response contracts
backend/app/market_data/   Historical provider access and normalization
backend/app/volatility/    Pure returns/rolling HV and Overview composition
backend/app/pricing/       Pure European Black–Scholes analytics
backend/app/explainability/ Deterministic explanations and model scenarios
backend/app/news/          Provider adapter, normalization, selection, TTL cache
backend/tests/             Numerical, adapter, API, and browser-server fixtures
frontend/src/app/          Exactly four sections
frontend/src/components/   Ticker form, charts, navigation
frontend/src/lib/          Server API requests and display types
frontend/tests/            Browser integration checks
research/                 Educational notebook and runner
docs/                     Learning plan, assumptions, and daily notes
```

Python owns every quantitative calculation; React formats and displays results.
The analytics module has no external API calls. We do not add databases, Redis,
orchestration, portfolios, strategies, ranking, or other future-scope features.
See [project instructions](AGENTS.md), [learning plan](docs/learning-plan.md),
[Day 1](docs/day-1.md), [Day 2](docs/day-2.md), [Day 3](docs/day-3.md),
[Day 4](docs/day-4.md), and [Day 4.5](docs/day-4.5-explainability-and-news.md).
