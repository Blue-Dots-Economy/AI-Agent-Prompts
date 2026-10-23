#!/usr/bin/env python3
"""prompt_structure.py: does every "go to Step N" in a prompt point where it says it does?

Field finding (Orange Dots, Oct 2026): the prompt's step numbering did not match its actual structure,
so a rule meant for one step sent the bot to the name question first. The tuner kept adding rules on
top; a fresh read of the whole prompt found the cause in minutes. A renumbered or renamed section leaves
every rule that cites it pointing at the wrong place or at nothing (analyser D125, and the dangling-label
patterns before it), and no amount of extra wording fixes that.

  python3 scripts/prompt_structure.py <prompt.md> [--map] [--json out.json]

Numbering schemes are kept apart: "Step 2", "Phase 2" and "Part 2" are three different things. A step is
defined by a heading ("## Step 2 — ...", "## 2 — ...") or a bold label at the start of a line
("**Step 2:**", "- **Phase 2** ...").

FAIL  a reference to a step, phase or part that is never defined ("Step 6" when there is no step 6);
      a reference whose own label names a DIFFERENT step of the same scheme ("Step 4 (consent)" when
      consent is Step 9): the rule sends the bot to the wrong place;
      two headings with the same number in the same scheme and section.
WARN  numbers out of order; a label (Turn B, Path A, Case B, Exit 3, Row 1, Scenario 12) used but never
      defined; "see <Name>" / "the <Name> section" with no heading of that name.
--map prints every step reference with the title it lands on, for a human read.
Exit 1 on any FAIL. Reads one file; changes nothing.
"""
import argparse, json, re, sys

HEAD = re.compile(r"^(#{1,6})\s+(.*)$")
KINDS = {"step": "step", "phase": "phase", "part": "part", "stage": "stage"}
NUM = r"([0-9]+(?:\.[0-9]+)?[a-z]?)"
HEAD_NUM = re.compile(r"^(?:(Step|Phase|Part|Stage)\s+)?%s\s*(?:[—–:.)-]|$)\s*(.*)$" % NUM, re.I)
BOLD_DEF = re.compile(r"^\s*(?:[-*]\s+|\d+\.\s+|>\s*)?\*\*(Step|Phase|Part|Stage)\s+%s\b[^*]*\*\*?\s*(.*)$" % NUM, re.I)
REF = re.compile(r"(?<![\w/#])(Step|step|Phase|phase|Part|part|Stage|stage|§|[Ss]ection)\s?%s\b(?!\s+of\s+(?:Phase|Step|Part))" % NUM)
LABEL_KINDS = "Turn|Path|Case|Exit|Scenario|Row|Branch|Example"
LABEL_REF = re.compile(r"\b(%s)\s+([A-Z]|[0-9]{1,3})\b(?!\.\d|\d)" % LABEL_KINDS)
LABEL_DEF = re.compile(r"(?:^#{1,6}\s+.*?|\*\*|^\s*[-*]\s+\**|^\|\s*\**|^\s*\d+\.\s+\**)\b(%s)\s+([A-Z]|[0-9]{1,3})\b" % LABEL_KINDS)
NAMED = re.compile(r"(?:\([Ss]ee|\b[Ss]ee|\bin the|\bunder|\bper the|\bfollow the|\bgo to the)\s+(?:the\s+)?[\"“*`]{1,2}"
                   r"([A-Z][\w /&'-]{2,48}?)[\"”*`]{1,2}(?:\s+(?:section|rules|block|table|flow))?")
STOP = set("the a an and or of to in on for with is are be then this that it its at by as from step section "
           "phase part before after own real name caller turn line call word only once first next same new here "
           "below above one two any every each not no".split())
WORDS = re.compile(r"[A-Za-z]{3,}")


def words(s):
    return {w.lower().rstrip("s") for w in WORDS.findall(s or "")} - STOP


def numkey(n):
    m = re.match(r"([0-9]+)(?:\.([0-9]+))?([a-z]?)", n)
    return (int(m.group(1)), int(m.group(2) or 0), m.group(3))


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("prompt"); ap.add_argument("--map", action="store_true"); ap.add_argument("--json")
    a = ap.parse_args()
    L = open(a.prompt, encoding="utf-8").read().split("\n")
    code = set()
    inside = False
    for i, l in enumerate(L):
        if l.strip().startswith("```"):
            inside = not inside
            code.add(i)
        elif inside:
            code.add(i)

    heads, defs, parents = [], {}, {}
    for i, l in enumerate(L):
        if i in code:
            continue
        m = HEAD.match(l)
        if m:
            level, text = len(m.group(1)), m.group(2).strip()
            parents[level] = i + 1
            for lv in [x for x in parents if x > level]:
                del parents[lv]
            hn = HEAD_NUM.match(text)
            h = {"line": i + 1, "level": level, "text": text, "kind": None, "num": None, "title": text,
                 "parent": parents.get(level - 1, 0)}
            if hn:
                h["kind"] = KINDS[(hn.group(1) or "step").lower()]
                h["num"], h["title"] = hn.group(2), (hn.group(3) or "").strip() or text
                defs.setdefault((h["kind"], h["num"]), []).append(h)
            heads.append(h)
            continue
        bn = re.match(r"^\s*(?:[-*]\s+)?\*\*%s\.\s" % NUM, l)       # "**4. Fields stored ...": a numbered point
        if bn:
            defs.setdefault(("step", bn.group(1)), []).append(
                {"line": i + 1, "level": 9, "text": l.strip()[:80], "title": l, "kind": "step", "num": bn.group(1), "bold": True})
        b = BOLD_DEF.match(l)
        if b:
            defs.setdefault((KINDS[b.group(1).lower()], b.group(2)), []).append(
                {"line": i + 1, "level": 9, "text": l.strip()[:80], "title": b.group(3) or l, "kind": KINDS[b.group(1).lower()],
                 "num": b.group(2), "bold": True})

    fails, warns, refmap = [], [], []
    # duplicates and order among numbered HEADINGS (bold sub-lists restart numbering, so they are skipped)
    groups = {}
    for h in heads:
        if h["num"]:
            groups.setdefault((h["kind"], h["level"], h["parent"]), []).append(h)
    for (kind, _, _), hs in groups.items():
        seen = {}
        for h in hs:
            if h["num"] in seen:
                fails.append(f"{kind} {h['num']} is used by two headings in the same section: line {seen[h['num']]['line']} "
                             f"'{seen[h['num']]['text'][:50]}' and line {h['line']} '{h['text'][:50]}'")
            seen[h["num"]] = h
        for x, y in zip(hs, hs[1:]):
            if numkey(y["num"]) < numkey(x["num"]):
                warns.append(f"{kind} numbers out of order: {x['num']} (line {x['line']}) comes before {y['num']} (line {y['line']})")

    def target(kind, n):
        for k in ([kind] if kind != "section" else ["step", "phase", "part", "stage"]):
            hs = defs.get((k, n)) or defs.get((k, n.rstrip("abcdefgh"))) or []
            if hs:
                return min(hs, key=lambda h: h["level"])
        return None

    labels = set()
    for i, l in enumerate(L):
        if i not in code:
            labels.update((m.group(1), m.group(2)) for m in LABEL_DEF.finditer(l))
    head_names = [h["text"].lower() for h in heads]

    for i, l in enumerate(L):
        if i in code or HEAD.match(l) or BOLD_DEF.match(l):
            continue
        local_list = re.match(r"^\s*\d+\.\s", l)          # "7. If yes, repeat from step 1": the list's own item
        quoted = [(q.start(), q.end()) for q in re.finditer(r"\"[^\"]*\"|“[^”]*”|\[[^\]]*\]", l)]
        for m in REF.finditer(l):
            word, n = m.group(1).lower(), m.group(2)
            if any(a <= m.start() < b for a, b in quoted):
                continue                                    # inside a quote: a spoken line or a past bad output
            if local_list and word == "step":
                continue
            kind = "section" if word in ("§", "section") else KINDS[word]
            tgt = target(kind, n)
            if not tgt:
                fails.append(f"line {i + 1}: '{m.group(0)}' points at a {kind} that is never defined")
                continue
            refmap.append({"line": i + 1, "ref": m.group(0), "lands_on": tgt["text"][:70], "context": l.strip()[:140]})
            ctx = l[m.end():m.end() + 60]
            lab = re.match(r"\s*\(([^)]{3,40})\)|\s*[,—–:-]\s*(?:the\s+)?([a-z][\w -]{3,40}?)(?=[.,;)]|$| step| turn| question)", ctx)
            label = (lab.group(1) or lab.group(2)) if lab else None
            lw = words(label)
            if lw and not (lw & words(tgt["title"] + " " + tgt["text"])):
                other = [h for (k, _), hs in defs.items() if k == tgt["kind"] for h in hs
                         if h is not tgt and h.get("num") != tgt.get("num") and lw <= words(h["title"] + " " + h["text"])]
                if other:
                    o = other[0]
                    fails.append(f"line {i + 1}: '{m.group(0)} ({label.strip()})' lands on '{tgt['text'][:50]}' (line {tgt['line']}), "
                                 f"but '{label.strip()}' is {o['kind']} {o['num']}: '{o['text'][:50]}' (line {o['line']})")
        for m in LABEL_REF.finditer(l):
            if (m.group(1), m.group(2)) not in labels:
                warns.append(f"line {i + 1}: '{m.group(0)}' is used but never defined (no heading, bold label, row or list item)")
        for m in NAMED.finditer(l):
            name = m.group(1).strip().lower()
            nw = words(name)
            if len(name) >= 4 and not any(name in h or (nw and nw <= words(h)) for h in head_names):
                warns.append(f"line {i + 1}: refers to '{m.group(1).strip()}' but no heading has that name")

    fails, warns = list(dict.fromkeys(fails)), list(dict.fromkeys(warns))
    nnum = sum(1 for h in heads if h["num"])
    print(f"\nStructure check: {a.prompt}  ({len(heads)} headings, {nnum} numbered, {len(refmap)} step references)\n")
    for f in fails:
        print("  FAIL", f)
    for w in warns[:40]:
        print("  WARN", w)
    if len(warns) > 40:
        print(f"  ... {len(warns) - 40} more warnings (use --json)")
    if a.map:
        print("\n  Where each step reference lands:")
        for r in refmap:
            print(f"   line {r['line']:>5}  {r['ref']:<12} -> {r['lands_on']}")
    print(f"\n  {len(fails)} FAIL, {len(warns)} WARN" + ("" if fails else ". Every step reference lands on a step that is defined.") + "\n")
    if a.json:
        json.dump({"fails": fails, "warns": warns, "map": refmap}, open(a.json, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    sys.exit(1 if fails else 0)


if __name__ == "__main__":
    main()
