"""Live-backed module tests — kernels + certification against the REAL canon index.

These modules are backed by PUBLISHED theorems (FNT/AST/GHT), so a plain CanonResolver()
reading RESEARCH_PIPELINE_v2/canon_fingerprint_index.json resolves them as gate-passed and
they certify for real — no fixture needed.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from runtime.canon_resolver import CanonResolver
from certification.certifier import Certifier
from modules.restoration import RestorationModule
from modules.restoration import engine as rest_engine
from modules.afforestation import AfforestationModule
from modules.harmonization import HarmonizationModule
from modules.harmonization import engine as harm_engine

LIVE = CanonResolver()   # reads the live canon index


# --- Restoration / FNT ------------------------------------------------------

def test_restoration_broadcast_fails_above_threshold():
    hi = rest_engine.design(sigma=2.0, delta_mu=1.0)   # Θ=2 → RED
    lo = rest_engine.design(sigma=0.3, delta_mu=1.0)   # Θ=0.3 → GREEN
    assert hi["recommendation"] == "RED" and hi["broadcast_fails"] is True
    assert lo["recommendation"] == "GREEN" and lo["broadcast_fails"] is False


def test_restoration_certifies_live_against_real_canon():
    m = RestorationModule(resolver=LIVE)
    assert m.state().value == "READY"           # FNT DOI 20982979 is in the canon index
    c = Certifier(resolver=LIVE)
    inputs = {"sigma": 1.5, "delta_mu": 1.0}
    cert = c.issue(m, subject="site-9", inputs=inputs)
    assert cert.claim.backing_doi == "10.5281/zenodo.20982979"
    assert c.verify(cert, m, inputs) is True


# --- Afforestation / AST ----------------------------------------------------

def test_afforestation_site_prep_cubic_lever():
    m = AfforestationModule(resolver=LIVE)
    out = m.preview({"sigma": 1.0, "delta_mu": 1.0, "prep": 2.0, "rate": 0.5, "rate_max": 1.0})
    assert out.values["site_prep_multiplier"] == 8.0     # prep=2 ⇒ ×8 (cubic)
    assert out.values["seeding_within_ib_ceiling"] is True


def test_afforestation_certifies_live():
    m = AfforestationModule(resolver=LIVE)
    assert m.certify_ready() is True
    c = Certifier(resolver=LIVE)
    inputs = {"sigma": 1.0, "delta_mu": 1.2, "prep": 1.5, "rate": 0.2, "rate_max": 1.0}
    cert = c.issue(m, subject="stand-3", inputs=inputs)
    assert c.verify(cert, m, inputs) is True


# --- Harmonization / GHT ----------------------------------------------------

def test_harmonization_clearing_price_and_wu_wei_dividend():
    out = harm_engine.harmonize(marginal_costs=[1.0, 3.0, 2.0], command_overhead=5.0,
                                bandwidth=0.5, ib_bound=1.0)
    assert out["shadow_price"] == 3.0
    assert out["decentralization_cheaper"] is True        # 3 stewards: central 15 > 5 decentralized
    assert out["coordination_within_ib"] is True


def test_harmonization_certifies_live():
    m = HarmonizationModule(resolver=LIVE)
    assert m.certify_ready() is True
    c = Certifier(resolver=LIVE)
    inputs = {"marginal_costs": [1.0, 2.5], "command_overhead": 4.0, "bandwidth": 0.3, "ib_bound": 1.0}
    cert = c.issue(m, subject="region-2", inputs=inputs)
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
