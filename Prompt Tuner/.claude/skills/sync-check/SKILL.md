---
name: sync-check
description: Check that every language version of a bot says and does the same thing. Compares the master language against each other language the bot speaks (read from raya/agents.json), finds rules, steps, tool calls or variables that reached some languages and not others, separates real gaps from the differences a language is meant to have and from owner-approved ones (raya/divergences.json), checks the bots' tool schemas match too, and hands any laggard to /update-prompt to bring it up. Use when the user asks "are the languages in sync", "is the Kannada version behind the Hindi one", "which language is behind", "did that fix land in every language", "compare the Marathi and Hindi prompts", "check language parity", before making a prompt change, or after a bot is taken into a new language. Runs automatically as the first step of /update-prompt and from /translate-prompt.
---

# Sync Check

**What it produces:** for one bot (or all), a per-language report: for each language other than the
master, whether it is **current**, **behind** (and exactly which rules or steps it is missing),
**ahead**, or **uncertain**; differences the owner approved, recorded in `raya/divergences.json`, are
shown as expected rather than flagged. It also reports tool-schema differences between sibling bots.

**Read-only by default.** It never edits a prompt itself: bringing a laggard up is a prompt change and
goes through `/update-prompt` (root `CLAUDE.md`: the only sanctioned write paths are `/update-prompt`,
`/port-feature`, `/translate-prompt` and `/register-bot`).

**Drift** is a language-agnostic rule, step, condition, variable, tool or payload that differs because
a change landed in some languages and not others. Different script, spoken lines, number words, place
names, gender rule or everyday-word table are **not** drift: differing is their correct state.

## Fast path

```bash
cd "/Users/parthbansal/EkStep/Prompt Tuner"
# 1. families, languages and masters (script in reference/n-language-parity.md § 1)
# 2. is any live agent ahead of the repo? (every target in the family)
python3 scripts/raya_deploy.py diff <target>
# 3. per mirror: mechanical rows, then heading set, token census, memory block (reference § 3)
python3 scripts/language_checks.py "<master>" "<mirror>" --lang <mirror-iso> --src <master-iso>
# 4. tool schemas across the bots of the family (read-only GETs)
python3 scripts/toolschema_parity.py --family <agent>
```

Then read the registry, walk the sections the mechanical passes pointed at, and report (step 8).

## The model: one master, N mirrors

- The **master** language is the source of truth; a change is made there first.
- Every other language is a **mirror**, compared **against the master**, never against another
  mirror.
- The language set is **discovered** from `raya/agents.json` (each target's `language` code), never
  enumerated here. Never infer a file's language from its name (`KKB Placeholder Inbound.md` is
  Hindi).
- A family with one language has nothing to mirror: say "single-language, nothing to sync" and stop.

## Inputs

- A bot (`KKB`, `DKB`, `Maya`, `TRRAIN`, a Purple Dots bot, ...), a project, or `all` (the default).
- Optionally a subset of mirror languages (`kn,te,ta`).

## Reference

- `reference/n-language-parity.md`: resolving families and the master (with the printer script), what
  must match and what must differ, the five passes with their commands, the report tables, and the
  registry schema.
- `../update-prompt/reference/prompt-anatomy.md`: the AGNOSTIC / SPECIFIC / MIXED tags. Drift is only
  possible in AGNOSTIC content and the rule half of MIXED sections.
- `raya/divergences.json`: the deliberate-divergence registry.

## Procedure

1. **Resolve the families and their masters.** Run the printer in `reference/n-language-parity.md`
   § 1. A family is one bot folder, one direction, one backend; a `<Bot>-Slim/` twin is its own family.
   Any `!!` line (two targets claiming one language, targets disagreeing on `agent`) is a manifest bug:
   report it before auditing, because an audit of the wrong pair still "passes".
2. **Reconcile with live, every target.** Any language can be ahead in production (the team edits the
   Raya console). Run `python3 scripts/raya_deploy.py diff <target>` for the master and every mirror. If
   live is ahead, adopt it first (`raya_deploy.py pull <target>`, or `/raya-reconcile` when GET is
   flaky) so the audit compares what is really live.
3. **Mechanical passes, per mirror.** Run `language_checks.py` and use only the rows that bear on sync
   (reference § 3 table): payload fields, instructions naming this language, hangup token, spoken lines
   present. Its other rows (questions, digits, everyday-word table, insulting words, gender rule) are
   language quality, not drift: count them and point to `/update-prompt`. Its exit code is not a sync
   verdict. Then the exact heading-set diff (Pass 1), the full token census (Pass 3) and the verbatim
   memory block (Pass 4).
4. **Walk the sections** the mechanical passes pointed at (Pass 2). AGNOSTIC: byte-identical, except a
   heading or rule that names its own script or language. MIXED: compare the English rule prose only.
   SPECIFIC: flag only a missing section, a missing structural sub-point (a new TTS category), or a
   **spoken-content gap** (a line the master has with no counterpart in the mirror).
5. **Consult `raya/divergences.json`** for every difference found. Covered (target, language, section
   and a `contains` token all match) means **EXPECTED (registered divergence)**, cited by `id`, and
   never proposed for "fixing". An entry whose tokens are gone from the files, or whose `review_on`
   date has passed, is a **registry gap**.
6. **Corroborate with the changelog** (Pass 5): an entry whose content is in only some languages names
   the languages it never reached and when. A declared divergence with no registry entry is a registry
   gap.
7. **Check the tool schemas.** A prompt and its tool schemas are one contract: on 2026-09-03 the
   `duplicate_check` parameter existed on 1 of 12 bots, so 11 prompts asked the model to send a
   parameter their tool did not define, while the prompt texts were in perfect sync. Run
   `python3 scripts/toolschema_parity.py --family <agent>` (it groups by agent and backend, since
   Signals and legacy differ by design, and exits 1 on a parameter, `required` or enum difference;
   description drift is info). Fix a finding with `scripts/raya_toolparam.py` or
   `scripts/raya_tooldesc.py` (both read back; a description is capped at 1024 characters).
8. **Report.** First, in plain words, one line per language: *"Kannada is missing two rules the Hindi
   version has: the follow-up question about qualifications, and the extra field sent when applying.
   Telugu matches. Marathi has one difference we cannot tell is deliberate: should it stay?"* Do not use
   the words agnostic, mirror, sync family, divergence registry or payload to someone who did not use
   them first (root `CLAUDE.md`). Then the headline line and the two tables from reference § 4 (verdict
   words CURRENT / LAGS (n) / AHEAD / DIVERGED (registered) / UNCERTAIN / MISSING), tool-schema
   findings, manifest or registry gaps, and the language-quality count. End with what is still open
   from earlier audits.
9. **Offer to reconcile; never write without a yes** (unless `/update-prompt` called this skill and
   already holds the go-ahead). Reconciling is an `/update-prompt` change, one laggard language at a
   time, carrying all of its obligations: reconcile with live, snapshot (`scripts/prompt-version.sh
   save <Bot> pre-sync-<slug> "<why>"`), surgical edit, `CHANGELOG.md` entry naming the languages,
   deploy through `scripts/raya_deploy.py`, and a live call per language. What sync adds:
   - copy AGNOSTIC content verbatim from the master; for the rule half of a MIXED section, insert the
     rule and re-author its spoken line to the `/translate-prompt` standard (the language's everyday
     words from `raya/translations/lexicon.json`, its own gender rule, numbers as words, pinned names);
   - **the master always leads.** A mirror that is AHEAD goes to the master first via `/update-prompt`,
     then fans out;
   - if the owner decides a difference should **stay**, add the `raya/divergences.json` entry in that
     same change, or the next audit will "fix" it;
   - re-run `language_checks.py` on each reconciled mirror; a FAIL the edit introduced blocks deploy.

## When invoked from /update-prompt or /translate-prompt

Run steps 1-8 and report the matrix briefly, then:
- **No drift:** say so; the caller proceeds.
- **Drift:** the caller reconciles every laggard first, so its change lands on an aligned base in every
  language; show what was aligned, per language.
- **The caller's change is itself deliberately single-language:** tell it to register the divergence.
- **From `/translate-prompt`:** the new language must come out clean (or with registered differences
  only) before it is deployed.

## The daily suite and this skill

`raya/regression/static_regression.py` (Tier 3) now reads every conversation target and language from
`raya/agents.json` and compares the master against every mirror (`sync_parity()`), but only by **heading
count** (`^#{1,2} ` lines, a gap over 2 is flagged), resolves the master as Hindi-first, and does not
read `raya/divergences.json`. So a clean daily report does not mean the languages are in sync. Still to
build (spec, not for this skill to edit): compare heading **sets** and the token census instead of
counts, honour `"master": true` before Hindi, and suppress registered divergences.

## Done means tested

A reconciliation is a prompt change: it is done only when each reconciled language has been deployed
and then proven by its own live call (a call made before the deploy grades the old prompt). Follow
`/update-prompt`'s testing: Tier 1, the scenario the copied rule governs, per language, with a call
id; Tier 2, the whole flow in that language and the mirror's own spoken lines undamaged; Tier 3, the
daily suite. **Never extrapolate:** a byte-identical copy can still behave differently in another
language, so N reconciled languages need N proving calls, per direction. Inbound bots are testable
(`/voice-test` → Inbound bots: an integer `out_did` on the inbound agent, the test profile on the tester's
number). Without a call, the only words are **DEPLOYED, NOT VERIFIED**. Revert on any regression
(`/prompt-version`).

## Guardrails

- **Never "fix" an expected difference** by making a mirror match the master's script, spoken lines,
  number words, names, gender rule or word lists. Never translate a `${variable}`, tool name, payload
  field or fixed param, and never "reconcile" one by translating it.
- **Never propose reconciling a registered divergence.** If you think one is wrong, say so and ask the
  owner.
- **Rule prose in a non-English language is a bug** in its own right: report it and route it to
  `/update-prompt`; never mirror it to other languages.
- **Reconcile before a new change, not during it,** one language at a time: a new change on top of
  half-aligned files is how a family goes three ways.
- **Unsure whether a difference is deliberate?** Mark it UNCERTAIN and ask. With N languages one wrong
  guess fans out N times.
- Never commit or push as part of an audit.
