"""D-Score Weight-Robustness kernel — D-Score Weight-Charter Certificate (DSWC, Run-132).

Backing: Zenodo 10.5281/zenodo.22236741; viridis-canon series/DSWC/ViridisRun132.lean,
namespace ``Viridis.DScore.WeightCharter`` (Comparator receipt
Run-132-DScoreWeightCharter-Engine3-Correction-r1-attempt-3). Theorems relied on:

  tv_range_certificate    |score w z - score v z| <= tv w v * span z
  strict_rank_stability   tv w v <= rho and rho * span z < score v z  =>  0 < score w z
  charter_nonvacuous      w0 = (0.6, 0.4), w = (0.3, 0.7), z = (0, 5): tv = 0.3, drift = 1.5

These contain no sorry, admit or axiom (the sorry-stubs in contracts/VERIFICATION_STATEMENT.lean
are the frozen statement contract, not the proof file).

Spec (numbered invariants)
--------------------------
I1  Weights. reference_weights v and alternative_weights w are probability vectors of the
    same length n >= 1: every entry >= 0 and the entries sum to 1 (tolerance 1e-9).
I2  Score: score(w, z) = sum_i w_i * z_i for any real indicator vector z of length n.
I3  tv(w, v) = (1/2) * sum_i |w_i - v_i|; span(z) = max(z) - min(z).
I4  Drift bound (tv_range_certificate): for each parcel, |score(w, z) - score(v, z)| <=
    tv(w, v) * span(z). Reported per parcel as drift_bound with the actual drift.
I5  Ranking (strict_rank_stability, applied to the contrast z = z_A - z_B, whose score is
    score(A) - score(B)): with gap = score(v, z) and bound = tv(w, v) * span(z),
    |gap| > bound guarantees that A and B keep their order under w AND under every weight
    vector within that total-variation distance of v. ranking_robust is that strict test.
    robust_tv_radius = |gap| / span(z) is the TV distance below which the order is
    guaranteed (null when span(z) = 0 and gap != 0: no weights can flip it).
I6  If ranking_robust is false the order MAY flip; the bound is only sufficient. The
    module reports whether it actually flips under the supplied w.

Not claimed: the D-Score's ecological validity is NOT proven. Nothing here says the
indicators measure ecosystem condition, that the reference weights are right, that the
indicators are comparably scaled, or that the ranking is a good decision. The theorem is
about the arithmetic of weighted sums only. The Lean file contains no sharpness theorem
beyond the charter_nonvacuous example, where the bound is attained.

Pure, deterministic — recomputable for certification (A-2).
"""

from __future__ import annotations

import math
from typing import Sequence

SUM_TOL = 1e-9

CLAIM_BOUNDARY = (
    "Arithmetic of weighted sums only. The D-Score's ecological validity is not proven: "
    "this does not show the indicators measure ecosystem condition, that any weighting is "
    "correct, or that a ranking should drive a decision."
)


def _vector(name: str, values: Sequence[float]) -> list[float]:
    if isinstance(values, (str, bytes)) or not hasattr(values, "__iter__"):
        raise ValueError(f"{name} must be a list of numbers")
    out = []
    for v in values:
        if isinstance(v, bool):
            raise ValueError(f"{name} must contain numbers, not booleans")
        try:
            x = float(v)
        except (TypeError, ValueError) as exc:
            raise ValueError(f"{name} must contain finite real numbers") from exc
        if not math.isfinite(x):
            raise ValueError(f"{name} must contain finite real numbers")
        out.append(x)
    if not out:
        raise ValueError(f"{name} needs at least one entry")
    return out


def _simplex(name: str, values: Sequence[float]) -> list[float]:
    w = _vector(name, values)
    if any(x < 0 for x in w):
        raise ValueError(f"{name} must be non-negative")
    if abs(math.fsum(w) - 1.0) > SUM_TOL:
        raise ValueError(f"{name} must sum to 1")
    return w


def score(weights: Sequence[float], z: Sequence[float]) -> float:
    return math.fsum(wi * zi for wi, zi in zip(weights, z))


def total_variation(w: Sequence[float], v: Sequence[float]) -> float:
    return 0.5 * math.fsum(abs(a - b) for a, b in zip(w, v))


def span(z: Sequence[float]) -> float:
    return max(z) - min(z)


def weight_robustness(*, reference_weights: Sequence[float], alternative_weights: Sequence[float],
                      parcel_a: Sequence[float], parcel_b: Sequence[float]) -> dict:
    """Drift bounds and ranking robustness for two parcels under disputed weights (I1–I6)."""
    v = _simplex("reference_weights", reference_weights)
    w = _simplex("alternative_weights", alternative_weights)
    za = _vector("parcel_a", parcel_a)
    zb = _vector("parcel_b", parcel_b)
    n = len(v)
    if not (len(w) == len(za) == len(zb) == n):
        raise ValueError("weights and parcel indicators must all have the same length")

    tv = total_variation(w, v)

    def parcel(z: list[float]) -> dict:
        ref, alt = score(v, z), score(w, z)
        return {"score_reference": ref, "score_alternative": alt,
                "drift": abs(alt - ref), "drift_bound": tv * span(z)}

    contrast = [a - b for a, b in zip(za, zb)]
    gap_ref = score(v, contrast)
    gap_alt = score(w, contrast)
    contrast_span = span(contrast)
    bound = tv * contrast_span
    if contrast_span > 0:
        radius = abs(gap_ref) / contrast_span
    else:
        radius = None if gap_ref != 0 else 0.0   # None: no TV distance can flip the order
    ref_order = (gap_ref > 0) - (gap_ref < 0)
    alt_order = (gap_alt > 0) - (gap_alt < 0)
    leader = {1: "A", -1: "B", 0: "tie"}
    return {
        "total_variation": tv,
        "parcel_a": parcel(za),
        "parcel_b": parcel(zb),
        "contrast_span": contrast_span,
        "gap_reference": gap_ref,
        "gap_alternative": gap_alt,
        "gap_drift_bound": bound,
        "ranking_robust": abs(gap_ref) > bound,
        "robust_tv_radius": radius,
        "leader_reference": leader[ref_order],
        "leader_alternative": leader[alt_order],
        "order_flipped_under_alternative": ref_order != alt_order,
        "ecological_validity_proven": False,
        "claim_boundary": CLAIM_BOUNDARY,
    }
