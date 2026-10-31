"""ViridisOS wrapper for the Anytime-valid Monitoring Alarm (ACC, Run-129).

Has a monitored binary signal (invasive detections, mortality events, ...) really changed,
with false-alarm probability at most alpha at every sample size? See engine.py for the
numbered invariants. Ships as PREVIEW: DOI 10.5281/zenodo.21971041 is not in the bundled
canon index (the canon catalog lists the package as 'working', not gate-passed), so
certification is refused (A-1) until it is admitted there.
"""

from __future__ import annotations

from runtime.module import Backing, Module

from . import engine


# Backing: Anytime Change Certificate, Zenodo 10.5281/zenodo.21971041, viridis-canon
# series/ACC. Lean theorems (namespace Viridis.Run129.PaperFormalization):
# anytime_change_mixture_martingale and anytime_change_ville_certificate
# (NullMartingale.lean), change_component_dominance_and_penalty (Dominance.lean),
# bounded_overshoot_expected_delay (Wald.lean), hasSum_changePrior (Prior.lean).
# Comparator receipt Run-129-AnytimeChange-Comparator-attempt-3-selective-imports-complete;
# zero sorry/admit, standard axioms only. The file's landauer_erasure_corridor corollary
# is deliberately not used.
ACC_BACKING = Backing(
    doi="10.5281/zenodo.21971041",
    lean_module="Viridis.Run129.PaperFormalization",
    aristotle_id="Run-129-AnytimeChange-Comparator-attempt-3-selective-imports-complete",
    verified=True,
    integrity_flag=False,
)


class AnytimeAlarmModule(Module):
    id = "anytime-alarm"
    name = "Anytime-valid Monitoring Alarm — has a monitored 0/1 signal really changed"
    line = "Monitoring integrity"
    version = "0.1.0"
    backing = ACC_BACKING

    def units(self) -> dict:
        return {
            "observations": "0/1 per sampling event, oldest first",
            "p0": "probability of a 1 with no change",
            "p1": "probability of a 1 after the change",
            "alpha": "false-alarm probability budget",
            "current_mixture_evidence": "likelihood ratio (null if > e^700)",
            "maximum_mixture_evidence": "likelihood ratio (null if > e^700)",
            "log_current_mixture_evidence": "natural log of likelihood ratio",
            "alarm_threshold": "likelihood ratio (1/alpha)",
            "alarm_index": "1-based observation index",
            "false_alarm_probability_bound": "probability",
            "delay.expected_delay_upper_bound": "post-change observations",
        }

    def compute(self, inputs: dict) -> dict:
        missing = [k for k in ("observations", "p0", "p1", "alpha") if k not in inputs]
        if missing:
            raise ValueError(f"missing required input(s): {', '.join(missing)}")
        return engine.monitor(observations=inputs["observations"], p0=inputs["p0"],
                              p1=inputs["p1"], alpha=inputs["alpha"],
                              change_time=inputs.get("change_time"))
