"""Certificate registry (L3) — record + revoke.

In-memory + optional JSON persistence now; swaps to the DATA plane later (same interface).
Revocation exists so a certificate whose backing theorem is later weakened can be invalidated.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Optional


class CertificateRegistry:
    def __init__(self, store_path: Optional[Path] = None):
        self._certs: dict[str, dict] = {}
        self._revoked: dict[str, str] = {}
        self._store_path = store_path
        if store_path and store_path.exists():
            data = json.loads(store_path.read_text(encoding="utf-8"))
            self._certs = data.get("certs", {})
            self._revoked = data.get("revoked", {})

    def record(self, certificate) -> None:
        self._certs[certificate.certificate_id] = certificate.to_dict()
        self._persist()

    def is_revoked(self, certificate_id: str) -> bool:
        return certificate_id in self._revoked

    def revoke(self, certificate_id: str, reason: str = "") -> None:
        self._revoked[certificate_id] = reason
        self._persist()

    def get(self, certificate_id: str) -> Optional[dict]:
        return self._certs.get(certificate_id)

    def _persist(self) -> None:
        if not self._store_path:
            return
        self._store_path.write_text(
            json.dumps({"certs": self._certs, "revoked": self._revoked}, indent=2),
            encoding="utf-8",
        )
