"""Financial calculations preserve unavailable inputs and units."""

import math
from .schemas import JsonObject


def value(period: JsonObject, name: str) -> float | None:
    fact = period["facts"].get(name)
    return float(fact["value"]) if fact is not None else None


def ratio(numerator: float | None, denominator: float | None) -> float | None:
    # Nonpositive bases do not support ordinary valuation/liquidity ratio interpretation.
    if numerator is None or denominator is None or denominator <= 0:
        return None
    result = numerator / denominator
    return result if math.isfinite(result) else None


def difference(a: float | None, b: float | None) -> float | None:
    return a - b if a is not None and b is not None else None


def total(*values: float | None) -> float | None:
    return sum(v for v in values if v is not None) if all(v is not None for v in values) else None


def statement_metrics(period: JsonObject) -> dict[str, float | None]:
    def get(name: str) -> float | None:
        return value(period, name)

    long_term = total(get("current_debt"), get("long_term_debt"))
    debt = total(long_term, get("short_term_borrowings"))
    return {
        "gross_margin": ratio(get("gross_profit"), get("revenue")),
        "operating_margin": ratio(get("ebit"), get("revenue")),
        "net_margin": ratio(get("net_income"), get("revenue")),
        # This proxy depends on the reported D&A scope; it is not issuer-adjusted EBITDA.
        "ebitda_proxy": total(get("ebit"), get("depreciation")),
        "fcf_cfo_less_capex": difference(get("cfo"), get("capex")),
        "cash_conversion": ratio(get("cfo"), get("net_income")),
        "current_ratio": ratio(get("current_assets"), get("current_liabilities")),
        "working_capital": difference(get("current_assets"), get("current_liabilities")),
        "reported_long_term_debt": long_term,
        "debt": debt,
        "net_debt": difference(debt, get("cash")),
        "debt_to_equity": ratio(debt, get("equity")),
        "interest_coverage": ratio(get("ebit"), get("interest")),
        "balance_sheet_residual": difference(
            difference(get("assets"), get("liabilities")), get("equity")
        ),
    }
