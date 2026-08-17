"""Claim + Certificate objects (L3)."""

from __future__ import annotations

from dataclasses import dataclass, asdict, field

from runtime.provenance import canonical


@dataclass(frozen=True)
class Claim:
    subject: str            # parcel / portfolio id the claim is about
    module_id: str
    values: dict            # the module output values
    units: dict
    backing_doi: str
    lean_module: str
    input_hashes: dict
    timestamp: str

    def payload_bytes(self) -> bytes:
        """Canonical, signature-stable byte payload."""
        return canonical(asdict(self)).encode("utf-8")


@dataclass(frozen=True)
class Certificate:
    claim: Claim
    signature: str
    key_id: str
    standard_id: str
    certificate_id: str
    revoked: bool = False

    def to_dict(self) -> dict:
        d = asdict(self)
        return d
