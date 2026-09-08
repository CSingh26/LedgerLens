import pytest
from ledgerlens.selection import select_period
from helpers import facts, query


def test_exact_accession_units_period_and_provenance():
 result=select_period(facts(),query())
 assert result['facts']['revenue']['value']==1000
 assert result['facts']['revenue']['tag']=='RevenueFromContractWithCustomerExcludingAssessedTax'
 assert result['facts']['revenue']['unit']=='USD'
 assert result['facts']['cash']['start'] is None
 assert '000000000126000001' in result['filing_url']


def test_future_and_wrong_duration_not_blended():
 data=facts();q=query().model_copy(update={'as_of':query().period_end})
 with pytest.raises(ValueError,match='revenue'): select_period(data,q)
 data.facts['us-gaap']['NetCashProvidedByUsedInOperatingActivities'].units['USD'][0].start=query().period_end
 assert select_period(data,query())['facts']['cfo'] is None


def test_conflicting_duplicates_and_different_accession_unavailable():
 data=facts();rows=data.facts['us-gaap']['OperatingIncomeLoss'].units['USD']
 rows.append(rows[0].model_copy(update={'val':999}))
 result=select_period(data,query())
 assert result['facts']['ebit'] is None
 assert any('Conflicting' in x for x in result['warnings'])
 data=facts();data.facts['us-gaap']['GrossProfit'].units['USD'][0].accn='0000000001-26-000099'
 assert select_period(data,query())['facts']['gross_profit'] is None
