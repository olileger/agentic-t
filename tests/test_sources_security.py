"""Security regression tests for HTTP-based signal source collectors.

These target a concrete finding: without a response-size cap, a
malicious/compromised server (or an on-path attacker impersonating a
configured endpoint) could return an oversized or effectively unbounded body
and exhaust memory in this single-process CLI. Collectors must instead
detect this and fail closed with ``SourceError`` (per the ``SignalSource``
contract), never crash the process or buffer unboundedly.
"""

from __future__ import annotations

import pytest
import requests
import requests_mock

from agentict.errors import SourceError
from agentict.sources._http import MAX_RESPONSE_BYTES
from agentict.sources.google_search import WebSearchSource
from agentict.sources.yahoo_finance import YahooFinanceSource


def test_web_search_source_rejects_oversized_response() -> None:
    source = WebSearchSource(endpoint="https://example.test/search")
    oversized_body = "x" * (MAX_RESPONSE_BYTES + 1024)

    with requests_mock.Mocker() as mocker:
        mocker.get("https://example.test/search", text=oversized_body)
        with pytest.raises(SourceError):
            source.fetch("AAPL", "NASDAQ")


def test_web_search_source_accepts_response_within_cap() -> None:
    source = WebSearchSource(endpoint="https://example.test/search")

    with requests_mock.Mocker() as mocker:
        mocker.get("https://example.test/search", text="some ordinary search result text")
        signal = source.fetch("AAPL", "NASDAQ")

    assert "search result text" in signal.text


def test_yahoo_finance_source_rejects_oversized_response() -> None:
    source = YahooFinanceSource(endpoint="https://example.test/quote")
    # Oversized but otherwise-valid-shaped JSON padding, so the size cap
    # (not JSON parsing) is what's being exercised.
    oversized_body = '{"quoteResponse": {"result": [], "pad": "' + (
        "x" * (MAX_RESPONSE_BYTES + 1024)
    ) + '"}}'

    with requests_mock.Mocker() as mocker:
        mocker.get("https://example.test/quote", text=oversized_body)
        with pytest.raises(SourceError):
            source.fetch("AAPL", "NASDAQ")


def test_yahoo_finance_source_accepts_response_within_cap() -> None:
    source = YahooFinanceSource(endpoint="https://example.test/quote")
    body = (
        '{"quoteResponse": {"result": [{"shortName": "Apple Inc.", '
        '"regularMarketPrice": 100, "regularMarketChangePercent": 1.5, '
        '"marketCap": 1000000, "sector": "Technology"}]}}'
    )

    with requests_mock.Mocker() as mocker:
        mocker.get("https://example.test/quote", text=body)
        signal = source.fetch("AAPL", "NASDAQ")

    assert "Apple" in signal.text


def test_web_search_source_never_leaks_raw_exception_type() -> None:
    """Per the SignalSource contract, only SourceError may escape fetch()."""
    source = WebSearchSource(endpoint="https://example.test/search")

    with requests_mock.Mocker() as mocker:
        mocker.get("https://example.test/search", exc=requests.exceptions.ConnectTimeout)
        with pytest.raises(SourceError):
            source.fetch("AAPL", "NASDAQ")
