# Project working agreement

This is a learning-first Equity Options Analytics Dashboard. The user wants
implementation structured into learning days. Day 1 covered the application skeleton
and option-basics notebook. Day 2 covered historical data, returns, realized volatility,
and the Overview. Day 3 covered dividend-adjusted European Black–Scholes pricing and
the Pricing Lab. Day 4 covers Delta, Gamma, Vega, Theta, and a selected
Greek-versus-spot chart. Implied volatility remains unimplemented.

- Follow docs/learning-plan.md, one user-selected day at a time.
- Do not interpret scaffolding, planning, or explanation requests as authorization
  to implement features. Do not implement future days in advance.
- Before each quantitative feature, explain measurement, purpose, inputs/outputs,
  mathematics, one numerical example, and validation. Wait for understanding unless
  the current task explicitly asks to build that feature.
- Quantitative calculations belong only in Python; separate market-data providers
  from analytics. Production code must not import research notebooks.
- Keep exactly four sections: Overview, Option Chain, Pricing Lab, Volatility.
- Limit V1 to the user's returns/realized volatility, dividend-adjusted European
  Black–Scholes, Greeks, Newton–Raphson IV, real chain normalization, ATM IV,
  IV-versus-strike smile, and basic data-quality scope.
- Keep units and assumptions explicit and distinguish market/model prices and
  realized/implied volatility. Never make valuation or arbitrage claims from a
  model-price difference.
- Do not add databases, Redis, orchestration, backtesting, ranking, 3D surfaces,
  strategies, portfolio Greeks, or P&L attribution.

## Explicitly approved bounded sprint: Day 4.5

The user approved **Day 4.5 — Market Explainability & Ticker Intelligence** outside
of the original day sequence. This authorizes deterministic Desk Translator
explanations in Overview/Pricing Lab, recent ticker-news retrieval in Overview,
and conservative deterministic explanations of provider topic categories.
Python owns scenarios and model repricing; news remains separate from analytics.
No LLM, fabricated news, causal price claims, or fifth navigation section.

This does not authorize Day 5 real option chains, Day 6 implied volatility,
Day 7 smile, trading strategies, portfolio analytics, or backtesting.

The user subsequently approved a full UI refresh using the Cedar identity and Style B
references, and replacement of the news provider. Use a warm, light editorial design
with Instrument Serif/Inter and restrained natural accents. Current news uses Yahoo
Finance with exact ticker metadata, direct headline matching, selected publications,
and a seven-day age cutoff. This does not expand quantitative scope or navigation.
