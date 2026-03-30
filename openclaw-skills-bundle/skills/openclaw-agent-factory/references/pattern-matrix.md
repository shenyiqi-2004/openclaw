# Pattern Matrix

Use this file first when the user wants a multi-agent system but has not chosen a topology yet.

## 1. Specialist team

Best for:
- solo founder support
- cross-functional work
- one control chat with named specialist agents

Core shape:
- 1 lead agent
- 1 to 3 specialists
- shared memory files
- optional scheduled updates

Do not use when:
- the user only needs one recurring automation
- the user mainly needs a pipeline, not a team

## 2. Project manager swarm

Best for:
- parallel execution
- coding or research projects with multiple workstreams
- minimizing main-session orchestration overhead

Core shape:
- thin main session
- project PM subagent
- optional specialist sub-subagents
- `STATE.yaml` as source of truth

Do not use when:
- there is no persistent project file area
- the task is just a single serial workflow

## 3. Chained content pipeline

Best for:
- research -> writing -> design handoffs
- scheduled production systems
- platform-specific content factories

Core shape:
- stage-based agents
- explicit handoff order
- separate channels or outputs per stage
- one recurring schedule

Do not use when:
- outputs are not stage-based
- content volume is too low to justify automation

## 4. Event-driven project state

Best for:
- replacing stale Kanban boards
- preserving blockers, decisions, pivots, and standups
- querying project history conversationally

Core shape:
- event log or database
- project status query flow
- daily summary cron
- optional commit linking

Do not use when:
- the user only needs agent routing
- there is no desire to maintain structured project state

## Selection rule

- If the user says "team", "roles", or "specialists": start with specialist team.
- If the user says "parallel", "subagents", or "project coordination": start with project manager swarm.
- If the user says "pipeline", "factory", or "overnight generation": start with content pipeline.
- If the user says "status", "blockers", "standups", or "why did we decide X": start with event-driven project state.
