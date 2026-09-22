# Project working agreement

This is a learning-first Equity Options Analytics Dashboard. The user wants
implementation structured into learning days. Day 1 covered the application skeleton
and option-basics notebook. Day 2 covered historical data, returns, realized volatility,
and the Overview. Day 3 covers dividend-adjusted European Black–Scholes pricing and
the Pricing Lab. Greeks and implied volatility remain unimplemented.

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
