# Financial methodology

## Financial period before arithmetic

Queries specify start, end, form (10-K or 10-Q), filing cutoff and normalized tax rate. Annual durations must be 330–400 days; quarters 60–110 days. The selector first locates eligible exact-period revenue, chooses the latest eligible accession and requires matching accession, filing date, end, duration and unit for each reported fact. Amendments are eligible only after their filing date. Conflicting same-context values remain unavailable. Instant balance facts have no start date. Eligibility uses day-level filing dates, not intraday availability.

Comparatives come from the selected filing, preserving its restated historical context. They are not the originally published values from every historical vintage. Fiscal intervals must be comparable, supporting 52/53-week calendars. Quarterly QoQ uses an adjacent eligible quarter with its own disclosed evidence. Quarterly cash-flow derivation subtracts preceding YTD from current YTD only with matching fiscal start, compatible units/tags and the preceding end immediately before the requested quarter. Both source observations remain visible; missing or conflicting evidence prevents derivation.

## Calculations

| Measure | Definition / eligibility |
|---|---|
| Growth | Current / prior − 1; prior must be positive |
| Revenue CAGR | (Latest / earliest)^(1 / fiscal year count) − 1; annual, positive endpoints |
| Margins | Gross profit, operating income or net income / revenue |
| EBIT | Reported operating income proxy |
| EBITDA proxy | Operating income + reported D&A; check source scope |
| CFO less capex | Operating cash flow − payments for property, plant and equipment |
| Cash conversion | CFO / net income; positive denominator |
| Working capital | Current assets − current liabilities |
| Current ratio | Current assets / current liabilities |
| Reported long-term debt | Current portion of long-term debt + noncurrent long-term debt |
| Debt | Reported long-term debt + explicitly reported ShortTermBorrowings |
| Net debt | Debt − cash and equivalents |
| Interest coverage | Operating income / interest expense |
| ROA / ROE | Annual net income / average opening and closing assets or equity |
| ROIC | Normalized NOPAT / average opening and closing (debt + equity − cash) |

NOPAT taxes positive operating income at the analyst's 0–60% assumed rate and does not assume a cash refund on losses. Annual return ratios require aligned opening balances; quarter flows are never silently annualized. Missing short-term borrowings does **not** mean zero: debt, net debt, leverage and ROIC are unavailable without explicit coverage. The long-term-debt proxy may still be shown. Leases, minority interests, excess cash and issuer-specific debt classification require review.

Ratios with missing inputs, nonpositive denominators or nonfinite arithmetic are unavailable. Nonfinite and excessively large source inputs are rejected. Every raw magnitude is interpreted in the reported unit; the display formats USD amounts compactly and converts rate fractions to percentages.

## Accounting connections

Assets − liabilities − equity is a consistency residual, not proof of a complete or audited reconstruction. The cash bridge requires the same cash-plus-restricted-cash scope at opening and closing and every CFO, CFI, CFF and FX component. Missing FX never becomes zero. CFO − net income aggregates working-capital/noncash adjustments without inventing their components. Change in retained earnings − net income includes unexplained dividends and other movements; it is not an inferred dividend value.

## Provenance

Each selected observation records tag, unit, dates, accession, form and basis. Derived quarters retain two source observations. Analysis includes a canonical normalized-input SHA-256 and calculation timestamp. An export also retains available provider metadata (raw-byte SHA-256, source URL and retrieval timestamp). Reimported metadata is labeled supplied/unverified. Hashes support reproducibility, not authenticity; analyst uploads are never authenticated by their asserted labels. The live retrieval marker applies to that session's fixed-host provider response, not to an independently audited statement.
