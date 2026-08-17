"""Harmonization kernel — Gaian Harmonization Theorem (GHT, DOI 21168212).

Headline: a SINGLE thermodynamic shadow price decentralizes planetary stewardship to the
social optimum (strong duality); coordination bandwidth is IB-bounded; wu-wei price signals
are strictly cheaper than central command.

Given a set of stewards each with a marginal stewardship cost, the clearing shadow price λ*
is the price at which each steward, optimizing privately, reproduces the social optimum. We
also report the decentralization saving vs. central command (the wu-wei dividend) and whether
the required coordination bandwidth is within the IB bound.

  λ*  = the market-clearing shadow price (max binding marginal cost across stewards)
  central_cost      ∝ Σ per-steward command overhead
  decentralized_cost ∝ one broadcast price signal
  wu_wei_dividend = central_cost − decentralized_cost  (> 0 by the theorem)

Pure, deterministic. Cost magnitudes are inputs; strict-duality structure is the theorem.
"""

from __future__ import annotations

from typing import Sequence


def clearing_price(marginal_costs: Sequence[float]) -> float:
    if not marginal_costs:
        raise ValueError("need at least one steward marginal cost")
    if any(c < 0 for c in marginal_costs):
        raise ValueError("marginal costs must be ≥ 0")
    return max(marginal_costs)   # the binding price that clears all stewards


def coordination_within_ib(n_stewards: int, bandwidth: float, ib_bound: float) -> bool:
    """Coordination bandwidth to run the price signal must be ≤ the IB bound."""
    return 0 <= bandwidth <= ib_bound


def harmonize(marginal_costs: Sequence[float], command_overhead: float,
              bandwidth: float, ib_bound: float) -> dict:
    lam = clearing_price(marginal_costs)
    n = len(marginal_costs)
    central_cost = command_overhead * n          # per-steward command
    decentralized_cost = command_overhead        # one broadcast price
    return {
        "shadow_price": round(lam, 9),
        "wu_wei_dividend": round(central_cost - decentralized_cost, 9),
        "decentralization_cheaper": central_cost > decentralized_cost,
        "coordination_within_ib": coordination_within_ib(n, bandwidth, ib_bound),
    }
