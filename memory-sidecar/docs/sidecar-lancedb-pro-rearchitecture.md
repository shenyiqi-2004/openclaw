# Memory Sidecar + LanceDB-Pro Architecture

Status: implemented baseline on 2026-03-20

## Summary

The sidecar has been repositioned from a small standalone memory system into a controller around `memory-lancedb-pro`.

Target split:

- `memory-sidecar`: controller, observability, recovery, operational snapshots
- `memory-lancedb-pro`: canonical long-term memory engine

This keeps the repo small and readable while removing duplicated long-term retrieval logic from the sidecar path.

## Validation status

Validated on 2026-03-20 with both unit tests and a real launcher-driven smoke test.

Completed checks:

- Python unit tests for backends, events, orchestration, selfcheck safety, and trace contract
- TypeScript launcher tests for skip, replay, and ack-missing handling
- `py_compile` on the Python sidecar modules
- direct `python3 main.py` execution
- real `external-memory-kernel.ts` launch against the actual sidecar root

Observed runtime results from the real smoke test:

- launcher wrote durable events, traces, acks, and commits
- committed runs advanced `runtime.json`
- replayed runs were marked with `replayed = true`
- the latest runtime record used:
  - `memory_backend = "memory_lancedb_pro"`
  - `memory_backend_mode = "bridge"`
  - `memory_backend_canonical = true`
  - `partition = "backend-managed"`
- signal-driven reasons appeared in runtime and trace output, including interruption recovery

Validation caveat:

- the launcher still processes one runnable event per trigger cycle by design
- this preserves the lightweight child-process model and may leave newer events in `pending` until the next trigger opportunity

## Ownership boundary

### Sidecar owns

- `working.json`
- `summary.json`
- `strategy.json`
- `reflection.json`
- `selfcheck.json`
- `runtime.json`
- event journal
- acks and commits
- replay and recovery
- signal-driven orchestration
- trace generation

### `memory-lancedb-pro` owns

- long-term recall
- long-term store / update / forget
- hybrid retrieval
- reranking
- scope isolation
- long-term lifecycle and decay

### Local JSON fallback

`memory/knowledge/*.json` still exists, but only as:

- fallback backend
- compatibility path
- test fixture storage

It is not the canonical long-term source when `memory-lancedb-pro` is available.

## Adapter layer

Sidecar now resolves a backend through a small adapter layer:

- `LanceDbProMemoryBackend`
- `JsonSnapshotMemoryBackend`

Operations exposed through the adapter:

- `recall_memory`
- `store_memory`
- `update_memory`
- `forget_memory`
- `get_memory_stats`

Preferred path:

1. detect active `memory-lancedb-pro`
2. use the local bridge
3. fall back to JSON snapshots only if the plugin backend is unavailable

## Durable transaction model

OpenClaw launcher now persists events before any spawn attempt.

Files:

- `memory/events.jsonl`
- `memory/acks.jsonl`
- `memory/commits.jsonl`
- `memory/traces.jsonl`
- `memory/recovery.json`

Event states:

- `pending`
- `processing`
- `committed`
- `failed`
- `skipped`

Rules:

- skipped triggers are retained
- failed triggers are replayable
- zero-exit without ack is treated as failed
- a committed `event_id` is idempotent on replay

## Replay flow

1. launcher writes event
2. launcher tries to run the oldest replayable event first
3. sidecar receives `OPENCLAW_MEMORY_EVENT_ID`
4. sidecar checks `acks.jsonl` and `runtime.json`
5. duplicate event becomes `duplicate_noop`
6. successful event writes ack
7. launcher observes ack and marks commit

## Signal-driven orchestration

Rigid rules such as:

- choose one partition
- fixed `top_k=3`
- reflect every 3 steps
- selfcheck every 5 steps

have been replaced by signal-driven control.

Signals include:

- repeated steps
- contradiction
- consecutive failures
- rapid health drop
- interruption recovery
- low health
- high pressure
- high noise
- abnormal growth
- low-yield recall

These signals drive:

- recall timing
- recall reason
- recall depth
- reflection
- selfcheck
- local cleanup
- mode switching: `normal`, `stability`, `convergence`

## Trace contract

Every run appends machine-readable records to `memory/traces.jsonl`.

Important orchestration fields:

- `event_id`
- `trigger_source`
- `replayed`
- `recall_requested`
- `recall_reason`
- `recall_query`
- `recall_limit`
- `returned_memory_count`
- `selected_memory_ids`
- `discarded_results`
- `health`
- `pressure`
- `noise`
- `complexity`
- `current_mode`
- `selected_strategy`
- `reflection_triggered`
- `selfcheck_triggered`
- `cleanup_triggered`
- `memory_write_allowed`
- `patch_proposal_generated`
- `patch_apply_enabled`
- `patch_apply_attempted`
- `patch_applied`
- `patch_failure_reason`
- `outcome`
- `failure_reason`

## Self-modification safety

Patch proposals remain available.

Patch apply is not automatic anymore.

Default policy:

- proposal generation: allowed
- patch apply: disabled

Patch apply requires explicit opt-in:

- `OPENCLAW_ENABLE_AUTO_PATCH=1`
- or `working.evolution_budget.auto_patch_enabled=true` with `auto_patch_disabled=false`

Proposal generation, apply attempts, and failures are traced explicitly.

## Tradeoffs

Chosen tradeoffs:

- keep the single-cycle child-process model
- keep JSON snapshots for operations and debugging
- use a thin bridge instead of rebuilding plugin behavior in Python
- keep local JSON fallback for compatibility

Not chosen:

- giant daemon
- second long-term memory engine
- duplicated rerank or decay logic
- automatic self-modification by default

## Deferred items

Intentionally not done in this baseline:

- richer memory result attribution from inside `memory-lancedb-pro`
- backend-native discard reasons beyond what the bridge returns
- deeper end-to-end replay prioritization policies
- broader patch allowlist
- dashboard or UI layer over traces
