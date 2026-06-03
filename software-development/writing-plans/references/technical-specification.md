# Technical Specification (Техническое Задание / ТЗ)

## When to Write a TZ

Write a technical specification when the user asks for:
- "Сделай техзадание" / "напиши ТЗ"
- "Architecture proposal" / "technical design doc"
- "План разработки платформы"
- Requirements involving payment integration, admin panels, multi-user auth

A TZ is a higher-level document than an implementation plan. It describes **what** to build and **why**, not the step-by-step **how**. The implementation plan comes after the TZ is approved.

## TZ Document Structure

### 1. Header
```
# Техническое задание: [Project Name] (v2)

## 1. Общая концепция
One paragraph describing the product. Core user value proposition.
What problem it solves. Target audience.

**Key technology choices** (brief):
- AI Engine: OpenRouter API — google/gemini-*-flash-image-preview
- Payments: WATA Pay SDK (wata-pay)
- Stack: React/Vite + Hono.js/Bun + SQLite
```

### 2. Архитектура системы
ASCII architecture diagram showing:
- Frontend → Backend → External APIs
- Database
- Payment flow
- Data flow for core operation (e.g., photo upload → generation → result)

### 3. Пользовательские роли
- **Гость** — what unregistered users can do
- **Зарегистрированный пользователь** — what registered users can do
- **Администратор** — admin panel features

### 4. Функциональные модули

#### 4.N. Module Name
**User Flow:** Step-by-step what the user does and what the system does.

**Technical requirements:**
- Formats, sizes, limits
- Storage approach
- API endpoints needed

**Example seed data** (e.g., default locations, tariff plans)

### 5. API Спецификация
Grouped by domain:
```
### 5.1. Auth
POST /api/auth/register
POST /api/auth/login

### 5.2. Core Feature
POST /api/generate
GET  /api/generate/:id
```

### 6. База Данных
```sql
CREATE TABLE users (
  id TEXT PRIMARY KEY,
  email TEXT UNIQUE,
  ...
);
```

### 7. Интеграции (детали)
For each third-party integration, document:
- SDK/library name and npm package
- Sandbox vs production
- Key API methods with real TypeScript code
- Webhook handling
- Environment variables needed

### 8. Этапы Разработки (Phases)

| Phase | Duration | What's included |
|-------|----------|-----------------|
| Phase 1: MVP | 1-2 weeks | Core feature, basic auth |
| Phase 2: Monetization | 1 week | Payments, tariffs |
| Phase 3: Admin | 1 week | Admin panel, analytics |
| Phase 4: Polish | Ongoing | Improvements, extras |

### 9. Инфраструктура

| Component | Technology | Cost |
|-----------|------------|------|
| Frontend | Vercel / Cloudflare | Free |
| Backend | VPS with Bun | $5-10/mo |
| AI | OpenRouter API | Pay-as-you-go |
| Payments | WATA Pay | Per-transaction fee |

### 10. Экономика Проекта
Revenue projection table:
- Package prices
- Estimated sales volume
- Infrastructure costs
- Margin calculation

### 11. Риски
List of technical and business risks with mitigation.

## Comparison: TZ vs Implementation Plan

| Aspect | TZ (this document) | Implementation Plan |
|--------|-------------------|-------------------|
| Scope | Whole platform / major feature | Single feature / sprint |
| Reader | Stakeholder, investor, developer | Developer (agent) |
| Detail | Architecture, API, DB schema | Exact code, test commands, steps |
| Changes | Iterated on feedback | Executed as-written |
| Output | Approved document → next phase | Working code |

## When to Update vs Create from Scratch

- **New project with existing stack** → adapt a previous TZ's structure
- **New project, new stack** → write from scratch
- **Phase iteration** → add section to existing TZ
- **Pivot (e.g., local GPU → serverless API)** → rewrite affected sections, keep structure
