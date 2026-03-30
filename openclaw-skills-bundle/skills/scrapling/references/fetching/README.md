# Fetching Reference

This local install is the lightweight version of the official Scrapling skill.

For the full fetching reference, see:
- https://github.com/D4Vinci/Scrapling/tree/main/agent-skill/Scrapling-Skill/references/fetching
- https://github.com/D4Vinci/Scrapling/tree/main/docs

## Quick reminder

- `Fetcher` / `FetcherSession`: plain HTTP with browser impersonation
- `DynamicFetcher` / `DynamicSession`: browser-rendered pages
- `StealthyFetcher` / `StealthySession`: anti-bot / protected pages

Escalate in this order:
1. Fetcher
2. Dynamic
3. Stealthy
