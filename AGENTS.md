# Agents and ViridisOS

This file is for two kinds of agent: one helping a person preview or verify a conservation module result, and a coding agent changing this repository, usually to add a module. The short machine-readable index is [llms.txt](llms.txt).

## Helping a person use ViridisOS

**What it does.** Each module wraps the numeric core of a Viridis Canon result. A preview returns the module's output; a certificate adds provenance (backing DOI, input hashes, timestamp) and can be recomputed by anyone with the same inputs.

**Paths to suggest.**

- See the whole flow: `python3 demo.py` runs catalog, certify and verify, and shows a blocked module being refused.
- Try a module: `python3 -m api.app`, then `GET /modules` and `POST /modules/{id}/preview` with inputs.
- Check a certificate: `POST /certificates/verify` with the certificate ID, module ID and the original inputs.

**Rules for agents.**

- Call `GET /modules` first and respect each module's state. Do not present a BLOCKED module's output as certifiable.
- A certificate from a local or development instance is self-rooted. Do not describe it as an official Viridis certificate or a certification mark.
- Relay a preview as a preview. Do not turn a Carbon Continuity preview into a credit quantity, rating or price.
- The backing Canon theorem is what a result rests on. Link its DOI when you relay a result.

## Working on this repository

- Run `bash run_all_tests.sh` before and after a change. Every invariant (A-1 to A-5) has a test that fails if it is violated; never weaken one to pass.
- New module: follow "Add a new module" in the [README](README.md): `modules/<name>/engine.py` with pure functions, `module.py` declaring its `Backing` DOI, registration, and `tests/test_<name>.py` covering the full certify and verify path.
- ViridisOS consumes Canon DOIs and never publishes to Canon (A-5).
- Keep the core pure Python stdlib. Do not add production trust-root keys, certification-mark authorization, settlement code or deployment assets; they are excluded by [OPEN_SOURCE_MANIFEST.json](OPEN_SOURCE_MANIFEST.json).
- New top-level files must be added to the manifest's `include` list to ship.
- Read [GOVERNANCE.md](GOVERNANCE.md) before changing what a result maps to. Outside contributions need a DCO sign-off.

## Related open projects

- [Viridis Canon](https://github.com/jdhart81/viridis-canon): the machine-checked results behind every module.
- [Viridis Agent Fleet](https://github.com/jdhart81/viridis-agent-fleet): deterministic, auditable MCP agents.
- [Viridis Conservation](https://viridisconservation.com/): the company that stewards these projects.
