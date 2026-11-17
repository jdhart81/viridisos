"""Auto-intake kernels from the Viridis Canon (tools/refresh_from_canon.py, GET /auto-kernels).

  R1 every canon ledger entry with a function appears once; live here exactly when live there
  R2 each kernel carries boundary, proven, assumed, rollback; no certification authority
  R3 the same canon commit gives byte-identical output
"""

from __future__ import annotations

import json
import shutil
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tools"))

from api.service import ViridisOSService, dispatch
from refresh_from_canon import build
from runtime.canon_auto_kernels import CanonAutoKernels
from runtime.registry import ModuleRegistry

COMMIT = "a" * 40


def _canon(statuses):
    tmp = Path(tempfile.mkdtemp())
    (tmp / "os").mkdir()
    entries, core, admitted = [], ["restoration"], [{"id": "restoration"}]
    for i, status in enumerate(statuses):
        fid = f"kernel-{i}"
        pkg = tmp / "research" / fid
        pkg.mkdir(parents=True)
        (pkg / "function.json").write_text(json.dumps({
            "id": fid, "name": f"Kernel {i}", "summary": "A proven kernel for tests of the refresh tool.",
            "scope": "test", "boundary": "Does not establish anything empirical.", "decision_family": "governance-coordination",
            "doi": "10.5281/zenodo.0000000", "empirical_validation": "NOT_VALIDATED"}), encoding="utf-8")
        entries.append({"statement": f"P9.S{i}", "class": "B", "status": status, "function_id": fid, "strengthens": "byproduct-exchange",
                        "run_dir": "runs/2026-11-16_P3", "statement_sha256": "b" * 64, "proven": "p", "assumed": "a",
                        "live_at": "2026-11-17T00:00:00Z" if status == "LIVE" else None, "rolled_back_at": None,
                        "rollback": f"python3 -m canon_core auto-intake rollback --function {fid}", "reason": "r"})
        if status == "LIVE":
            core.append(fid)
            admitted.append({"id": fid})
    entries.append({"statement": "P9.Declined", "class": "C", "status": "DECLINED", "function_id": None})
    (tmp / "os" / "research_statements.json").write_text(json.dumps({"entries": entries}), encoding="utf-8")
    (tmp / "os" / "core.json").write_text(json.dumps({"function_order": core}), encoding="utf-8")
    (tmp / "os" / "admissions.json").write_text(json.dumps({"admitted": admitted}), encoding="utf-8")
    (tmp / "os" / "auto_intake.json").write_text(json.dumps({"standard": "VOS-AUTO-INTAKE-1", "go_live": True,
                                                             "package_root": "research"}), encoding="utf-8")
    return tmp


def test_ledger_is_mirrored_with_live_flags():  # R1
    canon = _canon(["LIVE", "ROLLED_BACK", "ENTERED"])
    try:
        doc = build(canon, COMMIT)
        rows = {k["function_id"]: k for k in doc["kernels"]}
        assert set(rows) == {"kernel-0", "kernel-1", "kernel-2"}
        assert [rows[f]["live"] for f in sorted(rows)] == [True, False, False]
        assert doc["stats"] == {"kernels": 3, "live": 1, "rolled_back": 1}
    finally:
        shutil.rmtree(canon, ignore_errors=True)


def test_disagreement_with_the_live_list_is_refused():  # R1
    canon = _canon(["LIVE"])
    try:
        (canon / "os" / "core.json").write_text(json.dumps({"function_order": []}), encoding="utf-8")
        try:
            build(canon, COMMIT)
            raise AssertionError("expected a refusal")
        except ValueError as error:
            assert "live list" in str(error)
    finally:
        shutil.rmtree(canon, ignore_errors=True)


def test_every_kernel_carries_its_boundary_and_rollback():  # R2
    canon = _canon(["LIVE"])
    try:
        row = build(canon, COMMIT)["kernels"][0]
        for key in ("boundary", "proven", "assumed", "rollback"):
            assert row[key]
        assert row["certification_authority"] is False
        manifest = canon / "research" / "kernel-0" / "function.json"
        data = json.loads(manifest.read_text(encoding="utf-8"))
        data["summary"] += " Product-ready."
        manifest.write_text(json.dumps(data), encoding="utf-8")
        try:
            build(canon, COMMIT)
            raise AssertionError("expected a refusal")
        except ValueError as error:
            assert "product-ready" in str(error)
    finally:
        shutil.rmtree(canon, ignore_errors=True)


def test_output_is_deterministic():  # R3
    canon = _canon(["LIVE", "ENTERED"])
    try:
        assert json.dumps(build(canon, COMMIT)) == json.dumps(build(canon, COMMIT))
    finally:
        shutil.rmtree(canon, ignore_errors=True)


def test_checked_in_list_loads_and_api_serves_it():
    kernels = CanonAutoKernels()
    status, body = dispatch(ViridisOSService(ModuleRegistry()), "GET", "/auto-kernels", None)
    assert status == 200
    assert body["standard"] == "VOS-CANON-AUTO-KERNELS-1"
    assert len(body["kernels"]) == len(kernels.kernels())
    assert all(k["certification_authority"] is False for k in body["kernels"])


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
