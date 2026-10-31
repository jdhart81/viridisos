"""ViridisOS wrapper for the Precautionary Capacity Ceiling (PCR, Run-127).

A safe ceiling (for example an allowable harvest or stocking level) from the true mean and
standard deviation of a non-negative one-period capacity, with violation probability at
most alpha (one-sided Cantelli). See engine.py for the numbered invariants. Ships as
PREVIEW: DOI 10.5281/zenodo.21971046 is not in the bundled canon index (the canon catalog
lists the package as 'working', not gate-passed), so certification is refused (A-1).
"""

from __future__ import annotations

from runtime.module import Backing, Module

from . import engine


# Backing: The Precautionary Capacity Reserve, Zenodo 10.5281/zenodo.21971046,
# viridis-canon series/PCR. Lean theorems (namespace Viridis.Run127.PaperFormalization):
# capacityFloor_violation_prob_le, positive_floor_sharp_two_point_counterexample and
# mean_only_plugin_arbitrarily_unsafe in series/PCR/PaperFormalization/Targets.lean, using
# cantelli_lower_tail (Cantelli.lean) and the two-point laws in TwoPoint.lean. Verified by
# Comparator receipt Run-127-PrecautionaryCapacity-Comparator-attempt-1; zero sorry/admit,
# standard axioms only. The canon's rate-model outputs (power, temperature, rate ceiling)
# are deliberately not exposed.
PCR_BACKING = Backing(
    doi="10.5281/zenodo.21971046",
    lean_module="Viridis.Run127.PaperFormalization",
    aristotle_id="Run-127-PrecautionaryCapacity-Comparator-attempt-1",
    verified=True,
    integrity_flag=False,
)


class PrecautionaryCeilingModule(Module):
    id = "precautionary-ceiling"
    name = "Precautionary Capacity Ceiling — safe ceiling from a mean and variance"
    line = "Stewardship risk"
    version = "0.1.0"
    backing = PCR_BACKING

    def units(self) -> dict:
        return {
            "mean_capacity": "user's capacity units (e.g. m3/ha, head/ha)",
            "capacity_sd": "same units as mean_capacity",
            "alpha": "probability",
            "precautionary_ceiling": "same units as mean_capacity",
            "absolute_discount": "same units as mean_capacity",
            "cantelli_factor": "dimensionless",
            "capacity_fraction": "dimensionless, 0..1",
            "violation_probability_bound": "probability",
            "positive_floor": "boolean",
            "ceiling_is_sharp": "boolean",
            "mean_only_rule_safe": "boolean (always false)",
        }

    def compute(self, inputs: dict) -> dict:
        missing = [k for k in ("mean_capacity", "capacity_sd", "alpha") if k not in inputs]
        if missing:
            raise ValueError(f"missing required input(s): {', '.join(missing)}")
        extra = sorted(set(inputs) & {"power", "temperature"})
        if extra:
            raise ValueError("this module has no rate model; drop: " + ", ".join(extra))
        return engine.precautionary_ceiling(
            mean_capacity=inputs["mean_capacity"],
            capacity_sd=inputs["capacity_sd"],
            alpha=inputs["alpha"],
        )
