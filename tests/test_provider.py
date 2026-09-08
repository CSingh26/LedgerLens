import json
import httpx
import pytest
from ledgerlens.provider import ProviderError, fetch_companyfacts, parse_companyfacts

PAYLOAD = {"cik": 1, "entityName": "Demo Co", "facts": {}}


def test_offline_import_records_hash_and_rejects_bad_json():
    result = parse_companyfacts(json.dumps(PAYLOAD).encode())
    assert result["companyfacts"]["cik"] == 1
    assert len(result["metadata"]["sha256"]) == 64
    assert result["metadata"]["source"] == "USER PROVIDED DATA"
    with pytest.raises(ValueError):
        parse_companyfacts(b"{broken")
    with pytest.raises(ValueError):
        parse_companyfacts(b"x" * 10000001)


def test_sec_fetch_fixed_host_and_identity():
    def handle(request):
        assert str(request.url) == "https://data.sec.gov/api/xbrl/companyfacts/CIK0000000001.json"
        assert request.headers["User-Agent"] == "Research user@company.org"
        return httpx.Response(200, json=PAYLOAD)

    with httpx.Client(transport=httpx.MockTransport(handle)) as client:
        result = fetch_companyfacts(1, "Research user@company.org", client=client)
    assert result["metadata"]["source"] == "SEC EDGAR"
    assert result["metadata"]["source_url"].startswith("https://data.sec.gov/")


@pytest.mark.parametrize("status", [403, 404, 429, 500, 302])
def test_provider_errors_never_substitute_demo(status):
    with httpx.Client(
        transport=httpx.MockTransport(lambda request: httpx.Response(status))
    ) as client:
        with pytest.raises(ProviderError):
            fetch_companyfacts(1, "Research user@company.org", client=client)


def test_missing_user_agent_rejected_before_network():
    with pytest.raises(ValueError):
        fetch_companyfacts(1, "")
