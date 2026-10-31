"""Seed-Supply Bottleneck Check (SSBC, Run-130) — kernel, theorem properties and gating."""

from __future__ import annotations

import random
import sys
from collections import deque
from fractions import Fraction
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from certification.certifier import Certifier
from modules.seed_supply import SeedSupplyBottleneckModule
from modules.seed_supply import engine
from runtime.canon_resolver import CanonResolver
from runtime.module import CertifyBlocked

DOI = "10.5281/zenodo.21971057"
PRIVATE = [[0, 0], [1, 1]]                     # Epriv: source j serves only site j
FULL = [[0, 0], [0, 1], [1, 0], [1, 1]]        # Efull: every source serves every site


def _raises(fn, *args, **kwargs):
    try:
        fn(*args, **kwargs)
    except ValueError:
        return True
    return False


def _max_flow(demands, supplies, edges):
    """Independent exact max-flow (Edmonds–Karp) on source -> supplier -> site -> sink."""
    ns, nd = len(supplies), len(demands)
    S, T = 0, 1 + ns + nd
    cap: dict = {}

    def add(u, v, c):
        cap[(u, v)] = cap.get((u, v), Fraction(0)) + c
        cap.setdefault((v, u), Fraction(0))

    big = sum(Fraction(x) for x in supplies) + 1
    for j, x in enumerate(supplies):
        add(S, 1 + j, Fraction(x))
    for j, i in edges:
        add(1 + j, 1 + ns + i, big)
    for i, x in enumerate(demands):
        add(1 + ns + i, T, Fraction(x))
    adj: dict = {}
    for (u, v) in cap:
        adj.setdefault(u, []).append(v)
    flow = Fraction(0)
    while True:
        parent = {S: None}
        q = deque([S])
        while q and T not in parent:
            u = q.popleft()
            for v in adj.get(u, []):
                if v not in parent and cap[(u, v)] > 0:
                    parent[v] = u
                    q.append(v)
        if T not in parent:
            return flow
        path, v = [], T
        while parent[v] is not None:
            path.append((parent[v], v))
            v = parent[v]
        push = min(cap[e] for e in path)
        for u, v in path:
            cap[(u, v)] -= push
            cap[(v, u)] += push
        flow += push


# --- canon witnesses (series/SSBC/PaperFormalization/Witnesses.lean) ---------------------

def test_c1_witness_private_graph_gives_one_tenth():
    # C1_witness / certificate_priv: d = (1, 1), s = (0.1, 1.9), private eligibility -> 1/10,
    # even though total supply 2 equals total demand 2.
    out = engine.bottleneck_check(demands=[1, 1], supplies=[0.1, 1.9], edges=PRIVATE)
    assert out["common_fulfillment_fraction"] == 0.1
    assert out["full_fulfillment_feasible"] is False
    assert out["bottleneck_site_indices"] == [0]
    assert out["eligible_supply_indices"] == [0]
    assert abs(out["bottleneck_deficit"] - 0.9) < 1e-15
    assert out["sites_in_violated_cuts"] == [0]


def test_c2_witness_full_graph_is_feasible():
    # C2_witness_feasible / certificate_full: same numbers, complete eligibility -> 1.
    out = engine.bottleneck_check(demands=[1, 1], supplies=[0.1, 1.9], edges=FULL)
    assert out["common_fulfillment_fraction"] == 1.0
    assert out["full_fulfillment_feasible"] is True
    assert out["violated_cut_count"] == 0
    assert out["bottleneck_deficit"] == 0.0
    assert out["sources_that_cannot_help"] == []


def test_c3_capacity_outside_the_bottleneck_does_not_help():
    # C3_witness: raising source 1 from 1.9 to 100 leaves the certificate at 1/10.
    before = engine.bottleneck_check(demands=[1, 1], supplies=[0.1, 1.9], edges=PRIVATE)
    after = engine.bottleneck_check(demands=[1, 1], supplies=[0.1, 100], edges=PRIVATE)
    assert before["sources_that_cannot_help"] == [1]
    assert after["common_fulfillment_fraction"] == before["common_fulfillment_fraction"] == 0.1
    # ...while capacity inside N(U*) does help.
    inside = engine.bottleneck_check(demands=[1, 1], supplies=[0.5, 1.9], edges=PRIVATE)
    assert inside["common_fulfillment_fraction"] == 0.5


def test_negative_control_is_arbitrarily_severe():
    # negative_control_arbitrarily_severe: capacities (e, 2 - e) give exactly e.
    for e in (0.01, 0.25, 0.7, 1.0):
        out = engine.bottleneck_check(demands=[1, 1], supplies=[e, 2 - e], edges=PRIVATE)
        assert out["common_fulfillment_fraction"] == e


def test_canon_function_example():
    out = engine.bottleneck_check(demands=[4, 4], supplies=[3, 10], edges=PRIVATE)
    assert out["common_fulfillment_fraction"] == 0.75
    assert out["full_fulfillment_feasible"] is False
    assert out["bottleneck_site_indices"] == [0]
    assert out["eligible_supply_indices"] == [0]
    assert out["bottleneck_ratio"] == 0.75


# --- theorem properties checked against an independent max-flow --------------------------

def test_c1_certificate_is_the_largest_routable_common_fraction():
    rng = random.Random(130)
    for _ in range(40):
        n_sites, n_src = rng.randint(1, 5), rng.randint(1, 4)
        demands = [rng.randint(1, 9) for _ in range(n_sites)]
        supplies = [rng.randint(0, 9) for _ in range(n_src)]
        edges = [[j, i] for j in range(n_src) for i in range(n_sites) if rng.random() < 0.45]
        out = engine.bottleneck_check(demands=demands, supplies=supplies, edges=edges)
        # lam exactly, from the reported bottleneck (integer inputs, so no float rounding).
        lam = min(Fraction(1), Fraction(out["bottleneck_supply"]) / Fraction(out["bottleneck_demand"]))
        need = [lam * d for d in demands]
        assert _max_flow(need, supplies, edges) == sum(need)          # lam is routable
        if lam < 1:
            more = [(lam + Fraction(1, 1000)) * d for d in demands]
            assert _max_flow(more, supplies, edges) < sum(more)       # nothing larger is
        # C2: full feasibility <=> max-flow meets total demand.
        full_ok = _max_flow(demands, supplies, edges) == sum(Fraction(d) for d in demands)
        assert out["full_fulfillment_feasible"] is full_ok


def test_tightest_cut_is_reported_for_feasible_networks():
    out = engine.bottleneck_check(demands=[1, 1], supplies=[3, 4], edges=PRIVATE)
    assert out["common_fulfillment_fraction"] == 1.0
    assert out["bottleneck_ratio"] == 3.0                 # not clamped at 1
    assert out["bottleneck_site_indices"] == [0]


# --- input domain ------------------------------------------------------------------------

def test_rejects_invalid_inputs():
    good = {"demands": [1, 1], "supplies": [1, 1], "edges": PRIVATE}
    bad = [
        {**good, "demands": []},
        {**good, "demands": [1, 0]},                       # Lean needs d_i > 0
        {**good, "demands": [1, -2]},
        {**good, "supplies": [1, -0.5]},                   # Lean needs s_j >= 0
        {**good, "supplies": [1, float("nan")]},
        {**good, "demands": [1, float("inf")]},
        {**good, "edges": [[2, 0]]},                       # source out of range
        {**good, "edges": [[0, 5]]},                       # site out of range
        {**good, "edges": [[0]]},
        {**good, "edges": [[0.0, 1]]},
        {**good, "edges": [[True, 0]]},
        {**good, "demands": [1] * 21},                     # beyond exhaustive-cut limit
        {**good, "demands": "11"},
    ]
    for kwargs in bad:
        assert _raises(engine.bottleneck_check, **kwargs), kwargs
    assert _raises(SeedSupplyBottleneckModule(resolver=CanonResolver(entries={})).compute,
                   {"demands": [1]})


# --- gating ------------------------------------------------------------------------------

def test_bundled_canon_admits_the_backing_doi():
    # Admitted to the bundled canon index by Justin's decision, 2026-10-31.
    assert SeedSupplyBottleneckModule(resolver=CanonResolver()).state().value == "READY"


def test_unadmitted_canon_previews_but_refuses_certification():
    m = SeedSupplyBottleneckModule(resolver=CanonResolver(entries={}))
    assert m.state().value == "BLOCKED"                    # DOI not in this canon (A-1 fail-closed)
    out = m.preview({"demands": [1, 1], "supplies": [0.1, 1.9], "edges": PRIVATE})
    assert out.values["common_fulfillment_fraction"] == 0.1
    try:
        Certifier(resolver=CanonResolver(entries={})).issue(
            m, subject="nursery-net", inputs={"demands": [1], "supplies": [1], "edges": [[0, 0]]})
        assert False, "expected CertifyBlocked while the DOI is not in the canon"
    except CertifyBlocked:
        pass


def test_certify_then_tamper_fails_once_admitted():
    # Fixture resolver standing in for a future canon admission of this DOI.
    admitted = CanonResolver(entries={DOI: {"verified": True}})
    m = SeedSupplyBottleneckModule(resolver=admitted)
    c = Certifier(resolver=admitted)
    inputs = {"demands": [4, 4], "supplies": [3, 10], "edges": PRIVATE}
    cert = c.issue(m, subject="nursery-net", inputs=inputs)
    assert cert.claim.backing_doi == DOI
    assert c.verify(cert, m, inputs) is True
    assert c.verify(cert, m, {**inputs, "supplies": [4, 10]}) is False


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
