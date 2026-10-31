from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tools"))

from api.service import ViridisOSService, dispatch
from runtime.canon_kernel_registry import CanonKernelRegistry
from runtime.registry import ModuleRegistry
from sync_canon_kernels import build_registry, canonical_digest


def test_public_canon_is_completely_dispositioned():
    registry = CanonKernelRegistry()
    records = registry.records()
    assert len(records) == 120
    assert len(tuple(registry.candidates())) == 26
    assert all(row.disposition for row in records)
    assert all(row.certification_authority is False for row in records)


def test_candidate_requires_both_verified_and_gate_passed():
    for row in CanonKernelRegistry().records():
        expected = row.canon_status == "verified" and row.canon_integrity == "gate-passed"
        assert row.kernel_candidate is expected


def test_existing_modules_are_bound_without_promoting_working_records():
    expected = {
        "series-forestnucleation": "restoration",
        "series-afforestationstewardship": "afforestation",
        "series-gaianharmonization": "harmonization",
        "carbon-continuity-after-wildfire": "carbon-continuity",
    }
    registry = CanonKernelRegistry()
    for record_id, module_id in expected.items():
        row = registry.get(record_id)
        assert row is not None
        assert row.module_id == module_id
        assert row.kernel_state == "NOT_ELIGIBLE"
        assert "RECONCILIATION_REQUIRED" in row.disposition or "ADMISSION_REQUIRED" in row.disposition


def test_bound_disposition_matches_module_state():
    # A binding may say MODULE_BLOCKED_* only while the bound module is actually BLOCKED.
    # LIVE modules on records Canon has not admitted stay MODULE_CATALOG_RECONCILIATION_REQUIRED.
    from viridis_platform import catalog_status
    states = {row["id"]: row["state"] for row in catalog_status()}
    for row in CanonKernelRegistry().records():
        if not row.module_id:
            continue
        assert row.module_id in states, row.module_id
        if states[row.module_id] == "READY":
            assert not row.disposition.startswith("MODULE_BLOCKED"), row.record_id
        else:
            assert row.disposition.startswith("MODULE_BLOCKED"), row.record_id


def test_sync_never_activates_a_new_verified_record():
    row = {
        "record_id": "example", "title": "Example", "path": "Example.lean",
        "source_sha256": "a" * 64, "doi": "10.5281/zenodo.1",
        "lean_module": "Example", "status": "verified", "integrity": "gate-passed",
    }
    catalog = {
        "schema": "https://jdhart81.github.io/viridis-canon/schemas/research-catalog-v1.json",
        "publication_scope": "public", "release": "test", "concept_doi": "",
        "repository": "https://example.test/canon", "honesty_notice": "test",
        "human_publish_gate": True, "stats": {}, "records": [row],
    }
    catalog["catalog_digest"] = canonical_digest(catalog)
    record = build_registry(catalog, "0" * 40, {})["records"][0]
    assert record["kernel_state"] == "KERNEL_CANDIDATE"
    assert record["disposition"] == "BACKLOG_NO_WRAPPER"
    assert record["module_id"] == ""
    assert record["decision_tree_paths"] == []
    assert record["certification_authority"] is False


def test_api_exposes_registry_without_authority():
    service = ViridisOSService(ModuleRegistry())
    status, body = dispatch(service, "GET", "/research-kernels", None)
    assert status == 200
    assert body["stats"]["records"] == 120
    assert body["stats"]["kernel_candidates"] == 26
    assert all(row["certification_authority"] is False for row in body["records"])


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
