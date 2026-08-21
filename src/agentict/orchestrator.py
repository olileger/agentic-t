"""Per-(ticker, exchange) pipeline: dedup handling, source fan-out, agent call."""

from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass

from .agents.base import FinancialAnalyst
from .errors import SourceError
from .models import PestleSignals, RawSignal, ReportRow, Verdict, WatchlistEntry
from .sources.base import SignalSource

_DUPLICATE_REASON_TEMPLATE = (
    "duplicate across exchanges: '{ticker}' appears under {count} '# Stock "
    "exchange' sections; skipping signal collection for this row"
)


@dataclass
class OrchestratorResult:
    """Full outcome of running the pipeline over a parsed watchlist."""

    rows: list[ReportRow]


def build_report_rows(
    entries: list[WatchlistEntry],
    sources: list[SignalSource],
    analyst: FinancialAnalyst,
    max_workers: int = 4,
) -> list[ReportRow]:
    """Build one :class:`ReportRow` per watchlist entry.

    Cross-exchange duplicate tickers (the same ticker string listed under
    two or more different exchanges) are forced to ``NO_DATA`` with a
    distinguishing reason and MUST NOT trigger signal collection or an
    analyst call (BR-10/AC-8). All other entries are processed normally:
    every enabled source is queried, per-source failures are tolerated, and
    only a total failure across all sources forces ``NO_DATA`` (BR-7/BR-8).
    """
    # A ticker only counts as a cross-exchange duplicate if it appears under
    # more than one *distinct* exchange (in-section dedup already collapsed
    # same-exchange repeats upstream in the parser).
    tickers_per_exchange_set: dict[str, set[str]] = {}
    for entry in entries:
        tickers_per_exchange_set.setdefault(entry.ticker, set()).add(entry.exchange)
    duplicate_tickers = {
        ticker for ticker, exchanges in tickers_per_exchange_set.items() if len(exchanges) > 1
    }

    rows: list[ReportRow] = [None] * len(entries)  # type: ignore[list-item]
    normal_indices: list[int] = []

    for index, entry in enumerate(entries):
        if not entry.exchange:
            rows[index] = ReportRow(
                ticker=entry.ticker,
                exchange=entry.exchange,
                verdict=Verdict.NO_DATA,
                reason="exchange could not be determined for this entry",
            )
            continue

        if entry.ticker in duplicate_tickers:
            rows[index] = ReportRow(
                ticker=entry.ticker,
                exchange=entry.exchange,
                verdict=Verdict.NO_DATA,
                reason=_DUPLICATE_REASON_TEMPLATE.format(
                    ticker=entry.ticker,
                    count=len(tickers_per_exchange_set[entry.ticker]),
                ),
            )
            continue

        normal_indices.append(index)

    if normal_indices:
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = {
                index: executor.submit(
                    _assess_entry, entries[index], sources, analyst
                )
                for index in normal_indices
            }
            for index, future in futures.items():
                rows[index] = future.result()

    return rows


def _assess_entry(
    entry: WatchlistEntry,
    sources: list[SignalSource],
    analyst: FinancialAnalyst,
) -> ReportRow:
    signals_collected: list[RawSignal] = []
    for source in sources:
        try:
            signal = source.fetch(entry.ticker, entry.exchange)
        except SourceError:
            continue
        if signal is not None and signal.text.strip():
            signals_collected.append(signal)

    if not signals_collected:
        return ReportRow(
            ticker=entry.ticker,
            exchange=entry.exchange,
            verdict=Verdict.NO_DATA,
            reason="all signal sources failed or returned no usable data",
        )

    pestle_signals = _aggregate_signals(signals_collected)
    result = analyst.assess(entry.ticker, entry.exchange, pestle_signals)
    return ReportRow(
        ticker=entry.ticker,
        exchange=entry.exchange,
        verdict=result.verdict,
        reason=result.rationale,
    )


def _aggregate_signals(signals: list[RawSignal]) -> PestleSignals:
    """Aggregate raw signal text into PESTLE categories.

    Signals with a known ``category_hint`` are appended to that category;
    all other (uncategorized) signal text is appended to every category so
    the heuristic/LLM agent can still consider it. This keeps collector
    implementations simple (they don't need to classify PESTLE categories
    themselves) while still giving the agent layer full visibility.
    """
    pestle = PestleSignals()
    for signal in signals:
        text = signal.text.strip()
        if not text:
            continue
        if signal.category_hint and hasattr(pestle, signal.category_hint):
            current = getattr(pestle, signal.category_hint)
            setattr(pestle, signal.category_hint, f"{current} {text}".strip())
        else:
            for category in pestle.as_dict():
                current = getattr(pestle, category)
                setattr(pestle, category, f"{current} {text}".strip())
    return pestle
