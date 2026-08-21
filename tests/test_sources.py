"""Tests for the built-in network signal source collectors.

These use ``requests-mock`` (already a dev dependency) so no real network
access ever happens in the test suite.
"""

from __future__ import annotations

import requests

from agentict.errors import SourceError
from agentict.sources.yahoo_finance import YahooFinanceSource
from agentict.sources.google_search import WebSearchSource

import pytest


# ---------------------------------------------------------------------------
# YahooFinanceSource
# ---------------------------------------------------------------------------


def test_yahoo_finance_success_returns_economic_hinted_signal(requests_mock) -> None:
    source = YahooFinanceSource()
    requests_mock.get(
        source._endpoint,
        json={
            "quoteResponse": {
                "result": [
                    {
                        "shortName": "Apple Inc.",
                        "regularMarketPrice": 150.0,
                        "regularMarketChangePercent": 1.5,
                        "marketCap": 2_500_000_000_000,
                        "sector": "Technology",
                    }
                ]
            }
        },
    )

    signal = source.fetch("AAPL", "NASDAQ")

    assert signal.category_hint == "economic"
    assert "AAPL" in signal.text
    assert "NASDAQ" in signal.text


def test_yahoo_finance_http_error_wrapped_as_source_error(requests_mock) -> None:
    source = YahooFinanceSource()
    requests_mock.get(source._endpoint, status_code=500)

    with pytest.raises(SourceError):
        source.fetch("AAPL", "NASDAQ")


def test_yahoo_finance_network_exception_wrapped_as_source_error(requests_mock) -> None:
    source = YahooFinanceSource()
    requests_mock.get(source._endpoint, exc=requests.exceptions.ConnectTimeout)

    with pytest.raises(SourceError):
        source.fetch("AAPL", "NASDAQ")


def test_yahoo_finance_malformed_json_wrapped_as_source_error(requests_mock) -> None:
    source = YahooFinanceSource()
    requests_mock.get(source._endpoint, text="not json at all")

    with pytest.raises(SourceError):
        source.fetch("AAPL", "NASDAQ")


def test_yahoo_finance_empty_result_list_wrapped_as_source_error(requests_mock) -> None:
    source = YahooFinanceSource()
    requests_mock.get(source._endpoint, json={"quoteResponse": {"result": []}})

    with pytest.raises(SourceError):
        source.fetch("UNKNOWN", "NASDAQ")


# ---------------------------------------------------------------------------
# WebSearchSource
# ---------------------------------------------------------------------------


def test_web_search_success_returns_uncategorized_signal(requests_mock) -> None:
    source = WebSearchSource()
    requests_mock.get(source._endpoint, text="Apple stock outlook remains strong")

    signal = source.fetch("AAPL", "NASDAQ")

    assert signal.category_hint is None
    assert "Apple stock outlook" in signal.text


def test_web_search_http_error_wrapped_as_source_error(requests_mock) -> None:
    source = WebSearchSource()
    requests_mock.get(source._endpoint, status_code=503)

    with pytest.raises(SourceError):
        source.fetch("AAPL", "NASDAQ")


def test_web_search_network_exception_wrapped_as_source_error(requests_mock) -> None:
    source = WebSearchSource()
    requests_mock.get(source._endpoint, exc=requests.exceptions.ConnectionError)

    with pytest.raises(SourceError):
        source.fetch("AAPL", "NASDAQ")


def test_web_search_empty_response_wrapped_as_source_error(requests_mock) -> None:
    source = WebSearchSource()
    requests_mock.get(source._endpoint, text="   ")

    with pytest.raises(SourceError):
        source.fetch("AAPL", "NASDAQ")
