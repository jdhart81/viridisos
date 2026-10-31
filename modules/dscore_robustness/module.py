"""ViridisOS wrapper for D-Score Weight-Robustness (DSWC, Run-132).

Does a parcel ranking survive disputed weights? See engine.py for the numbered invariants.
The D-Score's ecological validity is NOT proven; this checks weighted-sum arithmetic only.
Ships as PREVIEW: DOI 10.5281/zenodo.22236741 is not in the bundled canon index, so
certification is refused (A-1) until the canon admits it.
"""

from __future__ import annotations

from runtime.module import Backing, Module

from . import engine


# Backing: The D-Score Weight-Charter Certificate, Zenodo 10.5281/zenodo.22236741,
# viridis-canon series/DSWC/ViridisRun132.lean (namespace Viridis.DScore.WeightCharter):
# tv_range_certificate, strict_rank_stability, charter_nonvacuous. Comparator receipt
# Run-132-DScoreWeightCharter-Engine3-Correction-r1-attempt-3 (LEAN_ZERO_SORRY_CERTIFIED,
# nanoda and Lean kernels PASS).
DSWC_BACKING = Backing(
    doi="10.5281/zenodo.22236741",
    lean_module="Viridis.DScore.WeightCharter",
    aristotle_id="Run-132-DScoreWeightCharter-Engine3-Correction-r1-attempt-3",
    verified=True,
    integrity_flag=False,
)


class DScoreRobustnessModule(Module):
    id = "dscore-robustness"
    name = "D-Score Weight-Robustness — does a parcel ranking survive disputed weights"
    line = "Verification & Certification"
    version = "0.1.0"
    backing = DSWC_BACKING

    def units(self) -> dict:
        return {
            "reference_weights": "probability vector (non-negative, sums to 1)",
            "alternative_weights": "probability vector (non-negative, sums to 1)",
            "parcel_a": "indicator values, same scale as parcel_b",
            "parcel_b": "indicator values, same scale as parcel_a",
            "total_variation": "dimensionless, 0..1",
            "contrast_span": "indicator units",
            "gap_reference": "score units",
            "gap_alternative": "score units",
            "gap_drift_bound": "score units",
            "ranking_robust": "boolean",
            "robust_tv_radius": "total-variation distance (null = unbounded)",
            "order_flipped_under_alternative": "boolean",
            "ecological_validity_proven": "boolean (always false)",
        }

    def compute(self, inputs: dict) -> dict:
        keys = ("reference_weights", "alternative_weights", "parcel_a", "parcel_b")
        missing = [k for k in keys if k not in inputs]
        if missing:
            raise ValueError(f"missing required input(s): {', '.join(missing)}")
        return engine.weight_robustness(**{k: inputs[k] for k in keys})
