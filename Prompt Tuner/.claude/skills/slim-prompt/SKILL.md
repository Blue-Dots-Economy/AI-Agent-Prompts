---
name: slim-prompt
description: Make a voice-agent conversation prompt shorter without losing any behaviour. Two modes. (1) MANDATORY size trim when a bot is past its size limit and has stopped calling tools, or a translation is projected past it (prompt_size.py says BLOCK, analyser D116): trim the master, never one language, then re-translate and re-check the languages. (2) Optional slim rewrite as a NEW A/B agent, proven by a coverage table, a static audit, N>=3 live calls per branch and a head-to-head against the original before any traffic moves. Use when the user says "the bot stopped calling tools", "the Kannada/Marathi prompt is too big", "prompt_size says BLOCK", "slim this prompt", "compress the prompt", "make the prompt shorter", "the prompt is too long", "reduce prompt size", "reduce latency by shrinking the prompt", "get the prompt under 50k", or "do for <bot> what we did for KKB Slim".
---

# Slim Prompt: a shorter prompt that still does everything the long one did

**Produces** either (1) a trimmed master plus re-translated, re-checked languages, each with a live
call proving its tools fire, or (2) a separate `<Bot>-Slim` A/B variant on its own agent, with a
coverage table, a static audit, an A/B report and an owner decision.

Read `<bot>` as the source bot and `<lang>` as any language it speaks. Resolve files through the
root `CLAUDE.md` path map and targets through `raya/agents.json` (languages from its `language`
codes); never hard-code a bot list or a language pair.

## Decide first

| Situation | What to do |
|---|---|
| `scripts/prompt_size.py` says **BLOCK** for a target, or a call has turns but **zero tool calls** on a path that needs one, with no tool error or backend cause (D116) | **Mode 1, size trim. Mandatory.** |
| A new language is projected past the bot's limit (`prompt_size.py project` BLOCK) | Mode 1 on the master, then `/translate-prompt` starts again |
| Goal is latency, cost, reviewability or a char target the team set | Mode 2, slim rewrite, only after the payoff check below |
| A behaviour bug (competing instruction, rule far from the line that uses it) | Not this skill: `/update-prompt`. Slimming does not fix mechanism bugs |

Size limits are per bot, in **bytes** (every Indic character is three bytes), and they are a zone,
not a line (Purple Dots Kannada: 0 of 3 calls used tools at ~125 KB, 1 of 2 at ~112 KB, 3 of 3 at
105.6 KB; KKB prompts run at 270 KB and still call tools). They live on each target in
`raya/agents.json`: `max_prompt_bytes` (seen failing), `proven_prompt_bytes` (seen working),
`size_evidence` (call ids, date). `raya_deploy.py` refuses at or past `max_prompt_bytes`.

```bash
cd "/Users/parthbansal/EkStep/Prompt Tuner"
python3 scripts/prompt_size.py check "<file>" --target <id>                          # finished file
python3 scripts/prompt_size.py project "<master>" --lang <iso> --target <id>          # before translating
python3 scripts/prompt_size.py ratios                                                # measured language ratios
```

**Mode 2 payoff check: be honest.** The only measured result is small. KKB Hindi Signals went from
219,518 to 68,744 chars (-69%) and bought about 7% per agent turn (16.00 vs 14.75 s median), and both
prompts failed the same classes at similar rates (`7d164b9`, `raya/slim/README.md`). The latency
cause at the time was unrelated to size: `hold_message` never played, so 348 of 348 tool calls sat in
silence. Before a Mode 2 rewrite, write down and get the owner's yes on:

- [ ] **The goal.** For latency, first rule out non-prompt causes (silent tool round-trips, platform
      settings, ASR timeouts). Expect single-digit percent from size alone.
- [ ] **The realistic floor** (from the composition measure, step B2). KKB's floor with behaviour
      intact was ~68k chars; the team's 50k target was reachable only by deleting the worked calls,
      the ASR section, the Situations and the canonical spellings together (still 56,657). Below the
      floor you are cutting behaviour: give the owner a menu, never cut silently.
- [ ] **A new A/B agent** will be created, and traffic moves only through the gate in step B11.

What slimming genuinely bought on KKB: 14 numbered steps in call order instead of 148 sections, one
`# No-Match Fallback` instead of a duplicated 23,723-char copy, and a safe experiment bed (the
ordinal-counter removal was proven there first: `0ab57b0`, `eadf269`). Claim those, not a quality gain.

---

## Never-drop list (both modes)

A shorter prompt that loses one of these is a regression, whatever its size.

- [ ] **Every tool contract**: name, when it fires, every payload field, fixed params
      (`sourceService`, `app_instance`, `languageSpoken`), enum values, how its result is read
      (which item, which field, live vs draft), and every failure-row line.
- [ ] **Every consent, disclosure and safety rule**: data-sharing line before apply, consent gates,
      AI/recording disclosures and every early exit that must still carry them (D103), dignity
      checks, do-not-call, proxy caller, distress handling, the safety interrupt (D121).
- [ ] **Every mandated spoken line**, verbatim, and every **named ban** whose exact wording is the
      failure (KKB kept "पक्का call आएगा" quoted, because a paraphrased ban does not stick).
- [ ] **Every input variable** (`${...}`), unrenamed, and the memory block byte for byte
      (`### Contact context` / `Here is the caller context:` / `{${contact_memory}}`).
- [ ] **TTS / script machinery**: number-to-word rules, canonical place spellings, slash and
      abbreviation handling, the `[slot]` marker rule (D77), the `*( )*` note rule.
- [ ] **Every branch of every multi-branch step**, including the rare ones (ask-the-pin when none is
      held, empty fetch, no-match, second consecutive failure).
- [ ] **Every pre-close owed item** (services offer, need capture, read-back), each named in the exit
      checklist (D96).

**May drop:** provenance prose (call ids, "this used to say", dates inside rules), exact duplicate
paragraphs, a second copy of a section, extra wordings of one rule, sample dialogues beyond one per
branch, quotes of past bugs (they live in `CHANGELOG.md` and `bug-patterns.md`), padding caller lines.

---

## Mode 1: size trim (mandatory when the bot is past its limit)

1. **Confirm it is size.** A `prompt_size.py` BLOCK, or a call id with turns and zero tool calls on a
   tool path, and no tool error or backend failure in that call. Record a failing size on the target
   as `max_prompt_bytes` + `size_evidence`.
2. **Reconcile and snapshot** the master and every mirror (step B0 commands).
3. **Trim the master through `/update-prompt`**, since this edits an existing prompt. What worked on
   Purple Dots: delete examples that repeat a rule stated elsewhere, and tighten wording without
   touching any rule. Never-drop list applies. Never trim one language on its own: the languages would
   stop matching.
4. **Prove nothing was lost** before any call: `compare_spec.py` from the pre-trim snapshot to the
   trimmed master (step B7), every dropped line classified, zero new spoken lines.
5. **Re-project every language** with `prompt_size.py project ... --target <that language's target>`
   until each is OK or WARN. Aim for the everyday-speech estimate, not the literal one.
6. **Bring the languages back**:
   - a language that failed on size, or does not exist yet: re-translate from the trimmed master with
     `/translate-prompt` (`scripts/speech_split.py extract` / `apply`, which sends only spoken lines to
     translators and proves every other line identical; its step 0 is already done);
   - a working mirror below its limit: `/update-prompt` mirrors the same cuts.
   - Either way: `python3 scripts/language_checks.py "<master>" "<mirror>" --lang <iso> --src <master-iso> --target <id>`
     (exit 0), `prompt_size.py check`, and `/sync-check` across all languages.
7. **Deploy and test each language on its own** (`/voice-test`). The first call on each target must
   show every tool firing. Record `proven_prompt_bytes` + `size_evidence` (call id, date) on that
   target. One passing call near the edge proves little; untested targets are DEPLOYED, NOT VERIFIED.
8. **Changelog** in the bot's `CHANGELOG.md`: bytes before and after per language, what was cut, call
   ids. Report in the short format at the end.

---

## Mode 2: slim rewrite on its own A/B agent

Codifies the KKB Hindi Signals rewrite (`9afc12a`, bot `140d13ca`, `KKB-Slim/CHANGELOG.md`,
`raya/slim/README.md`). The source prompt is never edited by this mode.

### B0. Reconcile and snapshot

```bash
python3 scripts/raya_deploy.py diff <source-target>     # is live ahead? (or /raya-reconcile)
python3 scripts/raya_deploy.py pull <source-target>     # only if live is ahead; commit before going on
scripts/prompt-version.sh save <Bot> pre-slim "baseline before slim rewrite"
```

Never slim a file that is behind live: the variant would bake in a stale inventory or rule.

### B1. Real-traffic latency baseline

Score the source bot's recent real calls with the scorer you will use for the A/B, so the number to
beat is known first (KKB: median 13.4 s per agent turn over 7 measurable calls).

`raya/slim/ab_compare.py` is **KKB Hindi Signals only**: the fat and slim agent uuids (lines 44-45),
the tester, the Devanagari and audio-check patterns and its invariants are hard-coded. For KKB Hindi:
`python3 raya/slim/ab_compare.py --score-only`. For any other bot or language it would score the
wrong agents: compute seconds per agent turn (call_duration / agent turns, with turn counts) from
`python3 scripts/raya_call.py <uuid> <n>` by hand, or ask to have the script parameterised first.

### B2. Measure the composition

Count, do not guess; report chars and percent of the file for provenance prose, exact duplicate
paragraphs, duplicated sections, paragraphs over 400 chars (KKB: 37% of the file in 128 of them),
and sample conversations.

```bash
grep -n '^#' "<source>" | sort -k2 | uniq -f1 -d      # repeated headings
python3 -c "import sys,collections;p=[x.strip() for x in open(sys.argv[1],encoding='utf-8').read().split('\n\n') if x.strip()];c=collections.Counter(p);d=sum(len(k)*(v-1) for k,v in c.items() if v>1);t=sum(map(len,p));print('dup chars',d,'of',t,round(100*d/t,1),'%');print('long paras',sum(1 for x in p if len(x)>400))" "<source>"
```

State the expected size and the floor in the plan you show the owner.

### B3. Extract the contract

```bash
python3 raya/slim/extract_spec.py "<source>" -o raya/slim/<target>/spec-source.json
```

Its tool list is a hard-coded regex that predates newer tools (`record_consent`, `get_services`,
`get_recommended_jobs`). List the agent's real tools from the live agent and add any it missed to the
coverage table by hand. An empty tool diff proves nothing until you have done that.

### B4. Coverage table first; nothing is written until it exists

One row per contractual item, saved as `raya/slim/<target>/coverage.md`:

| id | item | kind | source location(s) | times stated | points of use | decision | slim location | why |
|---|---|---|---|---|---|---|---|---|
| R-012 | never invent a job | guard | L98, L141, L520 | 17 | batch template, deep dive, no-match | MERGE + pointers | law 1; 6b; 7 | one statement, a pointer at each composition site |
| T-apply | `apply_job` payload | tool contract | L1673-1783 | 1 | step 10 | KEEP | Tools / apply_job | never dropped |

`kind`: tool contract, input variable, spoken line, named ban, branch, guard/rule, owed item,
TTS/script rule, situation, worked example, provenance.

- **KEEP** every never-drop item, unless the owner says otherwise in writing.
- **MERGE** a rule stated N times into one statement **at its point of use**, plus a one-line pointer
  at every other site where the governed text is composed. Record times stated before and after.
  Consolidating "never invent a job" from 17 statements to 3 at the top of the file made the slim bot
  invent jobs (`45e2cb3b`, `a4f378b9`; fat clean 5/5).
- **DROP** only provenance, duplicates and surplus samples; each DROP row says where the content
  still lives or why it is dead.
- A ban quoting a template with a slot is also a ready-made sentence (`69155e23` spoke one verbatim).
  Keep the ban as a class; quote the exact string only when the exact string is the failure.
- A row you cannot classify: stop and ask.

### B5. Write from the call flow, not from the old text

- [ ] **Numbered steps in call order**, each owning its turn(s) and saying what it guarantees; then
      reference sections (Tools, No-Match once, Speaking, Hearing, Situations) the steps point into,
      never restated. Put the flow map in the slim README (`9a71555`).
- [ ] **Instructions in English; only spoken lines in the call's language.**
- [ ] **Tables for parallel cases**, but no cell that reads aloud as a sentence; use ` · ` in
      input/decision tables (D102).
- [ ] **Every guard checkable from the turn being composed.** No running counts across turns (D76:
      the ordinal counter failed 14/24 multi-batch calls), no "recall the result from five turns ago".
- [ ] **Skip tests and tool triggers defined by type, naming the weaker fact they must not accept**
      (D95: a landmark test accepted an area, 2/12 with area+pin vs 5/6 without).
- [ ] **Every "do not invent X" has a mandatory, terminal honest path when X is absent** (D98).
- [ ] **Prohibitions name every kind of thing that could fill the slot** (D97, `d4dd4668`).
- [ ] **Terminal phrases scoped to the turn**; exit checklists list every owed item (D96).
- [ ] **No promise of finality before the last turn** ("आखिरी सवाल" made the pin turn unreachable,
      `d47db4c0`).
- [ ] **No `[slot]` markers or `*( )*` notes inside quoted turns** (D77; spoken aloud on 3/52 calls).
- [ ] **No moving a skippable step into a required tool parameter**: the model fills it falsely
      (D91, `6ae79885`).

### B6. Worked examples: few, real, branch-complete, not reusable as a fabrication

Examples are what the model follows (D50), and in a slim prompt there is less prose around them.

- [ ] One worked call per distinct path, each showing its **input state** so the branch is visibly
      caused by the input.
- [ ] **Every branch of every multi-branch step demonstrated at least once** (a branch only in rule
      prose fired 0 of 41 calls, D102).
- [ ] **Every example performs every mandatory step** on its path; count the ones that skip one.
- [ ] **No concrete value repeated across examples** (pin, phone, name, company, id, salary), each
      paired with its own place. Pin `110045`, used 12 times, was read back to callers with no pin
      (`2027e477`, `d9111476`).
- [ ] Example values not findable in the live inventory or a tester profile, and matching the bot's
      real backend region (D105).
- [ ] No JSON example whose values could become an output (`call_direction: "outbound"` on an inbound
      call, `2027e477`).
- [ ] No example demonstrating a shortening the rules forbid (`591e5c28`).

### B7. Static audit: prove nothing was lost before any call

```bash
python3 raya/slim/compare_spec.py "<source>" "<slim>" --json raya/slim/<target>/diff.json [--max-dropped N]
```

- [ ] **Every dropped spoken line classified by hand**; zero unexplained drops (KKB: 118 drops, 2 real
      ones restored). **Zero new spoken lines** unless the owner asked for a behaviour change.
- [ ] **Coverage diff**: every source row has a slim location or a justified DROP.
- [ ] **Input-variable set identical** to the source's: Raya derives `agent_args` from the `${...}`
      tokens, so one token added or lost changes the agent's arguments (a stray `${college_name}` gave
      the fat KKB agent a seventh argument). Use the token pattern in
      `.claude/skills/sync-check/reference/n-language-parity.md` (camelCase names exist).
- [ ] **Orphaned references**: every heading, step number, path/case/row label and cross-reference
      the rewrite removed or renamed (D51, D97). KKB Slim still says "go to Need Capture" and
      "Path A" after the services step replaced that section.
      ```bash
      grep -n -E 'Need Capture|Path [A-Z]|Case [A-Z]|Row [0-9]|per step|see section|step [0-9]+' "<slim>"
      ```
- [ ] **Guard placement**: each MERGE row's pointer exists at every listed point of use.
- [ ] **Example audit** (B6), memory block byte for byte, instructions English-only.
- [ ] **`/prompt-analyser`** on the slim file; fix every critical/major finding in the rewrite.
- [ ] `prompt_size.py check "<slim>" --target <source-target>`; record chars and bytes in the coverage file.

### B8. Register the variant with `/register-bot`

Never deploy the slim file to the production agent.

- [ ] Folder `<Bot>-Slim/` with the slim file(s) and a `CHANGELOG.md` whose header says: A/B twin of
      `<source-target>`, only the conversation prompt differs, not a language variant, so `/sync-check`
      must not treat it as a mirror of production.
- [ ] Path-map row in root `CLAUDE.md`; a `raya/agents.json` target named by `/register-bot`'s
      convention with `slim` as the last token (e.g. `kkb-hi-signals-slim`), an `_note` (clone source,
      "no production traffic until the A/B has run"), and `expected_name_contains` carrying both
      `Slim` and the language token.
- [ ] Clone the agent so the prompt is the only difference (dry run first):
      ```bash
      python3 raya/slim/create_slim_bot.py --source <source-uuid> --name "<Bot> Slim- <Lang> (A/B)" --instructions "<slim>" --dry-run
      ```
      For a slim mirror in another language: `python3 scripts/raya_clone_agent.py plan|apply <settings_target> <language_target> "<name>" <prompt_file>`.
      Both scripts use the default Raya account only; for a bot with an `"account"` on its target,
      stop and say so. Tool blobs carry live keys: in memory only, never on disk, never committed.
- [ ] **Verify field by field** after creation: language and voice ids, whole tool schema, DIDs,
      interruption and silence timings, nudges, max duration, webhook, memory and output prompts.
      Any difference voids the A/B.
- [ ] uuid copied by hand from `python3 scripts/raya_deploy.py list` (`/register-bot` step 5).
- [ ] Add the target to the regression fleet; add `raya/divergences.json` entries for anything the
      slim family deliberately does differently from production.
- [ ] If the slim agent owns its own output or memory prompt, give it its own file (KKB Slim's live
      output prompt drifted ahead of the shared one until adopted as `KKB-Slim/KKB Slim Output.md`).

### B9. Deploy to the slim agent only

```bash
python3 scripts/raya_deploy.py deploy <slim-target>     # read-back verified; records the deploy
```

Read-back proves it shipped, never that it behaves.

### B10. Test every tier, every language, on the slim agent

The whole prompt was rewritten, so every branch is a changed branch.

1. **Suite**: `/generate-test-cases` on the slim target, seeded from the coverage table (one case per
   branch row, tool contract, owed item and early exit), delivered as the linted test sheet. Grade
   both sides on the same lists: `.claude/skills/voice-test/reference/checklists/<bot>.md` + `generic.md`.
2. **Tier 1, equivalence**: `/voice-test` every case, **N >= 3 per branch**, same persona and fixture
   class. Report `k/N`; `0 < k < N` is UNRESOLVED, never "flaky". Assert against the input ("read back
   THE INPUT'S pin", D102). Split harness dials from real callers before quoting a rate (every KKB
   location "substitution" came from a fixture that disagreed with the tester's stored profile,
   `4b6ab6e`). Inbound directions are tested too (`/voice-test`: integer `out_did` on the inbound
   agent, dial the tester DID).
3. **Tier 2, A/B against the source**: same fixture and persona, dialled alternating, at least 3 pairs
   (more if turn counts differ). KKB Hindi only:
   `python3 raya/slim/ab_compare.py --pairs 3 --fixture <args.json> --persona raya/personas/<persona>.md`
   (`--selftest` first, offline). Other bots: alternate the dials through `/voice-test`. Report per
   side: median s per agent turn **with turn counts**, invariant failures, checklist pass rate. A class
   counts as a slim regression **only if the source passes it on the same fixture across N calls**
   (KKB's first "regression", `90658584`, was done five times in one fat call, `ea0477f4`).
4. **Tier 3**: the slim target is in the daily fleet (B8). It does not replace tiers 1-2.

Every claim names a call id; anything else is DEPLOYED, NOT VERIFIED or VERIFY-PENDING, per row.

### B11. Decision gate before any traffic moves

Show the owner one table: size (source vs slim), median s/turn, checklist pass rate, failure classes
new in slim (must be zero), shared classes, branches still NOT_EXERCISED, languages verified. Traffic
moves only on an explicit yes, as a recorded config change with the prior state saved for rollback
(KKB: `raya/live-snapshots/inbound_move_2026-10-05.json`), then a post-move real-traffic transcript
review before anything is called confirmed.

### B12. Other languages

- [ ] The slim variant is a **new sync family** (slim master + slim mirrors), never a mirror of the
      production prompts; `/sync-check` audits slim master against each slim mirror.
- [ ] Build each slim mirror from the slim master with **`/translate-prompt`**: `prompt_size.py
      project` first, `scripts/speech_split.py extract` / `apply` (spoken lines re-authored, reusing
      proven wording from that language's production prompt; every other line copied and proven
      identical), then `scripts/language_checks.py`.
- [ ] Per-language persona or name choices are registered divergences (KKB Kannada slim speaks as
      ಮಾಯಾ to match its production twin).
- [ ] **Each language tested on its own** through B10-B11: the Kannada slim invented jobs on a missing
      array while the Hindi slim did not (`24e5dabd`, `7fa799eb`; D98).
- [ ] From now on two families stay aligned: a production fix that also applies to slim goes through
      `/port-feature`, noted in both changelogs.

### B13. Changelog, analyser, snapshot, size budget

- [ ] `<Bot>-Slim/CHANGELOG.md`: why, measured composition, size before/after, never-drop checks, A/B
      numbers, files, status per item (DEPLOYED, NOT VERIFIED until each has a call id); a one-line
      pointer entry in the source bot's `CHANGELOG.md`.
- [ ] Every bug found (including in the source) gets a `bug-patterns.md` entry via the normal bug-fix
      loop, plus `section-checklists.md` if it implies a mandatory section.
- [ ] `scripts/prompt-version.sh save <Bot>-Slim slim-v1 "first slim deploy"`; keep the first draft as a
      reference (KKB: `raya/slim/slim-v1-reference.md`).
- [ ] **Size budget**: record chars and bytes in every later changelog entry, and re-run B2 and B7
      when it grows by ~20%. Slim prompts regrow: KKB Slim Hindi went from 68,744 to 138,584 chars
      (164 KB) by 2026-10-14.
- [ ] Later edits to the slim files go through `/update-prompt` or `/port-feature`. This skill only
      creates the variant; it is not a second edit path.

---

## Report (short, root `CLAUDE.md` format, plain words)

- **Size**: before -> after per language (chars and bytes), and the floor if Mode 2.
- **Verified**: one line per branch group or language, with the call id (Mode 1: the call where every
  tool fired at the new size).
- **Failed / not exercised**: one line each, with call ids.
- **A/B** (Mode 2): s/turn and checklist pass rate both sides, with call ids.
- **New bugs**: one line each. **Still open from before**: one line each.
- **Next**: one line (usually the owner decision in B11).

## Guardrails

- Never edit, overwrite or deploy over the source prompt in Mode 2; in Mode 1 the master changes only
  through `/update-prompt`.
- Never drop a never-drop item to hit a number. Below the floor, give the owner a menu.
- Never claim a quality gain from size alone; report the measured delta, whatever it is.
- No behaviour change smuggled into a rewrite. A deliberate one is its own experiment: slim-only,
  owner-approved, measured alone, recorded.
- Never write a third wording of a guard that failed twice, on either side, and never keep a rule aimed
  at the wrong mechanism (`d48bc07` was reverted 0/3 because it was).
- Tool snapshots never touch disk. Real users' numbers and profiles are read-only; test on the tester DID.

Related analyser patterns: D50, D51, D76, D77, D91, D95, D96, D97, D98, D102, D103, D105, D116, D121
(`.claude/skills/prompt-analyser/reference/bug-patterns.md`).
