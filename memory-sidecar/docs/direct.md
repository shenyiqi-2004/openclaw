# OpenClaw Memory Kernel — Final Codex Prompt

You are working inside my OpenClaw project.

This is a real repository implementation, cleanup, migration, and long-term memory-runtime task.

You must directly inspect the repository, create and modify files, run the code, verify behavior, and complete the work in the correct order.

Do **not** stop at planning.  
Do **not** redesign the system into your own alternative architecture.  
Do **not** overengineer.  
Do **not** add unnecessary complexity.  
Do **not** silently skip requested phases.  

Your job is to:

1. **reorganize and clean existing OpenClaw memory**
2. **build a stable minimal memory kernel**
3. **define and implement OpenClaw’s future memory operating logic**
4. **make the system self-checking, self-repairing, self-evaluating, and lightly self-evolving**
5. **keep everything simple, deterministic, low-token, low-disk, and auditable**

---

# Permanent Design Intent

This system must follow these permanent priorities:

1. Help OpenClaw live as long as possible
2. Build a memory structure that can keep being used in OpenClaw
3. Keep it free
4. Keep it easy for the human; Codex can do the heavy work
5. Retrieval must be fast, accurate, efficient, and low-token
6. Disk usage must stay as small as possible
7. The system must be able to self-check, self-repair, self-evaluate, and lightly self-evolve
8. It must **not** become so complex that it becomes slower, larger, more expensive, less accurate, or harder to maintain

---

# Core Philosophy

This is **not** a chatbot-style memory dump.

This is a **small, stable, deterministic memory kernel**.

The system should:

- remember only what is useful
- retrieve only what is necessary
- forget what is unused
- compress aggressively
- evaluate itself with lightweight numeric rules
- adjust itself only in safe, minimal ways
- avoid complexity creep

The system must prefer:

- stability over cleverness
- simplicity over sophistication
- small memory over large memory
- deterministic control over speculative intelligence
- low token usage over verbose reasoning
- low disk usage over archival completeness

---

# Hard Constraints

These are non-negotiable:

- Python standard library only
- JSON only
- No external dependencies
- No embeddings
- No vector database
- No graph database
- No async
- No database
- No frameworks
- No exec()
- No eval()
- No dynamic code execution
- No metaprogramming
- No hidden magic
- No over-abstraction
- Python 3.11+

The code must be:

- deterministic
- readable
- modular
- inspectable
- easy to debug
- easy to extend later
- easy to audit

---

# Required Operating Model

The final system must internally behave as **five small loops**, not a giant architecture:

1. **Execution loop**  
   Move the current task forward.

2. **Memory loop**  
   Retrieve, write, compress, deduplicate, clean.

3. **Evaluation loop**  
   Measure whether the system is getting healthier or worse.

4. **Repair loop**  
   If the system degrades, clean, shrink, simplify, and reduce learning frequency.

5. **Micro-evolution loop**  
   Only make tiny safe adjustments, preferably to rules and thresholds, not architecture.

Do not add more loops than necessary.

---

# Target File Structure

Create or ensure this structure exists:

```text
openclaw/
├─ AGENTS.md
├─ main.py
├─ memory/
│  ├─ working.json
│  ├─ summary.json
│  ├─ strategy.json
│  ├─ reflection.json
│  ├─ selfcheck.json
│  ├─ meta.json
│  └─ knowledge/
│     ├─ programming.json
│     ├─ science.json
│     ├─ finance.json
│     └─ general.json
└─ core/
   ├─ memory_manager.py
   ├─ strategy_manager.py
   ├─ router.py
   ├─ retriever.py
   ├─ reflection_manager.py
   ├─ cleaner.py
   ├─ executor.py
   ├─ selfcheck_manager.py
   └─ utils.py
````

Do not add extra top-level files unless absolutely necessary.
If you add anything, keep it minimal and explain why.

---

# Write `AGENTS.md` with This Exact Content

```md
🧠 AUTONOMOUS MEMORY AGENT SYSTEM (FOR CODEX / OPENCLAW)

You are an execution-focused AI agent with persistent memory, strict control logic, and self-improving behavior.

Your goal:

- COMPLETE tasks efficiently
- MINIMIZE unnecessary actions
- AVOID instability (exec, loops, memory overload)

---

🧩 MEMORY STRUCTURE

You operate with 5 memory layers:

1. WORKING MEMORY (working.json)

- goal
- current_step
- next_action
- focus
- step_history
- step_count

2. SUMMARY MEMORY (summary.json)

- facts
- decisions
- failures
- progress

3. STRATEGY MEMORY (strategy.json)

- strategies with score + usage

4. KNOWLEDGE MEMORY (partitioned)

- programming
- science
- finance
- general

Each memory item:

- content
- tags
- importance (0~1)

5. REFLECTION MEMORY (reflection.json)

- insights (behavior improvements)

---

⚙️ CORE EXECUTION LOOP

Follow STRICT order:

1. LOAD working memory
2. SELECT best strategy (highest score)
3. CHECK step repetition:
   - if repeated ≥2 → force new approach
4. APPLY retrieval cooldown:
   - do NOT retrieve within 2 steps
5. ROUTE memory:
   - choose ONE partition only
6. RETRIEVE top_k=3 only
7. APPLY attention budget:
   - working ≤400 tokens
   - retrieved ≤600 tokens
8. BUILD context
9. INJECT:
   - strategy
   - failures
   - top insights
10. EXECUTE current step directly
11. UPDATE memory:

- step_history
- step_count
- last_action
- next_action

12. SCORE strategy:

- success → +0.1
- failure → -0.2

13. LOG failures if any
14. EVERY 3 steps:

- perform reflection

---

🚫 HARD RULES (NON-NEGOTIABLE)

- NEVER use exec()
- NEVER use eval()
- NEVER generate dynamic execution code
- NEVER loop on same step
- NEVER retrieve full memory
- NEVER exceed attention budget
- ALWAYS produce usable output
- ALWAYS move forward

---

🧠 MEMORY ROUTER

Select ONE:

- programming → code, bugs, dev
- science → math, physics, logic
- finance → money, trading, economy
- general → everything else

---

🧹 MEMORY CLEANING

Trigger if:

- memory too large
- noise high

Actions:

- delete importance < 0.3
- merge duplicates
- boost frequently used memory

---

🔁 SELF-REFLECTION

Every 3 steps, analyze:

- what worked
- what failed
- what to avoid
- what to improve

Store 1 insight:

- short
- actionable
- high value

---

🎯 BEHAVIOR MODEL

You are NOT a chatbot.

You are:

- a task executor
- a memory optimizer
- a strategy learner

---

🔥 PRIORITY ORDER

1. Complete task
2. Stay stable
3. Minimize memory usage
4. Improve future performance

---

⚠️ FAILURE PREVENTION

If unsure:

- do simplest valid action
- DO NOT fallback to exec
- DO NOT stall

---

✅ OUTPUT STYLE

- Direct
- Minimal
- Actionable
- No unnecessary explanation

---

END SYSTEM
```

---

# Required Default JSON Files

## `memory/working.json`

```json
{
  "goal": "Build a stable minimal memory system for OpenClaw using Python and JSON.",
  "current_step": "Initialize memory files and managers",
  "next_action": "Create modular memory components",
  "focus": "stability and simplicity",
  "step_history": [],
  "step_count": 0,
  "last_action": "",
  "retrieval_cooldown_until": 0,
  "knowledge_write_cooldown_until": 0,
  "last_partition": "",
  "last_strategy": "",
  "last_query": "",
  "last_result_keys": [],
  "mode": "normal",
  "last_health": 1.0,
  "evolution_budget": {
    "max_suggestions_per_10_steps": 2,
    "max_patches_per_20_steps": 1,
    "disable_patch_after_failures": 2,
    "patch_failures": 0,
    "last_patch_step": 0
  }
}
```

## `memory/summary.json`

```json
{
  "facts": [],
  "decisions": [],
  "failures": [],
  "progress": [],
  "anti_patterns": []
}
```

## `memory/strategy.json`

```json
{
  "strategies": [
    {
      "name": "direct_execution",
      "description": "Do the simplest valid next action directly",
      "score": 1.0,
      "usage": 0,
      "last_used_step": 0,
      "when_to_use": ["obvious_next_step", "low_uncertainty"]
    },
    {
      "name": "decompose_task",
      "description": "Break task into smaller steps",
      "score": 0.8,
      "usage": 0,
      "last_used_step": 0,
      "when_to_use": ["complex_task", "high_uncertainty"]
    },
    {
      "name": "fallback_simplify",
      "description": "Reduce complexity and choose minimal working path",
      "score": 0.7,
      "usage": 0,
      "last_used_step": 0,
      "when_to_use": ["repetition", "failure_recovery"]
    }
  ]
}
```

## `memory/reflection.json`

```json
{
  "insights": []
}
```

## `memory/selfcheck.json`

```json
{
  "checks": [],
  "evaluations": [],
  "optimizations": [],
  "patch_proposals": [],
  "applied_patches": [],
  "last_run": ""
}
```

## `memory/meta.json`

```json
{
  "rules": [
    {
      "rule": "Only store high-value reusable knowledge",
      "confidence": 1.0,
      "last_validated_step": 0
    },
    {
      "rule": "Never retrieve more than top 3 items",
      "confidence": 1.0,
      "last_validated_step": 0
    },
    {
      "rule": "Avoid repeated steps",
      "confidence": 1.0,
      "last_validated_step": 0
    },
    {
      "rule": "Prefer direct execution when next action is obvious",
      "confidence": 1.0,
      "last_validated_step": 0
    },
    {
      "rule": "Reduce memory growth whenever possible",
      "confidence": 1.0,
      "last_validated_step": 0
    }
  ],
  "patterns": [
    {
      "pattern": "After repeated failure, switch strategy",
      "confidence": 1.0,
      "last_validated_step": 0
    },
    {
      "pattern": "Avoid frequent knowledge writes",
      "confidence": 1.0,
      "last_validated_step": 0
    },
    {
      "pattern": "Use summary instead of knowledge when possible",
      "confidence": 1.0,
      "last_validated_step": 0
    }
  ],
  "constraints": [
    "Keep memory small",
    "Keep retrieval fast",
    "Keep disk usage low",
    "Keep evaluation lightweight",
    "Prefer parameter tuning over code patching"
  ],
  "evaluation_rules": [
    "If duplicate ratio rises, prefer cleaning over new learning",
    "If retrieval effectiveness drops, reduce retrieval frequency and clean the active partition",
    "If a strategy is overused without strong success, diversify",
    "If memory pressure rises, prioritize compression and deletion over storage"
  ]
}
```

## Knowledge partitions

Each of these files must start as:

### `memory/knowledge/programming.json`

### `memory/knowledge/science.json`

### `memory/knowledge/finance.json`

### `memory/knowledge/general.json`

```json
{
  "items": [],
  "index": {}
}
```

---

# Phase A — Implement the New Memory Kernel

Implement the modules below with the exact responsibilities described.

---

## `core/utils.py`

Implement:

* `ensure_file(path, default_data)`
* `load_json(path)`
* `save_json(path, data)`
* `now_iso()`
* `clamp(value, min_value, max_value)`
* `unique_preserve_order(items)`
* `normalize_text(text)`
* `compact_step_label(text)`

Requirements:

* use `pathlib`, `json`, `datetime`, `re`
* use type hints
* add docstrings for public functions
* `ensure_file` creates parent directories if needed
* `load_json` returns parsed JSON
* `save_json` writes UTF-8 pretty JSON
* `now_iso` returns ISO string
* `normalize_text` lowercases, strips, and collapses whitespace
* `compact_step_label` turns a step into a short repetition-friendly label

---

## `core/memory_manager.py`

Implement class `MemoryManager`.

Methods:

* `initialize()`
* `load_working()`
* `save_working(data)`
* `load_summary()`
* `save_summary(data)`
* `load_strategy()`
* `save_strategy(data)`
* `load_reflection()`
* `save_reflection(data)`
* `load_selfcheck()`
* `save_selfcheck(data)`
* `load_meta()`
* `save_meta(data)`
* `load_partition(partition)`
* `save_partition(partition, data)`
* `append_summary(section, text, max_items=50)`
* `add_knowledge(partition, content, tags, importance, current_step_count=0)`
* `update_working_step(current_step, next_action, focus, last_action="")`
* `knowledge_write_allowed(working)`
* `mark_knowledge_write_used(working)`

Requirements:

* create missing files automatically
* validate partitions strictly
* append_summary ignores empty text
* summary sections stay capped at 50
* normalize tags with `unique_preserve_order`
* clamp importance to `[0.0, 1.0]`

Knowledge items must be stored as:

```json
{
  "content": "...",
  "tags": ["..."],
  "importance": 0.8,
  "created_at": "...",
  "last_accessed_step": 0,
  "access_count": 0,
  "tokens": ["..."],
  "key": "..."
}
```

Knowledge write rules:

* write only if content is useful and reusable
* reject if normalized content is too short (`<20 chars`)
* reject if meaningful token count `<3`
* reject if current step is before `knowledge_write_cooldown_until`
* after a successful write, set cooldown to `step_count + 2`
* compress content if too long
* target content length should be around `<=120 chars` when practical
* generate a compact key from useful tokens
* prevent exact duplicates
* prevent near-duplicates if token overlap `>0.7`
* keep code deterministic and simple

Partition format must remain:

```json
{
  "items": [...],
  "index": {...}
}
```

Index rules:

* token -> list of item indices
* each item contributes only a few useful tokens to the index (max 5)
* do not index stopwords

---

## `core/router.py`

Implement:

* `select_partition(text: str) -> str`

Rules:

* programming for `code, bug, python, memory, dev, function, class, json, module`
* science for `math, physics, logic, theorem, proof`
* finance for `money, market, stock, trading, economy`
* general otherwise

Requirements:

* choose exactly one partition
* deterministic
* lowercase keyword matching
* priority: `programming > science > finance > general`

---

## `core/retriever.py`

Implement:

* `tokenize(text)`
* `compute_overlap_score(query_tokens, item)`
* `retrieve_top_k(partition_data, query, k=3)`
* `retrieval_allowed(working)`
* `mark_retrieval_used(working)`
* `touch_retrieved_items(items, step_count)`
* `rebuild_index(partition_data)`

Rules:

* retrieve from one partition only
* top_k default is 3
* under pressure / convergence mode, top_k may be reduced to 2
* if `step_count < retrieval_cooldown_until`, do not retrieve
* after retrieval, set cooldown to `step_count + 2`
* deterministic lexical retrieval only
* use stopwords
* use stored item tokens and key
* use partition index first
* fallback to scan only if needed

Scoring formula:

```text
score =
  tag_overlap * 3 +
  token_overlap * 1.5 +
  key_overlap * 2 +
  importance +
  access_bonus
```

Where:

```text
access_bonus = min(access_count * 0.05, 0.3)
```

Additional rules:

* query tokenization must be simple and deterministic
* do not mutate original items except through `touch_retrieved_items`
* sort descending by score, then importance, then created_at
* prefer shorter reusable items when scores are similar
* if a very strong match is found early, allow early return
* never retrieve full partition into context
* return selected item dicts only

Cache rules:

* if current query is very similar to `last_query` and `last_result_keys` are still valid, allow simple reuse
* keep cache logic minimal

---

## `core/strategy_manager.py`

Implement:

* `select_best_strategy(strategy_data, current_step="", last_strategy=None, force_new=False, step_count=0)`
* `update_strategy_score(strategy_data, strategy_name, success)`

Rules:

* highest effective score wins
* if `force_new=True`, avoid `last_strategy` if possible
* prefer strategies not used very recently
* success => `+0.1`
* failure => `-0.2`
* clamp score to `[0.1, 3.0]`
* increment usage consistently
* update `last_used_step` on selection

Selection guidance:

* `direct_execution` when next step is obvious
* `decompose_task` for complex or uncertain tasks
* `fallback_simplify` after repetition or failure

If strategy not found during update, do nothing.

---

## `core/reflection_manager.py`

Implement:

* `should_reflect(step_count)`
* `generate_reflection_insight(working, summary)`
* `store_reflection(reflection_data, insight, max_items=20)`

Rules:

* reflect every 3 steps
* inspect recent history only
* store only 1 short actionable insight per reflection
* avoid duplicates
* keep newest insights
* cap total insights at 20
* keep reflection concise

Possible deterministic insights:

* avoid repeated retrieval when recent context is enough
* prefer direct execution when next action is obvious
* simplify after repeated failure
* change strategy after repeated step labels

---

## `core/cleaner.py`

Implement:

* `needs_cleaning(partition_data)`
* `clean_partition(partition_data, current_step_count=0)`
* `light_compress_summary(summary_data)`

Rules:

* clean if item count `>100`
* or if more than 30% of items have importance `<0.3`
* or if partition exceeds hard cap 120 items
* remove items with importance `<0.3`
* remove items never accessed and stale
* remove items with `access_count == 0` after enough steps
* merge duplicate content
* merge near-duplicates by high token overlap
* keep highest-value duplicate
* boost importance by `+0.05` up to `1.0` if `access_count >= 3`
* decay importance for long-unused items
* compress long content
* rebuild index after cleaning

Summary compression rules:

* sections should stay compact
* if a section exceeds 50 items, keep newest 30 plus highest-value 20 if practical
* anti_patterns should also remain short
* keep implementation deterministic and small

---

## `core/executor.py`

Implement:

* `detect_repetition(step_history, current_step, next_action)`
* `build_context(working, strategy, summary, reflections, retrieved_items, meta)`
* `execute_step(context)`

Rules:

* repetition detection checks last 5 history items
* repeated `>=2` counts as repetition
* use compact step labels when useful
* build minimal dict-based context
* include only essential working fields
* include selected strategy name
* include last few failures only
* include top reflections only
* include retrieved item contents only
* include only a small subset of meta rules/patterns
* keep context tiny

`execute_step` must be:

* deterministic
* no LLM
* always return usable output in this format:

```json
{
  "success": true,
  "output": "...",
  "new_fact": "...",
  "decision": "...",
  "failure": ""
}
```

Behavior:

* if current_step is empty, initialize it
* otherwise complete current step and move to next minimal improvement
* never stall
* never return all fields empty
* keep outputs short and actionable

---

## `core/selfcheck_manager.py`

This module is the **lightweight evaluation + selfcheck + repair + micro-evolution controller**.

Implement:

* `run_self_check(working, summary, strategy_data, reflection_data, partition_data_map)`
* `evaluate_health(current_check, previous_check=None)`
* `generate_optimization_suggestions(check_report, health_report, working, max_suggestions=2)`
* `generate_patch_proposals(check_report, health_report, working)`
* `apply_safe_patch_proposals(base_dir, proposals, working)`
* `store_selfcheck(selfcheck_data, report, health_report, suggestions, proposals, max_items=30)`

Purpose:

* detect whether the system is getting healthier or worse
* generate short low-risk optimization suggestions
* allow only tiny guarded self-modifications
* keep evaluation extremely lightweight

Self-check must inspect only these core metrics:

* `memory_pressure`
* `duplicate_ratio`
* `low_importance_ratio`
* `strategy_skew`
* `retrieval_effectiveness`
* `disk_usage_bytes`
* optional compact `complexity_score`

Do **not** add large textual analysis.

Health report must stay small, like:

```json
{
  "health": 0.74,
  "delta": -0.05,
  "pressure": 0.42,
  "noise": 0.12,
  "complexity": 0.38
}
```

Important rules:

* evaluation must be numeric and compact
* evaluation results must **not** be injected into executor context
* evaluation changes behavior, not prompt size
* suggestions must be short, deterministic, and few
* max suggestions per 10 steps must respect `evolution_budget`

Examples of good suggestions:

* `clean programming partition soon`
* `reduce knowledge write frequency`
* `fallback_simplify is overused`
* `summary progress section is growing too quickly`

Patch proposal rules:

* patching is optional, not mandatory
* prefer meta/rule tuning first
* prefer parameter tuning second
* only then allow tiny code patches
* only allowed target files:

  * `core/retriever.py`
  * `core/cleaner.py`
  * `core/strategy_manager.py`
  * `core/executor.py`
* proposals must be threshold-level or constant-level only
* allowed examples:

  * adjust `top_k` within `[2, 4]`
  * adjust cooldown values by at most 1
  * adjust summary caps by at most 10
  * adjust cleaner threshold slightly
* proposals must not rewrite architecture
* proposals must not change schema
* proposals must not add dependencies

Guarded self-modification rules:

* only apply a proposal if all are true:

  1. proposal type is allowlisted
  2. diff is small and localized
  3. syntax remains valid
  4. `python main.py` still runs
  5. change is recorded in `selfcheck.json`
* if any check fails, do not apply
* never apply more than 1 patch in a single run
* if patch failures reach the configured limit, disable auto patching
* if 3 consecutive patches show no meaningful improvement, stop auto patching and keep suggestions only

The selfcheck system must also support modes:

* `normal`
* `stability`
* `convergence`

Mode rules:

* if health drops too much, enter `stability`
* if complexity / pressure is too high, enter `convergence`
* if health recovers, return to `normal`

Mode behavior guidance:

### Stability mode

* reduce retrieval frequency
* force simpler strategy preference
* clean sooner
* reduce knowledge writes

### Convergence mode

* stop knowledge growth temporarily
* compress summary aggressively
* reduce top_k to 2
* disable patch proposals for that cycle
* prioritize shrinking and stabilizing over learning

---

## `main.py`

Create a runnable demo loop for one full execution cycle.

Flow:

1. initialize memory
2. load working / summary / strategy / reflection / selfcheck / meta
3. choose partition from goal + focus + current_step
4. detect repetition
5. select strategy
6. retrieve top-k if cooldown allows
7. build context
8. execute one step
9. update working memory
10. append summary entries
11. update strategy score
12. add reusable knowledge if useful
13. reflect if step_count hits multiple of 3
14. clean partition if needed
15. every 5 steps run light summary compression
16. every 5 steps run self-check + evaluation
17. generate very small optimization suggestions
18. optionally generate guarded patch proposals
19. apply at most one safe proposal if allowed and budget permits
20. save everything
21. print concise result

Working memory update rules after successful execution:

* append compact current_step label to step_history
* increment step_count
* set last_action = current_step
* set current_step = next_action
* set next_action = `"Review results and continue with the next minimal improvement"`

Keep step_history capped to latest 20 items.

Additional rules:

* store selected partition in `working["last_partition"]`
* store selected strategy in `working["last_strategy"]`
* persist retrieval cooldown
* if repetition detected, force strategy diversification
* if execution fails, still log failure and move to the simplest valid next action
* keep behavior deterministic
* do not write excessive knowledge
* prefer summary for ordinary progress, knowledge only for reusable facts

Approximate attention-budget behavior:

* only essential working fields
* retrieved_items max 3
* reflections max 3
* failures max 3
* only a few meta rules/patterns
* keep strings concise

Knowledge storage policy:

* store only if `new_fact` is non-empty and reusable
* route to the selected partition
* derive tags from:

  * selected partition
  * current focus
  * simple current_step keywords
* keep tags short and readable
* prefer importance `0.8` for stable reusable facts
* prefer importance `0.6` for ordinary but useful knowledge
* do not spam knowledge

Critical token rule:

* selfcheck and evaluation outputs must not be added to execution context
* they only influence mode, thresholds, and repair behavior

---

# Phase A Acceptance Criteria

Before moving to migration, verify all of the following:

1. all requested files exist
2. `AGENTS.md` content matches exactly
3. all JSON files exist with correct default structure
4. `python main.py` runs successfully
5. one full execution cycle completes
6. working memory updates correctly
7. strategy score updates correctly
8. retrieval cooldown persists
9. knowledge write cooldown persists
10. reflection triggers correctly on step multiples of 3
11. cleaner works on knowledge partitions
12. partition index is rebuilt and persisted
13. selfcheck runs and stores output correctly
14. evaluation runs and stores health output correctly
15. patch proposals are guarded and auditable
16. final Phase A output prints:

* created file tree
* short explanation of each module
* how to run the demo

Do not begin migration before Phase A is fully implemented and verified.

---

# Phase B — Discover, Clean, and Migrate Legacy Memory

Only after Phase A is complete and runnable, inspect the repository and reorganize legacy memory into the new system.

## Step B1 — Discover legacy memory sources

Scan the repository and identify all possible legacy memory sources, such as:

* old JSON memory files
* markdown notes
* summaries
* reflections
* planning docs
* scratchpads
* logs
* historical task notes
* previous memory systems
* prior summaries and decisions

Before migrating anything, produce a short inventory of all legacy memory sources found.

## Step B2 — Show inventory and mapping before migration

Before editing migrated memory, print:

1. list of legacy sources found
2. proposed mapping of each useful source into exactly one destination

Possible destinations:

* `memory/working.json`
* `memory/summary.json`
* `memory/strategy.json`
* `memory/reflection.json`
* `memory/selfcheck.json`
* `memory/meta.json`
* `memory/knowledge/programming.json`
* `memory/knowledge/science.json`
* `memory/knowledge/finance.json`
* `memory/knowledge/general.json`

Do not skip this step.

## Step B3 — Classification rules

Classify each useful piece into exactly one destination.

Rules:

* active current task state -> `working.json`
* durable facts / decisions / failures / progress -> `summary.json`
* reusable execution patterns -> `strategy.json`
* short behavior improvements -> `reflection.json`
* self-audit / tuning observations -> `selfcheck.json`
* durable system rules / operating rules -> `meta.json`
* reusable domain knowledge -> one knowledge partition only

Do not scatter the same item across many files unless absolutely necessary.

## Step B4 — Transform and compress

During migration:

* remove useless or empty memory
* merge duplicates
* keep highest-value version
* compress long text into concise reusable memory
* preserve important decisions
* preserve important failures
* remove verbose clutter when concise form is enough
* do not invent facts
* if unclear, keep in the safest minimal location or flag for review

## Step B5 — Knowledge migration format

Each migrated knowledge item must be stored as:

```json
{
  "content": "...",
  "tags": ["..."],
  "importance": 0.0,
  "created_at": "...",
  "last_accessed_step": 0,
  "access_count": 0,
  "tokens": ["..."],
  "key": "..."
}
```

Route each knowledge item into exactly one partition.

Routing policy:

* programming -> code, bugs, python, memory systems, dev, functions, classes, json
* science -> math, physics, logic, theorem, proof
* finance -> money, markets, stock, trading, economy
* general -> everything else

## Step B6 — Reflection migration rules

For `reflection.json`:

* keep only short actionable high-value insights
* remove vague reflections
* remove repeated reflections
* keep it concise

## Step B7 — Strategy migration rules

For `strategy.json`:

* preserve only reusable strategies
* initialize score / usage / last_used_step sanely if missing
* do not create too many strategies
* keep them practical and reusable

## Step B8 — Working memory migration rules

For `working.json`:

* keep only current active state
* do not dump historical backlog into working memory
* step_history should remain small and current
* prefer present actionability over archival completeness

## Step B9 — Selfcheck / meta migration rules

For `selfcheck.json`:

* keep only recent useful audit records
* preserve recurring optimization observations if actionable
* remove noisy repetitive checks
* keep patch proposals only if still relevant
* cap stored records so file stays compact

For `meta.json`:

* preserve only durable operating rules and useful recurring patterns
* remove vague advice
* keep rule count small
* keep confidence fields sane

## Step B10 — Final cleaning pass

After migration:

* deduplicate again
* remove low-value noise
* rebuild all partition indexes
* compress summary if needed
* compress selfcheck if needed
* keep everything small, stable, and inspectable

---

# Final Deliverables

After everything is complete, output:

1. created file tree
2. short explanation of each module
3. how to run the demo
4. Phase A verification results
5. legacy memory sources found
6. proposed mapping shown before migration
7. migration report:

   * what moved where
   * what was merged
   * what was discarded
   * why
8. selfcheck / evaluation / repair / micro-evolution report
9. final memory structure summary
10. any assumptions made
11. any ambiguous items needing manual review

---

# Final Execution Style

* work step by step
* directly modify repository files
* run the code and verify behavior
* keep implementation small and practical
* prefer the simplest valid solution
* be explicit about ambiguity
* do not preserve junk just because it exists
* do not stop at planning

---

# Final Safety Rule

Do not create an uncontrolled self-editing system.

This must remain a **guarded, auditable, deterministic, low-token, low-disk memory kernel** with **limited** self-check, repair, evaluation, and micro-evolution ability.

The final system must be able to run for a long time **because it stays small, clean, and stable**, not because it keeps adding complexity.

