# ViridisOS Platform Catalog

The modules the platform offers, each backed by a canon theorem. Assembled and resolved against
the **live canon** (`RESEARCH_PIPELINE_v2/canon_fingerprint_index.json`) — a module is LIVE only if
its backing DOI is a published, gate-passed theorem (invariant A-1). Regenerate with
`python3 viridis_platform.py`. Updated 2026-08-04.

| Module | Line | Backing theorem | DOI | State |
|---|---|---|---|---|
| **restoration** — nucleation planting design (Θ go/no-go + n*) | Restoration | Forest Nucleation (FNT) | `20982979` | 🟢 LIVE |
| **afforestation** — cubic optimal-seeding law + site-prep lever | Restoration | Afforestation Stewardship (AST) | `21168224` | 🟢 LIVE |
| **harmonization** — thermodynamic shadow-price coordination | Governance / OS | Gaian Harmonization (GHT) | `21168212` | 🟢 LIVE |
| **mutualist** — natural-capital risk-premium pricing | Valuation & Finance | Symbiotic Risk-Premium (SRPT) | pending | 🔴 BLOCKED |
| **carbon-continuity** — wildfire recovery threshold diagnostic | Risk & Insurance | Carbon Continuity After Wildfire (CCAW) | pending | 🔴 PREVIEW / BLOCKED |

**Why Mutualist and Carbon Continuity are BLOCKED:** each theorem has formal evidence but is not yet
published to the canon, so its DOI does not resolve to a gate-passed entry. This is correct A-1
behavior: previews may run, but neither module can issue a certificate against an unpublished
theorem. Publishing and wiring a DOI remains a research-pipeline / Justin-gated action.

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
