"""Certifier (L3) — issue + verify certificates. Enforces A-1, A-2, A-3.

Issuance requires a registered, READY module whose backing DOI is gate-passed (A-1).
Verification performs the three-part check (A-2): backing resolves, deterministic
recompute reproduces the values, signature verifies, and input hashes match.
"""

from __future__ import annotations

import secrets
from dataclasses import asdict
from typing import Optional

from runtime.module import Module, CertifyBlocked
from runtime.provenance import hash_inputs
from runtime.canon_resolver import CanonResolver
from .attestation import Signer, HmacSigner
from .claim import Claim, Certificate
from .registry import CertificateRegistry
from .standard import STANDARD


class Certifier:
    def __init__(self, resolver: Optional[CanonResolver] = None,
                 signer: Optional[Signer] = None,
                 registry: Optional[CertificateRegistry] = None):
        self.resolver = resolver or CanonResolver()
        self.signer = signer or HmacSigner()
        self.registry = registry or CertificateRegistry()

    # --- issue ------------------------------------------------------------
    def issue(self, module: Module, subject: str, inputs: dict) -> Certificate:
        # A-3: BLOCKED modules cannot certify (raises CertifyBlocked).
        out = module.certifiable_output(inputs)
        # A-1: backing DOI must resolve to a gate-passed canon entry.
        if not self.resolver.is_gate_passed(out.provenance.backing_doi):
            raise CertifyBlocked(
                f"backing DOI '{out.provenance.backing_doi}' is not a gate-passed canon entry (A-1)"
            )
        claim = Claim(
            subject=subject, module_id=module.id, values=out.values, units=out.units,
            backing_doi=out.provenance.backing_doi, lean_module=out.provenance.lean_module,
            input_hashes=out.provenance.input_hashes, timestamp=out.provenance.timestamp,
        )
        signature = self.signer.sign(claim.payload_bytes())
        cert = Certificate(
            claim=claim, signature=signature, key_id=self.signer.key_id,
            standard_id=STANDARD["id"], certificate_id=secrets.token_hex(16),
        )
        self.registry.record(cert)
        return cert

    # --- verify (three-part check, A-2) -----------------------------------
    def verify(self, certificate: Certificate, module: Module, inputs: dict) -> bool:
        c = certificate.claim
        if self.registry.is_revoked(certificate.certificate_id):
            return False
        # (a) backing resolves to a gate-passed canon entry
        if not self.resolver.is_gate_passed(c.backing_doi):
            return False
        # (c) input hashes match the supplied inputs
        if hash_inputs(inputs) != c.input_hashes:
            return False
        # (b) deterministic recompute reproduces the certified values...
        recomputed = module.compute(inputs)
        if recomputed != c.values:
            return False
        # ...and the signature verifies over the canonical claim payload
        return self.signer.verify(c.payload_bytes(), certificate.signature)

    def revoke(self, certificate_id: str, reason: str = "") -> None:
        self.registry.revoke(certificate_id, reason)
