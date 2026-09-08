# LedgerLens financial specification

Thesis: financial statements describe connected economic activity. Revenue growth is insufficient evidence of financial strength unless profitability, liquidity, capital efficiency and cash conversion support it.

Finance lead owns GAAP statement interpretation, debt/liquidity/profitability ratios and caveats. Quant lead owns growth durations and comparison validity. Data lead owns bounded SEC companyfacts ingestion, filing cutoffs, units and accession provenance. Engineering lead owns pure typed modules and stateless FastAPI. UI lead owns an evidence-first local workbench with actual imports and graphical statement connections. Release lead owns incremental tests, reproducible locks, CI, repository hygiene and remote verification. An independent project reviewer is assigned by the portfolio orchestrator; no child agents are spawned.

## Architecture and choices

Use a Python package with typed Pydantic inputs, pure domain modules, FastAPI API and bundled HTML/CSS/JavaScript workbench. No database is needed for stateless financial research. Download SEC companyfacts only from the fixed official host with an identifying User-Agent; require the user to supply the contact string, enforce bounded response/time/rate and never substitute demo data on failure. Offline JSON import works without network or credentials. A deterministic fictional issuer is clearly labeled DEMO DATA.

Separate source facts, derived calculations and explanatory interpretation. Match form, requested duration, cutoff and accession. Use a revenue anchor, then prefer exact unit/duration facts from the same accession/filing date. Conflicting same-context values are unavailable. Missing data never becomes zero. Comparisons retain evidence; calendar and 52/53-week differences require duration matching, not naive year subtraction. Annual ROA/ROE use average balance values; quarterly flows never receive annual ratios without a declared annualization method.

Flow metrics: revenue/growth, gross/operating/net margins, EBIT, qualified EBITDA, EPS, CFO, capex and CFO−capex diagnostic. Balance metrics: cash, receivables, inventory, debt, assets/liabilities/equity, working capital, current ratio, leverage. Capital metrics: ROA, ROE, normalized-tax ROIC, interest coverage. Show accounting connections through balance-sheet residual, cash movement bridge, net-income/CFO adjustment total and retained-earnings reconciliation when source facts permit; unexplained residuals are evidence to investigate, not errors to hide.

Quarterly requests require exact quarter duration. Quarterly cash flow may be derived from current and prior YTD values only with compatible fiscal boundaries and disclosed two-accession provenance. Missing/ambiguous preceding YTD data leaves values unavailable. Growth from nonpositive bases is unavailable; CAGR requires positive endpoints and documented elapsed years.

## Product and scope

Users import companyfacts or fetch a CIK, choose annual/quarter duration, cutoff and normalized tax assumption, then inspect conclusions, comparison charts, financial ratios and individual source tags/filings. Export a reproducible JSON evidence package. Input changes clear stale results. Local first; provider contact identities are not persisted, no AI-generated financial values, no claim of complete custom-taxonomy/segment extraction. Banks and insurer statements require specialized models.

## Incremental plan (each milestone: red/green tests, commit, push)

1. Specification, isolated repository and packaging.
2. Typed bounded SEC input contracts and validation tests.
3. Honest offline/live ingestion with provenance and provider errors.
4. Accession/period/as-of fact selection with ambiguous/missing cases.
5. Primary statements, margins, liquidity and accounting identity tests.
6. Fiscal comparative periods, YoY/CAGR and average-balance ratios.
7. Cash-flow/retained-earnings connections and capital-efficiency analysis.
8. Quarterly/YTD derivation with explicit provenance and safeguards.
9. Analysis composition, deterministic interpretation and evidence hashing.
10. FastAPI endpoints and integration errors.
11. Browser import/fetch/request workflow and clear result states.
12. Comparison charts, statement connections and financial explanations.
13. Evidence export/reimport, browser user-journey verification.
14. Independent review fixes, input/dependency/security checks and CI.
15. Finance-first documentation, screenshots, final local/remote release checks.
