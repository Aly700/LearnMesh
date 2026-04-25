"""HTTP conditional-GET helpers (RFC 7232).

Strong ``ETag`` generation over a deterministic JSON serialization of the
response payload, plus parsing of ``If-None-Match`` and ``If-Modified-Since``
to short-circuit unchanged responses to ``304 Not Modified``.
"""

from __future__ import annotations

import hashlib
import json
from datetime import UTC, datetime
from email.utils import parsedate_to_datetime
from typing import Any

from fastapi import Request


def compute_etag(payload: Any) -> str:
    """Return a strong ``ETag`` (RFC 7232 quoted opaque string) for ``payload``.

    ``payload`` is serialized via ``json.dumps`` with ``sort_keys=True``,
    compact separators, and ``default=str`` to coerce datetimes/enums.
    Hash is SHA-256 truncated to 64 hex chars and wrapped in double quotes.
    """
    serialized = json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
        default=str,
    )
    digest = hashlib.sha256(serialized.encode("utf-8")).hexdigest()
    return f'"{digest}"'


def _strip_weak_prefix(tag: str) -> str:
    return tag[2:] if tag.startswith("W/") else tag


def _parse_if_none_match(header_value: str) -> set[str] | None:
    """Return the set of unquoted entity-tags, ``{"*"}`` for wildcard, or ``None`` if empty."""
    stripped = header_value.strip()
    if not stripped:
        return None
    if stripped == "*":
        return {"*"}
    tags: set[str] = set()
    for raw in stripped.split(","):
        candidate = _strip_weak_prefix(raw.strip())
        if len(candidate) >= 2 and candidate.startswith('"') and candidate.endswith('"'):
            tags.add(candidate[1:-1])
    return tags or None


def not_modified(
    request: Request,
    etag: str,
    last_modified: datetime | None = None,
) -> bool:
    """Return True when the client's cached copy is still fresh.

    Precedence per RFC 7232 §6: ``If-None-Match`` wins when present. A non-matching
    ``If-None-Match`` short-circuits to False without consulting ``If-Modified-Since``.
    Malformed headers are treated as a cache miss (no 4xx).
    """
    inm = request.headers.get("if-none-match")
    if inm is not None:
        tags = _parse_if_none_match(inm)
        if tags is None:
            return False
        if "*" in tags:
            return True
        unquoted = etag[1:-1] if etag.startswith('"') and etag.endswith('"') else etag
        return unquoted in tags

    if last_modified is None:
        return False

    ims = request.headers.get("if-modified-since")
    if ims is None:
        return False

    try:
        client_time = parsedate_to_datetime(ims)
    except (TypeError, ValueError):
        return False
    if client_time is None:
        return False
    if client_time.tzinfo is None:
        client_time = client_time.replace(tzinfo=UTC)

    server_time = last_modified
    if server_time.tzinfo is None:
        server_time = server_time.replace(tzinfo=UTC)

    return server_time.replace(microsecond=0) <= client_time.replace(microsecond=0)
