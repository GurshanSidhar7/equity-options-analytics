# Equity Options Analytics Dashboard

A compact learning project for a CS student preparing for capital-markets internships.

**Current status: Day 1 application skeleton and educational notebook. No production quantitative features are implemented.**

## What exists

- Next.js, React, TypeScript, and Tailwind setup.
- Exactly four placeholder pages: Overview, Option Chain, Pricing Lab, Volatility.
- FastAPI `/health` endpoint, checked by the Next.js server and displayed in Overview.
- Empty pricing, volatility, and market-data packages, API wiring, and a health smoke test.
- An educational option-basics notebook with worked examples and assertions.
- Dependency manifests and a day-by-day learning plan.

There are no production calculations, market/demo data, charts, or analytics endpoints.
Payoff and profit experiments exist only in the research notebook.
Plotly and TanStack dependencies are reserved for later lessons. NumPy is installed
for later analytics; pandas and SciPy will be added when needed.

## Run the scaffold

Requirements: Python 3.11+ and Node.js 22.14+ with npm.

From the repository root:

```sh
python3 -m venv .venv
.venv/bin/python -m pip install -c backend/requirements-dev.lock -e './backend[dev]'
.venv/bin/python -m uvicorn app.main:app --app-dir backend --reload
```

In another terminal:

```sh
cd frontend
npm ci
npm run dev
```

Open <http://localhost:3000>. Backend health is at
<http://127.0.0.1:8000/health>. Overview shows **Backend connected** when Next.js receives
HTTP 200 with `{"status":"ok"}`. Connection errors, unexpected responses, or a three-second
timeout show **Backend unavailable**. The four sections remain accessible.

Next.js fetches the health endpoint on its server; no browser CORS configuration is
needed. The default backend address is `http://127.0.0.1:8000`. Optionally copy
`.env.example` to `frontend/.env.local` and set `API_BASE_URL` to change it.
This is application liveness only, not market-feed health. No market-data account is needed.

## Check the scaffold

```sh
cd backend
../.venv/bin/python -m pytest
```

```sh
cd frontend
npm run build
npm run typecheck
```

These checks verify application scaffolding, not production quantitative features.

## Run the Day 1 learning notebook

From the repository root:

```sh
.venv/bin/python -m pip install -r research/requirements.txt
.venv/bin/python research/run_notebook.py
```

The runner validates the notebook and executes all code cells in a fresh Python
kernel, including the assertions. It leaves source outputs empty for clean diffs.
For interactive experiments, open `research/notebooks/01_option_basics.ipynb` in
your notebook editor and select this project's `.venv` Python interpreter.
Notebook dependencies are separate from production dependencies.

## Structure

```text
backend/
  app/
    main.py          FastAPI entry point
    api/             Health route and future schema placeholder
    pricing/         Empty pricing package
    volatility/      Empty volatility package
    market_data/     Empty provider package
  tests/test_api.py  Health smoke test only
  pyproject.toml
  requirements-dev.lock
frontend/
  src/
    app/             Four placeholder pages and shared layout
    components/      Navigation and placeholder component
    lib/api.ts       Server-side backend health request
  package.json
  package-lock.json
research/
  notebooks/01_option_basics.ipynb
  run_notebook.py
  requirements.txt
docs/
  learning-plan.md
  day-1.md
  assumptions.md
```

## Learning workflow

Follow [the learning plan](docs/learning-plan.md). Days are learning units, not deadlines.
Select one day at a time. Before a quantitative feature is coded, explain what it
measures, why it exists, inputs/outputs, mathematics, one numerical example, and
validation. Then wait for understanding/approval unless that day's task explicitly
asks to build. Never implement later days in advance.

All quant calculations belong in Python. Provider code stays separate from analytics.
Research notebooks are for learning only and are never imported by production code. The frontend only presents API results.
See [documentation conventions](docs/assumptions.md).

V1 excludes databases, Redis, Docker orchestration, backtesting, ranking, 3D surfaces,
strategy builders, portfolio Greeks, and P&L attribution.
