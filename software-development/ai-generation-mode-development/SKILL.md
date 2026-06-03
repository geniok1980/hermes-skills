---
name: ai-generation-mode-development
title: AI Generation Mode Implementation
description: Implement a new AI generation mode (product photo, video, interior, etc.) in the ai-photostudio monorepo following Aidentika's feature set, with consistent DB → API → Frontend → Landing pattern.
tags: [aidentika, ai-generation, rabbit-api, bun, hono, react, typescript, monorepo]
---

# AI Generation Mode Implementation

Implement a new AI generation mode in the ai-photostudio monorepo by analyzing Aidentika's feature set and following the existing architecture patterns.

## When to use

- User asks to add a new AI generation capability (photo, video, interior, etc.)
- User says "в Aidentika есть X, надо чтобы у нас тоже было"
- Adding a new mode to the ProductDashboard mode switcher
- Updating the landing page to describe a new service

## Prerequisites

- Working directory: `/root/ai-photostudio`
- Git branch: `main`
- Docker container: `ai-photostudio` running on port 3007

## Architecture

```
monorepo (Turborepo, bun workspaces)
├── apps/api/           ← Hono.js backend (Bun)
│   ├── src/
│   │   ├── db/seed.ts  ← Generation modes, concepts, categories
│   │   ├── routes/generate.ts ← POST handler for all modes
│   │   ├── services/   ← Provider API calls (openrouter.ts, video.ts)
│   │   └── index.ts    ← Route registration
│   └── package.json
├── apps/web/           ← React/Vite frontend
│   └── src/
│       ├── lib/api.ts  ← API client (generatePhoto, types)
│       ├── pages/ProductDashboard.tsx ← Mode UI (switcher, forms, tips)
│       ├── pages/Landing.tsx          ← Public marketing page
│       └── components/Navbar.tsx      ← Navigation links
└── docker-compose.yml  ← Port 3007→3001
```

### Provider: Google Gemini API (single provider for all generation)

| Type | Model | Endpoint |
|------|-------|----------|
| **Images** | `gemini-3.1-flash-image-preview` (Nano Banana 2) | `.../models/{model}:generateContent` |
| **Video** | `veo-3.1-generate-preview` | `.../models/{model}:generateContent` |
| **Infographics** | `gemini-3.1-flash-image-preview` | `.../models/{model}:generateContent` |

**One API key for everything**: `GEMINI_API_KEY` (get at https://aistudio.google.com).

**Gemini API** — base URL: `https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent`
- Auth: `x-goog-api-key` header (NOT Bearer token)
- Body: standard `contents[{parts[{text, inline_data}]}]` format
- Image response: `candidates[0].content.parts[].inlineData` (base64)
- Video response: `candidates[0].content.parts[].inlineData` or `fileData.fileUri`; Veo may use async operations (poll via `.../operations/{name}`)
- DO NOT use OpenRouter or fal.ai — all media generation goes through Gemini API directly

## Steps

### 1. Research competitor (Aidentika)

Use browser tools to study Aidentika's feature:
```typescript
// Navigate to the app
browser_navigate('https://app.aidentika.com')
// Click the relevant mode tab
browser_click('@e...') // Photo/Card/Video buttons
// Read translations/localization from page source for feature detail
```

Also check the main site for marketing copy:
```typescript
browser_navigate('https://aidentika.com')
// Scroll through sections, note features, copy, pricing ratios
```

Key info to extract:
- Mode name, icon, description
- Concepts/sub-options available
- Pricing ratio (e.g., "50 sparks = 12 images or 3 videos")
- UI layout and feature descriptions
- Any specific settings (duration, loop, etc.)

**Download demo assets for landing page reference:**
Aidentika's public site hosts real demo images and videos that can be extracted for landing page design:

```typescript
// Step 1: Get all images from the page
browser_get_images()
// → returns Array<{src, alt, width, height}>

// Step 2: Extract video sources from the #ai-video section
browser_console({expression: `document.querySelector('#ai-video video')?.getAttribute('src')`})

// Step 3: Download assets via curl (best quality with w=3840&q=75)
// Product examples by category (on aidentika.com/_next/static/media/...)
// Demo concept images (on /demo/concepts/<name>.webp)
// Merge results (on /demo/merge/output-*.webp)
// Demo videos (on /demo/video/en/demo-*.webm)
```

Pattern: use `browser_get_images()` to list all image URLs → `curl -sL` to download. Videos are in `<video src="/demo/video/en/demo-*.webm">` in the #ai-video section.

### 2. Database — seed.ts

In `apps/api/src/db/seed.ts`:

```typescript
// a) Generate a UUID for the new mode
const videoModeId = uuidv4();

// b) Add mode entry in generation_modes
insertMode.run({
  $id: videoModeId,
  $name: 'video',
  $display_name: 'Видео',
  $description: 'Создайте динамичное видео из фото товара',
  $icon: '🎬',
  $sort_order: 4,  // next available
});

// c) Add concepts (prompts stored in DB, not hardcoded)
insertConcept.run({
  $id: uuidv4(),
  $mode_id: videoModeId,
  $name: 'product_showcase',
  $display_name: 'Обзор товара',
  $description: 'Плавный обзор товара со всех сторон',
  $prompt_template: 'Cinematic product showcase video of {product_description}. Smooth 360 rotation...',
  $sort_order: 1,
});
```

**Rules:**
- Every prompt goes in a concept in the DB, never hardcoded in the route
- Prompt templates use `{product_description}` as the placeholder
- Add UNIQUE constraint on `name` column for idempotent re-seeding
- Update package descriptions to mention video equivalents

### 3. API Service

Create `apps/api/src/services/<mode>.ts` for the Gemini API pattern:

```typescript
const GEMINI_ENDPOINT = 'https://generativelanguage.googleapis.com/v1beta/models';
const MODEL = 'gemini-3.1-flash-image-preview'; // or 'veo-3.1-generate-preview'

export async function generate<Type>(
  photoBase64: string,
  prompt: string
): Promise<{ /* videoUrl or imageUrl */: string; durationMs: number }> {
  const apiKey = process.env.GEMINI_API_KEY;
  if (!apiKey) throw new Error('GEMINI_API_KEY ...');

  const response = await fetch(`${GEMINI_ENDPOINT}/${MODEL}:generateContent`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'x-goog-api-key': apiKey,   // NOT Bearer token
    },
    body: JSON.stringify({
      contents: [{
        role: 'user',
        parts: [
          { text: prompt },
          { inline_data: { mime_type: 'image/jpeg', data: photoBase64 } },
        ],
      }],
    }),
  });

  // Extract from response...
}
```

**Pattern:**
- Export `generate<Type>(photoBase64, prompt)` with the same signature
- Read key from `process.env.GEMINI_API_KEY` (single key for all modes)
- POST to Gemini API `generateContent` endpoint with the model name
- Handle both sync response (inlineData) and async operations (polling) for Veo

**For video (Veo):** the call may return an async operation. Poll `https://generativelanguage.googleapis.com/v1beta/{operationName}` until done.

### 4. API Route — generate.ts

In `apps/api/src/routes/generate.ts`:

```typescript
// a) Add import at top
import { generateVideo } from '../services/video';

// b) Add mode handler in POST route, between the existing product/interior handler
// and the portrait fallback:
if (currentModeId === 'video') {
  if (!conceptId) { return c.json({ error: '...' }, 400); }
  // ... validate concept, user, free limit ...
  // ... insert generation with mode_id ...
  generateAndSaveVideo(generationId, prompt, user.id, isFreeUser)
    .catch(err => ...);
  return c.json({ generation: { ... } }, 202);
}

// c) Create generateAndSave<Mode> function before export:
async function generateAndSaveVideo(
  generationId: string, prompt: string, userId: string, isFreeUser: boolean
): Promise<void> { ... }
```

**Spark cost rule:** Video/photos cost 4 sparks each. Deduct via:
```typescript
if (userData.spark_balance >= 4) {
  // Deduct sparks and record transaction
} else if (userData.balance_generations > 0) {
  // Deduct 1 generation balance
}
```

### 5. Frontend — API client

In `apps/web/src/lib/api.ts`:

- Update `GenerationRequest` interface if new fields needed (e.g., `videoDescription`, `videoDuration`)
- Update `generatePhoto()` to pass the correct fields for the new mode
- For video modes, pass `videoDescription` as `productDescription` in the API call

### 6. Frontend — ProductDashboard

In `apps/web/src/pages/ProductDashboard.tsx`:

The new mode name must be added in **every mode-string-conditional** in the file. Scan for all these locations:

| Location | What to change | Example |
|---|---|---|
| `type ModeName` union | Add `\| 'food'` | `'portrait' \| 'product' \| 'interior' \| 'video' \| 'food'` |
| Header description | Add new line | `{activeMode === 'food' && '...'}` |
| Upload label | Add new ternary | `activeMode === 'food' ? 'Сфотографируйте блюдо' : 'Загрузите фото товара'` |
| `selectedConcept` validation | Add mode to `||` chain | `(activeMode === 'product' \|\| ... \|\| activeMode === 'food') && !selectedConcept` |
| `disabled` button condition | Add mode to `||` chain | Same pattern as concept validation |
| Generate button text | Add new mode branch | `activeMode === 'food' ? 'Сгенерировать фото блюда'` |
| "How it works" section | Add new `<div className="space-y-4...">` block with 3 steps | Copy existing mode's block structure |
| "Tips" section title | Add to ternary | `activeMode === 'food' ? 'Советы по фуд-съёмке'` |
| "Tips" content | Add new `<ul>` block | Food-specific tips |

**Common miss:** the `selectedConcept` validation and `disabled` button condition both use the same `||` chain. Always add the new mode to BOTH.

**Mode switcher renders all modes dynamically from the API.** No changes needed to the switcher itself — just ensure the new mode is in seed.ts.

**Category selector** — if the new mode uses categories (like food), enable it via:
```tsx
{(activeMode === 'product' || activeMode === 'video' || activeMode === 'food') && (
  <div className="card">{/* category grid */}</div>
)}
```

The existing categories already include `food_drinks` (Еда и напитки), `home_goods`, etc. — no need to add new categories unless the new mode needs a completely different taxonomy.

**Concept and description** sections follow the same enable pattern — add the new mode to the parent conditional wrapper.

### 7. Landing Page — Landing.tsx

Update `apps/web/src/pages/Landing.tsx`:

```typescript
// a) Add the service card to the services array (before the interior card)
{ icon: '🍽️', title: 'Меню / Еда', ... }

// b) Update hero badge text
"AI-генерация фото, товаров, интерьеров, меню и видео"

// c) Update hero h1 if needed
"Портреты, товары, интерьеры, меню и видео на основе нейросетей"

// d) Update hero subtitle
"...дизайн интерьера, фото блюда для меню или видео для маркетплейсов"

// e) Update stats line
"🎨 Портреты, товары, интерьеры, меню, видео"

// f) Update "N формата" title
"Пять форматов — одна платформа" (bump number, update grid to match)

// g) Update services grid column count when adding a card
// If adding mode #5, change md:grid-cols-4 to md:grid-cols-5
<div className="grid md:grid-cols-5 gap-6">

// h) Add new detail section — insert between the Video section and Examples section
// Full section with icon, title, description, features grid, image grid, CTA button

// i) Update features section text if it mentions old mode count
// Search for "Четыре формата" / "Три формата" in the features section

// j) Update the examples array with a relevant example (food/menu image)
const examples = [
  { id: 1, label: 'Украшения', image: '/jewelry.webp' },
  // ...
  { id: 8, label: 'Еда и напитки', image: '/tea_drinks.webp' },
];

// k) Update the features section card that mentions mode count
{ title: 'Пять форматов', description: 'Портреты, товары, интерьеры, меню и видео — всё в одном сервисе' }
```

### 7b. Replace placeholder gradients with real images

After you've downloaded demo assets from Aidentika (see references/aidentika-assets.md), copy them to Vite's `public/` directory so they're served at root `/`:

```bash
cp /path/to/downloads/*.webp /root/ai-photostudio/apps/web/public/
cp /path/to/downloads/*.webm /root/ai-photostudio/apps/web/public/
```

Then replace gradient/icon placeholders with `<img>` tags pointing to `/filename.ext`:

**Examples section** — replace the `placeholderImages` array (emojis + gradients) with real images:

```typescript
const examples = [
  { id: 1, label: 'Украшения', image: '/jewelry.webp' },
  { id: 2, label: 'Обувь', image: '/shoes.webp' },
  { id: 3, label: 'Одежда', image: '/clothing.webp' },
  { id: 4, label: 'Электроника', image: '/electronics.webp' },
  { id: 5, label: 'Товары для дома', image: '/home_goods.webp' },
  { id: 6, label: 'Чай и напитки', image: '/tea_drinks.webp' },
  { id: 7, label: 'Товары для животных', image: '/pet_supplies.webp' },
  { id: 8, label: 'Портретная съёмка', image: '/merge_output1.webp' },
];
```

Then render as `<img>` instead of emoji blocks:
```tsx
<div className="grid grid-cols-2 md:grid-cols-4 gap-4">
  {examples.map((img) => (
    <div key={img.id} className="group relative aspect-square rounded-2xl overflow-hidden bg-gray-800">
      <img
        src={img.image}
        alt={img.label}
        className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500"
      />
      <div className="absolute inset-0 bg-gradient-to-t from-black/70 via-transparent to-transparent opacity-0 group-hover:opacity-100 flex items-end p-4">
        <p className="text-white text-sm font-medium">{img.label}</p>
      </div>
    </div>
  ))}
</div>
```

**Detail section image placeholders** — replace gradient divs with image grids:
- Portrait section: grid of merge outputs (`/merge_output1.webp`, `/merge_output2.webp`, `/merge_output3.webp`)
- Product section: 2×2 grid of category examples (`/jewelry.webp`, `/shoes.webp`, `/electronics.webp`, `/clothing.webp`)
- Food section: gradient placeholders with food emoji (unless food demo images exist)
- Interior section: existing pattern uses `/interiors/gostinaya-*.jpg`

**Video section** — replace gradient placeholder with a `<video>` element:

```tsx
<div className="relative aspect-video overflow-hidden rounded-xl bg-gray-800">
  <video
    src="/demo_video2.webm"
    className="w-full h-full object-cover"
    muted
    autoPlay
    loop
    playsInline
  />
  {/* Optional play button overlay */}
  <div className="absolute inset-0 flex items-center justify-center pointer-events-none">
    <div className="w-12 h-12 rounded-full bg-red-500/80 flex items-center justify-center">
      <svg className="w-5 h-5 text-white ml-0.5" fill="currentColor" viewBox="0 0 24 24">
        <path d="M8 5v14l11-7z" />
      </svg>
    </div>
  </div>
</div>
```

Images in `public/` are served at root `/` by Vite. No import needed — just use `<img src="/filename.webp">`.

### 8. Deploy

```bash
# Commit
cd /root/ai-photostudio
git add -A
git commit -m "feat: add <mode> generation"

# Build Docker image
docker compose build

# IMPORTANT: docker compose up -d may NOT recreate the container
# Force recreation:
docker rm -f ai-photostudio
docker compose up -d

# Reseed database (new modes/concepts need to be in the DB)
sleep 5
docker exec ai-photostudio sh -c "cd /app/apps/api && bun run src/db/seed.ts"

# Verify
curl -s http://localhost:3007/ | grep -o '<heading[^>]*>[^<]*</heading>' | head -5
```

### Setting up GEMINI_API_KEY in production

Add to `docker-compose.yml`:
```yaml
environment:
  - GEMINI_API_KEY=your_key_here
```

Get key at https://aistudio.google.com → Get API Key. This single key covers both image (Gemini Flash Image) and video (Veo) generation.

## Pitfalls

### Gemini API: use x-goog-api-key, NOT Bearer token
The Gemini API authenticates via `x-goog-api-key` header, not `Authorization: Bearer`. Using Bearer will return 401/403. Always use:
```typescript
headers: { 'x-goog-api-key': process.env.GEMINI_API_KEY }
```

### Veo async operations need polling
Veo video generation may return an async operation response instead of immediate video. Check for `data.name` starting with `operations/` or `data.done === false`. If async, poll `https://generativelanguage.googleapis.com/v1beta/{operationName}` every 5s until `done: true`. Set a timeout (60+ iterations).

### Single GEMINI_API_KEY replaces all provider keys
One key from https://aistudio.google.com covers both image (Gemini) and video (Veo) generation. No need for OPENROUTER_API_KEY or FAL_API_KEY. Update docker-compose.yml environment to use only GEMINI_API_KEY.

### Docker container NOT recreated after build
`docker compose build` creates a new image, but `docker compose up -d` **may not recreate the container** — the old one keeps running with stale code. Always use:
```bash
docker rm -f ai-photostudio && docker compose up -d
```

### Seed duplicates on re-run
INSERT OR IGNORE only catches exact primary key collisions — with UUIDs generated fresh each run, every seed invocation creates new rows. **Solution**: ensure UNIQUE constraints on the `name` column in the table schema, then INSERT OR IGNORE will skip rows with the same logical key.

### Frontend not updating
If the Docker image was built before the latest changes were committed to the branch used by the Dockerfile's COPY, the old frontend will be deployed. **Fix**: always commit before building, or verify the build context in `docker compose build` picks up the right branch.

### Landing page changes not visible after deploy
Check the HTML response directly — if the container wasn't recreated, `docker compose up -d` silently uses the stale container. Force recreation.

### `placeholderImages` renamed to `examples`
The Landing.tsx `placeholderImages` array was renamed to `examples` in a prior session. If your edit references `placeholderImages`, TypeScript will error — use `examples` instead. The structure is `{ id: number, label: string, image: string }`.

### Grid column count must match service count
When adding a new service card, count the total number of services and update `md:grid-cols-N` accordingly. 4 services → `md:grid-cols-4`, 5 services → `md:grid-cols-5`. Forgetting this causes the last card to wrap awkwardly.

## Verification

```bash
# Landing page has the new mode
curl -s http://localhost:3007/ | grep -c 'Название режима'

# API returns the new mode
curl -s http://localhost:3007/api/modes | python3 -c "import sys,json; print([m['name'] for m in json.load(sys.stdin)['modes']])"

# DB has concepts for the new mode
docker exec ai-photostudio sh -c "cd /app/apps/api && bun run src/db/seed.ts" | grep -c 'Seeding'
```
