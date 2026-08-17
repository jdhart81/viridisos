"""ViridisOS module catalog — the single source of what the platform offers.

Each entry ties a module class to its product line and backing theorem. Mirrors the
research-arm product tree: modules whose backing theorem is published in the canon go
LIVE; modules whose theorem is still pending are correctly BLOCKED (A-1). Adding a new
module = wrapping its run engine and appending one line here.
"""

from __future__ import annotations

from modules.mutualist import MutualistModule
from modules.restoration import RestorationModule
from modules.afforestation import AfforestationModule
from modules.harmonization import HarmonizationModule
from modules.carbon_continuity import CarbonContinuityModule

# module class + a note on backing status (informational; the resolver is the real gate)
CATALOG = [
    MutualistModule,       # SRPT (Run-093) — pending publication → BLOCKED until DOI minted
    RestorationModule,     # FNT  (20982979) — published → LIVE
    AfforestationModule,   # AST  (21168224) — published → LIVE
    HarmonizationModule,   # GHT  (21168212) — published → LIVE
    CarbonContinuityModule,  # CCAW (2026-08-04) — Saturday/canon hold → BLOCKED
]


def all_module_classes():
    return list(CATALOG)
