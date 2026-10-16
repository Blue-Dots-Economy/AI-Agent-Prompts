#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Send the regression digest by email. Multi-provider, auto-detected from env.

Providers are tried in priority order; the first one whose secrets are present wins.
All of them work from a GitHub Actions runner, and NONE of 1-3 needs Workspace admin.

  1. GMAIL_OAUTH_REFRESH_TOKEN (+ CLIENT_ID/CLIENT_SECRET)  — Gmail API as YOU.
     Set up via Google Cloud Console (OAuth client) + one-time local consent:
     `python3 raya/regression/setup_gmail_oauth.py`. No Workspace admin required.
  2. RESEND_API_KEY            — Resend HTTP API. Free tier, 2-min signup, no Google at all.
  3. SMTP_HOST/SMTP_USER/SMTP_PASS — any SMTP (Gmail app password, Mailgun, SES, …).
  4. GMAIL_SA_JSON_BASE64      — service account + domain-wide delegation. NEEDS an admin
                                 to grant the gmail.send scope; kept for completeness.

Common env:
  GMAIL_SENDER / MAIL_FROM  from-address   (default parth@ekstepplus.org; Resend without a
                            verified domain must use onboarding@resend.dev)
  GMAIL_TO / MAIL_TO        recipient(s), comma-separated (default parth@ekstepplus.org)
  DIGEST_SUBJECT            subject line

Reads the HTML body from digest.html (built by build_digest.py) in the working dir.
Exits 0 when no provider is configured, so the workflow never fails just because email
isn't wired up yet.
"""
import base64, json, os, sys, smtplib, urllib.request, urllib.error
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

SCOPES = ["https://www.googleapis.com/auth/gmail.send"]


def env(*names, default=""):
    for n in names:
        v = os.environ.get(n, "").strip()
        if v:
            return v
    return default


def html_to_text(html):
    """Crude but adequate plain-text alternative for clients that strip HTML."""
    import re
    t = re.sub(r"(?is)<(script|style).*?</\1>", "", html)
    t = re.sub(r"(?i)</(div|p|tr|table)>", "\n", t)
    t = re.sub(r"(?i)<br\s*/?>", "\n", t)
    t = re.sub(r"<[^>]+>", "", t)
    for a, b in (("&nbsp;", " "), ("&amp;", "&"), ("&lt;", "<"), ("&gt;", ">"),
                 ("&ldquo;", '"'), ("&rdquo;", '"'), ("&mdash;", "—")):
        t = t.replace(a, b)
    lines = [ln.strip() for ln in t.splitlines()]
    out, blank = [], False
    for ln in lines:                       # collapse runs of blank lines
        if ln:
            out.append(ln); blank = False
        elif not blank:
            out.append(""); blank = True
    return "\n".join(out).strip()


def build_message(sender, to, subject, html):
    """multipart/alternative: plain-text part + the HTML digest."""
    msg = MIMEMultipart("alternative")
    msg["To"] = to
    msg["From"] = sender
    msg["Subject"] = subject
    msg.attach(MIMEText(html_to_text(html), "plain", "utf-8"))
    msg.attach(MIMEText(html, "html", "utf-8"))
    return msg


# --- providers ---------------------------------------------------------------

def send_gmail_oauth(sender, to, subject, html):
    """Gmail API using a refresh token obtained by the user's own consent (no admin)."""
    from google.oauth2.credentials import Credentials      # google-auth
    from googleapiclient.discovery import build            # google-api-python-client
    creds = Credentials(
        None,
        refresh_token=os.environ["GMAIL_OAUTH_REFRESH_TOKEN"],
        token_uri="https://oauth2.googleapis.com/token",
        client_id=os.environ["GMAIL_OAUTH_CLIENT_ID"],
        client_secret=os.environ["GMAIL_OAUTH_CLIENT_SECRET"],
        scopes=SCOPES,
    )
    svc = build("gmail", "v1", credentials=creds, cache_discovery=False)
    raw = base64.urlsafe_b64encode(build_message(sender, to, subject, html).as_bytes()).decode()
    svc.users().messages().send(userId="me", body={"raw": raw}).execute()
    return "Gmail API (OAuth user credentials)"


def send_resend(sender, to, subject, html):
    """Resend HTTP API — no Google involvement, no admin, free tier."""
    payload = json.dumps({
        "from": sender, "to": [a.strip() for a in to.split(",") if a.strip()],
        "subject": subject, "html": html,
    }).encode()
    req = urllib.request.Request(
        "https://api.resend.com/emails", data=payload, method="POST",
        headers={"Authorization": f"Bearer {os.environ['RESEND_API_KEY']}",
                 "Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=30) as r:
        r.read()
    return "Resend API"


def send_smtp(sender, to, subject, html):
    """Generic SMTP — Gmail app password, Mailgun, SES, anything."""
    host = os.environ["SMTP_HOST"]
    port = int(os.environ.get("SMTP_PORT", "465"))
    msg = build_message(sender, to, subject, html)
    rcpts = [a.strip() for a in to.split(",") if a.strip()]
    if port == 587:
        with smtplib.SMTP(host, port, timeout=30) as s:
            s.starttls()
            s.login(os.environ["SMTP_USER"], os.environ["SMTP_PASS"])
            s.sendmail(sender, rcpts, msg.as_string())
    else:
        with smtplib.SMTP_SSL(host, port, timeout=30) as s:
            s.login(os.environ["SMTP_USER"], os.environ["SMTP_PASS"])
            s.sendmail(sender, rcpts, msg.as_string())
    return f"SMTP ({host}:{port})"


def send_gmail_sa(sender, to, subject, html):
    """Service account + domain-wide delegation (requires a Workspace admin to grant scope)."""
    from google.oauth2 import service_account
    from googleapiclient.discovery import build
    info = json.loads(base64.b64decode(os.environ["GMAIL_SA_JSON_BASE64"]))
    creds = service_account.Credentials.from_service_account_info(
        info, scopes=SCOPES).with_subject(sender)
    svc = build("gmail", "v1", credentials=creds, cache_discovery=False)
    raw = base64.urlsafe_b64encode(build_message(sender, to, subject, html).as_bytes()).decode()
    svc.users().messages().send(userId="me", body={"raw": raw}).execute()
    return "Gmail API (service account + DWD)"


PROVIDERS = [
    ("GMAIL_OAUTH_REFRESH_TOKEN", send_gmail_oauth),
    ("RESEND_API_KEY",            send_resend),
    ("SMTP_PASS",                 send_smtp),
    ("GMAIL_SA_JSON_BASE64",      send_gmail_sa),
]


def main():
    chosen = next((fn for key, fn in PROVIDERS if os.environ.get(key, "").strip()), None)
    if chosen is None:
        print("No email provider configured (set GMAIL_OAUTH_REFRESH_TOKEN, RESEND_API_KEY, "
              "SMTP_PASS, or GMAIL_SA_JSON_BASE64) — skipping send.", file=sys.stderr)
        return 0

    sender = env("GMAIL_SENDER", "MAIL_FROM", default="parth@ekstepplus.org")
    to = env("GMAIL_TO", "MAIL_TO", default="parth@ekstepplus.org")
    subject = env("DIGEST_SUBJECT", default="[Prompt Tuner] regression digest")
    html = open("digest.html", encoding="utf-8").read()

    try:
        via = chosen(sender, to, subject, html)
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", "replace")[:400]
        print(f"Email send FAILED ({e.code}): {body}", file=sys.stderr)
        return 1
    print(f"Sent regression digest to {to} (as {sender}) via {via}.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
