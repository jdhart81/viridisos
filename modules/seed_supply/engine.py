"""Seed-Supply Bottleneck Check kernel — Seed-Source Bottleneck Certificate (SSBC, Run-130).

Backing: Zenodo 10.5281/zenodo.21971057; viridis-canon series/SSBC (Lean 4.28.0, Mathlib
8f9d9cff). Theorems relied on, all in namespace ``Viridis.Run130`` (restated verbatim under
``Viridis.Run130.PaperFormalization`` in series/SSBC/PaperFormalization.lean):

  C1 seed_routing_common_fraction_eq_min_cut_ratio      (PaperFormalization/Certificate.lean)
  C2 seed_routing_feasible_iff_cut_conditions           (PaperFormalization/Certificate.lean)
  C3 capacity_outside_active_bottleneck_irrelevant      (PaperFormalization/Certificate.lean)
  support: Viridis.Run130.Hall.exists_routing_of_hall   (PaperFormalization/Hall.lean)

None of these uses sorry, admit or a new axiom; the canon's axiom check lists only
propext, Classical.choice and Quot.sound.

Spec (numbered invariants)
--------------------------
I1  Model. Sites i have demands d_i > 0; nurseries/sources j have supplies s_j >= 0; a frozen
    binary eligibility relation E says which source may ship to which site. There are NO
    per-edge capacities in the theorem: an eligible edge can carry any amount, limited only
    by the source's supply.
I2  For a non-empty site set U, N(U) is the set of sources eligible for some site in U,
    D(U) = sum of d_i over U and S(N(U)) = sum of s_j over N(U).
I3  Certificate (C1): lambda* = min(1, min over non-empty U of S(N(U)) / D(U)) is the
    LARGEST common fraction lambda in [0, 1] such that some routing gives every site at
    least lambda * d_i without exceeding any supply. Computed by exhaustive enumeration of
    the 2^n - 1 site subsets, in exact rational arithmetic (each input is read as the
    decimal it prints as, so 0.1 + 1.9 is exactly 2).
I4  Feasibility (C2): all demand can be met in full exactly when D(U) <= S(N(U)) for every
    non-empty U. full_fulfillment_feasible is that check, and equals (lambda* == 1).
I5  Bottleneck: the minimising U of S(N(U)) / D(U) over ALL non-empty U (ties broken
    lexicographically, as in the canon runner) is reported with N(U), D(U), S(N(U)) and the
    deficit max(0, D(U) - S(N(U))). bottleneck_ratio is that minimum, not clamped at 1, so a
    feasible network shows its tightest cut (the canon runner clamps it and reports all
    sites; this module reports the real tightest cut instead). Every site set with
    D(U) > S(N(U)) is a violated cut; the union of their sites is reported.
I6  Expansion (C3): when lambda* < 1, raising the supply of any source outside N(U*) of
    the active bottleneck U* cannot raise lambda*. Those sources are listed.

Not claimed: field establishment, seed viability, species/provenance suitability, legality,
transport cost or timing, multi-period stock dynamics, or that the supplied numbers are
right. Per-edge capacities and the scenario-intersection result (C4) are not implemented.
The canon catalog lists this package as 'working', not spine-admitted.

Pure, deterministic — recomputable for certification (A-2).
"""

from __future__ import annotations

import math
from fractions import Fraction
from typing import Optional, Sequence

MAX_SITES = 20  # 2^20 subsets; the canon function.json uses the same limit

SCOPE = "continuous one-period frozen binary-eligibility supply network"

CLAIM_BOUNDARY = (
    "Model-scoped routing arithmetic only. It does not establish seed availability, field "
    "suitability, establishment success, land rights, permits, cost or delivery timing."
)


def _numbers(name: str, values: Sequence[float]) -> list[float]:
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


def _edges(edges, n_sources: int, n_sites: int) -> list[tuple[int, int]]:
    if isinstance(edges, (str, bytes)) or not hasattr(edges, "__iter__"):
        raise ValueError("edges must be a list of [source, site] pairs")
    out = []
    for e in edges:
        try:
            src, site = e
        except (TypeError, ValueError) as exc:
            raise ValueError("each edge must be a [source, site] pair") from exc
        for v in (src, site):
            if isinstance(v, bool) or not isinstance(v, int):
                raise ValueError("edge indices must be integers")
        if not (0 <= src < n_sources and 0 <= site < n_sites):
            raise ValueError(f"edge {[src, site]} names a source or site that does not exist")
        out.append((src, site))
    return out


def _exact(x: float) -> Fraction:
    """Read a float as the decimal it prints as (0.1 -> 1/10), so sums match the user's
    numbers exactly instead of their binary approximations."""
    return Fraction(repr(float(x)))


def _lexically_less(left: list[int], right: list[int]) -> bool:
    for a, b in zip(left, right):
        if a != b:
            return a < b
    return len(left) < len(right)


def bottleneck_check(*, demands: Sequence[float], supplies: Sequence[float], edges) -> dict:
    """Common fulfilment fraction, feasibility and bottleneck for a supply network (I1–I6)."""
    d = _numbers("demands", demands)
    s = _numbers("supplies", supplies)
    if any(x <= 0 for x in d):
        raise ValueError("every site demand must be > 0")
    if any(x < 0 for x in s):
        raise ValueError("every source supply must be >= 0")
    n = len(d)
    if n > MAX_SITES:
        raise ValueError(f"at most {MAX_SITES} sites (the check enumerates every site subset)")
    pairs = _edges(edges, len(s), n)

    dq = [_exact(x) for x in d]
    sq = [_exact(x) for x in s]
    site_mask = [0] * n
    for src, site in pairs:
        site_mask[site] |= 1 << src

    # Subset DP: neighbourhood and demand of every site subset, by lowest set bit.
    size = 1 << n
    nb = [0] * size
    dem = [Fraction(0)] * size
    supply_cache: dict[int, Fraction] = {0: Fraction(0)}

    def supply_of(mask: int) -> Fraction:
        got = supply_cache.get(mask)
        if got is None:
            low = mask & -mask
            got = supply_of(mask ^ low) + sq[low.bit_length() - 1]
            supply_cache[mask] = got
        return got

    def members(mask: int, count: int) -> list[int]:
        return [k for k in range(count) if (mask >> k) & 1]

    best: Optional[Fraction] = None
    best_sites: list[int] = []
    best_mask = size - 1
    violated_union = 0
    violated_count = 0
    for mask in range(1, size):
        low = mask & -mask
        i = low.bit_length() - 1
        nb[mask] = nb[mask ^ low] | site_mask[i]
        dem[mask] = dem[mask ^ low] + dq[i]
        cap = supply_of(nb[mask])
        ratio = cap / dem[mask]
        if cap < dem[mask]:
            violated_union |= mask
            violated_count += 1
        if best is None or ratio < best or (
            ratio == best and _lexically_less(members(mask, n), best_sites)
        ):
            best = ratio
            best_mask = mask
            best_sites = members(mask, n)

    certificate = min(Fraction(1), best)
    feasible = violated_count == 0
    eligible = members(nb[best_mask], len(s))
    out = {
        "common_fulfillment_fraction": float(certificate),
        "full_fulfillment_feasible": feasible,
        "bottleneck_ratio": float(best),
        "bottleneck_site_indices": best_sites,
        "eligible_supply_indices": eligible,
        "bottleneck_demand": float(dem[best_mask]),
        "bottleneck_supply": float(supply_of(nb[best_mask])),
        "bottleneck_deficit": float(max(Fraction(0), dem[best_mask] - supply_of(nb[best_mask]))),
        "violated_cut_count": violated_count,
        "sites_in_violated_cuts": members(violated_union, n),
        "sources_that_cannot_help": (
            [j for j in range(len(s)) if j not in eligible] if certificate < 1 else []
        ),
        "scope": SCOPE,
        "edge_capacities_modelled": False,
        "claim_boundary": CLAIM_BOUNDARY,
    }
    if feasible != (certificate == 1):  # C1 and C2 must agree; a mismatch is an engine bug
        raise AssertionError("internal inconsistency between C1 and C2")
    return out
