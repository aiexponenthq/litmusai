"""RFC 8785 JSON canonicalisation + SHA-256 hashing — FR-19, NFR-7."""

from __future__ import annotations

import hashlib
import json
from datetime import date, datetime
from typing import Any


def _default(obj: Any) -> Any:
    """Coerce types `json` does not know about into stable string forms.

    `date` and `datetime` get ISO-8601 strings — both round-trip-safe and
    canonical. Pydantic's `SystemDescription.metadata.last_reviewed` field
    is typed as `date`, so any input file that populates it lands here.
    """
    if isinstance(obj, datetime):
        return obj.isoformat()
    if isinstance(obj, date):
        return obj.isoformat()
    msg = f"Object of type {obj.__class__.__name__} is not JSON serializable"
    raise TypeError(msg)


def canonical_json(obj: Any) -> str:
    """Produce RFC 8785 canonical JSON: sorted keys, no whitespace, UTF-8."""
    return json.dumps(
        obj,
        sort_keys=True,
        ensure_ascii=False,
        separators=(",", ":"),
        default=_default,
    )


def sha256_hash(obj: Any) -> str:
    """SHA-256 hex digest of the RFC 8785 canonical form of `obj`."""
    return hashlib.sha256(canonical_json(obj).encode("utf-8")).hexdigest()
