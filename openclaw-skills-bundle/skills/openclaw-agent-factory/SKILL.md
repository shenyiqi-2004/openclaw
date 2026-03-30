---
name: openclaw-agent-factory
description: Design and scaffold OpenClaw multi-agent systems from proven template patterns. Use when the user wants to create, refine, or operationalize a multi-agent team, pipeline, project manager swarm, channel-routed agent setup, or scheduled specialist workflow in OpenClaw.
---

# OpenClaw Agent Factory

Use this skill when the task is to build or refine a multi-agent OpenClaw system. Do not load all references by default. First classify the request, then read only the relevant template file.

## Pattern selection

Choose one primary pattern first:

- Specialist team:
  - use when the user wants named roles such as strategy, dev, marketing, ops, or business
  - read `references/specialist-team.md`
- Project manager swarm:
  - use when the user wants parallel execution with thin coordination and shared task state
  - read `references/project-manager-swarm.md`
- Chained content pipeline:
  - use when the user wants staged handoffs such as research -> writing -> assets -> publish
  - read `references/content-pipeline.md`
- Event-driven project state:
  - use when the user wants automatic status tracking, blockers, standups, or decision history instead of a Kanban board
  - read `references/project-state.md`

If the user asks for a general multi-agent system and does not specify a topology, start with `references/pattern-matrix.md`, pick the smallest viable pattern, and only then read one detailed template.

## Design rules

- Prefer 2 agents over 5 unless the user clearly needs more.
- Keep one thin coordinator. Do not let every agent orchestrate every other agent.
- Give each agent one clear responsibility, one channel or trigger path, and one output type.
- Use shared files for durable coordination:
  - `GOALS.md`
  - `DECISIONS.md`
  - `PROJECT_STATUS.md`
  - `STATE.yaml` when parallel task ownership matters
- Give agents private notes only when domain specialization really needs it.
- Scheduled work is for recurring tasks only. Do not cron everything.
- Prefer explicit routing rules over fuzzy "anyone can answer" setups.

## Build procedure

1. Classify the requested system.
2. Choose the smallest pattern that fits.
3. Define:
   - agents
   - channels or trigger paths
   - shared state files
   - schedules
   - escalation / fallback rules
4. Produce only the needed artifacts:
   - `AGENTS.md`
   - `HEARTBEAT.md`
   - `STATE.yaml`
   - shared memory file layout
   - if the user wants a quick start, copy from `assets/`
5. Keep the first version minimal and runnable.

## Anti-patterns

- Too many agents with overlapping responsibilities
- Two coordinators fighting each other
- No shared source of truth
- Letting every agent write all shared files
- Storing all raw chat history as "memory"
- Adding cron jobs before the manual flow works

## Output style

When using this skill, prefer concrete artifacts over abstract advice:

- team layout
- routing rules
- file layout
- schedule
- first-pass prompts or role definitions
- minimal implementation steps

## Source and attribution

These templates are adapted from the public MIT-licensed repository:

- `hesamsheikh/awesome-openclaw-usecases`

They are distilled into reusable local templates instead of copied as a giant awesome-list.
