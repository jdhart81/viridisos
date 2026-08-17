"""Fail-closed Remaining Carbon Asset screen for hybrid satellite/field evidence.

This layer packages observations for a commercial decision interview. It does not infer the paper's
coefficients, certify a project, decide registry treatment, or convert physical carbon into credits.
The core is Python stdlib-only so the receipt is deterministic and easy to recompute.
"""

from __future__ import annotations

import hashlib
import json
import math
from typing import Any


SCHEMA_VERSION = "viridis.remaining-carbon-asset-screen.v1"
CLAIM_BOUNDARY = (
    "Decision-support evidence screen only. Physical carbon estimates are not issued credits. "
    "The screen does not determine additionality, permanence, reversal liability, registry "
    "eligibility, insurance coverage, reserves, or underwriting action."
)


def _canonical_hash(value: dict) -> str:
    raw = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def _mapping(parent: dict, key: str, *, required: bool = True) -> dict:
    value = parent.get(key)
    if value is None and not required:
        return {}
    if not isinstance(value, dict):
        raise ValueError(f"{key} must be an object")
    return value


def _text(parent: dict, key: str) -> str:
    value = parent.get(key)
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{key} must be a non-empty string")
    return value.strip()


def _number(parent: dict, key: str, *, minimum: float | None = None,
            maximum: float | None = None) -> float:
    try:
        value = float(parent.get(key))
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{key} must be a finite number") from exc
    if not math.isfinite(value):
        raise ValueError(f"{key} must be a finite number")
    if minimum is not None and value < minimum:
        raise ValueError(f"{key} must be >= {minimum}")
    if maximum is not None and value > maximum:
        raise ValueError(f"{key} must be <= {maximum}")
    return value


def _evidence_state(field: dict, key: str) -> str:
    value = field.get(key)
    if not isinstance(value, dict):
        return "FIELD_CONFIRMATION_REQUIRED"
    if value.get("status") != "OBSERVED":
        return "FIELD_CONFIRMATION_REQUIRED"
    required = ("source", "method", "observed_at", "uncertainty")
    if not all(isinstance(value.get(item), str) and value[item].strip() for item in required):
        return "FIELD_CONFIRMATION_REQUIRED"
    return "FIELD_OBSERVED_REVIEW_REQUIRED"


def _physical_aboveground_pool(biomass: dict) -> dict | None:
    if not biomass:
        return None
    source = _text(biomass, "source")
    method = _text(biomass, "method")
    carbon_fraction_source = _text(biomass, "carbon_fraction_source")
    post_agb_mg_ha = _number(biomass, "post_agb_mg_ha", minimum=0.0)
    area_ha = _number(biomass, "area_ha", minimum=0.0)
    carbon_fraction = _number(biomass, "carbon_fraction", minimum=0.0, maximum=1.0)
    relative_uncertainty = _number(
        biomass, "relative_uncertainty", minimum=0.0, maximum=1.0
    )
    mid = post_agb_mg_ha * area_ha * carbon_fraction * (44.0 / 12.0)
    return {
        "status": "MODELLED_PHYSICAL_POOL_REVIEW_REQUIRED",
        "post_agb_mg_ha": post_agb_mg_ha,
        "area_ha": area_ha,
        "carbon_fraction": carbon_fraction,
        "physical_aboveground_carbon_tco2e_mid": round(mid, 6),
        "physical_aboveground_carbon_tco2e_low": round(mid * (1.0 - relative_uncertainty), 6),
        "physical_aboveground_carbon_tco2e_high": round(mid * (1.0 + relative_uncertainty), 6),
        "relative_uncertainty": relative_uncertainty,
        "source": source,
        "method": method,
        "carbon_fraction_source": carbon_fraction_source,
        "credit_quantity_tco2e": None,
        "credit_eligibility": None,
    }


def build_remaining_asset_screen(request: dict) -> dict:
    """Validate and package one remote-first post-fire evidence request."""
    if not isinstance(request, dict):
        raise ValueError("request must be an object")
    project = _mapping(request, "project")
    satellite = _mapping(request, "satellite_burn_change")
    biomass = _mapping(request, "aboveground_biomass", required=False)
    field = _mapping(request, "field_evidence", required=False)
    registry = _mapping(request, "registry_context", required=False)

    project_identity = {
        "name": _text(project, "name"),
        "boundary_id": _text(project, "boundary_id"),
        "fire_date": _text(project, "fire_date"),
        "registry_project_id": project.get("registry_project_id"),
    }
    if project_identity["registry_project_id"] is not None and not isinstance(
        project_identity["registry_project_id"], str
    ):
        raise ValueError("registry_project_id must be a string or null")

    satellite_status = _text(satellite, "status")
    valid_fraction = _number(satellite, "valid_fraction", minimum=0.0, maximum=1.0)
    minimum_valid_fraction = _number(
        satellite, "minimum_valid_fraction", minimum=0.0, maximum=1.0
    )
    remote_ready = (
        satellite_status == "REMOTE_SCREEN_READY"
        and valid_fraction >= minimum_valid_fraction
        and satellite.get("dnbr_mean") is not None
    )
    if satellite.get("dnbr_mean") is not None:
        _number(satellite, "dnbr_mean", minimum=-2.0, maximum=2.0)

    physical_pool = _physical_aboveground_pool(biomass)
    field_states = {
        "standing_and_down_deadwood": _evidence_state(field, "standing_and_down_deadwood"),
        "soil_carbon": _evidence_state(field, "soil_carbon"),
        "pyrogenic_carbon": _evidence_state(field, "pyrogenic_carbon"),
        "post_fire_interventions": _evidence_state(field, "post_fire_interventions"),
        "safety_and_access": _evidence_state(field, "safety_and_access"),
    }
    field_complete = all(value == "FIELD_OBSERVED_REVIEW_REQUIRED" for value in field_states.values())
    registry_complete = all(
        isinstance(registry.get(key), str) and registry[key].strip()
        for key in ("methodology", "reversal_terms", "decision_owner")
    )

    if not remote_ready:
        status = "INSUFFICIENT_REMOTE_EVIDENCE"
    elif physical_pool and field_complete and registry_complete:
        status = "HYBRID_EVIDENCE_PACKAGE_READY_FOR_HUMAN_REVIEW"
    else:
        status = "REMOTE_SCREEN_READY_FIELD_CONFIRMATION_REQUIRED"

    missing = []
    if not remote_ready:
        missing.append("usable co-registered pre/post satellite burn-change receipt")
    if physical_pool is None:
        missing.append("post-fire aboveground biomass estimate with declared uncertainty")
    missing.extend(
        label.replace("_", " ")
        for label, state in field_states.items()
        if state != "FIELD_OBSERVED_REVIEW_REQUIRED"
    )
    if not registry_complete:
        missing.append("methodology, reversal terms, and named registry or portfolio decision owner")

    return {
        "schema_version": SCHEMA_VERSION,
        "input_sha256": _canonical_hash(request),
        "project": project_identity,
        "status": status,
        "satellite_observation": {
            "status": satellite_status,
            "algorithm_version": satellite.get("algorithm_version"),
            "valid_fraction": valid_fraction,
            "dnbr_mean": satellite.get("dnbr_mean"),
            "pre_scene_ids": satellite.get("pre_scene_ids", []),
            "post_scene_ids": satellite.get("post_scene_ids", []),
            "interpretation": "CONTINUOUS_CHANGE_SIGNAL_ONLY",
            "severity_class": None,
        },
        "physical_aboveground_pool": physical_pool,
        "field_evidence": field_states,
        "registry_context_status": (
            "SUPPLIED_HUMAN_REVIEW_REQUIRED" if registry_complete
            else "EXTERNAL_AUTHORITY_INPUT_REQUIRED"
        ),
        "missing_evidence": missing,
        "extension_handoff": [
            "Confirm the project boundary, fire date, access authority, and safety constraints.",
            "Record geotagged observations of live trees, standing deadwood, down wood, litter, and erosion.",
            "Collect soil or pyrogenic-carbon material only under an approved minimal-impact sampling and chain-of-custody plan.",
            "Document salvage, cutting, vehicle access, suppression, erosion control, and other post-fire interventions.",
            "Return source files and field notes; do not decide credit eligibility or represent the screen as certification.",
        ],
        "human_decisions_required": [
            "field evidence acceptance",
            "coefficient definition and calibration",
            "registry or contract treatment",
            "portfolio, reserve, remediation, or insurance action",
        ],
        "physical_remaining_asset_tco2e": (
            physical_pool["physical_aboveground_carbon_tco2e_mid"] if physical_pool else None
        ),
        "credit_quantity_tco2e": None,
        "credit_secured": False,
        "registry_eligible": None,
        "claim_boundary": CLAIM_BOUNDARY,
    }


def render_remaining_asset_statement(screen: dict) -> str:
    """Render the machine-readable screen as a compact buyer-review Markdown statement."""
    project = screen["project"]
    satellite = screen["satellite_observation"]
    pool = screen.get("physical_aboveground_pool")
    pool_line = "Not calculated; a sourced post-fire biomass input is required."
    if pool:
        pool_line = (
            f"{pool['physical_aboveground_carbon_tco2e_low']:.2f}–"
            f"{pool['physical_aboveground_carbon_tco2e_high']:.2f} tCO2e physical aboveground "
            f"pool (mid {pool['physical_aboveground_carbon_tco2e_mid']:.2f}); not a credit quantity."
        )
    missing = "\n".join(f"- {item}" for item in screen["missing_evidence"]) or "- None recorded"
    return f"""# Remaining Carbon Asset Screen

**Project:** {project['name']}  
**Boundary:** {project['boundary_id']}  
**Fire date:** {project['fire_date']}  
**Status:** `{screen['status']}`  
**Input SHA-256:** `{screen['input_sha256']}`

## Remote observation

- Satellite status: `{satellite['status']}`
- Valid paired coverage: {satellite['valid_fraction']:.1%}
- Mean dNBR: {satellite['dnbr_mean']}
- Interpretation: continuous change signal only; no severity class assigned

## Physical aboveground pool

{pool_line}

## Evidence still required

{missing}

## Decision boundary

{screen['claim_boundary']}

**Credit quantity:** not calculated  
**Credit secured:** no  
**Registry eligibility:** external authority decision required
"""
