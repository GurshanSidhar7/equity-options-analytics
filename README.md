# Equity Options Analytics Dashboard

A compact learning project for a CS student preparing for capital-markets internships.

**Current status: scaffolding only. No quantitative features are implemented.**

## What exists

- Next.js, React, TypeScript, and Tailwind setup.
- Exactly four placeholder pages: Overview, Option Chain, Pricing Lab, Volatility.
- FastAPI application wiring and a `/health` endpoint.
- Empty analytics and market-data packages, a schema placeholder, and a health smoke test.
- Dependency manifests and a day-by-day learning plan.

There are no calculations, market/demo data, charts, feature endpoints, or feature tests.
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
<http://127.0.0.1:8000/health>. The placeholder frontend runs independently of the backend.
No environment variables or market-data account are needed yet.

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

These checks verify application scaffolding, not quantitative features.

## Structure

```text
backend/
  app/
    main.py          FastAPI entry point
    routes.py        Health endpoint only
    schemas.py       Placeholder for future contracts
    analytics/       Empty Python package
    market_data/     Empty Python package
  tests/test_api.py  Health smoke test only
  pyproject.toml
  requirements-dev.lock
frontend/
  src/
    app/             Four placeholder pages and shared layout
    components/      Navigation and placeholder component
    lib/             Empty; future API access and display types
  package.json
  package-lock.json
docs/
  learning-plan.md
  assumptions.md
```

## Learning workflow

Follow [the learning plan](docs/learning-plan.md). Days are learning units, not deadlines.
Select one day at a time. Before a quantitative feature is coded, explain what it
measures, why it exists, inputs/outputs, mathematics, one numerical example, and
validation. Then wait for understanding/approval unless that day's task explicitly
asks to build. Never implement later days in advance.

All quant calculations belong in Python. Provider code stays separate from analytics.
Notebooks, if introduced, are for learning only. The frontend only presents API results.
See [documentation conventions](docs/assumptions.md).

V1 excludes databases, Redis, Docker orchestration, backtesting, ranking, 3D surfaces,
strategy builders, portfolio Greeks, and P&L attribution.
