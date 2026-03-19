---
name: self-improving
description: Build durable self-improvement loops for OpenClaw. Use when a command, tool, API, or operation fails, when the user corrects or rejects work, when a better recurring approach is discovered, or when stable learnings should be logged, reviewed, and promoted into long-term operating guidance.
---

# Self-Improving

Use this as the single self-improvement skill for OpenClaw.

## What this skill covers

- Self-reflection after meaningful work
- Correction logging after user feedback
- Error capture after command, tool, API, or integration failures
- Promotion of stable learnings into long-term operating guidance
- Optional proactive review and hook-based follow-through

## Quick actions

| Situation | Action |
|---|---|
| Command or tool failed | Log the failure and the fix pattern |
| User corrected the output | Record the correction and the better rule |
| Better recurring approach was discovered | Promote it as a reusable pattern |
| OpenClaw workflow should improve permanently | Update memory or operating files, not transient chat |
| A new integration needs continuous checks | Use the hook examples and setup references |

## Operating model

1. Capture the error, correction, or improved method in concise markdown.
2. Keep raw learnings small and structured.
3. Promote only stable, reusable rules into operating guidance.
4. Do not duplicate temporary chatter or low-confidence guesses into long-term memory.
5. Prefer one durable improvement record over repeated paraphrases.

## Storage guidance

Primary files already bundled in this skill:
- `memory.md`
- `corrections.md`
- `learning.md`
- `reflections.md`
- `operations.md`
- `boundaries.md`
- `heartbeat-rules.md`
- `heartbeat-state.md`
- `setup.md`

Bundled integration helpers merged from the lighter variant:
- `references/openclaw-integration.md`
- `references/hooks-setup.md`
- `references/examples.md`
- `hooks/openclaw/*`
- `scripts/activator.sh`
- `scripts/error-detector.sh`
- `scripts/extract-skill.sh`

## Promotion rules

Promote only:
- durable user preferences
- reusable workflows
- verified project facts
- important failures and fixes
- stable constraints affecting future decisions

Do not promote:
- temporary chatter
- speculative or unverified content
- noisy metadata
- repeated restatements of the same learning

## OpenClaw guidance

- Use this skill as the single self-improvement entry point.
- Do not keep a separate `self-improving-agent` skill active beside it.
- When in doubt, prefer fewer, cleaner learnings over more logs.
