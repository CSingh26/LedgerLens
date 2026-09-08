import pytest
from ledgerlens.service import analyze
from ledgerlens.schemas import AnalysisRequest
from ledgerlens.demo import demo_request
from helpers import facts, query


def test_analysis_layers_provenance_and_conclusions():
    request = AnalysisRequest(companyfacts=facts(), query=query())
    result = analyze(request)
    assert result["metrics"]["revenue_yoy"] == pytest.approx(0.25)
    assert result["connections"]["cash_bridge"]["residual"] == 0
    assert result["metadata"]["input_sha256"] == analyze(request)["metadata"]["input_sha256"]
    assert result["data_label"] == "USER PROVIDED DATA"
    assert result["interpretation"][0]["kind"] == "calculated_interpretation"
    assert any("cash" in x["title"].lower() for x in result["interpretation"])
    assert result["evidence"]["facts"]["revenue"]["value"] == 1000


def test_demo_is_labeled_and_schema_valid():
    request = demo_request()
    result = analyze(request)
    assert result["data_label"] == "DEMO DATA"
    assert result["metadata"]["entity"].startswith("DEMO DATA")
    assert result["metrics"]["balance_sheet_residual"] == 0


def test_quarterly_qoq_compares_adjacent_quarters_without_annualizing():
    from test_quarterly import setup_quarter
    from ledgerlens.schemas import SecFact

    data, q = setup_quarter()
    data.facts["us-gaap"]["Revenues"].units["USD"].append(
        SecFact.model_validate(
            {
                "val": 200,
                "start": "2025-01-01",
                "end": "2025-03-31",
                "filed": "2025-05-01",
                "accn": "0000000001-25-000001",
                "form": "10-Q",
            }
        )
    )
    result = analyze(AnalysisRequest(companyfacts=data, query=q))
    assert result["metrics"]["revenue_qoq"] == 0.25
    assert result["qoq_evidence"]["accession"] == "0000000001-25-000001"
    assert result["metrics"]["roe"] is None
    assert result["metrics"]["roic"] is None
    assert result["values"]["cfo"] == 80
