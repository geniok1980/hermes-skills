# ClawHost Improvement TZ — Example: Competitor-Driven Product Upgrade

This is a real ТЗ produced during a session where the user asked to improve their existing project (ClawHost) to match a competitor (MyClaw.ai).

**Pattern:** 1) Research competitor site → 2) Compare feature-by-feature → 3) Write ТЗ with MoSCoW → 4) Delegate implementation to Gemini CLI

## Key characteristics of this ТЗ

| Aspect | What it demonstrates |
|--------|---------------------|
| Scope | Improving an existing project, not building from scratch |
| Source material | Direct competitor site (myclaw.ai) — hero, skills marketplace, pricing, testimonials |
| Output | Single markdown document with phases, file paths, DB schema, API spec |
| Implementation | Delegated to Gemini CLI (external agent) after writing |
| Structure | MoSCoW priorities, phased roadmap, visual references section |

## Document structure used

1. Общая концепция — context + tech stack
2. Ключевые отличия — structured comparison table (Competitor | Current | Action)
3. Функциональные модули — 7 modules with detailed specs
4. Приоритеты по MoSCoW — Must / Should / Could
5. API спецификация — new endpoints
6. База данных — CREATE TABLE statements
7. Файловая структура — exact file paths for new/modified files
8. Этапы разработки — 4 phases with day estimates
9. Визуальный референс — description of competitor's visual patterns
10. Инфраструктура — deployment targets
11. Риски — honest assessment

## What worked well

- **Competitor comparison table** (3 columns: Competitor | Current | Action) made gaps immediately visible
- **File-level granularity** in the spec (exact component paths, new files) made delegation trivial
- **Self-contained prompt** for Gemini CLI included i18n keys, lint commands, and code conventions
- **Docker volume mounts** meant changes were live immediately after the CLI finished — no redeploy needed
- **MoSCoW prioritization** kept Phase 1 focused and achievable

## Full document

See `/root/clawhost/clawhost-improvement-tz.md` for the complete 20KB ТЗ.
