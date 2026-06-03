# GitHub → SaaS Digest Format

Template for a daily/weekly digest of trending GitHub projects evaluated for SaaS potential.

## Structure

```markdown
🚀 **GitHub Open Source → SaaS | DD.MM.YYYY**

Краткое введение: за какой период собрано, по каким языкам.

---

**N️⃣ owner/repo** ★stars
🟦 TypeScript | MIT | created DD.MM
Краткое описание проекта (1-2 предложения).

💡 **SaaS: Название идеи**
Описание SaaS-сервиса, превращающего open-source проект в managed продукт.

🎯 Кому: Целевая аудитория
💰 Монетизация: Модель и цены
```

## Translation conventions

When producing a Russian-language digest:
- Keep project names, technical terms, and repo owner/repo in original English
- Translate descriptions, SaaS ideas, and audience to Russian
- Use `★` for stars count
- Monetization section: always name the model (Freemium, Pay-per-use, Seat-based) + specific price ranges
- Maintain consistent emoji headers: 💡 🎯 💰

## Response fields per project

| Field | Content | Example |
|-------|---------|---------|
| Description | What the project does, in one sentence | "Python tool for converting files and office documents to Markdown." |
| Stars | Star count with ★ prefix | ★23 591 |
| SaaS idea | The managed product wrapping the open-source project | "Managed AI Workspace Cloud" |
| Target audience | Who would pay for this | "Teams, startups, enterprises" |
| Monetization | Pricing model + tiers | "$15–30/user/mo, freemium → team → enterprise" |

## Project selection criteria for the top-N

- **Not already a SaaS** — if the project itself is already a hosted platform, skip it
- **Real problem** — solves a recurring pain point people pay to fix
- **Wrappable** — can be offered as API hosting, managed infra, or platform
- **Paying audience** — the target segment has budget and willingness to pay
- **License-compatible** — MIT/Apache = clear path; AGPL/GPL = consult legal

## Footer: "Also trending" table

For projects that are trending but don't fit the SaaS evaluation (too niche, already commercial, educational), include a compact reference table at the bottom:

```
🔥 **Что ещё в топе (но не SaaS):**

| Проект | ★ | Причина |
|--------|---|---------|
| owner/repo | N | Explanation |
```
