"""Deterministic provenance hashing (invariant A-4) — canonical JSON → sha256.

Determinism is load-bearing: certificates must be independently, bit-identically
recomputable (A-2), which requires that identical inputs always hash identically
regardless of key order or process.
"""

from __future__ import annotations

import hashlib
import json
from typing import Any


def canonical(obj: Any) -> str:
    """Canonical JSON: sorted keys, no whitespace — stable across processes."""
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def sha256_hex(data: str) -> str:
    return hashlib.sha256(data.encode("utf-8")).hexdigest()


def hash_value(value: Any) -> str:
    """Stable sha256 of any JSON-serializable value."""
    return sha256_hex(canonical(value))


def hash_inputs(inputs: dict) -> dict:
    """Per-key input hashes (A-4 provenance)."""
    return {k: hash_value(v) for k, v in sorted(inputs.items())}
