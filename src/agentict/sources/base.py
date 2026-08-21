"""Signal source protocol used by all collector implementations."""

from __future__ import annotations

from typing import Protocol, runtime_checkable

from ..models import RawSignal


@runtime_checkable
class SignalSource(Protocol):
    """A pluggable collector that fetches raw PESTLE-relevant signal text.

    Implementations must never let an underlying exception (network error,
    timeout, HTTP error, parsing error, etc.) escape ``fetch``. Any failure
    must be caught and re-raised as :class:`agentict.errors.SourceError`.
    """

    name: str

    def fetch(self, ticker: str, exchange: str) -> RawSignal:
        """Fetch a raw signal for ``ticker`` listed on ``exchange``.

        Raises:
            agentict.errors.SourceError: if no usable signal could be
                retrieved for any reason.
        """
        ...
