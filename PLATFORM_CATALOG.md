# ViridisOS Platform Catalog

The modules the platform offers, each backed by a canon theorem. Assembled and resolved against
the **live canon** (`RESEARCH_PIPELINE_v2/canon_fingerprint_index.json`) — a module is LIVE only if
its backing DOI is a published, gate-passed theorem (invariant A-1). Regenerate with
`python3 viridis_platform.py`. Updated 2026-10-31.

| Module | Line | Backing theorem | DOI | State |
|---|---|---|---|---|
| **restoration** — nucleation planting design (critical cluster size n* + go/no-go) | Restoration | Forest Nucleation (FNT) | `20982979` | 🟢 LIVE |
| **afforestation** — seeding efficiency e = C/n* + the proven 8× edge-hostility lever | Restoration | Afforestation Stewardship (AST) | `21168224` | 🟢 LIVE |
| **harmonization** — single-price coordination toward a shared target | Governance / OS | Gaian Harmonization (GHT) | `21168212` | 🟢 LIVE |
| **mutualist** — natural-capital risk-premium pricing | Valuation & Finance | Symbiotic Risk-Premium (SRPT) | `21327066` | 🔴 BLOCKED |
| **carbon-continuity** — wildfire recovery threshold diagnostic | Risk & Insurance | Carbon Continuity After Wildfire (CCAW) | `21855690` | 🟢 LIVE |
| **seed-supply** — can nursery supply meet planting demand; which sites are short | Restoration | Seed-Source Bottleneck Certificate (SSBC, Run-130) | `21971057` | 🟡 PREVIEW |
| **precautionary-ceiling** — safe harvest/stocking ceiling from a mean and variance | Stewardship risk | Precautionary Capacity Reserve (PCR, Run-127) | `21971046` | 🟡 PREVIEW |

**Why Mutualist is BLOCKED:** SRPT is published (Zenodo 10.5281/zenodo.21327066, Canon record
`series-symbioticriskpremium`), but publication is not the gate. Canon lists the record as
`working` / `not-canon-admitted` with no hash-bound Comparator certificate, and the DOI is not in the
bundled canon index, so A-1 refuses to certify. The mathematics is also not yet a product warrant:
R1 and R3 take the Thermodynamic Uncertainty Relation as a hypothesis (Lean proves the premium floor
given the TUR bound, not that the bound holds for a natural-capital asset); R6 proves only that
P·D/(k_B T ln 2) is monotone, and reading it as a limit on hedging relies on the Intelligence Bound,
which is a conjecture; and the Canon function manifest labels `rho` as a correlation and `sigma` as
volatility, where the Lean statements use risk aversion and entropy production. Previews may run.
Unblocking needs Canon admission, a decision on the TUR premise and a corrected manifest, and remains
a research-pipeline / Justin-gated action.

**Carbon Continuity** is backed by Zenodo 10.5281/zenodo.21855690 and was re-certified on
2026-10-29 by the Viridis research engine (jdhart81/viridis-research, run `2026-10-29_P2`,
sealed statement `P2.CarbonContinuity`, PROVEN, not trivially closable, Lean v4.28.0 with pinned
Mathlib). It is the first module whose backing has been re-checked under the current pipeline.
PROVEN covers the threshold mathematics, not the coefficients or any field outcome. Restoration,
Afforestation and Harmonization are next in that re-certification queue (P2-T003 to P2-T005).

**Seed-Supply is PREVIEW:** its Lean proofs check (zero sorry, standard axioms; theorems
`seed_routing_common_fraction_eq_min_cut_ratio`, `seed_routing_feasible_iff_cut_conditions`,
`capacity_outside_active_bottleneck_irrelevant`), but the canon catalog lists the package as
`working`, not gate-passed, and DOI `21971057` is not in the bundled canon index. Previews run;
certification is refused (A-1) until the canon admits it. The module computes the largest common
fulfilment fraction the supply network can deliver, whether full demand is routable, the
bottleneck site set, and which nurseries cannot help. It makes no claim about seed viability,
field establishment, legality, cost or timing, and models no per-edge capacities.
**Precautionary Ceiling is PREVIEW:** its Lean proofs check (zero sorry, standard axioms;
theorems `capacityFloor_violation_prob_le`, `positive_floor_sharp_two_point_counterexample`,
`mean_only_plugin_arbitrarily_unsafe`), but the canon catalog lists the package as `working`, not
gate-passed, and DOI `21971046` is not in the bundled canon index. Previews run; certification is
refused (A-1) until the canon admits it. From the true mean and standard deviation of a
non-negative one-period capacity it returns d_α = [μ − σ√((1−α)/α)]₊, which is exceeded with
probability at most α under every such law, and no higher ceiling has that guarantee. A ceiling set
from the mean alone has no guarantee. Estimation error in μ and σ, dependence across periods,
and the choice of α are not covered. The canon's rate-model outputs are not exposed.

## What LIVE means

A LIVE module can issue a **certificate**: a signed, independently-recomputable claim whose backing
DOI resolves to a gate-passed canon theorem. See `demo.py` for the Restoration flow end to end
(issue → verify VALID; tampered inputs → INVALID).

## Product-line rollup (from the product tree)

- **Restoration line** (restoration + afforestation) → a Restoration/Afforestation SKU. Highest-ARR
  line in the product tree; ties directly to HDFM and drone-seeding operations.
- **Governance/OS line** (harmonization) → coordination-pricing module for the ViridisOS platform SKU.
- **Valuation & Finance** (mutualist) → the risk-pricing module; ships only after SRPT is Canon-admitted and its TUR premise is resolved.
- **Risk & Insurance** (carbon-continuity) → a model-scoped wildfire recovery diagnostic. The first
  commercial pilot is decision support only; it does not rate credits, set reserves, price cover, or
  make underwriting decisions.

## Adding the next module

Wrap the run's engine (`modules/<name>/engine.py`), subclass `Module` with its `Backing`
(`modules/<name>/module.py`), append one line to `catalog.py`, add `tests/test_*`. If the theorem is
published it goes LIVE automatically; if not, it's BLOCKED until it is. Candidates next: Tempo
(Run-060), MINT inference-network (DOI 21223160), IET exergy (DOI 21223218) — all with published DOIs
available to wire.
