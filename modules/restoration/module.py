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
    name = "Restoration — nucleation planting design (Θ go/no-go + n*)"
    line = "Restoration"
    version = "0.1.0"
    backing = FNT_BACKING

    def units(self) -> dict:
        return {"nucleation_number": "dimensionless", "critical_nucleus_n_star": "patch-size",
                "recommendation": "GREEN|AMBER|RED"}

    def compute(self, inputs: dict) -> dict:
        return engine.design(sigma=float(inputs["sigma"]), delta_mu=float(inputs["delta_mu"]))
