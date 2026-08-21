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
