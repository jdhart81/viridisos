# Canon to ViridisOS integration

`tools/sync_canon_kernels.py` verifies the digest of a pinned public Viridis
Canon catalog and writes `runtime/canon_kernel_registry.json`. The registry
contains every public Canon record and gives each one an explicit disposition.

A record becomes `KERNEL_CANDIDATE` only when Canon marks it both
`status=verified` and `integrity=gate-passed`. Ingestion never activates a
runtime module, creates a customer-facing decision-tree branch, or grants
certificate authority. A separately reviewed binding in
`runtime/canon_kernel_bindings.json` is required to name a module and decision
tree path. Missing bindings stay `BACKLOG_NO_WRAPPER`; working Canon records stay
`BACKLOG_CANON_ADMISSION_REQUIRED`; quarantined records remain quarantined.

The HTTP service exposes the read-only result at `GET /research-kernels`. Module
execution and certification continue to use their existing A-1 through A-5
gates.

To refresh from an exact Canon checkout:

```sh
python3 tools/sync_canon_kernels.py \
  --catalog /path/to/viridis-canon/docs/data/catalog.json \
  --canon-commit <full-40-character-commit>
```

Review the generated diff and any binding changes before release. Canon
publication and proof status do not establish empirical accuracy, ecological
outcomes, legal compliance, market acceptance, or commercial readiness.

## Auto-intake kernels (GET /auto-kernels)

Owner decision 2026-11-17: a statement the science engine proves that fits a Viridis
Conservation service is entered into the canon as a decision kernel and goes live automatically
once its checks pass (viridis-canon `docs/auto_intake/README.md`). After each canon merge the
engine runs

```
python3 tools/refresh_from_canon.py --canon <viridis-canon checkout at main>
```

which rewrites `runtime/canon_auto_kernels.json` from the canon's `os/research_statements.json`.
`GET /auto-kernels` serves that list: each kernel's status (LIVE, ENTERED, ROLLED_BACK), statement,
run, DOI, boundary, what is proven and what is assumed, and its one-step rollback. The tool refuses
to write a list that disagrees with the canon's live list (`os/core.json` and `os/admissions.json`),
and no kernel here carries certification authority. `tests/test_canon_auto_kernels.py` holds R1-R3.

The catalog registry above (`runtime/canon_kernel_registry.json`) is not refreshed by this step:
it is pinned to the 120-record catalog its bindings were reviewed against.
