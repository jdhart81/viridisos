# ViridisOS Network-Effect Standard

**Standard ID:** VOS-NET-1  
**Effective:** 2026-08-01  
**Owner:** Justin D. Hart  
**Purpose:** make ViridisOS the open participation layer that converts the
verified Viridis Canon into a compounding builder, module, verification, and
conservation network.

## 1. Strategic position

Viridis Canon is the public truth and provenance layer. ViridisOS is the open
building platform above it. The Canon becomes more useful when outside builders
can turn exact verified results into recomputable modules; ViridisOS becomes
more defensible when every module points back to the Canon and produces new
tests, data needs, corrections, and research pull.

```text
verified Canon result
  -> open recompute kernel and module contract
  -> outside builder integrates or extends it
  -> independent verification or certified conservation output
  -> new data, objections, and research requirements
  -> stronger paper, theorem, and module
  -> more builders and trusted flow
```

This loop is the intended network effect. Repository traffic, stars, clones,
downloads, AI-generated modules, and Viridis's own integrations are leading
signals only. They are not outside adoption.

## 2. Open-core boundary

The binding commercial posture remains `protocol-open, toll-the-flow`:

- open: Canon proofs, module recompute kernels, certificate format and
  verification specification, reference runtime, SDK/examples, and free
  verification;
- protected/commercial: Viridis trust root, authoritative issuance, revocation,
  certification mark, enterprise SLA/surfaces, and settlement rails;
- non-negotiable: an outside party can inspect and recompute a claim without
  paying Viridis;
- non-negotiable: open code cannot impersonate the Viridis trust root or use the
  protected certification mark without authorization.

This standard does not change licenses, publish a repository, release a signing
key, grant mark rights, or authorize settlement terms.

## 3. Network maturity ladder

The machine tracker assigns the highest level with inspectable evidence.

| Level | State | Evidence required |
|---|---|---|
| V0 | `PRE_PUBLIC` | Local implementation exists, but no verified standalone public repository and release contract exist. |
| V1 | `PUBLIC_FOUNDATION` | Public repo, real open-source license, contribution/security/governance files, installable quickstart, green CI, and versioned release exist. |
| V2 | `BUILDER_ENGAGEMENT` | At least one identifiable outside contributor opens a substantive issue/PR, reproduces a module, or completes the quickstart. |
| V3 | `ECOSYSTEM_REUSE` | At least one accepted outside module/integration or attributable downstream package/deployment exists. |
| V4 | `INDEPENDENT_VERIFICATION` | An outside party independently recomputes or verifies a ViridisOS claim/certificate with a retained receipt. |
| V5 | `MULTISIDED_NETWORK` | Multiple outside builders and multiple issuers/users repeatedly exchange compatible modules or certificates. |
| V6 | `INSTITUTIONAL_STANDARD` | Repeat use by an outside registry, insurer, land trust, lab, agency, or standards body is evidenced. |

Missing evidence is not zero adoption; it is `NOT_RECORDED`. No level above V1
can be assigned from owner activity alone.

## 4. Metrics that govern

Track these separately:

### Foundation health

- public repository identity and visibility;
- license, contribution guide, code of conduct, security policy, governance,
  roadmap, install/packaging metadata, semantic version, CI, and releases;
- core and integration test receipts;
- documented stable module/API/MCP contracts.

### Builder participation

- identifiable non-owner contributors;
- external issues, PRs, reviews, and completed quickstarts;
- time-to-first-success and time-to-merge;
- repeat contributors and maintainer diversity.

### Ecosystem breadth

- total modules versus external modules;
- downstream integrations, packages, deployments, and fleet mounts;
- modules with published, gate-passed Canon backing;
- modules blocked by proof, paper, integrity, or public-release state.

### Trust and use

- independently verified certificates or recomputations;
- outside issuers, verifiers, subjects, and organizations;
- validation failures and revocations preserved in the record;
- certified conservation value and settled value, reported separately from
  platform revenue.

### Research pull

- outside data or method requests that alter the research queue;
- counterexamples, correction requests, new theorem targets, and real-data
  benchmark gaps originating from builders or users;
- modules that create a falsifiable flagship test.

## 5. Evidence registry

`NETWORK_EFFECT_EVIDENCE.json` is append-only evidence inventory. Each external
entry must identify actor/organization, source URL or local receipt, date,
artifact/module, evidence class, and whether the actor is independent of
Viridis. Self-generated activity must be marked `internal`.

The following never self-promote:

- a fork without inspectable outside work;
- a bot or mirrored commit;
- a download or anonymous clone;
- a certificate issued and verified only by Viridis;
- an integration copied by Viridis into another Viridis-owned repository;
- unsigned pipeline, hypothetical ARR, or unsettled transaction value.

## 6. Public-release gate

Before calling ViridisOS open source, all of these must exist in the exact
release repository:

1. Justin-selected repository identity and explicit publication authorization;
2. license files matching the layer map;
3. no private key, credential, customer data, proprietary settlement logic, or
   protected mark asset in the public payload;
4. contribution guide, code of conduct, security policy, governance, roadmap,
   support boundary, and trademark/mark policy;
5. deterministic install and under-ten-minute quickstart;
6. green core, integration, packaging, adapter, and clean-clone tests;
7. stable public APIs and a compatibility/versioning policy;
8. seed issues labelled for outside builders and one minimal module template;
9. exact Canon-index configuration for local, package, container, and fleet
   contexts;
10. a signed release receipt identifying files, hashes, tag, CI, public URL, and
    rollback plan.

Repository creation, visibility changes, release/tag publication, package
publication, mark licensing, trust-root operations, outreach, and account
changes require Justin's exact authorization.

## 7. Weekly control loop

The Monday research evidence loop must:

1. rebuild `VIRIDISOS_NETWORK_STATE.json` from local state and live public
   GitHub evidence;
2. fail closed on source errors;
3. record module READY/BLOCKED state against the current Canon;
4. ingest only named evidence from `NETWORK_EFFECT_EVIDENCE.json`;
5. report the maturity level, first blocker, and one best participation action
   into the existing Morning Business Check-In;
6. never create a separate vanity dashboard or call traffic adoption.

## 8. Current honest baseline

As of 2026-08-01, ViridisOS has a working local reference runtime,
certification layer, four modules, API/MCP surfaces, and green local tests. The
connected GitHub inventory contains a private `jdhart81/viridis-platform`
repository but no verified standalone public ViridisOS repository. The local
ViridisOS root also lacks the release-level license, contribution, security,
governance, packaging, and public CI files required by this gate.

Therefore the current network state is **V0 `PRE_PUBLIC`**. The architecture is
open-core by policy; the platform is not yet honestly claimable as a public
open-source network.

