#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""One-time setup: get a Gmail refresh token by YOUR OWN consent (no Workspace admin).

This is the Google Cloud Console path. Do this once; the scheduled workflow then sends the
regression digest as you, forever.

STEP 1 — in Google Cloud Console (console.cloud.google.com), no admin rights needed:
  a) pick/create a project (e.g. the existing `operation-rozgar`)
  b) APIs & Services -> Library -> enable **Gmail API**
  c) APIs & Services -> OAuth consent screen -> User type **Internal** (if offered; else
     External + add yourself as a Test user). Add scope `.../auth/gmail.send`.
  d) APIs & Services -> Credentials -> Create credentials -> **OAuth client ID**
     -> Application type **Desktop app** -> Create -> **Download JSON**

STEP 2 — run this script with the downloaded file:
  python3 raya/regression/setup_gmail_oauth.py ~/Downloads/client_secret_*.json

It opens a browser for your consent, then stores the refresh token in
`secrets/gmail-oauth.json` (git-ignored) and — if `gh` is authed — sets the repo secrets
GMAIL_OAUTH_CLIENT_ID / GMAIL_OAUTH_CLIENT_SECRET / GMAIL_OAUTH_REFRESH_TOKEN.

The token is NEVER printed to stdout; only a masked confirmation is shown.
Requires: pip install google-auth-oauthlib
"""
import glob, json, os, subprocess, sys

SCOPES = ["https://www.googleapis.com/auth/gmail.send"]
REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
OUT = os.path.join(REPO, "secrets", "gmail-oauth.json")
GH_REPO = "parthekstep/Prompt-Tuner"


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return 2
    matches = sorted(glob.glob(os.path.expanduser(sys.argv[1])))
    if not matches:
        print(f"No client-secret JSON matched: {sys.argv[1]}", file=sys.stderr)
        return 1
    client_file = matches[0]
    print(f"Using OAuth client file: {os.path.basename(client_file)}")

    try:
        from google_auth_oauthlib.flow import InstalledAppFlow
    except ImportError:
        print("Missing dep. Run:  python3 -m pip install google-auth-oauthlib", file=sys.stderr)
        return 1

    flow = InstalledAppFlow.from_client_secrets_file(client_file, SCOPES)
    # Opens your browser; consent as the account you want the digest sent FROM.
    # SETUP_NO_BROWSER=1 prints the URL instead of launching a browser (lets an automated
    # session drive the consent page in a controlled tab).
    no_browser = os.environ.get("SETUP_NO_BROWSER", "").strip() in ("1", "y", "yes")
    creds = flow.run_local_server(
        port=int(os.environ.get("SETUP_OAUTH_PORT", "0")), prompt="consent",
        open_browser=not no_browser,
        authorization_prompt_message="Visit this URL to authorize: {url}")
    if not creds.refresh_token:
        print("No refresh_token returned. Re-run (consent must be fresh).", file=sys.stderr)
        return 1

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump({"client_id": creds.client_id, "client_secret": creds.client_secret,
                   "refresh_token": creds.refresh_token}, f, indent=1)
    os.chmod(OUT, 0o600)
    print(f"Refresh token stored in secrets/gmail-oauth.json (git-ignored, chmod 600).")
    print(f"  client_id: {creds.client_id[:18]}…  refresh_token: …{creds.refresh_token[-4:]} (masked)")

    # Push to GitHub secrets so the scheduled cloud run can use them.
    auto = os.environ.get("SETUP_SET_SECRETS", "").strip().lower() in ("1", "y", "yes")
    if auto or input("Set the GitHub repo secrets now via gh? [y/N] ").strip().lower().startswith("y"):
        for name, value in (("GMAIL_OAUTH_CLIENT_ID", creds.client_id),
                            ("GMAIL_OAUTH_CLIENT_SECRET", creds.client_secret),
                            ("GMAIL_OAUTH_REFRESH_TOKEN", creds.refresh_token)):
            p = subprocess.run(["gh", "secret", "set", name, "--repo", GH_REPO, "--body", value],
                               capture_output=True, text=True)
            print(f"  {name}: {'set ✓' if p.returncode == 0 else 'FAILED ' + p.stderr.strip()}")
        print("Also set GMAIL_SENDER / GMAIL_TO if you want a different from/to than the default.")
    else:
        print("Skipped. Later:  gh secret set GMAIL_OAUTH_REFRESH_TOKEN --repo " + GH_REPO)

    print("\nTest the whole flow locally:")
    print("  python3 raya/regression/static_regression.py && \\")
    print("  python3 raya/regression/build_digest.py daily > digest.html && \\")
    print("  python3 raya/regression/test_email.py")
    return 0


if __name__ == "__main__":
    sys.exit(main())
