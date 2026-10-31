"""Corridor Edge-Priority (PCS, Run-124) — kernel, theorem properties and gating."""

from __future__ import annotations

import random
import sys
from fractions import Fraction
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from certification.certifier import Certifier
from modules.corridor_priority import CorridorPriorityModule
from modules.corridor_priority import engine
from runtime.canon_resolver import CanonResolver
from runtime.module import CertifyBlocked

DOI = "10.5281/zenodo.22665554"
SERIES = {"num_nodes": 3, "edges": [[0, 1], [1, 2]], "core_a": [0], "core_b": [2]}
PARALLEL = {"num_nodes": 2, "edges": [[0, 1], [0, 1]], "core_a": [0], "core_b": [1]}


def _raises(fn, *args, **kwargs):
    try:
        fn(*args, **kwargs)
    except ValueError:
        return True
    return False


def _exact(graph, survival):
    return engine.reliability_and_pivotal(survival=survival, **graph)


def _random_graph(rng):
    n = rng.randint(3, 6)
    m = rng.randint(2, 9)
    edges = []
    while len(edges) < m:
        u, v = rng.randrange(n), rng.randrange(n)
        if u != v:
            edges.append([u, v])
    nodes = list(range(n))
    rng.shuffle(nodes)
    k = rng.randint(1, n - 1)
    return {"num_nodes": n, "edges": edges, "core_a": nodes[:k][:2], "core_b": nodes[k:][:2]}


# --- canon witnesses (ViridisRun124.lean, section Witnesses) ------------------------------

def test_series_witness_matches_the_lean_file():
    # reliability_series2_pEx = 1/6, pivotalProb_series2_pEx_zero = 1/3, _one = 1/2.
    out = engine.edge_priority(survival=[1 / 2, 1 / 3], **SERIES)
    assert abs(out["reliability"] - 1 / 6) < 1e-15
    assert abs(out["pivotal_probability"][0] - 1 / 3) < 1e-15
    assert abs(out["pivotal_probability"][1] - 1 / 2) < 1e-15
    assert out["priority_order"] == [1, 0]
    # Exact with dyadic probabilities: p = (1/2, 1/4) gives R = 1/8, pivotals (1/4, 1/2).
    r, piv = _exact(SERIES, [0.5, 0.25])
    assert r == Fraction(1, 8) and piv == [Fraction(1, 4), Fraction(1, 2)]


def test_c3_witness_best_ratio_with_costs():
    # witness_C3: costs (1, 2), p = (1/2, 1/3): best ratio 1/3, spent on link 0.
    out = engine.edge_priority(survival=[1 / 2, 1 / 3], costs=[1, 2], **SERIES)
    assert abs(out["best_ratio"] - 1 / 3) < 1e-15
    assert out["cost_priority_order"][0] == 0
    assert out["priority_order"][0] == 1          # costs can change which link comes first


def test_parallel_pair():
    r, piv = _exact(PARALLEL, [0.5, 0.25])
    assert r == 1 - Fraction(1, 2) * Fraction(3, 4)
    assert piv == [Fraction(3, 4), Fraction(1, 2)]   # pivotal_e = 1 - p_other


# --- theorem properties ------------------------------------------------------------------

def test_c1_reliability_is_affine_with_slope_the_pivotal_probability():
    # reliability_derivative_eq_pivotal_probability, checked exactly in rationals.
    rng = random.Random(124)
    for _ in range(60):
        g = _random_graph(rng)
        p = [rng.choice([0.1, 0.25, 0.5, 0.6, 0.75, 0.9]) for _ in g["edges"]]
        _, piv = _exact(g, p)
        for e in range(len(p)):
            r0, _ = _exact(g, p[:e] + [0.0] + p[e + 1:])
            r1, _ = _exact(g, p[:e] + [1.0] + p[e + 1:])
            assert piv[e] == r1 - r0                      # pivotalProb_eq_reliability_diff
            for t in (0.3, 0.8):
                rt, piv_t = _exact(g, p[:e] + [t] + p[e + 1:])
                assert rt == r0 + Fraction(repr(t)) * piv[e]
                assert piv_t[e] == piv[e]                 # C2: independent of own p_e


def test_c3_no_budget_split_beats_the_best_ratio():
    # local_linear_budget_gain_le_best_ratio: first-order gain <= B * best ratio.
    rng = random.Random(1240)
    g = {"num_nodes": 4, "edges": [[0, 1], [1, 3], [0, 2], [2, 3], [1, 2]],
         "core_a": [0], "core_b": [3]}
    p, c = [0.7, 0.6, 0.5, 0.8, 0.4], [1.0, 2.0, 1.5, 3.0, 0.5]
    out = engine.edge_priority(survival=p, costs=c, **g)
    B = 1.0
    for _ in range(500):
        d = [rng.random() for _ in p]
        scale = B / sum(ci * di for ci, di in zip(c, d))
        d = [di * scale for di in d]
        gain = sum(pv * di for pv, di in zip(out["pivotal_probability"], d))
        assert gain <= B * out["best_ratio"] + 1e-12


def test_structure_function_is_monotone():
    rng = random.Random(7)
    for _ in range(20):
        g = _random_graph(rng)
        links = [tuple(e) for e in g["edges"]]
        phi = engine._connected_table(g["num_nodes"], links, g["core_a"], g["core_b"])
        for s in range(len(phi)):
            for k in range(len(links)):
                if phi[s]:
                    assert phi[s | (1 << k)]


def test_bridge_link_ranks_first():
    # Two cores joined by a bridge (link 2) between two redundant triangles.
    g = {"num_nodes": 6, "edges": [[0, 1], [0, 2], [1, 2], [2, 3], [3, 4], [3, 5], [4, 5]],
         "core_a": [0], "core_b": [5]}
    out = engine.edge_priority(survival=[0.8] * 7, **g)
    assert out["top_link"] == 3


# --- input domain ------------------------------------------------------------------------

def test_rejects_invalid_inputs():
    good = {**SERIES, "survival": [0.5, 0.5]}
    big = {"num_nodes": 18, "edges": [[i, i + 1] for i in range(17)], "survival": [0.5] * 17,
           "core_a": [0], "core_b": [17]}
    for bad in (big,                                            # above the hard size cap
                {**good, "survival": [0.5]},
                {**good, "survival": [0.5, 1.2]},
                {**good, "survival": [0.5, float("nan")]},
                {**good, "edges": [[0, 0], [1, 2]]},
                {**good, "edges": [[0, 3], [1, 2]]},
                {**good, "edges": []},
                {**good, "core_a": [0], "core_b": [0]},
                {**good, "core_b": []},
                {**good, "num_nodes": 1},
                {**good, "costs": [1, 0]},
                {**good, "costs": [1]}):
        assert _raises(engine.edge_priority, **bad), {k: bad[k] for k in bad if k != "edges"}
    assert _raises(CorridorPriorityModule(resolver=CanonResolver(entries={})).compute,
                   {"num_nodes": 3})


# --- gating ------------------------------------------------------------------------------

INPUTS = {**SERIES, "survival": [0.5, 0.25]}


def test_ships_as_preview_against_the_bundled_canon():
    m = CorridorPriorityModule(resolver=CanonResolver())
    assert m.state().value == "BLOCKED"                     # DOI not in the bundled index
    assert m.preview(INPUTS).values["reliability"] == 0.125
    try:
        Certifier(resolver=CanonResolver()).issue(m, subject="corridor-1", inputs=INPUTS)
        assert False, "expected CertifyBlocked while the DOI is not gate-passed"
    except CertifyBlocked:
        pass


def test_certify_then_tamper_fails_once_admitted():
    admitted = CanonResolver(entries={DOI: {"verified": True}})   # fixture for a future admission
    m = CorridorPriorityModule(resolver=admitted)
    c = Certifier(resolver=admitted)
    cert = c.issue(m, subject="corridor-1", inputs=INPUTS)
    assert cert.claim.backing_doi == DOI
    assert c.verify(cert, m, INPUTS) is True
    assert c.verify(cert, m, {**INPUTS, "survival": [0.5, 0.5]}) is False


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
