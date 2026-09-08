from datetime import date,timedelta
import pytest
from ledgerlens.comparatives import comparative_periods, growth_metrics
from ledgerlens.selection import select_period
from helpers import facts, query


def test_growth_cagr_and_average_balance_returns():
 data=facts();q=query();current=select_period(data,q)
 periods=comparative_periods(data,q,current)
 assert len(periods)==3
 m=growth_metrics(periods,q)
 assert m['revenue_yoy']==pytest.approx(.25)
 assert m['revenue_cagr']==pytest.approx((1000/600)**.5-1)
 assert m['roe']==pytest.approx(120/450)
 assert m['roa']==pytest.approx(120/1100)


def test_nonpositive_growth_base_and_missing_comparative():
 data=facts();data.facts['us-gaap']['RevenueFromContractWithCustomerExcludingAssessedTax'].units['USD'][1].val=-100
 q=query();periods=comparative_periods(data,q,select_period(data,q))
 assert growth_metrics(periods,q)['revenue_yoy'] is None
 assert growth_metrics(periods[:1],q)['roe'] is None


def test_fiscal_52_week_comparisons_do_not_require_same_calendar_date():
 data=facts();q=query();prior_end=date(2024,12,28);prior_start=date(2023,12,31)
 for concept in data.facts['us-gaap'].values():
  for rows in concept.units.values():
   rows[1].end=prior_end
   if rows[1].start: rows[1].start=prior_start
 periods=comparative_periods(data,q,select_period(data,q))
 assert periods[1]['end']=='2024-12-28'
 assert growth_metrics(periods,q)['revenue_yoy']==pytest.approx(.25)
