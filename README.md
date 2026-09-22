# Equity Options Analytics Dashboard

A compact, learning-first project for equity-options fundamentals and capital-markets
internship recruiting. Features are implemented one user-selected sprint at a time.

**Current status: Day 3 — dividend-adjusted European Black–Scholes Pricing Lab.**

- **Overview:** ticker selection, latest completed daily close, daily change, HV20/HV30,
  Historical Price and Realized Volatility charts, explicit data limitations.
- **Volatility:** the existing HV20/HV30 chart within the same dashboard; no IV yet.
- **Pricing Lab:** user-supplied call/put assumptions with Python-computed model,
  intrinsic, and time values.
- **Option Chain:** clearly labeled as planned, without fabricated metrics.
- Day 1 option-basics notebook remains educational only.
- No Greeks, implied volatility, smile, database, strategy builder,
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

Open <http://localhost:3000>. The dark analytics workspace presents all four
sections on one page; the navigation rail
jumps between them without losing the selected ticker. Previous section URLs redirect
to the matching dashboard anchor. Methodology and observations expand in place.

Submit an equity ticker such as AAPL or MSFT using
**Load overview** or Enter. The backend needs outbound HTTPS access to Yahoo Finance.
No market-data key is needed. Provider failures display an error without fake metrics.

Next.js requests FastAPI on its server; browser CORS configuration is unnecessary.
The default API address is `http://127.0.0.1:8000`. Optionally copy `.env.example` to
`frontend/.env.local` and change `API_BASE_URL`. API docs: <http://127.0.0.1:8000/docs>.

## API

- `GET /health`: application liveness only.
- `GET /api/overview?ticker=AAPL`: real historical prices and Python analytics.
- `POST /api/pricing`: theoretical dividend-adjusted European Black–Scholes result.

Spot is a **latest completed daily close proxy**, not a live quote. Today's local
exchange date is excluded conservatively. Daily price change uses provider Close;
volatility uses split/dividend-adjusted Adj Close. HV20/HV30 use 20/30 **returns**
and require 21/31 valid prices. Annualized volatility and returns are decimals in
JSON; missing values are null. `timestamp` is UTC retrieval time; `as_of` is the
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
[Day 1](docs/day-1.md), [Day 2](docs/day-2.md), and [Day 3](docs/day-3.md).
