"""Mutualist numeric kernel — ports the verified core of SRPT (Run-093).

Backing theorem: the Symbiotic Risk-Premium Theorem (SRPT). The three headline results
this kernel computes (each traces to a Lean-verified statement in the canon):

  R1  Thermodynamic risk-premium floor:  π ≥ ρ · k_B / Σ
      (no riskless D-Capital asset at finite dissipation Σ).
  R3  Diversification Wall: physically coupled currents share a reservoir, so the best
      hedged joint variance is floored — a strictly positive undiversifiable residual
      π_min ≥ ρ · k_B / Σ_tot survives ANY hedge (systematic risk).
  R5  Contagion/Mutualism transition: sign of the coupling covariance r_c decides all —
      r_c < 0 mutualistic (portfolio effect), r_c > 0 contagious (systemic risk).

Pure functions, stdlib only, deterministic — so certificates are recomputable (A-2).
Physical magnitudes (k_B) are inputs/constants, not proven values (honest scope).
"""

from __future__ import annotations

K_B = 1.380649e-23  # Boltzmann constant (J/K) — a physical constant, not a proven value


def risk_premium_floor(rho: float, sigma: float) -> float:
    """R1: π ≥ ρ·k_B/Σ. Returns the floor value ρ·k_B/Σ (Σ>0)."""
    if sigma <= 0:
        raise ValueError("dissipation Sigma must be > 0 (zero variance ⇒ Sigma→∞)")
    return rho * K_B / sigma


def diversification_residual(rho: float, sigma_tot: float) -> float:
    """R3: undiversifiable residual premium π_min ≥ ρ·k_B/Σ_tot (Σ_tot>0)."""
    if sigma_tot <= 0:
        raise ValueError("shared dissipation Sigma_tot must be > 0")
    return rho * K_B / sigma_tot


def contagion_sign(r_c: float) -> str:
    """R5: sign of the coupling covariance r_c → regime."""
    if r_c < 0:
        return "mutualistic"      # portfolio-effect credit (stabilizing)
    if r_c > 0:
        return "contagious"       # systemic-risk flag (synchronized drawdown)
    return "neutral"              # transition at r_c = 0


def price_portfolio(rho: float, sigma: float, sigma_tot: float, r_c: float) -> dict:
    """Full Mutualist computation for a coupled portfolio."""
    return {
        "risk_premium_floor": risk_premium_floor(rho, sigma),
        "diversification_residual": diversification_residual(rho, sigma_tot),
        "contagion_regime": contagion_sign(r_c),
        # invariant the theorem asserts: coupled residual is strictly positive at finite Σ_tot
        "undiversifiable": diversification_residual(rho, sigma_tot) > 0,
    }
