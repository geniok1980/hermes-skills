# OpenRouter / Nano Banana for AI Image Generation

Using OpenRouter API for serverless AI image generation — an alternative to running local GPU models.

## Why API-Based Generation

| Aspect | Local GPU (InstantID + SDXL) | OpenRouter API |
|--------|------------------------------|----------------|
| GPU needed | RTX 3090/4090+ ($2000+) | ❌ None |
| Setup | Docker + CUDA + Python | HTTP API call |
| Cost | ~$0.10-0.50/image (GPU rental) | ~$0.0000015/image |
| Latency | 10-30s | 2-5s |
| Scaling | Complex | Instant |
| Control | Full (prompts, steps, etc.) | Limited to API params |
| Stack | Python + CUDA | TypeScript/Bun (no Python) |

## Key Model

**`google/gemini-2.5-flash-image-preview`** (or newer variants)
- Price: $0.0000015 per image
- Multi-modal: accepts text + image input
- Generates images with the reference person in new scenes

## Integration Pattern (Bun/TypeScript)

```typescript
const response = await fetch("https://openrouter.ai/api/v1/chat/completions", {
  method: "POST",
  headers: {
    "Authorization": `Bearer ${OPENROUTER_API_KEY}`,
    "Content-Type": "application/json",
  },
  body: JSON.stringify({
    model: "google/gemini-2.5-flash-image-preview",
    messages: [{
      role: "user",
      content: [
        { 
          type: "text", 
          text: "Generate this person on a tropical beach at sunset, 
                 photorealistic, cinematic lighting, 8k quality" 
        },
        { 
          type: "image_url", 
          image_url: { url: userPhotoBase64 }  // or URL
        }
      ]
    }]
  })
});

const data = await response.json();
const generatedImageUrl = data.choices[0].message.images[0].image_url.url;
```

## OpenRouter Pricing Matrix (May 2026)

| Model | Price/image |
|-------|-------------|
| google/gemini-3.5-flash | $0.0000015 |
| google/gemini-3.1-flash-lite | $0.00000025 |
| google/gemini-3.1-flash-image-preview | varies |

## Other OpenRouter Models for Image Gen

Check OpenRouter model list for available image-capable models:
```
GET https://openrouter.ai/api/v1/models
```

## Location Prompts (Example Library)

When writing a ТЗ with location-based generation, predefine prompts:

| Location | Prompt |
|----------|--------|
| Beach sunset | "person on a tropical beach at sunset, warm golden light, ocean waves, palm trees, photorealistic, 8k" |
| Times Square | "person in Times Square New York City at night, neon lights, busy streets, cinematic" |
| Outer Space | "person floating in outer space, Earth in background, stars, nebula, sci-fi, cinematic lighting" |
| Medieval Castle | "person in a grand medieval castle hall, armor, torches, stone walls, dramatic lighting" |
| Japanese Garden | "person in a traditional Japanese garden, cherry blossoms, pond, wooden bridge, serenity" |
| Futuristic Office | "person in a futuristic office, holographic displays, sleek design, blue lighting, cyberpunk" |
