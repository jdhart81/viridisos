"""Canon DOI resolver — the root of trust (invariant A-1).

Resolves a theorem DOI to its canon status. A module may only certify if its backing
DOI resolves to a gate-passed canon entry. Reads the live research-pipeline index when
available; falls back to an injectable fixture so the flow is testable offline. The
interface is stable so the fallback swaps to the live index/ledger without code change.
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

# Live index produced by the research pipeline. A small DOI-bound public snapshot
# ships with the reference package so a clean install fails closed but remains usable.
_WORKSPACE_INDEX = (
    Path(__file__).resolve().parents[2]
    / "RESEARCH_PIPELINE_v2" / "canon_fingerprint_index.json"
)
_BUNDLED_INDEX = Path(__file__).with_name("bundled_canon_index.json")
_DEFAULT_INDEX = Path(
    os.environ.get(
        "VIRIDISOS_CANON_INDEX",
        str(_WORKSPACE_INDEX if _WORKSPACE_INDEX.is_file() else _BUNDLED_INDEX),
    )
)


@dataclass(frozen=True)
class CanonEntry:
    doi: str
    verified: bool          # gate-passed canon entry
    lean_module: str = ""
    name: str = ""


class CanonResolver:
    """Resolve DOIs against the canon. Inject `entries` for tests/offline use."""

    def __init__(self, entries: Optional[dict] = None, index_path: Optional[Path] = None):
        self._entries: dict[str, CanonEntry] = {}
        if entries is not None:
            for doi, e in entries.items():
                self._entries[doi] = CanonEntry(doi=doi, **e) if isinstance(e, dict) else e
        else:
            self._load_index(index_path or _DEFAULT_INDEX)

    def _load_index(self, path: Path) -> None:
        if not path.exists():
            return
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            return
        for rec in data:
            doi = rec.get("doi") or ""
            if not doi:
                continue
            # a record present in the published canon index is, by construction, gate-passed
            self._entries[doi] = CanonEntry(
                doi=doi, verified=True, lean_module=rec.get("id", ""), name=rec.get("name", "")
            )

    def resolve(self, doi: str) -> Optional[CanonEntry]:
        return self._entries.get(doi)

    def is_gate_passed(self, doi: str) -> bool:
        e = self.resolve(doi)
        return bool(e and e.verified)
