"""Afforestation kernel — Afforestation Stewardship Theorem (AST, DOI 21168224).

Headline results: a cubic optimal-seeding law, a factor-8 site-prep lever, and an
IB seeding-rate ceiling. Complements FNT (restoration): FNT says *where/how* to cluster,
AST says *how much* to seed and how site-prep moves the optimum.

  optimal density  d* = k · (prep · Δμ / σ)³       cubic law (site-prep enters cubically → up to ×8)
  site-prep lever  bounded so prep ∈ [1, 2] ⇒ density multiplier ∈ [1, 8]
  IB ceiling       seeding rate ≤ rate_max (a Landauer/throughput bound on committing seed-state bits)

Pure, deterministic. Magnitudes are inputs; the cubic structure is the theorem.
"""

from __future__ import annotations


def optimal_density(sigma: float, delta_mu: float, prep: float = 1.0, k: float = 1.0) -> float:
    if sigma <= 0 or delta_mu <= 0:
        raise ValueError("σ and Δμ must be > 0")
    if not (1.0 <= prep <= 2.0):
        raise ValueError("site-prep factor must be in [1, 2] (cubic ⇒ up to ×8)")
    return k * (prep * delta_mu / sigma) ** 3


def site_prep_multiplier(prep: float) -> float:
    """Cubic site-prep lever: prep∈[1,2] → ×[1,8]."""
    return prep ** 3


def seeding_within_ceiling(rate: float, rate_max: float) -> bool:
    """IB seeding-rate ceiling (A-informational bound)."""
    return 0 <= rate <= rate_max


def plan(sigma: float, delta_mu: float, prep: float, rate: float, rate_max: float) -> dict:
    d = optimal_density(sigma, delta_mu, prep)
    return {
        "optimal_density": round(d, 9),
        "site_prep_multiplier": round(site_prep_multiplier(prep), 6),
        "seeding_within_ib_ceiling": seeding_within_ceiling(rate, rate_max),
    }
