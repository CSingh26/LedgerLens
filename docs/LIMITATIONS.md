# Scope and limitations

LedgerLens is a working analyst research application, not complete SEC filing extraction. It maps selected standard US-GAAP companyfacts concepts and rejects incompatible periods/units. Custom taxonomy, dimensions/segments, multiple share classes, IFRS, non-USD currency conversion, merger accounting and complex debt classifications are not reconstructed. Strict coverage therefore produces unavailable values for some real issuers.

Debt requires explicit short-term borrowings as well as current and noncurrent long-term debt. Separate commercial-paper-only or custom borrowing concepts are not inferred or combined; review completeness in the filing. ROIC uses all cash and a simplified capital base; leases, minority interests and tax attributes can materially change its interpretation. EBITDA adds reported D&A whose scope can differ from issuer-adjusted EBITDA. CFO minus capex is not unlevered FCFF.

Quarterly return ratios and some opening-balance connections are unavailable without appropriate beginning-period evidence. Quarterly YTD differences may span two filings and must be reviewed for restatements. Growth from zero/negative bases is unavailable, not zero. No forecasts, investment ratings or machine-learned statements are generated.

A filing cutoff excludes later filing dates but has day-level resolution. Comparatives within the chosen filing reflect that filing's historical presentation. Uploaded dates/identities are assertions; neither source labels nor hashes authenticate user data. Inspect original filings. The SEC provider has mocked success/error tests and an actual fixed-host implementation, but this release does not claim a successful live issuer download with a supplied personal identifying contact.

The fictional demo is reproducible and deliberately complete, unlike many actual companyfacts imports. There is no persisted user data, hosted production URL, custom tag editor or PDF/HTML narrative extraction. Provider network access, SEC availability and completeness remain external constraints.
