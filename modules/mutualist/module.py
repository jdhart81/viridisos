"""Mutualist module — wraps the SRPT kernel behind the ViridisOS module contract."""

from __future__ import annotations

from typing import Optional

from runtime.module import Module, Backing
from runtime.canon_resolver import CanonResolver
from . import engine

# Backing theorem: SRPT (Run-093), published as Zenodo 10.5281/zenodo.21327066 and recorded
# in Viridis Canon as `series-symbioticriskpremium` (series/SymbioticRiskPremium.lean).
#
# The module stays BLOCKED. Publication is not the gate; the DOI is deliberately absent from
# `runtime/bundled_canon_index.json`, so A-1 refuses to certify. Reasons it is not ready:
#   * Canon lists the record as status=working, integrity=not-canon-admitted, with no
#     hash-bound Comparator certificate (verification_coverage HOLD,
#     LEDGER_ENTITY_NOT_CERTIFIED), and the Canon function manifest is BLOCKED pending an
#     accepted product warrant.
#   * R1 risk_premium_tur_floor and R3 diversification_wall_residual_positive take the
#     Thermodynamic Uncertainty Relation as a hypothesis (`hTUR`). Lean proves the floor
#     *given* the TUR bound for the asset; it does not establish that the bound holds for a
#     natural-capital asset, which is what this module would price.
#   * R6 mutualist_ib_ceiling only proves monotonicity of P·D/(k_B T ln 2); reading it as a
#     limit on hedging relies on the Intelligence Bound, which is a conjecture, not a theorem.
#   * The Canon manifest (viridis-canon os/functions/mutualist/function.json) mislabels the
#     inputs: it calls `rho` an observed correlation and `sigma` asset volatility, while the
#     Lean statements use rho as the risk-aversion coefficient and Sigma as entropy
#     production. The manifest must be corrected before any runner is published.
# Unblocking needs Canon admission, a decision on the TUR premise, and the manifest fix;
# it is a research-pipeline / Justin-gated action, never a change to this file alone.
SRPT_BACKING = Backing(
    doi="10.5281/zenodo.21327066",
    lean_module="SymbioticRiskPremium",
    aristotle_id="run-093-srpt",
    verified=True,
    integrity_flag=False,
)


class MutualistModule(Module):
    id = "mutualist"
    name = "Mutualist — natural-capital risk-premium pricing"
    line = "Valuation & Finance"
    version = "0.1.0"
    backing = SRPT_BACKING

    def units(self) -> dict:
        return {
            "risk_premium_floor": "J·K/(J) dimensionless-scaled",
            "diversification_residual": "same units as premium",
            "contagion_regime": "categorical",
        }

    def compute(self, inputs: dict) -> dict:
        """
        inputs: {
          rho:       risk aversion / price-of-variance scalar (>0),
          sigma:     entropy production Σ of the asset (>0),
          sigma_tot: shared entropy production Σ_tot of the coupled portfolio (>0),
          r_c:       coupling covariance sign carrier,
        }
        """
        return engine.price_portfolio(
            rho=float(inputs["rho"]),
            sigma=float(inputs["sigma"]),
            sigma_tot=float(inputs["sigma_tot"]),
            r_c=float(inputs["r_c"]),
        )
