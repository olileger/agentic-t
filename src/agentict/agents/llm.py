"""Optional example LLM-backed Financial Analyst implementation.

This module is a documented extension point, not a working LLM
integration. It intentionally does not ship a real LLM SDK dependency:
any SDK import is performed lazily inside :meth:`LlmFinancialAnalyst.assess`
and guarded with ``try/except ImportError`` so that the module can always be
imported safely (e.g. by :mod:`agentict.agents.factory`) even when no LLM
SDK is installed. It is only ever instantiated when a caller explicitly
selects it (``AGENTICT_ANALYST=llm`` or ``--analyst llm``).

To wire in a real provider:
1. Add the desired SDK to project dependencies (kept optional/extra).
2. Replace the body of ``assess`` with a real prompt/response call using
   ``signals.as_dict()`` as structured PESTLE input.
3. Parse the model response into a :class:`agentict.models.VerdictResult`.
"""

from __future__ import annotations

import os

from ..errors import AnalystConfigurationError
from ..models import PestleSignals, VerdictResult


class LlmFinancialAnalyst:
    """Example extension point for an LLM-backed Financial Analyst.

    Not configured out of the box: calling :meth:`assess` raises
    :class:`agentict.errors.AnalystConfigurationError` unless a real
    provider has been wired in by a future implementer.
    """

    def __init__(self, model: str | None = None) -> None:
        self._model = model or os.environ.get("AGENTICT_LLM_MODEL", "")

    def assess(self, ticker: str, exchange: str, signals: PestleSignals) -> VerdictResult:
        try:
            # Lazy import: replace with the real provider SDK, e.g.:
            #     import openai  # noqa: F401
            # Any ImportError here must not break installation or the
            # default (heuristic) code path/test suite.
            import agentict_llm_provider_placeholder  # type: ignore[import-not-found]  # noqa: F401,E501
        except ImportError as exc:
            raise AnalystConfigurationError(
                "LLM-backed Financial Analyst is not configured: no LLM "
                "provider SDK is installed and no credentials are wired in. "
                "This is a documented extension point (see "
                "agentict/agents/llm.py) — install and configure a real "
                "provider to enable AGENTICT_ANALYST=llm, or use the "
                "default 'heuristic' analyst."
            ) from exc

        raise AnalystConfigurationError(
            "LLM-backed Financial Analyst has no provider wired in yet."
        )
