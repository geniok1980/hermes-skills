---
name: openclaw-hosting-platform
description: A self-hosted cloud hosting management platform built as a TypeScript monorepo (Turborepo, Bun). React/Vite frontend with Hono.js API, shadcn/ui, Tailwind CSS. Covers design system, landing page conventions, i18n, and pricing patterns.
category: software-development
triggers:
  - "clawhost"
  - "openclaw landing"
  - "openclaw"
  - "hosting platform"
  - "agent landing"
  - "изменить лендинг clawhost"
  - "агент хостинг"
  - "monorepo landing"
---

# OpenClaw Hosting Platform — Frontend Conventions

## Project Structure

```
openclaw.anywhere/
├── apps/
│   ├── api/              # Hono.js backend API (Bun)
│   └── web/              # React + Vite frontend
├── packages/
│   ├── shared/           # @openclaw/shared — HTTP client, constants, plans, validation
│   └── i18n/             # @openclaw/i18n — 14 languages
```

## Design System

### Font Hierarchy (user's explicit preference)

| Usage | Font Class | Font Name |
|-------|-----------|-----------|
| Headings / titles | `font-clash` | Clash Display |
| Body / general text | `font-satoshi` (or default `font-sans`) | Satoshi |
| Code / badges / tags / small meta | `font-mono` | JetBrains Mono |

**FAILURE MODE to avoid**: DO NOT use `font-syne` or `font-mono` for body text. The user corrected this explicitly — Syne is not their font, Clash Display is. Body text should never be JetBrains Mono unless it's genuinely code.

Root div should always have `font-satoshi`.

### Colors

- **Background**: `#020204` (darkest) / `#0a0a0a` (landing bg)
- **Text**: `#fafafa` / `text-white/80` through `text-white`
- **Accent**: Red `#ef4444` / `#ff4d4d` (gradient: `from-red-600 to-red-500`)
- **Cards**: `#070709` or `#0d0d0d` with `border-white/[0.06-0.1]`
- **Muted text**: `text-white/30`, `text-white/40`, `text-white/50`

### V2 Design System Components

The "v2" design system lives in `apps/web/src/components/v2/`. Key components:
- `HeaderV2` — fixed dark header with nav links, login, deploy button
- `FooterV2` — dark footer with column layout
- `PricingSectionV2` — pricing grid receiving `plans` prop
- `FaqSectionV2` — accordion FAQ section
- `ScrollRevealV2` — framer-motion scroll reveal wrapper
- `SectionLabelV2` — label with `// LABEL` comment style
- `FeaturesGridV2` — feature card grid
- `ComparisonTableV2` — side-by-side comparison table

All use `font-clash` for headings (patched from `font-syne` per user preference).

### Background Effects

```tsx
<div className='v2-grain' />              {/* noise texture overlay */}
<div className='v2-grid pointer-events-none' />  {/* dot grid */}
<div className='v2-gradient pointer-events-none' /> {/* radial gradient */}
```

## Landing Page (ROUTES.HOME → V2)

The main landing page at `/` is `V2.tsx` (NOT `Landing.tsx`). Route config in `App.tsx`:

```tsx
<Route path={ROUTES.HOME} element={<V2 />} />
```

### Landing Layout (top → bottom)

1. HeaderV2 + background effects (grain, grid, gradient)
2. **Hero**: video/dither background, heading with purple `#6B5CE7` accent, CTA button, stats row
2. **Agent catalog**: grid of available services (OpenClaw, Hermes, FreqDash, Hiddify) — each with SVG icon, name, description, tag badge, and deploy link
4. **FeaturesGridV2**: feature cards
5. **PricingSectionV2**: dynamic pricing
6. **ComparisonTableV2**: OpenClaw vs competitors
7. **FaqSectionV2**: accordion FAQ
8. **CTA**: final call-to-action
9. **FooterV2**

### v2Agents — Icon Type System

The `iconType` field in `v2Agents.ts` determines which SVG icon renders in the agent card. Currently supports:
- `'openclaw'` → `OpenClawIcon` (red claw icon)
- `'hermes'` → `HermesIcon` (detailed AI agent icon)
- `'freqtrade'` → `FreqtradeIcon` (bar chart icon)
- `'hiddify'` → `HiddifyIcon` (shield/security icon)

All icon components live in `apps/web/src/components/icons/`. The rendering in V2.tsx uses a 4-way ternary to select the component.

When adding a new iconType, you MUST:
1. Create the SVG icon component in `components/icons/`
2. Import it in `V2.tsx`
3. Add a new ternary branch for the rendering
4. No types need updating — iconType is just a string, the ternary handles all values at runtime

### Nav Links Structure

```typescript
const navLinks = [
  { label: {label}, href: '#use-cases', id: 'use-cases' },
  { label: t('landing.features'), href: '#features', id: 'features' },
  { label: t('landing.pricing'), href: '#pricing', id: 'pricing' },
  { label: 'Сравнение', href: '#comparison', id: 'comparison' },
  { label: 'FAQ', href: '#faq', id: 'faq' },
]
```

## Dynamic Pricing (CRITICAL)

### buildV2Plans — DO NOT hardcode plan IDs

The `buildV2Plans()` function in `apps/web/src/components/v2/buildV2Plans.ts` processes API plan data for the pricing section.

**CORRECT approach** (user's explicit requirement):
```typescript
const sorted = [...plans].sort((a, b) => a.priceMonthly - b.priceMonthly)
const top4 = sorted.slice(0, 4)
return top4.map((p, i) => ({
  planId: p.id,
  price: Math.round(p.priceMonthly),
  yearlyPerMonth: Math.round((p.priceYearly ?? p.priceMonthly * YEARLY_PAID_MONTHS) / 12),
  popular: i === 1,  // second cheapest = "recommended"
  features: [...specs, ...common, ...extras],
  // ...
}))
```

**FAILURE MODE to avoid**: Do NOT hardcode plan IDs (like `cpx21`, `ccx23`, `ccx33`, `ccx43`). The API may return different plans, different IDs, or RUB prices. Always sort by `priceMonthly` and take dynamically.

### Stats Row Price — also dynamic

The 5 stats at the top of V2.tsx come from `getV2Stats()` in `apps/web/src/data/v2Stats.ts`. The first stat (price) MUST use the min plan price from API, not a hardcoded value:

```typescript
// In V2.tsx:
const minMonthlyRub = plans && plans.length > 0
  ? Math.min(...plans.map((p) => p.priceMonthly))
  : null

// Pass to getV2Stats:
getV2Stats(minMonthlyRub)
```

**FAILURE MODE**: `getV2Stats()` originally hardcoded `{ price: 25 }` instead of receiving the dynamic price. Always pass the computed `minMonthlyRub` from `usePlans()`.

### Font in Stats Section
The stats section values should use `font-clash`, not `font-syne`. This was patched in V2.tsx but may resurface if the section is re-templated.

## i18n Conventions

- All translations live in `packages/i18n/src/langs/` (14 languages)
- Use `t()` from `@openclaw/i18n` for all user-facing strings
- The web app's `tsconfig.json` maps `#i18n/*` → `../../packages/i18n/src/*`
- There's also a root `/root/clawhost/ru.ts` which is a copy — BOTH must be updated for changes to take effect in all contexts
- When renaming a brand/product name (e.g., Agentist → ClawHost), update ALL 14 language files, not just Russian

## Adding a New Page / Route

Standard steps to add a new page to the web app:

### 1. Add path constant
In `apps/web/src/lib/paths.ts`:
```typescript
SKILLS: 'skills'
```

### 2. Add route constant
In `apps/web/src/lib/constants/routes.ts`:
```typescript
SKILLS: `/${PATHS.SKILLS}`
```

### 3. Create page component
In `apps/web/src/pages/Skills.tsx` — default export, FC<ReactNode> pattern.

### 4. Register in router
In `apps/web/src/App.tsx`:
```typescript
const Skills = lazy(() => import('@/pages/Skills'))
// ...
<Route path={ROUTES.SKILLS} element={<Skills />} />
```

### 5. Add nav link (optional)
In `apps/web/src/data/v2NavLinks.ts`:
```typescript
{ label: 'Навыки', href: ROUTES.SKILLS, id: 'skills' }
```

## Skills Hub Page

The `/skills` route serves a Skills Hub page (`apps/web/src/pages/Skills.tsx`) that displays community-created OpenClaw skills:
- **Data source**: `https://raw.githubusercontent.com/geniok1980/Skills/main/skills.json`
- **Filtering**: by category (14 categories with emoji icons) and search query
- **Sorting**: Popular (default order) or Newest
- **Each skill card** links to its GitHub repo for installation
- Uses same dark theme (`#0a0a0a`), `font-clash`/`font-satoshi`, HeaderV2 + FooterV2

## Brand Naming

- The platform is called **ClawHost** (NOT Agentist — this was a rebranding)
- The landing page title should say: "Deploy OpenClaw. One click. Done. - ClawHost"
- Never use "Agentist" anywhere in the UI

## Pitfalls

- **Font confusion**: The v2 components originally used `font-syne` (Syne). The user wants `font-clash` (Clash Display). When using or extending v2 components, ensure fonts match the hierarchy above.
- **Pricing hardcoding**: BuildV2Plans must be dynamic. If the API returns plans in RUB, prices show as ₽. The fallback PLANS from `@openclaw/shared` use USD.
- **Rebrand remnants**: Old translation files may still contain "Agentist". Run `grep -r "Agentist"` across all language files after any rebrand.
- **Two ru.ts files**: `/root/clawhost/ru.ts` and `packages/i18n/src/langs/ru.ts` are different files. Both must be updated. The package version is the one that the app actually reads.
- **Build errors**: `prerender.ts` and `RenewSubscriptionButton.tsx` have pre-existing TS errors unrelated to landing page work.
- **font-syne in stats section**: V2.tsx stats row originally used `font-syne` — always use `font-clash` for stats values.

## See Also

- `portfolio-landing-maintenance` — for the separate static HTML portfolio at geniok.ru (NOT the clawhost project)
- CLAUDE.md in project root — has extensive import rules (use `@/` aliases, one export per file, centralized types)
