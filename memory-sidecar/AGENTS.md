# Memory Sidecar

`memory-sidecar` is a lightweight controller for OpenClaw memory operations.

It is not the canonical long-term memory engine when `memory-lancedb-pro` is available.

## Ownership

`memory-sidecar` owns:

- working, summary, strategy, reflection, selfcheck, and runtime snapshots
- event durability
- commit and ack bookkeeping
- replay and recovery
- signal-driven orchestration
- observability and traces

`memory-lancedb-pro` owns:

- long-term recall
- long-term store, update, and forget
- retrieval ranking and filtering
- scope isolation
- lifecycle and decay of long-term memory items

## Execution model

The sidecar remains a single-cycle Python kernel:

1. load operational snapshots
2. load event context if present
3. short-circuit duplicate events by `event_id`
4. detect backend availability
5. derive runtime signals from working state, runtime history, selfcheck state, and replay status
6. choose mode: `normal`, `stability`, or `convergence`
7. decide whether recall is needed and why
8. call the canonical backend when recall or store is allowed
9. run one execution step
10. trigger reflection, selfcheck, and local cleanup from signals instead of fixed intervals
11. append runtime and trace records
12. write ack for committed events

## Hard rules

- Do not re-implement hybrid retrieval or reranking in sidecar when `memory-lancedb-pro` is active.
- Do not treat `memory/knowledge/*.json` as canonical long-term memory when the plugin backend is available.
- Keep sidecar small and explicit.
- Keep traces append-only.
- Keep event handling idempotent.
- Automatic patch apply is off by default.
- Patch apply requires explicit enablement with `OPENCLAW_ENABLE_AUTO_PATCH=1` or `working.evolution_budget.auto_patch_enabled=true`.

## Local fallback

If `memory-lancedb-pro` is unavailable, sidecar falls back to local JSON snapshots:

- recall/store use `memory/knowledge/*.json`
- cleanup only applies to these local snapshots
- this fallback exists for compatibility and testing, not as the preferred architecture
