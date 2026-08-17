# ViridisOS governance

ViridisOS is an open reference runtime with a protected production trust root.
Contributors can build, reproduce, and verify modules without permission. Open
source does not grant authority to issue Viridis-rooted certificates, use the
protected certification mark, publish research, change the Canon spine, or
operate settlement rails.

## Roles and decisions

- Contributors propose modules, tests, integrations, documentation, and field
  validation.
- Maintainers review code, provenance, safety boundaries, and compatibility.
- The Viridis Research Curator verifies DOI/Canon routing and proof receipts.
- Justin D. Hart authorizes exact public releases, production trust-root and
  mark operations, settlement terms, and production deployment.

Routine changes merge through reviewed pull requests. Security holds may be
immediate. Material governance or compatibility changes receive at least seven
days of public review when practicable.

## Versioning and compatibility

ViridisOS uses semantic versioning. Patch releases preserve public behavior;
minor releases add backward-compatible modules or APIs; major releases may
break declared interfaces. A module must pin its DOI and version. Deprecated
interfaces remain for at least one minor release unless they create a security
or evidence-integrity risk.

## Evidence boundary

Formal verification supports the modeled mathematical claim under declared
assumptions. It does not establish empirical accuracy, ecological outcomes,
legal compliance, market acceptance, safety, demand, or profitability. Those
receipts are reviewed independently.
