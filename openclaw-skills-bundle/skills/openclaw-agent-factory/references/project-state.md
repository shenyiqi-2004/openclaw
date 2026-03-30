# Event-Driven Project State Template

Adapted from the project state management pattern in `awesome-openclaw-usecases`.

## When to use

Use this when the user wants OpenClaw to track progress, blockers, decisions, and standups as structured state rather than a static board.

## Minimal data model

If a real database is too much, start with files:

```text
project-state/
├── PROJECT_STATUS.md
├── DECISIONS.md
├── BLOCKERS.md
└── EVENTS.md
```

If the user explicitly wants a database, use a simple events table plus blockers table.

## Event interpretation rules

- "Finished X" -> progress event
- "Blocked on Y" -> blocker event
- "Starting Z" -> active phase change
- "Decided to A" -> decision event
- "Pivoting to B" -> pivot event

## Daily summary template

```text
Daily standup

Yesterday:
- {progress}

Today:
- {planned}

Blocked:
- {open blockers}

Key decisions:
- {decisions}
```

## Guardrails

- Do not overbuild the schema on day one.
- Preserve decision context, not just status labels.
- Link commits only if the user already has a clean git workflow.
