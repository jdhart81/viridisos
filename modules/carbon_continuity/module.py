"""ViridisOS wrapper for the Carbon Continuity threshold kernel."""

from __future__ import annotations

from runtime.module import Backing, Module

from . import engine


# The Lean theorem passed the Aristotle and local zero-sorry audits, but the
# paper has not yet been published into the canon. The pending DOI therefore
# keeps certification fail-closed while previews remain available.
CARBON_CONTINUITY_BACKING = Backing(
    doi="10.5281/zenodo.CARBON-CONTINUITY-PENDING",
    lean_module="CarbonContinuity",
    aristotle_id="40c58299-efeb-4cad-b332-2525b7c8d6d1",
    verified=True,
    integrity_flag=False,
)


class CarbonContinuityModule(Module):
    id = "carbon-continuity"
    name = "Carbon Continuity — wildfire recovery threshold diagnostic"
    line = "Risk & Insurance"
    version = "0.1.0"
    backing = CARBON_CONTINUITY_BACKING

    def units(self) -> dict:
        return {
            "a": "dimensionless retention coefficient",
            "d": "dimensionless retention coefficient",
            "r": "dimensionless coupling coefficient",
            "p": "dimensionless coupling coefficient",
            "loop_gain": "dimensionless",
            "leakage_product": "dimensionless",
            "continuity_number": "dimensionless",
            "threshold_met": "boolean model result",
            "regime": "categorical model result",
            "credit_quantity_tco2e": "not computed",
        }

    def compute(self, inputs: dict) -> dict:
        missing = [key for key in ("a", "d", "r", "p") if key not in inputs]
        if missing:
            raise ValueError(f"missing required coefficient(s): {', '.join(missing)}")
        return engine.evaluate_threshold(
            a=inputs["a"],
            d=inputs["d"],
            r=inputs["r"],
            p=inputs["p"],
        )
