---
name: clawhost-landing
description: Maintain and restyle the ClawHost landing page — a React/TypeScript + Tailwind CSS monorepo (openclaw.anywhere). Covers design, fonts, dynamic pricing, routing, branding, and component choices.
category: software-development
triggers:
  - "clawhost лендинг"
  - "clawhost landing"
  - "clawhost.geniok.ru"
  - "оформление главной"
  - "редизайн лендинга clawhost"
  - "поменять дизайн clawhost"
---

# ClawHost Landing Page

## Context

The ClawHost landing page is the main page of a React/TypeScript monorepo at `/root/clawhost/`. It's a Turborepo with `apps/web` (React + Vite), `apps/api` (Hono.js), and shared packages. The landing route is `ROUTES.HOME = '/'` in `apps/web/src/App.tsx`.

## Key Files

| File | Purpose |
|---|---|
| `apps/web/src/pages/Landing.tsx` | Main landing page component (currently renders V2 content) |
| `apps/web/src/pages/V2.tsx` | V2-style landing page (used as the main landing) |
| `apps/web/src/App.tsx` | Router — HOME route renders the landing |
| `apps/web/src/components/v2/` | V2 component library (HeaderV2, FooterV2, PricingSectionV2, etc.) |
| `apps/web/src/components/v2/buildV2Plans.ts` | Pricing plan builder — MUST be dynamic from API |
| `apps/web/src/components/v2/LogoV2.tsx` | Logo (icon grid + "ClawHost" text) |
| `apps/web/src/components/v2/HeaderV2.tsx` | Navigation header with deploy button |
| `packages/i18n/src/langs/ru.ts` | Russian translations |
| `packages/shared/src/plans.ts` | Default PLANS fallback data |

## Design Preferences

### Colors
- **Background**: `#0a0a0a` (clean dark, NO grain, NO grid, NO gradient overlays)
- **Text**: `#fafafa` (off-white)
- **Accent**: Red gradient `from-[#ef5350] to-[#c62828]`

### Fonts
- **Headings**: `font-clash` (Clash Display) — bold/uppercase
- **Body**: `font-satoshi` (Satoshi) — inherit from root div
- **Code/meta**: `font-mono` (JetBrains Mono) — only for badges, tags, small labels
- Root div MUST have `font-satoshi` class

### Buttons (Header + CTAs)
- Gradient: `bg-gradient-to-r from-[#ef5350] to-[#c62828] border-0`
- **Rounded**: ALL gradient buttons MUST include `rounded-md` — the user wants rounded corners, not sharp edges
- Icon: `LightningIcon` with `weight='fill'`
- Text: `font-satoshi font-semibold`
- Hover: `hover:opacity-90`
- No arrow icons, no animated transitions on hover

### Background Effects
- Clean solid `#0a0a0a`. Do NOT add:
  - `v2-grain` (noise texture overlay)
  - `v2-grid` (grid pattern)
  - Radial gradient overlays at top

### Pricing

**Two pricing components exist. Use the right one based on user's request:**

#### 1. Old-style pricing (`PricingSection` — from `@/components/landing/`)
- Used on the original `Landing.tsx` (the landing before V2 redesign)
- Imports: `import { PricingSection } from '@/components/landing'`
- Uses `buildSimplePlans(plans)` with `SimplePlanCard` for 4 plan cards (Starter, Growth, Pro, Business)
- Has a "Show all plans" toggle that renders a full table with all API plans
- Uses shadcn/ui `Button` and `Badge` components
- Styling: rounded cards (`rounded-xl`), gradient popular badge, green/orange check icons
- Plan IDs used: cx23 (Starter), cpx21 (Growth), ccx23 (Pro), ccx33 (Business)

#### 2. V2-style pricing (`PricingSectionV2` — from `@/components/v2/`)
- Grid layout with `buildV2Plans(plans)` that sorts by price and takes 4 cheapest
- Each card shows CPU, RAM, disk, monthly/yearly via toggle, features

**IMPORTANT**: When user says "тарифы как на старом лендинге" or "верни старые тарифы" — use `PricingSection` + `buildSimplePlans` from `@/components/landing/`, NOT `PricingSectionV2`.

- **ALWAYS dynamic from API**. Never hardcode plan IDs or prices.
- The function receives `plans` from `usePlans()` hook → `plansResponse?.plans || PLANS` (PLANS is static fallback).
- The price stat in the hero also uses `minMonthlyRub` from the API.

### Stats Row (dynamic price stat)
- In `V2.tsx`, compute `minMonthlyRub` from plans:
  ```tsx
  const minMonthlyRub = plans && plans.length > 0
    ? Math.min(...plans.map((p) => p.priceMonthly))
    : null
  ```
- Pass to `getV2Stats(minMonthlyRub)` — the function in `v2Stats.ts` accepts an optional `minPrice` param.
- **CRITICAL**: `getV2Stats()` used to hardcode `{ price: 25 }`. It MUST receive the dynamic price from API.
- The i18n template `t('landing.startingPriceValue', { price })` renders as `₽{price}/месяц` in ru locale.
- All 5 stats come from `getV2Stats()`: price, zero-config, regions, deploy-time, uptime.

### Logo
- Grid icon (3×3 squares with center gap, white) + "ClawHost" text in `font-clash`
- Implementation: `LogoV2.tsx` — inline SVG icon + `<span>` text

### Branding
- All "Agentist" references in i18n files → "ClawHost" (ALL language files in `packages/i18n/src/langs/*.ts`)
- The `agentistGo` translation key name is internal — the displayed value is 'ClawHost Go'

## Routing

- `ROUTES.HOME = '/'` renders `<V2 />` (the V2-style landing, NOT the old Landing component)
- The old `Landing.tsx` page is preserved but not imported in App.tsx
- V2 page is at `ROUTES.V2 = '/v2'` as well (backup route)

## Typical Workflows

### Restyling the Landing

1. Edit `apps/web/src/pages/Landing.tsx` (or whichever component is the HOME route)
2. To change fonts globally in v2 components: update `font-syne` → `font-clash` in all `apps/web/src/components/v2/*.tsx`
3. To change button style: update `HeaderV2.tsx` deploy button + Landing.tsx CTAs
4. To update pricing logic: edit `apps/web/src/components/v2/buildV2Plans.ts`
5. To change logo: edit `apps/web/src/components/v2/LogoV2.tsx`
6. Verify: `cd /root/clawhost/apps/web && npx tsc --noEmit`

### Changing Brand Name in Translations

```bash
# Replace "Agentist" → "ClawHost" in ALL language files
sed -i 's/Agentist/ClawHost/g' /root/clawhost/packages/i18n/src/langs/*.ts
```

### Making the V2 Page the Main Landing

In `apps/web/src/App.tsx`:
```tsx
// Change HOME route from Landing to V2
<Route path={ROUTES.HOME} element={<V2 />} />
// Remove unused import: import Landing from '@/pages/Landing'
```

## Nav Links

Nav links are defined in `apps/web/src/data/v2NavLinks.ts`. The current nav:

| Label | Route | Description |
|-------|-------|-------------|
| Cloud | `/` or `/v2` | Main landing page |
| Примеры использования | `/use-cases` | Use cases catalog page |
| Навыки | `/skills` | Skills Hub page (replaced "Go") |
| Features | `/features` | Features page |
| Pricing | `/pricing` | Pricing page |
| Сравнение | `#comparison` | Hash anchor — scrolls to ComparisonTableV2 section on the SAME page |

**IMPORTANT**: 
- The "Сравнение" link uses **hash anchor** `#comparison` (not `/comparison` route) so it scrolls to the `ComparisonTableV2` section on the current landing page. The section already has `id='comparison'` in its `<section>` element.
- For hash anchors to work, V2.tsx MUST have a `useEffect` that reads `useLocation().hash` and calls `scrollIntoView()`:
  ```tsx
  const { hash } = useLocation()
  useEffect(() => {
      if (!hash) return
      const id = hash.replace('#', '')
      const el = document.getElementById(id)
      if (el) setTimeout(() => el.scrollIntoView({ behavior: 'smooth' }), 100)
  }, [hash])
  ```
- Other nav items (Features, Pricing) use full routes (`/features`, `/pricing`) that navigate to separate pages.
- The footer (`apps/web/src/components/v2/FooterV2.tsx`) has a `productLinks` array. Do NOT include `ROUTES.GO` / `nav.agentistGo` in that array — the user wants the Go product link removed from the footer.

### Adding a New Page (full workflow: route + component + nav)

1. Add path constant in `apps/web/src/lib/paths.ts` → e.g. `PATHS.USE_CASES`
2. Add route in `apps/web/src/lib/constants/routes.ts` → e.g. `ROUTES.USE_CASES`, `ROUTES.USE_CASE_DETAIL`
3. Create page component(s) in `apps/web/src/pages/`
4. Lazy-import and add `<Route>` in `apps/web/src/App.tsx`
5. Add nav link entry in `apps/web/src/data/v2NavLinks.ts`
6. If the page uses data, create a data file in `apps/web/src/data/`
7. Add i18n keys if needed (see i18n pitfalls above — must update ALL locale files)

### Use Cases Pages (`/use-cases` and `/use-cases/:slug`)

Data file `apps/web/src/data/useCases.ts` with fields: `slug`, `emoji`, `category`, `title`, `description`, `fullDescription`, `tags`, `forWhom`, `features` (`{title, description}[]`), `skills` (`{name, description, url}[]`), `beforeAfter` (`{before: string[], after: string[]}`), `steps`, `faq`.

**Listing page** (`UseCases.tsx`): dark theme, search, emoji category filters, card grid → `/use-cases/:slug` links. Same `HeaderV2`/`FooterV2` as landing.

**Detail page** (`UseCaseDetail.tsx`): hero with back link, emoji+badge, CTA buttons, conditional sections (For whom, Features, Skills, Before/After, Steps, FAQ, CTA). Uses `useParams<{slug}>` to find match, 404 fallback.

### Skills Hub Page (`/skills`)

`apps/web/src/pages/Skills.tsx`:
- **Text readability**: descriptions use `text-white/70` — `text-white/40` was too faded. Keep opacity ≥ 70% for body text on `bg-[#070709]` dark cards.
- Search, emoji category filters, sort (popular/newest), card grid with install buttons
- Data: `https://raw.githubusercontent.com/geniok1980/Skills/main/skills.json`
- Each card links to `https://github.com/geniok1980/Skills/tree/main/{name}`
- Cards: `bg-[#070709]` with border grid, framer-motion entrance animations

## Pitfalls

- **Do NOT hardcode plan IDs** in `buildV2Plans`. The API may return different plans. Sort dynamically by price.
- **Do NOT use `font-syne`** — the user prefers Clash Display for headings.
- **Do NOT add grain/grid/gradient overlays** to the landing page background.
- **Do NOT use RocketLaunchIcon or ArrowRightIcon** in buttons — use LightningIcon instead.
- **Translation keys** like `agentistGo` are internal names, not displayed text. The displayed value is what matters.
- **New i18n keys MUST be in ALL locale files**: The `TranslationKey` type in `packages/i18n/src/types.ts` is derived from `typeof en` (the English locale). Adding a new key to `en.ts` without adding it to ALL other locale files (`ar.ts`, `de.ts`, `es.ts`, `fr.ts`, `hi.ts`, `it.ts`, `ja.ts`, `nl.ts`, `pl.ts`, `pt.ts`, `tr.ts`, `zh.ts`, `ru.ts`) will cause TypeScript errors in every file. When adding new translation keys:
  1. First add to `en.ts` (defines the type)
  2. Add to `ru.ts` (user's primary language)
  3. Add stub values to ALL other locale files (can be English text as placeholder)
  4. Run `npx tsc --noEmit --project apps/web/tsconfig.json` to verify
- **New agent catalog entries**: To add a new deployable to the agent catalog section on V2.tsx:
  1. Create a new object in `apps/web/src/data/v2Agents.ts` with `nameKey`, `descKey`, `tag`, and `iconType`
  2. Available `iconType` values: `'openclaw'` | `'hermes'` | `'freqtrade'` — each maps to a different SVG icon component. If adding a new type, create the icon component in `apps/web/src/components/icons/`, add the import and ternary branch in `V2.tsx`.
  3. Add corresponding i18n keys (`agentXxxName`, `agentXxxDescription`) to ALL 14 locale files (see i18n pitfall)
  4. Tags are displayed as uppercase badges (e.g. `AI_AGENT`, `OPEN_SOURCE`) — choose a short descriptive tag
  5. The rendering is in `V2.tsx` lines 218-252 — it loops `v2Agents` and renders cards with icon, name, description, and deploy link. No component changes needed for new entries.
- **Removing an agent catalog entry**: To completely delete an agent (e.g. for compliance reasons like VPN advertising prohibition):
  1. Delete its object from `apps/web/src/data/v2Agents.ts`
  2. Remove the corresponding i18n keys (`agentXxxName`, `agentXxxDescription`) from the v2 section in ALL 14 locale files — if you leave them in any file, TypeScript will error because the type no longer defines them (the type comes from `en.ts`)
  3. If the removed agent had a unique `iconType`, remove the ternary branch in `V2.tsx` and drop the icon import
  4. Verify: `cd /root/clawhost/apps/web && bunx tsc --noEmit 2>&1 | grep -i "hiddify\\|vpn"` should return zero matches

**Prefer rebranding over removal**: Before deleting an agent entry, consider if renaming it (like Hiddify → "Other Open-Source Projects") would satisfy the requirement while keeping the card. See "Rebranding an agent catalog entry" below for the rename workflow.
- **Pre-existing errors** in `prerender.ts` and `RenewSubscriptionButton.tsx` are unrelated to the landing page and should be ignored.
- **font-syne still in V2.tsx stats**: The stats section in `V2.tsx` originally used `font-syne`. When modifying stats, ensure value uses `font-clash` (the user's preference over Syne).
- **Skills page nav links**: `Skills.tsx` passes its own `navLinks` array to `<HeaderV2 showNavLinks={true} navLinks={navLinks} />` — it does NOT use `getV2NavLinks()`. The navLinks array includes `{ label: 'Главная', href: '/' }` and `{ label: 'Навыки', href: '/skills' }`.
- **Footer "Go" link**: The footer `productLinks` should NOT include `ROUTES.GO`. Remove it if present.
- **Pricing component confusion**: When the user says "старые тарифы" or "тарифы с предыдущего лендинга", use `PricingSection` + `buildSimplePlans` from `@/components/landing/`, NOT the V2 versions from `@/components/v2/`.
- **Hash scroll effect in V2.tsx**: Without the `useEffect` + `useLocation().hash` handler, hash anchors (`#comparison`) in nav links won't scroll to the section. Always check it exists when using hash-based nav items.
- **ComparisonTableV2 already has `id='comparison'`**: The `<section>` element inside `ComparisonTableV2` already has this id — no need to add a wrapper.
- **Hero section label**: The `<SectionLabelV2>` in the hero uses `'Cloud Platform'` (was `'Multi Agent Platform'` — changed when services expanded beyond AI agents to include VPN and trading bots).
- **Hero title content**: The hero heading is built from three i18n keys — `heroTitle1` ("Разверните"), `heroTitle2` ("ИИ-агентов, Торговых роботов и другие Open-Source проекты" — rendered in purple `#6B5CE7` span), `heroTitle3` ("в Облаке в один Клик"). When changing hero text, update `heroTitle2` (the purple emphasis span), `heroDescription`, `title`, `description`, `agentsTitle`, `agentsDescription` in ALL 14 locale files — incomplete updates = TS errors. Current text (post-VPN-removal) references "Торговых роботов и другие Open-Source проекты" instead of "Приватный VPN".

- **Agent catalog has 3 services**: The `v2Agents` array in `apps/web/src/data/v2Agents.ts` now contains:
  - OpenClaw (`iconType: 'openclaw'` → `OpenClawIcon`, tag: `AI_AGENT`)
  - Hermes (`iconType: 'hermes'` → `HermesIcon`, tag: `AI_AGENT`)
  - FreqDash (`iconType: 'freqtrade'` → `FreqtradeIcon`, tag: `OPEN_SOURCE`)
  - Other Open-Source Projects (`iconType: 'hiddify'` → `HiddifyIcon`, tag: `OPEN_SOURCE`)

  Hiddify was rebranded to "Other Open-Source Projects" due to VPN advertising restrictions — the card was NOT removed, only renamed. The HiddifyIcon was retained as the generic icon for this card.

- **Rebranding an agent catalog entry (compliance)**: When a service can no longer be advertised under its original name (e.g. VPN restrictions):
  1. DO NOT delete the card from `v2Agents.ts` — rename `nameKey` and `descKey` values in ALL 14 locale files instead
  2. Change the `tag` from the original category (e.g. `'VPN'`) to `'OPEN_SOURCE'`
  3. Keep the same `iconType` (the HiddifyIcon stays — it's now just a generic deployment icon)
  4. Update the hero/description/agentsTitle text in all 14 locale files
  5. Keep the i18n key names (`agentHiddifyName` remains as-is — it's an internal ID, not displayed text)
  6. Verify: `cd /root/clawhost/apps/web && bunx tsc --noEmit 2>&1 | grep -i \"hiddify\\|vpn\" | grep -i \"agentHiddify\"` should only match `agentTypeHiddify` (agent type filter, unrelated to landing)

- **Icon selection in V2.tsx**: The icon rendering uses a 4-way ternary chain:
  ```tsx
  {agent.iconType === 'openclaw' ? <OpenClawIcon size={32} />
   : agent.iconType === 'freqtrade' ? <FreqtradeIcon size={32} />
   : agent.iconType === 'hiddify' ? <HiddifyIcon size={32} />
   : <HermesIcon size={32} />}
  ```
  Import 4 icon components from `@/components/icons`: `OpenClawIcon`, `HermesIcon`, `FreqtradeIcon`, `HiddifyIcon`.
- **`agent.ic` removal**: Every reference to "agent.ic" must be replaced with "ClawHost" — in i18n `title`, `description`, `pricingPageTitle`, `featuresPageTitle`, `featuresPageDescription` across ALL 14 locale files. Also in SEO metadata and comments. The only remaining `agent.*` matches should be JavaScript property access (`agent.iconType`).

## See Also

- `portfolio-landing-maintenance` — for the geniok.ru static portfolio (different project!)
- `web-design-recovery` — for extracting design tokens from reference sites
