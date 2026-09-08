"""Comparative fiscal periods remain in the same filing; no naive calendar subtraction."""

from datetime import date
from .schemas import CompanyFacts, JsonObject, Query
from .selection import rows_for, select_period
from .metrics import ratio, value


def comparative_periods(data: CompanyFacts, query: Query, current: JsonObject) -> list[JsonObject]:
    periods = [current]
    candidates = {
        (row.start, row.end)
        for _, _, row in rows_for(data, "revenue", query)
        if row.accn == current["accession"]
        and str(row.filed) == current["filed"]
        and row.start is not None
        and row.end < query.period_end
        and abs((row.end - row.start).days + 1 - current["days"]) <= 14
    }
    last_end = query.period_end
    for _ in range(4):
        eligible = [
            (start, end) for start, end in candidates if 330 <= (last_end - end).days <= 400
        ]
        if not eligible:
            break
        start, end = min(eligible, key=lambda p: abs((last_end - p[1]).days - 365))
        q = Query(
            period_start=start,
            period_end=end,
            as_of=query.as_of,
            form=query.form,
            tax_rate=query.tax_rate,
        )
        periods.append(
            select_period(
                data, q, accession=current["accession"], filed=date.fromisoformat(current["filed"])
            )
        )
        last_end = end
    return periods


def growth_metrics(periods: list[JsonObject], query: Query) -> dict[str, float | None]:
    current = periods[0]
    prior = periods[1] if len(periods) > 1 else None
    result: dict[str, float | None] = {}
    for name in ["revenue", "net_income", "eps", "diluted_shares", "cfo"]:
        comparison = ratio(value(current, name), value(prior, name)) if prior else None
        result[name + "_yoy"] = comparison - 1 if comparison is not None else None
    # CAGR spans consecutive eligible fiscal years, not a partial-year annualization.
    first, last = value(periods[-1], "revenue"), value(current, "revenue")
    endpoint_ratio = ratio(last, first)
    result["revenue_cagr"] = (
        endpoint_ratio ** (1 / (len(periods) - 1)) - 1
        if query.form == "10-K"
        and len(periods) > 1
        and first is not None
        and last is not None
        and first > 0
        and last > 0
        and endpoint_ratio is not None
        else None
    )
    result["cagr_fiscal_years"] = (
        float(len(periods) - 1) if query.form == "10-K" and len(periods) > 1 else None
    )
    for metric, balance in [("roe", "equity"), ("roa", "assets")]:
        a, b = value(current, balance), value(prior, balance) if prior else None
        comparable_opening = (
            prior and 1 <= (query.period_start - date.fromisoformat(prior["end"])).days <= 14
        )
        average = (a + b) / 2 if a is not None and b is not None else None
        result[metric] = (
            ratio(value(current, "net_income"), average)
            if query.form == "10-K" and comparable_opening
            else None
        )
    return result
