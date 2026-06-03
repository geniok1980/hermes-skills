---
name: writing-plans
description: "Write implementation plans: bite-sized tasks, paths, code."
version: 1.1.0
author: Hermes Agent (adapted from obra/superpowers)
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [planning, design, implementation, workflow, documentation]
    related_skills: [subagent-driven-development, test-driven-development, requesting-code-review]
---

# Writing Implementation Plans

## Overview

Write comprehensive implementation plans assuming the implementer has zero context for the codebase and questionable taste. Document everything they need: which files to touch, complete code, testing commands, docs to check, how to verify. Give them bite-sized tasks. DRY. YAGNI. TDD. Frequent commits.

Assume the implementer is a skilled developer but knows almost nothing about the toolset or problem domain. Assume they don't know good test design very well.

**Core principle:** A good plan makes implementation obvious. If someone has to guess, the plan is incomplete.

## When to Use

**Always use before:**
- Implementing multi-step features
- Breaking down complex requirements
- Delegating to subagents via subagent-driven-development

**Don't skip when:**
- Feature seems simple (assumptions cause bugs)
- You plan to implement it yourself (future you needs guidance)
- Working alone (documentation matters)

## Bite-Sized Task Granularity

**Each task = 2-5 minutes of focused work.**

Every step is one action:
- "Write the failing test" — step
- "Run it to make sure it fails" — step
- "Implement the minimal code to make the test pass" — step
- "Run the tests and make sure they pass" — step
- "Commit" — step

**Too big:**
```markdown
### Task 1: Build authentication system
[50 lines of code across 5 files]
```

**Right size:**
```markdown
### Task 1: Create User model with email field
[10 lines, 1 file]

### Task 2: Add password hash field to User
[8 lines, 1 file]

### Task 3: Create password hashing utility
[15 lines, 1 file]
```

## Plan Document Structure

### Header (Required)

Every plan MUST start with:

```markdown
# [Feature Name] Implementation Plan

> **For Hermes:** Use subagent-driven-development skill to implement this plan task-by-task.

**Goal:** [One sentence describing what this builds]

**Architecture:** [2-3 sentences about approach]

**Tech Stack:** [Key technologies/libraries]

---
```

### Task Structure

Each task follows this format:

````markdown
### Task N: [Descriptive Name]

**Objective:** What this task accomplishes (one sentence)

**Files:**
- Create: `exact/path/to/new_file.py`
- Modify: `exact/path/to/existing.py:45-67` (line numbers if known)
- Test: `tests/path/to/test_file.py`

**Step 1: Write failing test**

```python
def test_specific_behavior():
    result = function(input)
    assert result == expected
```

**Step 2: Run test to verify failure**

Run: `pytest tests/path/test.py::test_specific_behavior -v`
Expected: FAIL — "function not defined"

**Step 3: Write minimal implementation**

```python
def function(input):
    return expected
```

**Step 4: Run test to verify pass**

Run: `pytest tests/path/test.py::test_specific_behavior -v`
Expected: PASS

**Step 5: Commit**

```bash
git add tests/path/test.py src/path/file.py
git commit -m "feat: add specific feature"
```
````

## Writing Process

### Step 1: Understand Requirements

Read and understand:
- Feature requirements
- Design documents or user description
- Acceptance criteria
- Constraints

### Step 2: Explore the Codebase

Use Hermes tools to understand the project:

```python
# Understand project structure
search_files("*.py", target="files", path="src/")

# Look at similar features
search_files("similar_pattern", path="src/", file_glob="*.py")

# Check existing tests
search_files("*.py", target="files", path="tests/")

# Read key files
read_file("src/app.py")
```

### Step 3: Design Approach

Decide:
- Architecture pattern
- File organization
- Dependencies needed
- Testing strategy

### Step 4: Write Tasks

Create tasks in order:
1. Setup/infrastructure
2. Core functionality (TDD for each)
3. Edge cases
4. Integration
5. Cleanup/documentation

### Step 5: Add Complete Details

For each task, include:
- **Exact file paths** (not "the config file" but `src/config/settings.py`)
- **Complete code examples** (not "add validation" but the actual code)
- **Exact commands** with expected output
- **Verification steps** that prove the task works

### Step 6: Review the Plan

Check:
- [ ] Tasks are sequential and logical
- [ ] Each task is bite-sized (2-5 min)
- [ ] File paths are exact
- [ ] Code examples are complete (copy-pasteable)
- [ ] Commands are exact with expected output
- [ ] No missing context
- [ ] DRY, YAGNI, TDD principles applied

### Step 7: Save the Plan

```bash
mkdir -p docs/plans
# Save plan to docs/plans/YYYY-MM-DD-feature-name.md
git add docs/plans/
git commit -m "docs: add implementation plan for [feature]"
```

## Principles

### DRY (Don't Repeat Yourself)

**Bad:** Copy-paste validation in 3 places
**Good:** Extract validation function, use everywhere

### YAGNI (You Aren't Gonna Need It)

**Bad:** Add "flexibility" for future requirements
**Good:** Implement only what's needed now

```python
# Bad — YAGNI violation
class User:
    def __init__(self, name, email):
        self.name = name
        self.email = email
        self.preferences = {}  # Not needed yet!
        self.metadata = {}     # Not needed yet!

# Good — YAGNI
class User:
    def __init__(self, name, email):
        self.name = name
        self.email = email
```

### TDD (Test-Driven Development)

Every task that produces code should include the full TDD cycle:
1. Write failing test
2. Run to verify failure
3. Write minimal code
4. Run to verify pass

See `test-driven-development` skill for details.

### Frequent Commits

Commit after every task:
```bash
git add [files]
git commit -m "type: description"
```

## Common Mistakes

### Vague Tasks

**Bad:** "Add authentication"
**Good:** "Create User model with email and password_hash fields"

### Incomplete Code

**Bad:** "Step 1: Add validation function"
**Good:** "Step 1: Add validation function" followed by the complete function code

### Missing Verification

**Bad:** "Step 3: Test it works"
**Good:** "Step 3: Run `pytest tests/test_auth.py -v`, expected: 3 passed"

### Missing File Paths

**Bad:** "Create the model file"
**Good:** "Create: `src/models/user.py`"

## Execution Handoff

After saving the plan, offer the execution approach:

**"Plan complete and saved. Ready to execute using subagent-driven-development — I'll dispatch a fresh subagent per task with two-stage review (spec compliance then code quality). Shall I proceed?"**

When executing, use the `subagent-driven-development` skill:
- Fresh `delegate_task` per task with full context
- Spec compliance review after each task
- Code quality review after spec passes
- Proceed only when both reviews approve

## Competitor-Driven Technical Specification

When the user asks to analyze a competitor's product and backport features to their own project, use this workflow:

**Trigger phrases:** "посмотри что есть на [site]", "look at [competitor] and add similar", "сделай как на [site]"

### Workflow: Competitor Analysis → TZ → Agent Implementation

```
User: "посмотри что есть на [site.com/] и предложи что мы можем добавить"
  ↓
Step 1: Browse the competitor site (browser_navigate + scroll + snapshots)
  - Homepage: value prop, 3-step flow, pricing
  - Feature pages: AI Try-On, Video, specific tools
  - Pricing page: tiers, currency system, unit economics
  - FAQ / technical details if accessible
  ↓
Step 2: Map features to current project
  - Read current project structure (routes, DB schema, frontend pages, API endpoints)
  - For each competitor feature decide:
    - **Direct port** (same concept, adapt UI) — easiest
    - **Adapted port** (different domain but similar UX pattern) — medium
    - **New paradigm** (completely new capability) — hardest
  - Use MoSCoW priority: Must / Should / Could / Won't
  ↓
Step 3: Write the TZ (follow `references/technical-specification.md` structure)
  - Cover: DB schema, API routes, frontend pages, prompt engineering, pricing
  - Include concrete prompt templates the competitor likely uses
  - Include pricing table with competitor's actual prices
  - For each feature, specify: acceptance criteria, file paths, code examples
  ↓
Step 4: Create GitHub Issue with the TZ as body
  - Labels: `enhancement`, `agent-ready`, appropriate agent label
  - The Issue body IS the TZ (agents read it, not an attached file)
  ↓
Step 5: Trigger agent implementation
  - GitHub Actions workflow (if repo has one)
  - Local Gemini CLI launch (terminal background + notify_on_complete)
  - Or delegate_task to subagent with TZ context
```

### Competitor Analysis Techniques

**Site reading order** (what to capture):
1. **Landing page** — headline, value prop, how-it-works steps
2. **Feature pages** (AI Try-On, AI Video, etc.) — detailed screens, examples
3. **Pricing** — tier names, prices, units (images, videos, compute credits), currency system
4. **FAQ** — edge cases, limitations, user expectations
5. **Tech signals** — what AI model they likely use (check /robots.txt, /sitemap.xml, page meta, JS bundle hints, CDN patterns)

**What to capture in notes:**
- Exact pricing (with currency symbols)
- Step-by-step user flow (upload → choose → generate → enhance)
- Prompt template patterns (infer from examples on the site)
- Category/taxonomy structures they use
- Any mobile app vs web-only signals

### Feature Mapping to Existing Codebase

When mapping features from a site to your project, read these files first:

```
# Understand the current capabilities
apps/api/src/db/schema.sql     -- current tables
apps/api/src/index.ts          -- current routes
apps/web/src/App.tsx           -- current pages/routes  
apps/web/src/lib/api.ts        -- current API client methods
```

Then for each new feature, determine:
- Does it need new tables? → list them with full SQL
- Does it extend existing tables? → list ALTER TABLE statements
- Does it need new routes? → list endpoint method + path + response shape
- Does it need new frontend pages? → list component hierarchy

### TZ → Issue Handoff

The GitHub Issue body should be **self-contained** (agents read it directly):

```markdown
## 🎯 Goal: [One-liner]

Inspired by [competitor.com](URL) — add [feature summary] to our project.

### Phase N: [Feature Name]

**Database changes:**
```sql
CREATE TABLE ... ;
ALTER TABLE ... ADD COLUMN ... ;
```

**API:**
| Method | Path | Description |
|--------|------|-------------|
| POST | /api/feature | Create |

**Frontend:**
- New page: `apps/web/src/pages/FeaturePage.tsx`
- New component: `apps/web/src/components/FeatureComponent.tsx`
- Route: `/app/feature`

**Prompt templates** (store in DB, not hardcoded):
- `template_name`: "Prompt with {placeholders}"

**Acceptance Criteria:**
- [ ] Criterion 1
- [ ] Criterion 2

### Technical Constraints
- Stack stays the same
- Follow existing code patterns
- All prompts in DB, not hardcoded
```

### Real-World Example

See `references/aidentika-product-photography-tz.md` for a complete TZ from session that added Product Photography, Infographics, and Spark Currency to an existing AI photo app, inspired by Aidentika.com. This demonstrates:
- Competitor site analysis (browser_navigate → feature extraction)
- Full DB schema design (7 new tables)
- Prompt template engineering for e-commerce photography
- Spark virtual currency pricing table
- Infographic canvas editor spec
- 3-phase implementation plan with agent handoff

## Business & Financial Plans

The `writing-plans` skill also covers **business/financial plans** — revenue roadmaps, income targets, and growth strategies. These differ from code implementation plans in structure and audience.

### When to Use

- User asks for "план выхода на доход N" / "financial plan" / "income plan"
- User wants a structured roadmap with revenue targets per vertical
- Building a monetisation strategy across multiple business lines

### Structure for Income / Revenue Plans

```markdown
# План выхода на доход N ₽/мес

**Дата:** [month year]
**Статус:** Стратегический план

---

## 🎯 Цель

Выйти на стабильный ежемесячный доход **N ₽**

---

## 💰 Структура дохода (целевая)

| Направление | Цель ₽/мес | Доля |
|---|---|---|
| 🏪 **Vertical 1** | N ₽ | N% |
| 📊 **Vertical 2** | N ₽ | N% |
| **ИТОГО** | **N ₽** | **100%** |

---

## [Vertical 1]: [Description]

### Что предлагать
- Bullet list of offerings
- Per service / per client pricing

### Каналы продаж
- How to find clients
- Marketing channels

### Масштабирование
- Subscription model vs one-off
- Unit economics

### KPI
- [ ] Checkbox tasks for this vertical

---

## [Vertical 2]: [Description]
...

---

## 📅 Дорожная карта

### Месяц 1 — Фундамент
- [ ] Step-by-step actions

### Месяц 2 — Первые результаты
- [ ] ...

### Месяц 3–6 — Рост
- [ ] ...

### Месяц 7–12 — Цель
- [ ] ...

---

## 🚀 Ключевые риски

| Риск | Решение |
|---|---|
| Risk 1 | Mitigation |
| Risk 2 | Mitigation |

---

## 📌 Ближайшие шаги (сегодня-завтра)

1. Immediate actionable items
2. ...

```

### Key Differences from Code Plans

| Aspect | Code Implementation Plan | Business / Income Plan |
|---|---|---|
| **Audience** | Developer implementing code | Yourself (strategy) |
| **Tasks** | Bite-sized (2-5 min) | Month-level phases |
| **Verification** | Tests passing | KPI checkboxes |
| **Output** | Working code | Revenue, clients |
| **Granularity** | Per function/test | Per revenue vertical |

### Tip: Map to User's Verticals

When building an income plan for a multi-skill freelancer/consultant:
1. List each service/product line as a separate revenue vertical
2. Assign a realistic monthly target based on market rates
3. Include both active income (projects, one-off) and passive/recurring (subscription, maintenance)
4. Always include a risks table — especially regulatory (e.g., crypto restrictions) and seasonal (e.g., restaurant slow months)

---

## Further Reading / References

### Technical Specifications

For platform-level design documents (ТЗ / техническое задание) — architecture, API specs, database schema, pricing, infrastructure, economics — load `references/technical-specification.md`. This is a higher-level document than an implementation plan; it describes **what** to build before planning **how**.

### When to Load

- User asks for "техзадание" / "ТЗ" / "technical specification"
- Project involves multiple services, payments, or third-party integrations
- Building a SaaS or platform, not just a feature

**Important:** When the user says "ТЗ" or "техзадание", FIRST load the `technical-specifications` skill (it has the competitor analysis workflow, MoSCoW prioritization, no-GPU pivot pattern, and complete reference examples). Then load this `writing-plans` skill for the document structure. The two are complementary: the skill drives the discovery/analysis phase, writing-plans provides the output template.

> ⚠️ Pain point from session 2026-05-24: agent loaded writing-plans on a "напиши ТЗ" request but skipped `technical-specifications`. This caused missing the WATA Pay reference, competitor analysis patterns, and the Aidentika TZ example. Load BOTH for a ТЗ task.
- Building a SaaS or platform, not just a feature

Load the reference, follow its structure, then proceed to writing-plans for execution planning.

## Remember

```
Bite-sized tasks (2-5 min each)
Exact file paths
Complete code (copy-pasteable)
Exact commands with expected output
Verification steps
DRY, YAGNI, TDD
Frequent commits
```

**A good plan makes implementation obvious.**
