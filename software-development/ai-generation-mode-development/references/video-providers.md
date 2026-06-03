# Video Generation Providers

## fal.ai (Kling 1.6 Image-to-Video)

- **Endpoint:** `https://fal.run/fal-ai/kling-video/v1.6/standard/image-to-video`
- **Auth:** Header `Authorization: Key <FAL_API_KEY>`
- **Body:**
  ```json
  {
    "image_url": "data:image/jpeg;base64,...",
    "prompt": "Cinematic video of ...",
    "guidance_scale": 7,
    "num_frames": 24
  }
  ```
- **Response:** Returns `{ video: { url: "..." } }` or queues with `{ status: "IN_QUEUE", request_id: "..." }`
- **Polling:** `GET https://fal.run/fal-ai/kling-video/v1.6/standard/requests/{request_id}/status`
- **Cost:** ~$0.05 per 5-second video
- **Registration:** https://fal.ai — free credits on signup

## OpenRouter (Image Generation Only — NOT Video)

- **Current model:** `google/gemini-2.5-flash-image-preview`
- **Uses chat completions endpoint** `https://openrouter.ai/api/v1/chat/completions`
- **Image cost:** ~$0.0003/image
- **Video:** OpenRouter does NOT support video generation as of May 2026

## If neither provider works for a desired modality

1. Check OpenRouter `/api/v1/models` for models with the modality you need
2. Check fal.ai model catalog for the task
3. Direct API integration as a last resort (Runway, Google Veo, etc.)
