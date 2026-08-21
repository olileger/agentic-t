"""Selects a Financial Analyst implementation by name or environment.

Reads ``AGENTICT_ANALYST`` (values: ``heuristic`` | ``llm``) when ``name`` is
not passed explicitly. Defaults to ``heuristic``.
"""

from __future__ import annotations

import os

from ..errors import AnalystConfigurationError
from .base import FinancialAnalyst
from .heuristic import HeuristicFinancialAnalyst

_ENV_VAR = "AGENTICT_ANALYST"
_DEFAULT_ANALYST = "heuristic"


def get_financial_analyst(name: str | None = None) -> FinancialAnalyst:
    """Construct the selected :class:`FinancialAnalyst` implementation.

    Args:
        name: Explicit analyst name (``"heuristic"`` or ``"llm"``). When
            ``None``, falls back to the ``AGENTICT_ANALYST`` environment
            variable, and then to ``"heuristic"``.

    Raises:
        AnalystConfigurationError: if ``name`` (or the environment variable)
            is set to an unrecognized value.
    """
    selected = (name or os.environ.get(_ENV_VAR) or _DEFAULT_ANALYST).strip().lower()

    if selected == "heuristic":
        return HeuristicFinancialAnalyst()

    if selected == "llm":
        # Imported lazily here (rather than at module top) purely to keep
        # the dependency direction obvious; agents.llm itself already lazily
        # imports any real SDK, so this import is always safe.
        from .llm import LlmFinancialAnalyst

        return LlmFinancialAnalyst()

    raise AnalystConfigurationError(
        f"Unknown AGENTICT_ANALYST/--analyst value: '{selected}'. "
        "Valid options are: 'heuristic', 'llm'."
    )
