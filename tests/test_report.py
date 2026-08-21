"""Tests for agentict.report."""

from __future__ import annotations

from agentict.disclaimer import DISCLAIMER
from agentict.models import ReportRow, Verdict
from agentict.report import render_report


def test_report_includes_disclaimer() -> None:
    report = render_report([])
    assert DISCLAIMER in report


def test_report_has_expected_columns_and_rows() -> None:
    rows = [
        ReportRow(ticker="AAPL", exchange="NASDAQ", verdict=Verdict.INVEST, reason="strong signal"),
        ReportRow(ticker="XYZ", exchange="LSE", verdict=Verdict.NOT, reason="weak signal"),
        ReportRow(ticker="GOOGL", exchange="NASDAQ", verdict=Verdict.NO_DATA, reason="duplicate across exchanges"),
    ]

    report = render_report(rows)

    assert "Ticker" in report
    assert "Exchange" in report
    assert "Verdict" in report
    assert "Reason" in report
    assert "AAPL" in report
    assert "NASDAQ" in report
    assert "Invest" in report
    assert "XYZ" in report
    assert "Not" in report
    assert "GOOGL" in report
    assert "no data available" in report
    assert "duplicate across exchanges" in report


def test_verdict_strings_match_exact_report_values() -> None:
    assert Verdict.INVEST.value == "Invest"
    assert Verdict.NOT.value == "Not"
    assert Verdict.NO_DATA.value == "no data available"


def test_empty_watchlist_report_has_no_rows_but_still_valid() -> None:
    report = render_report([])
    assert "(no tickers in watchlist)" in report
    assert DISCLAIMER in report
