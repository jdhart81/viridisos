"""ViridisOS platform assembly.

(Named `viridis_platform` — NOT `platform` — to avoid shadowing Python's stdlib `platform`.)

Builds the platform against the LIVE canon: registers every catalog module, resolves each
one's backing DOI against `RESEARCH_PIPELINE_v2/canon_fingerprint_index.json`, and exposes
the registry + certifier. Modules backed by a published theorem are READY (can certify);
modules whose theorem is still pending are BLOCKED — enforced, not configured.
"""

from __future__ import annotations

from typing import Optional

from runtime.canon_resolver import CanonResolver
from runtime.registry import ModuleRegistry
from certification.certifier import Certifier
from certification.registry import CertificateRegistry
from certification.attestation import Signer
from catalog import all_module_classes


def build_platform(resolver: Optional[CanonResolver] = None,
                   signer: Optional[Signer] = None) -> tuple[ModuleRegistry, Certifier]:
    """Assemble the platform against the live canon (or an injected resolver for tests)."""
    resolver = resolver or CanonResolver()          # reads the live canon index by default
    registry = ModuleRegistry()
    for cls in all_module_classes():
        registry.register(cls(resolver=resolver))
    certifier = Certifier(resolver=resolver, signer=signer, registry=CertificateRegistry())
    return registry, certifier


def catalog_status(resolver: Optional[CanonResolver] = None) -> list[dict]:
    """Human-readable catalog: module → line → backing DOI → LIVE/BLOCKED."""
    resolver = resolver or CanonResolver()
    rows = []
    for cls in all_module_classes():
        m = cls(resolver=resolver)
        rows.append({
            "id": m.id, "name": m.name, "line": m.line,
            "backing_doi": m.backing.doi, "lean_module": m.backing.lean_module,
            "state": m.state().value,
        })
    return rows


if __name__ == "__main__":
    import json
    print(json.dumps(catalog_status(), indent=2))
