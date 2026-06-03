# Real-World Example: Aidentika-Style Features TZ

> **When this was used:** May 2026 — user asked "посмотри что есть на https://aidentika.com/ и предложи что мы можем добавить"
> **Project:** TypeScript monorepo (React/Vite + Hono/Bun + SQLite + OpenRouter)
> **Original:** Inspired by Aidentika.com — AI product photography for e-commerce
> **Outcome:** GitHub Issue #4 created → Gemini CLI agent dispatched

## What the TZ Covered

| Section | Content |
|---------|---------|
| Overview | Current state (portrait AI gen), goal (dual-mode: portrait + product), MoSCoW priorities |
| Product Photography | 3 new DB tables, 5 API endpoints, new frontend page, prompt templates |
| Infographics | Canvas editor component, 3 templates, render API |
| Spark Currency | Virtual currency table, 4 pricing tiers, cost-per-action matrix |
| Category Presets | 7 product categories with tailored prompt hints |
| Implementation Plan | 3 phases with ~17 step-level tasks |
| Acceptance Criteria | 8 checkboxes covering all features |
| Technical Notes | Stack constraints, code conventions, file structure |

## TZ Structure Template

### 1. Общее описание (Overview)
```
## 1. Общее описание
### 1.1 Текущее состояние
Brief what the project does now + tech stack.
### 1.2 Цель
What we're building, referencing the competitor.
### 1.3 Приоритет (MoSCoW)
| Priority | Feature | Description |
|----------|---------|-------------|
| **Must** | Core feature | Why |
| **Should** | Nice-to-have | Why |
| **Could** | Future | Why |
```

### 2. Feature Sections (one per major feature)

Each feature section follows this pattern:

```
## N. Feature Name

### N.1 Концепция
One paragraph describing what this feature does from the user's perspective.

### N.2 База данных
Full CREATE TABLE and/or ALTER TABLE SQL statements.
Every column documented inline with comments.

### N.3 API endpoints
| Method | Path | Description |
|--------|------|-------------|
| GET | /api/feature | What it returns |

### N.4 Frontend
New components, pages, routes needed.

### N.5 Prompt Engineering (for AI features)
Exact prompt templates with {placeholders}.
Note: all prompts stored in DB, not hardcoded.
```

### 3. План реализации (Implementation Plan)

```
### Фаза N: Feature Name (Priority)

**Шаги:**
1. Create [table]
2. Create [route]
3. Register in [index.ts]
4. Create [frontend component]
5. Update [App.tsx routes]
```

### 4. Acceptance Criteria (Checklist)

```
- [ ] Criterion 1
- [ ] Criterion 2
```

### 5. Technical Notes

```
### Текущий стек (не менять)
- Runtime: Bun
- Backend: Hono.js
- Frontend: React + Vite + TailwindCSS
- DB: SQLite (bun:sqlite)
- AI: OpenRouter → specific model
- Payments: WATA Pay

### Соглашения (соблюдать)
- Import style (relative / @-aliases)
- Component patterns
- CSS approach
- Where prompts/templates are stored
```

## Key Prompt Templates (from this TZ)

```
catalog_shot:
  "Product photography of {description}. Clean white background, studio lighting,
   professional catalog shot, high detail, 8K, centered composition"

on_model:
  "Product photography of {description}. Being held by a person, lifestyle shot,
   natural lighting, realistic, professional e-commerce"

composition:
  "Artistic composition of {description} with complementary props, flat lay style,
   warm lighting, premium product photography"
```

## Pricing Table Pattern

```
| Plan | Price | Units (Sparks) | Images | Video |
|------|-------|----------------|--------|-------|
| Старт | 390₽ | 50 | 12 | 3 |
| Креатор | 990₽ | 140 | 35 | 8 |
| Студия | 2,490₽ | 400 | 100 | 25 |
| Бизнес | 6,490₽ | 1,200 | 300 | 75 |
```

## What Worked Well

1. **Browser-first competitor analysis** — navigating Aidentika.com with browser_navigate/scroll/snapshot gave structured data (pricing, steps, categories) that was easy to map
2. **MoSCoW prioritization** — helped scope the TZ to what was feasible (Must = product photography + infographics, Could = video)
3. **Self-contained Issue body** — putting the full TZ in the GitHub Issue body meant the agent (Gemini CLI) could work from it directly without opening external files
4. **Phase-by-phase branching** — splitting into 3 phases made the work parallelizable and reviewable
