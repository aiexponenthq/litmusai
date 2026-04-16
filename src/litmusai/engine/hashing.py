"""RFC 8785 JSON canonicalisation + SHA-256 hashing — FR-19, NFR-7."""

from __future__ import annotations

import hashlib
import json
from typing import Any


def canonical_json(obj: Any) -> str:
    """Produce RFC 8785 canonical JSON: sorted keys, no whitespace, UTF-8."""
    return json.dumps(obj, sort_keys=True, ensure_ascii=False, separators=(",", ":"))


def sha256_hash(obj: Any) -> str:
    """SHA-256 hex digest of the RFC 8785 canonical form of `obj`."""
    return hashlib.sha256(canonical_json(obj).encode("utf-8")).hexdigest()
