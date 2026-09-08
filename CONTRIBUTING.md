# Contributing

Read the financial methodology before changing calculations. Create a regression test showing the intended financial behavior before implementation: period mismatch, denominator semantics, missing evidence and provenance matter as much as nominal arithmetic. Keep fixtures visibly fictional and avoid introducing real contact identities or credentials.

Use Python 3.12, install the locked dependencies and editable package as documented in the README, then `npm ci` and `npx playwright install chromium`. Run `CI=1 bash scripts/verify.sh` before submitting changes. Update locks deliberately when changing dependencies. Browser tests generate screenshots for visual review; inspect both desktop and mobile outputs after layout changes.

A pull request should explain the financial problem, resulting behavior, evidence supporting the method, tests and remaining assumptions. Do not expand tag aliases without considering overlap, dates and units. Keep pure calculation modules independent from provider/network code.
