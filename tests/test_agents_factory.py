"""Tests for agentict.agents.factory (analyst selection)."""

from __future__ import annotations

import pytest

from agentict.agents.factory import get_financial_analyst
from agentict.agents.heuristic import HeuristicFinancialAnalyst
from agentict.errors import AnalystConfigurationError


def test_default_analyst_is_heuristic_when_nothing_specified(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.delenv("AGENTICT_ANALYST", raising=False)
    analyst = get_financial_analyst(None)
    assert isinstance(analyst, HeuristicFinancialAnalyst)


def test_explicit_heuristic_name_selects_heuristic() -> None:
    analyst = get_financial_analyst("heuristic")
    assert isinstance(analyst, HeuristicFinancialAnalyst)


def test_explicit_name_takes_priority_over_environment_variable(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("AGENTICT_ANALYST", "does-not-exist")
    analyst = get_financial_analyst("heuristic")
    assert isinstance(analyst, HeuristicFinancialAnalyst)


def test_environment_variable_used_when_name_not_given(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("AGENTICT_ANALYST", "heuristic")
    analyst = get_financial_analyst(None)
    assert isinstance(analyst, HeuristicFinancialAnalyst)


def test_analyst_name_is_case_insensitive_and_trimmed() -> None:
    analyst = get_financial_analyst("  Heuristic  ")
    assert isinstance(analyst, HeuristicFinancialAnalyst)


def test_unknown_analyst_name_raises_configuration_error() -> None:
    with pytest.raises(AnalystConfigurationError):
        get_financial_analyst("not-a-real-analyst")


def test_unknown_environment_variable_value_raises_configuration_error(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("AGENTICT_ANALYST", "not-a-real-analyst")
    with pytest.raises(AnalystConfigurationError):
        get_financial_analyst(None)


def test_llm_analyst_selectable_but_unconfigured_by_default() -> None:
    """The llm analyst can be constructed but raises on use (no SDK wired in)."""
    from agentict.models import PestleSignals

    analyst = get_financial_analyst("llm")
    with pytest.raises(AnalystConfigurationError):
        analyst.assess("AAPL", "NASDAQ", PestleSignals(economic="growth"))
