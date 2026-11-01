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
from modules.seed_supply import SeedSupplyBottleneckModule
from modules.precautionary_ceiling import PrecautionaryCeilingModule
from modules.dscore_robustness import DScoreRobustnessModule
from modules.anytime_alarm import AnytimeAlarmModule
from modules.corridor_priority import CorridorPriorityModule
from modules.byproduct_exchange import ByproductExchangeModule

# module class + a note on backing status (informational; the resolver is the real gate)
CATALOG = [
    MutualistModule,       # SRPT (21327066) — published, not Canon-admitted; TUR premise → BLOCKED
    RestorationModule,     # FNT  (20982979) — published → LIVE
    AfforestationModule,   # AST  (21168224) — published → LIVE
    HarmonizationModule,   # GHT  (21168212) — published → LIVE
    CarbonContinuityModule,  # CCAW (21855690) — re-certified by the engine 2026-10-29 → LIVE
    SeedSupplyBottleneckModule,  # SSBC (21971057) — Lean zero-sorry; admitted to bundled index 2026-10-31 by Justin → LIVE
    PrecautionaryCeilingModule,  # PCR (21971046) — Lean zero-sorry; admitted to bundled index 2026-10-31 by Justin → LIVE
    DScoreRobustnessModule,  # DSWC (22236741) — Lean zero-sorry; admitted to bundled index 2026-10-31 by Justin → LIVE
    AnytimeAlarmModule,    # ACC  (21971041) — Lean zero-sorry; admitted to bundled index 2026-10-31 by Justin → LIVE
    CorridorPriorityModule,  # PCS (22665554) — Lean zero-sorry; admitted to bundled index 2026-10-31 by Justin → LIVE
    ByproductExchangeModule,  # RC (21971047) — Lean zero-sorry; admitted to bundled index 2026-10-31 by Justin → LIVE
]


def all_module_classes():
    return list(CATALOG)
