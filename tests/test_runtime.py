"""Runtime (L2) tests — enforce A-1, A-3, A-4."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from runtime.module import Module, Backing, CertifyBlocked, ModuleState
from runtime.registry import ModuleRegistry
from runtime.canon_resolver import CanonResolver
from runtime.provenance import hash_inputs, hash_value


VERIFIED_DOI = "10.5281/zenodo.TESTGOOD"
RESOLVER = CanonResolver(entries={VERIFIED_DOI: {"verified": True, "lean_module": "Good"}})


class _Demo(Module):
    id = "demo"; name = "Demo"; line = "Test"; version = "1.0.0"
    backing = Backing(doi=VERIFIED_DOI, lean_module="Good", aristotle_id="a", verified=True)
    def compute(self, inputs):
        return {"sum": inputs["a"] + inputs["b"]}


def _mk(backing=None, resolver=RESOLVER):
    m = _Demo(resolver=resolver)
    if backing is not None:
        m.backing = backing
    return m


def test_preview_always_allowed_even_when_blocked():
    m = _mk(backing=Backing(doi="x", lean_module="l", aristotle_id="a", verified=False))
    out = m.preview({"a": 1, "b": 2})
    assert out.values == {"sum": 3}
    assert m.state() is ModuleState.BLOCKED


def test_A1_certify_ready_true_only_when_gate_passed():
    assert _mk().certify_ready() is True
    # verified flag but DOI not in canon → not gate-passed
    m = _mk(backing=Backing(doi="10.5281/zenodo.NOTINCANON", lean_module="l", aristotle_id="a", verified=True))
    assert m.certify_ready() is False


def test_A3_blocked_module_refuses_certifiable_output():
    m = _mk(backing=Backing(doi=VERIFIED_DOI, lean_module="l", aristotle_id="a",
                            verified=True, integrity_flag=True))
    assert m.state() is ModuleState.BLOCKED
    try:
        m.certifiable_output({"a": 1, "b": 2})
        assert False, "expected CertifyBlocked"
    except CertifyBlocked:
        pass


def test_A4_provenance_present_and_hashes_inputs():
    out = _mk().certifiable_output({"a": 1, "b": 2})
    p = out.provenance
    assert p.backing_doi == VERIFIED_DOI and p.lean_module == "Good"
    assert p.input_hashes == hash_inputs({"a": 1, "b": 2})
    assert p.module_version == "1.0.0" and p.timestamp


def test_provenance_deterministic():
    assert hash_value({"a": 1, "b": 2}) == hash_value({"b": 2, "a": 1})


def test_registry_register_discover_reject_dupes():
    r = ModuleRegistry()
    r.register(_mk())
    assert len(r) == 1 and r.list_modules()[0]["id"] == "demo"
    try:
        r.register(_mk())
        assert False, "expected duplicate rejection"
    except ValueError:
        pass


if __name__ == "__main__":
    import traceback
    fns = [g for n, g in sorted(globals().items()) if n.startswith("test_") and callable(g)]
    p = f = 0
    for fn in fns:
        try:
            fn(); p += 1; print(f"PASS  {fn.__name__}")
        except Exception:
            f += 1; print(f"FAIL  {fn.__name__}"); traceback.print_exc()
    print(f"\n{p} passed, {f} failed")
    raise SystemExit(1 if f else 0)
