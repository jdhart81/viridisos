from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from runtime.research_registry import ResearchRegistry


def test_2026_08_15_wave_is_ingested_without_product_overclaim():
    registry = ResearchRegistry()
    records = registry.records()
    assert len(records) == 7
    assert {row.abbreviation for row in records} == {
        "SBB", "ICC", "PCR", "RC", "ACC", "SSBC", "CSHC"
    }
    assert all(row.state == "BACKLOG_NO_WRAPPER" for row in records)
    assert all(not row.has_product_wrapper for row in records)
    assert all(not row.certification_ready for row in records)
    assert all(not row.spine_admitted for row in records)
    assert {row.doi for row in records} == {
        "10.5281/zenodo.21971041",
        "10.5281/zenodo.21971042",
        "10.5281/zenodo.21971043",
        "10.5281/zenodo.21971046",
        "10.5281/zenodo.21971047",
        "10.5281/zenodo.21971052",
        "10.5281/zenodo.21971057",
    }


def test_seed_source_result_routes_to_restoration_backlog():
    record = ResearchRegistry().get("ssbc")
    assert record is not None
    assert record.doi == "10.5281/zenodo.21971057"
    assert record.product_line == "Restoration"
    assert record.successor_version_candidate == "0.2.1-release-reconciled"


if __name__ == "__main__":
    import traceback

    tests = [value for name, value in sorted(globals().items()) if name.startswith("test_") and callable(value)]
    failed = 0
    for test in tests:
        try:
            test()
            print(f"PASS  {test.__name__}")
        except Exception:
            failed += 1
            print(f"FAIL  {test.__name__}")
            traceback.print_exc()
    print(f"\n{len(tests) - failed} passed, {failed} failed")
    raise SystemExit(1 if failed else 0)
