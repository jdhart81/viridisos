"""Precautionary Capacity Ceiling (PCR, Run-127) — kernel, theorem properties and gating."""

from __future__ import annotations

import math
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from certification.certifier import Certifier
from modules.precautionary_ceiling import PrecautionaryCeilingModule
from modules.precautionary_ceiling import engine
from runtime.canon_resolver import CanonResolver
from runtime.module import CertifyBlocked

DOI = "10.5281/zenodo.21971046"


def _raises(fn, *args, **kwargs):
    try:
        fn(*args, **kwargs)
    except ValueError:
        return True
    return False


def _moments(atoms, probs):
    mean = sum(x * p for x, p in zip(atoms, probs))
    var = sum((x - mean) ** 2 * p for x, p in zip(atoms, probs))
    return mean, var


def _below(atoms, probs, level):
    return sum(p for x, p in zip(atoms, probs) if x < level)


# --- canon witnesses ---------------------------------------------------------------------

def test_nonvacuity_witness_from_the_lean_file():
    # NonVacuity.lean: witnessLaw = 4/13 at 1/4, 9/13 at 4/3; mean 1, variance 1/4,
    # cantelliFactor(1/2) = 1, capacityFloor 1 (1/2) (1/2) = 1/2, violation mass 4/13 <= 1/2.
    atoms, probs = [0.25, 4 / 3], [4 / 13, 9 / 13]
    mean, var = _moments(atoms, probs)
    assert abs(mean - 1.0) < 1e-15 and abs(var - 0.25) < 1e-15
    out = engine.precautionary_ceiling(mean_capacity=1.0, capacity_sd=0.5, alpha=0.5)
    assert out["cantelli_factor"] == 1.0
    assert out["precautionary_ceiling"] == 0.5
    assert abs(_below(atoms, probs, out["precautionary_ceiling"]) - 4 / 13) < 1e-15
    assert _below(atoms, probs, out["precautionary_ceiling"]) <= out["violation_probability_bound"]


def test_canon_function_example():
    out = engine.precautionary_ceiling(mean_capacity=10, capacity_sd=1, alpha=0.2)
    assert out["precautionary_ceiling"] == 8.0
    assert out["absolute_discount"] == 2.0
    assert out["capacity_fraction"] == 0.8
    assert out["violation_probability_bound"] == 0.2
    assert out["positive_floor"] is True
    assert out["mean_only_rule_safe"] is False


# --- theorem properties ------------------------------------------------------------------

def test_guarantee_holds_for_every_law_with_those_moments():
    # capacityFloor_violation_prob_le on many random non-negative discrete laws.
    rng = random.Random(127)
    for _ in range(2000):
        k = rng.randint(1, 6)
        atoms = [rng.uniform(0, 20) * rng.choice([0, 1, 1, 1]) for _ in range(k)]
        w = [rng.random() + 1e-9 for _ in range(k)]
        probs = [x / sum(w) for x in w]
        mean, var = _moments(atoms, probs)
        alpha = rng.choice([0.01, 0.05, 0.1, 0.2, 0.5, 0.8, 0.95])
        floor = engine.capacity_floor(mean, math.sqrt(var), alpha)
        assert _below(atoms, probs, floor) <= alpha + 1e-12


def test_ceiling_is_sharp_two_point_counterexample():
    # positive_floor_sharp_two_point_counterexample: any ceiling above d_alpha fails for some
    # non-negative law with the same mean and variance.
    for mu, sigma, alpha in ((10.0, 1.0, 0.2), (1.0, 0.5, 0.5), (50.0, 7.0, 0.05)):
        floor = engine.capacity_floor(mu, sigma, alpha)
        for d in (floor + 1e-6, floor + 0.3 * (mu - floor), mu, mu * 1.5):
            law = engine.two_point_counterexample(mu, sigma, alpha, d)
            atoms, probs = [law["low"], law["high"]], [law["p_low"], law["p_high"]]
            assert min(atoms) >= 0
            mean, var = _moments(atoms, probs)
            assert abs(mean - mu) < 1e-9 * max(1.0, mu)
            assert abs(var - sigma ** 2) < 1e-9 * max(1.0, sigma ** 2)
            assert _below(atoms, probs, d) > alpha
            # ...while the certified floor itself is still safe for this law.
            assert _below(atoms, probs, floor) <= alpha + 1e-12


def test_mean_only_rule_can_fail_with_probability_near_one():
    # mean_only_plugin_arbitrarily_unsafe: a ceiling at theta * mu, from the mean alone.
    for theta, beta in ((1.0, 0.999), (0.5, 0.9), (0.1, 0.0)):
        law = engine.mean_only_counterexample(100.0, theta, beta)
        atoms, probs = [law["low"], law["high"]], [law["p_low"], law["p_high"]]
        assert min(atoms) >= 0
        assert abs(_moments(atoms, probs)[0] - 100.0) < 1e-9
        assert _below(atoms, probs, theta * 100.0) > beta


def test_clipped_floor_and_fraction_identity():
    out = engine.precautionary_ceiling(mean_capacity=1.0, capacity_sd=10.0, alpha=0.05)
    assert out["precautionary_ceiling"] == 0.0
    assert out["positive_floor"] is False and out["ceiling_is_sharp"] is False
    mu, sigma, alpha = 40.0, 6.0, 0.1
    out = engine.precautionary_ceiling(mean_capacity=mu, capacity_sd=sigma, alpha=alpha)
    expected = max(0.0, 1 - (sigma / mu) * math.sqrt((1 - alpha) / alpha))
    assert abs(out["capacity_fraction"] - expected) < 1e-15
    assert engine.precautionary_ceiling(mean_capacity=5.0, capacity_sd=0.0, alpha=0.3)[
        "precautionary_ceiling"] == 5.0


# --- input domain ------------------------------------------------------------------------

def test_rejects_invalid_inputs():
    good = {"mean_capacity": 10.0, "capacity_sd": 1.0, "alpha": 0.2}
    for bad in ({**good, "alpha": 0.0}, {**good, "alpha": 1.0}, {**good, "alpha": -0.1},
                {**good, "alpha": float("nan")}, {**good, "mean_capacity": -1.0},
                {**good, "capacity_sd": -0.1}, {**good, "mean_capacity": float("inf")},
                {**good, "capacity_sd": "x"}, {**good, "alpha": True}):
        assert _raises(engine.precautionary_ceiling, **bad), bad
    m = PrecautionaryCeilingModule(resolver=CanonResolver(entries={}))
    assert _raises(m.compute, {"mean_capacity": 10.0, "capacity_sd": 1.0})
    assert _raises(m.compute, {**good, "power": 1.0, "temperature": 300.0})   # no rate model
    floor = engine.capacity_floor(10.0, 1.0, 0.2)
    assert _raises(engine.two_point_counterexample, 10.0, 1.0, 0.2, floor)    # must exceed floor
    assert _raises(engine.two_point_counterexample, 10.0, 0.0, 0.2, 11.0)     # needs sigma > 0
    assert _raises(engine.mean_only_counterexample, 0.0, 0.5, 0.5)
    assert _raises(engine.mean_only_counterexample, 1.0, 0.5, 1.0)


# --- gating ------------------------------------------------------------------------------

def test_bundled_canon_admits_the_backing_doi():
    # Admitted to the bundled canon index by Justin's decision, 2026-10-31.
    assert PrecautionaryCeilingModule(resolver=CanonResolver()).state().value == "READY"


def test_unadmitted_canon_previews_but_refuses_certification():
    m = PrecautionaryCeilingModule(resolver=CanonResolver(entries={}))
    assert m.state().value == "BLOCKED"                    # DOI not in this canon (A-1 fail-closed)
    assert m.preview({"mean_capacity": 10, "capacity_sd": 1, "alpha": 0.2}).values[
        "precautionary_ceiling"] == 8.0
    try:
        Certifier(resolver=CanonResolver(entries={})).issue(
            m, subject="stand-1", inputs={"mean_capacity": 10, "capacity_sd": 1, "alpha": 0.2})
        assert False, "expected CertifyBlocked while the DOI is not in the canon"
    except CertifyBlocked:
        pass


def test_certify_then_tamper_fails_once_admitted():
    admitted = CanonResolver(entries={DOI: {"verified": True}})   # fixture for a future admission
    m = PrecautionaryCeilingModule(resolver=admitted)
    c = Certifier(resolver=admitted)
    inputs = {"mean_capacity": 10, "capacity_sd": 1, "alpha": 0.2}
    cert = c.issue(m, subject="stand-1", inputs=inputs)
    assert cert.claim.backing_doi == DOI
    assert c.verify(cert, m, inputs) is True
    assert c.verify(cert, m, {**inputs, "capacity_sd": 0.5}) is False


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
