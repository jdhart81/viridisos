"""Restoration module — wraps the FNT kernel. Backed by a PUBLISHED canon theorem, so it
certifies live against the canon index."""

from __future__ import annotations

from runtime.module import Module, Backing
from . import engine

# FNT is published — DOI resolves to a gate-passed canon entry (canon_fingerprint_index.json).
FNT_BACKING = Backing(
    doi="10.5281/zenodo.20982979",
    lean_module="ForestNucleation",
    aristotle_id="run-061-fnt",
    verified=True,
    integrity_flag=False,
)


class RestorationModule(Module):
    id = "restoration"
    name = "Restoration — nucleation planting design (critical cluster size n* + go/no-go)"
    line = "Restoration"
    version = "0.2.0"
    backing = FNT_BACKING

    def units(self) -> dict:
        return {"critical_radius_r_star": "cube root of trees", "critical_nucleus_n_star": "trees",
                "barrier_height": "model energy units", "edge_to_suitability_ratio": "dimensionless",
                "cluster_size": "trees", "cluster_reaches_n_star": "bool", "go_no_go": "GO|NO_GO"}

    def compute(self, inputs: dict) -> dict:
        return engine.design(
            sigma=inputs["sigma"],
            delta_mu=inputs["delta_mu"],
            shape_factor=inputs.get("shape_factor", 1.0),
            cluster_size=inputs.get("cluster_size"),
        )
