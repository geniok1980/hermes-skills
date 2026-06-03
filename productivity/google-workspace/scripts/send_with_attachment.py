#!/usr/bin/env python3
"""
Send an email with a file attachment via the Gmail API.

The google_api.py `gmail send` command does not support attachments,
so this script uses the Gmail API directly.

Usage:
    python3 send_with_attachment.py --to user@example.com --subject "Subject" --body "Text" --file /path/to/file.pdf
    python3 send_with_attachment.py --to user@example.com --subject "HTML" --body "<h1>Hi</h1>" --html --file /tmp/doc.txt
"""
import argparse, base64, os, sys

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders


def main():
    parser = argparse.ArgumentParser(description='Send email with attachment via Gmail API')
    parser.add_argument('--to', required=True)
    parser.add_argument('--subject', required=True)
    parser.add_argument('--body', required=True)
    parser.add_argument('--file', required=True, help='Path to file to attach')
    parser.add_argument('--html', action='store_true', help='Send body as HTML')
    parser.add_argument('--from-header', help='Custom From header (e.g. "Name <user@example.com>")')
    args = parser.parse_args()

    if not os.path.exists(args.file):
        print(f'ERROR: file not found: {args.file}', file=sys.stderr)
        sys.exit(1)

    token_path = os.path.expanduser('~/.hermes/google_token.json')
    if not os.path.exists(token_path):
        print('ERROR: google_token.json not found. Run google-workspace setup first.', file=sys.stderr)
        sys.exit(1)

    creds = Credentials.from_authorized_user_file(token_path)
    if not creds.valid and creds.expired and creds.refresh_token:
        creds.refresh(Request())
        with open(token_path, 'w') as f:
            f.write(creds.to_json())

    service = build('gmail', 'v1', credentials=creds)

    msg = MIMEMultipart('mixed')
    msg['To'] = args.to
    msg['Subject'] = args.subject
    if args.from_header:
        msg['From'] = args.from_header

    msg_alt = MIMEMultipart('alternative')
    if args.html:
        msg_alt.attach(MIMEText(args.body, 'plain', 'utf-8'))
        msg_alt.attach(MIMEText(args.body, 'html', 'utf-8'))
    else:
        msg_alt.attach(MIMEText(args.body, 'plain', 'utf-8'))
    msg.attach(msg_alt)

    filename = os.path.basename(args.file)
    with open(args.file, 'rb') as f:
        part = MIMEBase('application', 'octet-stream')
        part.set_payload(f.read())
    encoders.encode_base64(part)
    part.add_header('Content-Disposition', 'attachment', filename=filename)
    msg.attach(part)

    raw = base64.urlsafe_b64encode(msg.as_bytes()).decode()
    result = service.users().messages().send(userId='me', body={'raw': raw}).execute()
    print(f'OK | message_id={result["id"]} | thread_id={result.get("threadId", "")}')


if __name__ == '__main__':
    main()
