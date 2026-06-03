# Aidentika Feature Analysis Guide

How to study Aidentika's feature set and replicate features in ai-photostudio.

## Where to look

| Target | URL | What to extract |
|--------|-----|-----------------|
| **Main website** | `https://aidentika.com` (or `/en` for English) | Hero text, service sections, features lists, pricing tiers, FAQ |
| **App interface** | `https://app.aidentika.com` | Mode tabs (Photo/Video/Card), concepts per mode, UI layout, settings options, generation results |
| **Page source** | View page source / inspect | Internationalization strings (JSON blobs in Next.js page props), feature flags, API endpoints |
| **Pricing data** | Dedicated pricing section on main site | Spark ratios (e.g., "50 sparks = 12 images or 3 videos"), tier names, prices |

## What to extract for replication

### For each generation mode:
1. **Mode name** — both display name and internal key
2. **Icon/emoji** — what represents the mode
3. **UI flow** — step-by-step user journey
4. **Concepts** — sub-options within the mode (e.g., "catalog shot", "on model", "composition")
5. **Settings** — any unique configuration options (duration, loop, aspect ratio)
6. **Prompt structure** — what user describes, what AI generates

### For the landing page:
1. **Section copy** — headlines, descriptions, feature lists
2. **CTA buttons** — text and destinations
3. **Service cards** — icon, title, description, features
4. **Comparison tables** — traditional vs AI (time/cost)
5. **Example gallery** — category labels

### For pricing:
1. **Spark cost per generation** — derive from (total sparks in tier ÷ items per tier)
2. **Pricing ratio across modes** — e.g., video costs 4x more than images
3. **Tier structure** — names, prices, quantities, popularity badges

## Extraction technique

```typescript
// Step 1: Load the page
browser_navigate('https://aidentika.com')

// Step 2: Scroll through all sections
browser_scroll('down')

// Step 3: Read the accessibility snapshot for text
browser_snapshot(full: true)

// Step 4: For the app interface, click mode tabs
browser_click(ref: '@e...')  // Click "Video" tab
browser_snapshot()
// Note what changes in the UI

// Step 5: Extract JSON data from page source
browser_console(expression: 'JSON.parse(document.querySelector("#__NEXT_DATA__")?.textContent || "{}")')
```

## Known Aidentika modes (as of May 2026)

| Mode | Icon | Description |
|------|------|-------------|
| **Photo** | 📸 | Product photo generation with concepts (catalog, on-model, composition) |
| **Card** | 🃏 | Infographic card generation with badge/price/text overlays |
| **Video** | 🎬 | Video generation (5/10 sec, loop, card mode, scenario description) |

## Localization structure

Aidentika uses Next.js with react-intl. Look for `messages` objects in page props:
- `"videoTool"` — all video-related UI strings
- `"inspector"` — result viewer strings
- `"pricing"` — pricing tier strings
- `"catalog"` — category and concept definitions
