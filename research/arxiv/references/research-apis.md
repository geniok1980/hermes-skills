# Supplementary Research APIs

When web search is blocked (CAPTCHA on Google/DuckDuckGo/Bing), use direct REST APIs. arXiv + Semantic Scholar cover papers; HuggingFace + GitHub cover models and code.

## HuggingFace API — Model Discovery

No auth needed for basic search. Rate limit: ~30 req/min.

### Search popular models by task

```bash
curl -s "https://huggingface.co/api/models?search=time-series-forecasting&sort=downloads&direction=-1&limit=20"
```

Fields returned: `modelId`, `downloads`, `likes`, `pipeline_tag`, `siblings`, `cardData`, `lastModified`.

### Search by specific model name

```bash
curl -s "https://huggingface.co/api/models?search=timesfm&sort=downloads&direction=-1&limit=5"
```

### Get specific model details

```bash
curl -s "https://huggingface.co/api/models/google/timesfm-2.0-500m-pytorch"
```

### Key fields for research

| Field | Meaning |
|-------|---------|
| `downloads` | Proxy for adoption/real-world use |
| `likes` | Community approval signal |
| `pipeline_tag` | Task type (e.g. `time-series-forecasting`) |
| `cardData.metadata.library_name` | Framework (`transformers`, `diffusers`, etc.) |
| `siblings` | File list including model weights |

## GitHub API — Repository Search

No auth needed for basic search (60 req/hr unauthenticated). `limit=N` for pagination.

### Search repos by topic + sort by stars

```bash
curl -s "https://api.github.com/search/repositories?q=time-series-forecasting+foundation+model&sort=stars&order=desc&per_page=10"
```

```bash
curl -s "https://api.github.com/search/repositories?q=crypto+price+prediction+machine+learning&sort=stars&order=desc&per_page=10"
```

### Search by language

```bash
curl -s "https://api.github.com/search/repositories?q=cryptocurrency+trading+language:python&sort=stars&order=desc&per_page=10"
```

### Key fields

| Field | Meaning |
|-------|---------|
| `stargazers_count` | Community interest / popularity |
| `description` | What the repo does |
| `language` | Primary programming language |
| `topics` | GitHub topics array |
| `updated_at` | Actively maintained? |
| `html_url` | Repo link |

### Output pattern for comparison

```bash
curl -s "..." | python3 -c "
import sys, json
data = json.load(sys.stdin)
for r in data.get('items', [])[:10]:
    print(f\"• {r['full_name']}  ⭐{r['stargazers_count']}  {r['description'][:120] if r.get('description') else 'N/A'}\")
"
```

## Pattern: Compare Models Across APIs

Goal: find best model for a task.

1. **HuggingFace →** search by task, sort by downloads/likes
2. **GitHub →** search by topic, sort by stars
3. **arXiv →** search by keyword for recent papers

```bash
# Chain: find papers on arXiv, then check HF for implementations, then GitHub for code
curl -s "https://export.arxiv.org/api/query?search_query=all:cryptocurrency+AND+all:deep+learning+AND+all:prediction&max_results=10"
curl -s "https://huggingface.co/api/models?search=cryptocurrency+price+prediction&sort=downloads&direction=-1&limit=5"
curl -s "https://api.github.com/search/repositories?q=cryptocurrency+price+prediction+deep+learning&sort=stars&order=desc&per_page=5"
```

## Rate Limits Summary

| API | Unauthenticated | With Token |
|-----|-----------------|------------|
| arXiv | ~1 req / 3s | Same |
| Semantic Scholar | 1 req/s | 100 req/s (free key) |
| HuggingFace | ~30 req/min | Higher (free token) |
| GitHub | 60 req/hr | 5000 req/hr (free token) |

For large-scale research, generate tokens for HF and GitHub to bypass rate limits.

## Example: Full Research Workflow (this technique used in a real session)

Goal: "best ML for crypto time series trading"

1. arXiv → search for recent papers on crypto prediction + deep learning
2. HuggingFace → search for time series foundation models, sorted by downloads
3. GitHub → search for top-starred repos on crypto price prediction
4. Cross-reference: which models from HF have papers on arXiv? Which repos are actively maintained?
5. Compile findings into a ranked comparison by adoption + recency

Result: Chronos (1.9M downloads) and TimesFM (89k downloads + 20k stars) are top foundation models; Kronos (27k stars) is top dedicated financial model; FinRL (3.2k stars) for RL-based trading.
