# 36 — docs migration to levels (`docs/0…9`)

The pass that put every live fact into `docs/<N>_<NAME>.md` with provenance zones, returned the run
narrative to the records, and retired `docs/drawing/`, `STATUS.md` and `WORKSPACE.md`.

- `work/docs-migration-contract.md` — the plan: target tree, section allocation, writing rules, packages.
- `work/rename-map.md` — old path → new home, for a reader following an old link.
- `work/validate.sh` — the mechanical acceptance checks (no dates, zone order, `P1`–`P41`, no retired
  path, no second home for a P-number).
- `evidence/audit-completeness.md` — independent audit: what from the retired docs went missing or
  changed, and where it belonged.
- `evidence/audit-ssot-provenance.md` — independent audit: two homes, provenance upgrades, dead pointers.
- `evidence/verify-after-repair.md` — the verification of the repairs, and what the repairs broke.

The retired doc text is in git at the commit before the migration.
