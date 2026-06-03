# Example: Aidentika Competitor Analysis TZ (AI PhotoStudio)

> Written during session 2026-05-24. Context: User's ai-photostudio project (personal portrait generator) needed to add features from Aidentika.com (product photography for e-commerce).

## Analysis Method

1. **Browser-surveyed** Aidentika.com — all sections: landing, how-it-works, AI try-on, video, pricing, FAQs
2. **Audited** existing project codebase — db schema, routes, frontend pages, services
3. **Mapped** features side-by-side
4. **Prioritized** with MoSCoW
5. **Wrote** full TZ with SQL DDL, API routes, prompt templates, and pricing tables

## Key Decisions

- **Prompts stored in DB**, not hardcoded — `concepts.prompt_template` column with `{product_description}` placeholder
- **Mode-based architecture** — `generation_modes` table (portrait/product) with separate concepts per mode
- **Spark virtual currency** — replaces `balance_generations` with universal tokens (4 sparks/image)
- **3 concept types** adapted from Aidentika: catalog_shot, on_model, composition
- **7 product categories** with tailored presets

## Pricing (mirrored from Aidentika)

| Plan | Price | Sparks | Images |
|------|-------|--------|--------|
| Старт | 390₽ | 50 | 12 |
| Креатор | 990₽ | 140 | 35 |
| Студия | 2,490₽ | 400 | 100 |
| Бизнес | 6,490₽ | 1,200 | 300 |

## Pattern: Competitive Feature Mapping

When a user asks "add features like SITE_X":

```
1. Browse SITE_X comprehensively → list every feature section
2. Audit existing project codebase → list every capability
3. Build gap matrix: SITE_X feature → existing? → priority (Must/Should/Could)
4. Research integration specifics (APIs, pricing, prompts)
5. Write TZ with:
   - New DDL (tables + columns)
   - New API endpoints (method + path + shapes)
   - Prompt templates (with placeholders, stored in DB)
   - Frontend components/pages
   - Updated pricing tables
   - Phase plan (atomic per-feature phases)
6. Create GitHub Issue → agent-ready label → implement
```
