"""Fixed-host SEC retrieval with bounded bodies, honest errors and provenance."""

from datetime import datetime, timezone
import hashlib
import re
import threading
import time
import httpx
from .schemas import CompanyFacts, JsonObject

MAX_BYTES = 10_000_000
_gate = threading.Lock()
_last_request = 0.0


class ProviderError(ValueError):
    pass


def parse_companyfacts(
    content: bytes, source: str = "USER PROVIDED DATA", url: str | None = None
) -> JsonObject:
    if len(content) > MAX_BYTES:
        raise ValueError("Companyfacts exceeds 10 MB")
    facts = CompanyFacts.model_validate_json(content)
    return {
        "companyfacts": facts.model_dump(mode="json"),
        "metadata": {
            "source": source,
            "source_url": url,
            "retrieved_at": datetime.now(timezone.utc).isoformat(),
            "sha256": hashlib.sha256(content).hexdigest(),
            "bytes": len(content),
            "identity_verified": source == "SEC EDGAR",
        },
    }


def fetch_companyfacts(cik: int, user_agent: str, client: httpx.Client | None = None) -> JsonObject:
    global _last_request
    if not 0 < cik <= 9999999999:
        raise ValueError("CIK must be a positive identifier up to 10 digits")
    if (
        not 8 <= len(user_agent) <= 200
        or not re.search(r"\S+@\S+\.\S+", user_agent)
        or "\n" in user_agent
        or "\r" in user_agent
    ):
        raise ValueError("Provide an identifying SEC User-Agent with your contact email")
    if client is None:
        with httpx.Client(timeout=15, follow_redirects=False) as owned:
            return fetch_companyfacts(cik, user_agent, owned)
    # Limit this process to four requests/second, below the SEC's per-user ceiling.
    with _gate:
        time.sleep(max(0.0, 0.25 - (time.monotonic() - _last_request)))
        _last_request = time.monotonic()
    url = f"https://data.sec.gov/api/xbrl/companyfacts/CIK{cik:010d}.json"
    try:
        with client.stream(
            "GET", url, headers={"User-Agent": user_agent, "Accept": "application/json"}
        ) as response:
            if response.status_code != 200:
                raise ProviderError(
                    f"SEC data unavailable (HTTP {response.status_code}); retry later or upload companyfacts JSON"
                )
            content = bytearray()
            for part in response.iter_bytes():
                content.extend(part)
                if len(content) > MAX_BYTES:
                    raise ProviderError("SEC response exceeds 10 MB")
        result = parse_companyfacts(bytes(content), "SEC EDGAR", url)
        if result["companyfacts"]["cik"] != cik:
            raise ProviderError("SEC response CIK does not match the requested issuer")
        return result
    except httpx.HTTPError as exc:
        raise ProviderError(
            "SEC data unavailable due to network/timeout; no replacement data supplied"
        ) from exc
