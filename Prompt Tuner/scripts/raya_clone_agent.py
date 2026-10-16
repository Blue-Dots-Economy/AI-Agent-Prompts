#!/usr/bin/env python3
"""raya_clone_agent.py — stand up a NEW conversation agent by cloning two existing ones.

Why: a new language variant of an existing bot needs (a) the SETTINGS of its A/B sibling —
timings, interruption thresholds, nudges, duration caps — and (b) the LANGUAGE machinery of the
production bot in that language: language_id, voice_id, the tool set whose payload templates carry
that language's `languageSpoken`, and its memory/output instructions. Hand-copying those in the
console is exactly the unrecorded drift `/raya-reconcile` exists to catch.

  python3 scripts/raya_clone_agent.py plan|apply <settings_target> <language_target> "<new name>" \
        <prompt_file> [--into <existing_uuid>]

`--into` PATCHes an existing agent instead of creating one (use it to repurpose a scratch agent).
Prints a KEY-FREE summary. NEVER writes the fetched tools object to disk (tool snapshots embed live
API keys and this repo is public).
"""
import copy, json, os, sys, urllib.error, urllib.request

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_env = {}
for _l in open(os.path.join(REPO, "raya/.env")):
    _l = _l.strip()
    if "=" in _l and not _l.startswith("#"):
        k, v = _l.split("=", 1)
        _env[k.strip()] = v.strip().strip('"').strip("'")
RAYA = _env["RAYA_BASE_URL"].rstrip("/"); RTOK = _env["RAYA_API_TOKEN"]
ENV = _env.get("RAYA_ENV", "prod")
AGENTS = json.load(open(os.path.join(REPO, "raya/agents.json")))["targets"]

CARRY_SETTINGS = ["allow_interruption", "allowed_silence_before_nudge", "allowed_speech_before_nudge",
                  "min_user_speech_to_interrupt", "required_silence_after_speech",
                  "max_call_duration_mins", "call_duration_exceed_message", "voicemail_msg",
                  "say_hello", "allow_call_transfer", "webhook_url", "out_did"]
CARRY_LANGUAGE = ["language_id", "voice_id", "tools", "memory_instructions", "memory_enabled",
                  "output_instructions", "output_fields"]
# NOTE: agent_args is NOT carried — the PATCH schema rejects it (400 unrecognized_keys), and the
# campaign supplies those per call anyway.


def uuid_for(t):
    for row in AGENTS:
        if row["id"] == t:
            u = (row.get("raya_agent_id") or {}).get(ENV, "")
            if not u: sys.exit(f"{t}: no {ENV} uuid")
            return u
    sys.exit(f"unknown target {t!r}")


def raya(path, method="GET", body=None):
    h = {"X-API-Key": RTOK, "User-Agent": "Mozilla/5.0", "Accept": "application/json"}
    data = json.dumps(body).encode() if body is not None else None
    if data is not None: h["Content-Type"] = "application/json"
    req = urllib.request.Request(RAYA + path, data=data, headers=h, method=method)
    try:
        with urllib.request.urlopen(req, timeout=180) as r:
            return r.status, json.loads(r.read() or b"{}")
    except urllib.error.HTTPError as e:
        return e.code, e.read()[:500].decode("utf8", "replace")


def main():
    mode, s_t, l_t, name, prompt_path = sys.argv[1:6]
    into = None
    if "--into" in sys.argv: into = sys.argv[sys.argv.index("--into") + 1]
    instructions = open(os.path.join(REPO, prompt_path), encoding="utf-8").read()
    st, S = raya("/api/agent/" + uuid_for(s_t)); S = S.get("data", S)
    lt, L = raya("/api/agent/" + uuid_for(l_t)); L = L.get("data", L)
    if st != 200 or lt != 200: sys.exit(f"GET failed {st}/{lt}")
    body = {"name": name, "instructions": instructions}
    for k in CARRY_SETTINGS:
        if k in S and S[k] is not None: body[k] = copy.deepcopy(S[k])
    for k in CARRY_LANGUAGE:
        if k in L and L[k] is not None: body[k] = copy.deepcopy(L[k])
    print(f"=== new agent {name!r}")
    print(f"  settings from {s_t}: " + ", ".join(f"{k}={json.dumps(body.get(k))[:28]}" for k in CARRY_SETTINGS if k in body))
    print(f"  language from {l_t}: language_id={body.get('language_id')} voice_id={body.get('voice_id')} "
          f"memory_enabled={body.get('memory_enabled')} tools=" +
          str([(t.get('function') or {}).get('name') for t in (body.get('tools') or {}).get('llm_tools', [])]))
    print(f"  instructions: {len(instructions)} bytes from {prompt_path}")
    print(f"  output_fields: {len(body.get('output_fields') or [])}  output_instructions: {len(body.get('output_instructions') or '')} bytes")
    if mode != "apply":
        print("(plan only — nothing sent)"); return
    if into:
        s2, r2 = raya("/api/agent/" + into, "PATCH", body); new_uuid = into
    else:
        s2, r2 = raya("/api/agent", "POST", body)
        new_uuid = (r2 or {}).get("uuid") if isinstance(r2, dict) else None
    if s2 not in (200, 201): sys.exit(f"write failed {s2}: {r2}")
    s3, D = raya("/api/agent/" + new_uuid); D = D.get("data", D)
    # Raya strips a trailing newline on write — compare without it (same rule raya_deploy.py uses)
    ok = (D.get("instructions") or "").rstrip("\n") == instructions.rstrip("\n")
    print(f"WRITE={s2} uuid={new_uuid} instructions_match={ok} "
          f"tools={[(t.get('function') or {}).get('name') for t in (D.get('tools') or {}).get('llm_tools', [])]}")
    if not ok: sys.exit("instructions read-back MISMATCH")
    print(f"OK — {name!r} live as {new_uuid}")


if __name__ == "__main__":
    main()
