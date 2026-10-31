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
    name = "Harmonization — single-price coordination toward a shared target"
    line = "Governance / OS Modules"
    version = "0.2.0"
    backing = GHT_BACKING

    def units(self) -> dict:
        return {"shadow_price": "cost per unit of effort", "allocation": "effort units per steward",
                "total": "effort units", "target": "effort units", "market_clears": "bool",
                "total_cost": "cost units"}

    def compute(self, inputs: dict) -> dict:
        return engine.harmonize(
            curvatures=inputs["curvatures"],
            ideals=inputs["ideals"],
            target=inputs["target"],
        )
