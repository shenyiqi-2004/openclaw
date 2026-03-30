# Chained Content Pipeline Template

Adapted from the content factory pattern in `awesome-openclaw-usecases`.

## When to use

Use this when the user wants a staged workflow such as research -> writing -> thumbnails -> publishing.

## Channel layout

```text
#research
#scripts
#assets
#publish
```

## Agent stages

- Research agent
- Writing agent
- Asset agent
- Optional publish/review agent

## Prompt template

```text
Build a multi-agent content pipeline.

1. Research Agent:
   - gather top opportunities
   - output top 5 with sources

2. Writing Agent:
   - pick the best opportunity
   - produce the requested draft format

3. Asset Agent:
   - create supporting visual assets

4. Optional Review/Publish Agent:
   - validate format
   - prepare final delivery package

Run on this schedule: {schedule}
Keep outputs in separate channels.
```

## Guardrails

- Keep handoffs explicit.
- Do not let downstream stages guess the input format.
- Validate one manual run before enabling a cron schedule.
