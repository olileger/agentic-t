"""Test doubles for orchestrator tests (no network, no LLM)."""

from __future__ import annotations

from agentict.errors import SourceError
from agentict.models import PestleSignals, RawSignal, Verdict, VerdictResult


class FakeSignalSource:
    """A configurable in-memory signal source for tests."""

    def __init__(self, name: str, text: str | None = None, fail: bool = False) -> None:
        self.name = name
        self._text = text if text is not None else f"{name} default signal text"
        self._fail = fail
        self.calls: list[tuple[str, str]] = []

    def fetch(self, ticker: str, exchange: str) -> RawSignal:
        self.calls.append((ticker, exchange))
        if self._fail:
            raise SourceError(f"{self.name}: simulated failure for {ticker} ({exchange})")
        return RawSignal(source_name=self.name, text=self._text)


class FakeFinancialAnalyst:
    """A configurable Financial Analyst test double."""

    def __init__(self, verdict: Verdict = Verdict.INVEST, rationale: str = "fake rationale") -> None:
        self._verdict = verdict
        self._rationale = rationale
        self.calls: list[tuple[str, str, PestleSignals]] = []

    def assess(self, ticker: str, exchange: str, signals: PestleSignals) -> VerdictResult:
        self.calls.append((ticker, exchange, signals))
        return VerdictResult(verdict=self._verdict, rationale=self._rationale)
