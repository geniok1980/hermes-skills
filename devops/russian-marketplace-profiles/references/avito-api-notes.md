# Avito API Notes

## Authentication

**Endpoint:** `POST https://api.avito.ru/token`

**Grant type:** `client_credentials`

**Parameters:**
- `client_id` — from Avito developer app
- `client_secret` — from Avito developer app
- `grant_type=client_credentials`
- `scope=user:read ads:read ads:write`

**Response:**
```json
{
  "access_token": "EzU693...",
  "expires_in": 86400,
  "scope": "user:read ads:read ads:write",
  "token_type": "Bearer"
}
```

Token is valid for 24 hours. Must be refreshed before each session.

## Known Working Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/token` | POST | Get access token |
| `/core/v1/accounts/self` | GET | Get user profile (limited with client_credentials) |
| `/ads/v1/ads` | GET | List existing ads |
| `/core/v1/categories?parent_id=0` | GET | Get root categories (returns object, not array) |

**Actual behavior (tested May 2026):**
- Without explicit scopes, `client_credentials` token still provided access to `/core/v1/accounts/self` (user info with name, email, phone, profile_url)
- Email: `geniok@mail.ru`
- Name: `Юпитер`
- Phone: `+7 9179534424`
- Profile URL: `https://www.avito.ru/user/7eecdfa9056d7b9c72667feec5ca175a/profile`

**CRITICAL: client_credentials is READ-ONLY for items**
- `GET /core/v1/items` → returns empty list (works, read-only)
- `POST /core/v1/items` → not tested (likely needs authorization_code)
- `GET /item/categories` → "no Route matched with those values" (this endpoint does NOT exist)
- `GET /core/v1/categories` → "no Route matched with those values" (same)
- `GET /autoload/v2/profile` → "Получение профиля недоступно" (autoload requires different auth)
- No combination of `scope` parameters changed behavior during testing

## TODO (Not Yet Tested)

- [ ] Ad creation via `POST /ads/v1/ads` — need to find the right category ID for IT services
- [ ] Image upload via `POST /core/v1/images`
- [ ] Category field discovery via `GET /core/v1/categories/{id}/fields`
- [ ] Service ad category vs goods category — may be completely different API paths
