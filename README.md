# ViridisOS

[![CI](https://github.com/jdhart81/viridisos/actions/workflows/ci.yml/badge.svg)](https://github.com/jdhart81/viridisos/actions/workflows/ci.yml) [![License: Apache-2.0](https://img.shields.io/badge/license-Apache--2.0-blue.svg)](LICENSE) [![OpenSSF Scorecard](https://api.scorecard.dev/projects/github.com/jdhart81/viridisos/badge)](https://scorecard.dev/viewer/?uri=github.com/jdhart81/viridisos)

Viridis Canon is the verified truth and provenance layer. ViridisOS is the
participation layer that lets builders turn those Lean-verified results into
recomputable conservation modules and certificates. This is the intended
cornerstone network loop: more verified research creates more useful modules;
outside use, verification, and objections create new research pull.

This directory contains the working reference service: module runtime (L2) +
certification layer (L3) + reference modules + HTTP and MCP surfaces. It is pure
Python stdlib at the core. `GOVERNANCE.md` defines the research-to-product and
authority boundaries; every published result must be mapped to an existing
module, a new module, or an explicit backlog disposition.

Important boundary: repository status comes from the live network-state receipt,
not this source tree. A local candidate remains V0 `PRE_PUBLIC`; it becomes V1
`PUBLIC_FOUNDATION` only after the exact standalone repository and release are
authorized, publicly readable, and independently re-cloned and tested.

## Status, AI use and citation

Reference software, not peer reviewed. Modules carry `empirical_validation: NOT_VALIDATED`
from the canon; a certificate here checks a computation against its DOI-backed Lean result, not
an ecological outcome. Much of the code was written with AI coding assistants (mainly Claude by
Anthropic, some OpenAI Codex), as the commit history shows; Justin D. Hart (Viridis LLC, ORCID
[0009-0008-3082-2482](https://orcid.org/0009-0008-3082-2482)) reviews changes and is the accountable
author. Code is Apache-2.0 ([LICENSE](LICENSE)); documentation terms are in
[DOCUMENTATION_LICENSE.md](DOCUMENTATION_LICENSE.md). Cite with [CITATION.cff](CITATION.cff). This
repository has no Zenodo record yet.

## Run

```bash
bash run_all_tests.sh        # run from a source checkout
python3 -m pip install -e .  # install the open reference package locally
viridisos-demo               # run the DOI-gated demonstration
python3 viridis_platform.py  # print the module catalog resolved against the live canon
python3 demo.py              # end-to-end: catalog → certify (live FNT) → verify; blocked module refused
python3 -m api.app           # serve the HTTP API on :8085
```

The installable payload is defined by `OPEN_SOURCE_MANIFEST.json`. It excludes
production trust-root keys and issuance, certification-mark authorization,
settlement/toll code, customer systems, and deployment assets. Development
certificates are self-rooted and are not authoritative Viridis certificates.

## Modules (see PLATFORM_CATALOG.md)

Five modules, each backed by a canon theorem. Resolved against the live canon — LIVE only if the
backing theorem is published (A-1): **restoration** (FNT) · **afforestation** (AST) · **harmonization**
(GHT) and **carbon-continuity** (CCAW) are LIVE; **mutualist** (SRPT) is BLOCKED until its paper
publishes. Carbon Continuity is the first module re-certified by the current research engine
(2026-10-29, statement `P2.CarbonContinuity`, PROVEN for the mathematics only). Its outputs do not
produce credit quantities, project ratings, insurance prices, or underwriting decisions.

## What's here

```
runtime/         L2 — module contract (module.py), registry, provenance, canon resolver
certification/   L3 — claim, attestation (dev signer), certifier (issue+verify), registry, standard
modules/mutualist/  reference module wrapping the SRPT (Run-093) kernel
modules/carbon_continuity/  wildfire recovery threshold diagnostic (re-certified 2026-10-29)
api/             L4 seam — service + pure dispatch + stdlib HTTP wrapper
tests/           core tests; every invariant has a failing-if-violated test
demo.py          full-flow demonstration
```

## Part of the Viridis open commons

ViridisOS is one of five open projects that build on each other. Each one is useful alone; together they carry a piece of land from a map to a verified result.

| Project | What it does | Where |
| --- | --- | --- |
| Dendritic Forest Management (DFM) | Starts from existing roads and waterways and checks whether retained forest stays connected as harvests are planned. MIT. | [hdfm-framework](https://github.com/jdhart81/hdfm-framework) · [dendriticforest.com](https://dendriticforest.com) |
| VergeCommon | Lets neighbours run a local conservation co-op: private mapping, parcel-by-parcel consent, evidence and shared decisions. Runs DFM inside its woodland projects. AGPL-3.0. | [verge-common](https://github.com/jdhart81/verge-common) · [vergecommon.com](https://vergecommon.com) |
| Global Soil Intelligence Project (GSIP) | Builds an open soil spectral reference library, with phone and web capture. MIT code, ODbL data. | [gsip](https://github.com/global-soil-intelligence/gsip) |
| ViridisOS | Turns verified results into recomputable conservation modules and certificates anyone can check. Apache-2.0. | [viridisos](https://github.com/jdhart81/viridisos) |
| Viridis Research | The public, machine-checked research record behind the methods. CC BY 4.0. | [viridis-research](https://github.com/jdhart81/viridis-research) |

How they connect: DFM finds where a corridor runs. The corridor almost always crosses property lines, so VergeCommon gives the neighbours along it a private place to organize and consent. GSIP adds soil evidence from the same ground. ViridisOS lets anyone recompute what was claimed, and Viridis Research holds the proofs those checks rest on. Viridis Conservation ([viridisconservation.com](https://viridisconservation.com)) offers paid data preparation, assessments and support for teams that want help.

Built something with one of these? Add the badge and tell us in an issue, so we can link back:

```markdown
[![Part of the Viridis open commons](https://img.shields.io/badge/Viridis-open%20commons-2e7d32)](https://github.com/jdhart81/hdfm-framework#part-of-the-viridis-open-commons)
```

## Network-effect tracking

- `VIRIDISOS_NETWORK_EFFECT_STANDARD.md` defines the V0–V6 evidence ladder and
  the public-release gate.
- `NETWORK_EFFECT_REGISTRY.json` defines expected public repositories and
  required release files.
- `NETWORK_EFFECT_EVIDENCE.json` stores only named, inspectable outside-builder,
  reuse, verification, institutional-use, research-pull, and settled-flow
  evidence.
- `build_network_state.py` writes the current JSON/Markdown state and a dated
  snapshot. It reads public GitHub state only when `--live` is supplied and
  never mutates an external surface.

Traffic, stars, downloads, owner activity, Viridis-authored integrations, and
self-issued certificates are distribution or internal-product evidence. They
do not count as outside adoption.

## The invariants it enforces

- **A-1 Backing-or-nothing** — no certificate without a resolvable, gate-passed canon DOI.
- **A-2 Recompute-verifiable** — every certificate is independently, bit-identically recomputable.
- **A-3 Blocked propagation** — unverified / integrity-flagged backing ⇒ module BLOCKED, cannot certify.
- **A-4 Provenance everywhere** — every output carries backing DOI + input hashes + timestamp.
- **A-5 Never publish to canon** — ViridisOS only consumes canon DOIs.

## Add a new module (the whole point — under an hour)

1. Create `modules/<name>/engine.py` — port the research run's `verify.py` numeric core as pure functions.
2. Create `modules/<name>/module.py` — subclass `runtime.module.Module`, set `id/name/line/version`,
   declare `backing = Backing(doi=..., lean_module=..., aristotle_id=..., verified=True)`, implement
   `compute(inputs)`.
3. Register it (`registry.register(...)`) and add a `tests/test_<name>.py` (kernel checks +
   full certify→verify path).

That's it — the runtime handles provenance, the certifier handles the moat, the API exposes it.
Next modules by product-tree priority: **Tempo** (Run-060), **Restoration/Nucleation** (Run-061).

## Part of the Viridis open-source commons

The mathematics behind each module lives in [Viridis Canon](https://github.com/jdhart81/viridis-canon), and [ProofLens](https://github.com/jdhart81/prooflens) explains what a Lean statement says before you read the proof.

This project is one of a connected set of open tools from Viridis. Each stands on its own; together they run from field evidence to checked decisions.

**Conservation commons**

- [VergeCommon](https://github.com/jdhart81/verge-common): community conservation co-ops with consent-based land mapping, field evidence and group decisions
- [Dendritic Forest Management (DFM)](https://github.com/jdhart81/hdfm-framework): compare forest-retention options around roads and waterways, with traceable inputs and portable reports
- [Global Soil Intelligence Project (GSIP)](https://github.com/global-soil-intelligence/gsip): contribute soil observations and explore open soil maps with explicit uncertainty

**Verifiable science**

- [Viridis Canon](https://github.com/jdhart81/viridis-canon): machine-checked Lean 4 mathematics for ecological decisions, with a DOI for every result
- **ViridisOS** (this repository): open reference runtime for DOI-backed decision modules and recomputable results
- [Viridis Research](https://github.com/jdhart81/viridis-research): the nightly public research record, each claim labeled by what a verifier actually checked
- [ProofLens](https://github.com/jdhart81/prooflens): see what a Lean statement means before reading the proof

**Agent tools**

- [Viridis Agent Fleet](https://github.com/jdhart81/viridis-agent-fleet): open-source MCP agents with deterministic, auditable cores
- [EnergyAI MCP](https://github.com/jdhart81/energyai-mcp): energy-planning estimates and incentive sources for AI agents

Browse every project on the [Viridis profile](https://github.com/jdhart81). If this one is useful to you, a star helps other people find it.

## API

| Method | Route | Body | Returns |
|---|---|---|---|
| GET | `/modules` | — | registered modules + state |
| POST | `/modules/{id}/preview` | `{inputs}` | module output (no certificate) |
| POST | `/modules/{id}/certify` | `{subject, inputs}` | issued certificate (409 if BLOCKED) |
| POST | `/certificates/verify` | `{certificate_id, module_id, inputs}` | `{valid}` |
| GET | `/standard` | — | Certification Standard v1 |
