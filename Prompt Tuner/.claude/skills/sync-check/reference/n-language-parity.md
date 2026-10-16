# N-language parity: one master, N mirrors

Mechanics for `/sync-check`. Two languages (Hindi and Kannada) is the special case of this, not the
model. Nothing here lists languages: the language set is always **discovered** from `raya/agents.json`
(each conversation target's `language` code), so taking a bot into another language needs no edit to
this file or to `SKILL.md`.

Read together with `../../update-prompt/reference/prompt-anatomy.md` (the AGNOSTIC / SPECIFIC / MIXED
taxonomy): every parity decision below depends on those tags.

---

## 1. Resolving the family

### Sync family
A **sync family** is the set of files that are *the same bot in different languages*: one bot folder,
one direction, one backend (Signals or legacy). Files from different families are **not** mirrors of
each other and are never diffed against each other: `KKB Placeholder Kannada.md` (legacy) is not a
mirror of `KKB Placeholder Hindi Signals.md` (Signals); an outbound prompt is not a mirror of an
inbound one; a `<Bot>-Slim/` A/B twin is its own family, never a mirror of the production prompt.

Print every family, its languages and its master straight from the manifests:

```bash
cd "/Users/parthbansal/EkStep/Prompt Tuner"
python3 - <<'PY'
import json, collections
targets = json.load(open("raya/agents.json"))["targets"]
try:
    fleet = {b["file"]: b.get("master_language") for b in json.load(open("raya/regression/fleet.json"))["bots"]}
except Exception:
    fleet = {}
fam = collections.defaultdict(list)
for t in targets:
    if t.get("kind") != "conversation":          # memory/output prompts have no language twin
        continue
    folder = t["file"].split("/")[0]             # the bot folder, as the daily suite groups them
    backend = "signals" if (t.get("signals") or "signals" in t["file"].lower()) else "legacy"
    fam[(folder, t.get("direction", "?"), backend)].append(t)
for key in sorted(fam):
    ts = fam[key]
    langs = collections.Counter(t.get("language") for t in ts)
    marked = [t["language"] for t in ts if t.get("master")]
    master = marked[0] if marked else fleet.get(ts[0]["file"]) or "?"
    print(f"{' · '.join(key)}  ({len(langs)} lang, master {master}{'' if marked else ' (derived)'})")
    for t in sorted(ts, key=lambda t: t.get("language") or ""):
        print(f"    {t.get('language') or '??':4} {t['id']:22} {t['file']}")
    for lang, n in langs.items():
        if n > 1:
            print(f"    !! {n} targets claim language {lang} in one family: fix raya/agents.json before auditing")
    if len({t.get('agent') for t in ts}) > 1:
        print(f"    !! targets disagree on 'agent': {sorted({t.get('agent') for t in ts})}")
PY
```

It groups by the **bot folder**, not the `agent` field, because the `agent` field is not reliable
(as of 2026-10-14 `kkb-hi-signals-slim` says `KKB` while its Kannada twin says `KKB-Slim`; grouping by
`agent` silently paired the slim Hindi file with the production Kannada file and dropped
`kkb-hi-signals`). Treat any `!!` line as a manifest bug to report before auditing: an audit of a
wrongly built family compares the wrong files and still "passes".

A family with **one** language has nothing to mirror: report "single-language, nothing to sync" and
stop.

### Master language
First hit wins:
1. A target in the family flagged `"master": true` in `raya/agents.json` (a recorded decision).
2. The `master_language` on a `raya/divergences.json` entry for that family.
3. `master_language` in `raya/regression/fleet.json`. Note: `scripts/build_fleet_manifest.py`
   **derives** it (Hindi if the family has Hindi, else the first code alphabetically), so it is a
   default, not a decision; the printer marks it `(derived)`.
4. The root `CLAUDE.md` sync rule ("the Hindi file is the source of truth") for the Blue Dots bots.
5. Otherwise, for a newly onboarded project: **ask the owner**, then have `/register-bot` record it
   as `"master": true`. Never guess, and never treat the largest file as the master.

If 1 and 3 disagree, say so in the report: the daily suite resolves the master its own way (Hindi
first) and will audit the wrong direction for that family.

The master is the baseline for every comparison. Mirrors are compared **against the master**, never
against each other: that keeps the work O(N) and stops two mirrors from ratifying a shared mistake.

---

## 2. What must match, what must differ

This is the false-positive firewall. With two languages a spurious flag is noise; with eight it drowns
the signal and the reader stops reading the audit.

| Content | Across languages | Flag when it differs? |
|---|---|---|
| **AGNOSTIC**: call flow, step structure, conditions and routing, input-variable names, tool names, JSON payloads and field names, fixed params, enum literals, prohibited-behaviour rules, safety and dignity checks, section skeleton | byte-identical | **YES: drift** |
| **MIXED, the rule half**: the English instruction wrapping a spoken line | byte-identical | **YES: drift** |
| **MIXED, the spoken half**: the quoted line inside the rule | re-authored per language | **NO** |
| **SPECIFIC**: spoken lines, greetings, examples, number/money/time words, script rules, everyday-word table, gender rule, insulting-word list, tone markers, adapted banned phrases, place and person names | different by design | **NO, never for merely differing** |

**Never flag a mirror because:**
- its spoken lines are in a different script or idiom (that is the point);
- its numbers are spelled as different words (`ಹದಿನೆಂಟು ಸಾವಿರ` vs `अठारह हज़ार`);
- its examples use different place or person names;
- its banned-phrase list, gender rule or everyday-word table is its own;
- a section is longer or shorter, or wraps differently;
- **the file has more or fewer heading lines**: count parity is not content parity.

**Always flag when:**
- a heading exists on one side only, or the order differs;
- an AGNOSTIC rule, condition, gate or ordering exists on one side only;
- a `${variable}`, tool name, payload field, fixed param or enum literal appears on one side only, or
  has been translated or transliterated (always a bug, never a localisation);
- rule prose is written in the target language instead of English (a bug of its own: report it, do not
  propagate it);
- an English rule in the mirror still tells the bot to speak the master's language (D117);
- the memory-injection block is missing or altered in any language (Pass 4);
- a required spoken element the master has (a fallback line, a TTS category, an example for a new
  branch) has **no counterpart** in the mirror: a **spoken-content gap**, reported separately because
  the fix is re-authoring, not copying.

---

## 3. The five comparison passes

Run all five for each mirror, master against mirror. Passes 1, 3 and 4 are mechanical: do them first;
they tell you where to read in passes 2 and 5.

**Start with the mechanical rows of `language_checks.py`** (one command covers parts of passes 3 and
4 and the D117 check):

```bash
python3 scripts/language_checks.py "$M" "$X" --lang <mirror-iso> --src <master-iso>
```

| Its row | Use in this audit |
|---|---|
| Payload fields untranslated | Pass 3: variables, backticked code values, JSON keys, payload blocks. FAIL = drift or a localised token |
| Instructions name this language | D117: a copied rule still naming the master language. FAIL = drift |
| Hangup token | `Goodbye` count differs: a closing branch is missing on one side |
| Spoken lines all present | FAIL = spoken-content gap (lines dropped) |
| Structure | coarse (heading **count** and the `${contact_memory}` token only): Pass 1 and Pass 4 below are authoritative |
| All snippets translated, Questions, Digits, Substitution table, Insulting words, Gender rules, Terms | **language quality, not drift.** Report them as a count with a pointer; older pairs that predate these checks (Oct 2026) fail some by design. Route fixes to `/update-prompt` |

It exits 1 on any FAIL, including the quality rows, so read the rows; do not treat the exit code as a
sync verdict. It truncates each list to four items: use the greps below for the full sets.

### Pass 1: skeleton (heading sets and order)
```bash
M="<master file>"; X="<mirror file>"
diff <(grep -E '^#{1,4} ' "$M") <(grep -E '^#{1,4} ' "$X")
```
Headings are English in every language file, so this diff is meaningful across scripts. Lines only in
the master = **sections missing from the mirror**; lines only in the mirror = mirror-only content
(drift the other way, or a registered divergence). Order matters: step order is AGNOSTIC.

**One expected false positive:** a heading that names its own script or language differs by design
(`## English-origin words are allowed only in Devanagari transliteration` vs `... only in Kannada
transliteration`). Match headings by intent, and never "reconcile" a script name.

Pass 1 does **not** surface a divergence that lives in section bodies (the registered ಮಾಯಾ / Maya
persona divergence changes no headings), so the registry is consulted at section-body level in
passes 2 and 3.

### Pass 2: taxonomy walk (section by section)
For each heading on both sides, look up its tag in `prompt-anatomy.md` and apply § 2. For MIXED
sections compare only the English rule prose; ignore the quoted spoken text. Record per section: tag,
status, which side is ahead, what the laggard is missing.

### Pass 3: token census
Every machine-readable token must be identical in every language. This pass finds most real drift
without reading prose.

```bash
# input variables (broad form: camelCase names such as ${phoneNumber} exist)
diff <(grep -oE '\$\{[A-Za-z0-9_]+\}' "$M" | sort -u) <(grep -oE '\$\{[A-Za-z0-9_]+\}' "$X" | sort -u)

# backticked tool names, field names, fixed params, enums (snake, camel, SCREAMING, dotted)
diff <(grep -oE '`[A-Za-z_][A-Za-z0-9_.]{1,60}`' "$M" | sort -u) \
     <(grep -oE '`[A-Za-z_][A-Za-z0-9_.]{1,60}`' "$X" | sort -u)

# quoted English enum / fixed-value literals (noisy: read it scoped to tool and payload sections)
diff <(grep -oE '"[A-Za-z][A-Za-z0-9 ./&+-]{2,40}"' "$M" | sort -u) \
     <(grep -oE '"[A-Za-z][A-Za-z0-9 ./&+-]{2,40}"' "$X" | sort -u)
```
A token on one side only is drift **or** a localisation bug. A Title-case backticked token is usually a
place or person name (localised on purpose) and an 8-hex token a call id cited in a note: ignore those.
A missing backend enum (`"ITI / Other Vocational Trainings"`, `"3-5 Years"`) is critical: an inexact
enum makes the write fail.

### Pass 4: standing-rule presence
Confirm every repo-wide mandatory block is in **each** language. The memory-injection block must be the
**exact three lines** (bug E3); checking only `{${contact_memory}}` passes a mirror whose heading or
lead line was translated:
```bash
python3 - "<file1>" "<file2>" ... <<'PY'
import io, sys
BLOCK = "### Contact context\nHere is the caller context:\n{${contact_memory}}"
for p in sys.argv[1:]:
    t = io.open(p, encoding="utf-8").read()
    state = ("VERBATIM OK" if BLOCK in t
             else "PRESENT BUT ALTERED" if "${contact_memory}" in t
             else "MISSING")
    print("%-58s memory-block: %s" % (p, state))
PY
```
`PRESENT BUT ALTERED` and `MISSING` are both bugs, fixed by restoring the exact English block, never by
translating it. Same treatment for any section the bot's use case requires per
`../../prompt-analyser/reference/section-checklists.md` (safety interrupt, graceful exit, consent
gate).

### Pass 5: changelog corroboration
Read `<Bot>/CHANGELOG.md` newest first. For each entry, check which language files carry its content.
An entry present in the master and 3 of 7 mirrors names the languages that were never updated, and
the date the drift started. An entry that **declares** a divergence with no `raya/divergences.json`
record is a registry gap.

---

## 4. Report shape

With N languages a prose diff does not scale: lead with the matrix, then detail only for rows that are
not clean. The verdict words below are labels for the record and for `/update-prompt`; to a person,
say the same thing in plain words first (SKILL.md → step 8).

### Headline (one line)
```
KKB · outbound · signals: master hi · 8 languages: 5 CURRENT, 2 LAGS, 1 UNCERTAIN · 3 differences matched registered divergences
```

### Table 1: per-language status (one row per mirror; the master is the baseline)

| Language | In sync? | Missing AGNOSTIC content | Spoken-content gaps | Registered divergences | Verdict |
|---|---|---|---|---|---|
| kn (`kkb-kn-signals`) | ✗ | Step 3.5 conditional-qualification block; `otherHelpNeeded` payload field | none | 1 (`kkb-kn-signals-maya-name`) | **LAGS (2)** |
| te (`kkb-te-signals`) | ✓ | none | TTS number words missing for lakh/crore | 0 | **CURRENT (spoken gap)** |
| mr (`kkb-mr-signals`) | ? | intro-turn rule differs: deliberate or drift? | none | 0 | **UNCERTAIN** |
| bn (none) | | file not created | | 0 | **MISSING** |

Verdict vocabulary (use these words exactly, so reports are greppable):
- **CURRENT**: no AGNOSTIC drift. Add `(spoken gap)` if re-authoring is owed.
- **LAGS (n)**: n AGNOSTIC drift items; the master is ahead. The actionable state.
- **AHEAD**: the mirror has AGNOSTIC content the master lacks. Escalate to the master via
  `/update-prompt`, then fan out; never mirror to mirror.
- **DIVERGED (registered)**: every difference found is covered by the registry. Not drift.
- **UNCERTAIN**: a difference that could be deliberate. Ask; do not guess.
- **MISSING**: no file for this language yet (a `/translate-prompt` job, not a sync job).

### Table 2: drift detail (only rows that are not CURRENT)

| Language | Section | Tag | Status | Ahead | Missing from laggard |
|---|---|---|---|---|---|
| kn | Step 3.5, Phase 1 | MIXED | **AGNOSTIC DRIFT** | master (hi) | conditional-qualification follow-up rule |
| kn | Introduction / intro-turn rules | MIXED | EXPECTED (registered `kkb-kn-signals-maya-name`) | | |
| te | TTS Normalization Rules | SPECIFIC | spoken gap | master (hi) | lakh/crore number words |

Then, per laggard: the proposed reconciliation (copy verbatim vs re-author) and the snapshot label you
will take before writing.

---

## 5. Registry — `raya/divergences.json`

### Why this location
It sits next to `raya/agents.json` because it is **fleet data**, not skill prose: `/sync-check`,
`/update-prompt`, `/port-feature` and the daily suite need to load it, it must be git-tracked and
reviewable in a diff, and a Python check must read it without parsing markdown. The file carries its
own field notes under `_schema`.

### Schema
Top level: `schema_version`, `_note`, `_schema`, `divergences: []`. Each entry:

| Field | Required | Meaning |
|---|---|---|
| `id` | yes | stable kebab-case key, cited verbatim in audit reports |
| `bot` | yes | the bot the divergence belongs to (e.g. `KKB`) |
| `sync_family` | yes | `bot · direction · variant`: scopes the entry to one family |
| `targets` | yes | `raya/agents.json` target ids it applies to |
| `files` | no | the prompt files, for a human reader |
| `master_language` | yes | the family's master at the time of approval |
| `languages_affected` | yes | the language codes that legitimately differ |
| `direction` | yes | `mirror-only`, `master-only` or `both-differ` |
| `scope[]` | yes | the sections or lines that differ: `section` (heading, matched by intent), `kind` (`persona` / `spoken-line` / `rule`), `what` (plain English), `contains[]` (tokens a script can match in the actual delta) |
| `why` | yes | the owner's reason, in plain English |
| `approved_by` | yes | who decided, and how ("explicit instruction", "email approval") |
| `approved_on` | yes | `YYYY-MM-DD` |
| `changelog_ref` | yes | the `CHANGELOG.md` entry that records the edit |
| `still_must_match` | yes | everything the entry does **not** excuse, audited normally |
| `not_applied_to` | no | sibling targets deliberately left alone (stops scope creep) |
| `review_on` | no | after this date the entry must be re-confirmed; past due = registry gap |
| `expires` | no | hard expiry; after it the divergence is drift again |

### Matching rule
A difference is **EXPECTED (registered divergence)** only if **all** hold:
1. the file's target id is in `targets` (and its family matches `sync_family`);
2. the file's language is in `languages_affected`;
3. the differing section matches a `scope[].section` (by intent, not exact string);
4. the actual delta contains at least one of that scope item's `contains` tokens.

Anything else is **UNREGISTERED** and is flagged. An entry is a narrow carve-out, never "this language
may differ".

### Staleness
If an entry's `contains` tokens are **no longer present** in the files it covers, the divergence was
undone (probably by a naive sync). Report a **registry gap / possible silent revert** and ask the
owner: do not delete the entry and do not silently re-apply it. Same for a `review_on` date that has
passed.

### Who writes entries
`/update-prompt`, `/port-feature` and `/translate-prompt`, in the same change as the prompt edit and
the changelog entry, whenever they knowingly leave some languages of a family different. `/sync-check`
only **reads** the registry, except when the owner confirms, during a reconciliation, that a difference
should stay: then the entry is added in that same `/update-prompt` change.
