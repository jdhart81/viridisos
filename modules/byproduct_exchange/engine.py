"""Byproduct Exchange Corridor kernel — Reciprocity Corridor (RC, Run-128).

A circular-economy screen for a TWO-WAY exchange between two partners, for example two
plants that each send the other a byproduct, residue, heat or water stream it would
otherwise pay to dispose of or buy virgin. It answers: does the exchange leave both
partners strictly better off, at what flow ratios, and what split does the symmetric Nash
bargaining rule pick at a given total flow.

Backing: Zenodo 10.5281/zenodo.21971047; viridis-canon series/RC/PaperFormalization.lean
(Lean 4.28.0, Mathlib 8f9d9cff), byte-identical to the certified candidate of
certificates/Run-128 (Comparator dual-kernel certificate, receipt
Run-128-ReciprocityCorridor-Comparator-attempt-1). Theorems relied on, namespace
``Viridis.Run128.PaperFormalization``:

  bilateral_benefit_iff_reciprocity_corridor        (C1)
  strict_corridor_nonempty_iff_product_condition     (C2)
  ratio_interval_nonempty_iff_product_condition      (support)
  share_payoff_identities, qL_lt_qU_iff_product_condition (support)
  share_coordinate_corridor_equivalence             (share coordinates)
  nash_midpoint_unique_maximizer                     (C3)
  bandwidth_scaling_cannot_restore_feasibility       (C4)

No sorry, admit, native_decide or new axiom; standard axioms only (propext,
Classical.choice, Quot.sound). None of them uses the Intelligence Bound, Landauer's
principle or any thermodynamic premise: the formal statements are unit-free real algebra.

Spec (numbered invariants)
--------------------------
I1  Model. One period, two partners X and Y. X sends flow x > 0 to Y, Y sends flow y > 0
    to X (same or different materials; units are the user's). Known constant per-unit
    coefficients, all > 0: v_x = X's value per unit of y received (e.g. avoided virgin
    purchase or disposal), c_x = X's cost per unit of x sent (processing, transport,
    forgone sale), and v_y, c_y likewise for Y. Payoffs are linear with zero disagreement
    utility: u_x = v_x*y - c_x*x, u_y = v_y*x - c_y*y. No externalities.
I2  Corridor (C1): u_x > 0 and u_y > 0  <=>  c_x/v_x < y/x < v_y/c_y.
I3  Feasibility (C2, C4): some positive (x, y) benefits both  <=>  c_x*c_y < v_x*v_y.
    If c_x*c_y >= v_x*v_y, NO positive flows benefit both, at any scale.
I4  Share coordinates (share_payoff_identities, share_coordinate_corridor_equivalence):
    with R = x + y > 0 and q = y/R, q_L = c_x/(v_x+c_x), q_U = v_y/(v_y+c_y):
    u_x = R(v_x+c_x)(q - q_L), u_y = R(v_y+c_y)(q_U - q); both > 0 <=> q_L < q < q_U;
    q_L < q_U <=> c_x*c_y < v_x*v_y.
I5  Nash split (C3): if feasible and R > 0, q* = (q_L + q_U)/2 is the UNIQUE maximiser of
    u_x*u_y over all shares q, with u_x* = R(v_x+c_x)(q_U-q_L)/2 and
    u_y* = R(v_y+c_y)(q_U-q_L)/2.
I6  Scale (C4): the set of mutually beneficial shares does not depend on R, and both
    payoffs are linear in R.

Not claimed: one-way exchanges paid in money (y = 0 is outside the model), nonlinear or
capacity-limited costs, more than two partners, multi-period or stock dynamics, any mass or
energy balance, recovery fractions, avoided emissions or landfill impacts, any
thermodynamic or Intelligence-Bound quantity, that partners will in fact bargain to the
Nash split, or that the supplied coefficients are correct. The canon paper motivates flows
as transfer entropy; this module uses only the unit-free algebra and not that measurement
layer. The canon catalog lists the package as 'working', not spine-admitted.

Pure, deterministic — recomputable for certification (A-2).
"""

from __future__ import annotations

import math
from typing import Optional

SCOPE = "two-partner one-period linear-payoff exchange with zero disagreement utility"

CLAIM_BOUNDARY = (
    "Exact for the supplied positive per-unit values and costs under linear payoffs and no "
    "externalities. It is not a mass or energy balance, does not cover one-way paid "
    "transfers, more than two partners or multi-period dynamics, and does not show that "
    "the coefficients are right or that partners will adopt the Nash split."
)


def _real(name: str, value: object) -> float:
    if isinstance(value, bool):
        raise ValueError(f"{name} must be a finite real number")
    try:
        x = float(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{name} must be a finite real number") from exc
    if not math.isfinite(x):
        raise ValueError(f"{name} must be a finite real number")
    return x


def _positive(name: str, value: object) -> float:
    x = _real(name, value)
    if not x > 0:
        raise ValueError(f"{name} must be > 0")
    return x


def _coefficients(value_x, value_y, cost_x, cost_y):
    return (_positive("value_x", value_x), _positive("value_y", value_y),
            _positive("cost_x", cost_x), _positive("cost_y", cost_y))


def payoffs(value_x, value_y, cost_x, cost_y, flow_x, flow_y) -> tuple[float, float]:
    """I1: u_x = v_x*y - c_x*x and u_y = v_y*x - c_y*y."""
    vx, vy, cx, cy = _coefficients(value_x, value_y, cost_x, cost_y)
    x = _positive("flow_x", flow_x)
    y = _positive("flow_y", flow_y)
    return vx * y - cx * x, vy * x - cy * y


def share_bounds(value_x, value_y, cost_x, cost_y) -> tuple[float, float]:
    """I4: q_L = c_x/(v_x+c_x), q_U = v_y/(v_y+c_y)."""
    vx, vy, cx, cy = _coefficients(value_x, value_y, cost_x, cost_y)
    return cx / (vx + cx), vy / (vy + cy)


def nash_product(value_x, value_y, cost_x, cost_y, total_flow, share) -> float:
    """u_x * u_y at total flow R and y-share q (x = R(1-q), y = Rq)."""
    vx, vy, cx, cy = _coefficients(value_x, value_y, cost_x, cost_y)
    r = _real("total_flow", total_flow)
    q = _real("share", share)
    x, y = r * (1 - q), r * q
    return (vx * y - cx * x) * (vy * x - cy * y)


def exchange_corridor(*, value_x: object, value_y: object, cost_x: object, cost_y: object,
                      total_flow: object, flow_x: Optional[object] = None,
                      flow_y: Optional[object] = None) -> dict:
    """The corridor, feasibility test and Nash split the theorems certify (I2–I6)."""
    vx, vy, cx, cy = _coefficients(value_x, value_y, cost_x, cost_y)
    r = _positive("total_flow", total_flow)
    if (flow_x is None) != (flow_y is None):
        raise ValueError("give both flow_x and flow_y to assess a proposed exchange, or neither")

    lower_ratio, upper_ratio = cx / vx, vy / cy
    q_lo, q_hi = cx / (vx + cx), vy / (vy + cy)
    feasible = cx * cy < vx * vy  # I3 product condition
    out = {
        "corridor_nonempty": feasible,
        "product_margin": vx * vy - cx * cy,
        "flow_ratio_lower": lower_ratio,
        "flow_ratio_upper": upper_ratio,
        "y_share_lower": q_lo,
        "y_share_upper": q_hi,
        "nash_y_share": None,
        "nash_x_flow": None,
        "nash_y_flow": None,
        "nash_payoff_x": None,
        "nash_payoff_y": None,
    }
    if feasible:
        q = (q_lo + q_hi) / 2.0
        delta = q_hi - q_lo
        out.update({
            "nash_y_share": q,
            "nash_x_flow": r * (1.0 - q),
            "nash_y_flow": r * q,
            "nash_payoff_x": r * (vx + cx) * delta / 2.0,
            "nash_payoff_y": r * (vy + cy) * delta / 2.0,
        })
    if flow_x is not None:
        x = _positive("flow_x", flow_x)
        y = _positive("flow_y", flow_y)
        ux, uy = vx * y - cx * x, vy * x - cy * y
        ratio = y / x
        out.update({
            "proposed_payoff_x": ux,
            "proposed_payoff_y": uy,
            "proposed_flow_ratio": ratio,
            "proposed_in_corridor": lower_ratio < ratio < upper_ratio,
            "proposed_bilateral_benefit": ux > 0 and uy > 0,
        })
    out.update({
        "scale_can_restore_feasibility": False,
        "scope": SCOPE,
        "mass_balance_covered": False,
        "claim_boundary": CLAIM_BOUNDARY,
    })
    return out
