"""Tests for agentict.orchestrator."""

from __future__ import annotations

from agentict.models import Verdict, WatchlistEntry
from agentict.orchestrator import build_report_rows

from .fakes import FakeFinancialAnalyst, FakeSignalSource


def test_partial_source_failure_still_assessed() -> None:
    entries = [WatchlistEntry(ticker="AAPL", exchange="NASDAQ")]
    good_source = FakeSignalSource("good", text="strong growth outlook")
    bad_source = FakeSignalSource("bad", fail=True)
    analyst = FakeFinancialAnalyst(verdict=Verdict.INVEST, rationale="looks good")

    rows = build_report_rows(entries, [good_source, bad_source], analyst)

    assert len(rows) == 1
    assert rows[0].ticker == "AAPL"
    assert rows[0].exchange == "NASDAQ"
    assert rows[0].verdict == Verdict.INVEST
    assert rows[0].reason == "looks good"
    assert len(analyst.calls) == 1
    assert good_source.calls == [("AAPL", "NASDAQ")]
    assert bad_source.calls == [("AAPL", "NASDAQ")]


def test_total_source_failure_forces_no_data_without_calling_analyst() -> None:
    entries = [WatchlistEntry(ticker="AAPL", exchange="NASDAQ")]
    source_one = FakeSignalSource("one", fail=True)
    source_two = FakeSignalSource("two", fail=True)
    analyst = FakeFinancialAnalyst()

    rows = build_report_rows(entries, [source_one, source_two], analyst)

    assert len(rows) == 1
    assert rows[0].verdict == Verdict.NO_DATA
    assert "all signal sources failed" in rows[0].reason
    assert analyst.calls == []


def test_cross_exchange_duplicate_forces_no_data_and_skips_sources_and_analyst() -> None:
    entries = [
        WatchlistEntry(ticker="GOOGL", exchange="NASDAQ"),
        WatchlistEntry(ticker="GOOGL", exchange="LSE"),
        WatchlistEntry(ticker="AAPL", exchange="NASDAQ"),
    ]
    source = FakeSignalSource("only", text="strong growth")
    analyst = FakeFinancialAnalyst()

    rows = build_report_rows(entries, [source], analyst)

    googl_rows = [row for row in rows if row.ticker == "GOOGL"]
    assert len(googl_rows) == 2
    for row in googl_rows:
        assert row.verdict == Verdict.NO_DATA
        assert "duplicate across exchanges" in row.reason

    # The non-duplicate ticker is processed normally.
    aapl_row = next(row for row in rows if row.ticker == "AAPL")
    assert aapl_row.verdict == Verdict.INVEST

    # Sources/analyst were never invoked for the duplicate ticker.
    assert all(ticker != "GOOGL" for ticker, _exchange in source.calls)
    assert all(ticker != "GOOGL" for ticker, _exchange, _signals in analyst.calls)


def test_row_order_matches_entry_order() -> None:
    entries = [
        WatchlistEntry(ticker="AAPL", exchange="NASDAQ"),
        WatchlistEntry(ticker="MSFT", exchange="NASDAQ"),
        WatchlistEntry(ticker="BARC", exchange="LSE"),
    ]
    source = FakeSignalSource("s", text="growth")
    analyst = FakeFinancialAnalyst()

    rows = build_report_rows(entries, [source], analyst)

    assert [row.ticker for row in rows] == ["AAPL", "MSFT", "BARC"]
