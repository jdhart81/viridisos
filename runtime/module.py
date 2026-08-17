"""The ViridisOS module contract (L2).

A module is a self-contained priced capability backed by exactly one verified theorem.
Enforces the platform invariants:

  A-1 Backing-or-nothing   — certify only with a resolvable, gate-passed canon DOI.
  A-3 Blocked propagation  — unverified/integrity-flagged backing ⇒ BLOCKED; certify() raises.
  A-4 Provenance everywhere — every output carries backing + input hashes + timestamp.

Uses stdlib dataclasses (no third-party deps) so the runtime installs nowhere and
stays deterministic. `compute()` typically wraps an existing research-run engine.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from enum import Enum
from typing import Optional

from .provenance import hash_inputs
from .canon_resolver import CanonResolver


class ModuleState(str, Enum):
    READY = "READY"        # verified backing → may certify
    BLOCKED = "BLOCKED"    # unverified / integrity-flagged → preview only


@dataclass(frozen=True)
class Backing:
    doi: str
    lean_module: str
    aristotle_id: str
    verified: bool
    integrity_flag: bool = False


@dataclass(frozen=True)
class Provenance:
    backing_doi: str
    lean_module: str
    input_hashes: dict
    timestamp: str
    module_version: str


@dataclass(frozen=True)
class ModuleOutput:
    module_id: str
    values: dict
    units: dict
    provenance: Provenance

    def to_dict(self) -> dict:
        d = asdict(self)
        return d


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


class CertifyBlocked(RuntimeError):
    """Raised when a BLOCKED module is asked to produce a certifiable output (A-3)."""


class Module(ABC):
    id: str = ""
    name: str = ""
    line: str = ""
    version: str = "0.1.0"
    backing: Backing = None  # type: ignore

    def __init__(self, resolver: Optional[CanonResolver] = None):
        self.resolver = resolver or CanonResolver()

    # --- kernel -----------------------------------------------------------
    @abstractmethod
    def compute(self, inputs: dict) -> dict:
        """The numeric kernel — usually a wrapped research-run engine. Returns raw values."""

    def units(self) -> dict:  # override to declare units
        return {}

    # --- state ------------------------------------------------------------
    def certify_ready(self) -> bool:
        """A-1 + A-3: verified backing, no integrity flag, and DOI is gate-passed in canon."""
        b = self.backing
        if b is None or not b.verified or b.integrity_flag:
            return False
        return self.resolver.is_gate_passed(b.doi)

    def state(self) -> ModuleState:
        return ModuleState.READY if self.certify_ready() else ModuleState.BLOCKED

    # --- outputs ----------------------------------------------------------
    def _output(self, inputs: dict) -> ModuleOutput:
        values = self.compute(inputs)
        prov = Provenance(
            backing_doi=self.backing.doi if self.backing else "",
            lean_module=self.backing.lean_module if self.backing else "",
            input_hashes=hash_inputs(inputs),
            timestamp=_now(),
            module_version=self.version,
        )
        return ModuleOutput(module_id=self.id, values=values, units=self.units(), provenance=prov)

    def preview(self, inputs: dict) -> ModuleOutput:
        """Always allowed — runs the kernel without any certification claim."""
        return self._output(inputs)

    def certifiable_output(self, inputs: dict) -> ModuleOutput:
        """Output intended for certification. Refuses if the module is BLOCKED (A-3)."""
        if not self.certify_ready():
            raise CertifyBlocked(
                f"module '{self.id}' is BLOCKED: backing not verified / not gate-passed / integrity-flagged"
            )
        return self._output(inputs)
