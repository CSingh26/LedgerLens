"""Derive a discrete quarter only from compatible cumulative fiscal periods."""
from copy import deepcopy
from datetime import date, timedelta
from .schemas import CompanyFacts, JsonObject, Query
from .selection import evidence, rows_for

CUMULATIVE = ['cfo','capex','cfi','cff','fx_cash','depreciation','repurchases']


def derive_quarterly_flows(data: CompanyFacts, query: Query, period: JsonObject) -> JsonObject:
    result = deepcopy(period)
    if query.form != '10-Q':
        return result
    cutoff = date.fromisoformat(period['filed'])
    for name in CUMULATIVE:
        if result['facts'][name] is not None:
            continue
        eligible = rows_for(data,name,query)
        current = [(tag,unit,row) for tag,unit,row in eligible
                   if row.accn==period['accession'] and row.filed==cutoff
                   and row.end==query.period_end and row.start is not None
                   and row.start<query.period_start and (row.end-row.start).days<=310]
        if not current:
            continue
        tag,unit,_ = current[0]
        current = [item for item in current if item[0]==tag]
        if len({(r.start,r.val) for _,_,r in current})!=1:
            result['warnings'].append(f'Ambiguous current YTD {name}; quarter unavailable')
            continue
        ending = current[0][2]
        prior = [(t,u,row) for t,u,row in eligible if t==tag and row.start==ending.start
                 and row.end==query.period_start-timedelta(days=1) and row.filed<=cutoff]
        if not prior:
            continue
        latest = max(prior,key=lambda item:(item[2].filed,item[2].accn))[2]
        matches = [r for _,_,r in prior if r.filed==latest.filed and r.accn==latest.accn]
        if len({r.val for r in matches})!=1:
            result['warnings'].append(f'Ambiguous preceding YTD {name}; quarter unavailable')
            continue
        result['facts'][name] = {**evidence(tag,unit,ending),
                                'value':ending.val-latest.val,'start':str(query.period_start),
                                'kind':'derived_ytd_difference',
                                'sources':[evidence(tag,unit,ending),evidence(tag,unit,latest)]}
        result['warnings'].append(f'{name} is current YTD minus prior YTD using disclosed accessions; review classification/restatement consistency.')
    return result
