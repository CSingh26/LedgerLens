# Architecture and operation

Browser → bounded stateless FastAPI → typed companyfacts/query → filing selector → metrics/comparatives/quarter derivation/connections → evidence response → charts and export.

Pure financial modules depend on typed validated inputs and explicit observation dictionaries. Provider code is the only external-network path: fixed `data.sec.gov`, numeric CIK, no redirects, 15-second timeout, 10 MB streamed cap and four requests/second process-local limiter. Contact identity is user-supplied. Multiple server processes would require a shared limit to enforce a combined user rate.

The browser and API share an origin. Static files are included in the wheel. There is no database, account system or disk upload persistence. API docs describe input schemas. Invalid finite bounds and nonfinite JSON return safe 422 responses without reserializing unsafe input; oversized bodies return 413. Provider errors return honest unavailable responses.

Rendering uses DOM text content for imported names and evidence. Source controls are disabled during requests and edits clear prior calculations. HTTP response data never becomes executable HTML. Browser tests cover a malicious issuer-name string. No remote font or analytics dependency is needed.

This release targets a local trusted analyst. Network deployment needs authentication, access control, TLS, cross-process/provider limits, request concurrency limits, monitoring and an explicit retention policy. Do not expose the development server as a multiuser service.

`requirements.lock` and `package-lock.json` pin the tested environment. CI executes `scripts/verify.sh` on Python 3.12/Node 22 and uploads browser screenshots. Local use of Chrome is supported; `CI=1` selects installed Playwright Chromium. The package has no ML subsystem: deterministic financial calculations are more appropriate for these statements.
