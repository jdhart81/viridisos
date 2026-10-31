"""ViridisOS wrapper for the Seed-Supply Bottleneck Check (SSBC, Run-130).

Can nursery supply meet planting demand, and which sites are short? See engine.py for the
numbered invariants. Ships as PREVIEW: DOI 10.5281/zenodo.21971057 is not in the bundled
canon index (the canon catalog lists the package as 'working', not gate-passed), so the
resolver refuses certification (A-1) until it is admitted there.
"""

from __future__ import annotations

from runtime.module import Backing, Module

from . import engine


# Backing: The Seed-Source Bottleneck Certificate, Zenodo 10.5281/zenodo.21971057,
# viridis-canon series/SSBC. Lean theorems: Viridis.Run130.seed_routing_common_fraction_eq_
# min_cut_ratio (C1), seed_routing_feasible_iff_cut_conditions (C2),
# capacity_outside_active_bottleneck_irrelevant (C3), all in
# series/SSBC/PaperFormalization/Certificate.lean, using Viridis.Run130.Hall.
# exists_routing_of_hall in series/SSBC/PaperFormalization/Hall.lean. Verified by
# Comparator receipt Run-130-SeedSourceBottleneck-Comparator-attempt-1; zero sorry/admit,
# standard axioms only.
SSBC_BACKING = Backing(
    doi="10.5281/zenodo.21971057",
    lean_module="Viridis.Run130.PaperFormalization",
    aristotle_id="Run-130-SeedSourceBottleneck-Comparator-attempt-1",
    verified=True,
    integrity_flag=False,
)


class SeedSupplyBottleneckModule(Module):
    id = "seed-supply"
    name = "Seed-Supply Bottleneck Check — can nursery supply meet planting demand"
    line = "Restoration"
    version = "0.1.0"
    backing = SSBC_BACKING

    def units(self) -> dict:
        return {
            "demands": "seed or seedling units per site",
            "supplies": "seed or seedling units per source",
            "edges": "[source index, site index] eligibility pairs",
            "common_fulfillment_fraction": "dimensionless, 0..1",
            "full_fulfillment_feasible": "boolean model result",
            "bottleneck_ratio": "dimensionless",
            "bottleneck_site_indices": "site indices",
            "eligible_supply_indices": "source indices",
            "bottleneck_demand": "seed or seedling units",
            "bottleneck_supply": "seed or seedling units",
            "bottleneck_deficit": "seed or seedling units",
            "violated_cut_count": "count of site subsets",
            "sites_in_violated_cuts": "site indices",
            "sources_that_cannot_help": "source indices",
        }

    def compute(self, inputs: dict) -> dict:
        missing = [k for k in ("demands", "supplies", "edges") if k not in inputs]
        if missing:
            raise ValueError(f"missing required input(s): {', '.join(missing)}")
        return engine.bottleneck_check(
            demands=inputs["demands"], supplies=inputs["supplies"], edges=inputs["edges"]
        )
