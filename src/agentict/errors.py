"""Domain-specific exceptions for agentict."""

from __future__ import annotations


class AgentictError(Exception):
    """Base class for all agentict domain errors."""


class WatchlistError(AgentictError):
    """Raised when a watchlist markdown file is malformed."""


class SourceError(AgentictError):
    """Raised when a signal source fails to fetch usable data.

    Collectors MUST catch any underlying exception (network, timeout, HTTP,
    parsing, etc.) and re-raise it wrapped as a ``SourceError`` so that no raw
    exception ever escapes a collector implementation.
    """


class AnalystConfigurationError(AgentictError):
    """Raised when a Financial Analyst implementation cannot be constructed.

    For example: an unknown ``AGENTICT_ANALYST`` value, or an LLM-backed
    analyst selected without the required SDK/credentials being available.
    """
