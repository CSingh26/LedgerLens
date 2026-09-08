import pytest
from ledgerlens.metrics import statement_metrics
from ledgerlens.selection import select_period
from helpers import facts, query


def test_hand_calculated_statements_and_liquidity():
    m = statement_metrics(select_period(facts(), query()))
    assert m["gross_margin"] == pytest.approx(0.4)
    assert m["operating_margin"] == pytest.approx(0.2)
    assert m["net_margin"] == pytest.approx(0.12)
    assert m["ebitda_proxy"] == 230
    assert m["fcf_cfo_less_capex"] == 130
    assert m["current_ratio"] == 2
    assert m["working_capital"] == 200
    assert m["debt"] == 300
    assert m["net_debt"] == 200
    assert m["debt_to_equity"] == 0.6
    assert m["interest_coverage"] == 10
    assert m["balance_sheet_residual"] == 0
    assert m["cash_conversion"] == 1.5


def test_missing_or_nonpositive_denominators_are_unavailable():
    p = select_period(facts(), query())
    p["facts"]["current_liabilities"]["value"] = 0
    p["facts"]["depreciation"] = None
    p["facts"]["capex"] = None
    p["facts"]["net_income"]["value"] = -1
    m = statement_metrics(p)
    assert m["current_ratio"] is None
    assert m["ebitda_proxy"] is None
    assert m["fcf_cfo_less_capex"] is None
    assert m["cash_conversion"] is None


def test_total_debt_requires_short_term_borrowing_coverage():
    p = select_period(facts(), query())
    p["facts"]["short_term_borrowings"] = None
    m = statement_metrics(p)
    assert m["debt"] is None
    assert m["reported_long_term_debt"] == 300


def test_ratio_overflow_is_unavailable():
    p = select_period(facts(), query())
    p["facts"]["interest"]["value"] = 1e-300
    p["facts"]["ebit"]["value"] = 1e18
    assert statement_metrics(p)["interest_coverage"] is None
