# Documentation conventions for future features

Day 2 implements the historical-data and realized-volatility conventions in
[Day 2 notes](day-2.md). Day 3 implements pricing conventions in
[Day 3 notes](day-3.md). Day 4 implements Greek conventions in
[Day 4 notes](day-4.md). IV conventions remain future decisions.

For each feature, record:

- What it measures and why it belongs in V1.
- Inputs, outputs, units, and a reliable mathematical reference.
- One worked numerical example and meaningful validation cases.
- Edge cases, assumptions, and limitations shown in the UI when applicable.

Project rules:

- Rates, dividend yields, and volatility are decimals; option time is in years.
- Distinguish observed market prices from theoretical model prices.
- Distinguish realized volatility from implied volatility.
- Never label a model-price difference as mispricing, undervaluation, overvaluation,
  or arbitrage.
- Quant calculations live only in Python. Data providers remain separate.

Remaining decisions include option-quote timestamps, ATM selection, and IV
convergence/failure handling. No IV calculations are implemented.

## Day 1 notebook only

The notebook uses hypothetical USD-per-share premiums, holds isolated call/put
positions until expiry, and ignores fees, financing, taxes, dividends, and early
exercise. A 100-share multiplier is an explicit example assumption. Payoff excludes
the premium; long profit subtracts it, short profit receives it and owes the long
payoff. These are educational expiry outcomes, not pre-expiry model prices or
market observations. Production code does not import the notebook.
