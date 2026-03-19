# OpenClaw Skills Bundle

This folder contains the current curated OpenClaw skill pool exported from the local runtime.

## Included

- `skills/`: active global OpenClaw skills
- `skills-on-demand/`: preserved specialized skills moved out of the always-loaded pool

## Current structure

- Active global skills: 61
- On-demand browser skills: 4
- On-demand skill-ecosystem helpers: 4

## Notes

- Fully overlapping Tavily duplicate was removed in favor of `tavily-search`.
- `self-improving-agent`, `cron-tools`, `github-search`, `github-release-monitor`, `github-ssh-fix`, and `github-to-skills` were merged into their primary entry skills before export.
- Browser and skill-ecosystem stacks were layered so that only one primary entry skill stays active for each stack.
