"""Afforestation module — wraps the AST kernel. Backed by published AST (DOI 21168224)."""

from __future__ import annotations

from runtime.module import Module, Backing
from . import engine

AST_BACKING = Backing(
    doi="10.5281/zenodo.21168224",
    lean_module="AfforestationStewardship",
    aristotle_id="ast-sower",
    verified=True,
    integrity_flag=False,
)


class AfforestationModule(Module):
    id = "afforestation"
    name = "Afforestation — cubic optimal-seeding law + site-prep lever"
    line = "Restoration"
    version = "0.1.0"
    backing = AST_BACKING

    def units(self) -> dict:
        return {"optimal_density": "seedlings/area", "site_prep_multiplier": "×",
                "seeding_within_ib_ceiling": "bool"}

    def compute(self, inputs: dict) -> dict:
        return engine.plan(
            sigma=float(inputs["sigma"]), delta_mu=float(inputs["delta_mu"]),
            prep=float(inputs.get("prep", 1.0)), rate=float(inputs.get("rate", 0.0)),
            rate_max=float(inputs.get("rate_max", 1.0)),
        )
