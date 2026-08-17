"""Carbon Continuity kernel and fail-closed product-boundary tests."""

from __future__ import annotations

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from modules.carbon_continuity import CarbonContinuityModule
from modules.carbon_continuity.engine import evaluate_threshold
from runtime.module import CertifyBlocked, ModuleState


def test_exact_boundary_is_continuity_capable():
    result = evaluate_threshold(a=0.6, d=0.8, r=0.4, p=0.2)
    assert math.isclose(result["loop_gain"], result["leakage_product"])
    assert math.isclose(result["continuity_number"], 1.0)
    assert result["threshold_met"] is True
    assert result["witness_nondecreasing"] is True


def test_strict_threshold_has_durable_growth():
    result = evaluate_threshold(a=0.6, d=0.8, r=0.5, p=0.2)
    assert result["continuity_number"] > 1.0
    assert result["threshold_met"] is True
    assert result["witness_next_durable"] > result["witness_durable"]


def test_below_threshold_is_depleting_in_model():
    result = evaluate_threshold(a=0.6, d=0.8, r=0.2, p=0.2)
    assert math.isclose(result["continuity_number"], 0.5)
    assert result["threshold_met"] is False
    assert result["regime"] == "DEPLETING_WITHIN_MODEL"
    assert result["witness_nondecreasing"] is False


def test_output_never_manufactures_market_claims():
    result = evaluate_threshold(a=0.7, d=0.95, r=0.25, p=0.1)
    assert result["market_use"] == "decision_support_only"
    assert result["formal_claim_type"] == "supplied_coefficient_threshold_evaluation"
    assert result["market_claim_status"] == "MODEL_OUTPUT_ONLY"
    assert result["empirically_calibrated"] is False
    assert result["underwriting_advice"] is False
    assert result["credit_quantity_tco2e"] is None
    assert "not a carbon credit" in result["claim_boundary"]


def test_module_rejects_missing_coefficients_as_bad_input():
    module = CarbonContinuityModule()
    try:
        module.preview({"a": 0.6, "d": 0.8, "r": 0.5})
        assert False, "expected missing p to fail"
    except ValueError as exc:
        assert "missing required coefficient" in str(exc)


def test_invalid_domain_is_rejected():
    bad_inputs = [
        {"a": -0.1, "d": 0.8, "r": 0.2, "p": 0.2},
        {"a": 1.0, "d": 0.8, "r": 0.2, "p": 0.2},
        {"a": 0.6, "d": 1.0, "r": 0.2, "p": 0.2},
        {"a": 0.6, "d": 0.8, "r": 0.0, "p": 0.2},
        {"a": 0.6, "d": 0.8, "r": 0.2, "p": float("nan")},
        {"a": 0.6, "d": 0.8, "r": float("inf"), "p": 0.2},
    ]
    for values in bad_inputs:
        try:
            evaluate_threshold(**values)
            assert False, f"expected invalid input to fail: {values}"
        except ValueError:
            pass


def test_pending_canon_entry_allows_preview_but_blocks_certification():
    module = CarbonContinuityModule()
    assert module.state() == ModuleState.BLOCKED
    output = module.preview({"a": 0.6, "d": 0.8, "r": 0.5, "p": 0.2})
    assert output.module_id == "carbon-continuity"
    assert output.values["threshold_met"] is True
    try:
        module.certifiable_output({"a": 0.6, "d": 0.8, "r": 0.5, "p": 0.2})
        assert False, "expected pending paper to block certification"
    except CertifyBlocked:
        pass


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
