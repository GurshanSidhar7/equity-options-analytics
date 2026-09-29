# Day-by-day learning plan

**Current stage: Day 4 Greeks. Later sprints remain pending.**

Each day is a learning unit; take more than one calendar day if needed. Do not move
on automatically or write later-day implementations in advance.

## Working agreement for every quantitative day

1. Explain what the feature measures.
2. Explain why it exists and where it fits in the four sections.
3. Define inputs, outputs, and units.
4. Explain the mathematical relationship using a reliable source.
5. Work through one numerical example.
6. Explain how to validate the result and handle edge cases.
7. Wait for your confirmation of understanding before implementation, unless your
   current request explicitly asks to build that day's feature.

After approval, build the feature in Python, add meaningful tests, document assumptions,
and connect the API/UI where applicable. Finish with files changed, tests run,
limitations, and five comprehension questions. A request to explain, plan, or scaffold
is not permission to implement calculations.

## Day 1 — Options fundamentals and application skeleton

Learn calls, puts, long/short, strike, expiry, premium, payoff versus profit,
intrinsic/time value, and moneyness. Work through one call and put example.

Preserve the four frontend sections and backend wiring. Keep API, pricing,
volatility, market-data, and test packages separate. Connect Overview to `/health`.
Run `research/notebooks/01_option_basics.ipynb` for educational payoff/profit experiments.
**No production finance calculations.** See [Day 1 notes](day-1.md) for commands,
assumptions, and the five questions to answer before Day 2.

## Day 2 — Returns and realized volatility

The user combined historical returns and realized volatility into this sprint.
Learn simple/log returns, sample standard deviation, rolling windows, and sqrt(252)
annualization. Build the historical-data adapter, pure Python analytics, HV20/HV30,
Overview API, ticker selection, and price/realized-volatility charts. Missing data
must remain unavailable. See [Day 2 notes](day-2.md).

## Day 3 — European option pricing

Learn call/put payoffs, spot, strike, expiry, rates, volatility, and continuous dividend
yield. Explain dividend-adjusted Black–Scholes and European exercise assumptions.
After confirmation, implement pricing and validation and connect Pricing Lab.

## Day 4 — Greeks

Explain Delta, Gamma, Vega, and Theta separately using the six-part learning format.
Agree on units and scaling before implementing each. Validate sensitivities and display
them in Pricing Lab. Rho remains optional. See [Day 4 notes](day-4.md).

## Day 5 — Real option-chain data and quote quality

Choose an accessible provider together and discuss source limitations. Implement
provider access separately from normalization and analytics. Define bid, ask, last,
timestamps, missing fields, and quality flags; present actual quotes in Option Chain.
Explain any derived quote measure before implementing it.

## Day 6 — Implied-volatility estimation

Learn IV as an inverse pricing problem. Explain Newton–Raphson, convergence, price
bounds, and failure cases. After confirmation, implement the solver and tests. Add a
simple fallback only if demonstrated necessary, explaining and documenting it first.
Use eligible quotes and expose failures and exercise-style limitations clearly.

## Day 7 — ATM IV and the volatility smile

Agree on the ATM definition, expiry grouping, quote eligibility, and units. Explain
and implement each approved measure, then show ATM IV and IV versus strike in
Volatility. No 3D surface or additional strategy features.

## Day 8 — V1 review and recruiting explanation

Verify the four sections, assumptions, tests, setup instructions, and data/model
limitations. Practice explaining the project and its tradeoffs. Write resume claims
only for completed and validated work. Add no new features.
