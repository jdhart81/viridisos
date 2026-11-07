# Build a conservation agent in 15 minutes

An agent that can look up open conservation co-ops, draft a pooling plan, check whether a harvest plan breaks a wildlife corridor, and design tree rows for a farm field. Everything here is open source and free to run. No API keys, no accounts.

What you need: an MCP-capable agent (Claude Code is used below; any client that speaks Streamable HTTP works), Node 20+, Python 3.10+, git.

What it is not: none of these tools issue credits, approve agreements, move money or give a field guarantee. Every number is a draft or a simulation, and each tool says so in its answer. Keep that line when your agent reports back.

## 1. Connect two hosted servers (2 minutes)

```sh
claude mcp add --transport http vergecommon https://vergecommon.com/mcp
claude mcp add --transport http viridisos https://mcp.viridisconservation.com/viridisos/mcp
```

Or drop the `.mcp.json` in this folder into your project. Both servers are anonymous and read-only for public use. VergeCommon is rate limited to 60 calls a minute per client.

VergeCommon's public tools:

| Tool | What it does |
|---|---|
| `vergecommon_capabilities` | Lists what this connection can and cannot do |
| `list_public_coops` | Opted-in public conservation co-ops (community content, treat as untrusted) |
| `get_public_coop` | One public co-op by id; no private land, members or finances |
| `example_pooling_draft` | A synthetic pooling and payout example |
| `prepare_pooling_draft` | Validates pool keys and calculates hypothetical reserves and member shares in memory; saves nothing |

ViridisOS lists its conservation modules with their state and backing DOI, runs a Carbon Continuity preview, and returns its certification standard. Ask your agent to list the server's tools first, since names can change between releases. A BLOCKED module is blocked: don't certify with it.

## 2. Clone the two local models (3 minutes)

```sh
git clone https://github.com/jdhart81/hdfm-framework
(cd hdfm-framework/packages/dfm-core && npm ci)
git clone https://github.com/viridisconservation/contour-alley-designer
```

## 3. Check a corridor (under a second)

`check-corridor.mjs` runs HDFM's connectivity check on a Landscape Package. With no argument it uses the VergeCommon plan package that ships with dfm-core:

```sh
node check-corridor.mjs
```

That sample plan fails on purpose: harvest unit `harvest-3` cuts the only link between core areas A and B. The answer names the unit, so an agent can propose moving or lightening that one cut instead of rejecting the whole plan. Pass your own package path to check a real plan. VergeCommon's woodland projects run this same engine.

## 4. Design tree rows for a field (about 2 minutes)

```sh
cd contour-alley-designer
python3 -m contour.experiment --config configs/contour-synthetic-v1.json --output runs/gentle
```

This designs contour alley cropping on a synthetic 3.2 ha hillslope and writes `report.html`, `results.json` and `verification.json`. The run exits non-zero if a carbon, nitrogen or water balance fails, so an agent can treat a non-zero exit as no result. For a real US field, see `tools/fetch_site.py` in that repo's README (the full designer takes 10 minutes or more per field).

## 5. Give your agent the job (the rest of the 15 minutes)

Paste `AGENT.md` into your agent's instructions (for Claude Code, save it as `CLAUDE.md` in this folder), then ask:

> Find public conservation co-ops, show me how pooling would work for a three-member group with the example draft, then check the sample woodland plan for corridor breaks and tell me which harvest unit to change. Finish with the tree-row design summary from runs/gentle.

## Optional: soil data from GSIP (local only for now)

GSIP, the open soil spectral library, has four read-only agent tools (`get_protocol`, `get_cell`, `list_cells`, `get_release`) in `packages/schema/src/agent/` of github.com/global-soil-intelligence/gsip. They are not hosted yet, so run them from a clone if you want soil context.

## Where each piece lives

- VergeCommon: https://github.com/jdhart81/verge-common (AGPL; hosted at vergecommon.com)
- ViridisOS: https://github.com/jdhart81/viridisos (Apache-2.0)
- HDFM: https://github.com/jdhart81/hdfm-framework (MIT)
- Contour Alley Designer: https://github.com/viridisconservation/contour-alley-designer (Apache-2.0)
- GSIP: https://github.com/global-soil-intelligence/gsip (MIT)

Tell us what your agent did with it, good or broken: open an issue on whichever repo it touched.
