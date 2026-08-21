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


def test_unresolved_exchange_forces_no_data_without_calling_sources_or_analyst() -> None:
    """AC-4: exchange could not be determined despite otherwise-valid headers."""
    entries = [WatchlistEntry(ticker="AAPL", exchange="")]
    source = FakeSignalSource("s", text="growth")
    analyst = FakeFinancialAnalyst()

    rows = build_report_rows(entries, [source], analyst)

    assert len(rows) == 1
    assert rows[0].verdict == Verdict.NO_DATA
    assert "exchange" in rows[0].reason.lower()
    assert source.calls == []
    assert analyst.calls == []


def test_ticker_duplicated_across_three_exchanges_all_rows_no_data() -> None:
    entries = [
        WatchlistEntry(ticker="GOOGL", exchange="NASDAQ"),
        WatchlistEntry(ticker="GOOGL", exchange="LSE"),
        WatchlistEntry(ticker="GOOGL", exchange="TSXV"),
    ]
    source = FakeSignalSource("only", text="strong growth")
    analyst = FakeFinancialAnalyst()

    rows = build_report_rows(entries, [source], analyst)

    assert len(rows) == 3
    assert {row.exchange for row in rows} == {"NASDAQ", "LSE", "TSXV"}
    for row in rows:
        assert row.verdict == Verdict.NO_DATA
        assert "duplicate across exchanges" in row.reason
        assert "3" in row.reason
    assert source.calls == []
    assert analyst.calls == []


def test_in_section_dedup_does_not_inflate_cross_exchange_duplicate_count() -> None:
    """A ticker repeated within one exchange section must not be conflated
    with the same ticker legitimately appearing under a second exchange:
    the cross-exchange duplicate count must reflect distinct exchanges only.
    """
    # Simulates what the parser hands the orchestrator after in-section
    # dedup has already collapsed same-exchange repeats (AAPL appears only
    # once for NASDAQ here, even though the raw file listed it twice).
    entries = [
        WatchlistEntry(ticker="AAPL", exchange="NASDAQ"),
        WatchlistEntry(ticker="AAPL", exchange="LSE"),
    ]
    source = FakeSignalSource("only", text="strong growth")
    analyst = FakeFinancialAnalyst()

    rows = build_report_rows(entries, [source], analyst)

    assert len(rows) == 2
    for row in rows:
        assert row.verdict == Verdict.NO_DATA
        # Exactly two distinct exchanges, not more.
        assert "2" in row.reason
        assert "duplicate across exchanges" in row.reason


def test_end_to_end_parser_and_orchestrator_dedup_interaction() -> None:
    """Integration check spanning parser (in-section dedup) and orchestrator
    (cross-exchange dedup) together, matching AC-7 + AC-8 simultaneously.
    """
    from agentict.parser import parse_watchlist

    text = """# Stock exchange
NASDAQ

# Tickers
- AAPL
- AAPL
- MSFT

# Stock exchange
LSE

# Tickers
- AAPL
- BARC
"""
    entries = parse_watchlist(text)
    # In-section dedup: AAPL appears once for NASDAQ despite two list lines.
    nasdaq_aapl = [e for e in entries if e.ticker == "AAPL" and e.exchange == "NASDAQ"]
    assert len(nasdaq_aapl) == 1

    source = FakeSignalSource("only", text="strong growth")
    analyst = FakeFinancialAnalyst()
    rows = build_report_rows(entries, [source], analyst)

    aapl_rows = [row for row in rows if row.ticker == "AAPL"]
    assert len(aapl_rows) == 2  # one per exchange, AC-7 + AC-8
    for row in aapl_rows:
        assert row.verdict == Verdict.NO_DATA
        assert "duplicate across exchanges" in row.reason
        assert "2" in row.reason  # exactly 2 distinct exchanges, not 3

    # Unrelated tickers in the same run are processed normally.
    msft_row = next(row for row in rows if row.ticker == "MSFT")
    barc_row = next(row for row in rows if row.ticker == "BARC")
    assert msft_row.verdict == Verdict.INVEST
    assert barc_row.verdict == Verdict.INVEST
