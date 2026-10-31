"""Corridor Edge-Priority kernel — Pivotal Corridor Stewardship (PCS, Run-124).

Backing: Zenodo 10.5281/zenodo.22665554; viridis-canon series/PCS/ViridisRun124.lean,
namespace ``Viridis.Run124.PaperFormalization`` (Comparator receipt
Run-124-PivotalCorridorStewardship-Comparator-attempt-7). Theorems relied on:

  reliability_derivative_eq_pivotal_probability   (C1)
  pivotalProb_eq_reliability_diff                 (lemma under C1)
  pivotal_probability_independent_of_own_probability (C2)
  local_linear_budget_gain_le_best_ratio          (C3, used only when costs are given)
  equal_marginals_do_not_identify_reliability     (C6, why independence is load-bearing)

ViridisRun124.lean contains no sorry, admit or axiom (the sorry-stubs in
contracts/VERIFICATION_STATEMENT.lean are the frozen statement contract, not the proof).

Spec (numbered invariants)
--------------------------
I1  Model. An undirected corridor graph on nodes 0..n-1 with m <= MAX_EDGES links; link e
    survives with probability p_e in [0, 1], INDEPENDENTLY of every other link (the
    product weight). Two disjoint, non-empty terminal cores A and B (node sets).
I2  Structure function phi(state) = 1 iff some node of A is joined to some node of B by
    surviving links. phi is monotone (coherent), the only hypothesis C1 needs.
I3  Reliability R(p) = sum over all 2^m link states of weight(p, state) * phi(state),
    computed exactly by enumeration in rational arithmetic (each probability read as the
    decimal it prints as). Graphs with more than MAX_EDGES links are rejected.
I4  Pivotal probability of link e: the probability, over the OTHER links, that the cores
    are connected with e up and disconnected with e down. Computed from that definition.
I5  C1: R is affine in p_e and dR/dp_e = pivotal_e exactly; equivalently
    pivotal_e = R(p_e := 1) - R(p_e := 0). C2: pivotal_e does not depend on p_e.
I6  Priority: links ranked by pivotal probability (largest first, ties by index). With
    positive costs c_e, links are also ranked by pivotal_e / c_e, and C3 says the best
    first-order reliability gain from a small budget B is B * max_e pivotal_e / c_e,
    achieved by spending it all on a best-ratio link. This is a LOCAL (first-order) rule.

Not claimed: correlated failures (fire, drought, a shared road) break I3–I6; C6 shows equal
marginal survival probabilities do not determine reliability once failures are correlated.
Not claimed either: that the survival probabilities are right, that connectivity between the
cores is the ecological goal, or that a first-order priority stays optimal for large
upgrades (link interactions, C4, are not used).

Pure, deterministic — recomputable for certification (A-2).
"""

from __future__ import annotations

import math
from fractions import Fraction
from typing import Optional, Sequence

MAX_EDGES = 16      # 65,536 states; exact rational enumeration stays fast
MAX_NODES = 64

CLAIM_BOUNDARY = (
    "Exact for independent link survival only. Correlated failures, wrong survival "
    "probabilities, or a goal other than core-to-core connectivity are not covered."
)


def _exact(name: str, value: object, lo: float, hi: Optional[float]) -> Fraction:
    if isinstance(value, bool):
        raise ValueError(f"{name} must be a number")
    try:
        x = float(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{name} must be a number") from exc
    if not math.isfinite(x) or x < lo or (hi is not None and x > hi):
        raise ValueError(f"{name} out of range")
    return Fraction(repr(x))


def _index(name: str, v: object, n: int) -> int:
    if isinstance(v, bool) or not isinstance(v, int) or not 0 <= v < n:
        raise ValueError(f"{name} must be a node index in 0..{n - 1}")
    return v


def _list(name: str, values) -> list:
    if isinstance(values, (str, bytes, dict)) or not hasattr(values, "__iter__"):
        raise ValueError(f"{name} must be a list")
    return list(values)


def _parse(num_nodes, edges, survival, core_a, core_b):
    if isinstance(num_nodes, bool) or not isinstance(num_nodes, int) or not 2 <= num_nodes <= MAX_NODES:
        raise ValueError(f"num_nodes must be an integer in 2..{MAX_NODES}")
    edge_list = _list("edges", edges)
    probs = _list("survival", survival)
    if not edge_list:
        raise ValueError("edges needs at least one link")
    if len(edge_list) > MAX_EDGES:
        raise ValueError(f"at most {MAX_EDGES} links (exact enumeration of 2^m states)")
    if len(probs) != len(edge_list):
        raise ValueError("survival needs one probability per link")
    links = []
    for e in edge_list:
        try:
            u, v = e
        except (TypeError, ValueError) as exc:
            raise ValueError("each link must be a [node, node] pair") from exc
        u, v = _index("link end", u, num_nodes), _index("link end", v, num_nodes)
        if u == v:
            raise ValueError("self-loops are not corridor links")
        links.append((u, v))
    p = [_exact("survival", x, 0.0, 1.0) for x in probs]
    a = sorted({_index("core_a", x, num_nodes) for x in _list("core_a", core_a)})
    b = sorted({_index("core_b", x, num_nodes) for x in _list("core_b", core_b)})
    if not a or not b:
        raise ValueError("both terminal cores need at least one node")
    if set(a) & set(b):
        raise ValueError("terminal cores must be disjoint")
    return links, p, a, b


def _connected_table(num_nodes: int, links, a, b) -> list[bool]:
    """phi[mask]: are the cores joined using exactly the links set in mask?"""
    m = len(links)
    target = 0
    for x in b:
        target |= 1 << x
    start = 0
    for x in a:
        start |= 1 << x
    table = [False] * (1 << m)
    for mask in range(1 << m):
        reach = start
        changed = True
        while changed:
            changed = False
            for k, (u, v) in enumerate(links):
                if (mask >> k) & 1:
                    ru, rv = (reach >> u) & 1, (reach >> v) & 1
                    if ru != rv:
                        reach |= (1 << u) | (1 << v)
                        changed = True
        table[mask] = bool(reach & target)
    return table


def _weights(p: list[Fraction]) -> list[Fraction]:
    m = len(p)
    w = [Fraction(1)]
    for k in range(m):           # bit k doubles the table
        up, down = p[k], 1 - p[k]
        w = [x * down for x in w] + [x * up for x in w]
    return w


def reliability_and_pivotal(*, num_nodes: int, edges, survival, core_a, core_b) -> tuple:
    """Exact (R, [pivotal_e]) as Fractions, from the definitions (I3, I4)."""
    links, p, a, b = _parse(num_nodes, edges, survival, core_a, core_b)
    phi = _connected_table(num_nodes, links, a, b)
    w = _weights(p)
    r = sum((w[s] for s in range(len(w)) if phi[s]), Fraction(0))
    piv = []
    for k in range(len(links)):
        bit = 1 << k
        total = Fraction(0)
        for s in range(len(w)):
            if s & bit:
                continue
            if phi[s | bit] and not phi[s]:
                total += w[s] + w[s | bit]          # = coWeight of the other links
        piv.append(total)
    return r, piv


def edge_priority(*, num_nodes: int, edges, survival, core_a, core_b,
                  costs: Optional[Sequence[float]] = None) -> dict:
    """Reliability, each link's pivotal probability, and the protection ranking (I1–I6)."""
    r, piv = reliability_and_pivotal(num_nodes=num_nodes, edges=edges, survival=survival,
                                     core_a=core_a, core_b=core_b)
    m = len(piv)
    order = sorted(range(m), key=lambda k: (-piv[k], k))
    out = {
        "reliability": float(r),
        "pivotal_probability": [float(x) for x in piv],
        "reliability_gradient": [float(x) for x in piv],    # C1: identical by theorem
        "priority_order": order,
        "top_link": order[0],
        "independence_assumed": True,
        "claim_boundary": CLAIM_BOUNDARY,
    }
    if costs is not None:
        c = [_exact("costs", x, 0.0, None) for x in _list("costs", costs)]
        if len(c) != m or any(x <= 0 for x in c):
            raise ValueError("costs needs one positive cost per link")
        ratio = [piv[k] / c[k] for k in range(m)]
        cost_order = sorted(range(m), key=lambda k: (-ratio[k], k))
        out["pivotal_per_cost"] = [float(x) for x in ratio]
        out["cost_priority_order"] = cost_order
        out["best_ratio"] = float(ratio[cost_order[0]])     # C3: gain per unit budget
    return out
