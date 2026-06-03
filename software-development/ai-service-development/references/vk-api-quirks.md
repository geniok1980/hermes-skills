# VK API Quirks

## Endpoints

| Method | What it does | Key params |
|--------|-------------|------------|
| `wall.get` | Get posts from group/user wall | `owner_id` (negative for groups), `count` (max 100), `offset` |
| `groups.getMembers` | Get group members | `group_id` (positive), `count` (max 1000), `offset`, `fields` |
| `groups.getById` | Get group info | `group_id`, `fields` |
| `newsfeed.search` | Search posts globally | `q`, `count` (max 100), `extended` |

## Authentication

VK API accepts **service keys** (получить: vk.cc → Мой профиль → Разработчикам → API → Сервисный ключ) or **user access tokens**.

Set via env: `VK_TOKEN=<service_key>` or pass `--token` flag.

## Rate limits

Strict: **3 requests per second** per method. Hard-block at 5/sec.

Implementation:
```python
request_count = 0
def _call(method, params):
    request_count += 1
    if request_count % 3 == 0:
        time.sleep(0.4)  # 400ms pause every 3 requests
```

## Error codes

| Code | Description | Meaning |
|------|-------------|---------|
| 1 | Unknown error | Rare, retry |
| 6 | Too many requests | HIT RATE LIMIT — increase pause |
| 15 | Access denied | Group is private or token lacks scope |
| 113 | Invalid user id | Wrong ID format |
| 201 | Access to groups denied | Token needs `groups` scope |
| 100 | Invalid parameters | Wrong param name or format |

## Group ID quirks

- For `wall.get`: `owner_id` must be **negative** for groups (e.g. `-12345`), positive for users
- For `groups.getMembers`: `group_id` is **positive** (no minus sign)
- Screen names work: pass `group_id="durov"` instead of numeric ID

## Fields for getMembers

Useful fields: `id, first_name, last_name, city, country, sex, bdate, photo_50, photo_100, photo_200, last_seen, online, online_mobile, domain`

Pass as comma-separated string.

## Search limitations

- `newsfeed.search` returns posts from last 7 days only
- Results are heavily filtered — not all matching posts returned
- For historical data use `wall.get` with large offset (but API caps at ~2000 posts)

## Working implementation

See `/root/ai-agent-services/vk-parser-bot/vk_parser.py` for a complete working parser with all these quirks handled.
