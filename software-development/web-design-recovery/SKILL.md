---
name: web-design-recovery
description: Extract a live or cached website's visual design (colors, fonts, layout, structure) for recreation in Figma, Tilda, or HTML/CSS. Covers site-availability checks, Wayback Machine exploration, CSS token extraction, and page structure mapping.
tags: [figma, tilda, design-recovery, css-extraction, bitrix, web-archive]
---

# Web Design Recovery

Recover a website's visual design from a live or cached copy. Use when the user wants to recreate a site in Figma, Tilda Zero Block, or HTML — and the original source files (PSD, Figma, Sketch) are unavailable.

## Workflow

### 1. Check site availability

Always check before trusting the user's claim that a site is "down".

```bash
# Quick availability check
curl -sI --max-time 10 https://example.com | head -20
curl -sI --max-time 10 http://example.com | head -20

# Full content download
curl -sL --max-time 30 "https://example.com" -o /tmp/site_main.html
```

### 2. Wayback Machine check

```bash
# Check if any captures exist
curl -sI --max-time 15 "https://web.archive.org/web/2025/https://example.com"

# Get complete timeline (all snapshots since inception)
curl -s "https://web.archive.org/web/timemap/link/example.com" --max-time 15

# Download a specific snapshot
curl -sL --max-time 30 "https://web.archive.org/web/20250719092359/https://example.com/" -o /tmp/wayback.html
```

### 3. Download all CSS

```bash
# Extract CSS URLs from HTML
grep -oP 'href="[^"]*\.css[^"]*"' index.html | sed 's/href="//;s/"//'

# Download each (handle relative paths)
for css in $(grep -oP 'href="[^"]*\.css[^"]*"' index.html | sed 's/href="//;s/"//'); do
  curl -sL --max-time 30 "https://example.com${css}" -o "css_$(echo $css | sed 's|/|_|g')"
done
```

### 4. Extract design tokens

**CSS custom properties (primary source):** Look in `<style>` tags in `<head>`:

```css
html {
  --theme-base-color: #2c6484;          /* Primary brand color */
  --theme-base-opacity-color: #2c64841a;
  --theme-more-color: #ec6a62;           /* Accent/secondary color */
  --theme-border-radius: 4px;
  --theme-text-transform: none;
  --theme-letter-spacing: normal;
}
```

**Extract top colors from CSS:**

```bash
grep -oP '#[0-9a-fA-F]{6}' css_file.css | sort | uniq -c | sort -rn | head -30
```

**Font families:**

```bash
grep -oP 'font-family:[^;}]+' css_file.css | sort -u
```

### 5. Map page structure

Use the browser snapshot to identify all sections:

```
Header (logo, nav, contacts)
├── Banner / Hero section (heading, subtitle, CTA)
├── Stats / Trust signals
├── Services / Products grid
├── Content sections
└── Footer (contacts, nav, social, copyright)
```

### 6. Capture all assets

```bash
# Extract image URLs from HTML
grep -oP '<img[^>]+src="([^"]+)"' index.html | grep -oP 'src="\K[^"]+'

# Download them
for url in $(grep -oP 'src="\K[^"]+(png|jpg|jpeg|svg|webp)' index.html); do
  curl -sL --max-time 15 "https://example.com$url" -o "assets/$(basename $url)"
done
```

### 7. Sub-page inventory

Download all subpages to capture consistent structure:

```bash
for page in "o-kompanii" "uslugi" "produkty" "kejsy" "kontakty"; do
  curl -sL --max-time 30 "https://example.com/$page/" -o "${page}.html"
  echo "$page: $(wc -c < ${page}.html) bytes"
done
```

## Figma Recreation

I cannot CREATE Figma files (Figma API is read-only for content), but can provide the full design spec for manual recreation:

- **Color palette:** extracted hex values with usage context
- **Typography:** font family, sizes, weights, line heights
- **Spacing grid:** padding, margins, gaps
- **Component specs:** button styles, card layouts, form elements
- **Page structure:** section-by-section layout description

## Tilda Zero Block Export

Tilda Zero Block accepts custom HTML/CSS/JS. Can generate:
- Complete HTML/CSS replica matching the source site's design
- Responsive layout adapted for Tilda's grid

Requires Tilda API key for direct publishing.

### 8. Extract design tokens via browser console (deep)

When the site is live and the browser is available, use the browser console to programmatically extract the actual computed design system. This is more reliable than guessing from CSS filenames.

```javascript
// Get all CSS custom properties from :root
const root = getComputedStyle(document.documentElement);
const vars = {};
for (let i = 0; i < root.length; i++) {
  const name = root[i];
  if (name.startsWith('--')) vars[name] = root.getPropertyValue(name).trim();
}
// Focus on key design tokens
const designTokens = {};
for (const [k, v] of Object.entries(vars)) {
  if (k.includes('accent') || k.includes('card') || k.includes('radius') ||
      k.includes('color') || k.includes('bg') || k.includes('border')) {
    designTokens[k] = v;
  }
}
console.log(JSON.stringify(designTokens, null, 2));
```

**Card/component styles (get actual computed values from the first instance):**

```javascript
const firstCard = document.querySelector('[class*="card"], [class*="Card"], [class*="skill"], [class*="item"]');
const cs = firstCard ? getComputedStyle(firstCard) : null;
if (cs) {
  console.log(JSON.stringify({
    background: cs.background,
    border: cs.border,
    borderRadius: cs.borderRadius,
    padding: cs.padding,
    boxShadow: cs.boxShadow,
    color: cs.color,
    fontSize: cs.fontSize,
    fontWeight: cs.fontWeight,
  }, null, 2));
}
```

**Hover/focus/transition effects (extract from stylesheets, not just computed - hover states aren't in computed):**

```javascript
const effects = {};
for (const ss of document.styleSheets) {
  try {
    for (const rule of ss.cssRules) {
      if (rule.selectorText && (
          rule.selectorText.includes(':hover') ||
          rule.selectorText.includes(':focus') ||
          rule.selectorText.includes('transition') ||
          rule.selectorText.includes('::after') ||
          rule.selectorText.includes('::before'))) {
        const key = rule.selectorText.replace(/\s+/g, ' ');
        // Only keep first 10 chars of CSS text for brevity
        effects[key] = rule.style.cssText.substring(0, 120);
      }
    }
  } catch(e) {}
}
console.table(Object.entries(effects).slice(0, 30));
```

**Shine/shimmer effects (card hover overlays):**

NeuralDeep-style cards use a `::after` pseudo-element with a linear-gradient that slides across on hover:

```css
.card-shine::after {
  content: "";
  pointer-events: none;
  background: linear-gradient(105deg,
    rgba(0,0,0,0) 40%, rgba(255,255,255,.02) 45%,
    rgba(255,255,255,.04) 50%, rgba(255,255,255,.02) 55%,
    rgba(0,0,0,0) 60%);
  transition: transform .6s;
  position: absolute; inset: 0;
  transform: translateX(-100%);
}
.card-shine:hover::after { transform: translateX(100%); }
```

### 9. Replicate the design as a catalog/directory page

> **Catalog architecture pattern moved to `portfolio-landing-maintenance`.** The sub-page structure, dynamic data from GitHub, search/filter, back-button, hamburger, and "agent skills vs personal stack" clarification are covered there. Below are the design-recovery-specific elements.

**NeuralDeep-style design tokens (for catalog cards):**

| Element | NeuralDeep style | Implementation |
|---|---|---|
| Cards/rows | Dark bg #18181b, border #27272a, radius 8px | `.skill-row { background: #18181b; border: 1px solid #27272a; border-radius: 8px; }` |
| Shimmer on hover | Pseudo-element with gradient translate | `::after` + `:hover::after { transform: translateX(100%); }` |
| Accent color | #0f8 on neuraldeep, use site's own accent | From `--accent` CSS variable |
| Category tags | Small colored pills per category | `.skill-cat-tag` with per-category colors |
| Agent badges | Rounded pills listing supported agents | `.agent-badge { border-radius: 20px; }` |
| Table grid layout | 4-column: #, Name+desc, Author, Stars | CSS grid `grid-template-columns: 40px 2fr 1fr 80px` |
| Search + filter | Live JS filtering on input + category buttons | `oninput` + `forEach(row => row.style.display = match ? 'grid' : 'none')` |

**Generation approach for large catalogs (50+ items):**
- Use Python to generate the HTML programmatically from a data list (f-strings, for loops)
- Save generated HTML to a temp file, then replace the section in the live file
- Add a `<script>` with DOMContentLoaded event listener for filter/search logic
- Avoid inline `onclick` on generated buttons -- use addEventListener to prevent conflicts
- Use a `catMap` (category label -> category code) lookup in JS for filter-to-category mapping

## Pitfalls

- **Site behind captcha/Bitrix composite cache:** may serve cached HTML without full CSS variables — force `?clear_cache=Y` or use Wayback Machine
- **CSS filenames with `?` query params:** glob patterns break — use exact filenames or quote the full path
- **Lazy-loaded images:** `src` may contain placeholder, real URL is in `data-src` attribute — grep both
- **Bitrix "no-store" cache headers:** don't assume the site is "down" because of 200 + no-store — the site is alive but uses aggressive anti-cache headers

## See Also

- `portfolio-landing-maintenance` — for implementing the recovered design as a geniok.ru sub-page (catalog architecture, hamburger menu, back button pattern)
- Reference: `references/react-landing-redesign.md` — redesigning an existing React/TypeScript landing page using a reference site's visual layout, component structure, and reusable project components (v2 dark theme, matching sections to existing components, fixing TS/build)
- Reference: `references/neuraldeep-skills-catalog.md` — full design tokens for neuraldeep-style catalog pages (card structure, shimmer effect, filter JS, category tag colors)
- Reference: `references/bitrix-aspro-digital.md` — Bitrix ASPRO Digital design patterns
