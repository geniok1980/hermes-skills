# Web-type OAuth client auth fallback

When the user creates a **"Web application"** type OAuth client (JSON key `"web"`),
`setup.py --auth-url` generates a URL with PKCE (`code_challenge`) which Google's
token endpoint rejects for web clients. Use this direct exchange instead.

## 1. Generate auth URL without PKCE

```python
import json
from urllib.parse import urlencode

secret = json.loads(open('/root/.hermes/google_client_secret.json').read())
client_id = secret['web']['client_id']

scopes = [
    "https://www.googleapis.com/auth/gmail.readonly",
    "https://www.googleapis.com/auth/gmail.send",
    "https://www.googleapis.com/auth/gmail.modify",
    "https://www.googleapis.com/auth/calendar",
    "https://www.googleapis.com/auth/drive",
    "https://www.googleapis.com/auth/contacts.readonly",
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/documents",
]

params = {
    'response_type': 'code',
    'client_id': client_id,
    'redirect_uri': 'http://localhost',  # MUST match registered URI exactly
    'scope': ' '.join(scopes),
    'access_type': 'offline',
    'prompt': 'consent',
}
print(f"https://accounts.google.com/o/oauth2/auth?{urlencode(params)}")
```

User visits URL → authorizes → pastes back the redirect URL containing `?code=...`.

## 2. Exchange code for token (no PKCE)

```python
import json, requests
from datetime import datetime, timedelta, timezone

secret = json.loads(open('/root/.hermes/google_client_secret.json').read())
client_id = secret['web']['client_id']
client_secret = secret['web']['client_secret']

code = "4/0A..."  # from user's redirect URL

resp = requests.post('https://oauth2.googleapis.com/token', data={
    'code': code,
    'client_id': client_id,
    'client_secret': client_secret,
    'redirect_uri': 'http://localhost',
    'grant_type': 'authorization_code',
})
result = resp.json()

token_payload = {
    "token": result['access_token'],
    "refresh_token": result.get('refresh_token'),
    "token_uri": "https://oauth2.googleapis.com/token",
    "client_id": client_id,
    "client_secret": client_secret,
    "scopes": result['scope'].split(),
    "expiry": (datetime.now(timezone.utc) + timedelta(seconds=result['expires_in'])).isoformat(),
}

import os
with open(os.path.expanduser('~/.hermes/google_token.json'), 'w') as f:
    json.dump(token_payload, f, indent=2)
print("✅ Token saved")
```

After this, `$GSETUP --check` passes and normal `GAPI` commands work.

## Symptoms that trigger this path

- Token exchange returns `invalid_grant: code_verifier or verifier is not needed`
- Client secret JSON has `"web"` key (not `"installed"`)
- Registered `redirect_uris` contain `http://localhost` (not `http://localhost:1`)
