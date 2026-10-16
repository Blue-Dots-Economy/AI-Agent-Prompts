#!/usr/bin/env python3
"""prompt_size.py: will this prompt still call its tools on this bot? Check BEFORE translating or deploying.

Field finding (Purple Dots, Oct 2026): at full size the Kannada outbound bot held fluent 30-turn calls and made
ZERO tool calls, while telling callers eleven times their details were saved. No error, empty call report: the
failure looked like a successful call. The size where this starts is a ZONE, not a line, and it differs per bot
(our KKB prompts run at 270 KB and call tools; that Purple Dots bot failed near 112 KB). So the limit is
recorded per target in raya/agents.json, from evidence, never assumed:

  "max_prompt_bytes":    size at or above which this bot was SEEN to stop calling tools (a failing call id)
  "proven_prompt_bytes": the largest size a live call has PROVEN still calls tools on this bot
  "size_evidence":       "<call ids and date>"

  python3 scripts/prompt_size.py project <master.md> --lang <iso> [--src hi] [--target <id>]
      estimate the translated size (everyday style vs literal) and compare it with the target's limits
  python3 scripts/prompt_size.py check <file.md> --target <id>
      the same verdict for a finished file (raya_deploy.py runs this rule on every deploy)
  python3 scripts/prompt_size.py ratios
      measured size ratios between the registered language twins in this repo

Verdicts: OK; WARN (bigger than any size proven on this bot: the first test call must confirm tools fire, or slim
the MASTER first with /slim-prompt); BLOCK (at or past the size where this bot already failed).
"""
import argparse, json, os, re, statistics, sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LEX = json.load(open(os.path.join(REPO, "raya", "translations", "lexicon.json"), encoding="utf-8"))["languages"]
TARGETS = json.load(open(os.path.join(REPO, "raya", "agents.json"), encoding="utf-8"))["targets"]
# Indic scripts are 3 bytes per character in UTF-8, Latin is 1. A translation that keeps everyday loanwords comes
# out near the master's size (measured below); a literal, bookish one runs larger. Per-language literal ceilings
# are estimates until a twin exists in the repo.
LITERAL = {"kn": 1.25, "te": 1.25, "ta": 1.35, "ml": 1.4, "mr": 1.1, "bn": 1.15, "as": 1.2, "or": 1.2,
           "gu": 1.05, "pa": 1.05, "ur": 0.8, "hi": 1.0}


def rx(iso):
    lo, hi = LEX[iso]["range"]
    return re.compile("[%s-%s]" % (chr(int(lo, 16)), chr(int(hi, 16))))


def speech_bytes(text, iso):
    r = rx(iso)
    return sum(len(l.encode()) for l in text.split("\n") if r.search(l) and not l.lstrip().startswith("#"))


def target(tid):
    for t in TARGETS:
        if t["id"] == tid:
            return t
    sys.exit(f"unknown target '{tid}' (see raya/agents.json)")


def measured(lang):
    out = []
    for t in TARGETS:
        if t.get("language") != "hi" or "-hi-" not in t["id"]:
            continue
        twin = next((x for x in TARGETS if x["id"] == t["id"].replace("-hi-", f"-{lang}-")), None)
        if twin and os.path.exists(os.path.join(REPO, t["file"])) and os.path.exists(os.path.join(REPO, twin["file"])):
            a = speech_bytes(open(os.path.join(REPO, t["file"]), encoding="utf-8").read(), "hi")
            b = speech_bytes(open(os.path.join(REPO, twin["file"]), encoding="utf-8").read(), lang)
            if a and b:
                out.append((t["id"], twin["id"], b / a))
    return out


def verdict(size, row, label):
    hard, proven = row.get("max_prompt_bytes"), row.get("proven_prompt_bytes")
    ev = row.get("size_evidence", "")
    if hard and size >= hard:
        return "BLOCK", (f"{label} {size:,} B is at or past {hard:,} B, where this bot already stopped calling tools ({ev}). "
                         "Slim the MASTER (/slim-prompt) before translating; never slim one language alone.")
    if proven and size > proven:
        return "WARN", (f"{label} {size:,} B is bigger than any size proven to call tools on this bot ({proven:,} B, {ev}). "
                        "The FIRST test call must check that every tool fires; a fluent call with no tool calls is this failure.")
    if not proven and not hard:
        return "WARN", (f"no size evidence recorded for this bot ({label} {size:,} B). The first test call must check that "
                        "tools fire; then record proven_prompt_bytes + size_evidence in raya/agents.json.")
    return "OK", f"{label} {size:,} B is within the size proven on this bot ({proven:,} B)."


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sp = ap.add_subparsers(dest="cmd", required=True)
    p = sp.add_parser("project"); p.add_argument("master"); p.add_argument("--lang", required=True)
    p.add_argument("--src", default="hi"); p.add_argument("--target")
    c = sp.add_parser("check"); c.add_argument("file"); c.add_argument("--target", required=True)
    sp.add_parser("ratios")
    a = ap.parse_args()

    if a.cmd == "ratios":
        for lang in sorted(l for l in LEX if l != "hi"):
            m = measured(lang)
            if m:
                print(f"hi -> {lang}: median speech ratio {statistics.median(r for *_, r in m):.2f} over {len(m)} twins "
                      + ", ".join(f"{x}->{y} {r:.2f}" for x, y, r in m))
        return

    if a.cmd == "check":
        row = target(a.target)
        size = os.path.getsize(a.file)
        v, msg = verdict(size, row, os.path.basename(a.file))
        print(f"{v}: {msg}")
        sys.exit(2 if v == "BLOCK" else 0)

    text = open(a.master, encoding="utf-8").read()
    total, sb = len(text.encode()), speech_bytes(text, a.src)
    m = measured(a.lang)
    low = statistics.median(r for *_, r in m) if m else 1.0
    high = max(LITERAL.get(a.lang, 1.3), low)
    est_lo, est_hi = int(total - sb + sb * low), int(total - sb + sb * high)
    print(f"master {total:,} B, of which spoken lines {sb:,} B ({sb * 100 // max(total, 1)}%)")
    print(f"estimated {LEX[a.lang]['name']} size: {est_lo:,} B written in everyday speech with loanwords"
          f"{' (measured on ' + str(len(m)) + ' twins)' if m else ' (no twin in this repo yet: estimate)'}, "
          f"up to {est_hi:,} B if translated literally")
    if not a.target:
        print("no --target given: pass the new variant's target id (or the master's) to compare with this bot's limits")
        return
    row = target(a.target)
    worst = "OK"
    for size, label in ((est_lo, "everyday estimate"), (est_hi, "literal estimate")):
        v, msg = verdict(size, row, label)
        print(f"{v}: {msg}")
        worst = max(worst, v, key=["OK", "WARN", "BLOCK"].index)
    sys.exit(2 if worst == "BLOCK" else 0)


if __name__ == "__main__":
    main()
