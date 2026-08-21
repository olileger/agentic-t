"""Deterministic, no-network default Financial Analyst implementation.

IMPORTANT — illustrative heuristic, not a certified scoring formula:
This module implements a simple keyword-polarity tally over aggregated
PESTLE signal text purely as a deterministic, offline stand-in so the CLI
has a working default with no external dependencies. It is NOT intended to
represent real investment analysis or a certified/validated scoring model.
In a production deployment the intent is for verdicts to come from genuine
analyst judgment (e.g. an LLM-backed :class:`agentict.agents.llm.LlmFinancialAnalyst`
or a human), not from a fixed keyword formula.
"""

from __future__ import annotations

from ..models import PESTLE_CATEGORIES, PestleSignals, Verdict, VerdictResult

#: Minimum number of PESTLE categories that must carry usable signal text
#: before the heuristic will attempt a directional verdict at all.
_MIN_CATEGORIES_WITH_SIGNAL = 2

#: When the positive/negative keyword tally is this close (inclusive), the
#: signal is treated as materially conflicting rather than decisive.
_CONFLICT_MARGIN = 1

_POSITIVE_KEYWORDS = (
    "growth",
    "profit",
    "profitable",
    "expansion",
    "record revenue",
    "strong demand",
    "beat expectations",
    "upgrade",
    "innovation",
    "favorable",
    "favourable",
    "surplus",
    "stable regulation",
    "strong",
    "outperform",
    "bullish",
    "gain",
    "growing",
)

_NEGATIVE_KEYWORDS = (
    "lawsuit",
    "recall",
    "decline",
    "loss",
    "layoffs",
    "downgrade",
    "investigation",
    "scandal",
    "fine",
    "penalty",
    "boycott",
    "shortage",
    "instability",
    "unfavorable",
    "unfavourable",
    "weak",
    "bearish",
    "bankruptcy",
    "recession",
    "sanctions",
)


class HeuristicFinancialAnalyst:
    """Default, deterministic, no-network Financial Analyst."""

    def assess(self, ticker: str, exchange: str, signals: PestleSignals) -> VerdictResult:
        usable_categories = signals.non_empty_categories()
        if len(usable_categories) < _MIN_CATEGORIES_WITH_SIGNAL:
            return VerdictResult(
                verdict=Verdict.NO_DATA,
                rationale=(
                    f"Only {len(usable_categories)} of {len(PESTLE_CATEGORIES)} PESTLE "
                    f"categories have usable signal text for {ticker} ({exchange}); "
                    f"at least {_MIN_CATEGORIES_WITH_SIGNAL} are required."
                ),
            )

        text = signals.combined_text().lower()
        positive_hits = sum(text.count(keyword) for keyword in _POSITIVE_KEYWORDS)
        negative_hits = sum(text.count(keyword) for keyword in _NEGATIVE_KEYWORDS)

        if abs(positive_hits - negative_hits) <= _CONFLICT_MARGIN and (
            positive_hits > 0 or negative_hits > 0
        ):
            return VerdictResult(
                verdict=Verdict.NO_DATA,
                rationale=(
                    f"Signal for {ticker} ({exchange}) is materially conflicting "
                    f"(positive keyword hits={positive_hits}, negative keyword "
                    f"hits={negative_hits}); withholding a directional verdict."
                ),
            )

        if positive_hits == 0 and negative_hits == 0:
            return VerdictResult(
                verdict=Verdict.NO_DATA,
                rationale=(
                    f"No decisive positive or negative keyword signal found for "
                    f"{ticker} ({exchange}) despite {len(usable_categories)} "
                    "populated PESTLE categories."
                ),
            )

        if positive_hits > negative_hits:
            return VerdictResult(
                verdict=Verdict.INVEST,
                rationale=(
                    f"Positive keyword signal ({positive_hits}) outweighs negative "
                    f"signal ({negative_hits}) across {len(usable_categories)} PESTLE "
                    f"categories for {ticker} ({exchange})."
                ),
            )

        return VerdictResult(
            verdict=Verdict.NOT,
            rationale=(
                f"Negative keyword signal ({negative_hits}) outweighs positive "
                f"signal ({positive_hits}) across {len(usable_categories)} PESTLE "
                f"categories for {ticker} ({exchange})."
            ),
        )
