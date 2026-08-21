"""Shared bounded-read helper for HTTP-based signal source collectors.

Both collectors read a response body from an external, untrusted network
endpoint. Without a cap, a malicious/compromised server (or an on-path/DNS
attacker impersonating a configured endpoint) could return an arbitrarily
large or unbounded (e.g. chunked, never-ending) response body and exhaust
process memory in this single-process CLI. ``read_bounded_text`` enforces a
hard cap while streaming, independent of any (attacker-controlled)
``Content-Length`` header.
"""

from __future__ import annotations

import requests

#: Generous but bounded cap for a single collector response. Search-result
#: HTML pages and quote JSON payloads are normally well under this size;
#: this exists purely as a DoS backstop, not a functional limit.
MAX_RESPONSE_BYTES = 2_000_000


def read_bounded_text(response: requests.Response, max_bytes: int = MAX_RESPONSE_BYTES) -> str:
    """Read ``response`` body up to ``max_bytes``, raising if it is exceeded.

    Streams the body in chunks rather than trusting ``Content-Length`` (which
    is attacker-controlled and may be absent or wrong), so an oversized body
    is detected and aborted without buffering it all in memory first.

    Raises:
        ValueError: if the body exceeds ``max_bytes``.
    """
    total = 0
    chunks: list[bytes] = []
    for chunk in response.iter_content(chunk_size=65536):
        if not chunk:
            continue
        total += len(chunk)
        if total > max_bytes:
            raise ValueError(
                f"response body exceeded maximum allowed size of {max_bytes} bytes"
            )
        chunks.append(chunk)

    encoding = response.encoding or "utf-8"
    return b"".join(chunks).decode(encoding, errors="replace")
