"""ViridisOS wrapper for the Byproduct Exchange Corridor (RC, Run-128).

A two-way industrial-symbiosis screen: from each partner's per-unit value and cost, is
there a flow ratio that leaves both strictly better off, and what split does the symmetric
Nash rule pick. See engine.py for the numbered invariants. Ships as PREVIEW: DOI
10.5281/zenodo.21971047 is not in the bundled canon index (the canon catalog lists the
package as 'working', not gate-passed), so certification is refused (A-1).
"""

from __future__ import annotations

from runtime.module import Backing, Module

from . import engine


# Backing: The Reciprocity Corridor, Zenodo 10.5281/zenodo.21971047, viridis-canon
# series/RC/PaperFormalization.lean (namespace Viridis.Run128.PaperFormalization):
# bilateral_benefit_iff_reciprocity_corridor, strict_corridor_nonempty_iff_product_condition,
# share_coordinate_corridor_equivalence, nash_midpoint_unique_maximizer and
# bandwidth_scaling_cannot_restore_feasibility. Verified by Comparator receipt
# Run-128-ReciprocityCorridor-Comparator-attempt-1; zero sorry/admit, standard axioms only.
# No Intelligence Bound or thermodynamic premise is used.
RC_BACKING = Backing(
    doi="10.5281/zenodo.21971047",
    lean_module="Viridis.Run128.PaperFormalization",
    aristotle_id="Run-128-ReciprocityCorridor-Comparator-attempt-1",
    verified=True,
    integrity_flag=False,
)

_REQUIRED = ("value_x", "value_y", "cost_x", "cost_y", "total_flow")
_ALLOWED = set(_REQUIRED) | {"flow_x", "flow_y"}


class ByproductExchangeModule(Module):
    id = "byproduct-exchange"
    name = "Byproduct Exchange Corridor — two-way industrial-symbiosis reciprocity test"
    line = "Circular economy"
    version = "0.1.0"
    backing = RC_BACKING

    def units(self) -> dict:
        return {
            "value_x": "X's value per unit of y received (user's currency per flow unit)",
            "value_y": "Y's value per unit of x received",
            "cost_x": "X's cost per unit of x sent",
            "cost_y": "Y's cost per unit of y sent",
            "total_flow": "flow units (x + y)",
            "corridor_nonempty": "boolean",
            "product_margin": "v_x*v_y - c_x*c_y (currency^2 per flow^2)",
            "flow_ratio_lower": "y/x, dimensionless",
            "flow_ratio_upper": "y/x, dimensionless",
            "y_share_lower": "y/(x+y), dimensionless",
            "y_share_upper": "y/(x+y), dimensionless",
            "nash_y_share": "y/(x+y), dimensionless",
            "nash_x_flow": "flow units",
            "nash_y_flow": "flow units",
            "nash_payoff_x": "currency",
            "nash_payoff_y": "currency",
            "proposed_payoff_x": "currency",
            "proposed_payoff_y": "currency",
        }

    def compute(self, inputs: dict) -> dict:
        missing = [k for k in _REQUIRED if k not in inputs]
        if missing:
            raise ValueError(f"missing required input(s): {', '.join(missing)}")
        extra = sorted(set(inputs) - _ALLOWED)
        if extra:
            raise ValueError("unsupported input(s) (no thermodynamic or rate model here): "
                             + ", ".join(extra))
        return engine.exchange_corridor(
            value_x=inputs["value_x"], value_y=inputs["value_y"],
            cost_x=inputs["cost_x"], cost_y=inputs["cost_y"],
            total_flow=inputs["total_flow"],
            flow_x=inputs.get("flow_x"), flow_y=inputs.get("flow_y"),
        )
