from datetime import date
import pytest
from pydantic import ValidationError
from ledgerlens.schemas import AnalysisRequest, CompanyFacts, Query, SecFact


def query(**changes):
    return dict(
        period_start="2025-01-01",
        period_end="2025-12-31",
        as_of="2026-03-01",
        form="10-K",
        **changes,
    )


def test_schema_accepts_official_extra_fields():
    fact = SecFact.model_validate(
        dict(
            start="2025-01-01",
            end="2025-12-31",
            val=100,
            accn="0000000001-26-000001",
            filed="2026-02-01",
            form="10-K",
            fy=2025,
            fp="FY",
        )
    )
    assert fact.val == 100
    assert fact.end == date(2025, 12, 31)


@pytest.mark.parametrize("value", [float("inf"), float("nan"), True])
def test_nonfinite_or_boolean_values_rejected(value):
    with pytest.raises(ValidationError):
        SecFact.model_validate(
            dict(
                end="2025-12-31",
                val=value,
                accn="0000000001-26-000001",
                filed="2026-02-01",
                form="10-K",
            )
        )


def test_date_and_duration_constraints():
    assert Query(**query()).form == "10-K"
    for field, value in [
        ("period_end", "2024-01-01"),
        ("as_of", "2024-01-01"),
        ("tax_rate", 1.2),
        ("form", "8-K"),
    ]:
        data = query()
        data[field] = value
        with pytest.raises(ValidationError):
            Query(**data)
    with pytest.raises(ValidationError):
        Query(period_start="2025-01-01", period_end="2025-12-31", as_of="2026-03-01", form="10-Q")


def test_request_rejects_unknown_analysis_parameters():
    facts = CompanyFacts(cik=1, entityName="Example", facts={})
    with pytest.raises(ValidationError):
        AnalysisRequest(companyfacts=facts, query=Query(**query()), unknown=True)
