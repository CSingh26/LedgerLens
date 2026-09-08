from datetime import date
from ledgerlens.quarterly import derive_quarterly_flows
from ledgerlens.schemas import CompanyFacts, Query
from ledgerlens.selection import select_period


def setup_quarter():
    def row(value, start, end, accn, filed):
        return dict(val=value, start=start, end=end, accn=accn, filed=filed, form="10-Q")

    current = "0000000001-25-000002"
    prior = "0000000001-25-000001"
    data = CompanyFacts.model_validate(
        {
            "cik": 1,
            "entityName": "DEMO Q",
            "facts": {
                "us-gaap": {
                    "Revenues": {
                        "units": {
                            "USD": [row(250, "2025-04-01", "2025-06-30", current, "2025-08-01")]
                        }
                    },
                    "NetCashProvidedByUsedInOperatingActivities": {
                        "units": {
                            "USD": [
                                row(140, "2025-01-01", "2025-06-30", current, "2025-08-01"),
                                row(60, "2025-01-01", "2025-03-31", prior, "2025-05-01"),
                            ]
                        }
                    },
                }
            },
        }
    )
    q = Query(period_start="2025-04-01", period_end="2025-06-30", as_of="2025-09-01", form="10-Q")
    return data, q


def test_ytd_difference_and_both_source_accessions():
    data, q = setup_quarter()
    p = select_period(data, q)
    assert p["facts"]["cfo"] is None
    result = derive_quarterly_flows(data, q, p)
    assert result["facts"]["cfo"]["value"] == 80
    assert result["facts"]["cfo"]["kind"] == "derived_ytd_difference"
    assert len(result["facts"]["cfo"]["sources"]) == 2
    assert result["facts"]["cfo"]["start"] == "2025-04-01"


def test_different_fiscal_starts_or_future_prior_restatement_are_rejected():
    data, q = setup_quarter()
    rows = data.facts["us-gaap"]["NetCashProvidedByUsedInOperatingActivities"].units["USD"]
    rows[1].start = date(2024, 12, 31)
    assert derive_quarterly_flows(data, q, select_period(data, q))["facts"]["cfo"] is None
    data, q = setup_quarter()
    rows = data.facts["us-gaap"]["NetCashProvidedByUsedInOperatingActivities"].units["USD"]
    rows[1].filed = date(2025, 8, 15)
    assert derive_quarterly_flows(data, q, select_period(data, q))["facts"]["cfo"] is None
