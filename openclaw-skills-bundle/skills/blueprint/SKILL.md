---
name: blueprint
description: "Turn a one-line objective into a step-by-step construction plan for multi-session projects. Each step has a self-contained context brief so a fresh agent can execute it cold. Use for complex multi-PR tasks."
---

# Blueprint — Construction Plan Generator

Turn a one-line objective into a step-by-step construction plan that any coding agent can execute cold.

## When to Use

- Breaking a large feature into multiple PRs with clear dependency order
- Planning a refactor or migration that spans multiple sessions
- Coordinating parallel workstreams across sub-agents
- Any task where context loss between sessions would cause rework

**Do NOT use** for tasks completable in a single PR, fewer than 3 tool calls, or when the user says "just do it."

## 5-Phase Pipeline

### Phase 1: Research
Pre-flight checks and context gathering:
- Git status, remote, default branch
- Project structure (top 2 levels)
- Existing plans in `plans/` directory
- Memory files and AGENTS.md protocols

### Phase 2: Design
Break objective into one-PR-sized steps (3–12 typical):
- Assign dependency edges (which steps block which)
- Mark parallel vs serial ordering
- Assign model tier per step (strongest for design, default for implementation)
- Define rollback strategy per step

### Phase 3: Draft
Write self-contained Markdown plan to `plans/`:

```markdown
# Plan: [Objective]

## Step 1: [Title]
### Context Brief
[Everything a fresh agent needs to execute this step cold]

### Tasks
- [ ] Task 1
- [ ] Task 2

### Verification
```bash
[Commands to verify step completion]
```

### Exit Criteria
- [Concrete, measurable conditions]

### Dependencies
- None / Depends on Step X

### Rollback
- [How to undo this step if needed]
```

Each step MUST include:
- **Context Brief** — self-contained, no prior context needed
- **Tasks** — specific, actionable items
- **Verification** — commands to confirm completion
- **Exit Criteria** — measurable conditions
- **Rollback** — how to undo

### Phase 4: Review
Adversarial review against checklist:
- [ ] Every step is independently executable?
- [ ] Dependency graph is acyclic?
- [ ] Parallel steps have no shared file mutations?
- [ ] Rollback strategy exists for each step?
- [ ] Verification commands are concrete (not "check it works")?
- [ ] No step exceeds single-PR scope?

### Phase 5: Register
- Save plan to `plans/` directory
- Update memory index if applicable
- Report step count + parallelism summary to user

## Key Features

- **Cold-start execution** — Every step includes full context brief
- **Parallel step detection** — Dependency graph identifies steps with no shared files
- **Plan mutation** — Steps can be split, inserted, skipped, reordered with audit trail
- **Git-aware** — With git+gh: generates branch/PR workflow. Without: direct mode

## Anti-Patterns to Avoid

- Steps that say "continue from previous step" (breaks cold-start)
- Verification that says "check it works" (not measurable)
- Steps that modify the same file in parallel (conflict risk)
- Plans with >12 steps (split into phases instead)
- Missing rollback strategies

## Example

```
Objective: "migrate database to PostgreSQL"

Steps:
1. Add PostgreSQL driver and connection config     [parallel: none]
2. Create migration scripts for each table          [depends: 1]
3. Update repository layer to use new driver        [depends: 1]
4. Add integration tests against PostgreSQL         [parallel with 3, depends: 2]
5. Remove old database code and config              [depends: 3, 4]
```

Origin: Adapted from Everything Claude Code (ECC) blueprint skill.
