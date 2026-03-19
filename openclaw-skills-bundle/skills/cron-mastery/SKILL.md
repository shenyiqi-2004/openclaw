---
name: cron-mastery
description: Master OpenClaw timing systems for reliable reminders, scheduled maintenance, periodic reports, and cron-based operational workflows. Use when choosing between heartbeat and cron, setting exact schedules, or using bundled daily and weekly automation scripts.
---

# Cron Mastery

Use this as the single scheduling skill for OpenClaw.

## Core rule

- Heartbeat is approximate and can drift.
- Cron is for exact timing and repeatable scheduled jobs.

## When to use cron

Use cron for:
- reminders at exact times
- daily or weekly reports
- maintenance and janitor jobs
- recurring operational checks

Use heartbeat for:
- casual polling
- low-priority periodic checks
- opportunistic follow-through that does not require exact timing

## Bundled scripts

This merged skill includes ready-to-run examples:
- `scripts/daily-brief.sh`
- `scripts/weekly-review.sh`

Use them as templates or directly schedule them via cron.

## Practical patterns

### One-shot reminder
Use cron or a one-shot scheduled job when a reminder must happen at a specific time.

### Daily brief
Run `scripts/daily-brief.sh` on workdays for a structured daily summary.

### Weekly review
Run `scripts/weekly-review.sh` at week end for a recurring review.

## Safety rules

- Do not use long waits or sleep loops as a substitute for scheduling.
- Keep cron jobs explicit and auditable.
- Prefer a small number of reliable jobs over many overlapping schedules.
- Remove one-shot jobs after they succeed.

## References

- `references/templates.md` contains reusable scheduling templates.

## OpenClaw guidance

- Use this skill as the single scheduling entry point.
- Do not keep `cron-tools` active beside it.
