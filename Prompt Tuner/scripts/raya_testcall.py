#!/usr/bin/env python3
"""Agent-to-agent voice test harness for Raya.

A TESTER agent ("Testing Agent- Blue Dots", inbound DID) role-plays a human persona.
The BOT UNDER TEST (an outbound agent, e.g. KKB Hindi Signals) initiates a call to the
tester's inbound DID via POST /api/call; the persona answers and converses so we can grade
the bot from the transcript.

Subcommands:
  whoami  <uuid>                          print name / lang / voice / dids / instructions-len
  persona <tester_uuid> <persona_file>    PATCH tester.instructions from a file (backs up prior)
  lang    <tester_uuid> <hi|kn|mr>           PATCH tester.language_id + voice_id
  call    <bot_uuid> --to <did> --args <json_file> [--out-did D] [--cc 91] [--tz Asia/Kolkata]
                                          POST /api/call to initiate the test call

Env: raya/.env (RAYA_BASE_URL, RAYA_API_TOKEN). The token is never printed.
Read past calls / transcripts with scripts/raya_call.py <bot_uuid> [limit].
"""
import json, os, sys, argparse, urllib.request, urllib.error, datetime

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_env = {}
for _line in open(os.path.join(REPO, "raya/.env")):
    _line = _line.strip()
    if "=" in _line and not _line.startswith("#"):
        _k, _v = _line.split("=", 1); _env[_k.strip()] = _v.strip()
BASE = _env.get("RAYA_BASE_URL", "").rstrip("/")
KEY = _env.get("RAYA_API_TOKEN", "")

# language_id + voice_id pairs, harvested from live agents (read-only GET):
#   hi  -> tester's Hindi voice (413cbfba); kn -> KN Signals bot's Kannada voice (c343cabe)
LANG = {
    "hi": {"language_id": "38695ff2-ee6f-4a1c-837b-27ab241377f7",
           "voice_id": "413cbfba-8270-4291-96cd-1a38a9d68fa7"},
    "kn": {"language_id": "ac4d6be6-3da2-4936-a841-0b23c7323446",
           "voice_id": "c343cabe-629e-48f6-998d-7fa4d6d3c20a"},
    # mr -> the Marathi pair of "Kaam Ki Baat (Persona Based - Marathi) (Group 2)" (cb470bc3), read-only GET 2026-09-28
    "mr": {"language_id": "9046a14a-e2f6-46df-95e8-3a9883ca40f7",
           "voice_id": "daf1d34b-e65c-4553-88fe-54d66c10b912"},
}

# raya/voices.json is the register of record (per account); the dict above is the built-in fallback.
try:
    _vp = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "raya", "voices.json")
    _acct = os.environ.get("RAYA_ACCOUNT", "ekstep")
    for _iso, _pair in json.load(open(_vp, encoding="utf-8"))["accounts"].get(_acct, {}).items():
        LANG[_iso] = {"language_id": _pair["language_id"], "voice_id": _pair["voice_id"]}
except (OSError, ValueError, KeyError):
    pass


def _req(method, path, body=None):
    data = json.dumps(body).encode() if body is not None else None
    h = {"X-API-Key": KEY, "User-Agent": "Mozilla/5.0"}
    if data is not None:
        h["Content-Type"] = "application/json"
    req = urllib.request.Request(BASE + path, data=data, headers=h, method=method)
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            raw = r.read().decode()
            return r.status, (json.loads(raw) if raw.strip() else {})
    except urllib.error.HTTPError as e:
        return e.code, {"_error": e.read().decode()[:500]}


def get(path):
    return _req("GET", path)[1]


def whoami(uuid):
    a = get(f"/api/agent/{uuid}")
    ins = a.get("instructions") or ""
    print(json.dumps({
        "uuid": a.get("uuid"), "name": a.get("name"),
        "in_did": a.get("in_did"), "out_did": a.get("out_did"),
        "language_id": a.get("language_id"), "voice_id": a.get("voice_id"),
        "allow_interruption": a.get("allow_interruption"),
        "max_call_duration_mins": a.get("max_call_duration_mins"),
        "instructions_len": len(ins),
    }, indent=2, ensure_ascii=False))
    print("--- instructions (first 400 chars) ---")
    print(ins[:400])


def persona(uuid, path):
    text = open(path, encoding="utf-8").read()
    cur = get(f"/api/agent/{uuid}").get("instructions") or ""
    bdir = os.path.join(REPO, "raya/personas/_backups"); os.makedirs(bdir, exist_ok=True)
    ts = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
    bpath = os.path.join(bdir, f"{uuid[:8]}-{ts}.txt")
    open(bpath, "w", encoding="utf-8").write(cur)
    st, resp = _req("PATCH", f"/api/agent/{uuid}", {"instructions": text})
    echoed = resp.get("instructions") if isinstance(resp, dict) else None
    ok = (echoed == text)
    print(f"PATCH persona -> HTTP {st} | wrote {len(text)} chars | echo-verified={ok} "
          f"| backup={os.path.relpath(bpath, REPO)}")
    if not ok and echoed is not None:
        print(f"  WARN echo len={len(echoed)} != sent len={len(text)}")
    if "_error" in (resp or {}):
        print("  ERROR:", resp["_error"])


def lang(uuid, code):
    if code not in LANG:
        sys.exit(f"unknown lang {code!r}; known: {list(LANG)}")
    st, resp = _req("PATCH", f"/api/agent/{uuid}", LANG[code])
    got = {k: resp.get(k) for k in ("language_id", "voice_id")} if isinstance(resp, dict) else {}
    ok = got == LANG[code]
    print(f"PATCH lang={code} -> HTTP {st} | echo-verified={ok} | {json.dumps(got)}")
    if "_error" in (resp or {}):
        print("  ERROR:", resp["_error"])


def call(bot_uuid, to, args_file, out_did, cc, tz):
    agent_args = json.load(open(args_file, encoding="utf-8")) if args_file else {}
    body = {"agent_id": bot_uuid, "to_number": to, "agent_args": agent_args,
            "country_code": cc, "timezone": tz}
    # Passing out_did explicitly gave 'Unanswered'; omitting it lets Raya route and connects.
    # Only include out_did if the caller explicitly asks for it.
    if out_did:
        body["out_did"] = out_did
    st, resp = _req("POST", "/api/call", body)
    print(f"POST /api/call -> HTTP {st} (out_did {'sent' if out_did else 'omitted'})")
    print(json.dumps(resp, indent=2, ensure_ascii=False)[:1200])


def main():
    p = argparse.ArgumentParser()
    sub = p.add_subparsers(dest="cmd", required=True)
    sub.add_parser("whoami").add_argument("uuid")
    sp = sub.add_parser("persona"); sp.add_argument("uuid"); sp.add_argument("file")
    sl = sub.add_parser("lang"); sl.add_argument("uuid"); sl.add_argument("code")
    sc = sub.add_parser("call")
    sc.add_argument("bot_uuid")
    sc.add_argument("--to", required=True)
    sc.add_argument("--args", required=True)
    sc.add_argument("--out-did", default="")  # omit by default — passing it gave 'Unanswered'
    sc.add_argument("--cc", default="91")
    sc.add_argument("--tz", default="Asia/Kolkata")
    a = p.parse_args()
    if a.cmd == "whoami": whoami(a.uuid)
    elif a.cmd == "persona": persona(a.uuid, a.file)
    elif a.cmd == "lang": lang(a.uuid, a.code)
    elif a.cmd == "call": call(a.bot_uuid, a.to, a.args, a.out_did, a.cc, a.tz)


if __name__ == "__main__":
    main()
