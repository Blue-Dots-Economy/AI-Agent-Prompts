#!/usr/bin/env python3
"""VoicERA integration for the Prompt Tuner: the VoicERA twin of raya_deploy.py + raya_testrun.py.

Talks to a VoicERA deployment's REST API (docs: https://voicera.mintlify.app/docs/api-reference),
e.g. the Blue Dots PoC at https://bluedots-poc.tech. Read-only unless a command says otherwise.

Credentials (git-ignored raya/.env):
    VOICERA_BASE_URL=https://bluedots-poc.tech
    VOICERA_EMAIL=...            # an account in the org (a dedicated eval account, not a person's)
    VOICERA_PASSWORD=...
  or VOICERA_TOKEN=<jwt>         # short-lived; email+password is preferred
    VOICERA_WS_URL=wss://<host>/agent/<org_id>/<agent_id>   # the eval agent's media socket, no token
    VOICERA_WS_TOKEN=<jwt>       # socket token from VoicERA (about 2 hours; they refresh it by hand)
    VOICERA_TEST_NUMBERS=911204404272,...   # optional: extra numbers `dial` may call

Targets live in raya/voicera/targets.json by agent name and the last four digits of its number. Agent and org ids are
resolved at run time and never committed. The media WebSocket needs a signed token since
2026-11-09 (it was open before), but the ids still stay out of git.

Commands
  whoami                                  who we are logged in as, org, role
  agents                                  every agent: name, number, models, prompt size
  pull   <target> [--out FILE]            save the agent's live config (prompts, behaviour, models)
  diff   <target> <FILE>                  live config vs a local file
  deploy <target> <FILE> [--yes]          PATCH the whole config (VoicERA does not merge), read back
  calls  <target> [--limit N]             recent calls of one agent, newest first
  record <call_id> [--out DIR] [--audio]  one call -> call record JSON (+ transcript, + recording)
  dial   <target> --to NUMBER [--var k=v ...] [--yes]
                                          VoicERA agent places an outbound call to a TESTER number
  ws-check                                open the eval agent's media socket with VOICERA_WS_TOKEN:
                                          token expiry, then OPEN or the close code (no REST login needed)
"""
import argparse, datetime as dt, json, os, re, sys, time, urllib.error, urllib.parse, urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TARGETS = os.path.join(ROOT, "raya", "voicera", "targets.json")
# Tester DIDs (Raya tester agents) that `dial` is allowed to call. Never a real caller's number.
TESTER_NUMBERS = {"911204404272", "911204404274", "911204413383", "917946350283", "918037006352"}


def env():
    e = {}
    p = os.path.join(ROOT, "raya", ".env")
    if os.path.exists(p):
        for line in open(p, encoding="utf-8"):
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                e[k.strip()] = v.strip().strip('"').strip("'")
    e.update({k: v for k, v in os.environ.items() if k.startswith("VOICERA_")})
    return e


class VoicERA:
    def __init__(self):
        e = env()
        self.base = (e.get("VOICERA_BASE_URL") or "").rstrip("/")
        if not self.base:
            sys.exit("VOICERA_BASE_URL is not set in raya/.env")
        self.extra_testers = {n.strip().lstrip("+") for n in e.get("VOICERA_TEST_NUMBERS", "").split(",") if n.strip()}
        self.token = e.get("VOICERA_TOKEN")
        if not self.token:
            if not (e.get("VOICERA_EMAIL") and e.get("VOICERA_PASSWORD")):
                sys.exit("set VOICERA_EMAIL + VOICERA_PASSWORD (or VOICERA_TOKEN) in raya/.env")
            r = self.req("POST", "/users/login", {"email": e["VOICERA_EMAIL"], "password": e["VOICERA_PASSWORD"]}, auth=False)
            self.token = r["access_token"]
        self._me = None

    def req(self, method, path, body=None, auth=True, raw=False, retries=3):
        url = self.base + "/api/v1" + path
        h = {"User-Agent": "Mozilla/5.0 (PromptTuner voicera_api)", "Accept": "*/*"}
        if auth:
            h["Authorization"] = "Bearer " + self.token
        data = None
        if body is not None:
            data = json.dumps(body, ensure_ascii=False).encode()
            h["Content-Type"] = "application/json"
        for i in range(retries):
            try:
                with urllib.request.urlopen(urllib.request.Request(url, data=data, headers=h, method=method), timeout=60) as r:
                    b = r.read()
                    return b if raw else (json.loads(b) if b else None)
            except urllib.error.HTTPError as ex:
                msg = ex.read().decode("utf-8", "replace")[:400]
                if ex.code in (429, 502, 503, 504) and i < retries - 1:
                    time.sleep(3 * (i + 1)); continue
                raise SystemExit(f"{method} {path} -> HTTP {ex.code}: {msg}")
            except urllib.error.URLError as ex:
                if i < retries - 1:
                    time.sleep(3); continue
                raise SystemExit(f"{method} {path} -> {ex}")

    def me(self):
        if not self._me:
            self._me = self.req("GET", "/users/me")
        return self._me

    def agents(self):
        return self.req("GET", "/agents")

    def agent(self, target):
        """Resolve a target name (targets.json), a phone number, an agent name, or an agent id."""
        names, last4 = {target}, None
        if os.path.exists(TARGETS):
            t = json.load(open(TARGETS)).get("targets", {}).get(target)
            if t:
                names.add(t["name"]); last4 = re.sub(r"\D", "", t.get("number", ""))[-4:] or None
        norm = lambda s: re.sub(r"\D", "", s or "")
        for a in self.agents():
            num = norm(a.get("linked_phone_number"))
            if a["agent_id"] in names or a["name"] in names or (norm(target) and len(norm(target)) >= 10 and norm(target) == num):
                if not last4 or num.endswith(last4):
                    return a
        sys.exit(f"no VoicERA agent matches {target!r} (see `agents`)")

    def calls(self, agent_id=None, limit=50):
        org, out, off = self.me()["org_id"], [], 0
        while len(out) < limit:
            page = self.req("GET", f"/calls/org/{org}?limit=200&offset={off}")
            cs = page.get("calls", [])
            out += [c for c in cs if not agent_id or c.get("agent_id") == agent_id]
            off += len(cs)
            if not cs or off >= page.get("total", 0):
                break
        return out[:limit]


# ---------- call record (one format the graders read; see docs/EVAL-HARNESS-PLAN.md) ----------

TS = re.compile(r"^\[(?P<ts>[^\]]+)\]\s*(?P<role>[a-zA-Z_]+):\s?(?P<text>.*)$")


def parse_transcript(text):
    """VoicERA transcript.txt: header, '---', then '[ISO ts] role: text' per completed turn."""
    turns = []
    body = text.split("\n---\n", 1)[1] if "\n---\n" in text else text
    for line in body.splitlines():
        m = TS.match(line)
        if m:
            turns.append({"ts": m["ts"], "role": "bot" if m["role"] == "assistant" else "caller" if m["role"] == "user" else m["role"],
                          "text": m["text"].strip()})
        elif line.strip() and turns:
            turns[-1]["text"] += "\n" + line.strip()
    return turns


def build_record(call, metrics, transcript_text, platform_url=""):
    """Join the call log, the per-turn pipeline metrics and the transcript into one call record."""
    turns = parse_transcript(transcript_text or "")
    stages = []
    m = metrics or {}
    lat = m.get("latencies") or {}
    for b in lat.get("breakdowns") or []:
        st = {x.get("stage"): round(x.get("duration_secs") or 0, 3) for x in b.get("ttfb") or []}
        procs = sorted({x.get("processor", "").split("#")[0] for x in b.get("ttfb") or [] if x.get("processor")})
        stages.append({
            "turn": b.get("turn_number"),
            "caller_turn": b.get("user_turn_start_time") is not None,
            "stt_s": st.get("stt"), "llm_s": st.get("llm"), "tts_s": st.get("tts"),
            "user_turn_s": round(b["user_turn_secs"], 3) if b.get("user_turn_secs") is not None else None,
            "tools": [f.get("function_name") for f in b.get("function_calls") or []],
            "services": procs,
        })
    interrupted = {t["turn_number"]: t.get("was_interrupted") for t in m.get("turns") or [] if "duration_secs" in t}
    for s in stages:
        s["interrupted"] = interrupted.get(s["turn"])
    u2b = [round(x, 3) for x in lat.get("user_to_bot_secs") or []]
    return {
        "schema": "call-record/v0",
        "platform": "voicera",
        "platform_url": platform_url,
        "call_id": call.get("call_id"),
        "agent": {"id": call.get("agent_id"), "name": call.get("agent_name")},
        "direction": call.get("call_type"),
        "status": call.get("status"), "answered": call.get("call_response"),
        "start": call.get("start_time_utc"), "end": call.get("end_time_utc"),
        "duration_s": round(call.get("duration") or 0, 1),
        "custom_variables": call.get("custom_variables") or {},
        "error": call.get("error_message"),
        "turns": turns,
        "timing": {
            "first_bot_speech_s": round(lat["first_bot_speech_secs"], 3) if lat.get("first_bot_speech_secs") is not None else None,
            "caller_to_bot_s": u2b,
            "per_turn": stages,
            "summary": m.get("summary"),
            "note": "Measured inside the VoicERA pipeline: excludes the phone network. "
                    "Tools run inside the LLM service and are not visible here except end_conversation.",
        },
        "tools_visible": sorted({t for s in stages for t in s["tools"]}),
        "audio": {"recording": "mono mix (caller and bot on one channel)"},
    }


# ---------- commands ----------

def cmd_whoami(v, a):
    me = v.me()
    print(f"{v.base}  {me.get('email')}  org={me.get('organisation_name')}  role={me.get('role')}")


def cmd_agents(v, a):
    for x in v.agents():
        c = x.get("config") or {}
        models = c.get("models") or {}
        # this deployment nests models per language ({"hi": {...}}); upstream has them flat
        per = models if "llm_config" in models else next(iter(models.values()), {}) if models else {}
        lm = lambda k: f"{(per.get(k) or {}).get('provider')}/{(per.get(k) or {}).get('model')}"
        print(f"{x['name'][:34]:34} {x.get('agent_category'):10} {x.get('linked_phone_number') or '-':14} "
              f"stt={lm('stt_config')} llm={lm('llm_config')} tts={lm('tts_config')} "
              f"prompt={len((c.get('prompts') or {}).get('system_prompt') or '')}ch")


def cmd_pull(v, a):
    ag = v.agent(a.target)
    out = a.out or os.path.join(ROOT, "raya", "voicera", "live", f"{a.target}.config.json")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    json.dump(ag["config"], open(out, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    print(f"saved {ag['name']} config -> {os.path.relpath(out, ROOT)}  (updated {ag.get('updated_at')})")


def _diff(live, local, path=""):
    out = []
    if isinstance(live, dict) and isinstance(local, dict):
        for k in sorted(set(live) | set(local)):
            out += _diff(live.get(k), local.get(k), f"{path}.{k}" if path else k)
    elif live != local:
        out.append((path, live, local))
    return out


def cmd_diff(v, a):
    ag = v.agent(a.target)
    d = _diff(ag["config"], json.load(open(a.file, encoding="utf-8")))
    if not d:
        print("IN SYNC: live config == local file"); return 0
    for p, l, r in d:
        print(f"- {p}\n    live : {json.dumps(l, ensure_ascii=False)[:200]}\n    local: {json.dumps(r, ensure_ascii=False)[:200]}")
    return 1


def cmd_deploy(v, a):
    ag = v.agent(a.target)
    new = json.load(open(a.file, encoding="utf-8"))
    d = _diff(ag["config"], new)
    if not d:
        print("nothing to deploy: live already matches"); return 0
    print(f"{ag['name']}: {len(d)} field(s) change: " + ", ".join(p for p, *_ in d))
    if not a.yes:
        print("dry run. Re-run with --yes to PATCH (the live config is saved first)."); return 0
    snap = os.path.join(ROOT, "raya", "voicera", "live", f"{a.target}.pre-deploy-{dt.datetime.now():%Y%m%d-%H%M%S}.json")
    os.makedirs(os.path.dirname(snap), exist_ok=True)
    json.dump(ag["config"], open(snap, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    r = v.req("PATCH", f"/agents/{ag['agent_id']}", {"config": new})
    left = _diff(r.get("config") or {}, new)
    print(f"PATCH ok; read-back {'MATCHES' if not left else 'DIFFERS on ' + ', '.join(p for p, *_ in left)}; rollback: {os.path.relpath(snap, ROOT)}")
    return 0 if not left else 1


def cmd_calls(v, a):
    ag = v.agent(a.target)
    for c in v.calls(ag["agent_id"], a.limit):
        print(f"{c['call_id']}  {c.get('created_at','')[:19]}  {c.get('call_type'):8} {c.get('status'):10} "
              f"{c.get('call_response') or '-':9} {round(c.get('duration') or 0):>4}s")


def cmd_record(v, a):
    call = v.req("GET", f"/calls/{a.call_id}")
    try:
        metrics = v.req("GET", f"/calls/{a.call_id}/metrics", retries=1)
    except SystemExit:
        metrics = None
    try:
        tr = v.req("GET", f"/calls/{a.call_id}/transcript", raw=True, retries=1).decode("utf-8", "replace")
    except SystemExit:
        tr = ""
    rec = build_record(call, metrics, tr, platform_url=f"{v.base}/history")
    out = a.out or os.path.join(ROOT, "raya", "voicera", "records")
    os.makedirs(out, exist_ok=True)
    base = os.path.join(out, a.call_id)
    json.dump(rec, open(base + ".json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    open(base + ".txt", "w", encoding="utf-8").write(tr)
    if a.audio:
        open(base + ".wav", "wb").write(v.req("GET", f"/calls/{a.call_id}/recording", raw=True))
    t = rec["timing"]
    print(f"{rec['call_id']}  {rec['direction']}  {rec['duration_s']}s  turns={len(rec['turns'])}  "
          f"caller->bot={t['caller_to_bot_s']}  tools={rec['tools_visible']}  -> {os.path.relpath(base, ROOT)}.json")


def cmd_dial(v, a):
    to = re.sub(r"\D", "", a.to)
    if to not in TESTER_NUMBERS | v.extra_testers:
        sys.exit(f"refusing to dial {a.to}: not a tester number (TESTER_NUMBERS / VOICERA_TEST_NUMBERS)")
    ag = v.agent(a.target)
    body = {"agent_id": ag["agent_id"], "to_number": "+" + to,
            "custom_variables": dict(kv.split("=", 1) for kv in a.var or [])}
    print(f"{ag['name']} -> +{to}  vars={list(body['custom_variables'])}")
    if not a.yes:
        print("dry run. Re-run with --yes to place the call."); return 0
    r = v.req("POST", "/calls/outbound", body)
    print(f"placed: call_id={r.get('call_id')} status={r.get('status')}")


def _jwt_claims(tok):
    import base64
    try:
        b = tok.split(".")[1]
        return json.loads(base64.urlsafe_b64decode(b + "=" * (-len(b) % 4)))
    except Exception:
        return {}


def cmd_ws_check(a):
    e = env()
    url, tok = e.get("VOICERA_WS_URL", "").split("?")[0], e.get("VOICERA_WS_TOKEN", "")
    if not url:
        sys.exit("set VOICERA_WS_URL (wss://<host>/agent/<org_id>/<agent_id>, no token) in raya/.env")
    if not tok:
        print("no VOICERA_WS_TOKEN set: checking that the socket refuses us")
    else:
        c = _jwt_claims(tok)
        if c.get("exp"):
            left = c["exp"] - time.time()
            when = dt.datetime.fromtimestamp(c["exp"]).strftime("%Y-%m-%d %H:%M")
            print(f"token: role={c.get('role')} expires {when} ({'EXPIRED' if left < 0 else f'{int(left // 60)} min left'})")
    try:
        import asyncio, websockets
    except ImportError:
        sys.exit("pip install websockets")

    async def go():
        full = url + ("?token=" + urllib.parse.quote(tok) if tok else "")
        try:
            async with websockets.connect(full, open_timeout=15, additional_headers={"User-Agent": "Mozilla/5.0"}) as ws:
                try:
                    m = await asyncio.wait_for(ws.recv(), 5)
                    return f"OPEN (first message: {type(m).__name__}, {len(m)} bytes)"
                except asyncio.TimeoutError:
                    return "OPEN (no message in 5 s; the agent waits for caller audio)"
                except websockets.ConnectionClosed as x:
                    return f"CLOSED {x.rcvd.code if x.rcvd else '?'} {x.rcvd.reason if x.rcvd else ''}"
        except websockets.InvalidStatus as x:
            return f"HTTP {x.response.status_code}"
        except Exception as x:
            return f"{type(x).__name__}: {x}"
    r = asyncio.run(go())
    print("socket:", r)
    if "1008" in r:
        print("  1008 = token missing, invalid or expired: ask VoicERA for a fresh one")
    return 0 if r.startswith("OPEN") else 1


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    s = p.add_subparsers(dest="cmd", required=True)
    s.add_parser("whoami"); s.add_parser("agents")
    x = s.add_parser("pull"); x.add_argument("target"); x.add_argument("--out")
    x = s.add_parser("diff"); x.add_argument("target"); x.add_argument("file")
    x = s.add_parser("deploy"); x.add_argument("target"); x.add_argument("file"); x.add_argument("--yes", action="store_true")
    x = s.add_parser("calls"); x.add_argument("target"); x.add_argument("--limit", type=int, default=20)
    x = s.add_parser("record"); x.add_argument("call_id"); x.add_argument("--out"); x.add_argument("--audio", action="store_true")
    x = s.add_parser("dial"); x.add_argument("target"); x.add_argument("--to", required=True)
    x.add_argument("--var", action="append"); x.add_argument("--yes", action="store_true")
    s.add_parser("ws-check")
    a = p.parse_args()
    if a.cmd == "ws-check":
        sys.exit(cmd_ws_check(a))
    sys.exit(globals()["cmd_" + a.cmd](VoicERA(), a) or 0)


if __name__ == "__main__":
    main()
