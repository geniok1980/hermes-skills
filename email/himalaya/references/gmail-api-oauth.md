# Gmail API OAuth (alternative to SMTP app passwords)

When Gmail blocks app passwords or you need Calendar + Gmail access, use OAuth instead.

## Prerequisites

- Google Cloud OAuth client_secret JSON (web app type, redirect_uri=http://localhost)
- Python: `google-auth-oauthlib`, `google-api-python-client`, `google-auth-transport-requests`

## Setup Flow

1. **Get client_secret.json** — from Google Cloud Console → APIs & Services → Credentials
2. **Generate auth URL** and ask user to open it:
   ```python
   from google_auth_oauthlib.flow import InstalledAppFlow
   flow = InstalledAppFlow.from_client_secrets_file('client_secret.json', 
       ['https://mail.google.com/', 'https://www.googleapis.com/auth/calendar'])
   # Use console flow: print the URL, user visits, copies redirect URL
   ```
3. User authorizes → gets redirect to `http://localhost/?code=...`
4. Exchange code for tokens via POST to `https://oauth2.googleapis.com/token`
5. Save `access_token` + `refresh_token` to JSON file

## Sending Email via Gmail API

```python
from email.mime.text import MIMEText
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
import base64, json

creds = Credentials(
    token=token_data['access_token'],
    refresh_token=token_data['refresh_token'],
    token_uri=token_data.get('token_uri', 'https://oauth2.googleapis.com/token'),
    client_id=token_data['client_id'],
    client_secret=token_data['client_secret'],
    scopes=['https://mail.google.com/']
)

# Auto-refresh if expired
if creds.expired:
    creds.refresh(Request())
    # save updated token

service = build('gmail', 'v1', credentials=creds)
msg = MIMEText(body, 'plain', 'utf-8')
msg['From'] = 'your@gmail.com'
msg['To'] = to
msg['Subject'] = subject
raw = base64.urlsafe_b64encode(msg.as_bytes()).decode()
service.users().messages().send(userId='me', body={'raw': raw}).execute()
```

## MIME Encoding for Cyrillic

Always use `MIMEText(body, 'plain', 'utf-8')` — raw string formatting breaks non-ASCII subjects.

## Token Refresh

- Save `token_uri`, `client_id`, `client_secret` alongside tokens in the JSON file
- Refresh token lasts 7 days (`refresh_token_expires_in: 604799`)
- On expiry: `creds.refresh(Request())` then re-save

## Resolving OAuth Errors

- `invalid_client`: OAuth client was deleted from Google Cloud Console — user must recreate
- `redirect_uri_mismatch`: ensure the client_secret has `"redirect_uris": ["http://localhost"]`
- No `run_console` in newer google-auth-oauthlib: use `run_local_server` with `open_browser=False` or manual code exchange via requests
