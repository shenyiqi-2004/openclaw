# Memory Sidecar

`memory-sidecar` is the control, observability, and recovery layer for OpenClaw memory.

When `memory-lancedb-pro` is available, it is the canonical long-term memory backend. The sidecar does not compete with it.

## Architecture

### `memory-sidecar` owns

- `working.json`
- `summary.json`
- `strategy.json`
- `reflection.json`
- `selfcheck.json`
- `runtime.json`
- durable events and acks
- replay and recovery metadata
- signal-driven recall/store gating
- mode switching
- traces

### `memory-lancedb-pro` owns

- long-term recall
- long-term store / update / forget
- retrieval ranking
- scope isolation
- long-term lifecycle and decay

### Fallback

If `memory-lancedb-pro` is unavailable, sidecar falls back to `memory/knowledge/*.json` through `JsonSnapshotMemoryBackend`.

That fallback is for compatibility and testing only. It is not the preferred source of truth.

## Backend adapter

Sidecar resolves one of two backends:

- `LanceDbProMemoryBackend`
- `JsonSnapshotMemoryBackend`

Current long-term operations behind the adapter:

- `recall_memory(...)`
- `store_memory(...)`
- `update_memory(...)`
- `forget_memory(...)`
- `get_memory_stats(...)`

`LanceDbProMemoryBackend` uses the local OpenClaw bridge instead of re-implementing retrieval logic in Python.

## Root resolution

The canonical defaults are:

- runtime root: `/home/park/openclaw`
- memory root: `/home/park/openclaw/memory-sidecar`

Resolution order:

1. `OPENCLAW_EXTERNAL_MEMORY_ROOT`
2. `OPENCLAW_RUNTIME_ROOT + "/memory-sidecar"`
3. code default

Old paths such as `D:\openclaw` and `/mnt/d/openclaw` are deprecated only.

## Transaction flow

Each trigger follows this flow:

1. OpenClaw persists an event to `memory/events.jsonl`
2. recovery metadata is updated in `memory/recovery.json`
3. request-side code stops there; it does not run a full sidecar cycle inline
4. a sidecar worker later claims one queued event
5. sidecar processes one event
6. sidecar appends runtime and trace records
7. sidecar writes `memory/acks.jsonl`
8. sidecar writes `memory/commits.jsonl`

## Replay and recovery

Replayable events include:

- skipped events
- failed events
- zero-exit runs without ack

On the next worker opportunity, the oldest replayable event is claimed first.

Sidecar is idempotent by `event_id`:

- if `acks.jsonl` already contains the event, it exits as `duplicate_noop`
- if `runtime.json` already contains the event, it also exits as `duplicate_noop`

This prevents duplicate memory side effects.

## Signal-driven orchestration

Sidecar no longer relies on fixed `%3` and `%5` loops.

It derives signals such as:

- repeated steps
- contradiction
- consecutive failures
- rapid health drop
- interruption recovery
- low health
- high pressure or noise
- abnormal growth
- repeated low-yield recall

These signals drive:

- whether recall should happen
- why recall should happen
- whether reflection should run
- whether selfcheck should run
- whether local cleanup should run
- mode selection: `normal`, `stability`, `convergence`

## Trace format

Append-only traces are written to `memory/traces.jsonl`.

Important fields include:

- `event_id`
- `request_id`
- `source`
- `replayed`
- `replay_attempt`
- `recall_requested`
- `recall_reason`
- `recall_query`
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
- `runtime_step`
- `ack_id`
- `outcome`
- `failure_reason`

## Self-modification safety

Patch proposals can still be generated.

Automatic patch apply is off by default.

Patch apply only runs when explicitly enabled:

- `OPENCLAW_ENABLE_AUTO_PATCH=1`
- or `working.evolution_budget.auto_patch_enabled=true` and `auto_patch_disabled=false`

Proposal generation, apply attempts, and failures are written to `traces.jsonl`.

## Migration notes

From the older sidecar model:

- `memory/knowledge/*.json` is no longer the preferred long-term memory store
- fixed `top_k=3` and fixed `%3/%5` control loops are gone
- sidecar now acts as controller and trace surface
- `memory-lancedb-pro` is the preferred long-term engine
- event durability and replay are now part of the default runtime contract

## Files

Operational snapshots:

- `memory/working.json`
- `memory/summary.json`
- `memory/strategy.json`
- `memory/reflection.json`
- `memory/selfcheck.json`
- `memory/runtime.json`

Durable transaction files:

- `memory/events.jsonl`
- `memory/acks.jsonl`
- `memory/commits.jsonl`
- `memory/traces.jsonl`
- `memory/recovery.json`

## Worker CLI

Sidecar now exposes these entrypoints:

- `python3 main.py`
- `python3 main.py --once`
- `python3 main.py --worker`
- `python3 main.py --queue-status`
- `python3 main.py --print-root`
