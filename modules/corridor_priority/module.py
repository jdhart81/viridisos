"""ViridisOS wrapper for Corridor Edge-Priority (PCS, Run-124).

Which corridor link to protect first? Each link's pivotal probability is exactly the
derivative of core-to-core reliability with respect to that link's survival probability.
See engine.py for the numbered invariants. Ships as PREVIEW: DOI 10.5281/zenodo.22665554
is not in the bundled canon index, so certification is refused (A-1).
"""

from __future__ import annotations

from runtime.module import Backing, Module

from . import engine


# Backing: Pivotal Corridor Stewardship, Zenodo 10.5281/zenodo.22665554, viridis-canon
# series/PCS/ViridisRun124.lean (namespace Viridis.Run124.PaperFormalization):
# reliability_derivative_eq_pivotal_probability, pivotalProb_eq_reliability_diff,
# pivotal_probability_independent_of_own_probability, local_linear_budget_gain_le_best_ratio.
# Comparator receipt Run-124-PivotalCorridorStewardship-Comparator-attempt-7
# (LEAN_ZERO_SORRY_CERTIFIED, nanoda and Lean kernels PASS).
PCS_BACKING = Backing(
    doi="10.5281/zenodo.22665554",
    lean_module="Viridis.Run124.PaperFormalization",
    aristotle_id="Run-124-PivotalCorridorStewardship-Comparator-attempt-7",
    verified=True,
    integrity_flag=False,
)


class CorridorPriorityModule(Module):
    id = "corridor-priority"
    name = "Corridor Edge-Priority — which corridor link to protect first"
    line = "Restoration"
    version = "0.1.0"
    backing = PCS_BACKING

    def units(self) -> dict:
        return {
            "num_nodes": "count (nodes are 0..num_nodes-1)",
            "edges": "[node, node] undirected links",
            "survival": "probability per link (independent)",
            "core_a": "node indices", "core_b": "node indices",
            "costs": "optional positive cost per link",
            "reliability": "probability the cores stay connected",
            "pivotal_probability": "probability per link (= dR/dp_e)",
            "priority_order": "link indices, highest pivotal first",
            "pivotal_per_cost": "probability per cost unit",
            "best_ratio": "reliability gain per unit budget (first order)",
        }

    def compute(self, inputs: dict) -> dict:
        keys = ("num_nodes", "edges", "survival", "core_a", "core_b")
        missing = [k for k in keys if k not in inputs]
        if missing:
            raise ValueError(f"missing required input(s): {', '.join(missing)}")
        return engine.edge_priority(**{k: inputs[k] for k in keys}, costs=inputs.get("costs"))
