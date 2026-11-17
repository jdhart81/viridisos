#!/usr/bin/env python3
"""Refresh ViridisOS's list of auto-intake kernels from a Viridis Canon checkout.

The canon's auto-intake (canon_core/auto_intake.py, docs/auto_intake/README.md) enters
PROVEN science-engine results as decision kernels and records each in
os/research_statements.json. This tool copies that list, with each kernel's manifest
digest, boundary and rollback, into runtime/canon_auto_kernels.json so ViridisOS serves the
same live set as the canon (GET /auto-kernels). It reads only; it decides nothing.

Invariants (tests/test_canon_auto_kernels.py):
  R1 every canon ledger entry with a function appears once, with the canon's status;
     LIVE here exactly when LIVE in the canon (in os/core.json and os/admissions.json)
  R2 every kernel carries its boundary, what is proven, what is assumed, its rollback,
     and certification_authority false; none is called product-ready
  R3 deterministic: the same canon commit gives byte-identical output
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
from pathlib import Path

STANDARD = "VOS-CANON-AUTO-KERNELS-1"
DEFAULT_OUTPUT = Path(__file__).resolve().parents[1] / "runtime" / "canon_auto_kernels.json"
STATUSES = ("ENTERED", "LIVE", "ROLLED_BACK")


def _json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def _commit(canon: Path) -> str:
    out = subprocess.run(["git", "-C", str(canon), "rev-parse", "HEAD"], capture_output=True, text=True)
    return out.stdout.strip()


def build(canon: Path, canon_commit: str) -> dict:
    if re.fullmatch(r"[0-9a-f]{40}", canon_commit or "") is None:
        raise ValueError("canon_commit must be a full 40-character Git commit")
    policy = _json(canon / "os" / "auto_intake.json")
    ledger = _json(canon / "os" / "research_statements.json")
    core = set(_json(canon / "os" / "core.json")["function_order"])
    admitted = {a["id"] for a in _json(canon / "os" / "admissions.json")["admitted"]}
    package_root = canon / policy.get("package_root", "research")
    kernels = []
    for entry in sorted(ledger["entries"], key=lambda e: e["statement"]):
        fid = entry.get("function_id")
        if not fid:
            continue
        if entry["status"] not in STATUSES:
            raise ValueError(f"{fid}: unknown status {entry['status']}")
        manifest_path = package_root / fid / "function.json"
        manifest = _json(manifest_path)
        live = fid in core and fid in admitted
        if live != (entry["status"] == "LIVE"):
            raise ValueError(f"{fid}: ledger says {entry['status']} but the live list says {'live' if live else 'not live'}")
        text = " ".join(str(manifest.get(k, "")) for k in ("name", "summary", "scope", "boundary"))
        if re.search(r"product[- ]ready|production[- ]ready", text, re.I):
            raise ValueError(f"{fid}: a kernel is never called product-ready")
        kernels.append({
            "function_id": fid,
            "name": manifest["name"],
            "status": entry["status"],
            "live": live,
            "statement": entry["statement"],
            "class": entry["class"],
            "strengthens": entry.get("strengthens"),
            "decision_family": manifest["decision_family"],
            "doi": manifest["doi"],
            "research_run": entry["run_dir"],
            "statement_sha256": entry["statement_sha256"],
            "manifest_path": manifest_path.relative_to(canon).as_posix(),
            "manifest_sha256": hashlib.sha256(manifest_path.read_bytes()).hexdigest(),
            "summary": manifest["summary"],
            "boundary": manifest["boundary"],
            "proven": entry["proven"],
            "assumed": entry["assumed"],
            "empirical_validation": manifest["empirical_validation"],
            "live_at": entry.get("live_at"),
            "rolled_back_at": entry.get("rolled_back_at"),
            "rollback": entry["rollback"],
            "certification_authority": False,
        })
    return {
        "standard": STANDARD,
        "source": {"repository": "https://github.com/jdhart81/viridis-canon", "canon_commit": canon_commit,
                   "ledger": "os/research_statements.json", "policy_standard": policy["standard"]},
        "policy": {"go_live": bool(policy["go_live"]), "go_live_decision": policy.get("go_live_decision", ""),
                   "automatic_certification_authority": False},
        "stats": {"kernels": len(kernels), "live": sum(k["live"] for k in kernels),
                  "rolled_back": sum(k["status"] == "ROLLED_BACK" for k in kernels)},
        "kernels": kernels,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--canon", type=Path, required=True, help="viridis-canon checkout (main after the merge)")
    parser.add_argument("--canon-commit", default="", help="defaults to the checkout's HEAD")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--check", action="store_true", help="fail if the output is not current")
    args = parser.parse_args()
    document = build(args.canon.resolve(), args.canon_commit or _commit(args.canon))
    text = json.dumps(document, indent=2, ensure_ascii=False) + "\n"
    if args.check:
        current = args.output.read_text(encoding="utf-8") if args.output.exists() else ""
        if current != text:
            print(f"{args.output} is not current with the canon")
            return 1
        print("auto kernels current")
        return 0
    args.output.write_text(text, encoding="utf-8")
    print(json.dumps(document["stats"], sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
