"""Certification (L3) tests — enforce A-1, A-2, A-3 + revocation."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from runtime.module import Module, Backing, CertifyBlocked
from runtime.canon_resolver import CanonResolver
from certification.certifier import Certifier

GOOD = "10.5281/zenodo.CERTGOOD"
RESOLVER = CanonResolver(entries={GOOD: {"verified": True, "lean_module": "Good"}})


class _Demo(Module):
    id = "demo"; name = "Demo"; line = "Test"; version = "1.0.0"
    backing = Backing(doi=GOOD, lean_module="Good", aristotle_id="a", verified=True)
    def compute(self, inputs):
        return {"score": round(inputs["x"] * 2.0, 6)}


def _module(backing=None):
    m = _Demo(resolver=RESOLVER)
    if backing is not None:
        m.backing = backing
    return m


def _certifier():
    return Certifier(resolver=RESOLVER)


def test_issue_then_verify_roundtrip():
    c = _certifier()
    m = _module()
    inputs = {"x": 3.0}
    cert = c.issue(m, subject="parcel-42", inputs=inputs)
    assert cert.claim.values == {"score": 6.0}
    assert c.verify(cert, m, inputs) is True


def test_A1_issue_blocked_without_gate_passed_backing():
    c = _certifier()
    m = _module(backing=Backing(doi="10.5281/zenodo.MISSING", lean_module="l",
                                aristotle_id="a", verified=True))
    try:
        c.issue(m, subject="p", inputs={"x": 1.0})
        assert False, "expected CertifyBlocked (A-1)"
    except CertifyBlocked:
        pass


def test_A3_issue_blocked_for_integrity_flagged_module():
    c = _certifier()
    m = _module(backing=Backing(doi=GOOD, lean_module="l", aristotle_id="a",
                                verified=True, integrity_flag=True))
    try:
        c.issue(m, subject="p", inputs={"x": 1.0})
        assert False, "expected CertifyBlocked (A-3)"
    except CertifyBlocked:
        pass


def test_A2_tampered_values_fail_verify():
    c = _certifier()
    m = _module()
    inputs = {"x": 3.0}
    cert = c.issue(m, subject="p", inputs=inputs)
    # tamper with the certified values
    tampered = cert.__class__(
        claim=cert.claim.__class__(**{**cert.claim.__dict__, "values": {"score": 999.0}}),
        signature=cert.signature, key_id=cert.key_id, standard_id=cert.standard_id,
        certificate_id=cert.certificate_id,
    )
    assert c.verify(tampered, m, inputs) is False


def test_A2_wrong_inputs_fail_verify():
    c = _certifier()
    m = _module()
    cert = c.issue(m, subject="p", inputs={"x": 3.0})
    assert c.verify(cert, m, {"x": 4.0}) is False    # input hashes + recompute mismatch


def test_revocation_invalidates_certificate():
    c = _certifier()
    m = _module()
    inputs = {"x": 3.0}
    cert = c.issue(m, subject="p", inputs=inputs)
    assert c.verify(cert, m, inputs) is True
    c.revoke(cert.certificate_id, reason="backing weakened")
    assert c.verify(cert, m, inputs) is False


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
