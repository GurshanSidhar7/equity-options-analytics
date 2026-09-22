# Unified analytics workspace

The UI refresh presents the existing analytics as one cohesive page. It does not
change the financial calculations, provider, or API contract.

- Four navigation targets remain: Overview, Option Chain, Pricing Lab, Volatility.
- Navigation uses in-page anchors and retains the ticker query parameter.
- Old section URLs redirect to the corresponding anchor, preserving the ticker.
- Historical Price and Realized Volatility share a coordinated chart style.
- The Volatility section presents existing realized volatility only. IV is not built.
- Option Chain and Pricing Lab are explicit planned sections. They contain no
  invented quotes, model prices, controls, or quantitative results.
- Latest session, retrieval time, currency, and historical-price basis stay visible.
- Source, methodology, and the historical table remain accessible on the same page.
- Null values still display as Unavailable, and provider errors replace prior metrics.

The dark graphite workspace uses layered panels, a cyan/violet heading accent,
prominent tabular figures, and luminous cyan/violet chart lines. Dark mode is the
default throughout, including form controls, chart tooltips, tables, errors, and
loading states. Existing data remains unaltered; chart lines are not smoothed. Mobile
navigation moves above the dashboard, metric cards use two columns, and charts stack.

Accessibility includes native links, labeled inputs, a keyboard skip link, focus
indicators, reduced-motion support, a chart-alternative data table, and explicit
planned/unavailable states. Charts retain provider data and gaps without smoothing.

Browser checks cover ticker refreshes, both chart renders, desktop-to-mobile resizing,
missing metrics, provider errors, four in-page anchors, and legacy URL redirection.

The production build and five browser integration checks pass. Real-data AAPL/MSFT
checks cover ticker updates and charts; desktop and mobile screenshots were inspected.
