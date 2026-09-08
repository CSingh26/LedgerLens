# Data dictionary

`companyfacts` follows the SEC companyfacts object: numeric `cik`, `entityName`, `facts.us-gaap`, concept objects, `units`, then observations with `val`, `start` when a duration, `end`, `accn`, `form`, `filed`. Source values are strictly finite numeric values bounded to ±1e18; booleans are rejected. No more than 200,000 observations or 10 MB may be imported.

The authoritative implemented tag alias map is `src/ledgerlens/selection.py:TAGS`. It covers revenue, gross profit, operating income, net income, CFO, capex, D&A, assets, liabilities, equity, cash, current assets/liabilities, receivables, inventory, current/noncurrent long-term debt, short-term borrowings, interest expense, diluted EPS/shares, retained earnings, investing/financing/FX cash flows, cash-plus-restricted-cash and repurchases. It does not support arbitrary custom tags or dimension reconstruction. Units are USD, shares or USD/shares as appropriate.

`query` uses ISO dates `period_start`, `period_end`, `as_of`, `form` and fractional `tax_rate` (0.25 means 25%). All UI tax entries are percentages and explicitly converted. `source_label` communicates the selected input route; it does not authenticate an upload.

Analysis response:

| Field | Meaning |
|---|---|
| `data_label` | Visible demo/upload/SEC source category |
| `metadata` | Issuer, CIK, units, normalized input hash, timestamp, method version, authenticity caveat |
| `evidence` | Selected filing and matched observations; nulls preserve missing values |
| `comparative_periods` | Matching fiscal observations and their source basis |
| `metrics` | Scalar financial calculations; null means unavailable |
| `connections` | Cash reconciliation, earnings links, capital inputs and assumptions |
| `interpretation` | Deterministic explanations tied to calculated evidence |
| `warnings` | Coverage and interpretation limitations |

Evidence package v1 contains `format`, original analysis `input`, calculated `result`, and optional `source_metadata`. Reimports consume the input and recalculate, treating any metadata as supplied provenance. User contact strings are not included in the exported analysis request.
