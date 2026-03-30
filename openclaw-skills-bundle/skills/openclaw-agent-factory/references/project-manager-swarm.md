# Project Manager Swarm Template

Adapted from the autonomous project management pattern in `awesome-openclaw-usecases`.

## When to use

Use this when the user wants parallel execution with low orchestrator overhead.

## Core rule

Main session stays thin. A PM subagent owns execution state.

## STATE.yaml template

```yaml
project: my-project
updated: 2026-03-19T12:00:00Z

tasks:
  - id: task-a
    status: in_progress
    owner: pm-frontend
    notes: Working on the responsive layout

  - id: task-b
    status: blocked
    owner: pm-backend
    blocked_by: task-a
    notes: Waiting for schema update

next_actions:
  - "pm-backend: resume when task-a is done"
  - "pm-frontend: request review when layout is stable"
```

## Delegation template

```text
Main session = coordinator only.

Workflow:
1. New task arrives
2. Check if PM already exists
3. If yes -> send to PM
4. If no -> spawn PM
5. PM updates STATE.yaml
6. Main session reports concise progress back
```

## Label convention

- `pm-{project}`
- `pm-{project}-{scope}` if you need more than one PM

## Guardrails

- Main session should not execute all subtasks itself.
- STATE.yaml must remain the source of truth.
- Only the owning PM updates task ownership and status.
