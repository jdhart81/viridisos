"""Platform assembly tests — catalog registers, states reflect the live canon."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from viridis_platform import build_platform, catalog_status


def test_catalog_registers_all_modules():
    registry, certifier = build_platform()
    ids = {m["id"] for m in registry.list_modules()}
    assert {"mutualist", "restoration", "afforestation", "harmonization", "carbon-continuity"} <= ids


def test_states_reflect_live_canon():
    by_id = {r["id"]: r for r in catalog_status()}
    # published theorems → READY
    assert by_id["restoration"]["state"] == "READY"
    assert by_id["afforestation"]["state"] == "READY"
    assert by_id["harmonization"]["state"] == "READY"
    # SRPT still pending → BLOCKED (A-1 enforced, not configured)
    assert by_id["mutualist"]["state"] == "BLOCKED"
    # Carbon Continuity is Aristotle-audited but not yet published to canon.
    assert by_id["carbon-continuity"]["state"] == "BLOCKED"


def test_blocked_module_cannot_certify_via_platform():
    from runtime.module import CertifyBlocked
    registry, certifier = build_platform()
    mutualist = registry.get("mutualist")
    try:
        certifier.issue(mutualist, subject="p", inputs={"rho": 1, "sigma": 1e-20, "sigma_tot": 2e-20, "r_c": -0.1})
        assert False, "expected CertifyBlocked for pending-backing module"
    except CertifyBlocked:
        pass


def test_carbon_continuity_cannot_certify_before_canon_publication():
    from runtime.module import CertifyBlocked
    registry, certifier = build_platform()
    module = registry.get("carbon-continuity")
    try:
        certifier.issue(
            module,
            subject="project-1",
            inputs={"a": 0.6, "d": 0.8, "r": 0.5, "p": 0.2},
        )
        assert False, "expected CertifyBlocked for unpublished Carbon Continuity paper"
    except CertifyBlocked:
        pass


if __name__ == "__main__":
    import traceback
    fns = [g for n, g in sorted(globals().items()) if n.startswith("test_") and callable(g)]
    p = f = 0
    for fn in fns:
        try:
            fn(); p += 1; print(f"PASS  {fn.__name__}")
        except Exception:
            f += 1; print(f"FAIL  {fn.__name__}"); traceback.print_exc()
    print(f"\n{p} passed, {f} failed")
    raise SystemExit(1 if f else 0)
