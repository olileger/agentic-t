"""Yahoo-Finance-style signal collector.

Fetches a lightweight quote summary for a ticker and turns the raw JSON
payload into a text blob usable as PESTLE-relevant signal input (primarily
economic/financial signal). This uses the unauthenticated public quote
endpoint; any failure (network, timeout, HTTP, malformed JSON) is wrapped as
a :class:`agentict.errors.SourceError`.
"""

from __future__ import annotations

import requests

from ..errors import SourceError
from ..models import RawSignal

_DEFAULT_TIMEOUT_SECONDS = 5
_DEFAULT_ENDPOINT = "https://query1.finance.yahoo.com/v7/finance/quote"


class YahooFinanceSource:
    """Collects a quote summary snippet for a ticker from Yahoo Finance."""

    name = "yahoo_finance"

    def __init__(
        self,
        endpoint: str = _DEFAULT_ENDPOINT,
        timeout_seconds: float = _DEFAULT_TIMEOUT_SECONDS,
    ) -> None:
        self._endpoint = endpoint
        self._timeout_seconds = timeout_seconds

    def fetch(self, ticker: str, exchange: str) -> RawSignal:
        try:
            response = requests.get(
                self._endpoint,
                params={"symbols": ticker},
                timeout=self._timeout_seconds,
                headers={"User-Agent": "agentict/0.1 (+one-time signal scan)"},
            )
            response.raise_for_status()
            payload = response.json()
        except requests.RequestException as exc:
            raise SourceError(
                f"{self.name}: request failed for {ticker} ({exchange}): {exc}"
            ) from exc
        except ValueError as exc:
            raise SourceError(
                f"{self.name}: malformed JSON response for {ticker} ({exchange}): {exc}"
            ) from exc
        except Exception as exc:  # noqa: BLE001 - collector boundary; must not leak
            raise SourceError(
                f"{self.name}: unexpected failure for {ticker} ({exchange}): {exc}"
            ) from exc

        results = payload.get("quoteResponse", {}).get("result", []) if isinstance(payload, dict) else []
        if not results:
            raise SourceError(
                f"{self.name}: no quote data returned for {ticker} ({exchange})"
            )

        quote = results[0]
        summary = (
            f"{quote.get('shortName', ticker)} ({ticker}) on {exchange}: "
            f"price={quote.get('regularMarketPrice')} "
            f"change={quote.get('regularMarketChangePercent')}% "
            f"marketCap={quote.get('marketCap')} "
            f"sector={quote.get('sector', '')}"
        )
        return RawSignal(source_name=self.name, text=summary, category_hint="economic")
