# Documentation conventions for future features

No model, estimator, or data convention has been implemented yet. Choose and document
these during the corresponding learning day rather than treating them as settled now.

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

Decisions to discuss later include the price-adjustment basis, return convention,
sampling frequency, volatility estimator and annualization, option day count,
Greek scaling, exercise-style limitations, quote timestamps, ATM selection, and
IV convergence/failure handling. None is implemented by this scaffold.
