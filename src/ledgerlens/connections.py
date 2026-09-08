"""Reconcile statements without inventing missing reconciling items."""
from datetime import date
from .metrics import difference, ratio, total, value
from .schemas import JsonObject, Query


def analyze_connections(periods: list[JsonObject], query: Query) -> JsonObject:
    current, prior = periods[0], periods[1] if len(periods)>1 else None
    # A comparative prior-year quarter is not the opening balance of the current quarter.
    opening_aligned = prior is not None and 1 <= (query.period_start-date.fromisoformat(prior['end'])).days <= 14
    def opening(name: str) -> float | None:
        return value(prior,name) if prior and opening_aligned else None
    closing_cash = value(current,'cash_flow_balance')
    cash_flows = total(*(value(current,k) for k in ['cfo','cfi','cff','fx_cash']))
    cash_change = difference(closing_cash,opening('cash_flow_balance'))
    def invested(period: JsonObject) -> float | None:
        return difference(total(*(value(period,k) for k in ['current_debt','long_term_debt','equity'])),value(period,'cash'))
    current_capital = invested(current)
    prior_capital = invested(prior) if prior and opening_aligned else None
    average = (current_capital+prior_capital)/2 if current_capital is not None and prior_capital is not None else None
    ebit = value(current,'ebit')
    # Normalized tax on profits; no assumed cash refund in loss periods.
    nopat = ebit-max(ebit,0)*query.tax_rate if ebit is not None else None
    return {
        'cash_bridge': {'opening':opening('cash_flow_balance'), 'cfo':value(current,'cfo'),
                       'cfi':value(current,'cfi'), 'cff':value(current,'cff'),'fx':value(current,'fx_cash'),
                       'net_flows':cash_flows,'closing':closing_cash,'residual':difference(cash_change,cash_flows)},
        'income_to_cfo_adjustments':difference(value(current,'cfo'),value(current,'net_income')),
        'retained_earnings_change':difference(value(current,'retained_earnings'),opening('retained_earnings')),
        'retained_earnings_other_changes':difference(difference(value(current,'retained_earnings'),opening('retained_earnings')),value(current,'net_income')),
        'average_invested_capital':average,
        'roic':ratio(nopat,average) if query.form=='10-K' else None,
        'tax_assumption':query.tax_rate,
        'notes':['Cash bridge requires the same cash+restricted-cash scope and every cash-flow component; no missing FX value becomes zero.',
                 'CFO minus net income aggregates working-capital and noncash adjustments; it does not identify individual reconciling items.',
                 'Retained earnings other changes may include dividends, accounting adjustments and other movements; no dividend amount is inferred.',
                 'ROIC uses debt + equity − all cash and normalized taxes. Review excess cash, leases, minority interests and tax-loss carryforwards.'],
    }
