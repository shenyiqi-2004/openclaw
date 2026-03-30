# Specialist Team Template

Adapted from the multi-agent team pattern in `awesome-openclaw-usecases`.

## When to use

Use this when the user wants a small team of named agents with distinct roles and one shared control interface.

## Minimal team

- Lead agent
- One specialist

Only add more roles when the user clearly needs them.

## Recommended artifacts

### Shared files

```text
team/
├── GOALS.md
├── DECISIONS.md
├── PROJECT_STATUS.md
└── agents/
    ├── lead/
    └── specialist/
```

### Routing template

```text
Telegram group: "Team"

Routing:
- @lead -> lead agent
- @specialist -> specialist agent
- @all -> broadcast
- no tag -> lead agent

Each agent:
1. Read GOALS.md and PROJECT_STATUS.md
2. Read private notes if needed
3. Answer
4. Update shared files only if the reply changes goals, decisions, or status
```

### Role template

```text
## SOUL.md

You are {name}, the {role}.

Responsibilities:
- {responsibility_1}
- {responsibility_2}
- {responsibility_3}

Style:
- {tone}
- {decision style}

Escalate to the lead when:
- work crosses roles
- priorities conflict
- a decision affects other agents
```

### Schedule template

```text
## HEARTBEAT.md

Daily:
- 8:00 AM: lead posts standup
- 6:00 PM: lead posts recap

Specialist:
- run only role-specific recurring tasks
```

## Guardrails

- Do not let every agent update every file.
- Keep a lead agent as the default responder.
- Keep private notes light; shared files should hold the durable project truth.
