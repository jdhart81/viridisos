"""API (L4 seam) tests — route dispatch, happy paths, and the blocked 409 path."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from runtime.canon_resolver import CanonResolver
from runtime.registry import ModuleRegistry
from certification.certifier import Certifier
from modules.mutualist import MutualistModule
from modules.mutualist.module import SRPT_BACKING
from api.service import ViridisOSService, dispatch


def _service(backing_ok: bool = True):
    entries = {SRPT_BACKING.doi: {"verified": True, "lean_module": "SymbioticRiskPremium"}} if backing_ok else {}
    resolver = CanonResolver(entries=entries)
    reg = ModuleRegistry()
    reg.register(MutualistModule(resolver=resolver))
    return ViridisOSService(reg, Certifier(resolver=resolver))


INPUTS = {"rho": 1.5, "sigma": 1e-20, "sigma_tot": 3e-20, "r_c": -0.4}


def test_get_modules():
    status, body = dispatch(_service(), "GET", "/modules", None)
    assert status == 200 and body["modules"][0]["id"] == "mutualist"


def test_get_standard():
    status, body = dispatch(_service(), "GET", "/standard", None)
    assert status == 200 and body["id"] == "viridisos-certification-v1"


def test_preview_route():
    status, body = dispatch(_service(), "POST", "/modules/mutualist/preview", {"inputs": INPUTS})
    assert status == 200 and body["values"]["contagion_regime"] == "mutualistic"


def test_certify_then_verify_routes():
    svc = _service()
    s1, cert = dispatch(svc, "POST", "/modules/mutualist/certify", {"subject": "p1", "inputs": INPUTS})
    assert s1 == 200 and cert["certificate_id"]
    s2, res = dispatch(svc, "POST", "/certificates/verify",
                       {"certificate_id": cert["certificate_id"], "module_id": "mutualist", "inputs": INPUTS})
    assert s2 == 200 and res["valid"] is True


def test_certify_blocked_returns_409():
    svc = _service(backing_ok=False)   # SRPT DOI not gate-passed → A-1 blocks
    status, body = dispatch(svc, "POST", "/modules/mutualist/certify", {"subject": "p", "inputs": INPUTS})
    assert status == 409 and body["error"] == "blocked"


def test_unknown_route_404():
    status, _ = dispatch(_service(), "GET", "/nope", None)
    assert status == 404


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
