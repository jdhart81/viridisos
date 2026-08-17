"""Restoration kernel — Forest Nucleation Theorem (FNT, Run-061 / DOI 20982979).

Headline: "concentrate, don't broadcast." On a site with Restoration Nucleation Number
Θ = σ/Δμ > 1, uniform broadcast seeding maximizes perimeter, holds every patch sub-critical,
and colonizes ~0 area; the same seed mass deposited in n*-sized clusters nucleates and spreads.

  Θ  = σ / Δμ           (edge/establishment cost σ over site suitability Δμ)
  n* = (σ / Δμ)³         critical nucleus (cluster) size — deposit seed in n*-sized packets

Recommendation (the go/no-go the product sells):
  Θ ≲ 0.5  GREEN  — passive/assisted natural regeneration; don't spend on planting
  0.5<Θ≤1  AMBER  — assisted clustering advised
  Θ > 1    RED    — broadcast fails; cluster at n* or waste the capital

Pure, deterministic — recomputable for certification (A-2). σ, Δμ are measured inputs.
"""

from __future__ import annotations


def nucleation_number(sigma: float, delta_mu: float) -> float:
    if delta_mu <= 0:
        raise ValueError("site suitability Δμ must be > 0")
    if sigma < 0:
        raise ValueError("edge cost σ must be ≥ 0")
    return sigma / delta_mu


def critical_nucleus(sigma: float, delta_mu: float) -> float:
    return nucleation_number(sigma, delta_mu) ** 3


def recommendation(theta: float) -> str:
    if theta <= 0.5:
        return "GREEN"      # passive
    if theta <= 1.0:
        return "AMBER"      # assisted clustering
    return "RED"            # must cluster at n*


def design(sigma: float, delta_mu: float) -> dict:
    theta = nucleation_number(sigma, delta_mu)
    return {
        "nucleation_number": round(theta, 9),
        "critical_nucleus_n_star": round(critical_nucleus(sigma, delta_mu), 9),
        "recommendation": recommendation(theta),
        "broadcast_fails": theta > 1.0,
    }
