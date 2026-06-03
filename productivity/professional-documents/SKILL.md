---
name: professional-documents
description: "Write CVs, resumes, cover letters, and professional profiles for Евгений (geniok). Captures formatting preferences, must-include sections, and style rules."
version: 1.0.0
author: geniok
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [resume, cv, documents, writing, russian, professional]
---

# Professional Documents

Write formal professional documents (CV/resume, cover letter, service descriptions) for Евгений. Use when the user asks for a resume, CV, professional profile, or cover letter.

## Formatting Rules

- **NO pipe tables** (`| col1 | col2 |`) — Telegram and many email clients strip or mangle them. Use bullet lists or labeled key:value pairs instead.
- **NO emoji** in formal documents (📍📧🔗 etc). They render as boxes or hieroglyphs in some clients. Use plain text labels instead.
- Use **clean markdown** with `##` headers, `-` lists, and `**bold**` for emphasis.
- Structure: sections separated by `---` horizontal rules for scannability.
- Keep the tone professional and factual. No fluff, no self-praise clichés.

## Required Sections (Resume/CV)

1. **Header** — Full name, title line, location, phone, email, website, Telegram, GitHub
2. **About / Обо мне** — 2-3 sentence summary of core competencies
3. **Key Competencies / Ключевые компетенции** — bullet list with domain:tech pairs
4. **Experience / Опыт работы** — reverse chronological with company, role, dates, key responsibilities
5. **Projects / Проекты** — name, stack, description, link. Include: ClawHost, RKDash, AI Photostudio, FreqDash, SMCBOT, Skills catalog, Freqtrade Strategies, UDAFF VPN
6. **Tech Stack** — grouped by category (languages, frameworks, databases, infrastructure, AI/ML, tools)
7. **Education** — institution, year, degree
8. **Certifications** — if any
9. **Languages** — Russian (native), English (technical)
10. **Links** — geniok.ru, GitHub, Telegram, email

## Data Sources

- User profile in memory (`user` target) — name, location, contact, preferences
- Memory entries (`memory` target) — platform credentials, project URLs, server info
- geniok.ru site — live portfolio and projects
- GitHub profile (github.com/geniok1980) — repos, bio

## Style Reference

For this user, write in **Russian** unless asked otherwise. Be direct and factual. The resume should sound like an experienced technical lead/engineer, not a junior. Highlight the 20+ years of experience in restaurant automation (rkeeper, iiko), full-stack development, trading bots, AI agents, and DevOps.

## References

- `references/resume-template.md` — Full resume template with all sections
