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
    name = "Afforestation — seeding efficiency and the 8× edge-hostility lever"
    line = "Restoration"
    version = "0.2.0"
    backing = AST_BACKING

    def units(self) -> dict:
        return {"critical_nucleus_n_star": "trees", "barrier_height": "model energy units",
                "seeding_efficiency": "established canopy per seed (scaled by C)",
                "efficiency_if_edge_hostility_halved": "established canopy per seed (scaled by C)",
                "efficiency_scaling_in_drive": "text"}

    def compute(self, inputs: dict) -> dict:
        return engine.plan(
            sigma=inputs["sigma"],
            delta_mu=inputs["delta_mu"],
            shape_factor=inputs.get("shape_factor", 1.0),
            establishment_constant=inputs.get("establishment_constant", 1.0),
        )
