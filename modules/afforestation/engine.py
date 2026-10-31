"""Afforestation kernel — Afforestation Stewardship Theorem (AST, DOI 10.5281/zenodo.21168224).

What the theorem proves (viridis-canon series/AfforestationStewardship.lean). For a site with
ecological drive (suitability) Δμ > 0, edge hostility σ > 0 and shape factor a > 0, using the
classical nucleation model shared with Forest Nucleation (FNT):

  n*  = (2aσ / (3Δμ))³                 critical nucleus (trees), definition `nStar`
  ΔG* = 4(aσ)³ / (27Δμ²) = ½·Δμ·n*      nucleation barrier, `homogeneous_limit_recovers_fnt`
  e   = C·(3Δμ / (2aσ))³ = C / n*       seeding efficiency (established canopy per seed), `eff`

and two levers on e:

  • scaling the drive Δμ by t multiplies e by t³   (`establishment_efficiency_cubic_in_drive_over_tension`)
  • halving the edge hostility σ multiplies e by 8 (`site_prep_halving_sigma_eightfolds_efficiency`)

Not used here: the theorem file's `sower_IB_ceiling` only rearranges an assumed premise
(rate·k_B·T·ln 2 ≤ P·D). The Intelligence Bound is a conjecture, not a proven constraint, so it
is not a product check. Earlier versions computed density as k·(prep·Δμ/σ)³, which drops the
theorem's (2a/3)³ factor, and applied that IB ceiling; both are removed.

σ, Δμ, a and C are user inputs that must be justified for the site; nothing here is
field-validated. Pure, deterministic — recomputable for certification (A-2).
"""

from __future__ import annotations

import math

DRIVE_CUBIC_EXPONENT = 3      # e(tΔμ) = t³·e(Δμ)
HALVED_EDGE_MULTIPLIER = 8.0  # e(σ/2) = 8·e(σ)


def _positive(name: str, value: float) -> float:
    v = float(value)
    if not math.isfinite(v) or v <= 0:
        raise ValueError(f"{name} must be a finite number > 0")
    return v


def critical_nucleus(sigma: float, delta_mu: float, shape_factor: float = 1.0) -> float:
    """n* = (2aσ / (3Δμ))³."""
    s = _positive("edge hostility σ", sigma)
    d = _positive("site suitability Δμ", delta_mu)
    a = _positive("shape factor a", shape_factor)
    return (2.0 * a * s / (3.0 * d)) ** 3


def barrier_height(sigma: float, delta_mu: float, shape_factor: float = 1.0) -> float:
    """ΔG* = 4(aσ)³ / (27Δμ²)."""
    s = _positive("edge hostility σ", sigma)
    d = _positive("site suitability Δμ", delta_mu)
    a = _positive("shape factor a", shape_factor)
    return 4.0 * (a * s) ** 3 / (27.0 * d ** 2)


def seeding_efficiency(sigma: float, delta_mu: float, shape_factor: float = 1.0,
                       establishment_constant: float = 1.0) -> float:
    """e = C·(3Δμ / (2aσ))³."""
    s = _positive("edge hostility σ", sigma)
    d = _positive("site suitability Δμ", delta_mu)
    a = _positive("shape factor a", shape_factor)
    c = _positive("establishment constant C", establishment_constant)
    return c * (3.0 * d / (2.0 * a * s)) ** 3


def plan(sigma: float, delta_mu: float, shape_factor: float = 1.0,
         establishment_constant: float = 1.0) -> dict:
    n_star = critical_nucleus(sigma, delta_mu, shape_factor)
    e = seeding_efficiency(sigma, delta_mu, shape_factor, establishment_constant)
    return {
        "critical_nucleus_n_star": round(n_star, 9),
        "barrier_height": round(barrier_height(sigma, delta_mu, shape_factor), 9),
        "seeding_efficiency": round(e, 9),
        "efficiency_if_edge_hostility_halved": round(HALVED_EDGE_MULTIPLIER * e, 9),
        "efficiency_scaling_in_drive": "cubic: multiplying Δμ by t multiplies efficiency by t³",
        "claim_boundary": (
            "Within the nucleation model only. σ, Δμ, the shape factor and the establishment "
            "constant are user inputs; the result is not field-validated and sets no seeding-rate limit."
        ),
    }
