#!/usr/bin/env python3
"""
verify_call.py — turn a real Raya call into an automated pass/fail verdict.

This is the *evaluation* half of the voice-test loop (the half that needs no
telephony). You (or an auto-dialer, later) place a call; this pulls that call
from the Raya API and checks it against a scenario's assertions — deterministically,
from the real transcript + call_output tool outcomes. No LLM, no new deps
(Python stdlib only), reuses raya/.env + raya/agents.json.

Usage:
  # verify the most recent call on an agent against a scenario
  python3 voice-harness/verify_call.py maya-hi-in --scenario voice-harness/scenarios/maya-inbound-mpl.json

  # verify a specific call by uuid
  python3 voice-harness/verify_call.py --uuid 49048e22-6f53-4bd8-8242-fe1132a66e5a \
      --scenario voice-harness/scenarios/maya-inbound-mpl.json

  # just dump what a call did (no scenario) — MPL offered? age asked? drop_reason?
  python3 voice-harness/verify_call.py maya-hi-in --facts

Options:
  --uuid <id>        verify this exact call (skips agent resolution)
  --latest           most recent call on the agent (default when no --uuid)
  --caller <num>     when listing, pick the most recent call from this caller number
  --scenario <path>  JSON scenario file with a "checks" array (see scenarios/)
  --facts            print the extracted facts and exit (no scenario needed)
  --json             machine-readable JSON verdict on stdout

Exit code: 0 if all non-info checks PASS, 1 if any FAIL, 2 on error.

Scenario check types (each yields PASS / FAIL / UNKNOWN):
  transcript_any   {patterns:[...], expect:bool}    observed = any pattern in AGENT turns
  transcript_user  {patterns:[...], expect:bool}    observed = any pattern in USER turns
  output_truthy    {field:str, expect:bool}         observed = bool(call_output[field])
  output_equals    {field:str, value:any}           observed = call_output[field] == value
  output_ge        {field:str, value:number}        observed = call_output[field] >= value
Each check may carry: id, desc, bug_pattern, severity ("error"|"info"; default error).
"""
import argparse, json, os, re, sys, urllib.request, urllib.error

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
UA = "Mozilla/5.0 (compatible; voice-harness/1.0; +prompt-tuner)"


def die(msg, code=2):
    print("error: " + msg, file=sys.stderr)
    sys.exit(code)


def load_env():
    path = os.environ.get("RAYA_ENV_FILE", os.path.join(REPO, "raya", ".env"))
    env = {}
    if os.path.exists(path):
        for line in open(path, encoding="utf-8"):
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            k, v = line.split("=", 1)
            env[k.strip()] = v.strip()
    base = env.get("RAYA_BASE_URL") or os.environ.get("RAYA_BASE_URL")
    token = env.get("RAYA_API_TOKEN") or os.environ.get("RAYA_API_TOKEN")
    if not base or not token:
        die("missing RAYA_BASE_URL / RAYA_API_TOKEN (raya/.env)")
    return base.rstrip("/"), token


def resolve_agent_uuid(target):
    path = os.environ.get("RAYA_AGENTS", os.path.join(REPO, "raya", "agents.json"))
    if not os.path.exists(path):
        die("agents.json not found: " + path)
    data = json.load(open(path, encoding="utf-8"))
    rows = data.get("agents", data) if isinstance(data, dict) else data
    env = (os.environ.get("RAYA_ENV") or "prod")
    for r in rows:
        if r.get("id") == target:
            aid = r.get("raya_agent_id")
            if isinstance(aid, dict):
                aid = aid.get(env)
            if not aid:
                die("target '%s' has no raya_agent_id for env '%s'" % (target, env))
            return aid
    die("target '%s' not found in agents.json" % target)


def api_get(base, token, path):
    req = urllib.request.Request(base + path, headers={"X-API-Key": token, "User-Agent": UA})
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return json.loads(r.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        die("HTTP %s on %s: %s" % (e.code, path, e.read().decode("utf-8", "replace")[:200]))
    except Exception as e:
        die("request failed on %s: %s" % (path, e))


def pick_call(base, token, agent_uuid, caller=None):
    d = api_get(base, token, "/api/call?agent_id=%s&limit=20&sort=desc" % agent_uuid)
    calls = d.get("calls", d) if isinstance(d, dict) else d
    if not isinstance(calls, list) or not calls:
        die("no calls found for agent %s" % agent_uuid)
    if caller:
        cand = [c for c in calls if str(c.get("caller_no", "")).endswith(str(caller)[-10:])]
        if not cand:
            die("no calls from caller ...%s" % str(caller)[-10:])
        calls = cand
    return calls[0].get("uuid")


def extract_facts(call):
    tr = call.get("call_transcript") or []
    agent_turns, user_turns = [], []
    for t in tr:
        if not isinstance(t, dict):
            continue
        role = str(t.get("role", "")).lower()
        content = t.get("content") or t.get("text") or ""
        if not isinstance(content, str):
            content = json.dumps(content, ensure_ascii=False)
        if role in ("user", "caller", "human", "customer"):
            user_turns.append(content)
        else:
            agent_turns.append(content)
    co = call.get("call_output") or {}
    return {
        "uuid": call.get("uuid"),
        "created_at": call.get("created_at"),
        "duration": call.get("call_duration"),
        "agent_text": "\n".join(agent_turns),
        "user_text": "\n".join(user_turns),
        "n_agent_turns": len(agent_turns),
        "output": co if isinstance(co, dict) else {},
    }


def _any(patterns, text):
    for p in patterns:
        if re.search(p, text):
            return True
    return False


def run_check(chk, facts):
    t = chk.get("type")
    co = facts["output"]
    try:
        if t == "transcript_any":
            obs = _any(chk["patterns"], facts["agent_text"])
            ok = obs == bool(chk.get("expect", True))
            return ok, obs
        if t == "transcript_user":
            obs = _any(chk["patterns"], facts["user_text"])
            ok = obs == bool(chk.get("expect", True))
            return ok, obs
        if t == "output_truthy":
            obs = bool(co.get(chk["field"]))
            ok = obs == bool(chk.get("expect", True))
            return ok, co.get(chk["field"])
        if t == "output_equals":
            obs = co.get(chk["field"])
            return obs == chk.get("value"), obs
        if t == "output_ge":
            v = co.get(chk["field"])
            if not isinstance(v, (int, float)):
                return None, v  # UNKNOWN
            return v >= chk["value"], v
    except KeyError as e:
        return None, "missing key %s" % e
    return None, "unknown check type %r" % t


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("target", nargs="?", help="agent id from agents.json (e.g. maya-hi-in)")
    ap.add_argument("--uuid")
    ap.add_argument("--latest", action="store_true")
    ap.add_argument("--caller")
    ap.add_argument("--scenario")
    ap.add_argument("--facts", action="store_true")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()

    base, token = load_env()
    if a.uuid:
        uuid = a.uuid
    elif a.target:
        uuid = pick_call(base, token, resolve_agent_uuid(a.target), a.caller)
    else:
        die("need a target agent id or --uuid")

    call = api_get(base, token, "/api/call/%s" % uuid)
    facts = extract_facts(call)

    # convenience derived facts
    co = facts["output"]
    derived = {
        "mpl_offered": _any([r"मार्केटर", r"प्रीमियर लीग", r" marketer", r"premier league", r"कॉम्पिटिशन", r"competition"], facts["agent_text"]),
        "age_asked": _any([r"उम्र कितनी", r"ವಯಸ್ಸು ಎಷ್ಟು", r"how old"], facts["agent_text"]),
        "gender_asked": _any([r"male हैं या female", r"male ಆ.*female", r"male or female"], facts["agent_text"]),
        "drop_reason": co.get("drop_reason"),
        "mpl_registration": co.get("mpl_registration"),
        "applications_count": co.get("applications_count"),
        "tried_to_apply": co.get("tried_to_apply"),
    }

    if a.facts or not a.scenario:
        out = {"call": {k: facts[k] for k in ("uuid", "created_at", "duration", "n_agent_turns")}, "facts": derived}
        if a.json:
            print(json.dumps(out, ensure_ascii=False, indent=2))
        else:
            print("call %s  (%s, %ss, %d agent turns)" % (facts["uuid"], facts["created_at"], facts["duration"], facts["n_agent_turns"]))
            for k, v in derived.items():
                print("  %-20s %s" % (k, v))
        return

    scen = json.load(open(a.scenario, encoding="utf-8"))
    checks = scen.get("checks", [])
    results, n_fail = [], 0
    for chk in checks:
        ok, obs = run_check(chk, facts)
        verdict = "PASS" if ok is True else ("FAIL" if ok is False else "UNKNOWN")
        sev = chk.get("severity", "error")
        if verdict == "FAIL" and sev != "info":
            n_fail += 1
        results.append({"id": chk.get("id"), "verdict": verdict, "observed": obs,
                        "bug_pattern": chk.get("bug_pattern"), "severity": sev, "desc": chk.get("desc")})

    report = {"scenario": scen.get("name"), "call": facts["uuid"], "created_at": facts["created_at"],
              "drop_reason": derived["drop_reason"], "results": results,
              "pass": n_fail == 0, "n_fail": n_fail}
    if a.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        print("scenario: %s   call: %s   (%s)" % (scen.get("name"), facts["uuid"], facts["created_at"]))
        print("drop_reason: %s\n" % derived["drop_reason"])
        for r in results:
            mark = {"PASS": "✅", "FAIL": "❌", "UNKNOWN": "❓"}[r["verdict"]]
            tag = (" [%s]" % r["bug_pattern"]) if r["bug_pattern"] else ""
            info = " (info)" if r["severity"] == "info" else ""
            print("  %s %-24s observed=%-8s%s%s  %s" % (mark, r["id"], r["observed"], tag, info, r["desc"] or ""))
        print("\n%s  (%d failing check%s)" % ("OVERALL: PASS" if n_fail == 0 else "OVERALL: FAIL", n_fail, "" if n_fail == 1 else "s"))
    sys.exit(0 if n_fail == 0 else 1)


if __name__ == "__main__":
    main()
