# Independent ChronosResearch review

Reviewed 2026-09-08, immutable source checkpoint `82d90931f57e4160a909c7a9b3fc8b29e36352b1`. Scope: finance, quantitative chronology, data/engineering, browser evidence integrity, input/security boundaries and 90-second portfolio presentation. Review was read-only in ChronosResearch; this report is stored in the reviewer's LedgerLens repository.

## P2 — Export can join new input to a previous calculation

`chronos/static/app.js:63–70` disables only the Run button and snapshots `csvText` for `reportInput` after awaiting the response. The file handler at lines52–58 can replace `csvText` while an older request is running. When that older request completes, the export contains the new input CSV with the older result/hash/metadata. Edits to costs, horizon or source also leave prior results/export visible; failed runs retain them with a warning.

Reproduced in Chromium against the running workbench: the initial demo calculated 800 observations. Changing cost to99 retained visible results. Holding a subsequent `/api/research` response, selecting a new CSV containing only `date,close\n2026-01-01,1`, then releasing the response produced an exported package with that one-row CSV while `data.observations` remained800 and `data.sha256` remained `624b156f55bc380c4acf90f427ce979104f869ceaefe6713af95d85357bcbd65`. The package cannot reproduce its claimed results.

Snapshot the full request before fetch and reuse that immutable snapshot for the exported input. Clear results and disable export on source/assumption changes and invalid imports. Disable all dependent controls during requests or use request-version cancellation/discarding so older completions cannot restore stale results. Add a browser regression that changes source while a response is delayed and verifies exported input hash matches the result.

## Checks supporting the financial approach

- Features exclude close at decision time and use only prices through t−1. Forward labels are explicit close[t+h]/close[t]−1 and unavailable terminal labels are removed.
- Every training label end is strictly before validation/test or walk-forward decision start; preprocessing is fit inside the eligible training pipeline.
- Alpha is selected using the fixed validation grid. The fixed test does not select it. Walk-forward blocks freeze alpha and add only matured historical outcomes.
- Baselines are explicit zero and training historical mean. Zero forecasts abstain from directional accuracy, with null accuracy and zero coverage. Constant-outcome R² is unavailable.
- One-period strategy uses an additional observation lag, proportional turnover costs, final liquidation and costed buy-and-hold. Multi-period overlapping labels and nonexecutable reference rates suppress strategy simulation. No Sharpe or significance claim is invented.
- Regime cutoff comes from training volatility; standardized coefficients are described as associations. Point-in-time adjustment limitations and repeated-experiment contamination are disclosed.
- CSV/body caps, finite bounded prices, duplicate/date validation, sanitized validation errors and DOM text rendering reduce input hazards. Public operation remains outside the stated local deployment scope.

Executed the Python test suite: **47 passed**. Source and browser review did not uncover an additional actionable financial calculation defect within this scope. This is not a proof of absence of defects or an exhaustive penetration test.

## Portfolio assessment

The initial labeled demo answers a financial question, exposes chronology and baseline comparisons, and the documented real ECB snapshot reports an honest negative finding for Ridge. The explanation distinguishes forecast error from profitability and makes reference-rate execution limits explicit. The stale export defect should be fixed before treating downloaded research packages as reproducible evidence.

Finding sent to project owner and portfolio lead. Owner follow-up verification will be recorded when available.

## Verified closure

Owner fix `06e78464358d1d8a6a21feff6264cbc8a4d2705b` creates the full immutable request before awaiting, disables all research-form controls in flight, invalidates results/export on input/source changes and discards completions whose revision is stale. Independent source re-review and an independent run of `scripts/browser_state_regression.py` both passed. The actual Chromium regression verifies edits hide prior results, CSV/source/cost controls lock, and exported configuration matches the calculated request. The reproduced P2 is closed.
