"""Attestation signer interface (L3).

VERIFY (L1) signs a claim so anyone can later check it. Production uses the K3 signer;
here we ship a deterministic HMAC dev implementation behind the same `Signer` interface
so the whole certify→verify flow is testable now. Swap `HmacSigner` for the K3 signer
without touching the certifier — see HANDOFF_NOTES.md.
"""

from __future__ import annotations

import hashlib
import hmac
from typing import Protocol


class Signer(Protocol):
    def sign(self, payload: bytes) -> str: ...
    def verify(self, payload: bytes, signature: str) -> bool: ...
    @property
    def key_id(self) -> str: ...


class HmacSigner:
    """DEV ONLY — deterministic HMAC-SHA256. Not a real K3 attestation. See HANDOFF_NOTES.md."""

    def __init__(self, secret: bytes = b"viridisos-dev-key", key_id: str = "dev-hmac-v0"):
        self._secret = secret
        self._key_id = key_id

    @property
    def key_id(self) -> str:
        return self._key_id

    def sign(self, payload: bytes) -> str:
        return hmac.new(self._secret, payload, hashlib.sha256).hexdigest()

    def verify(self, payload: bytes, signature: str) -> bool:
        return hmac.compare_digest(self.sign(payload), signature)
