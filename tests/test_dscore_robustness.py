"""D-Score Weight-Robustness (DSWC, Run-132) — kernel, theorem properties and gating."""

from __future__ import annotations

import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from certification.certifier import Certifier
from modules.dscore_robustness import DScoreRobustnessModule
from modules.dscore_robustness import engine
from runtime.canon_resolver import CanonResolver
from runtime.module import CertifyBlocked

DOI = "10.5281/zenodo.22236741"


def _raises(fn, *args, **kwargs):
    try:
        fn(*args, **kwargs)
    except ValueError:
        return True
    return False


def _random_simplex(rng, n):
    w = [rng.random() * rng.choice([0, 1, 1]) for _ in range(n)]
    if sum(w) == 0:
        w[0] = 1.0
    s = sum(w)
    return [x / s for x in w]


# --- canon witness (ViridisRun132.lean, charter_nonvacuous) -------------------------------

def test_charter_nonvacuous_witness_attains_the_bound():
    # w0 = (0.6, 0.4), w = (0.3, 0.7), z = (0, 5): tv = 0.3, score drift = 1.5 = tv * span.
    out = engine.weight_robustness(reference_weights=[0.6, 0.4], alternative_weights=[0.3, 0.7],
                                   parcel_a=[0.0, 5.0], parcel_b=[0.0, 0.0])
    assert abs(out["total_variation"] - 0.3) < 1e-15
    a = out["parcel_a"]
    assert abs((a["score_alternative"] - a["score_reference"]) - 1.5) < 1e-12
    assert abs(a["drift_bound"] - 1.5) < 1e-12              # bound is attained here
    assert a["drift"] <= a["drift_bound"] + 1e-12


# --- theorem properties ------------------------------------------------------------------

def test_tv_range_certificate_holds_on_random_instances():
    rng = random.Random(132)
    for _ in range(3000):
        n = rng.randint(1, 8)
        v, w = _random_simplex(rng, n), _random_simplex(rng, n)
        z = [rng.uniform(-10, 10) for _ in range(n)]
        drift = abs(engine.score(w, z) - engine.score(v, z))
        assert drift <= engine.total_variation(w, v) * engine.span(z) + 1e-9


def test_strict_rank_stability_robust_case_keeps_the_order():
    # v = (0.9, 0.1), A = (1, 0), B = (0, 1): gap 0.8; w = (0.8, 0.2): tv 0.1, bound 0.2 < 0.8.
    out = engine.weight_robustness(reference_weights=[0.9, 0.1], alternative_weights=[0.8, 0.2],
                                   parcel_a=[1.0, 0.0], parcel_b=[0.0, 1.0])
    assert out["ranking_robust"] is True
    assert out["leader_reference"] == out["leader_alternative"] == "A"
    assert out["order_flipped_under_alternative"] is False
    assert abs(out["robust_tv_radius"] - 0.4) < 1e-12       # |gap| / span = 0.8 / 2
    # Every weight vector strictly inside that radius keeps A ahead (the theorem's claim).
    rng = random.Random(7)
    for _ in range(2000):
        u = _random_simplex(rng, 2)
        if engine.total_variation(u, [0.9, 0.1]) < out["robust_tv_radius"]:
            assert engine.score(u, [1.0, -1.0]) > 0


def test_non_robust_case_can_actually_flip():
    # v = (0.6, 0.4): gap 0.2; w = (0.3, 0.7): tv 0.3, bound 0.6 > 0.2, and B overtakes A.
    out = engine.weight_robustness(reference_weights=[0.6, 0.4], alternative_weights=[0.3, 0.7],
                                   parcel_a=[1.0, 0.0], parcel_b=[0.0, 1.0])
    assert out["ranking_robust"] is False
    assert out["leader_reference"] == "A" and out["leader_alternative"] == "B"
    assert out["order_flipped_under_alternative"] is True
    # Robust verdicts never flip (strict_rank_stability), checked on random instances.
    rng = random.Random(1320)
    for _ in range(3000):
        n = rng.randint(1, 6)
        v, w = _random_simplex(rng, n), _random_simplex(rng, n)
        za = [rng.uniform(0, 1) for _ in range(n)]
        zb = [rng.uniform(0, 1) for _ in range(n)]
        r = engine.weight_robustness(reference_weights=v, alternative_weights=w,
                                     parcel_a=za, parcel_b=zb)
        if r["ranking_robust"]:
            assert r["order_flipped_under_alternative"] is False


def test_ecological_validity_is_never_claimed():
    out = engine.weight_robustness(reference_weights=[1.0], alternative_weights=[1.0],
                                   parcel_a=[2.0], parcel_b=[1.0])
    assert out["ecological_validity_proven"] is False
    assert "not proven" in out["claim_boundary"]
    assert out["total_variation"] == 0.0 and out["ranking_robust"] is True
    assert out["robust_tv_radius"] is None                  # span 0, nonzero gap: never flips


# --- input domain ------------------------------------------------------------------------

def test_rejects_invalid_inputs():
    good = {"reference_weights": [0.5, 0.5], "alternative_weights": [0.4, 0.6],
            "parcel_a": [1.0, 2.0], "parcel_b": [2.0, 1.0]}
    for bad in ({**good, "reference_weights": [0.5, 0.6]},          # does not sum to 1
                {**good, "alternative_weights": [1.2, -0.2]},       # negative weight
                {**good, "reference_weights": []},
                {**good, "parcel_a": [1.0]},                        # length mismatch
                {**good, "parcel_b": [1.0, float("nan")]},
                {**good, "parcel_a": [1.0, float("inf")]},
                {**good, "alternative_weights": [True, False]},
                {**good, "parcel_a": "12"}):
        assert _raises(engine.weight_robustness, **bad), bad
    m = DScoreRobustnessModule(resolver=CanonResolver(entries={}))
    assert _raises(m.compute, {"reference_weights": [1.0]})


# --- gating ------------------------------------------------------------------------------

INPUTS = {"reference_weights": [0.9, 0.1], "alternative_weights": [0.8, 0.2],
          "parcel_a": [1.0, 0.0], "parcel_b": [0.0, 1.0]}


def test_bundled_canon_admits_the_backing_doi():
    # Admitted to the bundled canon index by Justin's decision, 2026-10-31.
    assert DScoreRobustnessModule(resolver=CanonResolver()).state().value == "READY"


def test_unadmitted_canon_previews_but_refuses_certification():
    m = DScoreRobustnessModule(resolver=CanonResolver(entries={}))
    assert m.state().value == "BLOCKED"                     # DOI not in this canon (A-1 fail-closed)
    assert m.preview(INPUTS).values["ranking_robust"] is True
    try:
        Certifier(resolver=CanonResolver(entries={})).issue(m, subject="parcels", inputs=INPUTS)
        assert False, "expected CertifyBlocked while the DOI is not in the canon"
    except CertifyBlocked:
        pass


def test_certify_then_tamper_fails_once_admitted():
    admitted = CanonResolver(entries={DOI: {"verified": True}})   # fixture for a future admission
    m = DScoreRobustnessModule(resolver=admitted)
    c = Certifier(resolver=admitted)
    cert = c.issue(m, subject="parcels", inputs=INPUTS)
    assert cert.claim.backing_doi == DOI
    assert c.verify(cert, m, INPUTS) is True
    assert c.verify(cert, m, {**INPUTS, "alternative_weights": [0.3, 0.7]}) is False


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
