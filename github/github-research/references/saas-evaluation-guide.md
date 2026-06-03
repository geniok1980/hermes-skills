# SaaS Evaluation Guide

## Methodology for assessing open-source → SaaS potential

### The 5-question framework

For each candidate project, answer:

1. **What concrete job does it do?**
   - Library? Tool? CLI? Framework? Platform?
   - If it's already a hosted/SaaS product → skip immediately

2. **What's the wrapping layer?**
   - Managed hosting: deploy + maintain + scale for customers
   - API wrapper: expose CLI/library functions as REST endpoints
   - Platform: add auth, billing, team collaboration, dashboards
   - Premium features: add missing layers (monitoring, SSO, audit logs)

3. **Who pays and how much?**
   - Individual devs → $5–19/mo (low willingness)
   - Small teams → $29–99/mo (moderate)
   - Enterprise/Research → $149–999+/mo (high)
   - Per-use billing only works for compute-heavy workflows

4. **What's the competitive moat?**
   - Network effects (templates, community, integrations)
   - Data accumulation (usage patterns, training data)
   - Switching costs (integrations, team workflows)
   - Performance/cost advantage not replicable by competitors

5. **Can it be built in < 3 months by a small team?**
   - If yes → fast to MVP but easy to copy. Bet on execution + GTM
   - If no → harder to build but harder to compete. Bet on tech moat

### Monetization model selection guide

| Project type | Recommended model | Typical pricing |
|---|---|---|
| AI/ML tool or agent | Freemium + usage tiers | $0–29/mo individual, $99–499/mo team |
| Developer tool / CLI | Freemium → team seats | $9/mo individual, $49–149/mo team |
| Data processing pipeline | Pay-per-use (per GB/min) | $0.05–0.50/unit, volume discounts |
| API wrapper | Pay-per-call + tiered | $0.001–0.01/call, 10K free/mo |
| Hosted platform (managed infra) | Tiered by resources | $29–999/mo |
| Enterprise compliance/security | Per-seat enterprise | $99–299/user/mo, min 20 seats |

### Real project → SaaS mapping examples

| Open-source project | SaaS product | Wrapping layer | Target customer |
|---|---|---|---|
| FigMirror (graph styling) | "Canva for scientific figures" | Web UI + cloud API | Researchers, grad students |
| CCGlass (agent proxy) | "Datadog for AI agents" | Cloud dashboard + agent | Tech leads, DevOps |
| FlashLib (ML operators) | "Serverless sklearn" | REST API + auto-scaling | ML engineers, analysts |
| AV-Curator (video pipeline) | "Video cleaning service" | Web upload + cloud processing | ML teams, media archives |
| GSD-redux (agent mgmt) | "AI dev orchestration platform" | Cloud orchestrator + UI | Engineering teams, CTOs |
| Kimi-code (agent framework) | "Managed agent hosting" | Cloud infra + dashboard | Enterprise AI teams |

### Filters for quick triage

**Skip these project types (hard to SaaS-wrap):**
- Pure learning/educational repos (courses, tutorials)
- Personal configs, dotfiles, userstyles
- Art projects, wallpapers, fan games
- Low-code/no-code builders that would require building a full platform
- Databases and storage engines (too complex to manage)

**Prioritize these project types (good SaaS fit):**
- CLI tools that do a single thing well (wrap as API)
- Data processing pipelines (charge per job/volume)
- AI/ML model tools and agent frameworks (charge per inference/token)
- Code generation or analysis tools (wrap as web IDE or API)
- Monitoring/debugging/profiling tools (SaaS layer = dashboard + alerts)
- File/media format converters, validators, optimizers
