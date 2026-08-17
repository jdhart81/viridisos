"""The ViridisOS Certification Standard v1 (machine-readable spec).

A registry/insurer/auditor can require conformance to this standard as a line item.
It names the required certificate fields and the check that makes a certificate valid.
"""

from __future__ import annotations

STANDARD = {
    "id": "viridisos-certification-v1",
    "version": "1.0.0",
    "title": "ViridisOS Certification Standard",
    "summary": (
        "A conservation claim is ViridisOS-certified iff it is produced by a registered "
        "module whose core result is a gate-passed canon theorem, signed over canonical "
        "inputs, and independently recomputable."
    ),
    "required_certificate_fields": [
        "claim.subject", "claim.module_id", "claim.values", "claim.backing_doi",
        "claim.lean_module", "claim.input_hashes", "claim.timestamp",
        "signature", "key_id", "standard_id", "certificate_id",
    ],
    "validity_check": [
        "A-1: claim.backing_doi resolves to a gate-passed canon entry",
        "A-2: recomputing the module output from the same inputs reproduces claim.values, "
        "and the signature verifies over the canonical claim payload",
        "input hashes match the recorded inputs",
        "certificate is not revoked",
    ],
    "backing_families": ["D-Capital Valuation", "Monitoring/MRV", "Restoration", "Stewardship"],
}
