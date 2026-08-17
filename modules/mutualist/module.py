"""Mutualist module — wraps the SRPT kernel behind the ViridisOS module contract."""

from __future__ import annotations

from typing import Optional

from runtime.module import Module, Backing
from runtime.canon_resolver import CanonResolver
from . import engine

# Backing theorem: SRPT (Run-093). DOI is a placeholder until the SRPT deposit is minted;
# it must resolve to a gate-passed canon entry for the module to certify (A-1). Wire the
# real DOI when SRPT is published; until then the module is BLOCKED unless the resolver is
# given this entry (which is exactly the A-1/A-3 behavior we want).
SRPT_BACKING = Backing(
    doi="10.5281/zenodo.SRPT-PENDING",
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
