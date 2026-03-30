## Multi-Agent Routing

Default routing:
- No tag -> lead agent
- `@all` -> broadcast to all agents

Example specialist routing:
- `@lead` -> lead / coordinator
- `@dev` -> implementation agent
- `@research` -> research agent
- `@ops` -> operations agent

Rules:
1. Lead agent owns prioritization and cross-agent decisions.
2. Specialists answer only inside their scope.
3. Shared files are the durable source of truth:
   - `GOALS.md`
   - `DECISIONS.md`
   - `PROJECT_STATUS.md`
   - `STATE.yaml` when task ownership matters
4. Specialists update shared files only when their work changes goals, decisions, status, blockers, or next actions.
5. Do not let every agent orchestrate every other agent.

Delegation pattern:
1. Lead receives request.
2. Lead decides whether to answer directly, delegate to one specialist, or spawn parallel subtasks.
3. Specialists return concise outputs.
4. Lead synthesizes and reports back.
