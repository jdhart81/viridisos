"""Deterministic Carbon Continuity threshold kernel.

This ports the exact two-pool threshold from the Carbon Continuity paper into a
small preview-safe runtime. It deliberately does not estimate probabilities,
price insurance, rate credits, or infer coefficients from field observations.
"""

from __future__ import annotations

import math


CLAIM_BOUNDARY = (
    "Model-scoped decision support only. Coefficients must be supplied and "
    "empirically justified by the user; this output is not a carbon credit, "
    "project rating, insurance price, underwriting decision, or causal field claim."
)


def _coefficient(name: str, value: object) -> float:
    try:
        number = float(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{name} must be a finite real number") from exc
    if not math.isfinite(number):
        raise ValueError(f"{name} must be a finite real number")
    return number


def evaluate_threshold(*, a: object, d: object, r: object, p: object) -> dict:
    """Evaluate the exact local continuity threshold for supplied coefficients.

    Valid domain:
      0 <= a,d < 1  (within-pool retention)
      r,p > 0       (cross-pool coupling)
    """
    a_value = _coefficient("a", a)
    d_value = _coefficient("d", d)
    r_value = _coefficient("r", r)
    p_value = _coefficient("p", p)

    if not 0.0 <= a_value < 1.0:
        raise ValueError("a must satisfy 0 <= a < 1")
    if not 0.0 <= d_value < 1.0:
        raise ValueError("d must satisfy 0 <= d < 1")
    if r_value <= 0.0:
        raise ValueError("r must be > 0")
    if p_value <= 0.0:
        raise ValueError("p must be > 0")

    loop_gain = r_value * p_value
    leakage_product = (1.0 - a_value) * (1.0 - d_value)
    continuity_number = loop_gain / leakage_product
    threshold_met = loop_gain > leakage_product or math.isclose(
        loop_gain,
        leakage_product,
        rel_tol=1e-12,
        abs_tol=1e-15,
    )

    # The proof's explicit positive witness: L=r and D=1-a.
    living = r_value
    durable = 1.0 - a_value
    next_living = a_value * living + r_value * durable
    next_durable = p_value * living + d_value * durable

    return {
        "a": a_value,
        "d": d_value,
        "r": r_value,
        "p": p_value,
        "loop_gain": loop_gain,
        "leakage_product": leakage_product,
        "continuity_number": continuity_number,
        "threshold_met": threshold_met,
        "regime": (
            "CONTINUITY_CAPABLE_WITHIN_MODEL"
            if threshold_met
            else "DEPLETING_WITHIN_MODEL"
        ),
        "witness_living": living,
        "witness_durable": durable,
        "witness_next_living": next_living,
        "witness_next_durable": next_durable,
        "witness_nondecreasing": (
            threshold_met
            and next_living + 1e-12 >= living
            and next_durable + 1e-12 >= durable
        ),
        "market_use": "decision_support_only",
        "formal_claim_type": "supplied_coefficient_threshold_evaluation",
        "market_claim_status": "MODEL_OUTPUT_ONLY",
        "empirically_calibrated": False,
        "underwriting_advice": False,
        "credit_quantity_tco2e": None,
        "claim_boundary": CLAIM_BOUNDARY,
    }
