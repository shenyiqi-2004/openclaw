# OpenClaw Skills Bundle

This folder contains the current curated OpenClaw skill pool exported from the local runtime.

## Included

- `skills/`: the exported OpenClaw skills collection

### Notable additions

- `skills/gui-desktop-control`: Windows desktop GUI automation toolkit for OpenClaw and WSL, covering mouse control, keyboard input, screenshots, and window management. Screenshot interpretation is expected to come from the configured vision-capable OpenClaw model.

## Current structure

- Exported skills: 70

## Notes

- Fully overlapping Tavily duplicate was removed in favor of `tavily-search`.
- `self-improving-agent`, `cron-tools`, `github-search`, `github-release-monitor`, `github-ssh-fix`, and `github-to-skills` were merged into their primary entry skills before export.
- Browser and skill-ecosystem specializations are still included in the bundle, but no longer published under a separate disabled or on-demand folder.
- `agent-browser` and `find-skills` include explicit escalation rules for specialized follow-up skills.
