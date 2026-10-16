---
name: prompt-analyser
description: Read-only check of a voice bot's conversation prompt, in any language and any project, for the problems that break live calls, BEFORE they reach a caller. Finds missing parts the prompt needs (consent, safety interrupt, closing, per-language speech rules), and the failure patterns learned from past bugs - skipped steps, lines repeated, tools not called or called with wrong values, examples that teach the wrong thing, words callers will not understand, Hindi left in a translation, a prompt too big for its bot. Flags and explains; does not fix. Use when the user says "check this prompt before we go live", "what could go wrong with this prompt", "find the gaps", "audit / review the prompt", "is the Marathi (or any) translation OK", "is this prompt too big", when a new bot is registered, before translating a master, or as a review before /update-prompt.
---

# Prompt Analyser

**What it produces:** one report a non-specialist can read. First, in plain words, the problems a caller
could run into, most serious first, each with what to do next; then the technical detail (section,
line, pattern id, fix direction) for whoever makes the fix. It **flags**; it never edits a prompt.

**Fast path:**
1. Resolve the file and its target (path map in root `CLAUDE.md`, `raya/agents.json`). Is it a master
   or a mirror?
2. Run the mechanical checks: size, and the language checks if it is a mirror.
3. List the prompt's sections against `reference/section-checklists.md`.
4. Sweep `reference/bug-patterns.md` family by family, using its **Index**.
5. Check the prompt's examples against its rules.
6. Write the report.

## Inputs

- The prompt: a file path (resolve any bot through the path map and `raya/agents.json`, never a
  hard-coded bot list) or pasted text. One language file per run. For a mirror (non-master language),
  also load its master: several checks compare the two.
- Optional: reported live symptoms. Root-cause each against the prompt first, then do the full sweep.
- Optional: what kind of bot it is (outbound data collection, job matching, employer capture, campus
  recruitment, ...). If not given, infer it and say what you inferred.

## References

- `reference/bug-patterns.md`: every failure class learned from past bugs (symptom → root cause →
  **detection heuristic** → fix direction → where it was seen). Over 3,000 lines: **start from the Index
  at its top**, never by reading it end to end.
- `reference/section-checklists.md`: what a prompt of each kind must contain (Part 1), and the rule
  checklist for every prompt, including size, safety, access needs and per-language rules (Part 2).
  A missing critical section is a high finding.
- `../update-prompt/reference/prompt-anatomy.md`: section names and which content is agnostic
  (copied exactly across languages) vs specific (spoken, re-authored per language).
- Root `CLAUDE.md`: the standing rules (memory block, sync rule, Maya divergences, instructions always
  in English).
- `raya/divergences.json`: deliberate language differences. A registered divergence is not a finding.
- The bot's `CHANGELOG.md`: what has actually broken before.

## Procedure

1. **Mechanical checks** (fast, objective; run them before reading):
   - **Size (every file with a target):** `python3 scripts/prompt_size.py check <file> --target <id>`.
     BLOCK is a high finding (past the size where this bot already stopped calling tools, D116). WARN
     means no call has proven this size works: say the first test call must confirm every tool fires.
     For a master about to be translated: `python3 scripts/prompt_size.py project <master> --lang <iso>
     --target <id>`.
   - **Languages (every mirror):** `python3 scripts/language_checks.py <master> <mirror> --lang <iso>
     [--target <id>] [--config raya/translations/<bot>-checks.json]`. Each FAIL is a high finding, each
     WARN medium or "please confirm". Its word lists are seeds awaiting a native speaker; say so once.
   - **Tool schemas (optional, when payloads or enums are in scope):**
     `python3 scripts/toolschema_parity.py --family <Agent>` reads the live tool schemas (read-only)
     and flags a bot whose parameters, required fields or enums differ from its family (D111).
2. **Kind of bot and section inventory.** State the archetype you matched, list the prompt's section
   headings, and compare them with the matching checklist (match by intent, not heading text). A public
   bot with no safety interrupt (D121), or a mirror with no per-language speech rules (D117, D120,
   D123), is a missing critical section.
3. **Reported symptoms first, if any.** Find the exact lines that produce the behaviour and name the
   failure class. Do not stop at the surface rule: check whether an example, a competing action or skip
   logic overrides it.
4. **Sweep the bug patterns, family by family, from the Index:**
   - For each family, decide from the one-line names whether the prompt has the surface it needs (no
     consent step, no tools, a master file). Mark whole families N/A in one line, with the reason.
   - For every entry that could apply, open it (`grep -n "^#\+ D95\b" reference/bug-patterns.md`, read
     to the next heading) and apply its **Detection heuristic** as written. Do not work from memory of
     the entry.
   - Always apply, whatever the bot: E1 and D50 (examples against rules), D79 and D82 (rule stated far
     from where it is used), D95 (a skip test that accepts a weaker fact), D47 and D115 (failure lines
     that claim something false), D109 and D112 (example values copied into calls), E3 (memory block),
     D116 (size), D121 (safety interrupt).
   - On a long prompt, fan out one agent per family with the prompt path and that family's ids; each
     must quote the line for every hit. Merge the results and report one root cause once, listing every
     pattern id it trips.
5. **Examples against rules.** Sample calls are behaviour the model copies. A mandatory step an example
   skips, a value an example supplies, or a canonical line an example garbles is a real defect, usually
   a stronger cause than any rule (D50).
6. **Report** (format below). No edits.

## Root-cause lenses (apply to every flag)

A rule can be present and still fail. Check why it would not hold:
- **Competing action not forbidden.** The prompt says what to DO but never forbids the rival action,
  so the rival wins (A1). Look for a negative gate.
- **One-time action inside a per-item loop.** A line, consent or tool call that should fire once sits
  inside "for each X" and repeats (B1). Look for an explicit "exactly once".
- **Silent step with no anchor.** A background tool call with no "must run before you continue or
  close" gate gets dropped (C1).
- **Skip pressure without backpressure.** Skip-ahead or "move on silently" logic with no list of steps
  that are never skipped (A2).
- **Abstract instruction where a list is needed.** "Use simple words" or "don't repeat" loses to a
  concrete word list or count (D1, D123).
- **Example overrides prose.** An example models the shortcut the rule forbids (D50).
- **Guard tests the wrong fact.** A skip or "only when" clause is satisfied by a weaker value that is
  usually present (D95).

## Report format

Write the top half in the words of the call, not of the tuner (root `CLAUDE.md` → "Write for someone who
is not a prompt engineer"): no pattern ids, "payload", "agnostic" or "guard" there. Technical terms
belong in the detail table.

```
## Prompt check: <bot, language> (<what kind of bot>)

**In short:** <N> problems a caller could hit, <M> of them serious. <One sentence on the worst one.>

### What a caller could run into (most serious first)
1. **<What happens on the call, e.g. "the bot tells the caller their details were saved when nothing
   was saved">.** Why: <one sentence>. Next: <a sentence the user can type, e.g. "say 'fix the saved
   line on the Marathi bot'">.

### What caused the problems you reported (if any were reported)
- <symptom> → <the line(s) that cause it, in plain words>

### Parts the prompt is missing
- <part> - <what goes wrong on a call without it>

### Checks run
- Size: <OK / WARN / BLOCK, bytes vs the bot's limit>. Language checks: <N FAIL, N WARN, or "master file,
  not run">. Families not applicable: <list, one reason each>.

### Technical detail (for whoever fixes it)
| # | Severity | Section / line | Pattern id(s) | What is wrong | Fix direction |
|---|---|---|---|---|---|

### Not sure, please confirm
- <item>
```
Severity: **high** = wrong behaviour on a call, a broken or missing tool call, a false claim to the
caller, or a missing safety part; **medium** = some calls or quality; **low** = cosmetic or consistency.
High first.

## Guardrails

- **Analysis only.** Never edit the prompt from this skill. Fixes go through `/update-prompt` (or
  `/port-feature`, `/update-memory`, `/update-output`). If the user says "fix these", hand off.
- **Ground every flag in a line.** Quote or cite the section and line; no findings without one.
- **A finding is not yet a bug on a live bot.** For a prompt already running, a finding is fixed only
  after a call shows it (root `CLAUDE.md` → "No fix without a transcript"); hand it to `/voice-test` to
  reproduce, or to `/generate-test-cases` as a test case. For a prompt not yet live (a new bot, a
  master before translation, a slim rewrite), findings go to `/update-prompt` with the user's go-ahead.
- **Real gaps vs expected language differences.** A mirror's spoken line differing from the master's is
  not a bug; registered divergences are not findings. A logic difference between languages is, but
  this skill reviews one file: send parity questions to `/sync-check`.
- **Flag, don't guess.** If you cannot tell whether something is deliberate, put it under "Not sure".

## Growing the skill (this is how it compounds)

Every new class of live bug, found here or through `/update-prompt` or `/bug-fix`, gets an entry in
`reference/bug-patterns.md` (symptom, root cause, detection heuristic, fix direction, source bot and
date) under the next free id (D124 onward; never reuse a number), plus a row in the Index at the top
of that file. If it implies a section a prompt of that kind must always have, update
`reference/section-checklists.md` too. If a script can detect it, say which one in the entry.
