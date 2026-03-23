# OpenClaw Runtime Architecture v2

## 1. System Overview
- OpenClaw is a WSL-hosted runtime system for gateway request handling, agent execution, auto-reply dispatch, and externalized memory control.
- The system is not a standalone memory service. It is a combined runtime, agent system, and memory-control system.
- The gateway handles request-time work.
- Auto-reply and agent execution handle turn-time work.
- `memory-sidecar` handles post-request control, replay, and observability for external memory.
- `memory-lancedb-pro` is the canonical long-term memory engine.
- The runtime is event-driven at the memory boundary. Request handlers emit durable memory events instead of running the full sidecar cycle inline.

---

## 2. Canonical Facts
- Canonical runtime root:
  - `/home/park/openclaw`
- Canonical memory root:
  - `/home/park/openclaw/memory-sidecar`
- Canonical long-term memory engine:
  - `memory-lancedb-pro`
- Source of truth:
  - Current code under `/home/park/openclaw`
  - Runtime config under `/home/park/openclaw/.openclaw/openclaw.json`
  - If code and documents conflict, code wins
- Deprecated paths:
  - `/mnt/d/openclaw`
  - `D:\openclaw`
  - These remain only as compatibility markers in root resolvers and documentation

---

## 3. Global Architecture Layers

### CLI Layer
- Responsibility:
  - normalize process startup
  - parse CLI profile and command routing
  - dispatch core commands
- Key files:
  - [openclaw.mjs](/home/park/openclaw/openclaw.mjs)
  - [src/entry.ts](/home/park/openclaw/src/entry.ts)
  - [src/cli/run-main.ts](/home/park/openclaw/src/cli/run-main.ts)
- Input:
  - process argv and env
- Output:
  - command execution or gateway startup

### Gateway Layer
- Responsibility:
  - run the gateway server
  - accept RPC and chat requests
  - dispatch server methods
- Key files:
  - [src/cli/gateway-cli/run.ts](/home/park/openclaw/src/cli/gateway-cli/run.ts)
  - [src/cli/gateway-cli/run-loop.ts](/home/park/openclaw/src/cli/gateway-cli/run-loop.ts)
  - [src/gateway/server.impl.ts](/home/park/openclaw/src/gateway/server.impl.ts)
  - [src/gateway/server-methods.ts](/home/park/openclaw/src/gateway/server-methods.ts)
- Input:
  - CLI startup
  - gateway requests
- Output:
  - request dispatch
  - gateway responses

### Agent / Auto-reply Layer
- Responsibility:
  - dispatch inbound messages
  - run reply-agent turns
  - manage followup and payload assembly
- Key files:
  - [src/auto-reply/dispatch.ts](/home/park/openclaw/src/auto-reply/dispatch.ts)
  - [src/auto-reply/reply/agent-runner.ts](/home/park/openclaw/src/auto-reply/reply/agent-runner.ts)
- Input:
  - gateway chat and agent requests
- Output:
  - replies
  - agent execution results

### Orchestration Layer
- Responsibility:
  - classify runtime work
  - build sidecar signals and plans
  - choose reflection, selfcheck, and mode transitions
- Key files:
  - [src/infra/runtime-work-model.ts](/home/park/openclaw/src/infra/runtime-work-model.ts)
  - [memory-sidecar/core/orchestration.py](/home/park/openclaw/memory-sidecar/core/orchestration.py)
  - [memory-sidecar/core/runtime_work.py](/home/park/openclaw/memory-sidecar/core/runtime_work.py)
- Input:
  - request outcome
  - event context
  - sidecar operational state
- Output:
  - sidecar control decisions

### Execution Layer
- Responsibility:
  - run reply execution
  - run one sidecar cycle
- Key files:
  - [src/auto-reply/reply/agent-runner-execution.ts](/home/park/openclaw/src/auto-reply/reply/agent-runner-execution.ts)
  - [memory-sidecar/core/cycle.py](/home/park/openclaw/memory-sidecar/core/cycle.py)
- Input:
  - prepared execution context
- Output:
  - reply payloads
  - runtime records
  - memory acknowledgements

### Infra / Adapter Layer
- Responsibility:
  - path resolution
  - restart and lock handling
  - external memory emit
  - backend bridge access
- Key files:
  - [src/infra/external-memory-root.ts](/home/park/openclaw/src/infra/external-memory-root.ts)
  - [src/infra/external-memory-kernel.ts](/home/park/openclaw/src/infra/external-memory-kernel.ts)
  - [src/infra/post-run-memory.ts](/home/park/openclaw/src/infra/post-run-memory.ts)
  - [src/infra/memory-interaction.ts](/home/park/openclaw/src/infra/memory-interaction.ts)
- Input:
  - request completion
  - env and config
- Output:
  - durable event emit
  - backend metadata

### Memory Layer
- Responsibility:
  - long-term memory backend access
  - operational snapshot handling
  - fallback compatibility
- Key files:
  - [memory-sidecar/core/backends/base.py](/home/park/openclaw/memory-sidecar/core/backends/base.py)
  - [memory-sidecar/core/backends/lancedb_pro.py](/home/park/openclaw/memory-sidecar/core/backends/lancedb_pro.py)
  - [memory-sidecar/core/backends/json_snapshot.py](/home/park/openclaw/memory-sidecar/core/backends/json_snapshot.py)
  - [src/infra/memory-lancedb-pro-bridge.ts](/home/park/openclaw/src/infra/memory-lancedb-pro-bridge.ts)
- Input:
  - sidecar memory operations
- Output:
  - memory recall/store/delete/stat results

### Observability Layer
- Responsibility:
  - runtime state
  - traces
  - acks and commits
  - replay visibility
- Key files:
  - [src/commands/runtime-layout-status.ts](/home/park/openclaw/src/commands/runtime-layout-status.ts)
  - [memory-sidecar/core/events.py](/home/park/openclaw/memory-sidecar/core/events.py)
  - `memory-sidecar/memory/*.json{,l}`
- Input:
  - request emit
  - worker execution
- Output:
  - append-only journals and runtime snapshots

---

## 4. End-to-End Execution Flow

### 4.1 CLI → Gateway → Request
1. `openclaw.mjs` boots the Node entrypoint.
   - File: [src/entry.ts](/home/park/openclaw/src/entry.ts)
   - Scope: request-time startup
2. `runCli()` normalizes argv, env, and command routing.
   - File: [src/cli/run-main.ts](/home/park/openclaw/src/cli/run-main.ts)
3. `gateway start` resolves gateway options and enters the run loop.
   - Files:
     - [src/cli/gateway-cli/run.ts](/home/park/openclaw/src/cli/gateway-cli/run.ts)
     - [src/cli/gateway-cli/run-loop.ts](/home/park/openclaw/src/cli/gateway-cli/run-loop.ts)
4. The gateway server receives requests and dispatches methods.
   - File: [src/gateway/server.impl.ts](/home/park/openclaw/src/gateway/server.impl.ts)

### 4.2 chat.send / agent 调用链
1. `chat.send` is handled in [chat.ts](/home/park/openclaw/src/gateway/server-methods/chat.ts).
2. The chat path dispatches to auto-reply through [dispatch.ts](/home/park/openclaw/src/auto-reply/dispatch.ts).
3. `agent` RPC is handled in [agent.ts](/home/park/openclaw/src/gateway/server-methods/agent.ts).
4. Reply-agent turns are run in [agent-runner.ts](/home/park/openclaw/src/auto-reply/reply/agent-runner.ts).

### 4.3 Request → Event Emit
1. Request-time code does not run the full sidecar cycle inline.
2. `chat.ts`, `agent.ts`, and `agent-runner.ts` call shared post-run emit helpers.
   - File: [src/infra/post-run-memory.ts](/home/park/openclaw/src/infra/post-run-memory.ts)
3. Those helpers call `emitExternalMemoryInteraction(...)`.
   - File: [src/infra/memory-interaction.ts](/home/park/openclaw/src/infra/memory-interaction.ts)
4. `emitExternalMemoryInteraction(...)` calls `queueExternalMemoryKernelRun(...)`.
   - File: [src/infra/external-memory-kernel.ts](/home/park/openclaw/src/infra/external-memory-kernel.ts)
5. The emitter writes the durable event and returns.
   - Scope: post-request

### 4.4 Event → Worker → Sidecar Cycle
1. The worker claims the next event.
   - File: [memory-sidecar/core/worker.py](/home/park/openclaw/memory-sidecar/core/worker.py)
   - Scope: worker-time
2. The worker calls `run_single_cycle(...)`.
   - File: [memory-sidecar/core/cycle.py](/home/park/openclaw/memory-sidecar/core/cycle.py)
3. The cycle loads snapshots and event context.
   - Files:
     - [memory_manager.py](/home/park/openclaw/memory-sidecar/core/memory_manager.py)
     - [events.py](/home/park/openclaw/memory-sidecar/core/events.py)

### 4.5 Sidecar → Memory Backend
1. The cycle resolves the active backend.
   - File: [memory-sidecar/core/backends/__init__.py](/home/park/openclaw/memory-sidecar/core/backends/__init__.py)
2. Canonical backend path:
   - `LanceDbProMemoryBackend`
   - File: [lancedb_pro.py](/home/park/openclaw/memory-sidecar/core/backends/lancedb_pro.py)
3. Fallback backend path:
   - `JsonSnapshotMemoryBackend`
   - File: [json_snapshot.py](/home/park/openclaw/memory-sidecar/core/backends/json_snapshot.py)
4. Memory calls are wrapped in:
   - [memory_interaction.py](/home/park/openclaw/memory-sidecar/core/memory_interaction.py)
5. Request-time code does not call these backend methods directly through sidecar.

### 4.6 Runtime / Trace / Ack 写入链
1. `events.jsonl` is written by the request-side emitter.
2. `traces.jsonl` is written by both request-time emit and worker-time cycle code.
3. `runtime.json` is written by the sidecar cycle.
4. `acks.jsonl` and `commits.jsonl` are written after cycle completion or duplicate-noop detection.

---

## 5. Runtime Model
- request-time work:
  - gateway request handling
  - reply and agent execution
  - response delivery
- post-request work:
  - durable external-memory event emit
- worker / background work:
  - sidecar queue consumption
  - sidecar cycle execution
- replay / recovery work:
  - replayable event reclamation
  - duplicate-noop ack path
- maintenance work:
  - gateway lock and restart loop
  - heartbeat and maintenance flows

Why the model is split:
- request handlers must not block on sidecar control work
- replay and idempotency require durable state outside the request boundary
- worker-time side effects are easier to audit and re-run safely

---

## 6. Memory Architecture
- `memory-sidecar`:
  - controller
  - replay/ack/commit owner
  - operational snapshot owner
  - signal-driven decision layer
- `memory-lancedb-pro`:
  - canonical long-term memory backend
  - long-term recall/store/delete path
- JSON snapshots:
  - operational state only
  - fallback/testing compatibility
- Backend abstraction:
  - protocol: [base.py](/home/park/openclaw/memory-sidecar/core/backends/base.py)
  - wrappers: [memory_interaction.py](/home/park/openclaw/memory-sidecar/core/memory_interaction.py)

---

## 7. Event, Ack, Trace, Runtime Model
- `events.jsonl`
  - writer: request-side external memory emitter
  - purpose: durable handoff from request path to worker path
- `acks.jsonl`
  - writer: sidecar
  - purpose: idempotent acknowledgement
- `commits.jsonl`
  - writer: sidecar
  - purpose: durable processing result
- `traces.jsonl`
  - writers: request-side emitter and sidecar
  - purpose: append-only operational trace
- `runtime.json`
  - writer: sidecar cycle
  - purpose: operational runtime projection

Idempotency:
- same `event_id` is checked against ack/runtime state
- already-applied events are finalized as duplicate-noop

Replay:
- `recovery.json` keeps replayable status
- worker reclaims replayable events on later passes

---

## 8. Signal-Driven Orchestration
- Signals are built from:
  - working state
  - runtime history
  - event context
  - health metrics
  - recall yield
- Explicit signal structure:
  - [signals.py](/home/park/openclaw/memory-sidecar/core/signals.py)
- Controller implementation:
  - [orchestration.py](/home/park/openclaw/memory-sidecar/core/orchestration.py)
- Modes:
  - `normal`
  - `stability`
  - `convergence`
- Signal-triggered behaviors:
  - recall
  - reflection
  - selfcheck
  - local cleanup
  - mode switching

---

## 9. Path & Environment Resolution
- TS resolver:
  - [src/infra/external-memory-root.ts](/home/park/openclaw/src/infra/external-memory-root.ts)
- Python resolver:
  - [memory-sidecar/core/runtime_paths.py](/home/park/openclaw/memory-sidecar/core/runtime_paths.py)
- Resolution priority:
  1. `OPENCLAW_EXTERNAL_MEMORY_ROOT`
  2. `OPENCLAW_RUNTIME_ROOT + /memory-sidecar`
  3. canonical default
  4. Python-only `legacy-code-default`
- Current non-unified part:
  - Python still keeps `legacy-code-default` for direct package-local execution
  - TS does not

---

## 10. Observability & Debugging
- Trace structure uses correlation fields:
  - `request_id`
  - `event_id`
  - `worker_task_id`
  - `runtime_step`
  - `ack_id`
  - `replay_attempt`
  - `work_class`
- Main debug entrypoints:
  - `node --import tsx src/entry.ts runtime --json`
  - `python3 main.py --print-root`
  - `python3 main.py --queue-status`
  - `python3 main.py --trace-view 5`
- Debug patterns:
  - event not executing: inspect `events.jsonl` and `recovery.json`
  - ack missing: inspect `acks.jsonl`, `traces.jsonl`, `runtime.json`
  - backend inactive: inspect runtime config and backend identity fields

---

## 11. Safety Model
- Patch proposal and patch apply are separate
- Auto apply is disabled by default
- Apply requires explicit enable
- Allowlist enforcement lives in:
  - [selfcheck_manager.py](/home/park/openclaw/memory-sidecar/core/selfcheck_manager.py)
- Dangerous action tracing is explicit

---

## 12. Tradeoffs & Known Limitations
- File-backed journals instead of external message queue
- Worker process model instead of a long-running daemon framework
- Request pipelines still own their normal reply/session side effects
- Python and TS path resolution are close but not identical
- Project scope still contains both built-in memory modules and the external sidecar path

---

## 13. Migration Notes
- Old model:
  - best-effort trigger
  - more rigid sidecar loop
  - more standalone-sidecar behavior
- Current model:
  - durable event emit
  - worker consumption
  - signal-driven orchestration
  - canonical external long-term backend
- Compatibility:
  - deprecated paths retained in resolver logic
  - JSON fallback retained for testing and degraded mode

---

## 14. Quick Debug Checklist
- Check runtime root
- Check memory root
- Check `events.jsonl`
- Check `recovery.json`
- Check worker status
- Check `acks.jsonl`
- Check `runtime.json`
- Check backend slot in runtime config

---

## 15. Conclusion
- The runtime is event-driven at the external-memory boundary.
- `memory-sidecar` is the controller and replay layer.
- `memory-lancedb-pro` is the long-term memory engine.
- Observability is append-only and correlation-based.
- The current design favors explicit boundaries, replayability, and operational debugging over hidden background magic.
