"""Read-only list of the decision kernels the Viridis Canon entered by auto-intake.

Built by tools/refresh_from_canon.py from the canon's os/research_statements.json. A kernel
is live here exactly when it is live in the canon (os/core.json plus os/admissions.json);
this file grants no authority of its own and issues no certificate.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

DEFAULT_PATH = Path(__file__).with_name("canon_auto_kernels.json")
STANDARD = "VOS-CANON-AUTO-KERNELS-1"
REQUIRED = ("function_id", "name", "status", "live", "statement", "doi", "research_run", "boundary",
            "proven", "assumed", "rollback", "certification_authority", "manifest_sha256")


class CanonAutoKernels:
    def __init__(self, path: Path = DEFAULT_PATH):
        payload = json.loads(path.read_text(encoding="utf-8"))
        if payload.get("standard") != STANDARD:
            raise ValueError("invalid canon auto-kernel list standard")
        if re.fullmatch(r"[0-9a-f]{40}", str(payload.get("source", {}).get("canon_commit", ""))) is None:
            raise ValueError("invalid canon commit")
        seen = set()
        for row in payload.get("kernels", []):
            missing = [k for k in REQUIRED if k not in row]
            if missing:
                raise ValueError(f"auto kernel {row.get('function_id')} is missing {missing}")
            if row["function_id"] in seen:
                raise ValueError(f"duplicate auto kernel {row['function_id']}")
            seen.add(row["function_id"])
            if row["certification_authority"] is not False:
                raise ValueError(f"{row['function_id']}: auto kernels carry no certification authority")
            if row["live"] != (row["status"] == "LIVE"):
                raise ValueError(f"{row['function_id']}: live flag disagrees with status {row['status']}")
        self._payload = payload

    def kernels(self) -> list[dict]:
        return list(self._payload["kernels"])

    def live(self) -> list[dict]:
        return [k for k in self._payload["kernels"] if k["live"]]

    def as_dict(self) -> dict:
        return json.loads(json.dumps(self._payload))
