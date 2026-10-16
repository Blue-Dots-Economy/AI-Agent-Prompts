#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""End-to-end email test: build the digest and actually send it, using LOCAL credentials.

Picks up whichever of these exists (no secrets are printed):
  secrets/gmail-oauth.json   {client_id, client_secret, refresh_token}  <- setup_gmail_oauth.py
  secrets/resend-key.txt     the Resend API key on one line
  secrets/gmail-sa.json      service-account JSON (needs admin-granted DWD)
…or anything already exported in the environment.

Usage:
  python3 raya/regression/static_regression.py
  python3 raya/regression/build_digest.py daily > digest.html
  python3 raya/regression/test_email.py
"""
import json, os, subprocess, sys, base64

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
S = lambda *p: os.path.join(REPO, "secrets", *p)

env = dict(os.environ)

oauth = S("gmail-oauth.json")
resend = S("resend-key.txt")
sa = S("gmail-sa.json")

if os.path.exists(oauth) and not env.get("GMAIL_OAUTH_REFRESH_TOKEN"):
    d = json.load(open(oauth, encoding="utf-8"))
    env["GMAIL_OAUTH_CLIENT_ID"] = d["client_id"]
    env["GMAIL_OAUTH_CLIENT_SECRET"] = d["client_secret"]
    env["GMAIL_OAUTH_REFRESH_TOKEN"] = d["refresh_token"]
    print("credential: secrets/gmail-oauth.json (Gmail API as user)")
elif os.path.exists(resend) and not env.get("RESEND_API_KEY"):
    env["RESEND_API_KEY"] = open(resend, encoding="utf-8").read().strip()
    env.setdefault("GMAIL_SENDER", "onboarding@resend.dev")   # required until a domain is verified
    print("credential: secrets/resend-key.txt (Resend API)")
elif os.path.exists(sa) and not env.get("GMAIL_SA_JSON_BASE64"):
    env["GMAIL_SA_JSON_BASE64"] = base64.b64encode(open(sa, "rb").read()).decode()
    print("credential: secrets/gmail-sa.json (service account + DWD)")
else:
    print("Using credentials already present in the environment (if any).")

if not os.path.exists(os.path.join(os.getcwd(), "digest.html")):
    print("digest.html missing — run build_digest.py first:", file=sys.stderr)
    print("  python3 raya/regression/build_digest.py daily > digest.html", file=sys.stderr)
    sys.exit(1)

env.setdefault("DIGEST_SUBJECT", "[Prompt Tuner] E2E email test — regression digest")
sys.exit(subprocess.run([sys.executable, os.path.join(REPO, "raya/regression/send_digest.py")],
                        env=env).returncode)
