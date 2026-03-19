# Spiders Reference

This local install is the lightweight version of the official Scrapling skill.

For the full spider reference, see:
- https://github.com/D4Vinci/Scrapling/tree/main/agent-skill/Scrapling-Skill/references/spiders
- https://github.com/D4Vinci/Scrapling/tree/main/docs

## Quick reminder

- Subclass `Spider`
- Set `name` and `start_urls`
- Implement `async def parse(self, response)`
- Yield structured items or `response.follow(...)`
- Use `crawldir` for pause/resume on long crawls
