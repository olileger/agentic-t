"""Renders a plain-text report table from :class:`ReportRow` results."""

from __future__ import annotations

from .disclaimer import DISCLAIMER
from .models import ReportRow

_COLUMNS = ("Ticker", "Exchange", "Verdict", "Reason")


def render_report(rows: list[ReportRow]) -> str:
    """Render ``rows`` as a plain-text table, preceded by the disclaimer.

    One row is rendered per (ticker, exchange) pair. Exchanges with zero
    tickers contribute no rows and are simply absent from the table.
    """
    lines: list[str] = [DISCLAIMER, ""]

    table_rows = [
        (row.ticker, row.exchange, row.verdict_text, row.reason) for row in rows
    ]
    widths = [
        max(len(_COLUMNS[i]), *(len(row[i]) for row in table_rows)) if table_rows else len(_COLUMNS[i])
        for i in range(len(_COLUMNS))
    ]

    def format_row(values: tuple[str, str, str, str]) -> str:
        return " | ".join(value.ljust(widths[i]) for i, value in enumerate(values))

    lines.append(format_row(_COLUMNS))
    lines.append("-+-".join("-" * width for width in widths))
    for row in table_rows:
        lines.append(format_row(row))

    if not table_rows:
        lines.append("(no tickers in watchlist)")

    return "\n".join(lines) + "\n"
