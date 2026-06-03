# Gemini API Reference for Media Generation

## Base URL

```
https://generativelanguage.googleapis.com/v1beta
```

## Authentication

**Header:** `x-goog-api-key: <key>`
**Get key:** https://aistudio.google.com

NOT `Authorization: Bearer` — that returns 401 for Gemini API.

## Models available

| Model | Use | Notes |
|-------|-----|-------|
| `gemini-3.1-flash-image-preview` | Image generation (Nano Banana 2) | Text+image→text+image, cheap |
| `veo-3.1-generate-preview` | Video generation (Veo 3.1) | Cinematic quality, may be async |
| `veo-3.1-lite-generate-preview` | Video generation (Veo 3.1 Lite) | Faster/cheaper than full Veo 3.1 |
| `veo-2.0-generate-001` | Video generation (Veo 2.0) | Previous generation |

## Image Generation (Gemini Flash Image)

**Endpoint:** `POST /models/gemini-3.1-flash-image-preview:generateContent`

**Request:**
```json
{
  "contents": [{
    "role": "user",
    "parts": [
      {"text": "Professional product photo of black sneakers, studio lighting, white background"},
      {"inline_data": {"mime_type": "image/jpeg", "data": "<base64>"}}
    ]
  }],
  "generationConfig": {
    "temperature": 1,
    "topK": 32,
    "topP": 1
  }
}
```

**Response (image in inlineData):**
```json
{
  "candidates": [{
    "content": {
      "parts": [
        {"text": "Here's your product photo..."},
        {"inlineData": {"mimeType": "image/png", "data": "<base64-data>"}}
      ]
    }
  }]
}
```

Extract: iterate `candidates[0].content.parts[]`, look for `part.inlineData.mimeType.startsWith('image/')`, construct `data:${mimeType};base64,${data}`.

## Video Generation (Veo)

**Endpoint:** `POST /models/veo-3.1-generate-preview:generateContent`

**Request:** Same structure as image generation (image input + text prompt).

**Response (sync — video in inlineData):**
```json
{
  "candidates": [{
    "content": {
      "parts": [
        {"inlineData": {"mimeType": "video/mp4", "data": "<base64>"}}
      ]
    }
  }]
}
```

**Response (async — operation):**
```json
{
  "name": "operations/abc123",
  "done": false
}
```

If async, poll:
```
GET /operations/abc123
Header: x-goog-api-key: <key>
```

Poll response when done:
```json
{
  "name": "operations/abc123",
  "done": true,
  "response": {
    "candidates": [{
      "content": {
        "parts": [
          {"inlineData": {"mimeType": "video/mp4", "data": "<base64>"}}
        ]
      }
    }]
  }
}
```

Veo can also return `part.fileData.fileUri` instead of inlineData — a Google Cloud Storage URI to the video.

## Cost Notes

- Gemini Flash Image: extremely cheap (~$0.0000003/input image, ~$0.0000025/output image)
- Veo 3.1: priced per second of generated video (varies by model tier)
- Check https://ai.google.dev/pricing for current rates
