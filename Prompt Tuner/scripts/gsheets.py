#!/usr/bin/env python3
#
# gsheets.py — minimal Google Sheets API v4 client via a service-account key.
# Auth: RS256 self-signed JWT (cryptography) -> OAuth2 token -> Sheets REST (urllib).
# Stdlib + cryptography only (no google-api-python-client needed).
#
#   scripts/gsheets.py [--sheet-id ID] meta                       # list tabs + gids (proves auth)
#   scripts/gsheets.py [--sheet-id ID] get "<A1 range>" [--out f] # read values (JSON, or CSV to --out)
#   scripts/gsheets.py [--sheet-id ID] update "<A1 range>" '<2D-json>'   # write values (RAW)
#
# Key lookup order: $GOOGLE_SA_KEY -> <repo>/secrets/gsheets-sa.json -> $GOOGLE_APPLICATION_CREDENTIALS
#                   -> ~/Downloads/service-account.json
# Sheet id: --sheet-id or $GSHEET_ID.

import argparse
import base64
import csv
import json
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TOKEN_URL = "https://oauth2.googleapis.com/token"
SHEETS = "https://sheets.googleapis.com/v4/spreadsheets"
SCOPE = "https://www.googleapis.com/auth/spreadsheets"


def die(msg):
    sys.stderr.write("error: %s\n" % msg)
    sys.exit(1)


def b64u(raw):
    return base64.urlsafe_b64encode(raw).rstrip(b"=")


def key_path():
    if os.environ.get("GOOGLE_SA_KEY"):
        return os.environ["GOOGLE_SA_KEY"]
    for cand in (os.path.join(REPO_ROOT, "secrets", "gsheets-sa.json"),
                 os.environ.get("GOOGLE_APPLICATION_CREDENTIALS", ""),
                 os.path.expanduser("~/Downloads/service-account.json")):
        if cand and os.path.exists(cand):
            return cand
    return ""


def load_key():
    path = key_path()
    if not path or not os.path.exists(path):
        die("service-account key not found (set $GOOGLE_SA_KEY or put it at secrets/gsheets-sa.json).")
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def access_token(sa):
    now = int(time.time())
    header = {"alg": "RS256", "typ": "JWT"}
    claim = {"iss": sa["client_email"], "scope": SCOPE, "aud": TOKEN_URL, "iat": now, "exp": now + 3600}
    signing_input = b64u(json.dumps(header).encode()) + b"." + b64u(json.dumps(claim).encode())
    pk = serialization.load_pem_private_key(sa["private_key"].encode(), password=None)
    sig = pk.sign(signing_input, padding.PKCS1v15(), hashes.SHA256())
    assertion = (signing_input + b"." + b64u(sig)).decode()
    data = urllib.parse.urlencode({
        "grant_type": "urn:ietf:params:oauth:grant-type:jwt-bearer",
        "assertion": assertion,
    }).encode()
    req = urllib.request.Request(TOKEN_URL, data=data,
                                 headers={"Content-Type": "application/x-www-form-urlencoded"})
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.loads(resp.read())["access_token"]
    except urllib.error.HTTPError as exc:
        die("token exchange failed: HTTP %s\n%s" % (exc.code, exc.read().decode("utf-8", "replace")[:500]))


def api(token, path, method="GET", body=None):
    url = SHEETS + path
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(url, data=data, method=method,
                                 headers={"Authorization": "Bearer " + token,
                                          "Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            raw = resp.read().decode("utf-8")
            return json.loads(raw) if raw.strip() else {}
    except urllib.error.HTTPError as exc:
        die("Sheets API %s %s -> HTTP %s\n%s" % (method, path, exc.code, exc.read().decode("utf-8", "replace")[:700]))


def sheet_id(args):
    sid = args.sheet_id or os.environ.get("GSHEET_ID")
    if not sid:
        die("no spreadsheet id (pass --sheet-id or set $GSHEET_ID).")
    return sid


def cmd_meta(args, token):
    sid = sheet_id(args)
    d = api(token, "/%s?fields=properties.title,sheets.properties(sheetId,title,gridProperties)" % sid)
    print("spreadsheet:", d["properties"]["title"])
    for s in d.get("sheets", []):
        p = s["properties"]
        g = p.get("gridProperties", {})
        print("  gid=%-12s %-24s %sx%s" % (p["sheetId"], repr(p["title"]), g.get("rowCount"), g.get("columnCount")))


def cmd_get(args, token):
    sid = sheet_id(args)
    rng = urllib.parse.quote(args.range, safe="!:$")
    d = api(token, "/%s/values/%s" % (sid, rng))
    vals = d.get("values", [])
    if args.out:
        with open(args.out, "w", newline="", encoding="utf-8") as fh:
            csv.writer(fh).writerows(vals)
        print("wrote %d row(s) to %s" % (len(vals), args.out))
    else:
        print(json.dumps(vals, ensure_ascii=False))


def cmd_update(args, token):
    sid = sheet_id(args)
    values = json.loads(args.values)
    rng = urllib.parse.quote(args.range, safe="!:$")
    d = api(token, "/%s/values/%s?valueInputOption=RAW" % (sid, rng), method="PUT", body={"values": values})
    print("updated range %s (%s cells)" % (d.get("updatedRange"), d.get("updatedCells")))


def build_parser():
    p = argparse.ArgumentParser(prog="gsheets.py", description="Minimal Google Sheets API client (service account).")
    p.add_argument("--sheet-id", help="spreadsheet id (default $GSHEET_ID)")
    sub = p.add_subparsers(dest="cmd", required=True)
    sub.add_parser("meta", help="list tabs + gids (proves auth)")
    g = sub.add_parser("get", help="read a range")
    g.add_argument("range", help="A1 range, e.g. 'All Issues'!A1:K100")
    g.add_argument("--out", help="write CSV to this path instead of printing JSON")
    u = sub.add_parser("update", help="write a range (RAW)")
    u.add_argument("range", help="A1 range, e.g. 'All Issues'!H5")
    u.add_argument("values", help="2D JSON array, e.g. [[\"Fixed\"]]")
    return p


def main(argv):
    args = build_parser().parse_args(argv)
    token = access_token(load_key())
    {"meta": cmd_meta, "get": cmd_get, "update": cmd_update}[args.cmd](args, token)


if __name__ == "__main__":
    main(sys.argv[1:])
