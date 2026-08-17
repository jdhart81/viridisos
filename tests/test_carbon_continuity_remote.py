"""Remote-first Remaining Carbon Asset screen tests."""

from __future__ import annotations

import sys
from copy import deepcopy
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from modules.carbon_continuity.remote_screen import (
    build_remaining_asset_screen,
    render_remaining_asset_statement,
)


def request(*, include_biomass: bool = True) -> dict:
    value = {
        "project": {
            "name": "Synthetic Burned Forest Demonstration",
            "boundary_id": "sha256:demo-boundary-not-a-real-project",
            "fire_date": "2026-07-14",
            "registry_project_id": None,
        },
        "satellite_burn_change": {
            "algorithm_version": "viridis_sentinel_nbr_change_v1",
            "status": "REMOTE_SCREEN_READY",
            "valid_fraction": 0.92,
            "minimum_valid_fraction": 0.60,
            "dnbr_mean": 0.41,
            "pre_scene_ids": ["SYNTHETIC_PRE"],
            "post_scene_ids": ["SYNTHETIC_POST"],
        },
        "field_evidence": {},
        "registry_context": {},
    }
    if include_biomass:
        value["aboveground_biomass"] = {
            "post_agb_mg_ha": 40.0,
            "area_ha": 100.0,
            "carbon_fraction": 0.47,
            "carbon_fraction_source": "customer-supplied demonstration assumption",
            "relative_uncertainty": 0.20,
            "source": "synthetic GEDI-like demonstration value",
            "method": "demonstration only; not a real measurement",
        }
    return value


def test_remote_screen_never_mints_credit_claim():
    result = build_remaining_asset_screen(request())
    assert result["status"] == "REMOTE_SCREEN_READY_FIELD_CONFIRMATION_REQUIRED"
    assert result["physical_remaining_asset_tco2e"] > 0
    assert result["credit_quantity_tco2e"] is None
    assert result["credit_secured"] is False
    assert result["registry_eligible"] is None


def test_biomass_conversion_is_explicit_physical_pool_with_range():
    result = build_remaining_asset_screen(request())
    pool = result["physical_aboveground_pool"]
    assert pool["physical_aboveground_carbon_tco2e_low"] < pool["physical_aboveground_carbon_tco2e_mid"]
    assert pool["physical_aboveground_carbon_tco2e_high"] > pool["physical_aboveground_carbon_tco2e_mid"]
    assert pool["credit_quantity_tco2e"] is None


def test_missing_biomass_stays_missing_instead_of_using_default():
    result = build_remaining_asset_screen(request(include_biomass=False))
    assert result["physical_aboveground_pool"] is None
    assert result["physical_remaining_asset_tco2e"] is None
    assert any("aboveground biomass" in item for item in result["missing_evidence"])


def test_cloudy_satellite_receipt_holds_entire_screen():
    value = request()
    value["satellite_burn_change"].update({
        "status": "INSUFFICIENT_VALID_PIXELS",
        "valid_fraction": 0.15,
        "dnbr_mean": None,
    })
    result = build_remaining_asset_screen(value)
    assert result["status"] == "INSUFFICIENT_REMOTE_EVIDENCE"


def test_field_rows_require_provenance_not_boolean_assertion():
    value = request()
    value["field_evidence"]["soil_carbon"] = {"status": "OBSERVED"}
    result = build_remaining_asset_screen(value)
    assert result["field_evidence"]["soil_carbon"] == "FIELD_CONFIRMATION_REQUIRED"


def test_receipt_hash_and_report_are_deterministic():
    first = build_remaining_asset_screen(request())
    second = build_remaining_asset_screen(deepcopy(request()))
    assert first["input_sha256"] == second["input_sha256"]
    report = render_remaining_asset_statement(first)
    assert "not a credit quantity" in report
    assert "Credit secured:** no" in report


if __name__ == "__main__":
    import traceback

    fns = [g for n, g in sorted(globals().items()) if n.startswith("test_") and callable(g)]
    passed = failed = 0
    for fn in fns:
        try:
            fn()
            passed += 1
            print(f"PASS  {fn.__name__}")
        except Exception:
            failed += 1
            print(f"FAIL  {fn.__name__}")
            traceback.print_exc()
    print(f"\n{passed} passed, {failed} failed")
    raise SystemExit(1 if failed else 0)
