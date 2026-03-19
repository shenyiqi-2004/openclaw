# OpenClaw Skills Bundle

This folder contains the current curated OpenClaw skill pool exported from the local runtime.

## Included

- `skills/`: the exported OpenClaw skills collection

## Current structure

- Exported skills: 69

## Notes

- Fully overlapping Tavily duplicate was removed in favor of `tavily-search`.
- `self-improving-agent`, `cron-tools`, `github-search`, `github-release-monitor`, `github-ssh-fix`, and `github-to-skills` were merged into their primary entry skills before export.
- Browser and skill-ecosystem specializations are still included in the bundle, but no longer published under a separate disabled or on-demand folder.
- `agent-browser` and `find-skills` include explicit escalation rules for specialized follow-up skills.
