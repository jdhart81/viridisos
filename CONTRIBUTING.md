# Contributing to ViridisOS

ViridisOS turns DOI-backed Viridis research into recomputable decision modules.
Start with a reproduction, module proposal, test, documentation repair, or
small adapter improvement. Read `GOVERNANCE.md`, `SECURITY.md`,
`CODE_OF_CONDUCT.md`, `TRADEMARK.md`, and `OPEN_SOURCE_MANIFEST.json` first.

## Module contract

Every proposed module must declare:

- an exact Zenodo DOI and Git commit for its backing research;
- the Lean module and Harmonic Aristotle receipt when it makes a formal claim;
- typed inputs, units, assumptions, missing-data behavior, and refusal rules;
- output uncertainty, limitations, and human-review triggers;
- deterministic kernel tests and a certify/verify test; and
- empirical status without implying that formal proof establishes field results.

A module remains `BLOCKED` until its backing DOI resolves through the Canon
index. Working Corpus publication does not automatically make a module
certification-ready; the adapter and validation gates remain separate.

## Pull requests

Keep one scientific or product change per pull request. Include exact test
commands and results. Disclose reused sources and material AI assistance; AI
systems are tools, not authors or accountable maintainers. Do not submit
credentials, private keys, customer data, protected mark assets, restricted
datasets, or proprietary settlement logic.

By submitting a contribution to the open payload, you license software under
Apache-2.0 and documentation under CC-BY-4.0 unless the file states otherwise.
You must have the right to make that contribution.
