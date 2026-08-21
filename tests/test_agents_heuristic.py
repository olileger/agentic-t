"""Tests for agentict.agents.heuristic."""

from __future__ import annotations

from agentict.agents.heuristic import HeuristicFinancialAnalyst
from agentict.models import PestleSignals, Verdict


def test_insufficient_categories_returns_no_data() -> None:
    analyst = HeuristicFinancialAnalyst()
    signals = PestleSignals(economic="strong growth and record profit this year")

    result = analyst.assess("AAPL", "NASDAQ", signals)

    assert result.verdict == Verdict.NO_DATA
    assert "PESTLE" in result.rationale


def test_conflicting_signals_return_no_data() -> None:
    analyst = HeuristicFinancialAnalyst()
    signals = PestleSignals(
        economic="strong growth and record profit expected",
        legal="major lawsuit and investigation announced",
    )

    result = analyst.assess("AAPL", "NASDAQ", signals)

    assert result.verdict == Verdict.NO_DATA
    assert "conflicting" in result.rationale


def test_clear_positive_signals_return_invest() -> None:
    analyst = HeuristicFinancialAnalyst()
    signals = PestleSignals(
        economic="strong growth and record revenue, profitable expansion",
        technological="innovation driving strong demand",
        social="favorable public sentiment and growing loyalty",
    )

    result = analyst.assess("AAPL", "NASDAQ", signals)

    assert result.verdict == Verdict.INVEST


def test_clear_negative_signals_return_not() -> None:
    analyst = HeuristicFinancialAnalyst()
    signals = PestleSignals(
        legal="major lawsuit, investigation, and scandal reported",
        economic="revenue decline and layoffs amid recession fears",
        political="sanctions and instability weigh on outlook",
    )

    result = analyst.assess("AAPL", "NASDAQ", signals)

    assert result.verdict == Verdict.NOT


def test_no_keyword_signal_despite_enough_categories_returns_no_data() -> None:
    analyst = HeuristicFinancialAnalyst()
    signals = PestleSignals(
        economic="quarterly filing published on schedule",
        social="community event took place downtown",
    )

    result = analyst.assess("AAPL", "NASDAQ", signals)

    assert result.verdict == Verdict.NO_DATA
