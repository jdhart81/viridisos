"""Precautionary Capacity Ceiling kernel — Precautionary Capacity Reserve (PCR, Run-127).

Backing: Zenodo 10.5281/zenodo.21971046; viridis-canon series/PCR (Lean 4.28.0, Mathlib
8f9d9cff). Theorems relied on, namespace ``Viridis.Run127.PaperFormalization``:

  capacityFloor_violation_prob_le              (PaperFormalization/Targets.lean)
  positive_floor_sharp_two_point_counterexample (PaperFormalization/Targets.lean)
  mean_only_plugin_arbitrarily_unsafe          (PaperFormalization/Targets.lean)
  support: cantelli_lower_tail                 (PaperFormalization/Cantelli.lean)
  support: twoPointLaw, cantelliTwoPoint_*     (PaperFormalization/TwoPoint.lean)

None uses sorry, admit or a new axiom; the canon's axiom check lists only propext,
Classical.choice and Quot.sound.

Spec (numbered invariants)
--------------------------
I1  Model. D is a random, non-negative capacity for one period (for example the stock or
    yield a stand can sustain, or a site's carrying capacity), with finite variance. The
    user supplies its TRUE mean mu and standard deviation sigma, and a violation budget
    alpha with 0 < alpha < 1.
I2  Ceiling: k = sqrt((1 - alpha) / alpha) and d_alpha = max(0, mu - sigma * k)
    (the canon's capacityFloor).
I3  Guarantee (capacityFloor_violation_prob_le, one-sided Cantelli): for EVERY such law of
    D with that mean and standard deviation, P(D < d_alpha) <= alpha. Setting an allowable
    harvest or stocking level at d_alpha means it exceeds the realised capacity with
    probability at most alpha.
I4  Tightness (positive_floor_sharp_two_point_counterexample): when sigma > 0 and
    d_alpha > 0, no larger ceiling has the same guarantee: for every d > d_alpha there is
    a non-negative two-point law with the same mean and variance and P(D < d) > alpha.
    two_point_counterexample() returns the law the proof constructs.
I5  Mean-only rules can fail (mean_only_plugin_arbitrarily_unsafe): knowing only the mean,
    a ceiling at any positive fraction theta of mu can be violated with probability
    arbitrarily close to 1. mean_only_counterexample() returns the proof's two-point law.
    (The Lean statement is phrased through the canon's rate-model ceiling; its positive
    scalars cancel, leaving the capacity event {D < theta * mu}. This module uses no rate
    model, power or temperature.)
I6  capacity_fraction = d_alpha / mu = max(0, 1 - (sigma / mu) * k) for mu > 0 (algebra;
    the canon states the same ratio as capacity_reserve_fraction_eq).

Not claimed: that mu and sigma are known (estimation error from a sample is NOT covered),
dependence across periods or sites, any multi-period or cumulative risk, the shape of the
real distribution, or that alpha is an acceptable risk. The canon catalog lists this
package as 'working', not spine-admitted.

Pure, deterministic — recomputable for certification (A-2).
"""

from __future__ import annotations

import math

SCOPE = "one-period two-moment marginal Cantelli certificate"

CLAIM_BOUNDARY = (
    "Holds for the supplied true mean and standard deviation of a non-negative one-period "
    "capacity. It does not cover estimation error, dependence across periods, or the "
    "ecological suitability of the chosen violation budget."
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


def _check(mean: object, sd: object, alpha: object) -> tuple[float, float, float]:
    mu = _real("mean_capacity", mean)
    sigma = _real("capacity_sd", sd)
    a = _real("alpha", alpha)
    if mu < 0:
        raise ValueError("mean_capacity must be >= 0 (capacity is non-negative)")
    if sigma < 0:
        raise ValueError("capacity_sd must be >= 0")
    if not 0.0 < a < 1.0:
        raise ValueError("alpha must satisfy 0 < alpha < 1")
    return mu, sigma, a


def cantelli_factor(alpha: float) -> float:
    """k = sqrt((1 - alpha) / alpha)."""
    return math.sqrt((1.0 - alpha) / alpha)


def capacity_floor(mean: object, sd: object, alpha: object) -> float:
    """d_alpha = max(0, mu - sigma * sqrt((1 - alpha) / alpha))."""
    mu, sigma, a = _check(mean, sd, alpha)
    return max(0.0, mu - sigma * cantelli_factor(a))


def precautionary_ceiling(*, mean_capacity: object, capacity_sd: object, alpha: object) -> dict:
    """The ceiling the theorem certifies, with its guarantee and the mean-only warning."""
    mu, sigma, a = _check(mean_capacity, capacity_sd, alpha)
    k = cantelli_factor(a)
    discount = sigma * k
    floor = max(0.0, mu - discount)
    return {
        "precautionary_ceiling": floor,
        "absolute_discount": discount,
        "cantelli_factor": k,
        "capacity_fraction": (floor / mu) if mu > 0 else 0.0,
        "violation_probability_bound": a,
        "positive_floor": floor > 0,
        "ceiling_is_sharp": sigma > 0 and floor > 0,
        "mean_only_rule_safe": False,
        "mean_only_warning": (
            "A ceiling set from the mean alone (any fixed fraction of it) has no guarantee: "
            "some non-negative capacity law with that mean violates it with probability "
            "arbitrarily close to 1."
        ),
        "scope": SCOPE,
        "estimation_error_covered": False,
        "claim_boundary": CLAIM_BOUNDARY,
    }


def two_point_counterexample(mean: object, sd: object, alpha: object, ceiling: object) -> dict:
    """The law built in positive_floor_sharp_two_point_counterexample, for a ceiling above d_alpha.

    Returns atoms low < high with P(low) = q, same mean and variance, and P(D < ceiling) >= q > alpha.
    """
    mu, sigma, a = _check(mean, sd, alpha)
    d = _real("ceiling", ceiling)
    floor = max(0.0, mu - sigma * cantelli_factor(a))
    if not (sigma > 0 and floor > 0):
        raise ValueError("the sharpness theorem needs sigma > 0 and a positive floor")
    if not d > floor:
        raise ValueError("ceiling must exceed the certified floor d_alpha")
    low = (floor + min(d, mu)) / 2.0
    gap = mu - low
    high = mu + sigma ** 2 / gap
    q = sigma ** 2 / (sigma ** 2 + gap ** 2)
    return {"low": low, "high": high, "p_low": q, "p_high": 1.0 - q}


def mean_only_counterexample(mean: object, theta: object, beta: object) -> dict:
    """The law built in mean_only_plugin_arbitrarily_unsafe.

    For mu > 0, theta > 0 and beta < 1: mass 1 - eps at 0 and eps at mu / eps, with
    eps = min(1/2, (1 - beta)/2). Its mean is mu and P(D < theta * mu) = 1 - eps > beta.
    """
    mu = _real("mean", mean)
    t = _real("theta", theta)
    b = _real("beta", beta)
    if mu <= 0 or t <= 0 or b >= 1:
        raise ValueError("needs mean > 0, theta > 0 and beta < 1")
    eps = min(0.5, (1.0 - b) / 2.0)
    return {"low": 0.0, "high": mu / eps, "p_low": 1.0 - eps, "p_high": eps}
