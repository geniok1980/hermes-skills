# Aidentika Demo Assets (discovered 2026-05-31)

Source: https://aidentika.com/ (public site)

## Product Images

| Asset | URL |
|-------|-----|
| Dress | `/demo/products/dress.webp` |
| Gel | `/demo/products/gel.webp` |
| Chair | `/demo/products/chair.webp` |

## Concept Images

| Asset | URL |
|-------|-----|
| Studio (catalog shot) | `/demo/concepts/dress_studio.webp` |
| On model | `/demo/concepts/dress_model.webp?v=2` |
| Flatlay (composition) | `/demo/concepts/dress_flatlay.webp` |

## Merge Results (before/after)

| Asset | URL |
|-------|-----|
| Output 1 | `/demo/merge/output-1.webp` |
| Output 2 | `/demo/merge/output-2.webp` |
| Output 3 | `/demo/merge/output-3.webp` |

## Category Examples (bundled via Next.js static)

| Category | File hash |
|----------|-----------|
| Jewelry | `yingtu-gen-1767965669517` |
| Shoes | `yingtu-1767964585608` |
| Tea & drinks | `yingtu-1767970680846` |
| Pet supplies | `yingtu-1767967015476` |
| Electronics | `yingtu-1767966044531` |
| Home goods | `yingtu-1767967435030` |
| Clothing | `djinsi` |

URL pattern: `https://aidentika.com/_next/static/media/{hash}.{extension}.webp`

## Demo Videos (from #ai-video section)

| Asset | URL | Size |
|-------|-----|------|
| Demo 1 | `/demo/video/en/demo-1.webm` | ~276K |
| Demo 2 | `/demo/video/en/demo-2.webm` | ~1M |
| Demo 3 | `/demo/video/en/demo-3.webm` | ~429K |

## Usage in Vite project

1. Copy to `apps/web/public/`:
```bash
cp *.webp /root/ai-photostudio/apps/web/public/
cp *.webm /root/ai-photostudio/apps/web/public/
```
2. Reference in React as `/filename.webp` (Vite serves `public/` at root `/`)
3. Rebuild with `docker compose build` then `docker rm -f ai-photostudio && docker compose up -d`

## Download command

```bash
# Download all category examples
for pair in \
  "yingtu-gen-1767965669517|jewelry" \
  "yingtu-1767964585608|shoes" \
  "yingtu-1767970680846|tea_drinks" \
  "yingtu-1767967015476|pet_supplies" \
  "yingtu-1767966044531|electronics" \
  "yingtu-1767967435030|home_goods" \
  "djinsi|clothing"; do
  hash="${pair%%|*}"
  name="${pair##*|}"
  curl -sL "https://aidentika.com/_next/image?url=%2F_next%2Fstatic%2Fmedia%2F${hash}.2c226206.webp&w=3840&q=75" -o "${name}.webp"
done
```

Note: exact file extensions in the static media path may vary between builds.
Preferred: use Next.js image proxy URL with `w=3840&q=75` for highest quality.
