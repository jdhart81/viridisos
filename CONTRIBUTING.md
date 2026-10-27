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

## Sign your commits (DCO)

Pull requests from forks require an author-matching `Signed-off-by` trailer on
each contribution commit.

    Signed-off-by: Your Name <you@example.com>

`git commit -s` adds it, and `git rebase --signoff origin/main` fixes an existing branch. Signing off
certifies the Developer Certificate of Origin 1.1 (https://developercertificate.org): you wrote the
change, or you have the right to submit it under this repository's license.

An unsigned merge that only incorporates upstream history is permitted when a
maintainer verifies that its tree exactly matches a conflict-free automatic merge
of its parents and all non-merge contribution commits satisfy this requirement.
Merge commits containing conflict resolutions or additional changes require an
author-matching sign-off.

CI currently checks non-merge commits only; a passing check does not replace this
merge review.

## License of contributions

Contributions are licensed under the same license as the files they change (see `LICENSE`), with no
additional terms. Don't submit work you can't license that way.

## Never commit

Credentials, API keys, private keys, `.env` files, customer or partner data, or wallet files. The secret
scan blocks known key formats. If you find a leaked secret, report it privately as described in
`SECURITY.md`.

## Names and marks

The license does not cover Viridis names, logos or certification marks. See `TRADEMARK.md`.
