# -*- coding: utf-8 -*-
"""create_slim_bot.py — stand up a NEW Raya agent that is a byte-for-byte clone of an existing
one EXCEPT for its `instructions`, so a prompt rewrite can be A/B tested without touching the
live bot.

Everything that shapes behaviour other than the prompt is copied from the source agent: the
language and voice ids, the tool schemas, the memory and output prompts, the DIDs, the
interruption and silence timings, the max call duration, the webhook. If any of those differed,
a latency or quality difference between the two bots would not be attributable to the prompt.

SECURITY. The source agent's `tools` blob contains live API keys in its tool configuration. This
script moves it API -> API in memory and **never writes it to disk**. Do not add a debug dump, do
not save the response, and do not commit any file containing it. (A tool snapshot was leaked to a
public repo on 2026-08-02 and had to be purged from history.)

Usage:
  python3 raya/slim/create_slim_bot.py --source <uuid> --name "<new agent name>" \
      --instructions <file.md> [--dry-run]
"""
import argparse, json, os, sys, urllib.error, urllib.request

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
_env = {}
for _l in open(os.path.join(REPO, "raya/.env")):
    _l = _l.strip()
    if "=" in _l and not _l.startswith("#"):
        _k, _v = _l.split("=", 1); _env[_k.strip()] = _v.strip().strip('"').strip("'")
BASE = _env["RAYA_BASE_URL"].rstrip("/"); TOKEN = _env["RAYA_API_TOKEN"]

# Fields copied verbatim from the source agent. `instructions` is deliberately NOT here.
# The create endpoint's Zod schema rejects three of them as unrecognized keys
# (agent_args, memory_enabled, memory_instructions), so the clone is two-phase:
# POST what create accepts, then PATCH the rest. The memory prompt is in the PATCH set and is
# NOT optional -- without it `${contact_memory}` is empty on every call and the A/B comparison
# would be measuring two different bots rather than two prompts.
CLONED_ON_CREATE = [
    "language_id", "voice_id", "tools", "output_instructions", "output_fields", "in_did",
    "out_did", "say_hello", "allow_interruption", "min_user_speech_to_interrupt",
    "required_silence_after_speech", "allowed_silence_before_nudge", "allowed_speech_before_nudge",
    "max_call_duration_mins", "call_duration_exceed_message", "voicemail_msg", "webhook_url",
    "allow_call_transfer", "transfer_destination_phone",
]
CLONED_ON_PATCH = ["agent_args", "memory_enabled", "memory_instructions"]
CLONED = CLONED_ON_CREATE + CLONED_ON_PATCH


def call(method, path, body=None):
    data = json.dumps(body).encode() if body is not None else None
    h = {"X-API-Key": TOKEN, "User-Agent": "Mozilla/5.0"}
    if data is not None:
        h["Content-Type"] = "application/json"
    req = urllib.request.Request(BASE + path, data=data, headers=h, method=method)
    try:
        with urllib.request.urlopen(req, timeout=120) as r:
            raw = r.read().decode()
            return r.status, (json.loads(raw) if raw.strip() else {})
    except urllib.error.HTTPError as e:
        return e.code, {"_err": e.read().decode()[:600]}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--source", required=True)
    ap.add_argument("--name", required=True)
    ap.add_argument("--instructions", required=True)
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()

    instructions = open(a.instructions, encoding="utf-8").read()

    st, src = call("GET", "/api/agent/" + a.source)
    if st != 200:
        print("GET source failed: %s %s" % (st, src)); sys.exit(1)

    body = {"name": a.name, "instructions": instructions}
    patch_after = {}
    copied, absent = [], []
    for k in CLONED:
        if k in src and src[k] is not None:
            (patch_after if k in CLONED_ON_PATCH else body)[k] = src[k]
            copied.append(k)
        else:
            absent.append(k)

    print("source        : %s  (%s)" % (a.source, src.get("name")))
    print("source prompt : %d chars" % len(src.get("instructions") or ""))
    print("new prompt    : %d chars  (%s)" % (len(instructions), a.instructions))
    print("cloned fields : %d  %s" % (len(copied), ", ".join(copied)))
    if absent:
        print("absent/null   : %s" % ", ".join(absent))
    # never print the tools blob — it carries live keys
    print("tools         : %d chars, copied in memory (NOT written to disk)"
          % len(json.dumps(src.get("tools") or {})))

    if a.dry_run:
        print("\n--dry-run: nothing created."); return

    st, res = call("POST", "/api/agent", body)
    if st not in (200, 201):
        print("\nCREATE FAILED: %s\n%s" % (st, json.dumps(res, ensure_ascii=False)[:600])); sys.exit(1)
    uu = res.get("uuid") or (res.get("data") or {}).get("uuid")
    print("\nCREATED: %s" % uu)

    if patch_after:
        st2, res2 = call("PATCH", "/api/agent/" + str(uu), patch_after)
        print("PATCH %s -> %s%s" % (", ".join(sorted(patch_after)), st2,
                                    "" if st2 == 200 else "  " + json.dumps(res2, ensure_ascii=False)[:300]))
        if st2 != 200:
            print("  the memory prompt / agent_args did NOT land -- the A/B is invalid until they do")

    # Read back and verify the prompt landed byte-for-byte, and that the clone really matched.
    st, back = call("GET", "/api/agent/" + str(uu))
    if st == 200:
        got = back.get("instructions") or ""
        print("read-back     : %d chars  %s" % (len(got), "IDENTICAL" if got == instructions else "MISMATCH"))
        for k in ("language_id", "voice_id", "out_did", "max_call_duration_mins",
                  "allow_interruption", "memory_enabled", "agent_args"):
            same = back.get(k) == src.get(k)
            print("  %-24s %s" % (k, "same as source" if same else
                                  "DIFFERS  src=%r new=%r" % (src.get(k), back.get(k))))
        st_t = json.dumps(back.get("tools") or {}) == json.dumps(src.get("tools") or {})
        print("  %-24s %s" % ("tools", "same as source" if st_t else "DIFFERS"))
        mi_same = (back.get("memory_instructions") or "") == (src.get("memory_instructions") or "")
        print("  %-24s %s (%d chars)" % ("memory_instructions",
              "same as source" if mi_same else "DIFFERS", len(back.get("memory_instructions") or "")))
        oi_same = (back.get("output_instructions") or "") == (src.get("output_instructions") or "")
        print("  %-24s %s (%d chars)" % ("output_instructions",
              "same as source" if oi_same else "DIFFERS", len(back.get("output_instructions") or "")))
    print("\nAdd this uuid to raya/agents.json by hand — never inferred (see the manifest note).")


if __name__ == "__main__":
    main()
