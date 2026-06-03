---
name: technical-specifications
description: "Write product-level technical specifications (ТЗ): research open-source alternatives, compare approaches, design architecture, plan modules, integrate payments, define infrastructure."
version: 1.2.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [specification, architecture, research, planning, documentation, product-design]
    related_skills: [writing-plans, plan, spike]
---

# Technical Specification Writing (ТЗ)

## Overview

Write comprehensive product-level technical specifications — the kind that sits between the user's idea and a code-level implementation plan. This is a **what-to-build** document (ТЗ/техзадание), not a **how-to-implement** one (that's `writing-plans`).

**Core principle:** Answer the question "what exactly are we building and why this way" so completely that any developer can estimate it, any stakeholder can understand it, and any subsequent implementation plan has all the context it needs.

## When to Use

- User describes a product idea and asks "find me a starting point" or "write a spec"
- User asks "can we build X" and you need to evaluate approaches before committing
- Before implementing any non-trivial product feature with external integrations (payments, AI APIs, auth)
- Any time you're writing a .md file that describes system architecture, not code

**Do NOT use for:**
- Code-level task breakdowns (use `writing-plans` instead)
- Quick throwaway experiments (use `spike` instead)
- Refactoring existing code

## Workflow

### Phase 1: Research Open-Source Alternatives

> **Methodology note:** For general GitHub search patterns, API usage, trending discovery, and SaaS evaluation methodology, see the `github-research` skill. What follows is the spec-specific evaluation process tailored to AI/product projects.

When the user wants to find a project to build on:

**1. Search GitHub from multiple angles**

GitHub's search is picky — long queries return 0 repos. Use short, specific queries:

```markdown
Good:  "ai photo background replacement"  → often 0 results
Better: "virtual photobooth"              → often 0 results
Better: search known repos directly:      → InstantID, PhotoMaker, PuLID, FaceFusion
```

Strategy when search fails:
- Think of **well-known projects** in the domain and visit them directly (e.g., github.com/TencentARC/PhotoMaker)
- Search by **technology name** (e.g., "InstantID", "IP-Adapter", "PhotoMaker")
- Search by **problem component** (e.g., "face swapping github", "identity preservation stable diffusion")
- Use **DuckDuckGo/Google** as a fallback to find blog posts listing alternatives

**2. Evaluate each candidate systematically**

For each repo, note:
- **Stars** — rough popularity signal
- **Description** — is it actually solving the right problem?
- **README** — does it have a demo? Gradio app? Web UI?
- **Last commit** — is it actively maintained?
- **Framework** — Python (FastAPI/Gradio/ComfyUI) or other
- **License** — can you build a commercial product on it?
- **Integration path** — does it have a REST API? Can it be called from Bun/Node?

**3. Present a structured comparison**

Group by tiers of fit:
```
🥇 Tier 1 (perfect fit) — solves the exact problem, has a web UI
🥇 Tier 2 (great fit)  — solves the problem with minor adaptation
💪 As framework       — good as a foundation/backend to build on
🧱 As building block  — useful as a component within a larger system
```

**4. Make a recommendation with reasoning**

Don't just list — pick one and explain WHY it's the best starting point for THIS user's stack and skill level.

### Phase 2: Competitor / Reference Site Analysis

When the user says "add features like this site" or "look at X and tell me what we can add":

**1. Survey the competitor's full feature surface**

Use the browser tools to explore every section:
- Landing page value prop
- Step-by-step user flow (upload → select → result)
- Pricing / monetization model
- Differentiators (speed, quality, templates, integrations)
- Categories or presets offered
- Technical signals (API-based? Client-side rendering? Video generation?)

**2. Map features to existing project**

Create a structured comparison table:
```markdown
| Aidentika Feature | Our Project | Gap |
|---|---|---|
| Product photo generation | ❌ Missing | NEW — core feature |
| Infographics overlay | ❌ Missing | NEW — Phase 2 |
| Spark currency | Has `balance_generations` | UPGRADE — virtual currency |
```

**3. Prioritize (MoSCoW method)**

| Priority | Feature | Rationale |
|----------|---------|-----------|
| **Must** | Product photography mode | Core differentiator — opens e-commerce market |
| **Should** | Spark system | More flexible monetization |
| **Could** | AI video | Differentiator, but complex |

**4. Research integration details**

For each priority feature, research:
- **AI prompts** — inspect the competitor's UX to infer prompt patterns (concept names, categories)
- **Pricing** — capture their exact tiers and map to existing payment system
- **API needs** — what new endpoints and database tables are needed

**5. Write the spec**

Structure the spec per the template below, with one section per priority feature. Include:
- New database tables (CREATE TABLE statements)
- New API endpoints (method, path, request/response shapes)
- Prompt engineering templates (stored in DB, not hardcoded)
- Frontend page/component plan
- Pricing tables mapped from the competitor

**Key principle:** All prompts and templates must be stored in the database, not hardcoded — admins should be able to edit them later.

Before writing the spec, research any payment gateways, AI APIs, or third-party services the user mentioned:

**Payment systems:**
- Search for SDK availability (GitHub, npm, PyPI)
- Check language compatibility (User uses Bun/Node → needs JS/TS SDK)
- Note pricing model and sandbox availability
- Check integration pattern (redirect-based, inline, webhook)

**AI APIs/Models:**
- Check OpenRouter for model availability and pricing
- Check if it's a local model (needs GPU) or API-based (serverless)
- Compare cost per generation/request
- Note infrastructure implications

### Phase 3: Evaluate Architecture Approaches

When there's a choice between two approaches, present a structured comparison:

```
### 🔴 Approach A: [Name]

What it involves:
- Pro ✅
- Pro ✅
- Con ❌ (cost/complexity/risk)

### 🟢 Approach B: [Name]

What it involves:
- Pro ✅
- Pro ✅
- Con ❌

### Recommendation

Why B is better for THIS user's specific situation.
```

At a minimum, compare:
- **Infrastructure cost** (GPU/serverless)
- **Setup complexity** (Docker/Python vs HTTP API)
- **Scalability** (how does it handle 100 concurrent users)
- **Maintenance burden** (who keeps the models updated)
- **Alignment with existing stack** (TypeScript monorepo vs adding Python)

### Phase 4: Write the Specification

#### Document Structure

```markdown
# Техническое задание: [Product Name]

## 1. Общая концепция

[1-2 paragraphs describing the product, the base project chosen,
the tech stack, and the architecture in one diagram]

## 2. Архитектура системы

ASCII architecture diagram showing:
- Frontend → Backend → External services
- Data flow for the core user action
- Integration points

## 3. Пользовательские роли

### 3.1. Гость
### 3.2. Зарегистрированный пользователь
### 3.3. Администратор

## 4. Функциональные модули

For each module:
- **User flow** (numbered steps from user perspective)
- **Technical requirements** (formats, limits, storage)
- **Example data** (pricing tables, prompt examples, config snippets)

## 5. API спецификация

```
GET    /api/resource       — Description
POST   /api/resource       — Description
```

Show request/response shapes for the most important endpoints.

## 6. База данных

Core tables with CREATE TABLE statements. Include:
- Primary keys (UUID TEXT)
- Foreign keys with REFERENCES
- Timestamps
- Indexes

## 7. Интеграции

For each external service (payment, AI, auth):
- How it connects (SDK/API/REST)
- Code example showing the actual integration
- Sandbox vs production configuration
- Webhook handling pattern

## 8. Этапы разработки

```
### Phase N: [Name] (X-Y weeks)
- [ ] Task 1
- [ ] Task 2
```

Phases should be:
1. **MVP** — core functionality, minimum viable
2. **Monetization** — payments, packages, user accounts
3. **Admin/Management** — dashboards, CRUD, logs
4. **Enhancements** — nice-to-haves, optimizations

## 9. Инфраструктура

- Minimum hardware requirements (CPU/GPU/RAM/disk)
- Deployment targets (Vercel, VPS, Docker)
- File storage (local/S3/R2)
- CI/CD

## 10. Риски и ограничения

Honest assessment of:
- Maintenance risk (unmaintained upstream projects)
- Cost risk (GPU, API calls)
- Quality risk (model limitations)
- Legal risk (GDPR, image rights)
```

#### Writing Principles

1. **Be specific** — not "integrates with payment system" but shows `WataPayApi` code
2. **Be opinionated** — recommend a specific approach, don't just list options
3. **Be realistic** — include risks, costs, and limitations
4. **Stack-aware** — tailor to the user's existing tech stack (monorepo, Bun, React, etc.)
5. **Complete** — the spec should be enough for a dev to start building without asking questions

#### Save the Document

Save to the user's project directory:
```bash
# User has a monorepo — save there
/path/to/monorepo/product-name-tz.md
```

## Post-Spec: Delegate Implementation

After writing and saving the spec, ask the user if they want implementation started. Two paths:

### Path A: Hermes Subagents (`delegate_task`)

Use when the implementation touches the current project's codebase. See `subagent-driven-development` skill for the full workflow (fresh subagent per task, two-stage review).

### Path B: External Agent CLI (Gemini CLI, Codex CLI, Claude Code)

Use when the user explicitly asks for a specific CLI or when the task is well-scoped and the user has a CLI installed.

**How to delegate to an external CLI:**

1. **Write a self-contained prompt file** — craft a prompt that includes:
   - The relevant spec sections (phases, file paths, API endpoints, DB schema)
   - Project code conventions (import rules, naming, linting)
   - Exact file paths to create/modify
   - Verification steps (`bun run lint`, `bun run build`)
   - Constraints and DON'Ts

2. **Launch the CLI in headless mode:**
   ```
   # Gemini CLI
   /path/to/gemini -p "$(cat prompt.md)" --approval-mode yolo

   # Codex CLI
   codex -p "$(cat prompt.md)"

   # Claude Code
   claude -p "$(cat prompt.md)" --allowedTools
   ```
   Note: for Gemini CLI, use `--approval-mode yolo` (NOT `-y --approval-mode yolo` — they conflict).

3. **Verify the output** — after the CLI exits:
   - Check that expected files were created (`git diff --stat`)
   - Run the project's linter/tests
   - If using Docker with volume mounts, check the container has picked up changes

4. **Fallback** — if the CLI exits with no output, no files created, or compilation errors after 5+ minutes, switch to Hermes `delegate_task` subagents (see `subagent-driven-development` for the fallback pattern).

**Key differences between paths:**

| Aspect | Hermes subagents | External CLI |
|--------|-----------------|--------------|
| Parallelism | Up to 3 concurrent tasks | Serial (one CLI instance) |
| Output | Structured summaries returned | Raw terminal output |
| Review gates | Built-in (spec + quality review) | None — must verify manually |
| File creation | Reliable across all task types | May stall on complex multi-file tasks |
| Best for | Multi-file, multi-step features | Single-focused implementation waves |

**Pitfalls when delegating to external CLI agents:**

1. **i18n drift (multilingual projects):** External agents typically only update the reference language file (`en.ts`). The translation type (`TranslationKey`) is auto-derived from `en.ts`, so the build will pass for English. But ALL other language files will be missing the new keys, causing TS errors. After delegation, always run `bun run build` and fix i18n for non-English languages.

2. **Unescaped single quotes in translated strings:** When auto-generating translations for languages that use apostrophes extensively (French: `l'IA`, Italian: `l'intero`, Turkish: `AI'ya`), the agent may produce single-quoted TS strings containing unescaped single quotes. This breaks compilation silently (TS parser sees a string closer). For each affected language file, either:
   - Remove the apostrophe (preferred: `l AI` instead of `l'AI`)
   - Or switch the string to double-quoted delimiters (`"..."`) if the file already uses that pattern for some values
   
   Scan for this after delegation: `grep -n "'[^']*'" file.ts | grep -v "^\s*//"` — any line with >2 single quotes on a value line needs fixing.

3. **Docker volume mount verification:** If the project runs in Docker with volume mounts (dev mode), the external CLI writes files to the host filesystem. Docker's bind mounts reflect them live only if the paths match. After delegation, verify inside the container: `docker exec <container> ls -la <path>`. If files are missing, restart the container or rebuild.

4. **Barrel export missed:** New components created by the agent may not be added to the project's barrel index files (`index.ts`). After delegation, check that all new components are re-exported from the right barrel files.

### Keeping the spec in sync

If the implementation reveals spec gaps (missing endpoints, wrong field names, unhandled edge cases), update the ТЗ file immediately — the spec is the source of truth for the feature, not the code. Add a `## Changelog` section at the bottom to track post-spec corrections.

## The No-GPU Pivot Pattern

A recurring pattern in AI product specs: user assumes they need a local GPU model, but a serverless API (OpenRouter, Replicate, fal.ai) can replace it entirely.

### How to detect

Signals that a no-GPU pivot may work:
- User says "find me a project to build on" about an AI feature
- The core operation is: upload image → transform → show result
- Input is a photo of a person, output is a photo of that person in a new scene
- User has a Bun/Node.js/TypeScript stack (adding Python is expensive)

### How to present

Don't just dismiss the local approach — present a structured comparison:

```markdown
### 🔴 Approach A: Local GPU (InstantID + SDXL)

- ❌ Needs RTX 3090/4090 ($2000+ or $200-500/mo rental)
- ❌ Docker + CUDA + Python infra
- ❌ Queue, error handling, GPU monitoring
- ✅ Full control over model, prompt, parameters

### 🟢 Approach B: OpenRouter API (serverless)

- ✅ No GPU needed — Bun→HTTPS→OpenRouter
- ✅ $0.0000015/image (pennies for thousands of images)
- ✅ Instant scaling, no infra
- ❌ Less control over face fidelity
- ❌ Dependency on external API

### Recommendation

For this user (TypeScript monorepo, Bun stack, no GPU setup):
→ Approach B. The 99.9% cost reduction and zero infra outweigh the API dependency.
```

### What happens after the pivot

The architecture changes dramatically:

| Before (GPU) | After (API) |
|---|---|
| Python FastAPI server | Node/Bun HTTP call |
| Docker + CUDA | Zero containers |
| Queue (Redis/Bull) | Synchronous request |
| RTX 3090 | Any $5 VPS |
| 10-30s per image | 2-5s per image |

Update the TZ accordingly:
- Remove Python AI Engine section
- Replace with OpenRouter service code
- Simplify infrastructure requirements
- Update cost estimates (GPU rental → API costs)
- Note that the entire stack is now TypeScript/Bun only

## Common Mistakes

### Over-engineering Phase 1

**Bad:** "Let's build a custom solution from scratch"  
**Good:** Research what exists, pick the closest fit, plan to extend it

### Missing the "No GPU" path

**Bad:** Assuming local GPU is the only option  
**Good:** Check if there's an API alternative (OpenRouter, Replicate, fal.ai) that avoids infrastructure entirely

### Omitting pricing/packages

The user almost always wants to monetize. Include a pricing table even if approximate.

### Architecture without code examples

**Bad:** "We'll integrate WATA Pay"  
**Good:** Show the actual `createLink()` call with real parameters

### Only one approach

When there are meaningful tradeoffs (GPU vs API, Python vs TS), present both sides so the user can make an informed choice.

## Reference Files

This skill ships with reference files in `references/`:

| File | Contents |
|------|----------|
| `references/ai-face-preservation-projects.md` | Curated list of open-source projects for face-preserving image generation (InstantID, PhotoMaker, PuLID, etc.) — stars, descriptions, fit tiers |
| `references/wata-pay-integration.md` | WATA Pay SDK setup, API methods, sandbox mode, webhook handling, code examples for Bun/Hono |
| `references/openrouter-nanobanana-generation.md` | OpenRouter API for serverless image gen, Nano Banana approach, pricing, integration pattern, location prompt library |
| `references/example-ai-photostudio-tz.md` | Complete ТЗ for an AI PhotoStudio platform — v2 (OpenRouter/no-GPU). Demonstrates the full spec workflow from research through economics. |
| `references/example-aidentika-competitor-analysis-tz.md` | Competitor analysis TZ for adding Aidentika-style product photography to an existing project. Shows competitive mapping, MoSCoW, DDL design, and prompt engineering. |
| `references/example-clawhost-competitor-improvement-tz.md` | Competitor-driven product improvement ТЗ (ClawHost → MyClaw.ai). Demonstrates: 3-column competitor gap analysis, file-level implementation spec, phased roadmap, and delegation to Gemini CLI for execution. |
| `references/i18n-post-agent-sync.md` | Post-delegation i18n sync: fixing structural mismatches across 14 language files after agent-driven code changes. Covers detection, Python bulk-fix strategy, single-quote-in-string pitfalls, and verification. |

Consult these when the spec involves AI image generation or payment integration.

## Related Skills

- `writing-plans` — use AFTER this skill to break the spec into code-level implementation tasks
- `plan` — use to save the spec in plan mode without executing
- `spike` — use to validate technical assumptions before writing the spec
