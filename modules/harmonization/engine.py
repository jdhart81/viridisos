"""Harmonization kernel — Gaian Harmonization Theorem (GHT, DOI 21168212).

What the theorem proves (viridis-canon series/GaianHarmonization.lean,
`ght_market_clears` and `ght_strong_duality_decentralized_eq_centralized`):

  N stewards each choose an effort x_i with a local quadratic cost (a_i / 2)·(x_i − b_i)²,
  where a_i > 0 is the cost curvature and b_i the steward's ideal effort. The group must
  hit a shared total Σ x_i = X. Broadcast one price λ and each steward privately picks its
  best response x_i = b_i − λ / a_i. Then

    λ* = (Σ b_i − X) / Σ (1 / a_i)        clears: the best responses add up to X exactly
    x*_i = b_i − λ* / a_i                 and no allocation meeting X has lower total cost

This module computes exactly those quantities and checks them numerically. It makes no
claim beyond the model: the cost curvatures, ideals and target are the user's inputs and
are not validated here. The quadratic-cost result is a standard one (decentralization by a
single Lagrange price); the canon's contribution is the Lean formalization.

Pure, deterministic — recomputable for certification (A-2).
"""

from __future__ import annotations

import math
from typing import Sequence


def _finite_list(name: str, values: Sequence[float]) -> list[float]:
    out = [float(v) for v in values]
    if not out:
        raise ValueError(f"{name} needs at least one steward")
    if not all(math.isfinite(v) for v in out):
        raise ValueError(f"{name} must be finite real numbers")
    return out


def clearing_price(curvatures: Sequence[float], ideals: Sequence[float], target: float) -> float:
    """λ* = (Σ b − X) / Σ (1/a). Requires every curvature a_i > 0."""
    a = _finite_list("curvatures", curvatures)
    b = _finite_list("ideals", ideals)
    if len(a) != len(b):
        raise ValueError("curvatures and ideals must have one entry per steward")
    if any(ai <= 0 for ai in a):
        raise ValueError("every curvature must be > 0")
    x_total = float(target)
    if not math.isfinite(x_total):
        raise ValueError("target must be a finite real number")
    return (sum(b) - x_total) / sum(1.0 / ai for ai in a)


def best_response(curvature: float, ideal: float, price: float) -> float:
    """x_i = b_i − λ / a_i, the minimiser of (a_i/2)(x − b_i)² + λ·x."""
    return ideal - price / curvature


def total_cost(curvatures: Sequence[float], ideals: Sequence[float], allocation: Sequence[float]) -> float:
    """J(x) = Σ (a_i / 2)(x_i − b_i)²."""
    return sum((ai / 2.0) * (xi - bi) ** 2 for ai, bi, xi in zip(curvatures, ideals, allocation))


def harmonize(curvatures: Sequence[float], ideals: Sequence[float], target: float) -> dict:
    lam = clearing_price(curvatures, ideals, target)
    a = [float(v) for v in curvatures]
    b = [float(v) for v in ideals]
    alloc = [best_response(ai, bi, lam) for ai, bi in zip(a, b)]
    return {
        "shadow_price": round(lam, 9),
        "allocation": [round(x, 9) for x in alloc],
        "total": round(sum(alloc), 9),
        "target": round(float(target), 9),
        "market_clears": math.isclose(sum(alloc), float(target), rel_tol=1e-9, abs_tol=1e-9),
        "total_cost": round(total_cost(a, b, alloc), 9),
        "claim_boundary": (
            "Within the quadratic-cost model only: the broadcast price makes the stewards' "
            "best responses meet the target, at the lowest total cost of any allocation that "
            "meets it. Cost curvatures, ideals and the target are user inputs, not validated."
        ),
    }
