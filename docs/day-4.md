# Day 4 — Greeks

The Pricing Lab now reports local sensitivities of its **theoretical**, per-share,
dividend-adjusted European Black–Scholes price. It does not estimate sensitivities
from observed option prices. The selected volatility is a user assumption, not IV.
The [Options Industry Council](https://www.optionseducation.org/advancedconcepts/volatility-the-greeks)
describes the interpretation of Greeks; the formulas below follow by differentiating
the [Day 3](day-3.md) price with respect to one input at a time.

Let `S` be spot, `K` strike, `T` years to expiry, `σ` decimal annual volatility,
`r` the continuously compounded annual risk-free rate, and `q` the continuous
annual dividend yield. Define `d1 = [ln(S/K) + (r-q+σ²/2)T] / (σ√T)` and
`d2 = d1 - σ√T`. `N` and `φ` denote the standard-normal CDF and PDF.

| Greek | What it measures | Call | Put | Display unit |
| --- | --- | --- | --- | --- |
| Delta | `∂V/∂S` | `e^(-qT) N(d1)` | `-e^(-qT) N(-d1)` | Model-price change per +1 currency unit of spot |
| Gamma | `∂²V/∂S²` | `e^(-qT) φ(d1)/(Sσ√T)` | Same | Delta change per +1 currency unit of spot |
| Vega | `∂V/∂σ` | `S e^(-qT) φ(d1)√T` | Same | Model-price change per +1 volatility percentage point (`0.01` decimal), so formula × `0.01` |
| Theta | `-∂V/∂T` | `-Se^(-qT)φ(d1)σ/(2√T) - rKe^(-rT)N(d2) + qSe^(-qT)N(d1)` | `-Se^(-qT)φ(d1)σ/(2√T) + rKe^(-rT)N(-d2) - qSe^(-qT)N(-d1)` | Model-price change per calendar day elapsed, so annual formula ÷ `365` |

All price changes are currency units **per share**. Rho is the rate sensitivity
`∂V/∂r`; it is introduced in the notebook but is not a dashboard output. A one
percentage-point rate change would use `0.01 × Rho`.

Calls normally have positive Delta, puts negative Delta; Gamma and Vega are positive
for both. Theta is often negative, but rate/dividend terms can reverse its sign.
Far in/out of the money, Delta approaches its discounted spot limit/zero. Gamma
is often greatest around the strike and becomes sharper near expiry. Vega is often
largest around the strike and with more time remaining. Near-the-money Theta can
also become more pronounced near expiry. These patterns depend on the inputs.

With `S=K=100`, `T=1`, `σ=0.20`, `r=0.05`, `q=0.02`, the call model price is
`9.227006`. Delta `0.586851` predicts about `+0.586851` for a small `+1` spot
move; Gamma `0.018951` predicts Delta itself rises about `0.018951`. Vega
`0.379012` predicts about `+0.379012` for a change from 20% to 21% volatility.
Theta `-0.013943` predicts about `-0.013943` after one calendar day with the
other inputs fixed. Repricing gives the actual *model* changes; the notebook
compares them and shows the approximation error for larger changes.

Validation uses central finite differences of the existing Black–Scholes price
for calls and puts across different spots, maturities, volatility, rates, and
dividend yields. Put–call Delta parity, Gamma/Vega equality, boundary behavior,
and the API/UI are also checked. At expiry or effectively zero volatility, the
dashboard reports all Greeks as unavailable because the smooth formulas are
undefined or unstable near a kink. These derivatives are local estimates, not
predictions of market quotes: real spot, time, rates, dividends, and volatility
can change together. The spot chart varies only `S`, keeping the other submitted
inputs fixed.

To practice, answer these without code:

1. A call has Delta `0.55`. What model-price change does a small `+$0.20` spot move suggest?
2. Gamma is `0.03`. How does a `+$1` spot move locally affect Delta, and why might the original Delta estimate become inaccurate for a `+$10` move?
3. Displayed Vega is `0.40`. What does a change from 20% to 21% volatility suggest, and what is held fixed?
4. Displayed Theta is `-0.02`. What does one calendar day suggest under the model, and why could actual market price differ?
5. Why are Greeks unavailable at expiry or zero volatility in this dashboard?
