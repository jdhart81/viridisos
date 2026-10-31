"""Anytime-valid Monitoring Alarm (ACC, Run-129) — kernel, theorem properties and gating."""

from __future__ import annotations

import itertools
import math
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from certification.certifier import Certifier
from modules.anytime_alarm import AnytimeAlarmModule
from modules.anytime_alarm import engine
from runtime.canon_resolver import CanonResolver
from runtime.module import CertifyBlocked

DOI = "10.5281/zenodo.21971041"


def _raises(fn, *args, **kwargs):
    try:
        fn(*args, **kwargs)
    except ValueError:
        return True
    return False


def _path(xs, p0, p1):
    """Plain (non-log) recursion of Equation (2), for cross-checking: list of M_1..M_n."""
    up, down = p1 / p0, (1 - p1) / (1 - p0)
    acc, out = 0.0, []
    for n, x in enumerate(xs, start=1):
        acc = (up if x else down) * (acc + engine.change_prior(n))
        out.append(acc + 1.0 / (n + 1))
    return out


# --- canon example and witness -----------------------------------------------------------

def test_canon_function_example():
    out = engine.monitor(observations=[1, 0, 1, 1, 0, 1, 1, 1], p0=0.2, p1=0.6, alpha=0.05)
    assert abs(out["current_mixture_evidence"] - 114.806349206349) < 1e-9
    assert abs(out["maximum_mixture_evidence"] - 114.806349206349) < 1e-9
    assert out["alarm_threshold"] == 20.0
    assert out["alarmed"] is True and out["alarm_index"] == 7
    assert out["observations_processed"] == 8
    assert out["false_alarm_probability_bound"] == 0.05


def test_witness_likelihood_ratios_and_prior():
    # Witnesses.lean (C12Witness): Bernoulli(1/5) null with LR 3 on a 1 and 1/2 on a 0,
    # i.e. p1 = 3/5. Prior.lean: pi_k = 1/(k(k+1)) sums to 1 with tail 1/(n+1).
    assert abs(0.6 / 0.2 - 3.0) < 1e-12 and abs((1 - 0.6) / (1 - 0.2) - 0.5) < 1e-12
    assert abs(sum(engine.change_prior(k) for k in range(1, 1001)) - (1 - 1 / 1001)) < 1e-12
    assert engine.monitor(observations=[], p0=0.2, p1=0.6, alpha=0.05)[
        "current_mixture_evidence"] == 1.0                    # M_0 = 1


# --- theorem properties ------------------------------------------------------------------

def test_c1_mixture_is_mean_one_under_the_null():
    # anytime_change_mixture_martingale: E0[M_n] = 1 for every n (exact enumeration).
    for p0, p1 in ((0.2, 0.6), (0.7, 0.3), (0.05, 0.5)):
        for n in (1, 3, 6, 10):
            total = 0.0
            for xs in itertools.product((0, 1), repeat=n):
                w = math.prod(p0 if x else 1 - p0 for x in xs)
                total += w * _path(xs, p0, p1)[-1]
            assert abs(total - 1.0) < 1e-10, (p0, p1, n, total)


def test_c2_false_alarm_probability_at_most_alpha():
    # anytime_change_ville_certificate: P0(alarm by horizon n) <= alpha, exact over all paths.
    for p0, p1, alpha in ((0.2, 0.6, 0.05), (0.5, 0.9, 0.2), (0.3, 0.05, 0.1)):
        n = 14
        mass = 0.0
        for xs in itertools.product((0, 1), repeat=n):
            if engine.monitor(observations=list(xs), p0=p0, p1=p1, alpha=alpha)["alarmed"]:
                mass += math.prod(p0 if x else 1 - p0 for x in xs)
        assert mass <= alpha + 1e-12, (p0, p1, alpha, mass)


def test_log_space_matches_plain_recursion():
    rng = random.Random(129)
    xs = [1 if rng.random() < 0.3 else 0 for _ in range(60)]
    plain = _path(xs, 0.2, 0.35)
    out = engine.monitor(observations=xs, p0=0.2, p1=0.35, alpha=0.01)
    assert abs(out["current_mixture_evidence"] / plain[-1] - 1) < 1e-10
    assert abs(out["maximum_mixture_evidence"] / max([1.0] + plain) - 1) < 1e-10


def test_c3_mixture_dominates_each_change_component():
    # change_component_dominance_and_penalty: M_n >= pi_nu * prod_{i=nu..n} Lambda_i, and
    # a_nu = log(1/alpha) + log(nu(nu+1)).
    rng = random.Random(3)
    p0, p1 = 0.1, 0.4
    up, down = p1 / p0, (1 - p1) / (1 - p0)
    xs = [1 if rng.random() < 0.25 else 0 for _ in range(40)]
    m = _path(xs, p0, p1)
    for nu in range(1, 41):
        for n in range(nu, 41):
            comp = engine.change_prior(nu) * math.prod(up if x else down for x in xs[nu - 1:n])
            assert comp <= m[n - 1] * (1 + 1e-12)
    assert abs(engine.evidence_boundary(0.05, 3) - (math.log(20) + math.log(12))) < 1e-12


def test_c4_expected_delay_is_below_the_wald_bound():
    # bounded_overshoot_expected_delay via dominance: E1[post-change obs to alarm] <
    # (a_nu + z_max)/D. Monte Carlo with a fixed seed, change at nu = 1 and nu = 5.
    rng = random.Random(1290)
    p0, p1, alpha = 0.2, 0.6, 0.05
    for nu in (1, 5):
        bound = engine.delay_bounds(p0=p0, p1=p1, alpha=alpha, change_time=nu)
        delays = []
        for _ in range(1500):
            xs = [1 if rng.random() < p0 else 0 for _ in range(nu - 1)]
            while True:
                xs.append(1 if rng.random() < p1 else 0)
                out = engine.monitor(observations=xs, p0=p0, p1=p1, alpha=alpha)
                if out["alarmed"]:
                    delays.append(max(0, out["alarm_index"] - (nu - 1)))
                    break
        mean = sum(delays) / len(delays)
        assert mean < bound["expected_delay_upper_bound"], (nu, mean, bound)
        assert bound["component_expected_delay_lower"] < bound["expected_delay_upper_bound"]
    d = engine.kl_bernoulli(0.6, 0.2)
    assert abs(d - (0.6 * math.log(3) + 0.4 * math.log(0.5))) < 1e-12


# --- input domain ------------------------------------------------------------------------

def test_rejects_invalid_inputs():
    good = {"observations": [0, 1], "p0": 0.2, "p1": 0.6, "alpha": 0.05}
    for bad in ({**good, "observations": [0, 2]}, {**good, "observations": [0, 1.0]},
                {**good, "observations": [True]}, {**good, "observations": "01"},
                {**good, "p0": 0.0}, {**good, "p1": 1.0}, {**good, "alpha": 1.0},
                {**good, "alpha": float("nan")}, {**good, "p1": 0.2},
                {**good, "change_time": 0}, {**good, "observations": [0] * 100_001}):
        assert _raises(engine.monitor, **bad), {k: v for k, v in bad.items() if k != "observations"}
    assert _raises(AnytimeAlarmModule(resolver=CanonResolver(entries={})).compute, {"p0": 0.2})


# --- gating ------------------------------------------------------------------------------

INPUTS = {"observations": [1, 0, 1, 1, 0, 1, 1, 1], "p0": 0.2, "p1": 0.6, "alpha": 0.05}


def test_bundled_canon_admits_the_backing_doi():
    # Admitted to the bundled canon index by Justin's decision, 2026-10-31.
    assert AnytimeAlarmModule(resolver=CanonResolver()).state().value == "READY"


def test_unadmitted_canon_previews_but_refuses_certification():
    m = AnytimeAlarmModule(resolver=CanonResolver(entries={}))
    assert m.state().value == "BLOCKED"                    # DOI not in this canon (A-1 fail-closed)
    assert m.preview(INPUTS).values["alarm_index"] == 7
    try:
        Certifier(resolver=CanonResolver(entries={})).issue(m, subject="plot-7", inputs=INPUTS)
        assert False, "expected CertifyBlocked while the DOI is not in the canon"
    except CertifyBlocked:
        pass


def test_certify_then_tamper_fails_once_admitted():
    admitted = CanonResolver(entries={DOI: {"verified": True}})   # fixture for a future admission
    m = AnytimeAlarmModule(resolver=admitted)
    c = Certifier(resolver=admitted)
    cert = c.issue(m, subject="plot-7", inputs=INPUTS)
    assert cert.claim.backing_doi == DOI
    assert c.verify(cert, m, INPUTS) is True
    assert c.verify(cert, m, {**INPUTS, "observations": [1, 0, 1, 1, 0, 1, 1, 0]}) is False


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
