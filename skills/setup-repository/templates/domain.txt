# Domain documentation

This repository uses one domain context.
Read `CONTEXT.md` for terms before discussing the model or planning work.
Read relevant records under `docs/adr/` when those records exist.

## File roles

- `README.md` owns the project goal and current milestone.
- `CONTEXT.md` is a glossary, without implementation choices or progress notes.
- `docs/target-contract.md` records target, data, and feature conventions.
- `docs/research/` holds dated evidence and investigations.
- `docs/adr/` holds architectural decision records for costly, surprising
  choices made between real alternatives.

Create decision records only when a decision warrants one.
If a glossary or decision record is absent, continue without a placeholder.
Use the glossary's terms consistently. Surface conflicts with existing
decision records before changing their assumptions.
