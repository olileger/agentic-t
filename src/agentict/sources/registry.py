"""Registry of enabled signal source collectors.

A simple, explicit list — no plugin discovery magic. The orchestrator wires
against this list. Add or remove collector instances here to change what is
enabled at runtime.
"""

from __future__ import annotations

from .base import SignalSource
from .google_search import WebSearchSource
from .yahoo_finance import YahooFinanceSource


def enabled_sources() -> list[SignalSource]:
    """Return freshly constructed instances of all enabled sources.

    A factory function (rather than a module-level singleton list) avoids
    accidental shared mutable state between callers/tests.
    """
    return [WebSearchSource(), YahooFinanceSource()]
