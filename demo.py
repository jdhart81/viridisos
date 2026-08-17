"""ViridisOS end-to-end demo against the LIVE canon.

Assembles the full platform, prints the catalog (which modules are LIVE vs BLOCKED per the
real canon), then issues + locally recomputes a self-rooted development certificate
(Restoration / FNT). Shows A-1 in action: a module whose theorem is published certifies; one
whose theorem is pending is refused.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from viridis_platform import build_platform, catalog_status
from runtime.module import CertifyBlocked


def main() -> None:
    print("== ViridisOS catalog (resolved against the live canon) ==")
    for row in catalog_status():
        print(f"  [{row['state']:<7}] {row['id']:<14} ← {row['backing_doi']}  ({row['line']})")

    registry, certifier = build_platform()

    # LIVE module: Restoration (backed by published FNT).
    restoration = registry.get("restoration")
    inputs = {"sigma": 1.5, "delta_mu": 1.0}     # Θ = 1.5 > 1 → cluster (RED)
    cert = certifier.issue(restoration, subject="parcel-DEMO", inputs=inputs)
    print("\n== Self-rooted development certificate (Restoration / FNT) ==")
    print(json.dumps(cert.to_dict(), indent=2, default=str))
    ok = certifier.verify(cert, restoration, inputs)
    print(f"\nLocal recomputation:      {'VALID ✅' if ok else 'INVALID ❌'}")
    print(f"Tampered inputs verify:   {'VALID' if certifier.verify(cert, restoration, {**inputs, 'sigma': 0.1}) else 'INVALID ✅'}")

    # BLOCKED module: Mutualist (SRPT pending) — A-1 refuses.
    mutualist = registry.get("mutualist")
    try:
        certifier.issue(mutualist, subject="p", inputs={"rho": 1, "sigma": 1e-20, "sigma_tot": 2e-20, "r_c": -0.1})
        print("\nMutualist certified (unexpected!)")
    except CertifyBlocked:
        print("\nMutualist refused to certify ✅ — backing theorem (SRPT) not yet published (A-1).")


if __name__ == "__main__":
    main()
