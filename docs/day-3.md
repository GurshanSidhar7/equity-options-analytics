# Day 3 — Dividend-adjusted European Black–Scholes

The Pricing Lab computes a theoretical European call or put value from user-supplied
assumptions. It does not fetch an option quote or compare its output with a market
price. Production mathematics lives in `backend/app/pricing/black_scholes.py`; the
research notebook independently exposes the steps for learning.

## Inputs and units

- Spot and strike: currency units per share; both must be positive.
- Time: non-negative years, or calendar days converted using ACT/365.
- Volatility: non-negative annual decimal, so `0.20` means 20%.
- Risk-free rate and continuous dividend yield: continuously compounded annual decimals.
- Exercise: European, at expiry only.

The API returns model price, spot intrinsic value, and time value per share. Spot
intrinsic value is `max(S-K, 0)` for calls and `max(K-S, 0)` for puts. Time value is
model price minus intrinsic value. It can be negative for some dividend-paying
European options because the holder cannot exercise before expiry.

## Edge cases and assumptions

At effectively zero time, model value equals expiry payoff. At effectively zero
volatility before expiry, the implementation returns the discounted deterministic
payoff. The model assumes lognormal price dynamics, constant volatility, rate, and
dividend yield, frictionless markets, and no arbitrage. Actual market prices can differ
because these assumptions are simplified and quotes reflect liquidity and supply and
demand.

## Validation

Tests cover a known numerical example, put–call parity, call/put monotonic behavior,
scalar and NumPy-vector inputs, expiry, zero volatility, invalid inputs, the HTTP API,
and the browser workflow. Greeks and implied volatility remain outside Day 3.
