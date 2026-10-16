# -*- coding: utf-8 -*-
"""extract_spec.py — pull the BEHAVIOURAL CONTRACT out of a conversation prompt.

Why this exists. The slim rewrite must not lose behaviour, and "I read it carefully" is not a
check. This extracts the things that are contractual — the spoken lines, the tool names and
payload fields, the input variables, the enum values — into a machine-comparable spec, so
`compare_spec.py` can say exactly what the slim prompt dropped.

Not everything it extracts must survive: a 219k prompt contains six wordings of the same rule and
five sample conversations, and the point of the rewrite is to keep one of each. What must survive
is every DISTINCT spoken line, every tool, every payload field, and every input variable.

Usage: python3 raya/slim/extract_spec.py <prompt.md> [-o spec.json]
"""
import io, json, re, sys, argparse, collections

# A spoken line = a run of Devanagari/Kannada inside straight or curly quotes.
QUOTED = re.compile(u'[""“”]([^""“”]{4,400}?)[""“”]')
INDIC = re.compile(u"[ऀ-ॿಀ-೿]")
TOKEN = re.compile(r"\$\{([A-Za-z_][A-Za-z0-9_]*)\}")
TOOL = re.compile(r"\b(get_profile|create_profile|update_profile|apply_job|create_job|update_job|"
                  r"update_job_details|update_job_status|get_talent_insights|get_jobs)\b")
# payload field names: `backtickedCamelCase` or "quoted_snake" next to a colon in a payload block
FIELD = re.compile(r"`([a-zA-Z][a-zA-Z0-9_]{2,40})`")
HEAD = re.compile(r"^(#{1,6})\s+(.*)$")


def norm_spoken(s):
    """Collapse whitespace and strip the bracketed slots so two wordings of the same line match."""
    s = re.sub(r"\s+", " ", s).strip()
    s = re.sub(r"\[[^\]]{1,40}\]", "[]", s)          # [role], [शहर] -> []
    s = re.sub(r"\$\{[A-Za-z_][A-Za-z0-9_]*\}", "[]", s)
    return s.strip(" ।.?!,—-")


def extract(path):
    txt = io.open(path, encoding="utf-8").read()
    spec = {}
    spec["path"] = path
    spec["chars"] = len(txt)

    # Spoken lines. Scanned PER BLOCK, never across the whole file: pairing quotes over 220k chars
    # means one stray unmatched quote shifts every pairing after it, and three real spoken lines in
    # the slim prompt were reported as dropped for exactly that reason. A block is a run of
    # consecutive blockquote (`> `) lines joined together — the multi-line job-list templates live
    # that way — or a single ordinary line. A stray quote can now only corrupt its own block.
    spoken = collections.Counter()
    blocks, cur = [], []
    for ln in txt.split("\n"):
        if ln.lstrip().startswith(">"):
            cur.append(re.sub(r"^\s*>\s?", "", ln))
        else:
            if cur:
                blocks.append("\n".join(cur)); cur = []
            blocks.append(ln)
    if cur:
        blocks.append("\n".join(cur))
    for b in blocks:
        for m in QUOTED.finditer(b):
            v = m.group(1)
            if INDIC.search(v):
                spoken[norm_spoken(v)] += 1
    spec["spoken_lines"] = dict(spoken)

    # input variables
    spec["input_variables"] = sorted(set(TOKEN.findall(txt)))

    # tools
    spec["tools"] = sorted(set(TOOL.findall(txt)))

    # payload / field identifiers, filtered to plausible field names
    stop = set("""true false null undefined string number boolean object array json api http https
    get post patch put delete uuid item_id user_id agent_id md5 sha256 yyyy mm dd""".split())
    fields = collections.Counter()
    for m in FIELD.finditer(txt):
        v = m.group(1)
        if v.lower() in stop or TOOL.fullmatch(v):
            continue
        fields[v] += 1
    spec["identifiers"] = {k: v for k, v in fields.items() if v >= 1}

    # section outline
    spec["sections"] = [(len(m.group(1)), m.group(2).strip()) for m in
                        (HEAD.match(l) for l in txt.split("\n")) if m]
    return spec


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("prompt")
    ap.add_argument("-o", "--out", default="")
    a = ap.parse_args()
    spec = extract(a.prompt)
    if a.out:
        io.open(a.out, "w", encoding="utf-8").write(json.dumps(spec, ensure_ascii=False, indent=1))
    print("%s: %d chars" % (a.prompt, spec["chars"]))
    print("  distinct spoken lines : %d  (%d total quoted occurrences)"
          % (len(spec["spoken_lines"]), sum(spec["spoken_lines"].values())))
    print("  input variables       : %d  %s" % (len(spec["input_variables"]), spec["input_variables"]))
    print("  tools                 : %d  %s" % (len(spec["tools"]), spec["tools"]))
    print("  identifiers           : %d" % len(spec["identifiers"]))
    print("  sections              : %d" % len(spec["sections"]))
    if a.out:
        print("  -> %s" % a.out)


if __name__ == "__main__":
    main()
