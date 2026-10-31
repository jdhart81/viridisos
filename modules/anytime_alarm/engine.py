"""Anytime-valid Monitoring Alarm kernel — Anytime Change Certificate (ACC, Run-129).

Backing: Zenodo 10.5281/zenodo.21971041; viridis-canon series/ACC (Lean 4.28.0, Mathlib
8f9d9cff). Theorems relied on, namespace ``Viridis.Run129.PaperFormalization``:

  hasSum_changePrior                        (PaperFormalization/Prior.lean)
  anytime_change_mixture_martingale  (C1)   (PaperFormalization/NullMartingale.lean)
  ville_inequality, anytime_change_ville_certificate (C2)        (NullMartingale.lean)
  change_component_dominance_and_penalty (C3)                     (Dominance.lean)
  bounded_overshoot_expected_delay (C4), wald_identity            (Wald.lean)

No sorry, admit or axiom occurs in any ACC Lean file; the canon's axiom sweep lists only
propext, Classical.choice and Quot.sound.

Spec (numbered invariants)
--------------------------
I1  Model. Observations X_1, X_2, ... are 0/1. NULL (no change): X_i iid Bernoulli(p0).
    After a change at time nu: X_i iid Bernoulli(p1) for i >= nu. p0 and p1 are fixed in
    advance (not fitted to the same data), 0 < p0, p1 < 1, p0 != p1.
I2  Likelihood ratio: Lambda_i = p1/p0 if X_i = 1, else (1-p1)/(1-p0). Under the null,
    E0[Lambda_i | past] = 1, the only property C1 and C2 use.
I3  Prior over the change time (fixed by the Lean file, no free parameters):
    pi_k = 1/(k(k+1)), k >= 1, with tail t_n = 1/(n+1); it sums to 1.
I4  Statistic (Equation 2): A_0 = 0, A_n = Lambda_n * (A_{n-1} + pi_n), M_n = A_n + t_n,
    so M_0 = 1. Under the null (M_n) is a non-negative mean-one martingale (C1).
I5  Stopping rule: alarm at the first n with M_n >= 1/alpha. Ville (C2):
    P0(ever alarm) <= alpha, i.e. the false-alarm probability is at most alpha at every
    sample size and under continuous monitoring with optional stopping.
I6  Delay (C3 + C4, composed here): the alarm is never later than the change-at-nu
    component's, which needs log-evidence a_nu = log(1/alpha) + log(nu(nu+1)). With
    D = KL(Bern(p1) || Bern(p0)) > 0 and z_max = max log Lambda, the component's
    first-crossing count N satisfies a_nu/D <= E1[N] < (a_nu + z_max)/D, so the expected
    number of post-change observations until the mixture alarms is < (a_nu + z_max)/D.
    C4 ASSUMES E1[N] < infinity (the Wald integrability condition) rather than proving it.
    The lower bound a_nu/D is for the component only, not for the mixture.

Not claimed: that real observations are independent or identically distributed, that
p0 is the true pre-change rate, that p1 is the true post-change rate (a mis-specified p1
weakens detection; a mis-specified p0 voids the false-alarm guarantee), detection of
gradual drift, or anything about the ecological cause of a change. The canon catalog
lists this package as 'working', not spine-admitted.

Pure, deterministic — recomputable for certification (A-2). Computed in log space so
long sequences cannot overflow.
"""

from __future__ import annotations

import math
from typing import Optional, Sequence

MAX_OBSERVATIONS = 100_000

SCOPE = "single frozen Bernoulli likelihood-ratio process under the declared iid null"

CLAIM_BOUNDARY = (
    "The false-alarm bound holds only if, before any change, the observations really are "
    "independent Bernoulli(p0) draws. It says nothing about the cause of a change."
)


def _prob(name: str, value: object) -> float:
    if isinstance(value, bool):
        raise ValueError(f"{name} must be a number strictly between 0 and 1")
    try:
        x = float(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{name} must be a number strictly between 0 and 1") from exc
    if not (math.isfinite(x) and 0.0 < x < 1.0):
        raise ValueError(f"{name} must be a number strictly between 0 and 1")
    return x


def _observations(values) -> list[int]:
    if isinstance(values, (str, bytes)) or not hasattr(values, "__iter__"):
        raise ValueError("observations must be a list of 0/1 values")
    out = []
    for v in values:
        if isinstance(v, bool) or v not in (0, 1) or not isinstance(v, int):
            raise ValueError("every observation must be the integer 0 or 1")
        out.append(int(v))
    if len(out) > MAX_OBSERVATIONS:
        raise ValueError(f"at most {MAX_OBSERVATIONS} observations")
    return out


def _logaddexp(a: float, b: float) -> float:
    if a == -math.inf:
        return b
    if b == -math.inf:
        return a
    hi, lo = (a, b) if a >= b else (b, a)
    return hi + math.log1p(math.exp(lo - hi))


def change_prior(k: int) -> float:
    """pi_k = 1 / (k (k + 1))."""
    return 1.0 / (k * (k + 1))


def kl_bernoulli(p1: float, p0: float) -> float:
    """D = KL(Bern(p1) || Bern(p0)) = E1[log Lambda]."""
    return p1 * math.log(p1 / p0) + (1 - p1) * math.log((1 - p1) / (1 - p0))


def evidence_boundary(alpha: float, nu: int) -> float:
    """a_nu = log(1/alpha) + log(nu (nu + 1))."""
    return math.log(1.0 / alpha) + math.log(nu * (nu + 1))


def delay_bounds(*, p0: object, p1: object, alpha: object, change_time: int = 1) -> dict:
    """C3 + C4: expected post-change observations until alarm, for a change at nu."""
    q0, q1, a = _prob("p0", p0), _prob("p1", p1), _prob("alpha", alpha)
    if q0 == q1:
        raise ValueError("p0 and p1 must differ")
    if isinstance(change_time, bool) or not isinstance(change_time, int) or change_time < 1:
        raise ValueError("change_time must be an integer >= 1")
    d = kl_bernoulli(q1, q0)
    z_max = max(math.log(q1 / q0), math.log((1 - q1) / (1 - q0)))
    a_nu = evidence_boundary(a, change_time)
    return {
        "change_time": change_time,
        "evidence_boundary": a_nu,
        "kl_divergence": d,
        "z_max": z_max,
        "component_expected_delay_lower": a_nu / d,
        "expected_delay_upper_bound": (a_nu + z_max) / d,
        "assumes_wald_integrability": True,
    }


def monitor(*, observations: Sequence[int], p0: object, p1: object, alpha: object,
            change_time: Optional[int] = None) -> dict:
    """Run the mixture monitor over the sequence and apply the 1/alpha stopping rule."""
    xs = _observations(observations)
    q0, q1, a = _prob("p0", p0), _prob("p1", p1), _prob("alpha", alpha)
    if q0 == q1:
        raise ValueError("p0 and p1 must differ")
    log_up, log_down = math.log(q1 / q0), math.log((1 - q1) / (1 - q0))
    log_threshold = math.log(1.0 / a)

    log_acc = -math.inf                      # log A_0 = log 0
    log_current = 0.0                        # log M_0 = log 1
    log_max = 0.0
    alarm_index = None
    for n, x in enumerate(xs, start=1):
        log_acc = (log_up if x else log_down) + _logaddexp(log_acc, -math.log(n * (n + 1)))
        log_current = _logaddexp(log_acc, -math.log(n + 1))
        log_max = max(log_max, log_current)
        if alarm_index is None and log_current >= log_threshold:
            alarm_index = n

    def _exp(v: float) -> Optional[float]:
        return math.exp(v) if v < 700 else None

    out = {
        "current_mixture_evidence": _exp(log_current),
        "maximum_mixture_evidence": _exp(log_max),
        "log_current_mixture_evidence": log_current,
        "log_maximum_mixture_evidence": log_max,
        "alarm_threshold": 1.0 / a,
        "alarmed": alarm_index is not None,
        "alarm_index": alarm_index,
        "observations_processed": len(xs),
        "false_alarm_probability_bound": a,
        "scope": SCOPE,
        "claim_boundary": CLAIM_BOUNDARY,
    }
    out["delay"] = delay_bounds(p0=q0, p1=q1, alpha=a,
                                change_time=1 if change_time is None else change_time)
    return out
