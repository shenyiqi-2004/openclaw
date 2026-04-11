---
name: code-simplifier
description: Simplify and refine existing code for clarity, consistency, and maintainability while preserving exact behavior. Use when the user asks to simplify, clean up, refactor without changing functionality, reduce complexity, improve readability, remove redundant abstractions, or make recent code changes easier to understand and maintain.
---

# Code Simplifier

Use this skill when working on existing code that should behave the same but read better.

## Core rules

- Preserve behavior exactly unless the user explicitly asks for functional changes.
- Prefer clearer structure over fewer lines.
- Avoid clever compression that harms debugging or maintenance.
- Focus on recently touched code unless the user asks for a broader sweep.
- Follow repository-local conventions before generic preferences.

## Workflow

1. Identify the target files or the recently modified area.
2. Read project guidance first when present (`CLAUDE.md`, `AGENTS.md`, lint config, formatter config, tests, existing surrounding style).
3. Simplify only where there is a clear readability or maintainability win.
4. Keep public APIs, outputs, side effects, and error semantics unchanged unless told otherwise.
5. After edits, run the smallest useful validation available (tests, lint, typecheck, or targeted smoke check).

## Preferred transformations

- Reduce unnecessary nesting.
- Replace confusing conditionals with clearer `if/else` or `switch` flows.
- Remove dead/redundant intermediate variables and abstractions.
- Improve naming when it materially helps readability.
- Split overly dense logic into small, well-named helpers when that makes the code easier to follow.
- Remove comments that only restate obvious code.
- Keep useful comments that explain intent, constraints, or non-obvious decisions.

## Avoid

- Functional changes disguised as cleanup.
- Large drive-by refactors outside the requested scope.
- Style churn with no readability benefit.
- Over-inlining or over-abstracting.
- Nested ternaries when clearer control flow would help.

## Bundled source material

Anthropic's original plugin files are kept in this skill directory for reference:

- `.claude-plugin/plugin.json`
- `agents/code-simplifier.md`

Read them if you want the original plugin wording or behavior guidance.
