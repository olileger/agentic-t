"""Financial Analyst protocol shared by all agent implementations."""

from __future__ import annotations

from typing import Protocol, runtime_checkable

from ..models import PestleSignals, VerdictResult


@runtime_checkable
class FinancialAnalyst(Protocol):
    """Produces an investment verdict from aggregated PESTLE signals."""

    def assess(self, ticker: str, exchange: str, signals: PestleSignals) -> VerdictResult:
        """Assess ``ticker``/``exchange`` given aggregated PESTLE signal text.

        Implementations must be total: they must always return a
        :class:`VerdictResult` and never raise for merely weak/absent
        signal data (that case should resolve to ``Verdict.NO_DATA``).
        """
        ...
