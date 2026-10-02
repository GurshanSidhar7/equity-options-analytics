# Warm editorial analytics workspace

The user approved a full visual refresh using the supplied **Cedar Brand identity**
document and **Style B Colour Scheme** image. These are visual references, not
instructions to turn the dashboard into Cedar's organizational-network product.
The project name and financial-research purpose remain Equity Options Analytics.

## Visual system

- Warm parchment canvas `#F4EFE6`, quiet ivory surfaces `#FBF8F2`, charcoal `#292520`.
- Instrument Serif for page and section headings; Inter for controls, labels, body,
  and tabular data. Fonts are self-hosted from Google's font repository, with their
  SIL Open Font License files in `frontend/public/fonts/`.
- Sage `#9AA68F` for subtle structure, with darker `#4B5D49` for accessible data lines.
- Terracotta `#C96F4A` as the reference accent; darker clay `#A64B30` for readable
  actions and links on the light surface. Ochre chart line `#90661F` distinguishes HV30.
- Thin warm-grey borders, 5–10px radii, generous whitespace, flat surfaces, and no
  neon glow, decorative gradients, or heavy shadows.
- Quiet navigation, clear headline metrics, paper-like charts, publication-style
  news headlines, and structured explanations. Colour is not a price-direction signal.

The stylesheet defines one coherent light theme rather than appending overrides to
the old dark palette. Historical chart colours, tick labels, grids, and hover labels
use the new palette, as does the Greek-versus-spot chart. The user's sticky historical
table header behavior is preserved. Navigation sits in a sticky horizontal header to give the workspace its full screen
width, with small responsive outer gutters. The Overview uses one main panel: ticker
identity, headline metrics, and source context sit above a large Historical Price
chart. A shorter full-width Realized Volatility chart and supporting reading panels
follow below. The page heading is compact to keep the data prominent.

On mobile, navigation stays sticky and charts,
news, explanations, and pricing stack without horizontal overflow.

## Product behavior

Exactly four primary navigation targets remain: Overview, Volatility, Pricing Lab,
and Option Chain. Navigation retains the ticker; legacy routes still redirect to
anchors. Overview contains the existing prices/returns/HV, Ticker Intelligence,
and Desk Translator. Pricing Lab retains its inputs, backend model outputs, Greeks,
chart, submitted-result explanations, and stale-input indicator. Option Chain is
still explicitly planned. IV and future learning days remain unimplemented.

News now uses Yahoo Finance's unofficial ticker search endpoint. Provider ticker
metadata, issuer-name headline matching, selected publications, and a seven-day
cutoff jointly determine eligibility. The panel displays a reason for each match.
Publication selection does not independently verify article claims. News failure
remains independent of historical analytics and model pricing.

Keyboard controls, visible focus, semantic links, reduced motion, null values,
missing-data states, source/timestamps, and chart-alternative observations remain.
Tests use synthetic providers; production never uses test stories or prices.

## Validation

145 backend tests and 15 Chromium browser tests pass, along with production build,
TypeScript, and diff checks. Live NVDA/AAPL/MSFT provider checks returned direct
issuer headlines. The live NVDA dashboard was inspected from 320 to 1920 pixels wide, with no
browser exceptions or horizontal overflow; chart SVG widths matched their containers. Publication claims
were not independently verified. The local app remains available on port 3000.
