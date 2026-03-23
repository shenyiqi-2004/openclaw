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

The sidecar remains a single-cycle Python kernel, but request-side code only emits durable events.

1. request-side runtime emits a durable event
2. worker claims one queued or replayable event
3. sidecar loads operational snapshots
4. sidecar loads event context if present
5. sidecar short-circuits duplicate events by `event_id`
6. sidecar detects backend availability
7. sidecar derives runtime signals from working state, runtime history, selfcheck state, and replay status
8. sidecar chooses mode: `normal`, `stability`, or `convergence`
9. sidecar decides whether recall is needed and why
10. sidecar calls the canonical backend when recall or store is allowed
11. sidecar runs one execution step
12. sidecar triggers reflection, selfcheck, and local cleanup from signals instead of fixed intervals
13. sidecar appends runtime, ack, commit, and trace records

## Hard rules

- Do not re-implement hybrid retrieval or reranking in sidecar when `memory-lancedb-pro` is active.
- Do not treat `memory/knowledge/*.json` as canonical long-term memory when the plugin backend is available.
- Keep sidecar small and explicit.
- Keep traces append-only.
- Keep event handling idempotent.
- Keep request-side code limited to durable emit; do not run full memory cycles inline.
- Automatic patch apply is off by default.
- Patch apply requires explicit enablement with `OPENCLAW_ENABLE_AUTO_PATCH=1` or `working.evolution_budget.auto_patch_enabled=true`.

## CLI modes

- `python3 main.py`: run one direct single-cycle execution
- `python3 main.py --once`: consume exactly one queued event
- `python3 main.py --worker`: poll and consume queued events
- `python3 main.py --queue-status`: print queue and root status
- `python3 main.py --print-root`: print the effective runtime and memory roots

## Local fallback

If `memory-lancedb-pro` is unavailable, sidecar falls back to local JSON snapshots:

- recall/store use `memory/knowledge/*.json`
- cleanup only applies to these local snapshots
- this fallback exists for compatibility and testing, not as the preferred architecture
