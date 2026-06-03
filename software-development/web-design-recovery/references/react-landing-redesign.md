# Reference-Based Landing Page Redesign (React/TypeScript)

Workflow for redesigning an existing React landing page to match a reference site's visual structure and layout, while reusing existing project components.

## When to Use

- User wants landing page X to look like reference site Y
- Reference is a live SPA/React site (not just static HTML)
- Existing project uses React + Tailwind + component library (shadcn/ui, Radix)

## Workflow

### 1. Analyze reference site

```javascript
// Get background, text color, font family
JSON.stringify({
  bg: getComputedStyle(document.body).backgroundColor,
  color: getComputedStyle(document.body).color,
  fontFamily: getComputedStyle(document.body).fontFamily
})
```

```javascript
// Get all CSS custom properties from :root (design token system)
const root = getComputedStyle(document.documentElement);
const vars = {};
for (let i = 0; i < root.length; i++) {
  const name = root[i];
  if (name.startsWith('--')) vars[name] = root.getPropertyValue(name).trim();
}
console.log(JSON.stringify(vars, null, 2));
```

Check dark mode class: `document.documentElement.classList.contains('dark')`

Map page structure via browser snapshot (hero, features, use cases, pricing, FAQ, CTA, footer).

Identify animation patterns (framer-motion, scroll-triggered, parallax).

### 2. Analyze existing project layout

- Find the landing page component (typically `/pages/Landing.tsx` or similar)
- Read the component barrel (`/components/index.ts`) to see available reusable components
- Read the existing CSS (index.css or tailwind.config) for design tokens, custom classes, fonts
- Check for existing v2/alternative design systems in the project (e.g., `v2-grain`, `v2-grid`, `v2-gradient` in CSS)
- Check available icons and their naming convention (e.g., `@phosphor-icons/react` with `Icon` suffix)
- Read Data source files for existing nav links, features, stats, FAQs

### 3. Map reference sections to existing components

| Reference section | Best match | Notes |
|---|---|---|
| Header | HeaderV2 or custom | Use v2 dark theme header if available |
| Hero | Build inline | Combine badge + heading + CTA + optional demo panel |
| Feature cards | FeaturesGridV2 or custom | Match 3-card layout vs grid |
| Use cases/testimonials | Build inline | Tags + quote + author pattern |
| Connectors | Build inline | Icon + label grid |
| Comparison table | Build inline or ComparisonTableV2 | Match reference column structure |
| Stats | Build inline | Number + label cards |
| Pricing | PricingSectionV2 | Already has dark mode support |
| FAQ | FaqSectionV2 | Already has dark mode support |
| CTA | Build inline | Using existing Link + button patterns |
| Footer | FooterV2 | Already has dark mode support |

### 4. Set up the page shell

```tsx
<div className='bg-[#HEX] text-[#HEX] min-h-screen'>
  {/* v2-grain + v2-grid + v2-gradient for dark theme texture */}
  <div className='v2-grain' />
  <div className='v2-grid pointer-events-none' />
  <div className='pointer-events-none fixed inset-x-0 top-0 h-screen bg-[radial-gradient(...)]' />
  
  <HeaderV2 showNavLinks navLinks={navLinks} />
  
  <main className='v2-content'>
    {/* sections */}
  </main>
  
  <FooterV2 />
</div>
```

### 5. Hero section pattern (dark theme with demo panel)

Two-column layout: left = badge + heading + description + CTA, right = demo chat panel.

Use framer-motion staggered animations:
```tsx
<motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.6, delay: 0.15 }}>
```

Gradient text: `bg-gradient-to-r from-red-500 via-red-400 to-red-500 bg-clip-text text-transparent`

Live status dot: `<span class="relative flex h-1.5 w-1.5"><span class="animate-ping ... bg-emerald-500" /></span>`

### 6. Sections pattern

```
hero → 3 feature cards → use cases → connectors → comparison → stats → pricing → FAQ → CTA → footer
```

Each section: `<section className='border-t border-white/[0.025] px-6 py-24'>` with `ScrollRevealV2` wrapper.

Grid cards with hover: `grid gap-px border border-white/10 bg-white/[0.03] md:grid-cols-3`

Card cell: `bg-[#070709] p-8 transition-colors hover:bg-[#0a0a12]`

### 7. Fix TypeScript/build after redesign

Common issues to fix:
- Remove unused imports (React doesn't flag them but tsc does with `noUnusedLocals`)
- Replace `import { useAuth } from '@/hooks'` → `import { useAuth } from '@/lib/auth'` if hooks barrel doesn't export it
- Remove unused icon imports before building
- Remove type imports from Interfaces if no longer used
- Check that all Phosphor icons with `Icon` suffix actually exist in the package

### 8. Verify

- `tsc --noEmit` — no new errors (pre-existing errors are okay)
- vite/build should pass (or at least compile without import/resolution errors on the changed file)
- Check responsive layout: hero two-column collapses to single on mobile

## Route-aware editing (critical)

**After changing which component handles the `/` route** (e.g., replacing `<Landing />` with `<V2 />` in `App.tsx`), the file that renders on the page CHANGES. All subsequent edits must target the NEW active file, not the old one. Editing the old `Landing.tsx` has zero effect on the live page.

Always verify which component is currently routed to `ROUTES.HOME` before making changes.

## Global branding replacements across i18n

When renaming a brand/product across the site, the i18n package (`@openclaw/i18n`) under `packages/i18n/src/langs/` has translation files for all languages (en, ru, de, fr, es, it, pt, pl, nl, tr, zh, ja, hi, ar). A single `sed -i 's/OldName/NewName/g'` across all of them is faster and safer than editing each file individually.

Also check:
- SVG text paths in logo components (like `LogoV2.tsx`) — may contain the old brand name as hardcoded SVG path data
- Translation key names (e.g., `nav.agentistGo`) — the value is what renders, but the key name might still reference the old brand

## Button style uniformity

Buttons that appear on the landing page may come from MULTIPLE components, not just the page file itself. When restyling buttons, check:
- The landing page file (`V2.tsx` / `Landing.tsx`) — hero CTA, agent cards, bottom CTA
- `HeaderV2.tsx` — the deploy button in the navigation bar
- `PricingSectionV2.tsx` — plan selection buttons
- Footer, FAQ, comparison sections typically don't have buttons but verify

Use a consistent pattern across ALL of them: same gradient, same icon, same font, same hover behavior.

## Dynamic pricing from API

When a landing page shows plan prices, the data should come from the API response, not hardcoded defaults:

1. The page component uses `usePlans()` hook → `plansResponse?.plans || PLANS` (fallback)
2. `buildV2Plans(plans)` transforms API plans into display format
3. **Ensure `buildV2Plans` is truly dynamic** — it should sort plans by `priceMonthly` and pick top N, not hardcode plan IDs. If IDs are hardcoded and the API returns different IDs or different pricing, the fallback `??` values will be shown instead of real data.

```typescript
// DYNAMIC approach (correct):
const sorted = [...plans].sort((a, b) => a.priceMonthly - b.priceMonthly)
const top4 = sorted.slice(0, 4)
return top4.map((p) => ({
  planId: p.id,
  price: Math.round(p.priceMonthly),
  yearlyPerMonth: Math.round((p.priceYearly ?? p.priceMonthly * 10) / 12),
  // ...
}))

// STATIC approach (wrong):
const result = [
  { planId: 'cpx21', price: Math.round(planMap.get('cpx21')?.priceMonthly ?? 40), ... }
  // Falls back to 40 if API plan missing
]
```

## Logo SVG replacement

If a logo component uses inline SVG path data to render text (like `LogoV2.tsx`), replacing the brand name requires either:
1. **Complex**: Rewriting all the path `d` attributes to spell the new name (impractical without a font-to-path tool)
2. **Simple**: Replace the entire SVG with an icon-only mark + HTML text in the desired font using a `<span>`:
   ```tsx
   <Link to={ROUTES.V2} className='flex items-center gap-3'>
     {/* Icon SVG (simple geometric shapes) */}
     <svg>...</svg>
     {/* Text rendered in the project's heading font */}
     <span className='font-clash text-lg font-bold text-white'>NewName</span>
   </Link>
   ```

## Pitfalls

- **Don't assume all reference site fonts are available** — check existing project's font imports first
- **Phosphor icons v2 use `Icon` suffix** — `Check` is deprecated, use `CheckIcon`
- **Don't reuse old landing layout components** if they're styled for a different theme (light mode) — they'll look wrong on the new dark bg
- **Framer-motion on scroll** works best with `viewport={{ once: true, margin: '-80px' }}`
- **Pre-existing build errors** in unrelated files don't indicate your changes are broken — verify by grepping tsc output for your file
- **Route-aware editing**: changing the home route in App.tsx means you must edit the new component, not the old one
- **Replace brand names across ALL i18n files**, not just the user's language — the browser might request English or another language
- **Check for inline `font-syne` in the main page file** in addition to component files — V2.tsx had hardcoded `font-syne` classes on headings that weren't part of any imported component
