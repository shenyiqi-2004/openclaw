---
name: session-cleanup
description: Safely decide whether stale OpenClaw sessions, subagent runs, and collaboration-room artifacts should be kept, hidden, deferred, or deleted. Use when the session picker is noisy, old subagent sessions linger, or internal runtime records need low-token LLM review before cleanup.
---

# session-cleanup

Use this skill for OpenClaw session noise, especially stale `agent:*:subagent:*` records and leftover collaboration-room artifacts.

## Goal

Make a cheap, safe decision for each candidate:

- `keep`
- `hide`
- `defer`
- `delete`

Prefer `hide` or `defer` over `delete` when evidence is weak.

## Safe scope

- `agent:*:subagent:*`
- stale records in:
  - `.openclaw/subagents/runs.json`
  - `.openclaw/workspace/runtime/chat-rooms.json`
  - `.openclaw/workspace/runtime/chat-messages.json`
  - `.openclaw/workspace/runtime/collaboration-halls.json`
  - `.openclaw/workspace/runtime/collaboration-task-cards.json`
  - `.openclaw/workspace/runtime/collaboration-hall-messages.json`
  - `.openclaw/workspace/runtime/tasks.json`
  - `.openclaw/workspace/runtime/projects.json`

Never delete by this skill:

- `agent:main:main`
- currently active sessions
- records still referenced by active rooms, tasks, or controllers
- anything without a backup

## Process

1. Gather compact metadata only. Do not send full transcripts to the LLM.
2. Rule-filter first. Skip LLM review for obvious non-candidates.
3. For each remaining candidate, build a tiny review block with:
   - session key
   - controller session key
   - age / last update
   - whether it is a subagent
   - whether it is still referenced elsewhere
   - a one-line purpose or title if present
4. Ask the LLM for `keep`, `hide`, `defer`, or `delete` plus one short reason.
5. Backup every touched file before any deletion.
6. Apply cleanup conservatively.
7. Restart the gateway only if runtime files were changed.

## Rule filter

Send a candidate to LLM review only if all are true:

- it is not `agent:main:main`
- it is not obviously active now
- it is older than the current task window
- it looks internal, stale, or orphaned

Immediately `keep` without LLM review if any are true:

- it is the main session
- it updated recently
- it still has clear live references

## LLM review budget

- Keep each candidate summary under about 150 tokens.
- Review candidates independently.
- Do not include raw chat history unless there is no other way to judge.
- If uncertain, return `defer`.

Use a stable prompt shape:

```text
Decide whether this OpenClaw session artifact should be kept, hidden, deferred, or deleted.
Return exactly: decision | short reason

candidate:
- key: ...
- type: ...
- controller: ...
- age: ...
- referenced: yes/no
- note: ...
```

## Deletion rule

Delete only when all are true:

- LLM says `delete`
- the record is stale
- it has no live references
- a backup exists

If the LLM says `hide`, prefer UI filtering or leaving the record in place.

## Output

Report decisions in a compact table or flat list:

- `candidate`
- `decision`
- `reason`
- `files touched`

## Boundary

This skill decides cleanup. It does not patch OpenClaw core display logic. Use the session-title patch separately for title pollution.
