#!/usr/bin/env python3
"""language_checks.py: the prompt-level language checks, run on a finished translation.

These are the "Prompt" rows of the Purple Dots language-testing sheet (Surabhi, Oct 2026), made mechanical so
they run on every new language and every edit, not once by hand. The "Call" rows (tone, numbers heard right,
proper nouns, gender in practice, sensitive moments) need a live call and a listener: they stay in the test
sheet's language tab and in /voice-test.

  python3 scripts/language_checks.py <master.md> <target.md> --lang <iso> [--src hi] [--target <id>]
          [--config raya/translations/<bot>-checks.json] [--json out.json]

Exit 1 if any check FAILs. Works on any pair of files: it does not need the two files to be line-aligned.

Optional config (per bot) for the checks that need bot knowledge:
  {"disclosure": {"anchor": "<English words on the master's consent/disclosure rule line>",
                  "elements": {"app": {"hi": "पर्पल डॉट्स", "mr": "पर्पल डॉट्स"}, "one year": {"hi": "एक साल", ...}}},
   "denylist_required": true,
   "substitution_required": true}     # makes a missing everyday-word table a FAIL (default: WARN)
"""
import argparse, json, os, re, subprocess, sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LEXF = json.load(open(os.path.join(REPO, "raya", "translations", "lexicon.json"), encoding="utf-8"))
LEX, MIN_TERMS = LEXF["languages"], LEXF["min_terms"]
DANDA = "।॥"
NEG = re.compile(r"\b(never|not|no|don't|do not|avoid|instead of|rather than|forbidden|banned)\b", re.I)
GOODBYE_TRANSLIT = re.compile(r"गुड ?बाय|गुड ?बाई|ಗುಡ್ ?ಬೈ|గుడ్ ?బై|ଗୁଡ ?ବାଇ|গুড ?বাই|ગુડ ?બાય|ਗੁੱਡ ?ਬਾਏ|گڈ ?بائے|குட் ?பை|ഗുഡ് ?ബൈ")
QUOTE = re.compile(r"[\"“]([^\"“”]{2,400})[\"”]")


def rx(iso):
    lo, hi = LEX[iso]["range"]
    return re.compile("[%s-%s]" % (chr(int(lo, 16)), chr(int(hi, 16))))


def digits_re(iso):
    lo = int(LEX[iso]["range"][0], 16)
    native = "".join(chr(lo + 0x66 + k) for k in range(10)) if lo >= 0x0900 and lo < 0x0E00 else ""
    return re.compile(r"[0-9%s]|₹|%%|\bAM\b|\bPM\b|/" % native)


BAD_CTX = re.compile(r"\b(said|says|invented|failure|failed|wrong|old|bug|regression|instead|back as|came out|spoke|e\.g\. not|call `?[0-9a-f]{8})\b", re.I)
META = r"\s+(twin|master|file|version|prompt|bot|agent|side|call|calls|original|source|mirror)\b"


def quoted_as_bad(line, m, prev=""):
    """A quote that shows a wrong form: the left side of "x" -> "y", or right after never / not / said / wrong."""
    after, before = line[m.end():m.end() + 6], (prev + " " + line[:m.start()])[-60:]
    return "→" in after or "->" in after or bool(NEG.search(before)) or bool(BAD_CTX.search(before))


def spoken(text, iso, keep_bad=False):
    """(line_no, string) for every quoted string in the language's script that the bot may actually say."""
    r, out, prev = rx(iso), [], ""
    for n, line in enumerate(text.split("\n"), 1):
        if not line.lstrip().startswith("#"):
            for m in QUOTE.finditer(line):
                if r.search(m.group(1)) and (keep_bad or not quoted_as_bad(line, m, prev)):
                    out.append((n, m.group(1).strip()))
        prev = line
    return out


def section(text, pattern):
    """Body of the first section whose heading matches pattern (to the next heading of the same or higher level)."""
    L = text.split("\n")
    for i, l in enumerate(L):
        m = re.match(r"^(#{1,4}) ", l)
        if m and re.search(pattern, l, re.I):
            lvl, body = len(m.group(1)), []
            for x in L[i + 1:]:
                m2 = re.match(r"^(#{1,4}) ", x)
                if m2 and len(m2.group(1)) <= lvl:
                    break
                body.append(x)
            return l.strip(), "\n".join(body)
    return None, ""


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


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("master"); ap.add_argument("target")
    ap.add_argument("--lang", required=True); ap.add_argument("--src", default="hi")
    ap.add_argument("--target", dest="target_id"); ap.add_argument("--config"); ap.add_argument("--json")
    a = ap.parse_args()
    M, T = open(a.master, encoding="utf-8").read(), open(a.target, encoding="utf-8").read()
    src, lang = a.src, a.lang
    lx, sx = LEX[lang], LEX[src]
    cfg = json.load(open(a.config, encoding="utf-8")) if a.config else {}
    same_script = sx["range"] == lx["range"]
    Ms, Ts = spoken(M, src), spoken(T, lang)
    res = []

    def add(name, level, verdict, evidence):
        res.append({"scenario": name, "level": level, "result": verdict, "evidence": evidence})

    # 1. All snippets translated
    if same_script:
        marks = [m for m in lx.get("hindi_markers", [])]
        hits = [(n, s) for n, s in Ts for m in marks if m in s + " "]
        same = sorted(x for x in {s for _, s in Ms} & {s for _, s in Ts} - {"Goodbye"} if len(x.split()) >= 2)
        bad = len(hits) + len(same)
        add("All snippets translated", "Prompt", "FAIL" if bad else "PASS",
            (f"{len(same)} spoken strings identical to the {sx['name']} master (e.g. \"{same[0][:60]}\")" if same else "") +
            (f"; {sx['name']} words in {len({n for n, _ in hits})} spoken lines (e.g. line {hits[0][0]}: \"{hits[0][1][:60]}\")" if hits else "")
            or f"{len(Ts)} spoken strings, none left in {sx['name']}")
    else:
        sr = rx(src)
        resid = [(n, s) for n, s in spoken(T, lang) if any(c not in DANDA for c in sr.findall(s))]
        lines_with_src = [n for n, l in enumerate(T.split("\n"), 1)
                          if not l.lstrip().startswith("#") and any(c not in DANDA for c in sr.findall(l))]
        add("All snippets translated", "Prompt", "FAIL" if resid else ("WARN" if lines_with_src else "PASS"),
            (f"{sx['script']} letters inside {len(resid)} spoken strings (e.g. line {resid[0][0]})" if resid else
             f"no {sx['script']} letters in any spoken string (the shared danda is allowed)") +
            (f"; {len(lines_with_src)} other lines still carry {sx['script']} text (e.g. line {lines_with_src[0]}): "
             "check they are rules that name a word to avoid, not leftovers" if lines_with_src and not resid else ""))
    ratio = len(Ts) / max(len(Ms), 1)
    if ratio < 0.8:
        add("Spoken lines all present", "Prompt", "FAIL",
            f"target has {len(Ts)} spoken strings vs {len(Ms)} in the master ({ratio:.0%}): lines were dropped, not translated")

    # 2. Hangup token
    gb_m, gb_t = M.count("Goodbye"), T.count("Goodbye")
    tl = [n for n, l in enumerate(T.split("\n"), 1) if GOODBYE_TRANSLIT.search(l)]
    notlast = [n for n, l in enumerate(T.split("\n"), 1)
               if "Goodbye" in l and re.search(r"Goodbye[\s.,!।]*[^\s.,!।\"”*)`|]", l) and not NEG.search(l)]
    twice = [n for n, l in enumerate(T.split("\n"), 1) if len(re.findall(r"Goodbye[^A-Za-z]{0,3}Goodbye", l))]
    v = "FAIL" if tl or twice or gb_t < gb_m else ("WARN" if notlast else "PASS")
    add("Hangup token", "Prompt", v,
        f"Goodbye {gb_t}x in target vs {gb_m}x in master" + (f"; translated/transliterated Goodbye on lines {tl[:5]}" if tl else "")
        + (f"; doubled on lines {twice[:5]}" if twice else "") + (f"; words after Goodbye on lines {notlast[:5]}" if notlast else ""))

    # 3. Payload fields untranslated
    sets = {
        "${variables}": lambda x: set(re.findall(r"\$\{[A-Za-z0-9_]+\}", x)),
        # tool names, field names, enums: snake/camel/SCREAMING case or dotted. Title-case words are place or
        # person names (localised on purpose) and 8-hex tokens are call ids cited in notes: both skipped.
        "`code` identifiers (tool names, enums, fields)": lambda x: {t for t in re.findall(r"`([A-Za-z_][A-Za-z0-9_.]{1,60})`", x)
                                                         if not re.fullmatch(r"[A-Z][a-z]+|[0-9a-f]{8}", t)},
        "JSON keys": lambda x: set(re.findall(r"\"([A-Za-z_][A-Za-z0-9_]*)\"\s*:", x)),
    }
    diffs = []
    for k, f in sets.items():
        gone, extra = f(M) - f(T), f(T) - f(M)
        if gone or extra:
            diffs.append(f"{k}: missing {sorted(gone)[:4]} extra {sorted(extra)[:4]}")
    cm = [b for b in re.findall(r"```.*?```", M, re.S) if not rx(src).search(b)]
    ct = [b for b in re.findall(r"```.*?```", T, re.S) if not rx(lang).search(b)]
    if cm != ct:
        diffs.append(f"{sum(1 for b in cm if b not in ct)} code/payload blocks differ from the master")
    add("Payload fields untranslated", "Prompt", "FAIL" if diffs else "PASS",
        "; ".join(diffs) or "variables, code values, JSON keys and payload blocks byte-identical to the master")

    # 4. Questions written properly
    qm, qt = sum(1 for _, s in Ms if "?" in s or "؟" in s), sum(1 for _, s in Ts if "?" in s or "؟" in s)
    v = "PASS" if qt >= qm * 0.85 else ("WARN" if qt >= qm * 0.7 else "FAIL")
    add("Questions written properly", "Prompt", v,
        f"{qt} spoken questions in target vs {qm} in master; mark them with {lx.get('question', '?')}")

    # 5. Digits
    dr = digits_re(lang)
    dig = [(n, s) for n, s in Ts if dr.search(re.sub(r"\$\{[^}]+\}|\[[^\]]+\]", "", s))]
    add("Digits", "Prompt", "FAIL" if dig else "PASS",
        f"{len(dig)} spoken strings with a digit or symbol (e.g. line {dig[0][0]}: \"{dig[0][1][:60]}\")" if dig
        else "no digits, currency symbols, %, '/' or AM/PM in any spoken string")

    # 6. Substitution table
    head, body = section(T, r"substitut|everyday|\bplain (word|speech|language)|simple (word|speech)|word (list|table)|vocabulary|words? to use")
    _, mbody = section(M, r"substitut|everyday|\bplain (word|speech|language)|simple (word|speech)|word (list|table)|vocabulary|words? to use")
    if not head:
        add("Substitution table", "Prompt", "FAIL" if cfg.get("substitution_required") else "WARN",
            "no everyday-words section found (heading with substitution / everyday / plain / vocabulary)")
    else:
        miss = [t for t in MIN_TERMS if not re.search(t.replace("centre", "cent(re|er)"), body, re.I)]
        copied = body.strip() == mbody.strip()
        add("Substitution table", "Prompt", "FAIL" if copied else ("WARN" if miss else "PASS"),
            (f"'{head}' is byte-identical to the master's: copied, not rebuilt for {lx['name']}" if copied else
             f"'{head}' found" + (f"; missing minimum terms {miss}" if miss else "; all minimum terms covered")))

    # 7. Insulting words
    dh, dbody = section(T, r"never (say|use)|deny|insult|offensive|disrespect|words? (to avoid|never)|banned")
    words = lx.get("denylist") or []
    outside = T.replace(dbody, "") if dbody else T
    said = sorted({w for w in words for _, s in spoken(outside, lang) if re.search(r"(?<!\w)%s(?!\w)" % re.escape(w), s)})
    if said:
        add("Insulting words", "Prompt / Call", "FAIL", f"denylisted words spoken: {said}")
    elif not dh and (cfg.get("denylist_required") or words):
        add("Insulting words", "Prompt / Call", "FAIL" if cfg.get("denylist_required") else "WARN",
            f"no denylist section for {lx['name']}; seed words in raya/translations/lexicon.json: {words[:6]}")
    else:
        add("Insulting words", "Prompt / Call", "PASS",
            f"'{dh}' present; none of the {len(words)} seed words spoken" if dh else "no denylist needed for this bot")

    # 8. Gender rules
    gl_m = [l for l in M.split("\n") if re.search(r"\bgender|feminine|masculine\b", l, re.I) and not l.startswith("#")]
    gl_t = [l for l in T.split("\n") if re.search(r"\bgender|feminine|masculine\b", l, re.I) and not l.startswith("#")]
    names_lang = any(al.lower() in " ".join(gl_t).lower() for al in lx["aliases"])
    copied = gl_m and gl_t and set(gl_t) <= set(gl_m)
    v = "FAIL" if copied else ("PASS" if gl_t and names_lang else "WARN")
    add("Gender rules", "Prompt", v,
        ("gender rule lines are byte-identical to the master's: copied from " + sx["name"]) if copied else
        (f"{len(gl_t)} gender rule lines" + (f", naming {lx['name']}" if names_lang else
                                             f", none naming {lx['name']}: write this language's own rule (lexicon: {lx.get('gender', '')[:90]}...)")))

    # 9. Terms (consent disclosure elements): bot-specific
    dc = cfg.get("disclosure")
    if dc:
        miss = [k for k, per in dc["elements"].items() if per.get(lang) and per[lang] not in T]
        unk = [k for k, per in dc["elements"].items() if not per.get(lang)]
        add("Terms", "Prompt / Call", "FAIL" if miss else ("WARN" if unk else "PASS"),
            (f"missing disclosure elements {miss}" if miss else "all disclosure elements present")
            + (f"; no {lang} token configured for {unk}" if unk else ""))
    else:
        add("Terms", "Prompt / Call", "N/A", "no disclosure elements configured for this bot (--config)")

    # 10. Language identity in the English rules
    alias = [re.escape(x) for x in sx["aliases"] if re.match(r"[A-Za-z]", x)]
    if not same_script:
        alias.append(re.escape(sx["script"].split(" ")[0]))
    idre = re.compile(r"\b(%s)\b" % "|".join(alias))
    stale = [n for n, l in enumerate(T.split("\n"), 1) if not l.lstrip().startswith("#") and instructs(l, idre)]
    names_tgt = any(re.search(r"\b%s\b" % re.escape(x), T) for x in lx["aliases"] if re.match(r"[A-Za-z]", x))
    add("Instructions name this language", "Prompt", "FAIL" if stale else ("PASS" if names_tgt else "WARN"),
        (f"rules still tell the bot to use {sx['name']}/{sx['script']} on lines {stale[:8]}" if stale else
         f"no rule tells the bot to use {sx['name']}") + ("" if names_tgt else f"; and no rule names {lx['name']}"))

    # 11. Structure
    hm = [l for l in M.split("\n") if re.match(r"^#{1,4} ", l)]
    ht = [l for l in T.split("\n") if re.match(r"^#{1,4} ", l)]
    mem = "{${contact_memory}}"
    st = []
    if len(hm) != len(ht):
        st.append(f"{len(ht)} headings vs {len(hm)} in master")
    if mem in M and mem not in T:
        st.append("memory injection block missing")
    add("Structure", "Prompt", "FAIL" if st else "PASS", "; ".join(st) or f"{len(ht)} headings, same count as the master")

    # 12. Size
    if a.target_id:
        p = subprocess.run([sys.executable, os.path.join(REPO, "scripts", "prompt_size.py"), "check", a.target, "--target", a.target_id],
                           capture_output=True, text=True)
        out = (p.stdout or p.stderr).strip()
        add("Size (tools still fire)", "Prompt", out.split(":")[0] if out else "N/A", out)

    w = max(len(r["scenario"]) for r in res)
    print(f"\nLanguage checks: {os.path.basename(a.target)} ({lx['name']}) against {os.path.basename(a.master)} ({sx['name']})"
          f"{'' if lx.get('review') == 'call-verified' else '  [word lists for this language are seeds awaiting native review]'}\n")
    for r in res:
        print(f"  {r['result']:5} {r['scenario']:<{w}}  {r['evidence']}")
    fails = sum(r["result"] == "FAIL" for r in res)
    print(f"\n  {fails} FAIL, {sum(r['result'] == 'WARN' for r in res)} WARN, {sum(r['result'] == 'PASS' for r in res)} PASS."
          " Call-level checks (tone, numbers heard, proper nouns, gender in practice, sensitive moments) need a live call:"
          " see the test sheet's language tab.\n")
    if a.json:
        json.dump(res, open(a.json, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    sys.exit(1 if fails else 0)


if __name__ == "__main__":
    main()
