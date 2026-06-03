# Gmail OAuth 2.0 Manual Console Flow

Use this when the user has a Google Cloud `client_secret_*.json` file and wants to send emails without an App Password.

## Prerequisites

- Google Cloud OAuth 2.0 client secret JSON file
- Python with packages: `google-auth`, `google-auth-oauthlib`, `requests` (install via uv venv)

## Step-by-Step

### 1. Save the client_secret file

Write the JSON content to a clean path:

```bash
cat > /root/gmail-client-secret.json << 'EOF'
{"web":{"client_id":"...","project_id":"...","auth_uri":"https://accounts.google.com/o/oauth2/auth","token_uri":"https://oauth2.googleapis.com/token","client_secret":"...","redirect_uris":["http://localhost"]}}
EOF
```

### 2. Install deps in a venv

```bash
uv venv /tmp/gmail-venv
source /tmp/gmail-venv/bin/activate
uv pip install google-auth google-auth-oauthlib requests
```

### 3. Run the OAuth flow script

```python
import json, pickle, requests, webbrowser
from urllib.parse import urlencode, parse_qs, urlparse

CLIENT_SECRET_FILE = '/root/gmail-client-secret.json'
TOKEN_FILE = '/root/gmail-token.pickle'

with open(CLIENT_SECRET_FILE) as f:
    web = json.load(f)['web']

# Step 1: Generate auth URL
params = {
    'client_id': web['client_id'],
    'redirect_uri': 'http://localhost',
    'response_type': 'code',
    'scope': 'https://mail.google.com/',
    'access_type': 'offline',
    'prompt': 'consent',
}
auth_url = f"{web['auth_uri']}?{urlencode(params)}"
print('=== OPEN THIS URL IN YOUR BROWSER ===')
print(auth_url)

# Step 2: User pastes the redirect URL or code
auth_code = input('Paste the full redirect URL (or just the code= parameter): ').strip()

if 'code=' in auth_code:
    qs = parse_qs(urlparse(auth_code).query)
    code = qs['code'][0]
else:
    code = auth_code

# Step 3: Exchange code for tokens
token_data = {
    'client_id': web['client_id'],
    'client_secret': web['client_secret'],
    'code': code,
    'grant_type': 'authorization_code',
    'redirect_uri': 'http://localhost',
}
resp = requests.post(web['token_uri'], data=token_data)
tokens = resp.json()

if 'error' in tokens:
    print(f"Error: {tokens['error']} - {tokens.get('error_description', '')}")
    exit(1)

pickle.dump(tokens, open(TOKEN_FILE, 'wb'))
print(f'Token saved. Refresh token: {tokens.get("refresh_token", "NONE")[:30]}...')
```

### 4. User interaction

The script prints an auth URL. Send it to the user. They open it in their browser, authorize the Gmail access, and get redirected to `http://localhost/?code=...` (which shows "site can't be reached" — that's expected). They copy that full URL from the address bar and paste it back.

### 5. Using the token to send email

```python
import pickle, base64, requests
from email.message import EmailMessage

TOKEN_FILE = '/root/gmail-token.pickle'
with open(TOKEN_FILE, 'rb') as f:
    tokens = pickle.load(f)

access_token = tokens['access_token']

# Build email message
msg = EmailMessage()
msg['From'] = 'geniok@gmail.com'
msg['To'] = 'geniok@gmail.com'
msg['Subject'] = 'Subject here'
msg.set_content('Body here')

# Gmail API send
raw = base64.urlsafe_b64encode(msg.as_bytes()).decode()
resp = requests.post(
    'https://gmail.googleapis.com/gmail/v1/users/me/messages/send',
    headers={'Authorization': f'Bearer {access_token}'},
    json={'raw': raw}
)

if resp.status_code == 200:
    print('Email sent!')
else:
    print(f'Error: {resp.status_code} {resp.text}')
    # If 401, refresh token
    if resp.status_code == 401 and 'refresh_token' in tokens:
        refresh_data = {
            'client_id': '...',
            'client_secret': '...',
            'refresh_token': tokens['refresh_token'],
            'grant_type': 'refresh_token',
        }
        refresh_resp = requests.post('https://oauth2.googleapis.com/token', data=refresh_data)
        new_tokens = refresh_resp.json()
        new_tokens['refresh_token'] = tokens['refresh_token']  # preserve
        pickle.dump(new_tokens, open(TOKEN_FILE, 'wb'))
        # Retry with new token...
```

## Pitfalls

- **`run_console()` not available** — newer google-auth-oauthlib versions removed `run_console`. Only `run_local_server` exists (which opens a browser — useless in headless). Always use the manual URL + code exchange approach above.
- **Scope must be `https://mail.google.com/`** for full Gmail access. `gmail.send` alone may work but `mail.google.com/` is safer. For multi-scope access (e.g., Gmail + Calendar), space-separate them in the scope parameter.
- **Refresh token may not be returned** if user already authorized before without `prompt=consent` and `access_type=offline`. Ensure these params are set.
- **Token expiry** — access tokens expire after ~1 hour. Use the refresh token to get new ones. The Gmail API returns 401 when expired.
- **Himalaya doesn't support OAuth tokens** — if you need himalaya (CLI email), use the App Password method. OAuth tokens work with the Gmail REST API only.
- **`Invalid client` error** during OAuth means the OAuth client was deleted from Google Cloud Console. The user needs to either create a new client or use an App Password instead.
- **Cache directory files are invisible to terminal tools** — files saved at `/root/.hermes/cache/documents/` by the `read_file` tool cannot be accessed by `terminal`, `cp`, or `cat` with their literal paths. Use Python's `os.walk()` to find and read them, or copy content via `write_file` to a clean path like `/root/gmail-client-secret.json`.

### Using google-api-python-client (recommended for production)

Instead of raw HTTP requests, use the official Google client library which handles token refresh automatically:

```python
import json, base64
from email.mime.text import MIMEText
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

TOKEN_FILE = '/root/.gmail-tokens.json'
SCOPES = ['https://mail.google.com/', 'https://www.googleapis.com/auth/calendar']

with open(TOKEN_FILE) as f:
    token_data = json.load(f)

creds = Credentials(
    token=token_data.get('access_token'),
    refresh_token=token_data.get('refresh_token'),
    token_uri=token_data.get('token_uri', 'https://oauth2.googleapis.com/token'),
    client_id=token_data.get('client_id'),
    client_secret=token_data.get('client_secret'),
    scopes=SCOPES
)

# Auto-refresh if expired
if creds.expired:
    creds.refresh(Request())
    with open(TOKEN_FILE, 'w') as f:
        token_data['access_token'] = creds.token
        json.dump(token_data, f)

service = build('gmail', 'v1', credentials=creds)

# Send email with proper UTF-8 Subject (use MIMEText, not raw string)
msg = MIMEText('Body text', 'plain', 'utf-8')
msg['From'] = 'user@gmail.com'
msg['To'] = 'recipient@gmail.com'
msg['Subject'] = 'Тема с кириллицей'
raw = base64.urlsafe_b64encode(msg.as_bytes()).decode()
sent = service.users().messages().send(userId='me', body={'raw': raw}).execute()
print(f'Sent! ID: {sent["id"]}')
```

Key advantages of google-api-python-client:
- Automatic token refresh (no manual 401 handling)
- Proper MIME encoding for Cyrillic subjects
- Multi-scope support (Gmail + Calendar + Drive, etc.)
- Better error messages

### Token file format

After the OAuth exchange, ensure the saved JSON has ALL fields needed for refresh:

```json
{
  "access_token": "ya29.a...",
  "refresh_token": "1//03...",
  "token_uri": "https://oauth2.googleapis.com/token",
  "client_id": "433049900642-...apps.googleusercontent.com",
  "client_secret": "GOCSPX-..."
}
```

Without `token_uri`, `client_id`, and `client_secret` in the saved file, token refresh will fail silently.

### Installation

```bash
uv venv /tmp/gmail-venv
source /tmp/gmail-venv/bin/activate
uv pip install google-auth google-auth-oauthlib google-api-python-client
```

## When to Use Which

| Scenario | Method |
|----------|--------|
| User has App Password | Himalaya + SMTP — simpler, CLI-based |
| User has client_secret.json | OAuth + Gmail API — no password needed, supports Calendar too |
| User has neither | Ask for App Password (simpler) |
