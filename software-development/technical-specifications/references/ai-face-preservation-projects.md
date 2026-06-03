# AI Face-Preserving Image Generation Projects

Reference for selecting a base project for photo → new location generation platforms.

## Tier 1: Best Fit (Zero-shot ID preservation with web UI)

### InstantID — 12k ⭐
https://github.com/instantX-research/InstantID
- Zero-shot Identity-Preserving Generation in seconds
- Has Gradio web demo
- Uses InsightFace for face embedding + ControlNet + SDXL
- Good quality, fast inference
- Last updated ~2 years ago
- Python (PyTorch)

### PhotoMaker (TencentARC) — 10.1k ⭐
https://github.com/TencentARC/PhotoMaker
- CVPR 2024 — personalized photo generation
- Has Gradio demo
- Stacking ID embeddings approach
- PhotoMaker V2 available
- Last updated ~2 years ago
- Python (PyTorch)

## Tier 2: Good Fit

### PuLID — 3.5k ⭐
https://github.com/ToTheBeginning/PuLID
- NeurIPS 2024 — Pure and Lightning ID Customization
- Works with FLUX.1
- Has app.py demo
- Contrastive alignment approach
- Better face fidelity than InstantID in some cases
- Last updated ~10 months ago
- Python (PyTorch)

## Infrastructure Frameworks

### ComfyUI — 114k ⭐
https://github.com/Comfy-Org/ComfyUI
- Node-based GUI for diffusion models
- Has REST API
- Supports custom nodes (InstantID, PuLID nodes available)
- Most flexible, but highest complexity
- Actively maintained (updated 6 hours ago)
- Python (PyTorch)

### FaceFusion — 28.4k ⭐
https://github.com/facefusion/facefusion
- Full face manipulation platform
- Has web UI and API
- More about face swapping, less about scene generation
- Actively maintained (last month)

## Building Blocks

### IP-Adapter (Tencent) — 6.6k ⭐
https://github.com/tencent-ailab/IP-Adapter
- Image prompt adapter for text-to-image models
- IP-Adapter-Face variant for face preservation
- Can be combined with SDXL, SD3
- Good as a component in a larger pipeline

## Alternatives: No-GPU Approach

### OpenRouter API (Nano Banana)
https://openrouter.ai/
- Model: `google/gemini-*-flash-image-preview`
- Price: ~$0.0000015/image
- No GPU needed — pure REST API
- Works with Bun/Node (any HTTP client)
- TypeScript SDK available
- Multi-modal: send reference photo + text prompt
- Pros: Zero infrastructure, pay-per-use, instant scaling
- Cons: Less control over face preservation quality, dependency on external API

### Replicate
https://replicate.com/
- Hosted models: SDXL, InstantID, etc.
- Pay-per-use (varies by model)
- REST API + Node.js client library
- Good middle ground: no GPU, but runs specific models

## Real-World Decision: Which One to Pick?

From a production build session (May 2026):

**The user chose InstantID → then pivoted to OpenRouter/Nano Banana** after seeing the cost and complexity comparison. The whole platform ended up being pure TypeScript/Bun with zero GPU infra.

### Decision Flow

```
"What project can I build on?"
  → Found InstantID (12k⭐), PhotoMaker (10k⭐), PuLID (3.5k⭐)
  → All need Python + GPU
  → Compared with OpenRouter API (serverless, $0.0000015/image)
  → User chose OpenRouter (no GPU, Bun-native, 99.9% margin)
  → Result: full-stack TypeScript project, no Python at all
```

### Lesson

Don't default to local GPU even when the user asks "what project can I build on." Present the serverless API as a viable alternative — for many products, the simplicity and cost advantage outweigh model control.
