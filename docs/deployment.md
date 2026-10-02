# Vercel deployment

Production: https://equity-options-analytics-1.vercel.app

Vercel project: `equity-options-analytics-1`, linked to the existing GitHub
repository. The initial release was uploaded from the current local workspace.
The changes are not committed or pushed by deployment; future Git deployments
use the contents of the pushed commit.

Deploy from the repository root. `vercel.json` defines two services in one project:

- `frontend/`: Next.js, installed with `npm ci` and built with `npm run build`.
- `backend/`: FastAPI, entrypoint `app.main:app`, Python 3.12. Runtime dependencies
  come from `backend/pyproject.toml`; the Python function has a 60-second limit.

The public catch-all rewrite points to the frontend, including its existing
`/api/news` and `/api/pricing` route handlers. The frontend calls FastAPI through
a [service binding](https://vercel.com/docs/services/bindings) that injects
`API_BASE_URL` at runtime. Keep the backend private: it needs no public rewrite,
second domain, CORS configuration, or preview-protection bypass token.
The Overview is dynamic, so it does not request the binding during the build.

[Vercel Services](https://vercel.com/docs/services) is currently beta. The
configuration uses the current `services` model, not `experimentalServices`.

## Publish the current workspace

```sh
cd /Users/doughboy/equity-options-analytics-1
npx vercel@latest login
npx vercel@latest deploy --prod
```

Select your account/team, create or link the project, and keep the project Root
Directory at `./`. The CLI uses the services in the root configuration. Copy the
production URL printed when deployment finishes. CLI deployment uploads local
files; a GitHub commit is not required for this first deployment.

No Yahoo Finance or news key is needed. Do not add a localhost `API_BASE_URL` to
Vercel; the binding supplies it. `.vercelignore` excludes local environment files,
virtual environments, dependencies, build outputs, test fixtures, and notebooks
from CLI uploads. `.gitignore` excludes Vercel linkage/auth environment artifacts.

For deployments triggered by GitHub pushes, commit and push the current work,
import the repository at https://vercel.com/new, and keep Root Directory `./`.
The uncommitted UI and news work will not appear in a GitHub import until pushed.

## Verify the hosted app

1. Open the production URL and load AAPL, MSFT, and NVDA. Check actual prices,
   source, latest session, chart rendering, and the backend-connected indicator.
2. Calculate a call and a put in Pricing Lab. Check the model result and Greeks.
3. Check Ticker Intelligence independently; an unavailable news response should
   not block historical analytics or model pricing.
4. Check all four navigation links and a mobile-width browser.

Production checks on 2026-10-02 passed for AAPL, MSFT, and NVDA: HTTP 200,
backend connected, both historical charts, and news responses. Hosted call and put
calculations returned model values and four Greeks. All four navigation links worked
at 390 pixels wide, without horizontal overflow or browser exceptions.

The production release uses Next.js 16.3.8, with zero reported npm vulnerabilities
at installation, after applying the patch identified during the first cloud build.
The local production build, 145 backend tests, and 15 browser tests also passed.
The FastAPI health endpoint remains internal; use the dashboard's backend status
and Vercel's backend-service logs to diagnose connectivity.

## Provider and runtime behavior

Yahoo Finance's unofficial endpoints can reject or rate-limit cloud-hosted
requests even when local requests work. Inspect service logs if market data fails;
the dashboard reports unavailable data and never substitutes invented observations.
Pricing calculations do not depend on Yahoo Finance.

The news TTL cache is local to a Python process. Cold starts and separate function
instances can each fetch again. It is a best-effort cache, not shared persistence.
No database or infrastructure beyond the hosting configuration has been added.
