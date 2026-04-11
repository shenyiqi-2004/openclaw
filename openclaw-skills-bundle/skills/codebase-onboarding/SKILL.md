---
name: codebase-onboarding
description: "Analyze an unfamiliar codebase and generate a structured onboarding guide with architecture map, key entry points, conventions, and starter project instructions. Use when joining a new project or first time opening a repo."
---

# Codebase Onboarding

Systematically analyze an unfamiliar codebase and produce a structured onboarding guide.

## When to Use

- First time opening a project
- Joining a new team or repository
- "Help me understand this codebase"
- "Walk me through this repo"
- Generating project-level instructions for a new repo

## 4-Phase Workflow

### Phase 1: Reconnaissance

Gather signals **without reading every file**. Run in parallel:

1. **Package manifest** → package.json, go.mod, Cargo.toml, pyproject.toml, pom.xml, Gemfile, etc.
2. **Framework fingerprint** → next.config.*, vite.config.*, django settings, fastapi main, rails config, etc.
3. **Entry points** → main.*, index.*, app.*, server.*, cmd/, src/main/
4. **Directory tree** → top 2 levels, ignoring node_modules/vendor/.git/dist/build/__pycache__
5. **Tooling** → .eslintrc*, tsconfig.json, Makefile, Dockerfile, .github/workflows/, CI configs
6. **Test structure** → tests/, __tests__/, *_test.go, *.spec.ts, pytest.ini, jest.config.*

### Phase 2: Architecture Mapping

From reconnaissance, identify:

- **Tech Stack**: language(s), framework(s), database(s), build tools, CI/CD
- **Architecture Pattern**: monolith/monorepo/microservices, frontend/backend split, API style
- **Key Directories**: map top-level dirs to purpose
- **Data Flow**: trace one request from entry to response (router → validation → business logic → database)

### Phase 3: Convention Detection

- **Naming**: file naming (kebab/camel/Pascal/snake), component naming, test file pattern
- **Code Patterns**: error handling style, DI vs direct imports, state management, async patterns
- **Git**: branch naming, commit style, PR workflow (skip if history unavailable)

### Phase 4: Generate Output

#### Onboarding Guide (print to conversation)

```markdown
# Onboarding Guide: [Project Name]

## Overview
[2-3 sentences: what it does and who it serves]

## Tech Stack
| Layer | Technology | Version |
|-------|-----------|---------|
| ... | ... | ... |

## Architecture
[How components connect]

## Key Entry Points
- **API**: path — description
- **UI**: path — description
- **Config**: path — description

## Directory Map
[Top-level dir → purpose]

## Common Tasks
- Dev: `command`
- Test: `command`
- Build: `command`

## Where to Look
| I want to... | Look at... |
|--------------|-----------|
| ... | ... |
```

#### Project Instructions (write to repo root as CLAUDE.md or equivalent)

```markdown
# Project Instructions

## Tech Stack
[summary]

## Code Style
[detected conventions]

## Testing
- Command: [detected]
- Pattern: [detected]

## Build & Run
- Dev/Build/Lint commands

## Conventions
[commit style, error handling, etc.]
```

## Rules

- **Don't read everything** — use Glob/Grep, read selectively
- **Verify, don't guess** — trust code over config if they conflict
- **Respect existing docs** — enhance, don't replace
- **Stay concise** — scannable in 2 minutes
- **Flag unknowns** — "Could not determine X" > wrong answer

Origin: Adapted from Everything Claude Code (ECC) codebase-onboarding skill.
