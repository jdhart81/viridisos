"""Harmonization module — wraps the GHT kernel. Backed by published GHT (DOI 21168212)."""

from __future__ import annotations

from runtime.module import Module, Backing
from . import engine

GHT_BACKING = Backing(
    doi="10.5281/zenodo.21168212",
    lean_module="GaianHarmonization",
    aristotle_id="ght-harmonizer",
    verified=True,
    integrity_flag=False,
)


class HarmonizationModule(Module):
    id = "harmonization"
    name = "Harmonization — thermodynamic shadow-price coordination"
    line = "Governance / OS Modules"
    version = "0.1.0"
    backing = GHT_BACKING

    def units(self) -> dict:
        return {"shadow_price": "cost/unit", "wu_wei_dividend": "cost saved",
                "decentralization_cheaper": "bool", "coordination_within_ib": "bool"}

    def compute(self, inputs: dict) -> dict:
        return engine.harmonize(
            marginal_costs=[float(x) for x in inputs["marginal_costs"]],
            command_overhead=float(inputs.get("command_overhead", 1.0)),
            bandwidth=float(inputs.get("bandwidth", 0.0)),
            ib_bound=float(inputs.get("ib_bound", 1.0)),
        )
