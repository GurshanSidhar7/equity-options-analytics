# Day-by-day learning plan

**Current stage: scaffold only. All feature work below is pending.**

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

## Day 1 — Understand the scaffold and project boundaries

Walk through Python versus TypeScript responsibilities, the four sections, data flow,
and how to start both applications. Understand `/health` and run the scaffold checks.
**No finance calculations.**

## Day 2 — Historical prices and log returns

Learn price adjustment and proportional changes. Agree on input dates and quality
rules. After confirmation, implement returns, tests, an API contract, and an Overview
presentation using a clearly labeled learning fixture.

## Day 3 — Realized volatility

Learn historical return dispersion, the estimator, sample size, and annualization.
After confirmation, implement and test realized volatility and display its assumptions
in Overview. Explain why it differs from implied volatility.

## Day 4 — European option pricing

Learn call/put payoffs, spot, strike, expiry, rates, volatility, and continuous dividend
yield. Explain dividend-adjusted Black–Scholes and European exercise assumptions.
After confirmation, implement pricing and validation and connect Pricing Lab.

## Day 5 — Greeks

Explain Delta, Gamma, Vega, and Theta separately using the six-part learning format.
Agree on units and scaling before implementing each. Validate sensitivities and display
them in Pricing Lab. Rho remains optional.

## Day 6 — Real option-chain data and quote quality

Choose an accessible provider together and discuss source limitations. Implement
provider access separately from normalization and analytics. Define bid, ask, last,
timestamps, missing fields, and quality flags; present actual quotes in Option Chain.
Explain any derived quote measure before implementing it.

## Day 7 — Implied-volatility estimation

Learn IV as an inverse pricing problem. Explain Newton–Raphson, convergence, price
bounds, and failure cases. After confirmation, implement the solver and tests. Add a
simple fallback only if demonstrated necessary, explaining and documenting it first.
Use eligible quotes and expose failures and exercise-style limitations clearly.

## Day 8 — ATM IV and the volatility smile

Agree on the ATM definition, expiry grouping, quote eligibility, and units. Explain
and implement each approved measure, then show ATM IV and IV versus strike in
Volatility. No 3D surface or additional strategy features.

## Day 9 — V1 review and recruiting explanation

Verify the four sections, assumptions, tests, setup instructions, and data/model
limitations. Practice explaining the project and its tradeoffs. Write resume claims
only for completed and validated work. Add no new features.
