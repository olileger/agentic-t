"""Parses watchlist markdown files into validated :class:`WatchlistEntry` lists.

Grammar (see product/tech-lead direction for the authoritative spec)::

    # Stock exchange
    <exchange name, single line, trimmed>

    # Tickers
    - TICKER1
    - TICKER2

A file may contain multiple ``# Stock exchange`` / ``# Tickers`` blocks in
sequence. Each ``# Stock exchange`` heading must be followed (ignoring blank
lines) by exactly one non-empty exchange-name line, and must have exactly one
``# Tickers`` heading associated with it before the next ``# Stock exchange``
heading or end of file.
"""

from __future__ import annotations

from dataclasses import dataclass

from .errors import WatchlistError
from .models import WatchlistEntry

_EXCHANGE_HEADING = "# stock exchange"
_TICKERS_HEADING = "# tickers"


@dataclass
class _Block:
    exchange: str
    tickers: list[str]


def parse_watchlist(text: str) -> list[WatchlistEntry]:
    """Parse watchlist markdown text into a de-duplicated entry list.

    In-section duplicate tickers (exact, case-sensitive match after trim)
    collapse into a single entry. Tickers appearing under two or more
    different exchange blocks are NOT deduplicated here: the caller
    (orchestrator) is responsible for detecting and handling cross-exchange
    duplicates, since that requires cross-block visibility this function
    intentionally does not hide.

    Raises:
        WatchlistError: if the file does not conform to the grammar.
    """
    lines = text.splitlines()
    blocks = _parse_blocks(lines)
    if not blocks:
        raise WatchlistError(
            "Watchlist file must contain at least one '# Stock exchange' section."
        )

    entries: list[WatchlistEntry] = []
    for block in blocks:
        seen: set[str] = set()
        for ticker in block.tickers:
            if ticker in seen:
                continue
            seen.add(ticker)
            entries.append(WatchlistEntry(ticker=ticker, exchange=block.exchange))
    return entries


def _normalize(line: str) -> str:
    return line.strip().lower()


def _parse_blocks(lines: list[str]) -> list[_Block]:
    saw_exchange_heading = False
    saw_tickers_heading = False
    blocks: list[_Block] = []

    index = 0
    total = len(lines)

    while index < total:
        raw_line = lines[index]
        normalized = _normalize(raw_line)

        if normalized == _TICKERS_HEADING and not saw_exchange_heading:
            raise WatchlistError(
                "'# Tickers' heading found before any '# Stock exchange' heading."
            )

        if normalized == _EXCHANGE_HEADING:
            saw_exchange_heading = True
            exchange_name, index = _read_exchange_name(lines, index + 1)
            tickers, has_tickers_block, index = _read_tickers_block(lines, index)
            if not has_tickers_block:
                raise WatchlistError(
                    f"'# Stock exchange' section for '{exchange_name}' is missing "
                    "its required '# Tickers' heading."
                )
            saw_tickers_heading = True
            blocks.append(_Block(exchange=exchange_name, tickers=tickers))
            continue

        index += 1

    if not saw_exchange_heading:
        raise WatchlistError("Watchlist file is missing a '# Stock exchange' heading.")
    if not saw_tickers_heading:
        raise WatchlistError("Watchlist file is missing a '# Tickers' heading.")

    return blocks


def _read_exchange_name(lines: list[str], start: int) -> tuple[str, int]:
    """Read the single non-empty exchange-name line following the heading."""
    index = start
    total = len(lines)
    while index < total and lines[index].strip() == "":
        index += 1
    if index >= total or _normalize(lines[index]) in (_EXCHANGE_HEADING, _TICKERS_HEADING):
        raise WatchlistError(
            "'# Stock exchange' heading must be immediately followed by a "
            "non-empty exchange name line."
        )
    exchange_name = lines[index].strip()
    return exchange_name, index + 1


def _read_tickers_block(lines: list[str], start: int) -> tuple[list[str], bool, int]:
    """Scan forward for the '# Tickers' heading belonging to the current block.

    Returns the parsed ticker list, whether a '# Tickers' heading was found
    before the next '# Stock exchange' heading (or EOF), and the index to
    resume scanning from.
    """
    index = start
    total = len(lines)

    while index < total:
        normalized = _normalize(lines[index])
        if normalized == _EXCHANGE_HEADING:
            return [], False, index
        if normalized == _TICKERS_HEADING:
            return _read_ticker_items(lines, index + 1)
        index += 1

    return [], False, index


def _read_ticker_items(lines: list[str], start: int) -> tuple[list[str], bool, int]:
    tickers: list[str] = []
    index = start
    total = len(lines)

    while index < total:
        stripped = lines[index].strip()
        normalized = _normalize(lines[index])
        if normalized in (_EXCHANGE_HEADING, _TICKERS_HEADING):
            break
        if stripped == "":
            index += 1
            continue
        if stripped.startswith("- ") or stripped.startswith("* "):
            ticker = stripped[2:].strip()
            if ticker:
                tickers.append(ticker)
            index += 1
            continue
        # Any other non-blank, non-list-item content ends the ticker list
        # implicitly; stop consuming it as ticker data.
        break

    return tickers, True, index
