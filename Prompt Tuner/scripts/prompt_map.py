#!/usr/bin/env python3
"""prompt_map.py: a map of a prompt's parts, built fresh from the prompt file every time, used to find
WHICH part of the prompt a bug comes from, WHAT ELSE a change affects, and WHICH rules compete.

Why a generated map and never a hand-kept copy: a structure maintained beside the prompt drifts from it
(an MSR 2025 study of 1,262 real prompt changes found most went undocumented and that edits introduced
logical inconsistencies; our own stale step references, analyser D125, are the same drift). So the map
is derived from the prompt itself, the way a compiler derives a program's dependency graph, and it is
correct for whatever the file says right now.

The ideas, and where they come from:
  - a prompt as a tree of components (Microsoft SAMMO "prompts as programs", POML) and a call as a walk
    through a graph of steps (Pipecat Flows, Retell conversation flows): sections are the nodes;
  - impact analysis by following dependencies (program slicing, def-use chains): which sections WRITE a
    variable / field / tool result and which READ it, so a fix to one shows what else it touches;
  - fault localisation from passing and failing runs (spectrum-based fault localisation, Ochiai): the
    sections that show up in failing calls and rarely in passing ones are the first suspects;
  - competing instructions (IHEval, "Control Illusion", 2025): models do not reliably resolve two rules
    that can both be "followed", so every rule about the same thing is listed side by side.

  python3 scripts/prompt_map.py outline  <prompt>                      # the tree: sections, steps, kinds
  python3 scripts/prompt_map.py locate   <prompt> --call <call.json|uuid> [--call ...]
                                                                       # which section produced each bot turn
  python3 scripts/prompt_map.py locate   <prompt> --say "<a line the bot said>"
  python3 scripts/prompt_map.py impact   <prompt> --section "<title words or line number>" [--sheet rows.json]
  python3 scripts/prompt_map.py rules-about <prompt> <tool | ${variable} | field | phrase>
  python3 scripts/prompt_map.py spectrum <prompt> --calls <dir or files> --fail <uuid,uuid,...>
                                                                       # rank sections by how often they appear in failing calls
Reads only. A call given as a uuid is fetched read-only from Raya (raya/.env).
"""
import argparse, difflib, glob, json, math, os, re, sys, unicodedata, urllib.request

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HEAD = re.compile(r"^(#{1,6})\s+(.*)$")
STEP = re.compile(r"^(?:(Step|Phase|Part|Stage)\s+)?([0-9]+(?:\.[0-9]+)?[a-z]?)\s*(?:[—–:.)-]|$)", re.I)
INDIC = re.compile(r"[ऀ-෿]")
QUOTE = re.compile(r"[\"“]([^\"“”]{6,400})[\"”]")
VAR = re.compile(r"\$\{([A-Za-z0-9_]+)\}")
TOOL = re.compile(r"\b((?:get|create|update|apply|record|close|fetch|search|send|save|check|list|delete)_[a-z0-9_]+)\b")
CODE = re.compile(r"`([A-Za-z_][A-Za-z0-9_.]{2,50})`")
WRITE = re.compile(r"\b(save|saves|saved|store|stores|stored|set|sets|write|writes|written|record|records|persist|"
                   r"update|updates|capture|captures|fill|fills|send|sends|pass|passes|put)\b", re.I)
READ = re.compile(r"\b(if|when|unless|only when|check|checks|has|have|holds|empty|missing|present|absent|is not|"
                  r"equals|contains|already|on record|known)\b", re.I)
MUST = re.compile(r"\b(must|always|mandatory|required|say|ask|call|do)\b", re.I)
NEVER = re.compile(r"\b(never|do not|don't|must not|no |forbidden|banned|skip|not)\b", re.I)
KIND_WORDS = [("tool", r"\btool|payload|get_|create_|update_|apply_|record_|json"),
              ("example", r"example|worked call|sample|scenario [a-z0-9]"),
              ("language", r"speak|language|script|tts|number|spelling|hearing|asr|pronunc|names of"),
              ("safety", r"safety|distress|self-harm|emergency|consent|disclos|privacy|dignity"),
              ("flow", r"^(step|phase|turn|part)\b|^[0-9]+(\.[0-9]+)?[a-z]?\s*[—–:-]|in order|flow|opening|closing|exit")]


def ident(c):
    """A field / enum / tool name, not a call id ("f6882d0b") or an example word ("Acme")."""
    return not re.fullmatch(r"[0-9a-f]{8}", c) and ("_" in c or "." in c or (c[:1].islower() and len(c) > 3)) \
        and c not in ("true", "false", "null", "none")


def norm(s):
    s = unicodedata.normalize("NFC", s or "")
    s = re.sub(r"\[[^\]]*\]|\$\{[^}]*\}|\{[^}]*\}", " ", s)
    s = re.sub(r"[़]", "", s)                        # nukta variants
    s = re.sub(r"[^\wऀ-෿ ]+", " ", s)
    return re.sub(r"\s+", " ", s).strip().lower()


def parse(path):
    L = open(path, encoding="utf-8").read().split("\n")
    secs, stack, in_code = [], [], False
    for i, l in enumerate(L):
        if l.strip().startswith("```"):
            in_code = not in_code
        m = None if in_code else HEAD.match(l)
        if m:
            lvl, title = len(m.group(1)), m.group(2).strip()
            while stack and stack[-1]["level"] >= lvl:
                stack.pop()
            sm = STEP.match(title)
            kind = "rules"
            for k, rx in KIND_WORDS:
                if re.search(rx, title, re.I):
                    kind = k
                    break
            path_ = [s["title"] for s in stack] + [title]
            if any(re.search(r"example|worked call|sample", t, re.I) for t in path_):
                kind = "example"
            sec = {"id": f"L{i + 1}", "line": i + 1, "end": len(L), "level": lvl, "title": title, "path": path_,
                   "step": (sm.group(2) if sm else None), "kind": kind}
            if secs:
                for prev in reversed(secs):
                    if prev["end"] == len(L):
                        prev["end"] = i
                        break
            for s in stack:
                pass
            stack.append(sec)
            secs.append(sec)
    # close spans: a section ends where the next heading of the same or higher level starts
    for a in secs:
        nxt = next((b for b in secs if b["line"] > a["line"] and b["level"] <= a["level"]), None)
        a["end"] = (nxt["line"] - 1) if nxt else len(L)
    own = {}
    for s in secs:                                         # each line belongs to its deepest section
        for j in range(s["line"], s["end"] + 1):
            own[j] = s
    for s in secs:
        s.update({"vars": set(), "tools": set(), "fields": set(), "writes": set(), "reads": set(), "spoken": []})
    for j, l in enumerate(L, 1):
        s = own.get(j)
        if not s:
            continue
        syms = {"$" + v for v in VAR.findall(l)} | set(TOOL.findall(l)) | {c for c in CODE.findall(l) if ident(c)}
        s["vars"] |= {x for x in syms if x.startswith("$")}
        s["tools"] |= set(TOOL.findall(l))
        s["fields"] |= {x for x in syms if not x.startswith("$") and x not in s["tools"]}
        for sent in re.split(r"(?<=[.;:])\s+", l):
            ss = {"$" + v for v in VAR.findall(sent)} | set(TOOL.findall(sent)) | {c for c in CODE.findall(sent) if ident(c)}
            if not ss:
                continue
            if WRITE.search(sent):
                s["writes"] |= ss
            if READ.search(sent):
                s["reads"] |= ss
        for m in QUOTE.finditer(l):
            if INDIC.search(m.group(1)):
                s["spoken"].append({"line": j, "text": m.group(1), "n": norm(m.group(1))})
        if l.lstrip().startswith(">") and INDIC.search(l):
            body = re.sub(r"^\s*>\s*(\*\*[^*]+\*\*:?)?\s*", "", l)
            if not re.match(r"^\s*>\s*\*\*(User|Caller|Seeker|Owner)", l, re.I):
                s["spoken"].append({"line": j, "text": body, "n": norm(body)})
    return L, secs


def find_section(secs, spec):
    if spec.isdigit():
        n = int(spec)
        c = [s for s in secs if s["line"] <= n <= s["end"]]
        return max(c, key=lambda s: s["level"]) if c else None
    w = spec.lower()
    c = [s for s in secs if w in s["title"].lower()] or [s for s in secs if all(x in s["title"].lower() for x in w.split())]
    return min(c, key=lambda s: s["level"]) if c else None


def label(s):
    return " > ".join(p[:40] for p in s["path"][-2:]) + f" (line {s['line']})"


def load_env():
    env = {}
    p = os.path.join(REPO, "raya", ".env")
    if os.path.exists(p):
        for l in open(p):
            if "=" in l and not l.startswith("#"):
                k, v = l.strip().split("=", 1)
                env[k] = v.strip().strip('"').strip("'")
    return env


def load_call(spec):
    if os.path.exists(spec):
        d = json.load(open(spec, encoding="utf-8"))
    else:
        env = load_env()
        req = urllib.request.Request(env["RAYA_BASE_URL"].rstrip("/") + "/api/call/" + spec,
                                     headers={"X-API-Key": env["RAYA_API_TOKEN"], "User-Agent": "Mozilla/5.0"})
        d = json.loads(urllib.request.urlopen(req, timeout=60).read())
    return d.get("data", d)


def turns_of(call):
    out = []
    for t in call.get("call_transcript") or []:
        if t.get("role") == "assistant":
            if t.get("content"):
                out.append(("say", t["content"]))
            for tc in t.get("tool_calls") or []:
                out.append(("tool", (tc.get("function") or {}).get("name", "?")))
    return out


def best_match(secs, text):
    n = norm(text)
    if not n:
        return None, 0.0, None
    best = (None, 0.0, None)
    for s in secs:
        for sp in s["spoken"]:
            if not sp["n"]:
                continue
            a, b = set(n.split()), set(sp["n"].split())
            if not a or not b or len(a & b) / len(b) < 0.3:
                continue
            r = difflib.SequenceMatcher(None, n, sp["n"]).ratio()
            r = max(r, len(a & b) / max(len(b), 1) * 0.95 if len(b) >= 4 else 0)
            if r > best[1]:
                best = (s, r, sp)
    return best


def tool_section(secs, name):
    c = [s for s in secs if name in s["title"]] or [s for s in secs if s["kind"] == "tool" and name in s["tools"]]
    return min(c, key=lambda s: s["level"]) if c else None


def cmd_outline(a, L, secs):
    for s in secs:
        tag = f"[{s['kind']}]" + (f" step {s['step']}" if s["step"] else "")
        extra = []
        if s["writes"]:
            extra.append("writes " + ", ".join(sorted(s["writes"]))[:70])
        if s["reads"] - s["writes"]:
            extra.append("checks " + ", ".join(sorted(s["reads"] - s["writes"]))[:70])
        print("  " * (s["level"] - 1) + f"- {s['title'][:70]}  {tag}  lines {s['line']}-{s['end']}, "
              f"{len(s['spoken'])} spoken lines" + ("  | " + "; ".join(extra) if extra else ""))


def trace_call(secs, call, verbose=True):
    hit, rows = set(), []
    for kind, val in turns_of(call):
        if kind == "tool":
            s = tool_section(secs, val)
            rows.append(("tool", val, s, 1.0, None))
        else:
            s, r, sp = best_match(secs, val)
            rows.append(("say", val, s, r, sp))
        if rows[-1][2] and rows[-1][3] >= 0.45:
            hit.add(rows[-1][2]["id"])
    if verbose:
        for kind, val, s, r, sp in rows:
            if kind == "tool":
                print(f"  TOOL {val:<24} -> {label(s) if s else 'no section names this tool'}")
            elif s and r >= 0.45:
                flag = "  <- copied from an EXAMPLE (D50: fix the example, not the rule)" if s["kind"] == "example" else ""
                print(f"  SAID {val[:70]!r}\n       -> {label(s)}  match {r:.0%}{flag}")
            else:
                print(f"  SAID {val[:70]!r}\n       -> NO prompt line close to this (improvised; best {r:.0%})")
    return hit, rows


def cmd_locate(a, L, secs):
    if a.say:
        s, r, sp = best_match(secs, a.say)
        print(f"best match {r:.0%}: {label(s) if s else '-'}" + (f"\n  prompt line {sp['line']}: {sp['text'][:120]}" if sp else ""))
        return
    for c in a.call:
        call = load_call(c)
        print(f"\n== call {call.get('uuid', c)}")
        trace_call(secs, call)


def cmd_impact(a, L, secs, path):
    s = find_section(secs, a.section)
    if not s:
        sys.exit(f"no section matches {a.section!r}; run 'outline' to see the titles")
    print(f"If you change: {label(s)}  [{s['kind']}]\n")
    inside = [x for x in secs if s["line"] <= x["line"] <= s["end"]]
    writes = set().union(*(x["writes"] for x in inside)); reads = set().union(*(x["reads"] for x in inside))
    allsyms = set().union(*(x["vars"] | x["tools"] | x["fields"] for x in inside))
    # 1. sections that point at it
    words = set(re.findall(r"[a-z]{4,}", s["title"].lower())) - {"step", "turn", "only", "with", "then", "from"}
    lab = re.match(r"((?:Turn|Path|Case|Exit|Row|Scenario|Branch|Part|Phase|Step)\s+[A-Z0-9][0-9.]*[a-z]?)\b", s["title"])
    name = re.split(r"\s+[—–(:-]\s*", re.sub(r"^[0-9.]+[a-z]?\s*[—–:-]\s*", "", s["title"]))[0].strip()
    refs = []
    for j, l in enumerate(L, 1):
        if s["line"] <= j <= s["end"] or HEAD.match(l):
            continue
        hit = (s["step"] and re.search(r"\b(?:[Ss]tep|§|[Ss]ection)\s?%s\b" % re.escape(s["step"]), l)) or \
              (lab and re.search(r"\b%s\b" % re.escape(lab.group(1)), l)) or \
              (len(name) >= 8 and name.lower() in l.lower())
        if hit:
            o = max((x for x in secs if x["line"] <= j <= x["end"]), key=lambda x: x["level"], default=None)
            if o:
                refs.append((j, o))
    print("1. Rules elsewhere that point at it (they break if it is renamed, renumbered or moved):")
    seen = set()
    for j, o in refs or [(None, None)]:
        if o and o["id"] in seen:
            continue
        seen.add(o["id"] if o else None)
        print(f"   line {j}: {label(o)}" if o else "   none")
        if len(seen) >= 12:
            print(f"   ... and more ({len(refs)} lines in all)"); break
    # 2. data flow
    print("\n2. Values it writes, and who else reads them (re-test those steps):")
    shown = 0
    for sym in sorted(writes):
        readers = [x for x in secs if sym in x["reads"] and x["kind"] != "example" and not (s["line"] <= x["line"] <= s["end"])]
        if readers:
            print(f"   {sym}: read by " + "; ".join(label(x) for x in readers[:4])); shown += 1
    print("   none found" if not shown else "", end="" if shown else "\n")
    print("\n3. Values it depends on, and who else writes them (a wrong value may come from there):")
    shown = 0
    for sym in sorted(reads - writes):
        writers = [x for x in secs if sym in x["writes"] and x["kind"] != "example" and not (s["line"] <= x["line"] <= s["end"])]
        if writers:
            print(f"   {sym}: written by " + "; ".join(label(x) for x in writers[:4])); shown += 1
    if not shown:
        print("   none found")
    guard_slot = sorted(sym for sym in reads & writes)
    if guard_slot:
        print(f"   NOTE: {', '.join(guard_slot)} is both checked and written in this part: the storage slot doubles as "
              "the evidence slot (root CLAUDE.md, D3 smell (a)). Check what the weakest value satisfying the check is.")
    # 3. tools
    tools = set().union(*(x["tools"] for x in inside))
    if tools:
        print("\n4. Tools it uses (their contracts must still match): " + ", ".join(sorted(tools)))
    # 4. mirrors
    mirrors = []
    try:
        T = json.load(open(os.path.join(REPO, "raya", "agents.json")))["targets"]
        rel = os.path.relpath(os.path.abspath(path), REPO)
        me = next((t for t in T if t["file"] == rel), None)
        if me:
            for t in T:
                same_family = os.path.dirname(t["file"]) == os.path.dirname(rel) and \
                    (("Signals" in t["file"]) == ("Signals" in rel)) and (("Inbound" in t["file"]) == ("Inbound" in rel))
                if t["file"] != rel and t.get("kind") == "conversation" and t.get("language") != me.get("language") \
                        and same_family and t.get("direction") == me.get("direction"):
                    mirrors.append(t)
    except (OSError, ValueError, KeyError):
        pass
    print("\n5. The same part in the other languages (a change lands in every one, each tested on its own):")
    for t in mirrors or [None]:
        if t:
            ok = any(l.strip() == L[s["line"] - 1].strip() for l in open(os.path.join(REPO, t["file"]), encoding="utf-8"))
            print(f"   {t['id']}: {t['file']}" + ("" if ok else "  (no identical heading: check it exists there)"))
        else:
            print("   none registered")
    # 5. tests
    if a.sheet:
        d = json.load(open(a.sheet, encoding="utf-8"))
        rows = [r for tab in d.get("bot_tabs", {}).values() for r in tab]
        spoken = [sp["n"] for x in inside for sp in x["spoken"]]
        hits = []
        for r in rows:
            ex = norm(r.get("expected", ""))
            if any(sp and len(sp) > 12 and sp[:40] in ex for sp in spoken) or \
                    any(w in (r.get("phase", "") + " " + r.get("scenario", "")).lower() for w in words if len(w) > 5):
                hits.append(r)
        print(f"\n6. Test rows that exercise it ({len(hits)}): re-run these after the change (Tier 2):")
        for r in hits[:20]:
            print(f"   {r.get('id')}: {r.get('scenario', '')[:80]}")
    else:
        print("\n6. Test rows: pass --sheet <rows.json> (scripts/testcase_sheet.py pull) to list the rows to re-run.")


def cmd_rules_about(a, L, secs):
    term = a.term.strip()
    rx = re.compile(re.escape(term), re.I)
    hits = []
    for j, l in enumerate(L, 1):
        if rx.search(l) and not HEAD.match(l):
            o = max((x for x in secs if x["line"] <= j <= x["end"]), key=lambda x: x["level"], default=None)
            hits.append((j, o, l.strip()))
    by = {}
    for j, o, l in hits:
        by.setdefault(o["id"] if o else "-", []).append((j, o, l))
    print(f"Every rule about {term!r}: {len(hits)} lines in {len(by)} sections\n")
    musts, nevers = [], []
    for k, rows in by.items():
        o = rows[0][1]
        print(f"- {label(o) if o else 'top of file'}  [{o['kind'] if o else '-'}]")
        for j, _, l in rows[:4]:
            print(f"    {j}: {l[:150]}")
            sent = next((x for x in re.split(r"(?<=[.;])\s+", l) if rx.search(x)), l)
            (nevers if NEVER.search(sent) else musts if MUST.search(sent) else []).append((j, o))
    if musts and nevers:
        ms = sorted({label(o) for _, o in musts if o}); ns = sorted({label(o) for _, o in nevers if o})
        print(f"\nPossible competing rules: {len(musts)} lines direct it and {len(nevers)} lines forbid or limit it, across "
              f"{len(set(ms) | set(ns))} sections. Read them together: where two can both be 'followed' in the same moment, "
              "models do not reliably pick the intended one (ladder rung 2), so scope or delete one. Most pairs are fine "
              "(a 'never before X' next to a 'do it after X'); this list is for reading, not a verdict.")


def cmd_spectrum(a, L, secs):
    files = []
    for c in a.calls:
        files += sorted(glob.glob(os.path.join(c, "*.json"))) if os.path.isdir(c) else [c]
    fail = {x.strip() for x in (a.fail or "").split(",") if x.strip()}
    cov, verdict = {}, {}
    for f in files:
        call = load_call(f)
        u = call.get("uuid") or os.path.basename(f)
        hit, _ = trace_call(secs, call, verbose=False)
        cov[u] = hit
        verdict[u] = any(u.startswith(x) for x in fail)
    nf = sum(verdict.values()); npass = len(verdict) - nf
    if not nf or not npass:
        sys.exit(f"{len(files)} calls, {nf} failing: need at least one failing and one passing call (pass --fail <uuid prefixes>)")
    rank = []
    for s in secs:
        ef = sum(1 for u, h in cov.items() if s["id"] in h and verdict[u])
        ep = sum(1 for u, h in cov.items() if s["id"] in h and not verdict[u])
        if ef:
            rank.append((ef / math.sqrt(nf * (ef + ep)), ef, ep, s))
    rank.sort(key=lambda x: -x[0])
    print(f"{len(files)} calls ({nf} failing, {npass} passing). Sections ranked by how strongly they go with failing calls "
          "(Ochiai: 1.0 = in every failing call and no passing one):\n")
    for sc, ef, ep, s in rank[:12]:
        print(f"  {sc:.2f}  in {ef}/{nf} failing, {ep}/{npass} passing   {label(s)}  [{s['kind']}]")
    print("\nA ranking, not a verdict: a section that runs on every call scores low even if it is wrong ('coincidentally "
          "correct' calls), and a section the bot never quotes does not show up at all. Read the top 3 against the "
          "failing transcripts, then run D1-D3 (root CLAUDE.md) before any edit.")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sp = ap.add_subparsers(dest="cmd", required=True)
    o = sp.add_parser("outline"); o.add_argument("prompt")
    l = sp.add_parser("locate"); l.add_argument("prompt"); l.add_argument("--call", action="append", default=[]); l.add_argument("--say")
    i = sp.add_parser("impact"); i.add_argument("prompt"); i.add_argument("--section", required=True); i.add_argument("--sheet")
    r = sp.add_parser("rules-about"); r.add_argument("prompt"); r.add_argument("term")
    s = sp.add_parser("spectrum"); s.add_argument("prompt"); s.add_argument("--calls", nargs="+", required=True); s.add_argument("--fail")
    a = ap.parse_args()
    L, secs = parse(a.prompt)
    if a.cmd == "outline":
        cmd_outline(a, L, secs)
    elif a.cmd == "locate":
        if not a.call and not a.say:
            sys.exit("give --call <file|uuid> or --say '<line>'")
        cmd_locate(a, L, secs)
    elif a.cmd == "impact":
        cmd_impact(a, L, secs, a.prompt)
    elif a.cmd == "rules-about":
        cmd_rules_about(a, L, secs)
    else:
        cmd_spectrum(a, L, secs)


if __name__ == "__main__":
    main()
