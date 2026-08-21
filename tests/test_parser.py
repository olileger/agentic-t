"""Tests for agentict.parser."""

from __future__ import annotations

from pathlib import Path

import pytest

from agentict.errors import WatchlistError
from agentict.models import WatchlistEntry
from agentict.parser import parse_watchlist

FIXTURES_DIR = Path(__file__).parent / "fixtures"


def test_valid_watchlist_parses_expected_entries() -> None:
    text = (FIXTURES_DIR / "valid_watchlist.md").read_text(encoding="utf-8")
    entries = parse_watchlist(text)

    assert WatchlistEntry(ticker="AAPL", exchange="NASDAQ") in entries
    assert WatchlistEntry(ticker="MSFT", exchange="NASDAQ") in entries
    assert WatchlistEntry(ticker="GOOGL", exchange="NASDAQ") in entries
    assert WatchlistEntry(ticker="BARC", exchange="LSE") in entries
    assert WatchlistEntry(ticker="GOOGL", exchange="LSE") in entries
    # TSXV has zero tickers -> contributes no entries, and is not an error.
    assert all(entry.exchange != "TSXV" for entry in entries)


def test_in_section_duplicate_tickers_collapse_to_one_entry() -> None:
    text = (FIXTURES_DIR / "valid_watchlist.md").read_text(encoding="utf-8")
    entries = parse_watchlist(text)

    nasdaq_aapl = [e for e in entries if e.ticker == "AAPL" and e.exchange == "NASDAQ"]
    assert len(nasdaq_aapl) == 1


def test_cross_exchange_duplicate_ticker_appears_once_per_exchange() -> None:
    text = (FIXTURES_DIR / "valid_watchlist.md").read_text(encoding="utf-8")
    entries = parse_watchlist(text)

    googl_entries = [e for e in entries if e.ticker == "GOOGL"]
    assert len(googl_entries) == 2
    assert {e.exchange for e in googl_entries} == {"NASDAQ", "LSE"}


def test_zero_ticker_exchange_section_is_valid() -> None:
    text = """# Stock exchange
NASDAQ

# Tickers
- AAPL

# Stock exchange
TSXV

# Tickers
"""
    entries = parse_watchlist(text)
    assert entries == [WatchlistEntry(ticker="AAPL", exchange="NASDAQ")]


def test_missing_stock_exchange_heading_entirely_raises() -> None:
    text = """# Tickers
- AAPL
"""
    with pytest.raises(WatchlistError):
        parse_watchlist(text)


def test_missing_tickers_heading_entirely_raises() -> None:
    text = (FIXTURES_DIR / "malformed_watchlist.md").read_text(encoding="utf-8")
    with pytest.raises(WatchlistError):
        parse_watchlist(text)


def test_stock_exchange_block_without_tickers_before_next_exchange_raises() -> None:
    text = """# Stock exchange
NASDAQ

# Stock exchange
LSE

# Tickers
- BARC
"""
    with pytest.raises(WatchlistError):
        parse_watchlist(text)


def test_stock_exchange_block_without_tickers_before_eof_raises() -> None:
    text = """# Stock exchange
NASDAQ
"""
    with pytest.raises(WatchlistError):
        parse_watchlist(text)


def test_tickers_block_before_any_stock_exchange_heading_raises() -> None:
    text = """# Tickers
- AAPL

# Stock exchange
NASDAQ

# Tickers
- MSFT
"""
    with pytest.raises(WatchlistError):
        parse_watchlist(text)


def test_stock_exchange_heading_without_following_name_line_raises() -> None:
    text = """# Stock exchange
# Tickers
- AAPL
"""
    with pytest.raises(WatchlistError):
        parse_watchlist(text)


def test_completely_empty_file_raises_watchlist_error() -> None:
    with pytest.raises(WatchlistError):
        parse_watchlist("")


def test_whitespace_only_file_raises_watchlist_error() -> None:
    with pytest.raises(WatchlistError):
        parse_watchlist("   \n\n\t\n")


def test_whitespace_only_bullet_line_is_skipped_not_a_ticker() -> None:
    text = """# Stock exchange
NASDAQ

# Tickers
- AAPL
-
-   
"""
    entries = parse_watchlist(text)
    assert entries == [WatchlistEntry(ticker="AAPL", exchange="NASDAQ")]


def test_mixed_dash_and_asterisk_bullet_styles_both_parse() -> None:
    text = """# Stock exchange
NASDAQ

# Tickers
- AAPL
* MSFT
"""
    entries = parse_watchlist(text)
    assert set(entries) == {
        WatchlistEntry(ticker="AAPL", exchange="NASDAQ"),
        WatchlistEntry(ticker="MSFT", exchange="NASDAQ"),
    }


def test_unicode_ticker_and_exchange_names_round_trip() -> None:
    text = """# Stock exchange
Börse Frankfurt

# Tickers
- 東証１
"""
    entries = parse_watchlist(text)
    assert entries == [WatchlistEntry(ticker="東証１", exchange="Börse Frankfurt")]


def test_non_bullet_text_after_tickers_heading_implicitly_ends_ticker_list() -> None:
    text = """# Stock exchange
NASDAQ

# Tickers
- AAPL
Some free-form note that is not a bullet item
- MSFT
"""
    entries = parse_watchlist(text)
    # Parsing stops consuming ticker items at the first non-bullet content;
    # the "- MSFT" line after the free-form note is never reached as a
    # ticker item for this block.
    assert entries == [WatchlistEntry(ticker="AAPL", exchange="NASDAQ")]


def test_large_adversarial_watchlist_parses_in_bounded_time() -> None:
    """Security regression: a large/pathological watchlist must not cause
    unbounded runtime or memory blowup (e.g. from quadratic/backtracking
    parsing behavior). The parser only does linear scans/string ops (no
    regex), so this is primarily a guardrail against future regressions.
    """
    import time

    # Many repeated blank-ish/noise lines interleaved with a huge ticker
    # list, well beyond any realistic watchlist size.
    noise_lines = ["   " for _ in range(5000)]
    ticker_lines = [f"- TCK{i}" for i in range(20000)]
    text = (
        "# Stock exchange\n"
        + "NASDAQ\n"
        + "\n".join(noise_lines)
        + "\n# Tickers\n"
        + "\n".join(ticker_lines)
        + "\n"
    )

    start = time.monotonic()
    entries = parse_watchlist(text)
    elapsed = time.monotonic() - start

    assert len(entries) == 20000
    assert elapsed < 5.0
