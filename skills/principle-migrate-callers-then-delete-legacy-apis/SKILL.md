---
description: "Apply when introducing a new internal API while old callers still exist. Migrate callers and delete the old API in the same wave instead of preserving compatibility layers."
enabled: true
id: principle-migrate-callers-then-delete-legacy-apis
name: principle-migrate-callers-then-delete-legacy-apis
---

# Migrate Callers Then Delete Legacy APIs

- Update tests to assert the new contract, and delete tests that only protect pre-refactor implementation details

**When this applies:**

- The API lives inside a single deployable binary or process with no external compatibility guarantee
- The project can migrate every in-memory caller in one coordinated change

## When NOT to apply (persisted, wire, or rolling boundaries)

If a change alters a persisted database schema, storage format, message queue payload, cross-service RPC, or a rolling `N-1` and `N+1` deployment boundary, same-wave deletion breaks active callers and destroys rollback safety. Follow the `6-step Expand-Contract with reverse sync` protocol instead:

1. **Expand.** Add the new column, table, field, or endpoint additively alongside the legacy contract.
2. **Dual-write and backfill.** Write both old and new shapes and run a throttled, version-guarded backfill.
3. **Shadow dark-read parity.** Read both shapes in the background and verify zero unexplained mismatches.
4. **Progressive read cutover.** Shift live reads incrementally from the old shape to the new shape.
5. **Write cutover with reverse sync.** Switch primary writes to the new store while maintaining asynchronous reverse sync back to the old store during the bake window so rollback loses zero writes.
6. **Contract.** Stop reverse sync and remove legacy writers and schemas once the bake window finishes cleanly.
