# Day 1 — Options fundamentals and application skeleton

Scope: preserve the scaffold, organize packages, connect the health endpoint, and
run the option-basics notebook. No production option analytics are implemented.

## Learning recap

A call gives its buyer the right to buy at the strike; a put gives the right to sell.
Long means buying and paying a premium. Short means selling to open, receiving a
premium, and accepting an obligation on assignment. Expiry ends the contract;
exercise timing depends on American versus European style.

At expiry, long-call payoff is `max(stock - strike, 0)` and long-put payoff is
`max(strike - stock, 0)`. Long profit subtracts the premium. Short profit is premium
received minus the corresponding long payoff. Fees and financing are excluded here.

For example, a $100-strike call bought for $5 has a $12 payoff and $7 profit per
share when stock expires at $112. A $100-strike put bought for $4 has a $10 payoff
and $6 profit when stock expires at $90. With an assumed 100-share multiplier,
profits are $700 and $600. These are hypothetical inputs, not market observations.

Intrinsic value uses the same positive difference with today's stock price. Time
value is premium minus intrinsic value. A call is ITM above its strike; a put is
ITM below it. ATM means equal in these examples (often near in practice); the opposite
side is OTM. Moneyness ignores the premium: an ITM option can still lose money.

The notebook includes the full explanation, boundary checks, and experiments.
Long-option loss is limited to premium in these examples; an uncovered short call
can lose without a finite upper bound as stock rises. None of this models early exercise.

Sources: [SEC options introduction](https://www.investor.gov/introduction-investing/general-resources/news-alerts/alerts-bulletins/investor-bulletins-63),
[OIC options pricing](https://prd-web.optionseducation.org/optionsoverview/options-pricing),
[CME moneyness](https://www.cmegroup.com/education/courses/introduction-to-options/calculating-options-moneyness-and-intrinsic-value).

## Application boundaries

- `backend/app/api`: routes and future request/response schemas. Only `/health` exists.
- `backend/app/pricing`: empty package for later pricing lessons.
- `backend/app/volatility`: empty package for later volatility lessons.
- `backend/app/market_data`: existing empty provider package.
- `backend/tests`: health smoke test, with a package marker.
- `frontend/src/lib/api.ts`: Next.js server fetches `/health`; there are no quant formulas.
- `research/notebooks`: educational calculations only; production never imports them.

The original empty `analytics` package was replaced by the requested `pricing` and
`volatility` packages. Existing routes and schemas moved into `api`; the health route
and four-section navigation were reused.

## Commands and manual verification

See the README for installation and startup. From the repository root:

```sh
.venv/bin/python -m pytest backend/tests
.venv/bin/python research/run_notebook.py
```

From `frontend`:

```sh
npm run build
npm run typecheck
```

Run backend and frontend in separate terminals. Open Overview and confirm **Backend
connected**, then visit all four tabs. Stop the backend and refresh Overview: it
should say **Backend unavailable**. Restart it and click **Check again** to recover.
This checks liveness and connectivity only, not finance logic or a market-data feed.

## Completed validation

- Backend health smoke test: 1 passed (two upstream dependency deprecation warnings).
- Next.js production build and TypeScript check: passed.
- Notebook: all 6 code cells executed in a fresh kernel, including every assertion.
- Browser smoke check with local backend/frontend: all four tabs rendered and navigated.
- Health display: connected, unavailable after shutdown, and connected again after restart.
- Mobile viewport: navigation visible, no horizontal page overflow or browser runtime errors.
- Production source review: no notebook imports or finance calculations.

The browser check used temporary ports 8110 and 3110 and shut down its test servers
after completion. The default development ports remain 8000 and 3000.

## Five questions before Day 2

1. What rights does a long call or put provide, and what obligation does its short seller accept?
2. For a $100-strike call bought for $5, what are payoff, profit, and moneyness if the stock expires at $103?
3. For a $100-strike put bought for $4, what are expiry breakeven and maximum loss for the buyer?
4. If a call's premium is $5 and its intrinsic value is $3, what is its time value, and what happens to time value at expiry?
5. How does the frontend reach `/health`, and why must notebook calculations stay outside production imports?
