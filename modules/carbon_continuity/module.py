"""ViridisOS wrapper for the Carbon Continuity threshold kernel."""

from __future__ import annotations

from runtime.module import Backing, Module

from . import engine


# Backing: Carbon Continuity After Wildfire, Zenodo 10.5281/zenodo.21855690 (version
# 0.2.0-formal), theorem Viridis.CarbonContinuity.carbon_continuity_threshold_iff in
# viridis-canon releases/2026-08-08/Carbon_Continuity_After_Wildfire (Lean source sha256
# 899d3bb1929bac8d1ab6b760caffac428de115489e6fc7c1b2752e0769a77fc1).
#
# Re-certified 2026-10-29 by the Viridis research engine (jdhart81/viridis-research,
# run 2026-10-29_P2, task P2-T001): sealed statement P2.CarbonContinuity, label PROVEN,
# not closed by the triviality probe, Lean v4.28.0 with Mathlib 8f9d9cff. The statement:
# for a, d in [0, 1) and r, p > 0, a strictly positive two-pool portfolio that one cycle
# does not shrink exists exactly when (1 - a)(1 - d) <= r * p. This is what
# engine.evaluate_threshold computes. PROVEN covers the mathematics only; coefficients and
# ecological outcomes stay ASSUMED and are the user's to justify.
RECERTIFICATION = {
    "engine_run": "viridis-research/runs/2026-10-29_P2",
    "statement_id": "P2.CarbonContinuity",
    "label": "PROVEN",
    "trivial": False,
    "lean_toolchain": "v4.28.0",
    "mathlib_rev": "8f9d9cff6bd728b17a24e163c9402775d9e6a365",
    "covers": "the threshold mathematics only, not coefficients or field outcomes",
}

CARBON_CONTINUITY_BACKING = Backing(
    doi="10.5281/zenodo.21855690",
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
