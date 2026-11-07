// Corridor check with HDFM's dfm-core: does a treatment plan break a link between core areas?
// Usage: node check-corridor.mjs [path/to/landscape-package.json]
// Default input is the VergeCommon plan package fixture that ships with dfm-core.
// Structural connectivity only. It does not establish species movement, genetic viability,
// regulatory compliance or old-growth condition.
import { readFileSync } from 'node:fs';
import { resolve } from 'node:path';

const root = process.env.HDFM_DIR ?? 'hdfm-framework';
const core = await import(resolve(root, 'packages/dfm-core/src/index.mjs'));
const input = process.argv[2] ?? resolve(root, 'packages/dfm-core/fixtures/vergecommon-plan-package.json');
const raw = JSON.parse(readFileSync(input, 'utf8'));
const pkg = raw.package ?? raw; // fixture wraps the package; a plain Landscape Package works too

const r = core.checkConnectivitySync(core.fromLandscapePackage(pkg));
console.log(JSON.stringify({
  status: r.status,                      // pass | fail | incomplete
  lostLinks: r.lostLinks ?? [],          // each names the unit(s) that alone break it
  pinchedLinks: r.pinchedLinks ?? [],
  warnings: r.warnings ?? [],
  reasons: r.reasons ?? [],
  engine: r.engineVersion ?? r.engine,
}, null, 2));
