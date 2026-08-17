"""Mutualist module tests — kernel correctness + full certify→verify path."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from runtime.canon_resolver import CanonResolver
from certification.certifier import Certifier
from modules.mutualist import MutualistModule
from modules.mutualist import engine
from modules.mutualist.module import SRPT_BACKING

# make the SRPT backing DOI resolve as gate-passed for the test
RESOLVER = CanonResolver(entries={SRPT_BACKING.doi: {"verified": True, "lean_module": "SymbioticRiskPremium"}})


def test_kernel_risk_premium_floor_positive_and_scales():
    # R1: π ≥ ρk_B/Σ ; halving Σ doubles the floor
    a = engine.risk_premium_floor(rho=2.0, sigma=1e-20)
    b = engine.risk_premium_floor(rho=2.0, sigma=5e-21)
    assert a > 0 and b > a


def test_kernel_zero_dissipation_raises():
    try:
        engine.risk_premium_floor(rho=1.0, sigma=0.0)
        assert False, "expected ValueError (zero variance ⇒ Σ→∞)"
    except ValueError:
        pass


def test_kernel_contagion_sign_transition():
    assert engine.contagion_sign(-0.3) == "mutualistic"
    assert engine.contagion_sign(0.3) == "contagious"
    assert engine.contagion_sign(0.0) == "neutral"


def test_kernel_diversification_residual_strictly_positive():
    # R3: undiversifiable residual > 0 at finite Σ_tot
    out = engine.price_portfolio(rho=1.0, sigma=1e-20, sigma_tot=2e-20, r_c=-0.5)
    assert out["undiversifiable"] is True
    assert out["diversification_residual"] > 0


def test_module_certify_ready_with_resolvable_backing():
    m = MutualistModule(resolver=RESOLVER)
    assert m.certify_ready() is True


def test_full_measure_compute_certify_verify_path():
    m = MutualistModule(resolver=RESOLVER)
    c = Certifier(resolver=RESOLVER)
    inputs = {"rho": 1.5, "sigma": 1e-20, "sigma_tot": 3e-20, "r_c": -0.4}
    cert = c.issue(m, subject="portfolio-7", inputs=inputs)
    assert cert.claim.values["contagion_regime"] == "mutualistic"
    assert c.verify(cert, m, inputs) is True


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
