---
name: subagent-driven-development
description: "Execute plans via delegate_task subagents (2-stage review)."
version: 1.2.0
author: Hermes Agent (adapted from obra/superpowers)
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [delegation, subagent, implementation, workflow, parallel]
    related_skills: [writing-plans, requesting-code-review, test-driven-development]
---

# Subagent-Driven Development

## Overview

Execute implementation plans by dispatching fresh subagents per task with systematic two-stage review.

**Core principle:** Fresh subagent per task + two-stage review (spec then quality) = high quality, fast iteration.

## When to Use

Use this skill when:
- You have an implementation plan (from writing-plans skill or user requirements)
- Tasks are mostly independent
- Quality and spec compliance are important
- You want automated review between tasks

**vs. manual execution:**
- Fresh context per task (no confusion from accumulated state)
- Automated review process catches issues early
- Consistent quality checks across all tasks
- Subagents can ask questions before starting work

## The Process

### 1. Read and Parse Plan

Read the plan file. Extract ALL tasks with their full text and context upfront. Create a todo list:

```python
# Read the plan
read_file("docs/plans/feature-plan.md")

# Create todo list with all tasks
todo([
    {"id": "task-1", "content": "Create User model with email field", "status": "pending"},
    {"id": "task-2", "content": "Add password hashing utility", "status": "pending"},
    {"id": "task-3", "content": "Create login endpoint", "status": "pending"},
])
```

**Key:** Read the plan ONCE. Extract everything. Don't make subagents read the plan file — provide the full task text directly in context.

### 2. Per-Task Workflow

For EACH task in the plan:

#### Step 1: Dispatch Implementer Subagent

Use `delegate_task` with complete context:

```python
delegate_task(
    goal="Implement Task 1: Create User model with email and password_hash fields",
    context="""
    TASK FROM PLAN:
    - Create: src/models/user.py
    - Add User class with email (str) and password_hash (str) fields
    - Use bcrypt for password hashing
    - Include __repr__ for debugging

    FOLLOW TDD:
    1. Write failing test in tests/models/test_user.py
    2. Run: pytest tests/models/test_user.py -v (verify FAIL)
    3. Write minimal implementation
    4. Run: pytest tests/models/test_user.py -v (verify PASS)
    5. Run: pytest tests/ -q (verify no regressions)
    6. Commit: git add -A && git commit -m "feat: add User model with password hashing"

    PROJECT CONTEXT:
    - Python 3.11, Flask app in src/app.py
    - Existing models in src/models/
    - Tests use pytest, run from project root
    - bcrypt already in requirements.txt
    """,
    toolsets=['terminal', 'file']
)
```

#### Step 2: Dispatch Spec Compliance Reviewer

After the implementer completes, verify against the original spec:

```python
delegate_task(
    goal="Review if implementation matches the spec from the plan",
    context="""
    ORIGINAL TASK SPEC:
    - Create src/models/user.py with User class
    - Fields: email (str), password_hash (str)
    - Use bcrypt for password hashing
    - Include __repr__

    CHECK:
    - [ ] All requirements from spec implemented?
    - [ ] File paths match spec?
    - [ ] Function signatures match spec?
    - [ ] Behavior matches expected?
    - [ ] Nothing extra added (no scope creep)?

    OUTPUT: PASS or list of specific spec gaps to fix.
    """,
    toolsets=['file']
)
```

**If spec issues found:** Fix gaps, then re-run spec review. Continue only when spec-compliant.

#### Step 3: Dispatch Code Quality Reviewer

After spec compliance passes:

```python
delegate_task(
    goal="Review code quality for Task 1 implementation",
    context="""
    FILES TO REVIEW:
    - src/models/user.py
    - tests/models/test_user.py

    CHECK:
    - [ ] Follows project conventions and style?
    - [ ] Proper error handling?
    - [ ] Clear variable/function names?
    - [ ] Adequate test coverage?
    - [ ] No obvious bugs or missed edge cases?
    - [ ] No security issues?

    OUTPUT FORMAT:
    - Critical Issues: [must fix before proceeding]
    - Important Issues: [should fix]
    - Minor Issues: [optional]
    - Verdict: APPROVED or REQUEST_CHANGES
    """,
    toolsets=['file']
)
```

**If quality issues found:** Fix issues, re-review. Continue only when approved.

#### Step 4: Mark Complete

```python
todo([{"id": "task-1", "content": "Create User model with email field", "status": "completed"}], merge=True)
```

### 3. Final Review

After ALL tasks are complete, dispatch a final integration reviewer:

```python
delegate_task(
    goal="Review the entire implementation for consistency and integration issues",
    context="""
    All tasks from the plan are complete. Review the full implementation:
    - Do all components work together?
    - Any inconsistencies between tasks?
    - All tests passing?
    - Ready for merge?
    """,
    toolsets=['terminal', 'file']
)
```

### 4. Verify and Commit

```bash
# Run full test suite
pytest tests/ -q

# Review all changes
git diff --stat

# Final commit if needed
git add -A && git commit -m "feat: complete [feature name] implementation"
```

## Task Granularity

**Each task = 2-5 minutes of focused work.**

**Too big:**
- "Implement user authentication system"

**Right size:**
- "Create User model with email and password fields"
- "Add password hashing function"
- "Create login endpoint"
- "Add JWT token generation"
- "Create registration endpoint"

## Parallel Web Research (Delegate for Discovery)

A distinct pattern from development — use `delegate_task(tasks=[...])` with `toolsets=['web']` to research multiple topics in parallel. Each subagent gets a web-capable browser and returns a curated summary.

### When to Use

- User asks "research X, Y, Z" — three topics that are independent
- Need to gather intelligence from multiple angles (market, competitors, tools, cases)
- Want to compare pricing, approaches, or technologies across sources
- Time-sensitive research where sequential searches would lag

### The Pattern

```python
delegate_task(
    context="Background context the subagent needs (user profile, constraints, language preference)",
    tasks=[
        {
            "goal": "Research topic A with specific questions",
            "toolsets": ["web"]
        },
        {
            "goal": "Research topic B with specific questions",
            "toolsets": ["web"]
        },
        {
            "goal": "Research topic C with specific questions",
            "toolsets": ["web"]
        }
    ]
)
```

### Key Rules

1. **Set `context` at the top level** — shared context (user profile, language, constraints) that applies to all tasks. This avoids repeating the same info in every task goal.
2. **Be specific in each `goal`** — include exact search terms, what to look for, what to ignore. Vague goals produce shallow results.
3. **Specify language** in the context: `"Respond in Russian"` or `"Return findings in English"`. Subagents default to English for web content even with Russian context — be explicit.
4. **Use `toolsets: ['web']`** — don't include `terminal` or `file` unless the subagent needs to save results. Web-only is lighter and faster.
5. **Accept that summaries are self-reports** — verify critical claims (URLs, specific numbers) if they sound suspect. The subagent may hallucinate references it couldn't actually load.
6. **3 is the max** — up to 3 concurrent subagents per batch. Use 3 for breadth (different angles) or fewer for depth.

### Example (from a real session)

```python
delegate_task(
    context="This is for a restaurant automation specialist (rkeeper, iiko), trading bot developer, TypeScript/Python dev. Need concrete, actionable ideas.",
    tasks=[
        {
            "goal": "Find current freelance demand in Russia for AI agents and automation in 2026. What services using AI/bots/automation are in demand on fl.ru, kwork, freelance.ru?",
            "toolsets": ["web"]
        },
        {
            "goal": "Find SaaS product ideas for restaurant business (rkeeper, iiko). What ready-made products sell well — dashboards, Telegram bots, analytics, loyalty systems?",
            "toolsets": ["web"]
        },
        {
            "goal": "Find how to sell TypeScript/Python dev skills on Upwork/Freelancer.com — what categories are in demand, what rates, what positioning works?",
            "toolsets": ["web"]
        }
    ]
)
```

### When NOT to Use

- **Mechanical multi-step work** with no reasoning needed → use `execute_code` instead
- **Single focused question** → just use the browser tool directly
- **You need to verify outputs** (file writes, API calls, remote side-effects) → use single delegate_task with `['web', 'terminal', 'file']` so you can trust the result
- **User interaction required** → subagents cannot use `clarify`

For projects with clearly separated concerns (e.g., backend vs. frontend, API vs. UI), use `delegate_task(tasks=[...])` to dispatch them in **parallel**. This dramatically speeds up full-stack development.

### How It Works

Instead of sequential fine-grained tasks, split the project by **layer**:

```
delegate_task(tasks=[
  {goal: "Build backend (API, DB, services)", context: "..."},
  {goal: "Build frontend (pages, components, routing)", context: "...")
])
```

Each subagent gets a **complete, self-contained task** — not a tiny step to execute, but a whole module to build from scratch with full file paths, exact requirements, and all constraints. The subagents work independently and return their results.

### When to Use Parallel Dispatch

| Use sequential (per-task) | Use parallel (per-layer) |
|---|---|
| Tasks touch the same files | Entirely separate codebases (apps/api vs apps/web) |
| Dependencies between tasks | Independent layers that communicate via API contract |
| Need tight spec compliance per step | High-level spec is clear and stable |
| Small project (<10 files) | Large project (20+ files per layer) |

### How to Write Context for Parallel Subagents

Each subagent context must be **self-contained** — the subagent has no memory of your conversation:

```python
delegate_task(
    tasks=[
        {
            "goal": "Build the complete backend API with routes, DB, and services",
            "context": """
            EXISTING FILES (read them first, don't recreate):
            - apps/api/package.json (deps: hono, bcrypt, jwt, wata-pay)
            - apps/api/src/db/schema.sql (tables: users, locations, packages, etc.)
            
            WRITE THESE FILES:
            - src/routes/auth.ts — POST /register, POST /login, GET /me (JWT + bcrypt)
            - src/services/openrouter.ts — calls OpenRouter API, returns image URL
            - ... (exact file paths + complete requirements)
            
            DO NOT: install packages, run the server, create files outside the specified paths
            
            CONSTRAINTS:
            - All TypeScript, all imports use workspace:* packages
            - DB uses bun:sqlite singleton
            """
        },
        {
            "goal": "Build the complete React frontend with all pages and components",
            "context": """
            EXISTING FILES:
            - apps/web/package.json (react, react-dom, react-router-dom, vite, tailwind)
            - apps/web/vite.config.ts
            
            WRITE THESE FILES:
            - src/App.tsx — React Router with all routes
            - src/pages/Landing.tsx — Hero, gallery, features, CTA
            - src/components/Navbar.tsx — Glass navbar, responsive
            - ... (exact file paths + complete requirements)
            
            CONSTRAINTS:
            - Dark theme (bg-gray-950), purple/indigo accents
            - Tailwind CSS only, no CSS-in-JS
            - All text in Russian
            """
        }
    ]
)
```

### Key Rules

1. **Each subagent gets ALL relevant context** — path to every file it needs to write, exact code requirements, constraints. The subagent should never need to guess.

2. **Use `toolsets=['file', 'terminal']`** — file access to read existing files and write new ones, terminal to run builds and verify compilation.

3. **Explicitly state DON'Ts** — "DO NOT install packages", "DO NOT modify files outside apps/web", "DO NOT run the server". Parallel subagents can interfere if not constrained.

4. **Accept that parallel subagents can't coordinate** — they each build their layer independently. The API contract between layers must be pre-defined in the task description.

### After Parallel Dispatch

Once both subagents complete:
1. **Verify integration** — run the full build (`turbo run build`) to catch cross-layer issues
2. **Test the API** — start the backend, hit an endpoint
3. **Commit everything** — `git add -A && git commit`

### Example: Full-Stack Project in One Turn

```
[User asks: build AI PhotoStudio platform]
[Dispatch parallel subagents:]
  → Backend agent: writes 14 files (routes, services, DB, middleware) → verifies bun build
  → Frontend agent: writes 16 files (pages, components, API client) → verifies vite build
[After both complete: verify turbo build, git commit, push to GitHub]
[Total: ~8 minutes for full-stack project]
```

This pattern safely bypasses the need for multi-round review cycles when layers are truly independent.

## Red Flags — Never Do These

- Start implementation without a plan
- Skip reviews (spec compliance OR code quality)
- Proceed with unfixed critical/important issues
- Dispatch multiple implementation subagents for tasks that touch the same files (use per-layer parallel instead, which works because the codebases are separate)
- Make subagent read the plan file (provide full text in context instead)
- Skip scene-setting context (subagent needs to understand where the task fits)
- Ignore subagent questions (answer before letting them proceed)
- Accept "close enough" on spec compliance
- Skip review loops (reviewer found issues → implementer fixes → review again)
- Let implementer self-review replace actual review (both are needed)
- **Start code quality review before spec compliance is PASS** (wrong order)
- Move to next task while either review has open issues

## External Agent CLI Pattern

When the user asks you to hand off development to an Agent CLI (Gemini CLI, Codex CLI, Claude Code, OpenCode), use this pattern to maximize success.

### When to use

- The user explicitly asks for a specific CLI (Gemini CLI, Codex CLI, etc.)
- The task is well-scoped with clear file paths and constraints
- You have a comprehensive spec/ТЗ written (see `technical-specifications` skill)
- The implementation is a single wave (not multi-step with review cycles)

### How to succeed

1. **Write a self-contained prompt** in a temp file — include exact file paths, code conventions, constraints, verification steps
2. **Launch in headless mode** with auto-approve:
   ```
   # Gemini CLI
   /path/to/gemini -p "$(cat prompt.md)" --approval-mode yolo
   ```
3. **Run via terminal with pty=true** — headless mode benefits from a PTY
4. **Use notify_on_complete=true** when backgrounding — the CLI may take minutes
5. **Verify after completion** — check `git diff --stat`, run linter/tests

### Signs an Agent CLI is failing

- Process runs but produces **zero stdout** for >2 minutes
- Process runs but **no files are created** after 5+ minutes
- CLI reports warnings (MCP issues, missing tools, pgrep errors) but doesn't progress
- CLI exits silently with no output or non-zero exit code

### Fallback to delegate_task

When the CLI fails or stalls:

```typescript
// INSTEAD of: agent_cli -p "big task" --yolo
// DO THIS:
const [backend, frontend] = await delegate_task(tasks: [
  {
    goal: "Build the complete backend with all routes and services",
    context: /* full file list, paths, exact requirements */
  },
  {
    goal: "Build the complete frontend with all pages and components",
    context: /* full file list, paths, exact requirements */
  }
]);
// After: verify builds, test API, git commit & push
```

### Why delegate_task beats Agent CLI in headless mode

| Aspect | Agent CLI headless | delegate_task |
|--------|-------------------|---------------|
| Output visibility | Buffered, hard to monitor | Summary returned |
| File creation | May stall on complex tasks | Direct, reliable |
| Error recovery | Session lost on error | Returns error summary |
| Parallelism | Serial (one agent CL) | Parallel (up to 3 tasks) |
| Context budget | Shared with parent | Fresh per subagent |

## Handling Issues

### If Subagent Asks Questions

- Answer clearly and completely
- Provide additional context if needed
- Don't rush them into implementation

### If Reviewer Finds Issues

- Implementer subagent (or a new one) fixes them
- Reviewer reviews again
- Repeat until approved
- Don't skip the re-review

### If Subagent Fails a Task

- Dispatch a new fix subagent with specific instructions about what went wrong
- Don't try to fix manually in the controller session (context pollution)

## Efficiency Notes

**Why fresh subagent per task:**
- Prevents context pollution from accumulated state
- Each subagent gets clean, focused context
- No confusion from prior tasks' code or reasoning

**Why two-stage review:**
- Spec review catches under/over-building early
- Quality review ensures the implementation is well-built
- Catches issues before they compound across tasks

**Cost trade-off:**
- More subagent invocations (implementer + 2 reviewers per task)
- But catches issues early (cheaper than debugging compounded problems later)

## Integration with Other Skills

### With writing-plans

This skill EXECUTES plans created by the writing-plans skill:
1. User requirements → writing-plans → implementation plan
2. Implementation plan → subagent-driven-development → working code

### With test-driven-development

Implementer subagents should follow TDD:
1. Write failing test first
2. Implement minimal code
3. Verify test passes
4. Commit

Include TDD instructions in every implementer context.

### With requesting-code-review

The two-stage review process IS the code review. For final integration review, use the requesting-code-review skill's review dimensions.

### With systematic-debugging

If a subagent encounters bugs during implementation:
1. Follow systematic-debugging process
2. Find root cause before fixing
3. Write regression test
4. Resume implementation

## Example Workflow

```
[Read plan: docs/plans/auth-feature.md]
[Create todo list with 5 tasks]

--- Task 1: Create User model ---
[Dispatch implementer subagent]
  Implementer: "Should email be unique?"
  You: "Yes, email must be unique"
  Implementer: Implemented, 3/3 tests passing, committed.

[Dispatch spec reviewer]
  Spec reviewer: ✅ PASS — all requirements met

[Dispatch quality reviewer]
  Quality reviewer: ✅ APPROVED — clean code, good tests

[Mark Task 1 complete]

--- Task 2: Password hashing ---
[Dispatch implementer subagent]
  Implementer: No questions, implemented, 5/5 tests passing.

[Dispatch spec reviewer]
  Spec reviewer: ❌ Missing: password strength validation (spec says "min 8 chars")

[Implementer fixes]
  Implementer: Added validation, 7/7 tests passing.

[Dispatch spec reviewer again]
  Spec reviewer: ✅ PASS

[Dispatch quality reviewer]
  Quality reviewer: Important: Magic number 8, extract to constant
  Implementer: Extracted MIN_PASSWORD_LENGTH constant
  Quality reviewer: ✅ APPROVED

[Mark Task 2 complete]

... (continue for all tasks)

[After all tasks: dispatch final integration reviewer]
[Run full test suite: all passing]
[Done!]
```

## Remember

```
Fresh subagent per task
Two-stage review every time
Spec compliance FIRST
Code quality SECOND
Never skip reviews
Catch issues early
```

**Quality is not an accident. It's the result of systematic process.**

## Further reading (load when relevant)

When the orchestration involves significant context usage, long review loops, or complex validation checkpoints, load these references for the specific discipline:

- **`references/context-budget-discipline.md`** — Four-tier context degradation model (PEAK / GOOD / DEGRADING / POOR), read-depth rules that scale with context window size, and early warning signs of silent degradation. Load when a run will clearly consume significant context (multi-phase plans, many subagents, large artifacts).
- **`references/gates-taxonomy.md`** — The four canonical gate types (Pre-flight, Revision, Escalation, Abort) with behavior, recovery, and examples. Load when designing or reviewing any workflow that has validation checkpoints — use the vocabulary explicitly so each gate has defined entry, failure behavior, and resumption rules.

Both references adapted from gsd-build/get-shit-done (MIT © 2025 Lex Christopherson).
