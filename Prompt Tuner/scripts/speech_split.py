#!/usr/bin/env python3
"""speech_split.py: take a bot into a new language without ever handing a rule to a translator.

A conversation prompt is two kinds of text (root CLAUDE.md, "agnostic vs language-specific"): rules,
flow, variables, tool names, payloads and headings, which must stay byte-identical in every language,
and the words the bot SPEAKS, which must be re-authored. Field reports (Purple Dots, Oct 2026) showed
what goes wrong when a model rewrites the whole file: instructions and tool calls got translated, the
file bloated past the size where the bot stops calling tools, Hindi words survived inside Marathi, and a
city changed (Nagpur became Jabalpur). So the translator never sees a rule line. We split out only:

  1. SPEECH lines: any non-heading line containing the master's script (spoken lines, examples, number words);
  2. LANGUAGE-IDENTITY lines: English rule lines that NAME the master language or script ("Speak Hindi /
     Hinglish", "write in Devanagari"). They stay English, but must name the target language instead.
     A copied "speak Hindi" rule made a live Marathi call slip into Hindi.

Every other line is copied by machine, and `apply` proves it.

  python3 scripts/speech_split.py extract <master.md> <workdir> --lang <iso> [--src hi] [--chunks 4]
          [--pin "old=new|why" ...] [--names names.json] [--terms terms.md]
      -> <workdir>/chunk-<k>.json   [{"id": 17, "kind": "speech"|"lang-rule", "line": "..."}, ...]
         <workdir>/STYLE.md         the card every translating agent reads (style + term sheet + pins + rules)
         <workdir>/manifest.json

  python3 scripts/speech_split.py apply <master.md> <workdir> <out.md>
      reads <workdir>/chunk-<k>.out.json {"17": "<re-authored line>", "_notes": "..."}, writes <out.md>,
      prints the mechanical proof; exit 1 on any failure.

Per-language data (formal words, Hindi markers, insulting words, script range) lives in
raya/translations/lexicon.json; per-language style cards in raya/translations/style/<iso>.md.
"""
import argparse, json, os, re, sys
from collections import Counter

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LEX = json.load(open(os.path.join(REPO, "raya", "translations", "lexicon.json"), encoding="utf-8"))["languages"]
STYLE_DIR = os.path.join(REPO, "raya", "translations", "style")
VAR = re.compile(r"\$\{[A-Za-z0-9_]+\}")
SLOT = re.compile(r"\[[^\]]{2,60}\]")
DANDA = "।॥"                       # shared sentence marks: never counted as residue
SCRIPT_WORDS = {"Devanagari", "Kannada script", "Telugu script", "Tamil script", "Odia script", "Bengali script",
                "Gurmukhi", "Gujarati script", "Malayalam script", "Nastaliq"}
NEGATION = re.compile(r"\b(never|not|no|don't|do not|avoid|instead of|rather than|unlike|forbidden|banned)\b", re.I)


def script_re(iso):
    lo, hi = LEX[iso]["range"]
    return re.compile("[%s-%s]" % (chr(int(lo, 16)), chr(int(hi, 16))))


def letters(iso, s):
    """Characters of iso's script in s, ignoring the shared danda marks."""
    return [c for c in script_re(iso).findall(s) if c not in DANDA]


def identity_re(src, tgt=None):
    """English words naming the master language (and its script, unless the target shares that script)."""
    words = [re.escape(a) for a in LEX[src]["aliases"] if re.match(r"[A-Za-z]", a)]
    if not tgt or LEX.get(tgt, {}).get("range") != LEX[src]["range"]:
        words.append(re.escape(LEX[src]["script"].split(" ")[0]))
    return re.compile(r"\b(%s)\b" % "|".join(words))


def instructs(l, name_re):
    """True when an English rule line TELLS the bot to use a language/script (not when it cites a past call)."""
    for m in name_re.finditer(l):
        before, after = l[max(0, m.start() - 50):m.start()], l[m.end():m.end() + 25]
        if re.search(r"\b(speak|speaks|say|says it|respond|reply|talk|answer|write|written|use|using|spoken|everyday|simple|natural)\b[^.;:()]*$", before, re.I) \
                or re.search(r"\bin\s+(simple\s+|everyday\s+|spoken\s+|natural\s+)?$", before, re.I) \
                or re.match(r"\s*(/\s*\w+\s*)?(number words?|words?|script|only|language|speech|sentences?|lines?|text)\b", after, re.I):
            if not re.search(r"\b(never|not|no|avoid|instead of|rather than)\b", before, re.I) and not re.match(r"\s+(numerals|digits)\b", after, re.I):
                return True
    return False


def classify(L, src, tgt):
    srx, idre = script_re(src), identity_re(src, tgt)
    speech, ident = [], []
    for i, l in enumerate(L):
        if l.lstrip().startswith("#"):
            continue
        if any(c not in DANDA for c in srx.findall(l)):
            speech.append(i)
        elif idre.search(l):
            ident.append(i)
    return speech, ident


RULES = """## How to re-author each line (read once)
- Read STYLE.md and your chunk file in ONE turn (two Read calls together), then write your output file in the next turn.
- Each line comes from a voice-bot prompt. Lines of kind "speech" mix ENGLISH instruction text with SPOKEN text in the
  source language. Rewrite ONLY the spoken parts, as a real speaker of the target language would say them on this
  phone call: everyday words, short, warm, never bookish. Use the everyday-word table below; never the formal word.
- Keep EVERYTHING ELSE on the line byte-identical: English words, markdown (**, >, -, |, quotes), `${variables}`,
  [bracket slots], tool names, JSON, enum values, punctuation outside the spoken text, and the word Goodbye
  (it stays exactly `Goodbye`, in Latin letters, last word of the line, never translated or transliterated).
- Lines of kind "lang-rule" are ENGLISH rules that name the source language or script. Keep them English and keep
  their meaning; change only the language/script names so they describe the TARGET language and script. A rule
  that tells the bot to avoid the source language may keep naming it.
- A question stays a question, marked the way the target language marks one (see STYLE.md).
- Numbers are words, never digits; no currency symbols, no "/", no AM/PM, no abbreviations.
- Person, place, school, department and programme names: use the pinned spelling below when one is given; otherwise
  transliterate the SAME name into the target script. Never replace a name with a different local one.
- If a line has no natural equivalent (e.g. a Hindi example about masculine vs feminine verb forms, in a language
  whose verbs carry no gender), write the closest true line for the target language and say so in "_notes".
  Never output two lines that say the same thing.
- Output ONLY a JSON object: {"<id>": "<rewritten line>", ..., "_notes": "<optional, one or two lines>"}: every id.
"""


MATRIX = os.path.join(REPO, ".claude", "skills", "translate-prompt", "reference", "language-matrix.md")


def matrix_section(lang):
    """The language's section of the language matrix (register, numbers, honorifics, greeting, places, pitfalls)."""
    text = open(MATRIX, encoding="utf-8").read()
    m = re.search(r"^## [^\n]*\(`%s`\)\n(.*?)(?=^---|^## )" % re.escape(lang), text, re.S | re.M)
    return m.group(1).strip() if m else ""


def style_card(lang, pins, terms_md):
    lx = LEX.get(lang, {})
    card = f"# Target: {lx.get('name', lang)} (`{lang}`): the way a real caller speaks on the phone, never written language\n\n"
    sec = matrix_section(lang)
    card += (sec + "\n") if sec else (f"(No section for `{lang}` in the language matrix: add one before a real run.)\n")
    extra = os.path.join(STYLE_DIR, f"{lang}.md")
    if os.path.exists(extra):
        card += "\n## Lessons from earlier runs in this language\n" + open(extra, encoding="utf-8").read() + "\n"
    card += f"\n## Script\n{lx.get('script', '?')}. Numbers as words in this language.\n"
    card += f"\n## Gender\n{lx.get('gender', 'Write the rule for this language down before authoring.')}\n"
    card += f"\n## Questions\nMark a question with {lx.get('question', '?')}.\n"
    every = lx.get("min_terms_everyday") or {}
    formal = lx.get("formal") or {}
    if every or formal:
        card += "\n## Everyday words (use the right-hand word; the left-hand word is bookish)\n| meaning / bookish word | say |\n|---|---|\n"
        card += "".join(f"| {k} | {v} |\n" for k, v in every.items())
        card += "".join(f"| {k} | {v} |\n" for k, v in formal.items())
    if lx.get("denylist"):
        card += "\n## Never say (insulting words for disabilities; use the person's own words or a neutral description)\n"
        card += ", ".join(lx["denylist"]) + "\n"
    if lx.get("review") != "call-verified":
        card += "\n(These word lists are seeds awaiting a native speaker's review. Prefer what a real speaker says.)\n"
    if terms_md:
        card += "\n## Term sheet for this bot (FIXED: several agents work in parallel, use exactly these)\n" + terms_md + "\n"
    if pins:
        card += "\n## Pinned by the orchestrator before fan-out (use exactly these)\n" + "".join(
            f"- **{x['old']}** -> **{x['new']}** everywhere it is spoken. Why: {x['why']}\n" for x in pins)
    return card + "\n" + RULES


def extract(a):
    L = open(a.master, encoding="utf-8").read().split("\n")
    speech, ident = classify(L, a.src, a.lang)
    items = [{"id": i, "kind": "speech", "line": L[i]} for i in speech] + \
            [{"id": i, "kind": "lang-rule", "line": L[i]} for i in ident]
    items.sort(key=lambda x: x["id"])
    os.makedirs(a.work, exist_ok=True)
    size = -(-len(items) // a.chunks)
    for k in range(a.chunks):
        json.dump(items[k * size:(k + 1) * size], open(os.path.join(a.work, f"chunk-{k + 1}.json"), "w", encoding="utf-8"),
                  ensure_ascii=False, indent=0)
    pins = []
    for p in a.pin or []:
        pair, _, why = p.partition("|")
        old, _, new = pair.partition("=")
        pins.append({"old": old.strip(), "new": new.strip(), "why": why.strip()})
    names = json.load(open(a.names, encoding="utf-8")) if a.names else {}
    pins += [{"old": k, "new": v, "why": "pinned proper name"} for k, v in names.items()]
    terms = open(a.terms, encoding="utf-8").read() if a.terms else ""
    open(os.path.join(a.work, "STYLE.md"), "w", encoding="utf-8").write(style_card(a.lang, pins, terms))
    heads = [l for l in L if l.lstrip().startswith("#") and identity_re(a.src, a.lang).search(l)]
    json.dump({"master": os.path.relpath(a.master, REPO), "src": a.src, "lang": a.lang, "chunks": a.chunks,
               "speech_lines": speech, "identity_lines": ident, "total_lines": len(L), "pins": pins},
              open(os.path.join(a.work, "manifest.json"), "w", encoding="utf-8"), indent=1, ensure_ascii=False)
    print(f"{len(speech)} speech lines + {len(ident)} language-identity rule lines, of {len(L)}, -> {a.chunks} chunks in {a.work}/")
    print(f"the other {len(L) - len(speech) - len(ident)} lines (rules, headings, variables, tools, payloads) are copied by machine")
    if not matrix_section(a.lang):
        print(f"WARNING: no section for '{a.lang}' in the language matrix: add one before a real run")
    for h in heads:
        print(f"WARNING: heading names the master language and must stay identical across languages: {h.strip()!r}"
              " -> make it language-neutral in the MASTER first (via /update-prompt), e.g. 'the call language'")


def apply(a):
    L = open(a.master, encoding="utf-8").read().split("\n")
    man = json.load(open(os.path.join(a.work, "manifest.json"), encoding="utf-8"))
    src, lang, pins = man["src"], man["lang"], man.get("pins", [])
    speech, ident = man["speech_lines"], man["identity_lines"]
    owned = set(speech) | set(ident)
    lx = LEX.get(lang, {})
    same_script = LEX[src]["range"] == lx.get("range")
    new, notes = {}, []
    for f in sorted(os.listdir(a.work)):
        if f.endswith(".out.json"):
            d = json.load(open(os.path.join(a.work, f), encoding="utf-8"))
            if d.get("_notes"):
                notes.append(d.pop("_notes"))
            new.update({int(k): v for k, v in d.items() if not str(k).startswith("_")})
    fails, warns = [], []
    missing = [i for i in sorted(owned) if i not in new]
    if missing:
        fails.append(f"{len(missing)} lines not returned (first: line {missing[0] + 1})")
    O = list(L)
    pre = lambda x: re.match(r"^\s*(>\s*\*\*[A-Za-z ]+:\*\*|[-*|]|\d+\.)?", x).group(0)
    strip_code = lambda x: re.sub(r"\$\{[^}]+\}|\[[^\]]+\]|`[^`]*`|\{[^}]*\}", "", x)
    for i in sorted(owned):
        if i not in new:
            continue
        s, t = L[i], new[i]
        if sorted(VAR.findall(s)) != sorted(VAR.findall(t)):
            fails.append(f"line {i + 1}: ${{variables}} changed {VAR.findall(s)} -> {VAR.findall(t)}")
        if re.findall(r"`[^`]*`", s) != re.findall(r"`[^`]*`", t):
            fails.append(f"line {i + 1}: a `code` value (tool name / enum / payload) changed")
        if len(SLOT.findall(s)) != len(SLOT.findall(t)):
            fails.append(f"line {i + 1}: [slot] count changed")
        if pre(s) != pre(t) or s.count("|") != t.count("|"):
            fails.append(f"line {i + 1}: markdown structure changed ({pre(s)!r} -> {pre(t)!r})")
        if s.count("Goodbye") != t.count("Goodbye"):
            fails.append(f"line {i + 1}: the hang-up word Goodbye was dropped, added or doubled")
        elif "Goodbye" in s and s.rstrip(' "*.)').endswith("Goodbye") and not t.rstrip(' "*.)').endswith("Goodbye"):
            fails.append(f"line {i + 1}: Goodbye is no longer the last word")
        if re.search(r"[0-9]", strip_code(t)) and not re.search(r"[0-9]", strip_code(s)):
            fails.append(f"line {i + 1}: a digit appeared in speech")
        if s.count("?") and not t.count("?") and i in speech:
            fails.append(f"line {i + 1}: a question in the master is no longer a question")
        O[i] = t
    # residue: every spoken line must actually be in the target language (not "is it the right alphabet")
    if same_script:
        unchanged = [i + 1 for i in speech if new.get(i) == L[i]]
        if unchanged:
            fails.append(f"{len(unchanged)} speech lines returned unchanged (e.g. line {unchanged[0]}): same script hides "
                         "untranslated lines")
        for m in lx.get("hindi_markers", []):
            hits = [i + 1 for i in speech if m in new.get(i, "") and not NEGATION.search(new.get(i, ""))]
            if hits:
                fails.append(f"{LEX[src]['name']} word '{m.strip()}' left in {lx.get('name', lang)} speech, line(s) {hits[:5]}")
    else:
        res = [i + 1 for i in speech if letters(src, new.get(i, ""))]
        if res:
            fails.append(f"{LEX[src]['script']} letters left in {len(res)} speech lines (e.g. line {res[0]}); "
                         "the shared danda (।) is allowed")
        tgt = script_re(lang) if lang in LEX else None
        silent = [i + 1 for i in speech if tgt and not tgt.search(new.get(i, ""))]
        if silent:
            warns.append(f"{len(silent)} speech lines contain no {lx.get('name', lang)} letters (e.g. line {silent[0]})")
    # instructions must name the target language and script, never the master's
    idre = identity_re(src, lang)
    stale = [i + 1 for i, l in enumerate(O) if not l.lstrip().startswith("#") and instructs(l, idre)]
    if stale:
        fails.append(f"English rules still tell the bot to use {LEX[src]['name']}/{LEX[src]['script']} on line(s) {stale[:6]}")
    # pinned names and terms
    for pn in pins:
        left = [i + 1 for i in speech if pn["old"] in new.get(i, "") and pn["old"] != pn["new"]]
        if left:
            fails.append(f"pinned: '{pn['old']}' still spoken on line(s) {left[:5]}; must be '{pn['new']}'")
        need = [i + 1 for i in speech if pn["old"] in L[i] and pn["new"] not in new.get(i, "")]
        if need:
            fails.append(f"pinned: '{pn['new']}' (for '{pn['old']}') missing on line(s) {need[:5]}: a name was changed")
    # same-script names: a word kept verbatim somewhere in the translation is a name or a loanword; if it
    # vanished from one line while new words arrived, a name or place may have been swapped (Nagpur->Jabalpur).
    # The real guard is the central --names pin list; this only catches recurring names left unpinned.
    if same_script:
        tok = lambda x: set(re.findall(r"[\u0900-\u097F]{3,}", x))
        has = Counter(w for i in speech for w in tok(L[i]))
        kept_n = Counter(w for i in speech for w in tok(L[i]) & tok(new.get(i, "")))
        free = Counter(w for i in speech for w in tok(new.get(i, "")) - tok(L[i]))   # used where the master lacks it
        names = {w for w in has if has[w] >= 2 and kept_n[w] >= max(2, (2 * has[w] + 2) // 3) and not free[w]}
        gone_at = {}
        for i in speech:
            for w in tok(L[i]) & names:
                if w not in new.get(i, ""):
                    gone_at.setdefault(w, []).append(i + 1)
        for w, at in gone_at.items():
            warns.append(f"'{w}' is kept in {kept_n[w]} of {has[w]} lines but gone on line(s) {at[:6]}: "
                         "a changed name or place? (fine if it is an ordinary word)")

    # plain speech: bookish words and insulting words
    for w, sub in (lx.get("formal") or {}).items():
        hits = [i + 1 for i in speech if w in new.get(i, "") and not NEGATION.search(new.get(i, ""))]
        if hits:
            warns.append(f"bookish word '{w}' on line(s) {hits[:4]}: people say '{sub}'")
    for w in lx.get("denylist") or []:
        hits = [i + 1 for i in speech if re.search(r"(?<!\w)%s(?!\w)" % re.escape(w), new.get(i, ""))
                and not NEGATION.search(new.get(i, ""))]
        if hits:
            fails.append(f"insulting word '{w}' spoken on line(s) {hits[:4]}")
    # a distinction that collapsed (two different master lines -> one identical target line, side by side)
    for x, y in zip(speech, speech[1:]):
        if y == x + 1 and L[x] != L[y] and new.get(x) and new.get(x) == new.get(y):
            warns.append(f"lines {x + 1}-{y + 1} differ in the master but are identical now: drop one and register a divergence")
    open(a.out, "w", encoding="utf-8").write("\n".join(O))
    rules_same = all(O[i] == L[i] for i in range(len(L)) if i not in owned)
    heads_same = [l for l in L if l.lstrip().startswith("#")] == [l for l in O if l.lstrip().startswith("#")]
    vars_same = sorted(set(VAR.findall("\n".join(L)))) == sorted(set(VAR.findall("\n".join(O))))
    mb, ob = len("\n".join(L).encode()), len("\n".join(O).encode())
    print(f"\n  MECHANICAL PROOF: {os.path.relpath(a.out, REPO)}")
    print(f"   {'OK' if rules_same else 'XX'} {len(L) - len(owned)} rule / structure lines byte-identical to the master")
    print(f"   {'OK' if heads_same else 'XX'} section skeleton identical ({sum(1 for l in L if l.lstrip().startswith('#'))} headings)")
    print(f"   {'OK' if vars_same else 'XX'} ${{variables}} identical ({len(set(VAR.findall(chr(10).join(L))))} distinct)")
    print(f"   {'OK' if not missing else 'XX'} {len(owned) - len(missing)} of {len(owned)} lines re-authored "
          f"({len(speech)} spoken, {len(ident)} language-identity rules)")
    print(f"   size: master {mb:,} bytes -> {ob:,} bytes ({(ob - mb) * 100 // max(mb, 1):+d}%); run scripts/prompt_size.py check before deploy")
    for f in fails[:12]:
        print("   XX", f)
    for w in warns[:12]:
        print("   ..", w)
    for n in notes:
        print("   note from a translating agent:", n)
    ok = rules_same and heads_same and vars_same and not fails
    print("  " + ("PASS: only the spoken words and the language name changed" if ok else "FAIL: fix the lines above before deploying") + "\n")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sp = ap.add_subparsers(dest="cmd", required=True)
    e = sp.add_parser("extract")
    e.add_argument("master"); e.add_argument("work")
    e.add_argument("--lang", required=True); e.add_argument("--src", default="hi")
    e.add_argument("--chunks", type=int, default=4); e.add_argument("--pin", action="append")
    e.add_argument("--names"); e.add_argument("--terms")
    p = sp.add_parser("apply")
    p.add_argument("master"); p.add_argument("work"); p.add_argument("out")
    a = ap.parse_args()
    for k in ("master", "work", "out", "names", "terms"):
        if getattr(a, k, None):
            setattr(a, k, os.path.abspath(getattr(a, k)))
    if a.cmd == "extract":
        for code in (a.src, a.lang):
            if code not in LEX:
                sys.exit(f"unknown language '{code}': add it to raya/translations/lexicon.json first")
        extract(a)
    else:
        apply(a)
