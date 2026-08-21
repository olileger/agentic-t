"""Generic web-search-style signal collector.

This is a simple stand-in for a real news/web-search integration (e.g. a
search API). It performs a single HTTP GET against a configurable search
endpoint and treats the response body text as raw, uncategorized PESTLE
signal content. PESTLE categorization of the returned text happens later,
during aggregation in the orchestrator/agent layer, not here.
"""

from __future__ import annotations

import requests

from ..errors import SourceError
from ..models import RawSignal
from ._http import read_bounded_text

_DEFAULT_TIMEOUT_SECONDS = 5
_DEFAULT_ENDPOINT = "https://duckduckgo.com/html/"


class WebSearchSource:
    """Collects freeform web-search snippets mentioning a ticker/exchange."""

    name = "web_search"

    def __init__(
        self,
        endpoint: str = _DEFAULT_ENDPOINT,
        timeout_seconds: float = _DEFAULT_TIMEOUT_SECONDS,
    ) -> None:
        self._endpoint = endpoint
        self._timeout_seconds = timeout_seconds

    def fetch(self, ticker: str, exchange: str) -> RawSignal:
        query = f"{ticker} {exchange} stock news outlook"
        try:
            response = requests.get(
                self._endpoint,
                params={"q": query},
                timeout=self._timeout_seconds,
                headers={"User-Agent": "agentict/0.1 (+one-time signal scan)"},
                stream=True,
            )
            response.raise_for_status()
            try:
                text = read_bounded_text(response)
            finally:
                response.close()
        except requests.RequestException as exc:
            raise SourceError(
                f"{self.name}: request failed for {ticker} ({exchange}): {exc}"
            ) from exc
        except ValueError as exc:
            raise SourceError(
                f"{self.name}: response too large for {ticker} ({exchange}): {exc}"
            ) from exc
        except Exception as exc:  # noqa: BLE001 - collector boundary; must not leak
            raise SourceError(
                f"{self.name}: unexpected failure for {ticker} ({exchange}): {exc}"
            ) from exc

        if not text.strip():
            raise SourceError(f"{self.name}: empty response for {ticker} ({exchange})")

        return RawSignal(source_name=self.name, text=text)
