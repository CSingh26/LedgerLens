"""Compose structured evidence, calculations and deterministic financial interpretation."""

from datetime import date, datetime, timezone
import hashlib
import json
from .comparatives import comparative_periods, growth_metrics
from .connections import analyze_connections
from .metrics import ratio, statement_metrics, value
from .quarterly import derive_quarterly_flows
from .schemas import AnalysisRequest, JsonObject, Query
from .selection import TAGS, rows_for, select_period


def analyze(request: AnalysisRequest) -> JsonObject:
    data, query = request.companyfacts, request.query
    selected = select_period(data, query)
    periods = comparative_periods(data, query, selected)
    periods = [
        derive_quarterly_flows(
            data,
            Query(
                period_start=p["start"],
                period_end=p["end"],
                as_of=query.as_of,
                form=query.form,
                tax_rate=query.tax_rate,
            ),
            p,
        )
        for p in periods
    ]
    current = periods[0]
    metrics = statement_metrics(current) | growth_metrics(periods, query)
    metrics["revenue_qoq"] = None
    qoq_evidence = None
    if query.form == "10-Q":
        rows = [
            r
            for _, _, r in rows_for(data, "revenue", query)
            if r.start is not None
            and (query.period_start - r.end).days == 1
            and 60 <= (r.end - r.start).days + 1 <= 110
            and str(r.filed) <= current["filed"]
        ]
        if rows:
            anchor = max(rows, key=lambda r: (r.filed, r.accn))
            assert anchor.start is not None
            qoq_evidence = select_period(
                data,
                Query(
                    period_start=anchor.start,
                    period_end=anchor.end,
                    as_of=date.fromisoformat(current["filed"]),
                    form="10-Q",
                    tax_rate=query.tax_rate,
                ),
            )
            growth = ratio(value(current, "revenue"), value(qoq_evidence, "revenue"))
            metrics["revenue_qoq"] = growth - 1 if growth is not None else None
    connections = analyze_connections(periods, query)
    metrics["roic"] = connections["roic"]
    missing = [name for name in TAGS if current["facts"][name] is None]
    warnings = [
        *current["warnings"],
        *connections["notes"],
        "Total debt requires explicit short-term borrowings plus current and noncurrent long-term debt. Missing coverage suppresses net debt, leverage and ROIC; the separately named long-term-debt proxy excludes short-term borrowing.",
        "Nonpositive ratio bases and nonfinite calculations are unavailable; inspect source units and very small denominators.",
        "US GAAP common-tag mapping; custom taxonomy, segment dimensions and non-USD statements need specialist review.",
        "Uploaded issuer identity and fact authenticity are user assertions. Filed-date cutoff is day-level, not intraday availability.",
        "Banks and insurers require specialized balance-sheet and capital definitions.",
        "EBITDA is an EBIT-plus-reported-D&A proxy, not issuer-adjusted EBITDA. CFO minus capex is not unlevered FCFF.",
    ]
    if missing:
        warnings.append("Unavailable matched facts: " + ", ".join(missing))
    if query.form == "10-Q":
        warnings.append(
            "Quarterly flows are not annualized. ROA/ROE/ROIC and annual CAGR remain unavailable."
        )
    residual = metrics["balance_sheet_residual"]
    assets = value(current, "assets")
    if residual is not None and assets is not None and abs(residual) > max(1, abs(assets) * 1e-6):
        warnings.append(
            "Assets differ from liabilities plus equity beyond tolerance; inspect scope, minority interest and filing context."
        )
    fcf = metrics["fcf_cfo_less_capex"]
    growth_value = metrics["revenue_yoy"]
    conclusions = [
        {
            "title": "Cash behind earnings",
            "text": f"CFO less capital expenditure is USD {fcf:,.0f}. Investigate reinvestment and working-capital movements before treating earnings as available cash."
            if fcf is not None
            else "Matched CFO and capex are unavailable. No free-cash-flow amount is inferred.",
            "evidence": ["cfo", "capex"],
            "kind": "calculated_interpretation",
        },
        {
            "title": "Growth needs a comparable base",
            "text": f"Revenue changed {growth_value:.1%} against the comparable prior fiscal period in this filing. Margins and cash conversion determine its economic quality."
            if growth_value is not None
            else "A positive, comparable prior revenue base is unavailable; growth is not calculated.",
            "evidence": ["revenue"],
            "kind": "calculated_interpretation",
        },
        {
            "title": "Statements should connect",
            "text": f"The assets − liabilities − equity residual is USD {residual:,.0f}. A zero residual is a consistency check, not proof that source facts are complete or audited."
            if residual is not None
            else "The balance-sheet identity cannot be assessed because matched components are missing.",
            "evidence": ["assets", "liabilities", "equity"],
            "kind": "calculated_interpretation",
        },
    ]
    canonical = json.dumps(
        request.model_dump(mode="json"), sort_keys=True, separators=(",", ":"), allow_nan=False
    )
    if request.source_label == "DEMO DATA":
        current["filing_url"] = None
    return {
        "data_label": request.source_label,
        "metadata": {
            "entity": data.entityName,
            "cik": data.cik,
            "input_sha256": hashlib.sha256(canonical.encode()).hexdigest(),
            "calculated_at": datetime.now(timezone.utc).isoformat(),
            "as_of": str(query.as_of),
            "currency": "USD",
            "money_unit": "absolute",
            "tax_assumption": query.tax_rate,
            "methodology_version": "ledgerlens-v1",
            "source_authenticity_verified": False,
        },
        "evidence": current,
        "comparative_periods": periods,
        "qoq_evidence": qoq_evidence,
        "metrics": metrics,
        "connections": connections,
        "interpretation": conclusions,
        "warnings": warnings,
        "values": {name: value(current, name) for name in TAGS},
    }
