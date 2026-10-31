# ViridisOS Platform Catalog

The modules the platform offers, each backed by a canon theorem. Assembled and resolved against
the **live canon** (`RESEARCH_PIPELINE_v2/canon_fingerprint_index.json`) — a module is LIVE only if
its backing DOI is a published, gate-passed theorem (invariant A-1). Regenerate with
`python3 viridis_platform.py`. Updated 2026-08-04.

| Module | Line | Backing theorem | DOI | State |
|---|---|---|---|---|
| **restoration** — nucleation planting design (critical cluster size n* + go/no-go) | Restoration | Forest Nucleation (FNT) | `20982979` | 🟢 LIVE |
| **afforestation** — cubic optimal-seeding law + site-prep lever | Restoration | Afforestation Stewardship (AST) | `21168224` | 🟢 LIVE |
| **harmonization** — single-price coordination toward a shared target | Governance / OS | Gaian Harmonization (GHT) | `21168212` | 🟢 LIVE |
| **mutualist** — natural-capital risk-premium pricing | Valuation & Finance | Symbiotic Risk-Premium (SRPT) | pending | 🔴 BLOCKED |
| **carbon-continuity** — wildfire recovery threshold diagnostic | Risk & Insurance | Carbon Continuity After Wildfire (CCAW) | `21855690` | 🟢 LIVE |
| **byproduct-exchange** — two-way industrial-symbiosis reciprocity test | Circular economy | Reciprocity Corridor (RC, Run-128) | `21971047` | 🟡 PREVIEW |

**Why Mutualist is BLOCKED:** its theorem has formal evidence but is not yet published to the
canon, so its DOI does not resolve to a gate-passed entry. This is correct A-1 behavior: previews
may run, but the module cannot issue a certificate against an unpublished theorem. Publishing and
wiring a DOI remains a research-pipeline / Justin-gated action.

**Carbon Continuity** is backed by Zenodo 10.5281/zenodo.21855690 and was re-certified on
2026-10-29 by the Viridis research engine (jdhart81/viridis-research, run `2026-10-29_P2`,
sealed statement `P2.CarbonContinuity`, PROVEN, not trivially closable, Lean v4.28.0 with pinned
Mathlib). It is the first module whose backing has been re-checked under the current pipeline.
PROVEN covers the threshold mathematics, not the coefficients or any field outcome. Restoration,
Afforestation and Harmonization are next in that re-certification queue (P2-T003 to P2-T005).

**Byproduct Exchange is PREVIEW:** its Lean proofs check (zero sorry, standard axioms;
`bilateral_benefit_iff_reciprocity_corridor`, `strict_corridor_nonempty_iff_product_condition`,
`nash_midpoint_unique_maximizer`, `bandwidth_scaling_cannot_restore_feasibility`), but the canon
catalog lists the package as `working`, not gate-passed, and DOI `21971047` is not in the bundled
canon index. Previews run; certification is refused (A-1). For two partners that each send the
other a byproduct stream, with linear per-unit values and costs, it returns the flow-ratio corridor
c_x/v_x < y/x < v_y/c_y in which both gain, says whether any such exchange exists
(c_x·c_y < v_x·v_y, at any scale), and gives the unique symmetric Nash split. It is not a mass or
energy balance and uses no thermodynamic or Intelligence-Bound premise; one-way paid transfers,
more than two partners and multi-period dynamics are not covered.

## What LIVE means

A LIVE module can issue a **certificate**: a signed, independently-recomputable claim whose backing
DOI resolves to a gate-passed canon theorem. See `demo.py` for the Restoration flow end to end
(issue → verify VALID; tampered inputs → INVALID).

## Product-line rollup (from the product tree)

- **Restoration line** (restoration + afforestation) → a Restoration/Afforestation SKU. Highest-ARR
  line in the product tree; ties directly to HDFM and drone-seeding operations.
- **Governance/OS line** (harmonization) → coordination-pricing module for the ViridisOS platform SKU.
- **Valuation & Finance** (mutualist) → the risk-pricing module; ships when SRPT publishes.
- **Risk & Insurance** (carbon-continuity) → a model-scoped wildfire recovery diagnostic. The first
  commercial pilot is decision support only; it does not rate credits, set reserves, price cover, or
  make underwriting decisions.

## Adding the next module

Wrap the run's engine (`modules/<name>/engine.py`), subclass `Module` with its `Backing`
(`modules/<name>/module.py`), append one line to `catalog.py`, add `tests/test_*`. If the theorem is
published it goes LIVE automatically; if not, it's BLOCKED until it is. Candidates next: Tempo
(Run-060), MINT inference-network (DOI 21223160), IET exergy (DOI 21223218) — all with published DOIs
available to wire.
