"""Restoration kernel — Forest Nucleation Theorem (FNT, Run-061 / DOI 20982979).

What the theorem proves (viridis-canon series/ForestNucleation.lean, `critical_nucleus` and
`barrier_half_identity`): treat a planted cluster of n = r³ trees with free energy

  G(r) = −Δμ·r³ + a·σ·r²

where Δμ > 0 is the per-tree driving force (site suitability), σ > 0 the edge cost and a > 0
a shape factor. Then

  r* = 2aσ / (3Δμ)          the unique barrier top on r ≥ 0
  n* = r*³                  the critical cluster size
  ΔG* = ½·Δμ·n*             the barrier height

A cluster smaller than n* sits on the uphill side of the barrier (expected to dissolve); one
at or above n* is past the barrier top (expected to grow). That go/no-go is the decision this
module supports, within the model.

Not from the theorem: the ratio Θ = σ/Δμ is reported for convenience only. Earlier versions
graded Θ into GREEN/AMBER/RED at 0.5 and 1 and said broadcast seeding fails above Θ = 1; those
cut-offs are not in the theorem and have been removed. σ, Δμ and a are user inputs that must be
justified for the site; nothing here is field-validated.

Pure, deterministic — recomputable for certification (A-2).
"""

from __future__ import annotations

import math
from typing import Optional


def _positive(name: str, value: float) -> float:
    v = float(value)
    if not math.isfinite(v) or v <= 0:
        raise ValueError(f"{name} must be a finite number > 0")
    return v


def critical_radius(sigma: float, delta_mu: float, shape_factor: float = 1.0) -> float:
    """r* = 2aσ / (3Δμ)."""
    s = _positive("edge cost σ", sigma)
    d = _positive("site suitability Δμ", delta_mu)
    a = _positive("shape factor a", shape_factor)
    return 2.0 * a * s / (3.0 * d)


def critical_nucleus(sigma: float, delta_mu: float, shape_factor: float = 1.0) -> float:
    """n* = r*³ = (2aσ / (3Δμ))³."""
    return critical_radius(sigma, delta_mu, shape_factor) ** 3


def barrier_height(sigma: float, delta_mu: float, shape_factor: float = 1.0) -> float:
    """ΔG* = G(r*) = ½·Δμ·n*."""
    return 0.5 * float(delta_mu) * critical_nucleus(sigma, delta_mu, shape_factor)


def design(sigma: float, delta_mu: float, shape_factor: float = 1.0,
           cluster_size: Optional[float] = None) -> dict:
    n_star = critical_nucleus(sigma, delta_mu, shape_factor)
    out = {
        "critical_radius_r_star": round(critical_radius(sigma, delta_mu, shape_factor), 9),
        "critical_nucleus_n_star": round(n_star, 9),
        "barrier_height": round(barrier_height(sigma, delta_mu, shape_factor), 9),
        "edge_to_suitability_ratio": round(float(sigma) / float(delta_mu), 9),
        "claim_boundary": (
            "Within the nucleation model only: n* is the cluster size at the barrier top. "
            "σ, Δμ and the shape factor are user inputs; the result is not field-validated."
        ),
    }
    if cluster_size is not None:
        n = _positive("cluster size", cluster_size)
        out["cluster_size"] = round(n, 9)
        out["cluster_reaches_n_star"] = n >= n_star
        out["go_no_go"] = "GO" if n >= n_star else "NO_GO"
    return out
