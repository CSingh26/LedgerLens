import pytest
from ledgerlens.connections import analyze_connections
from ledgerlens.comparatives import comparative_periods
from ledgerlens.selection import select_period
from helpers import facts, query


def test_cash_earnings_and_roic_hand_calculation():
    data = facts()
    q = query()
    p = comparative_periods(data, q, select_period(data, q))
    result = analyze_connections(p, q)
    assert result["cash_bridge"]["opening"] == 80
    assert result["cash_bridge"]["net_flows"] == 20
    assert result["cash_bridge"]["closing"] == 100
    assert result["cash_bridge"]["residual"] == 0
    assert result["income_to_cfo_adjustments"] == 60
    assert result["retained_earnings_other_changes"] == -30
    assert result["roic"] == pytest.approx(150 / 660)


def test_missing_fx_is_not_assumed_zero_and_negative_ebit_gets_no_refund():
    data = facts()
    q = query()
    p = comparative_periods(data, q, select_period(data, q))
    p[0]["facts"]["fx_cash"] = None
    p[0]["facts"]["ebit"]["value"] = -100
    result = analyze_connections(p, q)
    assert result["cash_bridge"]["residual"] is None
    assert result["roic"] == pytest.approx(-100 / 660)
