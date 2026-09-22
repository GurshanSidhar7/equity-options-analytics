# Day 2 — Returns and realized volatility

## Learning notes

Returns compare proportional moves across price levels: a $1 change on a $10 stock
is different from a $1 change on a $200 stock. Simple return is `P[t]/P[t-1] - 1`;
log return is `ln(P[t]/P[t-1])`. Simple returns compound multiplicatively through
`1 + return`; log returns add across periods. For small movements they are close.

Sample standard deviation measures dispersion about the mean, using denominator
`n - 1`. A rolling window discards the oldest return and includes the newest, with
no future information. HV20 uses 20 returns/21 prices; HV30 uses 30 returns/31 prices.
These are trading-session observation windows, not calendar-day windows.

```text
r[t] = ln(P[t]) - ln(P[t-1])
mean = sum(last n returns) / n
sample_variance = sum((return - mean)^2) / (n - 1)
annualized_realized_volatility = sqrt(sample_variance) * sqrt(252)
```

Variance adds for uncorrelated daily returns with stable variance. Standard deviation
is the square root of variance, hence sqrt(252) annualization. It does not guarantee
future volatility, a price range, or normal returns. HV is historical, not implied.

### Worked example

Prices `100 -> 101 -> 100` yield simple returns `0.01` and `-0.00990099`;
log returns are approximately `0.00995033` and `-0.00995033`. Mean log return is zero.
Sample variance is `(0.00995033^2 + (-0.00995033)^2) / (2 - 1) = 0.000198018`.
Daily standard deviation is about `0.0140719`; multiplying by sqrt(252) gives
`0.223384`, displayed as **22.34%**. This two-return teaching example is too short
for either production window and must not be presented as HV20/HV30.

## Inputs, outputs, and price conventions

- The pure analytics module is `backend/app/volatility/realized_vol.py`, preserving
  the existing `backend/app` package layout. It never calls the network.
- Input: a sequence of daily positive adjusted closes; NaN denotes missing data.
- Output: aligned daily log returns and annualized rolling-volatility arrays.
  First return, leading windows, and windows touching missing returns are NaN.
- The API converts unavailable values to JSON `null`, and the UI displays
  **Unavailable**. A true constant-price window produces numerical zero, not null.
- Returns and volatility are decimals, e.g. 0.20 means 20%. `daily_change_pct`
  is also a decimal simple return. Frontend formatting is not a second calculation.
- Daily change is latest provider close minus the preceding provider close; its
  percentage is that difference divided by the preceding close.

## Data source and limitations

`market_data/history.py` fetches one year of daily equity/ETF history from Yahoo
Finance's unofficial chart endpoint. There is no provider key, database, cache,
generated data, or production fallback. The endpoint may fail or rate limit.
Do not assume its availability, adjustments, or accuracy are guaranteed.

The provider supplies `Close` (split-adjusted, not dividend-adjusted) and `Adj Close`
(split/dividend-adjusted). Historical Price, spot proxy, and daily change use Close;
HV uses Adj Close. Historical adjusted prices can change after corporate actions.
Missing adjusted closes are never replaced with ordinary closes. Dividend effects
can appear in daily price change; this is not a total-return metric.

**Spot is explicitly a historical proxy:** the latest returned completed daily close,
not an intraday quote. To avoid partial bars, today's exchange-local date is excluded
even after the market closes. This conservative convention intentionally waits until
the next local day to include that session. `as_of` is the latest included session
date; `timestamp` is retrieval time in UTC, not quote time or an invented close time.

Dates are sorted; duplicates and malformed shapes are rejected. Missing/nonpositive/
nonfinite price fields become null gaps without dropping their rows. Missing sessions
not returned by the provider cannot be detected without an exchange calendar; this
limitation is always visible. No interpolation or filling is used. Currency comes
from the provider and is never assumed; quoted minor-unit codes are retained as-is.
An older-than-four-calendar-day last session gets a stale-data warning; this is a
simple warning threshold, not exchange-calendar validation.

## API and UI

`GET /api/overview?ticker=AAPL` returns ticker, provider currency/source, timestamp,
as_of, spot, daily_change, daily_change_pct, hv20, hv30, units, assumptions, and
history rows with date, close, adjusted_close, log_return, hv20, and hv30.

Provider failures return an error (404 for unavailable symbol/history, 503 for
network/service/rate-limit failures, 502 for malformed data). Invalid ticker syntax
or unsupported instrument types return 422. Failed ticker requests remove the prior
metrics; no substitute numbers are shown. Submit a ticker with **Load overview** or
Enter to refresh the server-rendered results. Pending results retain their ticker label.
Both charts use Python outputs; historical values are also available in a table.

## Validation

- Constant-price windows return zero after exactly 21/31 observations.
- Hand-calculated sample and independent `statistics.stdev` references.
- Rolling-window alignment, price-scale invariance, annualization scaling, and no lookahead.
- Missing-price contamination and recovery; insufficient samples stay unavailable.
- Adapter normalization, incomplete current-day exclusion, invalid fields, and HTTP failures.
- API units, daily change, missing latest metrics, ticker errors, and provider failure.
- Browser checks cover ticker replacement, both charts, null metrics, errors, and mobile layout.
  Browser tests use a test-only provider, never a fallback in the production application.

## Five questions before Day 3

Completed validation: **51 backend tests** and **3 browser integration tests** passed;
the production build and TypeScript checks passed. A live AAPL-to-MSFT browser
check also passed using the production provider, with 251 completed sessions for
each ticker and latest session 2026-09-15. Test servers were shut down afterward.
The Python test stack emits two upstream deprecation warnings; these do not fail tests.

1. Why are simple and log returns different, and why do log returns add across time?
2. Why does HV20 need 21 prices, and which observation leaves the window tomorrow?
3. Why divide sample variance by n-1 and multiply daily standard deviation by sqrt(252)?
4. Why use adjusted closes for HV, and why is the spot card not a live quote?
5. How do missing data and insufficient history differ from a genuine zero-volatility result?

Sources: [pandas rolling sample standard deviation](https://pandas.pydata.org/pandas-docs/version/2.3/reference/api/pandas.core.window.rolling.Rolling.std.html),
[Nasdaq annualization convention](https://indexes.nasdaqomx.com/docs/FactSheet_Qgreen.pdf),
[yfinance's Yahoo chart integration](https://github.com/ranaroussi/yfinance/blob/main/yfinance/scrapers/history.py).
