"""Core data models shared across agentict modules."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class Verdict(Enum):
    """Investment verdict produced by a Financial Analyst.

    Values map exactly to the strings rendered in the report table.
    """

    INVEST = "Invest"
    NOT = "Not"
    NO_DATA = "no data available"


#: The six PESTLE analysis categories.
PESTLE_CATEGORIES: tuple[str, ...] = (
    "political",
    "economic",
    "social",
    "technological",
    "legal",
    "environmental",
)


@dataclass(frozen=True)
class WatchlistEntry:
    """A single (ticker, exchange) pair parsed from a watchlist file."""

    ticker: str
    exchange: str


@dataclass
class PestleSignals:
    """Aggregated raw text collected per PESTLE category for one ticker.

    Each category maps to a single concatenated text blob built from all
    signal sources that contributed content relevant to that category. An
    empty string means no usable signal was collected for that category.

    ``uncategorized`` holds text from sources that did not provide a
    recognized ``category_hint``. It is intentionally excluded from
    :meth:`non_empty_categories` (which only counts genuine PESTLE category
    coverage) so a single uncategorized source cannot, by itself, satisfy a
    "signal spans multiple PESTLE categories" requirement. It is still
    included (once) in :meth:`combined_text` so heuristics/agents can
    consider it as general context.
    """

    political: str = ""
    economic: str = ""
    social: str = ""
    technological: str = ""
    legal: str = ""
    environmental: str = ""
    uncategorized: str = ""

    def as_dict(self) -> dict[str, str]:
        return {
            "political": self.political,
            "economic": self.economic,
            "social": self.social,
            "technological": self.technological,
            "legal": self.legal,
            "environmental": self.environmental,
        }

    def non_empty_categories(self) -> list[str]:
        """Return the names of PESTLE categories with non-blank signal text.

        Deliberately excludes ``uncategorized`` text.
        """
        return [name for name, text in self.as_dict().items() if text.strip()]

    def combined_text(self) -> str:
        """Return all category text (including uncategorized) concatenated
        once each, for simple heuristics."""
        parts = [text for text in self.as_dict().values() if text.strip()]
        if self.uncategorized.strip():
            parts.append(self.uncategorized)
        return " ".join(parts)


@dataclass
class VerdictResult:
    """Result returned by a Financial Analyst assessment."""

    verdict: Verdict
    rationale: str


@dataclass
class RawSignal:
    """Raw content returned by a single signal source for one ticker."""

    source_name: str
    text: str
    category_hint: str | None = None


@dataclass
class ReportRow:
    """One row of the final rendered report."""

    ticker: str
    exchange: str
    verdict: Verdict
    reason: str = ""

    @property
    def verdict_text(self) -> str:
        return self.verdict.value
