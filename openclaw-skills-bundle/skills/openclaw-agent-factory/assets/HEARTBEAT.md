## Heartbeat

Use recurring work only for stable, repeated tasks.

Daily:
- 08:00 Lead posts morning standup from current goals, blockers, and overnight work.
- 18:00 Lead posts end-of-day recap with progress and next actions.

Optional specialist jobs:
- Research: collect top opportunities or monitor target sources.
- Dev: check CI health and open implementation blockers.
- Ops: check service health and critical failures only.

Rules:
1. Do not add cron jobs before the manual flow works once.
2. Keep each scheduled task single-purpose.
3. Scheduled tasks should update shared files, not create parallel truth sources.
