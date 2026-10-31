"""Byproduct Exchange Corridor (RC, Run-128) — kernel, theorem properties and gating."""

from __future__ import annotations

import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from certification.certifier import Certifier
from modules.byproduct_exchange import ByproductExchangeModule
from modules.byproduct_exchange import engine
from runtime.canon_resolver import CanonResolver
from runtime.module import CertifyBlocked

DOI = "10.5281/zenodo.21971047"
FEASIBLE = dict(value_x=2, value_y=2, cost_x=1, cost_y=1)     # canon witness economy
INFEASIBLE = dict(value_x=1, value_y=1, cost_x=2, cost_y=2)   # canon witness economy


def _raises(fn, *args, **kwargs):
    try:
        fn(*args, **kwargs)
    except ValueError:
        return True
    return False


def _close(a, b, tol=1e-12):
    return abs(a - b) <= tol * max(1.0, abs(a), abs(b))


# --- canon witnesses ---------------------------------------------------------------------

def test_witness_C1_benefit_and_no_benefit():
    # witness_C1_benefit: x = y = 1 benefits both and is in the corridor.
    ux, uy = engine.payoffs(**FEASIBLE, flow_x=1, flow_y=1)
    assert ux == 1 and uy == 1
    out = engine.exchange_corridor(**FEASIBLE, total_flow=2, flow_x=1, flow_y=1)
    assert out["proposed_in_corridor"] is True and out["proposed_bilateral_benefit"] is True
    # witness_C1_no_benefit: x = 1, y = 10 is outside and Y loses.
    out = engine.exchange_corridor(**FEASIBLE, total_flow=11, flow_x=1, flow_y=10)
    assert out["proposed_in_corridor"] is False and out["proposed_bilateral_benefit"] is False
    assert out["proposed_payoff_y"] < 0


def test_witness_C2_nonempty_and_empty():
    assert engine.exchange_corridor(**FEASIBLE, total_flow=1)["corridor_nonempty"] is True
    out = engine.exchange_corridor(**INFEASIBLE, total_flow=1)
    assert out["corridor_nonempty"] is False and out["nash_y_share"] is None


def test_witness_C3_nash_midpoint_is_one_half():
    out = engine.exchange_corridor(**FEASIBLE, total_flow=1)
    assert _close(out["nash_y_share"], 0.5)
    best = engine.nash_product(**FEASIBLE, total_flow=1, share=out["nash_y_share"])
    assert best > 0
    for k in range(-200, 401):
        q = k / 200.0
        if abs(q - 0.5) > 1e-9:
            assert engine.nash_product(**FEASIBLE, total_flow=1, share=q) < best


def test_witness_C4_scale_and_infeasible_economy():
    # uXshare 2 1 1 (1/2) = 1/2 and doubling R doubles it.
    one = engine.exchange_corridor(**FEASIBLE, total_flow=1)
    two = engine.exchange_corridor(**FEASIBLE, total_flow=2)
    assert _close(one["nash_payoff_x"], 0.5) and _close(two["nash_payoff_x"], 1.0)
    rng = random.Random(4)
    for _ in range(500):
        x, y = rng.uniform(1e-3, 100), rng.uniform(1e-3, 100)
        ux, uy = engine.payoffs(**INFEASIBLE, flow_x=x, flow_y=y)
        assert not (ux > 0 and uy > 0)


def test_canon_function_example():
    out = engine.exchange_corridor(value_x=4, value_y=4, cost_x=1, cost_y=1, total_flow=10)
    assert out["corridor_nonempty"] is True
    assert out["flow_ratio_lower"] == 0.25 and out["flow_ratio_upper"] == 4
    assert _close(out["y_share_lower"], 0.2) and _close(out["y_share_upper"], 0.8)
    assert _close(out["nash_y_share"], 0.5)
    assert _close(out["nash_x_flow"], 5) and _close(out["nash_y_flow"], 5)
    assert _close(out["nash_payoff_x"], 15) and _close(out["nash_payoff_y"], 15)


# --- theorem properties on random economies ------------------------------------------------

def _random_economy(rng):
    return dict(value_x=rng.uniform(0.1, 10), value_y=rng.uniform(0.1, 10),
                cost_x=rng.uniform(0.1, 10), cost_y=rng.uniform(0.1, 10))


def test_C1_corridor_iff_bilateral_benefit():
    rng = random.Random(128)
    checked = 0
    for _ in range(4000):
        eco = _random_economy(rng)
        x, y = rng.uniform(0.01, 50), rng.uniform(0.01, 50)
        ux, uy = engine.payoffs(**eco, flow_x=x, flow_y=y)
        if min(abs(ux), abs(uy)) < 1e-9:
            continue  # float boundary; the theorem is about strict inequalities
        out = engine.exchange_corridor(**eco, total_flow=x + y, flow_x=x, flow_y=y)
        assert out["proposed_in_corridor"] == out["proposed_bilateral_benefit"]
        checked += 1
    assert checked > 3900


def test_C2_product_condition_iff_some_flow_benefits_both():
    rng = random.Random(2)
    for _ in range(2000):
        eco = _random_economy(rng)
        out = engine.exchange_corridor(**eco, total_flow=1)
        if out["corridor_nonempty"]:
            # the Nash split is a constructive witness of strict mutual benefit
            ux, uy = engine.payoffs(**eco, flow_x=out["nash_x_flow"], flow_y=out["nash_y_flow"])
            assert ux > 0 and uy > 0
            assert out["y_share_lower"] < out["y_share_upper"]
        else:
            assert out["y_share_lower"] >= out["y_share_upper"] - 1e-15
            for k in range(1, 100):
                q = k / 100.0
                ux, uy = engine.payoffs(**eco, flow_x=1 - q, flow_y=q)
                assert not (ux > 1e-12 and uy > 1e-12)


def test_share_payoff_identities_and_nash_payoffs():
    rng = random.Random(5)
    for _ in range(1000):
        eco = _random_economy(rng)
        r, q = rng.uniform(0.1, 20), rng.uniform(-0.5, 1.5)
        q_lo, q_hi = engine.share_bounds(**eco)
        vx, vy, cx, cy = eco["value_x"], eco["value_y"], eco["cost_x"], eco["cost_y"]
        x, y = r * (1 - q), r * q
        assert _close(vx * y - cx * x, r * (vx + cx) * (q - q_lo), 1e-9)
        assert _close(vy * x - cy * y, r * (vy + cy) * (q_hi - q), 1e-9)
        out = engine.exchange_corridor(**eco, total_flow=r)
        if out["corridor_nonempty"]:
            qs = out["nash_y_share"]
            assert _close(out["nash_payoff_x"], vx * r * qs - cx * r * (1 - qs), 1e-9)
            assert _close(out["nash_payoff_y"], vy * r * (1 - qs) - cy * r * qs, 1e-9)
            best = engine.nash_product(**eco, total_flow=r, share=qs)
            for dq in (-0.3, -0.05, -1e-3, 1e-3, 0.05, 0.3):
                assert engine.nash_product(**eco, total_flow=r, share=qs + dq) < best


def test_C4_beneficial_shares_do_not_depend_on_scale():
    rng = random.Random(44)
    for _ in range(300):
        eco = _random_economy(rng)
        a = engine.exchange_corridor(**eco, total_flow=rng.uniform(0.1, 1))
        b = engine.exchange_corridor(**eco, total_flow=rng.uniform(10, 1000))
        for key in ("corridor_nonempty", "y_share_lower", "y_share_upper", "nash_y_share"):
            assert a[key] == b[key]
        assert a["scale_can_restore_feasibility"] is False


# --- invalid inputs ----------------------------------------------------------------------

def test_invalid_inputs_rejected():
    base = dict(**FEASIBLE, total_flow=1)
    for key in ("value_x", "value_y", "cost_x", "cost_y", "total_flow"):
        for bad in (0, -1, float("nan"), float("inf"), "abc", None, True):
            assert _raises(engine.exchange_corridor, **{**base, key: bad}), (key, bad)
    assert _raises(engine.exchange_corridor, **base, flow_x=1)          # half a proposal
    assert _raises(engine.exchange_corridor, **base, flow_x=1, flow_y=0)  # y = 0: one-way
    assert _raises(engine.exchange_corridor, **base, flow_x=-1, flow_y=1)
    m = ByproductExchangeModule()
    assert _raises(m.compute, {"value_x": 1})
    assert _raises(m.compute, {**base, "temperature": 300})
    assert _raises(m.compute, {**base, "power": 1})


# --- gating: PREVIEW against the bundled canon, certify-then-tamper under a stand-in -------

def test_preview_runs_but_certification_is_refused():
    m = ByproductExchangeModule()
    assert m.backing.doi == DOI
    assert m.state().value == "BLOCKED"
    out = m.preview({**FEASIBLE, "total_flow": 2})
    assert out.values["corridor_nonempty"] is True
    assert out.provenance.backing_doi == DOI
    try:
        Certifier().issue(m, subject="park-1", inputs={**FEASIBLE, "total_flow": 2})
        assert False, "expected CertifyBlocked"
    except CertifyBlocked:
        pass


def test_certify_then_tamper_with_stand_in_resolver():
    resolver = CanonResolver(entries={DOI: {"verified": True,
                                            "lean_module": "Viridis.Run128.PaperFormalization"}})
    m = ByproductExchangeModule(resolver=resolver)
    c = Certifier(resolver=resolver)
    inputs = {"value_x": 3, "value_y": 2, "cost_x": 1, "cost_y": 1.5, "total_flow": 8,
              "flow_x": 4, "flow_y": 4}
    cert = c.issue(m, subject="park-1", inputs=inputs)
    assert cert.claim.backing_doi == DOI
    assert cert.claim.values["proposed_bilateral_benefit"] is True
    assert c.verify(cert, m, inputs) is True
    assert c.verify(cert, m, {**inputs, "cost_y": 1.6}) is False
    assert c.verify(cert, m, {**inputs, "flow_y": 5}) is False


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
